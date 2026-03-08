import hashlib
from datetime import date


def sha256(value: str) -> str:
    """Return the hex SHA-256 digest of a UTF-8 string."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def hash_fingerprint(client_prehashed: str, salt: str) -> str:
    """
    Server-side second pass of SHA-256 on the client's pre-hashed fingerprint.
    Only the double-hashed value is stored in the database.
    """
    return sha256(client_prehashed + salt)


def hash_ip(raw_ip: str, ip_hash_salt: str, current_date: date | None = None) -> str:
    """
    Daily-rotating IP hash. Uses SHA-256(raw_ip + SHA-256(IP_HASH_SALT + date_string)).
    An IP hash from yesterday will not match today's, making historical correlation impossible.
    """
    if current_date is None:
        current_date = date.today()
    date_str = current_date.strftime("%Y-%m-%d")
    daily_salt = sha256(ip_hash_salt + date_str)
    return sha256(raw_ip + daily_salt)


def hash_subnet_prefix(raw_ip: str, ip_hash_salt: str) -> str:
    """
    Extract first three octets of IPv4 (or reduced form for IPv6) and hash.
    Consistent across time — used to detect subnet-level clustering.
    For IPv6, uses first 3 segments up to the :: boundary or first 3 groups.
    """
    try:
        if ":" in raw_ip:
            # IPv6: take first 3 groups
            parts_full = raw_ip.split(":")
            parts = [parts_full[i] for i in range(min(3, len(parts_full)))]
            prefix = ":".join(p for p in parts if p)
        else:
            # IPv4: take first 3 octets
            parts_full = raw_ip.split(".")
            parts = [parts_full[i] for i in range(min(3, len(parts_full)))]
            prefix = ".".join(parts)
    except Exception:
        prefix = "unknown"
    return sha256(prefix + ip_hash_salt)
