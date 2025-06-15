import tempfile
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Form, UploadFile, File, HTTPException, Request

from api.schemas.document_schemas import CreateCollectionResponse, UploadDocumentResponse, ListCollectionsResponse, \
    ListUploadedDocumentsResponse, DeleteUploadedDocumentResponse, DeleteCollectionResponse
from rag.services.document_services import list_collections_service, create_collection_service, upload_document_service, \
    list_uploaded_documents_service, delete_uploaded_document_service, delete_collection_service

docs_router = APIRouter(prefix="/rag/docs", tags=["Docs Router"])


@docs_router.get("/list-collections", response_model=ListCollectionsResponse)
async def list_collections():
    """
    Retrieves the list of collections.

    Returns:
        ListCollectionsResponse: A response containing the list of collections.
    """
    collections = list_collections_service()
    return ListCollectionsResponse(collections=collections)


@docs_router.post("/create-collection", response_model=CreateCollectionResponse, status_code=201)
async def create_collection(
        collection_name: str = Form(...)
):
    """
    Creates a new document collection for the current user.

    Args:
        collection_name (str): The name of the collection to create.

    Returns:
        dict: A success message confirming the creation of the collection.
    """
    create_collection_service(collection_name)
    return {"message": f"Collection '{collection_name}' created successfully."}


@docs_router.post("/upload-document", response_model=UploadDocumentResponse, status_code=201)
async def upload_document(
    request: Request,
    files: List[UploadFile] = File(...),
    collection_name: str = Form(...),
):
    """
    Uploads one or more documents to a specified collection and processes them for embedding.

    Args:
        request (Request): The incoming request, containing the embedding model.
        files (List[UploadFile]): A list of uploaded files.
        collection_name (str): The name of the collection to store the documents in.

    Returns:
        UploadDocumentResponse: Details of the uploaded and processed documents.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        file_paths = []
        for file in files:
            content = await file.read()
            file_path = Path(temp_dir) / file.filename
            file_path.write_bytes(content)
            file_paths.append(file_path)
        result = upload_document_service(file_paths, collection_name, request)
    return UploadDocumentResponse(
        filename=[file.filename for file in files],
        collection_name=collection_name,
        uploaded_documents=result["uploaded_documents"],
        status={"message": "Documents processed and inserted successfully"}
    )


@docs_router.get("/list-uploaded-documents", response_model=ListUploadedDocumentsResponse)
async def list_uploaded_documents(
    collection_name: Optional[str] = None
):
    """
    Retrieves the list of uploaded documents for a collection or all accessible collections.

    Args:
        collection_name (Optional[str]): The name of the collection to filter by (optional).

    Returns:
        ListUploadedDocumentsResponse: A response containing the list of uploaded documents.
    """
    if collection_name:
        collections = [collection_name]
    else:
        collections = [col["name"] for col in list_collections_service()]

    documents = list_uploaded_documents_service(collections)
    return ListUploadedDocumentsResponse(documents=documents)



@docs_router.delete("/delete-uploaded-document", response_model=DeleteUploadedDocumentResponse)
async def delete_uploaded_document(
    collection_name: str,
    document_name: str,
):
    """
    Deletes a specific document from a collection for the current user.

    Args:
        collection_name (str): The name of the collection.
        document_name (str): The name of the document to delete.
        current_user (User): The authenticated user.

    Returns:
        DeleteUploadedDocumentResponse: A response confirming the document deletion.
    """
    delete_uploaded_document_service(collection_name, document_name)
    return DeleteUploadedDocumentResponse(
        collection_name=collection_name,
        document_name=document_name,
        status="Deleted by file_name"
    )


@docs_router.delete("/delete-collection", response_model=DeleteCollectionResponse)
async def delete_collection(collection_name: str):
    """
    Deletes an entire document collection for the current user.

    Args:
        collection_name (str): The name of the collection to delete.

    Returns:
        DeleteCollectionResponse: A response confirming the collection deletion.
    """
    delete_collection_service(collection_name)
    return DeleteCollectionResponse(
        collection_name=collection_name,
        status="Deleted by collection_name"
    )