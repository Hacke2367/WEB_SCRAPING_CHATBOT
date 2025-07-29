import streamlit as st
import requests
import os

FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")

CHAT_ENDPOINT = f"{FASTAPI_BASE_URL}/chat"
HEALTH_ENDPOINT = f"{FASTAPI_BASE_URL}/health"

st.set_page_config(page_title="RAG Chatbot", page_icon="🤖")

st.title("🤖 RAG Chatbot")
st.markdown(
    """
    Ek AI chatbot jo aapke diye gaye data (Changi Airport websites) par based questions ka jawab de sakta hai.
    """
)

try:
    health_response = requests.get(HEALTH_ENDPOINT, timeout=5)
    health_response.raise_for_status()
    st.success("Chatbot API connected successfully! ✅")
except requests.exceptions.ConnectionError:
    st.error(f"Error: Could not connect to the Chatbot API at {FASTAPI_BASE_URL}. Please ensure the FastAPI server is running and accessible.")
    st.stop()
except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to Chatbot API: {e}")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred during API health check: {e}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about Changi Airport or Jewel Changi Airport..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(CHAT_ENDPOINT, json={"query": prompt}, timeout=60)
                response.raise_for_status()

                bot_response = response.json().get("response", "Sorry, I couldn't get a response from the API.")

            except requests.exceptions.RequestException as e:
                bot_response = f"Error communicating with the API: {e}"
                st.error(bot_response)
            except Exception as e:
                bot_response = f"An unexpected error occurred: {e}"
                st.error(bot_response)

        st.markdown(bot_response)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

st.markdown("---")
st.markdown("Made with ❤️ for Changi Airport knowledge.")




## this is main code, we have to change code due to deployment reason
#If you are using this app locally, run the code below. Thank you

# import streamlit as st
# import requests
# import os
# import sys
#
#
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
#
# FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")
# CHAT_ENDPOINT = f"{FASTAPI_BASE_URL}/chat"
# HEALTH_ENDPOINT = f"{FASTAPI_BASE_URL}/health"
#
# st.set_page_config(page_title="RAG Chatbot", page_icon="🤖")
#
# st.title("🤖 RAG Chatbot")
# st.markdown(
#     """
#     Ek AI chatbot jo aapke diye gaye data (Changi Airport websites) par based questions ka jawab de sakta hai.
#     """
# )
#
# try:
#     health_response = requests.get(HEALTH_ENDPOINT, timeout=5)
#     health_response.raise_for_status()
#     st.success("Chatbot API connected successfully! ✅")
# except requests.exceptions.ConnectionError:
#     st.error(f"Error: Could not connect to the Chatbot API at {FASTAPI_BASE_URL}. Please ensure the FastAPI server is running (`uvicorn api_server:app --reload`).")
#     st.stop()
# except requests.exceptions.RequestException as e:
#     st.error(f"Error connecting to Chatbot API: {e}")
#     st.stop()
#
# if "messages" not in st.session_state:
#     st.session_state.messages = []
#
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])
#
# if prompt := st.chat_input("Ask me anything about Changi Airport or Jewel Changi Airport..."):
#     st.chat_message("user").markdown(prompt)
#     st.session_state.messages.append({"role": "user", "content": prompt})
#
#     with st.chat_message("assistant"):
#         with st.spinner("Thinking..."):
#             try:
#                 response = requests.post(CHAT_ENDPOINT, json={"query": prompt}, timeout=60)
#                 response.raise_for_status()
#                 bot_response = response.json().get("response", "Sorry, I couldn't get a response from the API.")
#             except requests.exceptions.RequestException as e:
#                 bot_response = f"Error communicating with the API: {e}"
#                 st.error(bot_response)
#             except Exception as e:
#                 bot_response = f"An unexpected error occurred: {e}"
#                 st.error(bot_response)
#
#         st.markdown(bot_response)
#         st.session_state.messages.append({"role": "assistant", "content": bot_response})
#
# st.markdown("---")
# st.markdown("Made with ❤️ for Changi Airport knowledge.")