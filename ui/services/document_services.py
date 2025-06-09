import os
import requests

from config.logger import logger

APP_URL = os.getenv("APP_URL", "http://localhost")
APP_PORT = os.getenv("APP_PORT_INTERNAL", "8000")
API_URL = f"{APP_URL}:{APP_PORT}"


def delete_document(collection_name, document_name):
    response = requests.delete(
        f"{API_URL}/rag/docs/delete-uploaded-document",
        params={
            "collection_name": collection_name,
            "document_name": document_name
        }
    )
    return response.ok


def delete_collection(collection_name):
    response = requests.delete(
        f"{API_URL}/rag/docs/delete-collection",
        params={"collection_name": collection_name}
    )
    return response.ok


def fetch_collections_raw() -> dict:
    url = f"{API_URL}/rag/docs/list-collections"

    response = requests.get(url)
    response.raise_for_status()

    return response.json()


def get_collection_names():
    raw = fetch_collections_raw()
    return raw.get("collections", [])



def upload_document_to_collection(file, collection_name):
    files = {"files": (file.name, file.getvalue())}
    data = {"collection_name": collection_name}

    response = requests.post(
        f"{API_URL}/rag/docs/upload-document",
        files=files,
        data=data
    )
    response.raise_for_status()
    return response.json()


def list_documents_in_collection(collection_name=None):
    params = {"collection_name": collection_name} if collection_name else {}

    response = requests.get(
        f"{API_URL}/rag/docs/list-uploaded-documents",
        params=params
    )
    response.raise_for_status()
    return response.json().get("documents", {})


def create_collection(collection_name, vector_size=os.getenv("EMBEDDING_VECTOR_SIZE", 1024)):
    data = {
        "collection_name": collection_name,
        "vector_size": str(vector_size)
    }

    response = requests.post(
        f"{API_URL}/rag/docs/create-collection",
        data=data
    )
    response.raise_for_status()
    return response.json()
