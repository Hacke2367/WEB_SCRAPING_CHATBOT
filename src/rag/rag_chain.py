import asyncio
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from src.config import Config
from src.rag.retriever import ContentRetriever
from src.utils.logger import get_logger
from src.utils.exceptions import GenerationException, VectorDBException, EmbeddingException

logger = get_logger(__name__)
load_dotenv()

class RAGChain:

    def __init__(self, pinecone_index_name: str = Config.PINECONE_INDEX_NAME):
        self.retriever = ContentRetriever(pinecone_index_name)
        # Initialize LLM. Make sure OPENAI_API_KEY is set in your .env
        self.llm = ChatOpenAI(model_name=Config.LLM_MODEL_NAME, temperature=Config.LLM_TEMPERATURE
                              )
        self.rag_chain = None
        logger.info(f"RAGChain initialized with LLM: {Config.LLM_MODEL_NAME}")

    async def initialize(self):
        await self.retriever.initialize()
        logger.info("Retriever initialized for RAGChain.")

        prompt = ChatPromptTemplate.from_template(
            """Answer the question based ONLY on the following context:
                        {context}
    
                        Question: {question}
                        """
        )

        def format_docs(docs: List[Document]) -> str:
            return "\n\n".join(doc.page_content for doc in docs)

        self.rag_chain = (
                {
                    "context": RunnableLambda(self.retriever.get_relevant_documents) | RunnableLambda(format_docs),
                    "question": RunnablePassthrough()
                }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        logger.info("RAG chain constructed successfully.")

    async def generate_response(self, query: str) -> str:

        if not self.rag_chain:
            await self.initialize()

        try:
            logger.info(f"Generating response for query: '{query}'")
            response = await self.rag_chain.ainvoke(query)

            if not response or response.strip() == "":
                logger.warning("Empty response from LLM. Using fallback message.")
                return "I'm sorry, I couldn't find relevant information."

            logger.info("Response generated")
            return response

        except (VectorDBException, EmbeddingException) as e:
            logger.error(f"Error during retrieval for RAG chain: {e}")
            raise GenerationException(f"Failed to retrieve context: {e.message}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during response generation: {e}", exc_info=True)
            raise GenerationException(f"Failed to generate response: {e}")

    async def close(self):
        await self.retriever.close()
        logger.info("RAGChain cleanup complete.")


if __name__ == "__main__":
    async def run_rag_chain_test():
        # Ensure your OPENAI_API_KEY is set in your .env file
        # os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY_HERE" # Uncomment and set if not in .env

        if not os.getenv("OPENAI_API_KEY"):
            logger.error("OPENAI_API_KEY environment variable not set. Please set it to run this test.")
            return

        rag_system = RAGChain()
        await rag_system.initialize()

        test_queries = [
            "What amenities does Changi Airport offer?",
            "Tell me about Jewel Changi Airport's main attraction.",
            "What services are available for arriving passengers at Changi Airport?",
            "Is there a hotel at Jewel Changi Airport?",
            "What is the capital of France?" # Example of a query outside the scraped content
        ]

        for query in test_queries:
            try:
                response = await rag_system.generate_response(query)
                logger.info(f"\n--- Query: {query} ---")
                logger.info(f"Response: {response}")
                logger.info("-" * 80)
            except GenerationException as e:
                logger.error(f"Failed to generate response for '{query}': {e}")
            except Exception as e:
                logger.error(f"An unexpected error occurred for query '{query}': {e}", exc_info=True)

            finally:
                await rag_system.close()


    asyncio.run(run_rag_chain_test())






