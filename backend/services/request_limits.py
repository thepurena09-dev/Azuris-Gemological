"""Bounded process-local limits with explicit trusted proxy traversal."""
import ipaddress
import math
import os
import time
from collections import OrderedDict, deque
from fastapi import HTTPException


def client_ip(request):
    peer = request.client.host if request.client else "unknown"
    networks = [ipaddress.ip_network(v.strip()) for v in os.getenv("TRUSTED_PROXY_IPS", "127.0.0.1/32,::1/128").split(",") if v.strip()]
    def trusted(value):
        try:
            return any(ipaddress.ip_address(value) in n for n in networks)
        except ValueError:
            return False
    if not trusted(peer):
        return peer
    for value in reversed(request.headers.get("x-forwarded-for", "").split(",")):
        value = value.strip()
        if not value:
            continue
        try:
            ipaddress.ip_address(value)
        except ValueError:
            return peer
        if not trusted(value):
            return value
    return peer


class WindowLimit:
    def __init__(self, maximum, seconds=60, capacity=10000):
        self.maximum, self.seconds, self.capacity = maximum, seconds, capacity
        self.buckets = OrderedDict()

    def check(self, key):
        now = time.monotonic()
        while self.buckets and now - next(iter(self.buckets.values()))[-1] >= self.seconds:
            self.buckets.popitem(last=False)
        q = self.buckets.get(key)
        if q is None:
            if len(self.buckets) >= self.capacity:
                raise HTTPException(429, "Too many attempts. Please try again later.", headers={"Retry-After": str(self.seconds)})
            q = self.buckets[key] = deque()
        self.buckets.move_to_end(key)
        while q and now - q[0] >= self.seconds:
            q.popleft()
        if len(q) >= self.maximum:
            raise HTTPException(429, "Too many attempts. Please try again later.", headers={"Retry-After": str(max(1, math.ceil(self.seconds - now + q[0])))})
        q.append(now)
