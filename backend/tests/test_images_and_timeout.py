"""Test image-size, orientation and timeout boundaries that matter on a laptop.
Copyright (c) 2026 Imarah.tech. All rights reserved.
"""

import io
import subprocess

import pytest
from PIL import Image

from backend.app.services import vlm
from backend.app.services.images import clean_image


def test_large_pixel_count_is_rejected_before_full_decode(tmp_path):
    output = io.BytesIO()
    Image.new("RGB", (5001, 4000), "grey").save(output, "JPEG")
    with pytest.raises(ValueError, match="20 megapixels"):
        clean_image(output.getvalue(), tmp_path / "result.jpg")


def test_orientation_and_camera_metadata_are_handled(tmp_path):
    output = io.BytesIO()
    source = Image.new("RGB", (100, 50), "grey")
    exif = source.getexif()
    exif[274] = 6  # Camera stored the image rotated 90 degrees.
    exif[271] = "Test camera"
    source.save(output, "JPEG", exif=exif)
    destination = tmp_path / "clean.jpg"
    assert clean_image(output.getvalue(), destination) == {"width": 50, "height": 100}
    with Image.open(destination) as cleaned:
        assert not cleaned.getexif()


@pytest.mark.parametrize("configured,seconds", [(None, 300), ("2", 2)])
def test_timeout_becomes_a_useful_model_error(tmp_path, monkeypatch, configured, seconds):
    monkeypatch.delenv("VLM_TIMEOUT_SECONDS", raising=False)
    if configured is not None:
        monkeypatch.setenv("VLM_TIMEOUT_SECONDS", configured)
    target = tmp_path / "models/smolvlm-256m"
    target.mkdir(parents=True)
    (target / "READY").write_text("test-only marker")
    monkeypatch.setattr(vlm, "PROJECT", tmp_path)

    def timeout(*args, **kwargs):
        assert kwargs["timeout"] == seconds
        assert kwargs["env"]["HF_HUB_OFFLINE"] == "1"
        raise subprocess.TimeoutExpired("test worker", seconds)

    monkeypatch.setattr(vlm.subprocess, "run", timeout)
    with pytest.raises(ValueError, match="exceeded its time limit"):
        vlm.run_vlm("smolvlm-256m", tmp_path / "photo.jpg")


@pytest.mark.parametrize("value", ["0", "nan", "inf", "not-a-number"])
def test_invalid_timeout_cannot_disable_the_worker_limit(tmp_path, monkeypatch, value):
    monkeypatch.setenv("VLM_TIMEOUT_SECONDS", value)
    with pytest.raises(ValueError, match="positive number"):
        vlm.run_vlm("smolvlm-256m", tmp_path / "photo.jpg")
