from typing import Dict, List, Any
from pydantic import BaseModel, Field

class ListCollectionsResponse(BaseModel):
    """
    Response model for listing collections.

    Attributes:
        collections (List[Dict[str, Any]]): List of collections with their details.
    """

    collections: List[str] = Field(
        ...,
        description="List of collections with their details."
    )

class ListUploadedDocumentsResponse(BaseModel):
    """
    Response model for listing uploaded documents.

    Attributes:
        documents (Dict[str, List[str]]): Dictionary of collection names and their document filenames.
    """
    documents: Dict[str, List[str]] = Field(
        ..., description="Dictionary of collections and their document filenames."
    )

class CreateCollectionResponse(BaseModel):
    """
    Response model for confirming the creation of a collection.

    Attributes:
        message (str): A success message confirming the creation of the collection.
    """
    message: str = Field(..., description="A message confirming the collection creation.")


class UploadDocumentResponse(BaseModel):
    """
    Response model for document upload.

    Attributes:
        filename (str): The name of the uploaded file.
        collection_name (str): The name of the collection.
        uploaded_documents (int): The number of documents uploaded.
        status (str): The status of the upload process.
    """

    filename: List[str] = Field(
        ...,
        description="The name of the uploaded file."
    )
    collection_name: str = Field(
        ...,
        description="The name of the collection."
    )
    uploaded_documents: int = Field(
        ...,
        description="The number of documents uploaded."
    )
    status: Dict = Field(
        ...,
        description="The status of the upload process."
    )


class DeleteUploadedDocumentResponse(BaseModel):
    """
    Response model for the /delete-uploaded-document endpoint.

    Attributes:
        collection_name (str): The collection from which the document was deleted.
        document_name (str): The name of the document that was deleted.
        status (str): Status message indicating the result of the deletion.
    """
    collection_name: str = Field(..., description="Collection where the document was stored")
    document_name: str = Field(..., description="Name of the document that was deleted")
    status: str = Field(..., description="Status of the deletion process")


class DeleteCollectionResponse(BaseModel):
    """
    Response model for the operation of deleting a collection.

    Attributes:
        collection_name (str): Name of the collection that was requested to be deleted.
        status (str): Status of the deletion process (e.g., 'success', 'error').
    """
    collection_name: str = Field(..., description="Name of the collection that was deleted")
    status: str = Field(..., description="Result status of the deletion process (e.g., 'success', 'error')")
