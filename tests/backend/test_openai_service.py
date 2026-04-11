import pytest
from services.openai_service import test_openai_key


def test_test_openai_key_returns_true_when_api_call_succeeds(monkeypatch):
    monkeypatch.setattr(
        "services.openai_service.client.models.list", lambda: ["model-1"]
    )

    result = test_openai_key()

    assert result is True


def test_test_openai_key_returns_false_when_api_call_fails(monkeypatch):
    def fake_models_list():
        raise Exception("Invalid API key")

    monkeypatch.setattr("services.openai_service.client.models.list", fake_models_list)

    result = test_openai_key()

    assert result is False
