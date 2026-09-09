from slowapi import Limiter
from slowapi.util import get_remote_address

# Per-client-IP limits. Behind a reverse proxy, replace key_func with one
# that trusts X-Forwarded-For instead of the raw socket address.
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")