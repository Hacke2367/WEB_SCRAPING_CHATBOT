import asyncio
import os
from dotenv import load_dotenv
from typing import List, Dict

import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import Config
from src.data_processing.scraper import Webscraper
from src.data_processing.cleaner import HTMLCleaner
from src.data_processing.chunker import TextChunker
from src.embeddings.vectorizer import TextVectorizer
from src.embeddings.vector_db_client import VectorDBClient
from src.utils.logger import get_logger
from src.utils.exceptions import (
    ScrapingException, CleaningException, ChunkingException,
    EmbeddingException, VectorDBException
)
from langchain_core.documents import Document

logger = get_logger(__name__)


async def ingest_data_pipeline(
        urls: list[str],
        pinecone_index_name: str = Config.PINECONE_INDEX_NAME
):

    load_dotenv()

    logger.info("Starting data ingestion pipeline...")

    scraper = Webscraper()
    cleaner = HTMLCleaner()
    chunker = TextChunker()
    vectorizer = TextVectorizer(Config.EMBEDDING_MODEL_NAME)
    db_client = VectorDBClient(
        provider=Config.VECTOR_DB_PROVIDER,
        api_key=Config.PINECONE_API_KEY,
        environment=Config.PINECONE_ENVIRONMENT,
        index_name=pinecone_index_name
    )

    try:
        logger.info("Initializing vector database client...")
        await db_client.initialize()

        all_documents_for_db: List[Document] = []

        logger.info(f"Initiating scraping for configured URLs.")
        scraped_results_list: List[Dict[str, str]] = []
        try:
            scraped_results_list = await scraper.scrape_all()
            if not scraped_results_list:
                logger.warning(f"No data returned by Webscraper.scrape_all(). Skipping data processing.")
                return
            logger.info(f"Successfully scraped {len(scraped_results_list)} items.")
        except ScrapingException as e:
            logger.critical(f"Failed to perform bulk scraping: {e}")
            return

        for scraped_data_item in scraped_results_list:
            current_url = scraped_data_item.get('url', 'unknown_url')
            raw_html_content = scraped_data_item.get('content', '')
            if not raw_html_content:
                logger.warning(f"No HTML content found for URL: {current_url}. Skipping cleaning.")
                continue

            logger.info(f"Processing scraped item from URL: {current_url}")

            try:
                cleaned_data_list = cleaner.clean_scraped_data([{"url": current_url, "content": raw_html_content}])
                if not cleaned_data_list:
                    logger.warning(f"No cleaned text from {current_url}. Skipping.")
                    continue

                cleaned_text_content = cleaned_data_list[0].get('cleaned_text', '')
                if not cleaned_text_content:
                    logger.warning(f"Cleaned text content is empty for {current_url}. Skipping.")
                    continue
                logger.info(f"Cleaned data from {current_url}.")
            except CleaningException as e:
                logger.error(f"Failed to clean data from {current_url}: {e}")
                continue

            try:
                chunked_documents = chunker.chunk_text(
                    text_content=cleaned_text_content,
                    metadata={"source": current_url, "url": current_url} # Pass URL within metadata dict
                )
                if not chunked_documents:
                    logger.warning(f"No chunks generated for {current_url}. Skipping.")
                    continue
                logger.info(f"Generated {len(chunked_documents)} chunks for {current_url}.")
                all_documents_for_db.extend(chunked_documents)
            except ChunkingException as e:
                logger.error(f"Failed to chunk text from {current_url}: {e}")
                continue

        if not all_documents_for_db:
            logger.warning("No documents were prepared for upsert. Pipeline finished with no data ingested.")
            return

        logger.info(f"Upserting {len(all_documents_for_db)} documents to vector database...")
        embedding_model_for_db = vectorizer.get_embedding_model()
        await db_client.upsert_documents(all_documents_for_db, embedding_model_for_db)
        logger.info("All documents successfully upserted.")

    except (ScrapingException, CleaningException, ChunkingException,
            EmbeddingException, VectorDBException) as e:
        logger.critical(f"Pipeline failed due to a critical error: {e}")
    except Exception as e:
        logger.critical(f"An unexpected critical error occurred: {e}", exc_info=True)
    finally:
        logger.info("Closing vector database client...")
        await db_client.close()
        logger.info("Data ingestion pipeline finished.")

if __name__ == "__main__":
    example_urls = [
        "http://example.com/test",
        "https: // www.changiairport.com"
    ]

    target_index_name = Config.PINECONE_INDEX_NAME

    logger.info(f"Starting ingestion for configured URLs into index: {target_index_name}")
    asyncio.run(ingest_data_pipeline(example_urls, target_index_name))