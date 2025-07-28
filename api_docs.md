# API Documentation: RAG Chatbot API

## 📄 Overview
This document provides comprehensive details for interacting with the **RAG Chatbot API**.  
This API serves as the backend for a Retrieval-Augmented Generation (RAG) chatbot, designed to answer user queries by leveraging knowledge extracted from specific web content (e.g., Changi Airport and Jewel Changi Airport websites).

- **Title:** RAG Chatbot API  
- **Description:** API for a Retrieval-Augmented Generation (RAG) chatbot.  
- **Version:** 1.0.0  
- **Base URL:** `http://localhost:8000` *(Default. This may change in a deployed environment.)*

---

## 🔒 Authentication
Currently, this API does **not require any authentication** for access. All endpoints are publicly accessible.  

> ⚠️ For production deployments, it's highly recommended to implement an authentication and authorization mechanism (e.g., API Keys, OAuth2, JWT).

---

## 🚀 Endpoints

### 1️⃣ GET `/health`
This endpoint provides a simple health check for the API. It indicates whether the service is running and if the underlying RAG system (LLM and Vector Database) is initialized and ready to process requests.

- **Method:** GET  
- **URL:** `/health`  
- **Description:** Checks the API's operational status and the readiness of the RAG system.  

#### Request
- **Headers:** None  
- **Body:** None  

#### Responses
**200 OK**  
Description: The API is running and the RAG system is ready.  
Example Body:
```json
{
    "status": "ok",
    "message": "RAG Chatbot API is running and ready."
}
```

**503 Service Unavailable**  
Description: The API is starting up, or there was an issue initializing the RAG system.  
Example Body:
```json
{
    "detail": "RAG Chatbot API is starting up or has issues."
}
```

#### Example Usage (cURL)
```bash
curl -X GET "http://localhost:8000/health"
```

---

### 2️⃣ POST `/chat`
This is the primary endpoint for interacting with the RAG chatbot. Send a user query, and the API will process it using the RAG pipeline to generate a relevant answer based on the indexed knowledge base.

- **Method:** POST  
- **URL:** `/chat`  
- **Description:** Sends a user query to the RAG chatbot and receives a generated response.  

#### Request
- **Headers:**  
  `Content-Type: application/json`  
- **Body:** A JSON object containing the user's query.  

Example Body:
```json
{
    "query": "What are the main attractions at Jewel Changi Airport?"
}
```

#### Responses
**200 OK**  
Description: The query was processed successfully, and a response was generated.  
Example Body:
```json
{
    "response": "Jewel Changi Airport's main attraction is the Rain Vortex, the world's tallest indoor waterfall. It also features attractions like the Canopy Park, Shiseido Forest Valley, and various dining and retail options."
}
```

**500 Internal Server Error**  
Description: An error occurred during the response generation process.  
Example Body:
```json
{
    "detail": "Error generating response: Failed to retrieve context: Pinecone service unavailable."
}
```

**503 Service Unavailable**  
Description: The RAG system was not initialized or is not ready to process queries.  
Example Body:
```json
{
    "detail": "Chat service is not ready. Please try again later."
}
```

---

#### Example Usage (cURL)
```bash
curl -X POST \
  http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "What services are available for arriving passengers at Changi Airport?"
  }'
```

#### Example Usage (Python using `requests` library)
```python
import requests
import json

api_url = "http://localhost:8000/chat"
query_data = {"query": "Tell me about the amenities available at Changi Airport."}

try:
    response = requests.post(api_url, json=query_data)
    response.raise_for_status() # Raise an exception for HTTP errors
    print(json.dumps(response.json(), indent=2))
except requests.exceptions.RequestException as e:
    print(f"Error making API request: {e}")
```

---


