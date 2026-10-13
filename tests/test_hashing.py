from app.core.hashing import hash_prompt, hash_to_int


def test_hash_prompt_is_stable():
    assert hash_prompt("hello") == hash_prompt("hello")


def test_hash_prompt_normalizes_whitespace():
    assert hash_prompt("  hello  ") == hash_prompt("hello")


def test_hash_prompt_differs_for_different_prompts():
    assert hash_prompt("hello") != hash_prompt("world")


def test_hash_to_int_returns_int():
    assert isinstance(hash_to_int("some-key"), int)
