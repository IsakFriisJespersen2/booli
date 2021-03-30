from hashlib import sha1
import time
import random
import string
from typing import List


class BooliApi():
    def __init__(
        self,
        user_agent: str,
        base_url: str,
        id_caller: str,
        private_key: str
    ) -> None:
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/hal+json",
            "User-Agent": user_agent
        }
        self.base_url = base_url
        self.id_caller = id_caller
        self.private_key = private_key
    
    def create_hash(self, unique: str, timestamp: str) -> str:
        return sha1(
            '{}{}{}{}'.format(
                self.id_caller,
                timestamp,
                self.private_key,
                unique
            ).encode('utf-8')
        ).hexdigest()

    def create_unique(self) -> str:
        return ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for _ in range(16)
        )

    def create_booli_parameters(
        self,
        resource: str,
        q: str,
        offset: int,
        limit: int
    ) -> str:
        timestamp: str = str(int(time.time()))
        unique: str = self.create_unique()
        hashstr: str = self.create_hash(unique=unique, timestamp=timestamp)
        return '/{}?q={}&limit={}&offset={}&callerId={}&time={}&unique={}&hash={}'.format( # noqa
            resource,
            q,
            limit,
            offset,
            self.id_caller,
            timestamp,
            unique,
            hashstr
        )

    def get_offset(self, count: int, offset: int) -> int:
        return count + offset

    def extract_date_price(self, data: List[dict]) -> List[dict]:
        return [
            {
                'soldPrice': d.get('soldPrice'),
                'soldDate': d.get('soldDate')
            }
            for d in data
        ]
