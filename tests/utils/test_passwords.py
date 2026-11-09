from src.utils.passwords import hash_password
from src.utils.passwords import verify_password


def test_verify_accepts_the_original_password() -> None:
    assert verify_password("correct horse", hash_password("correct horse")) is True


def test_verify_rejects_a_different_password() -> None:
    assert verify_password("wrong", hash_password("correct horse")) is False


def test_hash_is_salted_so_equal_passwords_hash_differently() -> None:
    assert hash_password("same") != hash_password("same")


def test_hash_does_not_contain_the_plaintext() -> None:
    assert "correct horse" not in hash_password("correct horse")


def test_verify_rejects_malformed_hashes_instead_of_raising() -> None:
    assert verify_password("x", "") is False
    assert verify_password("x", "not-a-hash") is False
    assert verify_password("x", "scrypt$1$2$3$!!!$!!!") is False
    assert verify_password("x", "bcrypt$1$2$3$YQ==$YQ==") is False
