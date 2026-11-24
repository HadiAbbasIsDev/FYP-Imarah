"""Check that automatic startup only manages this app's own local model process.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import pytest

from scripts import ollama_local


def test_existing_model_server_is_left_running(monkeypatch):
    monkeypatch.delenv("OLLAMA_URL", raising=False)
    monkeypatch.setattr(ollama_local, "version", lambda: "0.34.2")
    monkeypatch.setattr(
        ollama_local.subprocess,
        "Popen",
        lambda *args, **kwargs: pytest.fail("Must not start another server"),
    )
    assert ollama_local.ensure_server() is None


def test_custom_server_does_not_start_project_runtime(monkeypatch):
    monkeypatch.setenv("OLLAMA_URL", "http://127.0.0.1:11434")
    monkeypatch.setattr(
        ollama_local,
        "version",
        lambda: pytest.fail("Do not probe the project port"),
    )
    assert ollama_local.ensure_server() is None


def test_absent_optional_runtime_does_not_stop_app_startup(monkeypatch, tmp_path):
    monkeypatch.delenv("OLLAMA_URL", raising=False)
    monkeypatch.setattr(ollama_local, "version", lambda: None)
    monkeypatch.setattr(ollama_local, "BINARY", tmp_path / "not-installed")
    assert ollama_local.ensure_server() is None


def test_invalid_runtime_archive_is_not_extracted(monkeypatch, tmp_path):
    monkeypatch.setattr(ollama_local.platform, "system", lambda: "Linux")
    monkeypatch.setattr(ollama_local.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(ollama_local, "version", lambda: None)
    archive = tmp_path / "wrong.tar.zst"
    archive.write_bytes(b"An incomplete download is not an executable runtime.")
    monkeypatch.setattr(
        ollama_local.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("Must not extract an unverified archive"),
    )
    with pytest.raises(SystemExit, match="SHA256 does not match"):
        ollama_local.install(archive)
