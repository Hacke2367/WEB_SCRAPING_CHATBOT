import asyncio
from typing import List, Dict
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStoreRetriever

from src.config import Config
from src.embeddings.vectorizer import TextVectorizer
from src.embeddings.vector_db_client import VectorDBClient
from src.utils.logger import get_logger
from src.utils.exceptions import VectorDBException, EmbeddingException

logger = get_logger(__name__)

class ContentRetriever:
    def __init__(self, pinecone_index_name: str = Config.PINECONE_INDEX_NAME):
        self.vectorizer = TextVectorizer(Config.EMBEDDING_MODEL_NAME)
        self.db_client = VectorDBClient(
            provider=Config.VECTOR_DB_PROVIDER,
            api_key=Config.PINECONE_API_KEY,
            environment=Config.PINECONE_ENVIRONMENT,
            index_name=pinecone_index_name
        )
        self.embedding_model: Embeddings | None = None
        self.retriever: VectorStoreRetriever | None = None
        logger.info(f"ContentRetriever initialized for index: {pinecone_index_name}")

    async def initialize(self):
        if not self.embedding_model:
            self.embedding_model = self.vectorizer.get_embedding_model()
            logger.info("Embedding model loaded for retriever.")
        await self.db_client.initialize()
        logger.info("VectorDBClient initialized for retriever.")

        if not self.retriever:
            self.retriever = self.db_client.get_retriever(self.embedding_model)
            logger.info("LangChain retriever obtained from VectorDBClient.")


    async def get_relevant_documents(self, query: str, top_k: int = Config.TOP_K_RETRIEVAL) -> List[Document]:

        if not self.retriever:
            await self.initialize()

        try:
            logger.info(f"Retrieving top {top_k} documents for query: '{query}'")
            relevant_docs = await self.retriever.ainvoke(query, config={"k": top_k})
            logger.info(f"Found {len(relevant_docs)} relevant documents.")
            return relevant_docs
        except VectorDBException as e:
            logger.error(f"Error querying vector database: {e}")
            raise VectorDBException(f"Failed to retrieve documents from DB: {e.message}", details=e.details)
        except EmbeddingException as e:
            logger.error(f"Error generating query embedding: {e}")
            raise EmbeddingException(f"Failed to embed query for retrieval: {e.message}", details=e.details)
        except Exception as e:
            logger.error(f"An unexpected error occurred during document retrieval: {e}", exc_info=True)
            raise

    async def close(self):
        await self.db_client.close()
        logger.info("ContentRetriever cleanup complete.")


if __name__ == "__main__":
    async def run_retriever_test():
        test_query = "What is Changi Airport known for?"
        retriever = ContentRetriever()
        await retriever.initialize()

        try:
            relevant_documents = await retriever.get_relevant_documents(test_query, top_k=3)
            if relevant_documents:
                logger.info(f"\n--- Relevant Documents for query: '{test_query}' ---")
                for i, doc in enumerate(relevant_documents):
                    logger.info(f"Document {i+1} (Source: {doc.metadata.get('url', 'N/A')}):")
                    logger.info(doc.page_content[:200] + "...")
                    logger.info("-" * 50)
            else:
                logger.info("No relevant documents found.")
        except (VectorDBException, EmbeddingException) as e:
            logger.error(f"Retriever test failed: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during retriever test: {e}", exc_info=True)
        finally:
            await retriever.close()

    asyncio.run(run_retriever_test())