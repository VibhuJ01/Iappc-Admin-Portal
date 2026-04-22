from pymongo import MongoClient, collection

from src.cred import Credentials


class BaseDatabase:
    mongo_client = MongoClient(Credentials.mongo_url)
    db = mongo_client[Credentials.db_name]

    @classmethod
    def get_collection(cls, collection_name) -> collection.Collection:
        return cls.db[collection_name]

    @classmethod
    def ensure_indexes(cls):
        """Drop existing indexes and create fresh ones for all collections."""
