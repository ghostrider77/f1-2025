import hashlib
import hmac
import os

MIN_PASSWORD_SIZE = 8
SALT_BYTE_SIZE = 32
NR_ITERATIONS = 100_000


def hash_password(password: str) -> bytes | None:
    if _is_suitable_password_string(password):
        salt = os.urandom(SALT_BYTE_SIZE)
        hashed_password = hashlib.pbkdf2_hmac("sha256", password.encode("ascii"), salt, NR_ITERATIONS)
        return salt + hashed_password

    return None


def is_password_valid(password: str, *, stored_password: bytes) -> bool:
    if _is_suitable_password_string(password):
        salt = stored_password[:SALT_BYTE_SIZE]
        stored_hashed_password = stored_password[SALT_BYTE_SIZE:]
        hashed_password = hashlib.pbkdf2_hmac("sha256", password.encode("ascii"), salt, NR_ITERATIONS)
        return hmac.compare_digest(hashed_password, stored_hashed_password)

    return False


def _is_suitable_password_string(string: str) -> bool:
    return string.isascii() and len(string) >= MIN_PASSWORD_SIZE
