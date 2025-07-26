from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.config import Config
from src.utils.logger import get_logger
from src.utils.exceptions import DataProcessingException

logger = get_logger(__name__)

class TextChunker:

    def __init__(self, chunk_size: int= Config.CHUNK_SIZE, chunk_overlap: int = Config.CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitters = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        logger.info(f"Initialized TextChunker with chunk_size={self.chunk_size}, chunk_overlap={self.chunk_overlap}")

    def chunk_text(self, text_content: str, metadata: Dict[str, str]) -> List[Document]:

        if not text_content:
            logger.warning('Empty text content provided for chunking')
            return []

        try:
            documents = self.text_splitters.create_documents([text_content], metadatas=[metadata])
            logger.info(f"Chunked text info {len(documents)} documents for URL: {metadata.get('url', 'N/A')}")
            return documents
        except Exception as e:
            logger.error(f"Error chunking text for URL {metadata.get('url', 'N/A')}: {e}")
            raise DataProcessingException(f"Failed to chunk text: {e}")

    def chunk_cleaned_data(self, cleaned_data: List[Dict[str, str]]) -> List[Document]:

        all_chunks: List[Document] = []
        if not cleaned_data:
            logger.warning("No cleaned data provided by chunking")
            return []

        for item in cleaned_data:
            url = item.get("url")
            cleaned_text = item.get("cleaned_text")

            if not url or not cleaned_text:
                logger.warning(f"Skipping incomplete cleaned data item {item}")
                continue

            chunk_metadata = {"source": url, "url": url}

            try:
                chunks = self.chunk_text(cleaned_text, chunk_metadata)
                all_chunks.extend(chunks)
            except DataProcessingException as e:
                logger.error(f"Error processing item from {url}: {e}. Skipping this item.")

        if not all_chunks:
            raise DataProcessingException("No documents were successfully chunked from the cleaned data.")

        logger.info(f"Finished chunking. Total {len(all_chunks)} documents created.")
        return all_chunks

if __name__ == "__main__":
    cleaned_text_sample = {
        "url": "http://example.com/long-article",
        "cleaned_text": "Changi Airport is a major international airport that serves Singapore. It is located at the eastern end of Singapore and is one of the busiest airports in the world by international passenger traffic. Changi Airport offers excellent connectivity to over 400 cities worldwide, with about 100 airlines operating from its four passenger terminals. The airport is renowned for its high-quality services, efficient operations, and a wide array of amenities. Jewel Changi Airport is a mixed-use development at Changi Airport, Singapore. It includes gardens, attractions, a hotel, and retail and dining options. Jewel is directly connected to Terminals 1, 2, and 3, making it easily accessible for travelers and visitors alike. Its most prominent feature is the Rain Vortex, the world's tallest indoor waterfall. Jewel offers a unique blend of nature and retail experiences." * 5

    }
    cleaned_data_list = [cleaned_text_sample]
    chunker = TextChunker(chunk_size=200, chunk_overlap=20)

    try:
        documents = chunker.chunk_cleaned_data(cleaned_data_list)
        for i, doc in enumerate(documents):
            logger.info(f"--- Document {i + 1} ---")
            logger.info(f"Metadata: {doc.metadata}")
            logger.info(f"Content (first 200 chars): {doc.page_content[:200]}...")
            logger.info("-" * 30)

    except DataProcessingException as e:
        logger.error(f"Chunking failed: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during chunking test: {e}")


