import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    APP_NAME: str = "LLMCHATBOT"
    APP_VERSION = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    ## LLM SETTINGS
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    HUGGINGFACE_API_KEY: str | None = os.getenv("HUGGINGFACE_API_KEY")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.7))

    ## EMBEDDINGS SETTINGS
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION : int = int(os.getenv("EMBEDDING_DIMENSION", 384))

    ##VECTOR DATABASE SETTINGS
    VECTOR_DB_PROVIDER: str = os.getenv("VECTOR_DB_PROVIDER", "pinecone").lower()
    PINECONE_API_KEY: str | None = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: str | None = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "llmchatbot-index")
    NUMBER_OF_RETRIEVED_DOCS: int = int(os.getenv("NUMBER_OF_RETRIEVED_DOCS", 4))

    ##DATA PREPROCESSING SETTING
    SCRAPING_URLS: list[str] = [
        "https://www.changiairport.com",
        "https://www.jewelchangiairport.com"
    ]

    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 500))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 50))
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K", 4))

    ## --- API Settings ---
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", 8000))

    # -- LOGGING SETTINGS ---
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE: str = os.getenv("LOG_FILE", "/tmp/app.log")

if not Config.DEBUG:
    if not Config.OPENAI_API_KEY and not Config.HUGGINGFACE_API_KEY:
        raise ValueError("Critical: no llm api key (openai api key or huggingface api key")
    if Config.VECTOR_DB_PROVIDER == "pinecone" and (not Config.PINECONE_ENVIRONMENT or Config.PINECONE_API_KEY):
        raise ValueError("Critical: Pinecone API Key or Enviroment not found for pinecone provihder. cannot proceed in non-debug mode.")

