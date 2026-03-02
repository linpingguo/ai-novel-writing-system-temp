from pymilvus import connections, utility, Collection, FieldSchema, CollectionSchema, DataType
from typing import List, Dict, Any, Optional
import numpy as np


class VectorDBClient:
    def __init__(self, host: str = "localhost", port: int = 19530):
        self.host = host
        self.port = port
        self.connections = connections

    async def connect(self):
        try:
            self.connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            print(f"Connected to Milvus at {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to connect to Milvus: {e}")
            raise

    async def disconnect(self):
        self.connections.disconnect("default")

    async def create_collection(self, collection_name: str, dimension: int = 1536):
        from pymilvus import connections

        if not utility.has_collection(collection_name):
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, auto_id=True, max_length=36),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension),
                FieldSchema(name="metadata", dtype=DataType.JSON),
            ]

            schema = CollectionSchema(
                fields=fields,
                description=f"{collection_name} collection",
                enable_dynamic_field=True
            )

            await utility.create_collection(schema)
            print(f"Collection '{collection_name}' created successfully")
        else:
            print(f"Collection '{collection_name}' already exists")

    async def insert_vectors(
        self,
        collection_name: str,
        ids: List[str],
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]]
    ):
        from pymilvus import Collection

        collection = Collection(collection_name)
        collection.load()

        data = [ids, embeddings, metadata]
        await collection.insert(data)
        print(f"Inserted {len(ids)} vectors into {collection_name}")

    async def search_vectors(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        from pymilvus import Collection

        collection = Collection(collection_name)
        collection.load()

        search_params = {"metric_type": "IP", "params": {"nprobe": 10}}

        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=None
        )

        return results

    async def get_collection(self, collection_name: str) -> Optional[Collection]:
        from pymilvus import Collection

        if utility.has_collection(collection_name):
            return Collection(collection_name)
        return None


vector_db_client = VectorDBClient(host="localhost", port=19530)
