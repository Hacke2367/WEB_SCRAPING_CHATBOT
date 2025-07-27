import asyncio
from pinecone import Pinecone, PodSpec, ServerlessSpec
from typing import List, Dict
from langchain_core.embeddings import Embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from src.config import Config
from src.embeddings.vectorizer import TextVectorizer
from src.utils.logger import get_logger
from src.utils.exceptions import VectorDBException, EmbeddingException

logger = get_logger(__name__)

class VectorDBClient:
    def __init__(self, provider: str, api_key: str | None, environment: str | None, index_name: str):
        self.provider = provider.lower()
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.pinecone_client = None
        self.index = None
        self.vectorstore: PineconeVectorStore | None = None

    async def initialize(self):
        if self.provider == "pinecone":
            if not self.api_key or not self.environment:
                raise VectorDBException("Pinecone API Key or Environment not provided.")

            try:
                self.pinecone_client = Pinecone(api_key=self.api_key, environment=self.environment)
                logger.info("Pinecone client initialized")
                existing_indexes_meta = await self._list_pinecone_indexes()
                existing_index_names = [idx.name for idx in existing_indexes_meta] # FIXED: Extract names
                logger.info(f"Existing Pinecone index names: {existing_index_names}") # Updated logging

                if self.index_name not in existing_index_names: # FIXED: Check against names
                    logger.info(f"Pinecone index '{self.index_name}' not found. Attempting to create...")
                    spec = ServerlessSpec(cloud='aws', region='us-east-1') # Adjust region as needed

                    try:
                        self.pinecone_client.create_index(
                            name= self.index_name,
                            dimension=Config.EMBEDDING_DIMENSION,
                            metric="cosine",
                            spec=spec
                        )
                        logger.info(f"Pinecone index '{self.index_name}' created successfully.")
                    except Exception as e:
                        if "(409) Conflict" in str(e) and "ALREADY_EXISTS" in str(e):
                            logger.warning(f"Pinecone index '{self.index_name}' already exists despite initial check. Proceeding.")
                        else:
                            raise e
                else:
                    logger.info(f"Pinecone index '{self.index_name}' already exists.")

                self.index = self.pinecone_client.Index(self.index_name)
                logger.info(f"Pinecone Index instance for '{self.index_name}' obtained.")

            except Exception as e:
                logger.error(f"Error initializing Pinecone: {e}")
                raise VectorDBException(f"Failed to initialize Pinecone: {e}")
        else:
            raise VectorDBException(f"Unsupported vector database provider: {self.provider}")

    async def _list_pinecone_indexes(self) -> list:
        return await asyncio.to_thread(self.pinecone_client.list_indexes)

    async def upsert_documents(self, documents: List[Document], embedding_model: Embeddings):
        if not self.index:
            raise VectorDBException("Vector database index not initialized. Call initialize() first.")
        if not documents:
            logger.info("No documents provided for upsert. Skipping.")
            return

        try:
            await asyncio.to_thread(
                PineconeVectorStore.from_documents,
                documents=documents,
                embedding=embedding_model,
                index_name=self.index_name
            )
            logger.info(f"Successfully upserted {len(documents)} documents to Pinecone index '{self.index_name}'.")

        except Exception as e:
            logger.error(f"Error upserting documents to Pinecone: {e}")
            raise VectorDBException(f"Failed to upsert documents: {e}")

    def get_retriever(self, embedding_model: Embeddings):
        if not self.index:
            raise VectorDBException("Vector database index not initialized. Call initialize() first.")

        if self.vectorstore is None:
            try:
                self.vectorstore = PineconeVectorStore(
                    index=self.index,
                    embedding=embedding_model,
                    text_key="text"
                )
                logger.info(f"LangChain PineconeVectorStore initialized for index '{self.index_name}'.")
            except Exception as e:
                logger.error(f"Error initializing PineconeVectorStore: {e}")
                raise VectorDBException(f"Failed to create vector store: {e}")

        return self.vectorstore.as_retriever(search_type="similarity", k=Config.NUMBER_OF_RETRIEVED_DOCS)

    async def close(self):
        if self.provider == "pinecone" and self.pinecone_client:
            logger.info("Pinecone client does not require explicit close method in its Python client.")
        logger.info("VectorDBClient cleanup complete.")

if __name__ == "__main__":
    import os
    import sys
    from dotenv import load_dotenv
    load_dotenv()

    if not hasattr(Config, 'NUMBER_OF_RETRIEVED_DOCS'):
        Config.NUMBER_OF_RETRIEVED_DOCS = int(os.getenv("NUMBER_OF_RETRIEVED_DOCS", 4))


    async def run_vector_db_test():

        test_db_client = VectorDBClient(
            provider=Config.VECTOR_DB_PROVIDER,
            api_key=Config.PINECONE_API_KEY,
            environment=Config.PINECONE_ENVIRONMENT,
            index_name=Config.PINECONE_INDEX_NAME + "-test"
        )

        try:
            logger.info("Initializing VectorDBClient for test...")
            await test_db_client.initialize()

            from langchain_core.documents import Document
            dummy_documents = [
                Document(page_content="This is the first test document about Changi Airport's Terminal 3.", metadata={"source": "test_url_1", "title": "Doc 1"}),
                Document(page_content="This second document talks about the Rain Vortex at Jewel Changi Airport.", metadata={"source": "test_url_2", "title": "Doc 2"}),
                Document(page_content="Third document discusses services like baggage claim and customs.", metadata={"source": "test_url_3", "title": "Doc 3"})
            ]

            logger.info(f"Upserting {len(dummy_documents)} dummy documents...")
            real_vectorizer = TextVectorizer(Config.EMBEDDING_MODEL_NAME)
            await test_db_client.upsert_documents(dummy_documents, real_vectorizer.get_embedding_model())

            logger.info("Waiting 3 seconds for Pinecone to index documents...")
            await asyncio.sleep(3)


            logger.info("Retriever obtained. Performing a dummy similarity search...")
            retriever = test_db_client.get_retriever(real_vectorizer.get_embedding_model())

            query_doc = await retriever.ainvoke("What are the main services at the airport?")
            logger.info(f"Retrieved {len(query_doc)} documents.")
            for i, doc in enumerate(query_doc):
                logger.info(f"Retrieved document {i+1}: {doc.page_content[:100]}... (Source: {doc.metadata.get('source')})")

        except VectorDBException as e:
            logger.error(f"VectorDB test failed: {e}")
        except EmbeddingException as e:
            logger.error(f"Embedding model error during VectorDB test: {e}")
        except Exception as e:
            logger.exception(f"An unexpected error occurred during vector DB test: {e}")
        finally:
            current_indexes_before_cleanup = []
            if test_db_client.pinecone_client:
                try:
                    current_indexes_before_cleanup = await test_db_client._list_pinecone_indexes()
                except Exception as e:
                    logger.warning(f"Could not list indexes before cleanup: {e}")

            current_index_names = [idx.name for idx in current_indexes_before_cleanup]

            if test_db_client.index_name in current_index_names:
                logger.info(f"Deleting test index: {test_db_client.index_name}")
                await asyncio.to_thread(test_db_client.pinecone_client.delete_index, test_db_client.index_name)
                logger.info("Test index deleted.")
            else:
                logger.info(f"Test index '{test_db_client.index_name}' not found for deletion, likely already removed or never created.")

            await test_db_client.close()

    asyncio.run(run_vector_db_test())