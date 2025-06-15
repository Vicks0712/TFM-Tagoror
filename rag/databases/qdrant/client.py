import os

from qdrant_client import QdrantClient

class QdrantDBClient:
    def __init__(self, qdrant_client: QdrantClient):
        self.qdrant_client = qdrant_client

    def drop_collection(self, collection_name: str) -> None:
        """
        Deletes a collection from the Qdrant vector database.

        Args:
            collection_name (str): The name of the collection to delete.
        """
        self.qdrant_client.delete_collection(collection_name)

    def list_collections(self) -> list:
        """
        Retrieves a list of all collection names in the Qdrant vector database.

        Returns:
            list: A list of collection names.
        """
        return [col.name for col in self.qdrant_client.get_collections().collections]


class QdrantClientBuilder:
    def __init__(self):
        self._host = "localhost"
        self._port = 6333

    def set_host(self, host: str):
        """
        Sets the host address for the Qdrant connection.

        Args:
            host (str): The host address to connect to.

        Returns:
            QdrantClientBuilder: The builder instance for chaining.
        """
        self._host = host
        return self

    def set_port(self, port: int):
        """
        Sets the port number for the Qdrant connection.

        Args:
            port (int): The port number to connect to.

        Returns:
            QdrantClientBuilder: The builder instance for chaining.
        """
        self._port = port
        return self


    def build(self) -> QdrantDBClient:
        """
        Builds and returns a configured QdrantDBClient instance.

        Returns:
            QdrantDBClient: A new QdrantDBClient with the specified host and port.
        """
        client = QdrantClient(host=self._host, port=self._port)
        return QdrantDBClient(client)


qdrant_client_builder = QdrantClientBuilder()
qdrant_client_builder.set_host(os.getenv("QDRANT_URL", "localhost"))
qdrant_client_builder.set_port(int(os.getenv("QDRANT_PORT_INTERNAL", 6333)))
qdrant_client = qdrant_client_builder.build()