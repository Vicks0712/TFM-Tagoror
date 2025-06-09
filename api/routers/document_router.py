from fastapi import APIRouter

docs_router = APIRouter(prefix="/rag/docs", tags=["Docs Router"])


@docs_router.get("/list-collections", response_model=ListCollectionsResponse)
async def list_collections():
    """
    Retrieves the list of collections available to the current user.

    Args:
        current_user (User): The authenticated user.

    Returns:
        ListCollectionsResponse: A response containing the list of collections.
    """
    collections = list_collections_service(current_user)
    return ListCollectionsResponse(collections=collections)