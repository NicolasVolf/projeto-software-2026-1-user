import os
import json
import redis

class RedisEventService:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        

        self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)

    def salvar_evento(self, key: str, event_data: dict):
        json_event = json.dumps(event_data)
        self.redis_client.set(key, json_event)

    def buscar_evento(self, key: str) -> dict:
        json_event = self.redis_client.get(key)
        if json_event:
            return json.loads(json_event)
        return None