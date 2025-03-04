from enum import Enum
import os
import dotenv
import redis
from redis.commands.json.path import Path
import redis.commands.search.aggregation as aggregations
import redis.commands.search.reducers as reducers
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
import redis.exceptions

class CacheName(str, Enum):
    STOCKS = 'stocks'
    STOCK_PORTFOLIO = 'stock_portfolio'
    STOCK_TX = 'stock_tx'
    WALLETS = 'wallets'
    WALLET_TX = 'wallet_tx'
    USERS = 'users'


class RedisClient:
    def __init__(self):
        dotenv.load_dotenv(override=True)
        port = os.getenv("REDIS_PORT") or 6379
        host = os.getenv("REDIS_HOST") or 'cache'
        self.__client = redis.Redis(host=host, port=port, decode_responses=True)

    def get(self, key: str):
        """Key should be something like wallet:user_id"""
        return self.__client.json().get(key)

    def set(self, key: str, value: dict):
        """client.set(f'wallet_tx:user_id', wallet_tx_id, {...})"""
        return self.__client.json().set(key, Path.root_path(), value)


    def update(self, key: str, value: dict):
        result = self.__client.json().get(key)
        if not result:
            return self.__client.json().set(key, Path.root_path(), value)
        result.update(value)

    def delete(self, key):
        return self.__client.json().delete(key, Path.root_path())
