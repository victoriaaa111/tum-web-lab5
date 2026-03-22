import os
import json
import time
import hashlib

CACHE_DIR = ".cache"
CACHE_TTL = 3600  # 1 hour


def cache_key(url):
    return hashlib.md5(url.encode()).hexdigest()


def cache_get(url):
    path = os.path.join(CACHE_DIR, cache_key(url) + ".json")
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        entry = json.load(f)
    if time.time() - entry['time'] > CACHE_TTL:
        os.remove(path)  # expired, delete it
        return None
    print(f"  [cache hit]")
    return entry['status'], entry['headers'], entry['body']


def cache_set(url, status, headers, body):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, cache_key(url) + ".json")
    with open(path, 'w') as f:
        json.dump({
            'time': time.time(),
            'status': status,
            'headers': headers,
            'body': body
        }, f)