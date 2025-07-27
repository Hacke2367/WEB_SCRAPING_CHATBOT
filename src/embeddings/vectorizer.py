from typing import List, Dict
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings

from src.config import Config
from src.utils.logger import get_logger
from src.utils.exceptions import EmbeddingException

logger = get_logger(__name__)

class TextVectorizer:

    def __init__(self, model_name: str = Config.EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self.embedding_model = None
        self.langchain_embedding_model = None
        self._load_model()
        logger.info(f"TextVectorizer initialized with model: {self.model_name}")

    def _load_model(self):
        try:
            self.embedding_model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded SentenceTransformer model: {self.model_name}")

            self.langchain_embedding_model = HuggingFaceEmbeddings(model_name=self.model_name)
            logger.info("Wrapped embedding model for LangChain compatibility.")

            dummy_embedding = self.embed_text("test")
            if len(dummy_embedding) != Config.EMBEDDING_DIMENSION:
                logger.warning(
                    f"Configured EMBEDDING_DIMENSION ({Config.EMBEDDING_DIMENSION}) "
                    f"does not match actual model dimension ({len(dummy_embedding)}). "
                    "Please update config.py or choose a different model."
                )
        except Exception as e:
            logger.error(f"Failed to load embedding model '{self.model_name}': {e}")
            raise EmbeddingException(f"Failed to load embedding model: {e}")

    def embed_text(self, text: str) -> List[float]:

        if not self.embedding_model:
            raise EmbeddingException("Embedding model not loaded. Call _load_model first.")
        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=False)
            return embedding
        except Exception as e:
            logger.error(f"Error embedding text: '{text[:50]}...': {e}")
            raise EmbeddingException(f"Failed to embed text: {e}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:

        if not self.embedding_model:
            raise EmbeddingException("Embedding model not loaded. Call _load_model first.")

        try:
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=False)
            logger.debug(f"Generated {len(embeddings)} embeddings.")
            return embeddings
        except Exception as e:
            logger.error(f"Error embedding multiple documents: {e}")
            raise EmbeddingException(f"Failed to embed documents: {e}")

    def get_embedding_model(self):

        if not self.langchain_embedding_model:
            raise EmbeddingException("LangChain embedding model not initialized.")
        return self.langchain_embedding_model

if __name__ == "__main__":

    vectorizer = TextVectorizer()
    sample_texts = [
        "What are the attractions at Jewel Changi Airport?",
        "How many terminals does Changi Airport have?",
        "Where can I find dining options at Jewel?",
        "This is a test sentence for embedding."
    ]

    try:
        embeddings = vectorizer.embed_documents(sample_texts)
        logger.info(f"Generated {len(embeddings)} embeddings.")
        for i, emb in enumerate(embeddings):
            logger.info(f"Embedding {i + 1} (first 5 values): {emb[:5]}...")
            logger.info(f"Embedding {i + 1} dimension: {len(emb)}")

        langchain_emb_model = vectorizer.get_embeddings_model()
        lc_embedding = langchain_emb_model.embed_query("Another test query for LangChain.")
        logger.info(f"LangChain embedding (first 5 values): {lc_embedding[:5]}...")
        logger.info(f"LangChain embedding dimension: {len(lc_embedding)}")

    except EmbeddingException as e:
        logger.error(f"Embedding test failed: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during vectorizer test: {e}")






