## RAG Chatbot: Changi Airport & Jewel Information System

This project implements a **Retrieval-Augmented Generation (RAG)** chatbot designed to answer questions based on information scraped from the official Changi Airport and Jewel Changi Airport websites.  
It features a robust data pipeline, a Pinecone vector database for efficient retrieval, an OpenAI LLM for generation, and a user-friendly web interface built with **Streamlit** and **FastAPI**.

---

## ✨ Features

- **Web Scraping:** Automatically collects data from specified URLs.  
- **Data Preprocessing:** Cleans and chunks raw text for optimal retrieval.  
- **Vector Embeddings:** Converts text chunks into numerical vectors using a SentenceTransformer model.  
- **Vector Database Integration:** Stores and retrieves vector embeddings efficiently using Pinecone.  
- **Retrieval-Augmented Generation (RAG):** Enhances LLM responses by providing relevant context from the vector database.  
- **OpenAI LLM Integration:** Uses `gpt-3.5-turbo` for generating coherent and context-aware answers.  
- **FastAPI Backend:** Provides a RESTful API endpoint for chatbot interactions.  
- **Streamlit Frontend:** Offers an intuitive web-based chat interface.  
- **Modular Design:** Components are separated for clarity, maintainability, and scalability.  

---

## 🏗️ Architecture & Components

- `src/scraper/`: Handles fetching raw HTML content from specified URLs.  
- `src/data_processor/`: Cleans and chunks the scraped content.  
- `src/embeddings/`:  
  - `vectorizer.py`: Manages the text embedding model.  
  - `vector_db_client.py`: Interfaces with the Pinecone vector database.  
- `src/rag/`:  
  - `retriever.py`: Queries the vector database to fetch relevant documents.  
  - `rag_chain.py`: Orchestrates retrieval with the LLM to generate answers.  
- `scripts/ingest_data.py`: Runs the entire data ingestion pipeline.  
- `api_server.py`: FastAPI backend exposing the `/chat` endpoint.  
- `streamlit_app.py`: Streamlit frontend for user interaction.  
- `src/config.py`: Centralized configuration management.  
- `src/utils/`: Utility functions like logging and custom exceptions.  

---

## ⚙️ Prerequisites

```
- Python 3.9+
- pip (Python package manager)
- A Pinecone account and API key
- An OpenAI account and API key
```

---

## 🚀 Setup Instructions

### 1. Clone the Repository
```
git clone <repository_url>
cd <project_directory>
```

### 2. Set up Virtual Environment
```
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. Configure Environment Variables  
Create a `.env` file in the root directory:  
```
OPENAI_API_KEY="your_openai_api_key"
PINECONE_API_KEY="your_pinecone_api_key"
PINECONE_ENVIRONMENT="your_pinecone_environment"
PINECONE_INDEX_NAME="llmchatbot-index"
FASTAPI_BASE_URL="http://localhost:8000"
```

---

## 🚀 Usage

### 1. Run the Data Ingestion Pipeline
```
python scripts/ingest_data.py
```

### 2. Start the FastAPI Backend
```
uvicorn api_server:app --reload
```

### 3. Run the Streamlit Frontend
```
streamlit run streamlit_app.py
```

---

## 📂 Project Structure
```
WEB_SCRAPER_CHATBOT/
├── api_server.py
├── streamlit_app.py
├── requirements.txt
├── scripts/
│   └── ingest_data.py
└── src/
    ├── config.py
    ├── scraper/
    ├── data_processor/
    ├── embeddings/
    ├── rag/
    └── utils/
```

---

## 💡 Future Enhancements

```
- Add user authentication for secure interactions  
- Store conversation history for better context  
- Add reranker models for improved retrieval  
- Build more advanced UI features  
```
