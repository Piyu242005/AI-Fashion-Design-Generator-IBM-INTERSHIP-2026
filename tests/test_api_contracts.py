"""Fast, network-free tests for the serverless API contracts."""

import importlib
import json


def test_design_model_allowlist_contains_all_supported_models():
    design = importlib.import_module("api.design")
    assert len(design.ALLOWED_MODELS) == 4
    assert design.CF_DEFAULT_MODEL in design.ALLOWED_MODELS


def test_design_error_contract_is_stable():
    design = importlib.import_module("api.design")
    result = design._json_error(400, "VALIDATION_ERROR", "bad prompt")
    assert result == {
        "success": False,
        "error": {"code": "VALIDATION_ERROR", "message": "bad prompt"},
    }


def test_gemini_json_parser_accepts_plain_json():
    gemini = importlib.import_module("api.gemini")
    assert gemini._extract_json('{"category":"shirt"}') == {"category": "shirt"}


def test_gemini_json_parser_accepts_markdown_fence():
    gemini = importlib.import_module("api.gemini")
    payload = "```json\n{\"fabric\":\"linen\"}\n```"
    assert gemini._extract_json(payload) == {"fabric": "linen"}


def test_gemini_parser_rejects_invalid_json():
    gemini = importlib.import_module("api.gemini")
    try:
        gemini._extract_json("not json")
    except json.JSONDecodeError:
        return
    raise AssertionError("Invalid JSON should raise JSONDecodeError")


def test_health_configuration_helper_requires_all_variables(monkeypatch):
    health = importlib.import_module("api.health")
    monkeypatch.setenv("A", "1")
    monkeypatch.setenv("B", "2")
    assert health._configured("A", "B") is True
    monkeypatch.delenv("B")
    assert health._configured("A", "B") is False
