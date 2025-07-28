import asyncio
import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.rag.rag_chain import RAGChain
from src.config import Config
from src.utils.logger import get_logger
from src.utils.exceptions import GenerationException, VectorDBException, EmbeddingException


logger = get_logger(__name__)

app = FastAPI(
    title="RAG Chatbot API",
    description="API for a Retrieval-Augmented Generation (RAG) chatbot.",
    version="1.0.0",
)

origins = [
    "http://localhost",
    "http://localhost:8501", # Default Streamlit port
    "http://127.0.0.1:8501",
    "http://localhost:8000", # Default FastAPI port
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_system: RAGChain | None = None

@app.on_event("startup")
async def startup_event():

    global rag_system
    logger.info("FastAPI startup event: Initializing RAG Chain...")
    try:
        rag_system = RAGChain(pinecone_index_name=Config.PINECONE_INDEX_NAME)
        await rag_system.initialize()
        logger.info("RAG Chain initialized successfully for API.")
    except Exception as e:
        logger.critical(f"Failed to initialize RAG Chain on startup: {e}", exc_info=True)

@app.on_event("shutdown")
async def shutdown_event():
    """
    Closes RAGChain resources when the FastAPI application shuts down.
    """
    global rag_system
    if rag_system:
        logger.info("FastAPI shutdown event: Closing RAG Chain resources...")
        await rag_system.close()
        logger.info("RAG Chain resources closed.")

class QueryRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat_endpoint(request: QueryRequest):
    if not rag_system:
        logger.error("RAG system not initialized. Cannot process query.")
        raise HTTPException(status_code=503, detail="Chat service is not ready. Please try again later.")

    logger.info(f"Received query: '{request.query}'")
    try:
        response = await rag_system.generate_response(request.query)
        logger.info("Response generated and sent.")
        return {"response": response}
    except GenerationException as e:
        logger.error(f"Error generating response for query '{request.query}': {e}")
        raise HTTPException(status_code=500, detail=f"Error generating response: {e.message}")
    except (VectorDBException, EmbeddingException) as e:
        logger.error(f"Retrieval or embedding error for query '{request.query}': {e}")
        raise HTTPException(status_code=500, detail=f"Internal service error during retrieval: {e.message}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred during chat processing for query '{request.query}': {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

@app.get("/health")
async def health_check():
    if rag_system:
        return {"status": "ok", "message": "RAG Chatbot API is running and ready."}
    else:
        raise HTTPException(status_code=503, detail="RAG Chatbot API is starting up or has issues.")

if __name__ == "__main__":
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)



