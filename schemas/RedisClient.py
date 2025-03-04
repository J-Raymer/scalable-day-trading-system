from enum import Enum
import json
import redis
import os
import dotenv
from typing import List


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
        self.__client = redis.Redis(host=host, port=port)

    def __decode(self, res):
        return {key.decode(): json.loads(value.decode()) for key, value in res.items()}

    def set(self, name: CacheName, key: str | int, value: dict):
        """Set an Item (also overrides an existing item)
        client.set(CacheName.STOCKS, 1, {"stock_id": 1, "stock_name": "Google", "price": 100}
        client.set(CacheName.STOCKS, 1, dict(Stock(id=1, name="Google", current_price=100))
        """
        return self.__client.hset(name, key, json.dumps(value, default=str))

    def get(self, name: CacheName, key: str | int):
        """Get an item from the cache.
        client.get(CacheNames.USERS, "123")
        {"id": "123", "user_name": "Test User"}
        """
        result = self.__client.hget(name, key)
        if not result:
            return None
        return json.loads(result)

    def get_all(self, key: str | int):
        """Get all the items from a given key as a dictionary
        client.get_all(CacheNames.STOCKS)
        """
        result = self.__client.hgetall(key)
        if not result:
            return None
        return self.__decode(result)

    def get_list(self, name: CacheName, key: str | int, sort_key: str, reverse=True) -> List[dict] | None:
        """Return a list of dictionaries (useful for formatting something like stock portfolios)
        use reverse=False to sort in reverse order
        client.get_list(CacheName.STOCK_PORTFOLIO, user_id)
        [{'stock_id': 1, 'quantity_owned': 100, 'stock_name': 'Smith-Bryan'},
        {'stock_id': 2, 'quantity_owned': 100, 'stock_name': 'Richardson and Sons'}]
        """
        result = self.__client.hget(name, key)
        if not result:
            return None
        return sorted(list(json.loads(result).values()), key=lambda x: x[sort_key], reverse=reverse)

    def get_all_list(self, key: str | int, sort_key: str, reverse=False):
        """Get all items as a list (same as get_all() but it returns a list instead)
        sort_key: the key to SORT the list by (this is separate from the CACHE key)
        use reverse=False to sort in reverse order
        client.get_all(CacheNames.STOCKS)
        """
        result = self.__client.hgetall(key)
        if not result:
            return None
        return sorted(list(self.__decode(result).values()), key=lambda x: x[sort_key], reverse=reverse)

    def update(self, name: CacheName, key: str | int, value: dict):
        """Update a value of a cache item, or set if no entry exists
        client.update(CacheName.STOCK_PORTFOLIO, 1, {"price": 100})
        """
        result = self.__client.hget(name, key)
        if not result:
            return self.set(name, key, value)
        data = json.loads(result)
        data.update(value)
        return self.__client.hset(name, key, json.dumps(data, default=str))


    def delete(self, name: CacheName, keys: List[str] | List[int]):
        """Delete a cache entry
        client.delete('stocks', ['Google', 'Amazon'])
        """
        return self.__client.hdel(name, *keys)

    def delete_all(self, key: str | int):
        """Delete the entire cache entry
        client.delete_all('stocks')
        """
        return self.__client.delete(key)


import redis
from redis.commands.json.path import Path
import redis.commands.search.aggregation as aggregations
import redis.commands.search.reducers as reducers
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
import redis.exceptions

class RedisClient2:
    def __init__(self):
        dotenv.load_dotenv(override=True)
        port = os.getenv("REDIS_PORT") or 6379
        host = os.getenv("REDIS_HOST") or 'cache'
        self.__client = redis.Redis(host=host, port=port, decode_responses=True)


    def get(self, key):
        """Key should be something like wallet:user_id"""
        return self.__client.json().get(key)

    def set(self, key, id, value):
        """client.set(f'wallet_tx:user_id', wallet_tx_id, {...})"""
        return self.__client.json().set(key, Path.root_path(), {id: value})


    def update(self, key, id, value):
        result = self.__client.json().get(key)
        if not result:
            return self.__client.json().set(key, Path.root_path(), value)
        result.update({id: value})

    def delete(self, key):
        return self.__client.json().delete(key, Path.root_path())
