import uuid
from qdrant_client import models
from qdrant_client.models import PointStruct
from qdrant_client.models import VectorParams, SparseVectorParams, SparseIndexParams, Distance
from qdrant_client.models import SparseVector
from qdrant_client.models import Prefetch, FusionQuery, Fusion

from rag.databases.qdrant.client import QdrantDBClient


class QdrantCollection:
    def __init__(self, db_client: QdrantDBClient, collection_name: str, vector_size: int, type: str):
        self.db_client = db_client
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.type = type  # "dense", "hybrid", "sparse"
        self._create_collection()

    def _create_collection(self) -> None:
        """
        Creates the collection in Qdrant if it does not already exist,
        based on the collection type.
        """
        if self.collection_name in self.db_client.list_collections():
            return

        if self.type == "dense":
            self._create_dense_collection()
        elif self.type == "hybrid":
            self._create_hybrid_collection()
        elif self.type == "sparse":
            self._create_sparse_collection()
        else:
            raise ValueError(f"Unknown collection type '{self.type}'.")

    def _create_dense_collection(self):
        """
        Creates a dense collection in Qdrant with cosine distance metric.
        """
        self.db_client.qdrant_client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
        )

    def _create_hybrid_collection(self):
        """
        Creates a hybrid collection in Qdrant combining dense and sparse vectors.
        """
        self.db_client.qdrant_client.create_collection(
            collection_name=self.collection_name,
            vectors_config={"text-dense": VectorParams(size=self.vector_size, distance=Distance.COSINE)},
            sparse_vectors_config={"text-sparse": SparseVectorParams(index=SparseIndexParams(on_disk=False))}
        )

    def _create_sparse_collection(self):
        """
        Creates a sparse-only collection in Qdrant.
        """
        self.db_client.qdrant_client.create_collection(
            collection_name=self.collection_name,
            vectors_config={},
            sparse_vectors_config={"text-sparse": SparseVectorParams(index=SparseIndexParams(on_disk=False))}
        )

    def insert_document(self, document: dict, embedding: dict, metadata: dict) -> None:
        """
        Inserts a document into the collection with the given embeddings and metadata.

        Args:
            document (dict): The document containing at least 'PK' and 'text' fields.
            embedding (dict): The embedding(s) for the document (dense, sparse, or both).
            metadata (dict): Additional metadata for the document.
        """
        point_id = str(uuid.uuid4())
        payload = {"PK": document["PK"], "text": document["text"], **metadata}

        if self.type == "dense":
            point = self._build_point_dense(point_id, embedding, payload)
        elif self.type == "hybrid":
            point = self._build_point_hybrid(point_id, embedding, payload)
        elif self.type == "sparse":
            point = self._build_point_sparse(point_id, embedding, payload)
        else:
            raise ValueError(f"Unknown collection type '{self.type}'.")

        self.db_client.qdrant_client.upsert(collection_name=self.collection_name, points=[point])

    def _build_point_dense(self, point_id, embedding, payload):
        """
        Builds a dense PointStruct for insertion.

        Args:
            point_id (str): The unique identifier for the point.
            embedding (list): The dense embedding vector.
            payload (dict): The payload associated with the point.

        Returns:
            PointStruct: The constructed dense point.
        """
        return PointStruct(id=point_id, vector=embedding, payload=payload)

    def _build_point_hybrid(self, point_id, embedding, payload):
        """
        Builds a hybrid PointStruct combining dense and sparse vectors.

        Args:
            point_id (str): The unique identifier for the point.
            embedding (dict): The dense and sparse embeddings.
            payload (dict): The payload associated with the point.

        Returns:
            PointStruct: The constructed hybrid point.
        """
        try:
            dense_vector = embedding["dense"]
            sparse_dict = embedding["sparse"]
            return PointStruct(
                id=point_id,
                vector={
                    "text-dense": dense_vector,
                    "text-sparse": SparseVector(
                        indices=list(map(int, sparse_dict.keys())),
                        values=list(sparse_dict.values())
                    )
                },
                payload=payload
            )
        except Exception as e:
            raise ValueError(f"ERROR INSERTANDO {e}")

    def _build_point_sparse(self, point_id, sparse_dict, payload):
        """
        Builds a sparse PointStruct for insertion.

        Args:
            point_id (str): The unique identifier for the point.
            sparse_dict (dict): The sparse embedding dictionary.
            payload (dict): The payload associated with the point.

        Returns:
            PointStruct: The constructed sparse point.
        """
        return PointStruct(
            id=point_id,
            vector={
                "text-sparse": SparseVector(
                    indices=list(map(int, sparse_dict.keys())),
                    values=list(sparse_dict.values())
                )
            },
            payload=payload
        )

    def delete_document(self, pk: str) -> None:
        """
        Deletes a document from the collection by its primary key.

        Args:
            pk (str): The primary key of the document to delete.
        """
        self.db_client.qdrant_client.delete(
            collection_name=self.collection_name,
            points_selector=models.Filter(
                must=[models.FieldCondition(
                    key="PK",
                    match=models.MatchValue(value=pk)
                )]
            )
        )

    def find_all_documents(self) -> list:
        """
        Retrieves all documents in the collection (limited to 100).

        Returns:
            list: A list of documents with payloads.
        """
        return self.db_client.qdrant_client.scroll(collection_name=self.collection_name, limit=100)[0]

    def find_most_similar(self, query_embedding, n: int = 5):
        """
        Finds the most similar documents to a given embedding.

        Args:
            query_embedding (dict): The embedding used for similarity search.
            n (int): The number of top results to retrieve.

        Returns:
            list: A list of the most similar documents with scores.
        """
        try:
            if self.type == "dense":
                return self._search_dense(query_embedding, n)
            elif self.type == "hybrid":
                return self._search_hybrid(query_embedding, n)
            elif self.type == "sparse":
                return self._search_sparse(query_embedding, n)
            else:
                raise ValueError(f"Unknown collection type: {self.type}.")
        except Exception as e:
            raise e

    def _search_dense(self, query, n):
        """
        Searches for dense embeddings most similar to the query.

        Args:
            query (list): The dense embedding query.
            n (int): The number of top results.

        Returns:
            list: A list of matching documents with scores.
        """
        self._check_dim(query)
        return self._format_results(self.db_client.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=query,
            limit=n
        ).points)

    def _search_sparse(self, sparse_vector_dict, n):
        """
        Searches for sparse embeddings most similar to the query.

        Args:
            sparse_vector_dict (dict): The sparse vector query.
            n (int): The number of top results.

        Returns:
            list: A list of matching documents with scores.
        """
        return self._format_results(self.db_client.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=SparseVector(
                indices=list(sparse_vector_dict.keys()),
                values=list(sparse_vector_dict.values())
            ),
            using="text-sparse",
            limit=n,
            with_payload=True
        ).points)

    def _search_hybrid(self, query_embedding, n):
        """
        Searches for documents using both dense and sparse embeddings.

        Args:
            query_embedding (dict): Contains both dense and sparse vectors.
            n (int): The number of top results.

        Returns:
            list: A list of matching documents with scores.
        """
        dense_vector = query_embedding["dense"]
        sparse_vector_dict = query_embedding["sparse"]
        self._check_dim(dense_vector)

        return self._format_results(self.db_client.qdrant_client.query_points(
            collection_name=self.collection_name,
            prefetch=[
                Prefetch(query=dense_vector, using="text-dense", limit=n),
                Prefetch(
                    query=SparseVector(
                        indices=list(sparse_vector_dict.keys()),
                        values=list(sparse_vector_dict.values())
                    ),
                    using="text-sparse",
                    limit=n
                ),
            ],
            query=FusionQuery(fusion=Fusion.DBSF),
            limit=n,
            with_payload=True
        ).points)

    def _check_dim(self, vector):
        """
        Checks if the given vector has the correct dimension.

        Args:
            vector (list): The embedding vector to check.

        Raises:
            ValueError: If the dimension is incorrect.
        """
        if len(vector) != self.vector_size:
            raise ValueError(f"Dimensión incorrecta: esperada {self.vector_size}, obtenida {len(vector)}")

    def _format_results(self, points):
        """
        Formats the results of a search to extract relevant fields.

        Args:
            points (list): A list of Qdrant point objects.

        Returns:
            list: A list of dictionaries with primary key, text, and score.
        """
        return [{"PK": p.payload.get("PK", ""), "text": p.payload.get("text", ""), "score": p.score} for p in points]


    def find_by_payload(self, field: str, value: str) -> list:
        """
        Finds documents in the collection by matching a specific field in the payload.

        Args:
            field (str): The payload field to filter by.
            value (str): The value to search for.

        Returns:
            list: A list of matching documents.
        """
        response = self.db_client.qdrant_client.scroll(
            collection_name=self.collection_name,
            scroll_filter=models.Filter(
                must=[models.FieldCondition(
                    key=field,
                    match=models.MatchValue(value=value)
                )]
            ),
            limit=100,
            with_payload=True
        )

        return [
            {"PK": p.payload.get("PK", ""), "text": p.payload.get("text", ""),
             "score": p.score if hasattr(p, "score") else None}
            for p in response[0]
        ]




