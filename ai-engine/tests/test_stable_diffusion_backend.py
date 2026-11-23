import base64
from pathlib import Path
from types import SimpleNamespace

from app.services.stable_diffusion_cpp import StableDiffusionCppBackend


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        # A valid 1x1 PNG header is enough to exercise the adapter's file handling.
        png = bytes.fromhex(
            "89504e470d0a1a0a0000000d494844520000000100000001"
            "08060000001f15c4890000000b49444154789c636000020000"
            "050001a5f645400000000049454e44ae426082"
        )
        return {"data": [{"b64_json": base64.b64encode(png).decode("ascii")}]}


def test_backend_saves_png_and_returns_generation_metadata(tmp_path, monkeypatch):
    executable = tmp_path / "sd-server"
    executable.write_text("#!/bin/sh\n")
    executable.chmod(0o755)
    model = tmp_path / "model.gguf"
    model.write_bytes(b"fake-model")

    backend = StableDiffusionCppBackend(
        executable=executable,
        model_path=model,
        output_dir=tmp_path / "outputs",
    )
    backend.process = SimpleNamespace(poll=lambda: None)

    captured = {}

    def fake_post(url, json, timeout):
        captured.update(url=url, payload=json, timeout=timeout)
        return FakeResponse()

    monkeypatch.setattr("app.services.stable_diffusion_cpp.requests.post", fake_post)

    result = backend.generate(
        prompt="A cute 3D robot",
        width=512,
        height=512,
        seed=123,
        negative_prompt="blurry",
    )

    saved = Path(result["image_path"])
    assert saved.is_file()
    assert saved.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert result["seed"] == 123
    assert captured["url"].endswith("/v1/images/generations")
    assert '"seed": 123' in captured["payload"]["prompt"]
    assert captured["payload"]["negative_prompt"].startswith("blurry, ")
    assert "low quality" in captured["payload"]["negative_prompt"]


def test_backend_rejects_unsupported_resolution(tmp_path):
    backend = StableDiffusionCppBackend(
        executable=tmp_path / "missing",
        model_path=tmp_path / "missing.gguf",
        output_dir=tmp_path / "outputs",
    )
    try:
        backend.generate("A cute 3D robot", width=256, height=256)
    except ValueError as error:
        assert "512x512" in str(error)
    else:
        raise AssertionError("Expected unsupported resolution to be rejected")
