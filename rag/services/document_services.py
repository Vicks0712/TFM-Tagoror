import os
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Set


from rag.config.logger import logger
from rag.databases.qdrant.client import qdrant_client
from rag.databases.qdrant.collections import QdrantCollection
from rag.components.preprocessor import Preprocessor


def list_collections_service() -> list:
    """
    Retrieves the list of collections accessible to the current user.

    Args:
        current_user (User): The authenticated user.

    Returns:
        list: A list of collection metadata dictionaries.
    """
    all_collections = qdrant_client.list_collections()
    return all_collections


def create_collection_service(
        collection_name: str
) -> None:
    """
    Creates a new collection in Qdrant and updates the collection lists.

    Args:
        collection_name (str): The name of the collection to create.
    """
    qdrant_collection = QdrantCollection(
        db_client=qdrant_client,
        collection_name=collection_name,
        vector_size=os.getenv("EMBEDDING_VECTOR_SIZE", 0)
    )
    qdrant_collection._create_collection()



def upload_document_service(
    files: List[Path],
    collection_name: str,
    request,
) -> Dict:
    """
    Processes and uploads a list of documents to a specified collection.
    Documents are preprocessed, embedded, and stored in Qdrant.

    Args:
        files (List[Path]): A list of document file paths to upload.
        collection_name (str): The name of the collection to upload to.
        embedding_model: The embedding model used for vectorization.

    Returns:
        dict: A summary containing the number of uploaded documents.
    """
    preprocessor = Preprocessor()
    all_preprocessed_docs = []

    for file in files:
        logger.info(f"Processing file: {file}")
        processed_docs = preprocessor.run(file_path=file)
        all_preprocessed_docs.extend(processed_docs)

    qdrant = QdrantCollection(
        db_client=qdrant_client,
        collection_name=collection_name,
        vector_size=int(os.getenv("EMBEDDING_VECTOR_SIZE", 0)),
        type=os.getenv("EMBEDDING_SEARCH_TYPE", "hybrid"),
    )
    embedding_model = request.app.state.embedding_model
    texts = [doc.text for doc in all_preprocessed_docs]
    dense_vectors = embedding_model.encode(texts)
    sparse_vectors = embedding_model.encode_sparse(texts)

    for doc, dense, sparse in zip(all_preprocessed_docs, dense_vectors, sparse_vectors):
        embeddings = {"dense": dense, "sparse": sparse}
        qdrant.insert_document(
            document={"PK": doc.PK, "text": doc.text},
            embedding=embeddings,
            metadata=doc.metadata.to_dict()
        )

    return {
        "uploaded_documents": len(all_preprocessed_docs)
    }


def list_uploaded_documents_service(collections: List[str]) -> Dict[str, List[str]]:
    """
    Lists the uploaded documents for each collection.

    Args:
        collections (List[str]): A list of collection names.

    Returns:
        dict: A mapping from collection names to lists of document filenames.
    """
    collection_docs: Dict[str, Set[str]] = defaultdict(set)
    for col in collections:
        try:
            qdrant_collection = QdrantCollection(
                db_client=qdrant_client,
                collection_name=col,
                vector_size=os.getenv("EMBEDDING_VECTOR_SIZE", 0),
                type=os.getenv("EMBEDDING_SEARCH_TYPE", "hybrid")
            )
            for doc in qdrant_collection.find_all_documents():
                pk = (doc.payload or {}).get("PK")
                if pk:
                    collection_docs[col].add(pk)
                else:
                    logger.warning(f"Document in collection '{col}' has no valid file_name → {pk}")
        except Exception as e:
            logger.warning(f"Skipping collection '{col}' due to error: {e}")
            continue
    return {col: sorted(list(pk_names)) for col, pk_names in collection_docs.items()}


def delete_uploaded_document_service(collection_name: str, document_name: str) -> None:
    """
    Deletes a specific document from a collection.

    Args:
        collection_name (str): The name of the collection.
        document_name (str): The name of the document to delete.
    """
    qdrant_collection = QdrantCollection(
        db_client=qdrant_client,
        collection_name=collection_name,
        vector_size=os.getenv("EMBEDDING_VECTOR_SIZE",0),
        type=os.getenv("EMBEDDING_SEARCH_TYPE", "hybrid")
    )
    qdrant_collection.delete_document(pk=document_name)


def delete_collection_service(collection_name: str):
    """
    Deletes an entire collection.

    Args:
        collection_name (str): The name of the collection to delete.
    """
    qdrant_client.drop_collection(collection_name=collection_name)