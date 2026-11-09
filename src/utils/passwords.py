# src/utils/passwords.py
import base64
import hashlib
import hmac
import secrets

_N = 2**14
_R = 8
_P = 1
_KEY_LENGTH = 32
_SALT_LENGTH = 16


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(_SALT_LENGTH)
    digest = _derive(password, salt, _N, _R, _P)
    return "$".join(["scrypt", str(_N), str(_R), str(_P), _b64(salt), _b64(digest)])


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, n, r, p, salt, expected = stored.split("$")
        if scheme != "scrypt":
            return False
        digest = _derive(password, _unb64(salt), int(n), int(r), int(p))
        return hmac.compare_digest(digest, _unb64(expected))
    except ValueError:
        return False


def _derive(password: str, salt: bytes, n: int, r: int, p: int) -> bytes:
    return hashlib.scrypt(
        password.encode(), salt=salt, n=n, r=r, p=p, dklen=_KEY_LENGTH, maxmem=128 * n * r * 2
    )


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def _unb64(text: str) -> bytes:
    return base64.b64decode(text, validate=True)
