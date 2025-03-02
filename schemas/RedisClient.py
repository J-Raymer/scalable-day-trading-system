from enum import Enum
import json
import redis
import os
import dotenv
from typing import List


from pydantic import BaseModel

class CacheName(str, Enum):
    STOCKS = 'stocks'
    STOCK_TX = 'stock_tx'
    WALLETS = 'wallets'
    WALLET_TX = 'wallet_tx'
    USERS = 'users'


class RedisClient:
    def __init__(self):
        dotenv.load_dotenv(override=True)
        port = os.getenv("REDIS_PORT") or 6379
        host = os.getenv("REDIS_HOST") or 'cache'
        self.client = redis.Redis(host=host, port=port)

    def __decode(self, res):
        return {key.decode(): value.decode() for key, value in res.items()}

    def set(self, name: CacheName, key: str, value):
        """Set an Item
        client.set(CacheName.STOCKS, 1, {"stock_id": 1, "stock_name": "Google", "price": 100}
        client.set(CacheName.STOCKS, 1, Stock(id=1, name="Google", current_price=100)
        """
        if isinstance(value, dict):
            return self.client.hset(name, key, json.dumps(value))
        else:
            return self.client.hset(name, key, json.dumps(dict(value)))

    def get(self, name: CacheName, key: str):
        """Get an item from the cache.
        client.get(CacheNames.USERS, "123")
        {"id": "123", "user_name": "Test User"}
        """
        result = self.client.hget(name, key)
        if not result:
            return None
        return json.loads(result)

    def get_all(self, key: str):
        """Get all the items from a given key as a dictionary
        client.get_all(CacheNames.STOCKS)
        """
        result = self.client.hgetall(key)
        if not result:
            return None
        return self.__decode(result)

    def get_all_list(self, key: str):
        """Get all items as a list (same as get_all() but it returns a list instead)
        client.get_all(CacheNames.STOCKS)
        """
        result = self.client.hgetall(key)
        if not result:
            return None
        return list(self.__decode(result).values())

    def delete(self, name: CacheName, keys: List[str]):
        """Delete a cache entry
        client.delete('stocks', ['Google', 'Amazon'])
        """
        return self.client.hdel(name, *keys)

    def delete_all(self, key):
        """Delete the entire cache entry
        client.delete_all('stocks')
        """
        return self.client.delete(key)


