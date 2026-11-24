"""Check download recovery and integrity using tiny byte strings, not real model weights.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import hashlib
import json

import httpx
import pytest

from scripts import download_ollama_models as downloader


def fake_server(monkeypatch, handler):
    original = httpx.Client
    monkeypatch.setattr(
        httpx, "Client", lambda **kwargs: original(**kwargs, transport=httpx.MockTransport(handler))
    )
    monkeypatch.setattr(downloader, "CHUNK_BYTES", 4)
    monkeypatch.setattr(downloader.time, "sleep", lambda _: None)


def test_interrupted_download_resumes_only_unsaved_pieces(tmp_path, monkeypatch):
    content = b"abcdefghij"
    sha = hashlib.sha256(content).hexdigest()
    requests = []
    failing = True

    def handler(request):
        first, last = map(int, request.headers["range"].removeprefix("bytes=").split("-"))
        requests.append(first)
        if failing and first >= 4:
            raise httpx.ReadError("Connection interrupted")
        return httpx.Response(
            206,
            content=content[first : last + 1],
            headers={"content-range": f"bytes {first}-{last}/{len(content)}"},
        )

    fake_server(monkeypatch, handler)
    destination = tmp_path / "ready" / sha
    work = tmp_path / "partial"
    with pytest.raises(httpx.ReadError):
        downloader.download_layer(
            "https://example.test/blob", destination, len(content), sha, work, workers=1
        )
    assert not destination.exists()
    assert json.loads((work / f"{sha}.json").read_text())["completed_chunks"] == [0]
    failing = False
    requests.clear()
    downloader.download_layer(
        "https://example.test/blob", destination, len(content), sha, work, workers=1
    )
    assert requests == [4, 8]
    assert destination.read_bytes() == content
    assert not (work / f"{sha}.json").exists()


def test_ignored_range_is_rejected_before_activation(tmp_path, monkeypatch):
    fake_server(monkeypatch, lambda request: httpx.Response(200, content=b"abcdefgh"))
    destination = tmp_path / "ready"
    with pytest.raises(ValueError, match="exact requested range"):
        downloader.download_layer(
            "https://example.test/blob", destination, 8, "a" * 64, tmp_path / "partial", workers=1
        )
    assert not destination.exists()


def test_wrong_final_hash_never_becomes_an_installed_layer(tmp_path, monkeypatch):
    fake_server(
        monkeypatch,
        lambda request: httpx.Response(
            206, content=b"WRNG", headers={"content-range": "bytes 0-3/4"}
        ),
    )
    destination = tmp_path / "ready"
    sha = hashlib.sha256(b"GOOD").hexdigest()
    work = tmp_path / "partial"
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        downloader.download_layer("https://example.test/blob", destination, 4, sha, work, workers=1)
    assert not destination.exists()
    assert not (work / f"{sha}.json").exists()  # A retry must fetch fresh pieces.
