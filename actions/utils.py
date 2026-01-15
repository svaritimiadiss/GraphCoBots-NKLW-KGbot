import requests
# import os
# import yaml
# from dotenv import load_dotenv, set_key
from rasa_sdk.executor import CollectingDispatcher
import yaml

BASE_URL = "http://127.0.0.1:8000"

LOCAL_BASE_DIR = "./actions"
FILENAME = "genai_placeholders.yml"
RAG_FALLBACK_ANSWER_ENDPOINT = "rag/fallback"
FILEPATH = f"{LOCAL_BASE_DIR}/{FILENAME}"

with open(FILEPATH, 'r', encoding='utf-8') as f:
    genai_data = yaml.safe_load(f)

def get_rag_response(query: str) -> str:
    """Send query to RAG API and return response"""
    generate_fallback_answer_url = f"{BASE_URL}/{RAG_FALLBACK_ANSWER_ENDPOINT}"

    params = {
        "query": query,
        "document_url": genai_data["documents"]["url"],
        "db_path":genai_data["vector_stores"]["vector_db"],
        "collection_name": genai_data["vector_stores"]["collection"],
        "embedding_model": genai_data["models"]["embeddings"],
        "system_prompt": genai_data["tasks"]["rag_prompts"]["system_prompt"],
        "user_prompt": genai_data["tasks"]["rag_prompts"]["user_prompt"].format(query=query, context="{context}"),
        "chat_model": genai_data["models"]["chat"],
        "n_results": genai_data["rag"]["n_results"],
        "max_tokens": genai_data["rag"]["max_tokens"],
    }

    try:
        response = requests.get(generate_fallback_answer_url, params=params).json()
        print(response)
        return response
    except requests.exceptions.RequestException as e:
        print("Συγγνώμη, υπήρξε κάποιο πρόβλημα κατά την επεξεργασία του ερωτήματός σου.")
        print(f"API request failed: {e}")
