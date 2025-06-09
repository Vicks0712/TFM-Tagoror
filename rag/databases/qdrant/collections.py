import uuid
from qdrant_client import models
from qdrant_client.models import PointStruct
from databases.qdrant.client import QdrantDBClient
from qdrant_client.models import VectorParams, SparseVectorParams, SparseIndexParams, Distance
from qdrant_client.models import NamedVector, NamedSparseVector, SparseVector, SearchRequest
from qdrant_client.models import Prefetch, FusionQuery, Fusion


class QdrantCollection:
    def __init__(self, db_client: QdrantDBClient, collection_name: str, vector_size: int, type: str):
        self.db_client = db_client
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.type = type  # "dense" o "hybrid"
        self._create_collection()

    def _create_collection(self) -> None:
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
        self.db_client.qdrant_client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
        )

    def _create_hybrid_collection(self):
        self.db_client.qdrant_client.create_collection(
            collection_name=self.collection_name,
            vectors_config={"text-dense": VectorParams(size=self.vector_size, distance=Distance.COSINE)},
            sparse_vectors_config={"text-sparse": SparseVectorParams(index=SparseIndexParams(on_disk=False))}
        )

    def _create_sparse_collection(self):
        self.db_client.qdrant_client.create_collection(
            collection_name=self.collection_name,
            vectors_config={},
            sparse_vectors_config={"text-sparse": SparseVectorParams(index=SparseIndexParams(on_disk=False))}
        )

    def insert_document(self, document: dict, embedding: dict, metadata: dict) -> None:
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
        return PointStruct(id=point_id, vector=embedding, payload=payload)

    def _build_point_hybrid(self, point_id, embedding, payload):
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
        return self.db_client.qdrant_client.scroll(collection_name=self.collection_name, limit=100)[0]

    def find_most_similar(self, query_embedding, n: int = 5):
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
        self._check_dim(query)
        return self._format_results(self.db_client.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=query,
            limit=n
        ).points)

    def _search_sparse(self, sparse_vector_dict, n):
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
        if len(vector) != self.vector_size:
            raise ValueError(f"Dimensión incorrecta: esperada {self.vector_size}, obtenida {len(vector)}")

    def _format_results(self, points):
        return [{"PK": p.payload.get("PK", ""), "text": p.payload.get("text", ""), "score": p.score} for p in points]


    def find_by_payload(self, field: str, value: str) -> list:
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




