from qdrant_client import QdrantClient

class QdrantDBClient:
    def __init__(self, qdrant_client: QdrantClient):
        self.qdrant_client = qdrant_client

    def drop_collection(self, collection_name: str) -> None:
        self.qdrant_client.delete_collection(collection_name)

    def list_collections(self) -> list:
        return [col.name for col in self.qdrant_client.get_collections().collections]


class QdrantClientBuilder:
    def __init__(self):
        self._host = "localhost"
        self._port = 6333

    def set_host(self, host: str):
        self._host = host
        return self

    def set_port(self, port: int):
        self._port = port
        return self


    def build(self) -> QdrantDBClient:
        client = QdrantClient(host=self._host, port=self._port)
        return QdrantDBClient(client)