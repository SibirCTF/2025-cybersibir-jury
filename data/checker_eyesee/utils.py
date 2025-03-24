import os
import uuid
from hashlib import md5


def ping(host) -> bool:
    ping_timeout = 2
    response = os.system(f"timeout {ping_timeout}s ping -c 1 {host} > /dev/null 2>&1")
    return response == 0


def get_uuid(string: str) -> str:
    return str(uuid.UUID(hex=md5(string.encode('utf-8')).hexdigest()))
