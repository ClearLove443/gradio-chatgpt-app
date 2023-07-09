class RedisCache:
    def __init__(self):
        import redis

        self.r = redis.StrictRedis(host="192.168.2.201", port=6379)

    def set(self, key: str, value: str) -> None:
        self.r.set(key, value)

    def get(self, key: str) -> str:
        v = self.r.get(key)
        return v if v is None else v.decode("utf-8")

    def delete(self, key: str) -> None:
        self.r.delete(key)

    def clear(self) -> None:
        self.r.delete(*self.r.keys(pattern="*"))
