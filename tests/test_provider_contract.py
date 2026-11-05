from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from sticker_maker.providers.base import (
    ProviderAuthError,
    ProviderCapabilityError,
    ProviderRateLimitError,
)
from sticker_maker.providers.fake import FakeStickerProvider
from sticker_maker.providers.openai_images import OpenAIImagesProvider
from sticker_maker.providers.openai_native_gif import OpenAINativeGifProvider


def test_fake_provider_contract(tmp_path: Path):
    fake = FakeStickerProvider()
    caps = fake.capabilities()
    assert caps.edit_with_reference is True
    assert caps.transparent_png is True
    assert caps.native_gif is True

    out_png = tmp_path / "anchor.png"
    fake.render_anchor([], "prompt", out_png)
    assert out_png.exists()

    out_gif = tmp_path / "test.gif"
    fake.render_native_gif("prompt", out_gif, frames=8)
    assert out_gif.exists()


def test_fake_provider_error_simulation(tmp_path: Path):
    fake_auth = FakeStickerProvider(simulate_error="auth")
    with pytest.raises(ProviderAuthError):
        fake_auth.render_anchor([], "prompt", tmp_path / "test.png")

    fake_rate = FakeStickerProvider(simulate_error="rate_limit")
    with pytest.raises(ProviderRateLimitError):
        fake_rate.render_anchor([], "prompt", tmp_path / "test.png")


def test_openai_images_auth_error(tmp_path: Path):
    # Empty api key
    provider = OpenAIImagesProvider(api_key="")
    with pytest.raises(ProviderAuthError):
        provider.render_anchor([], "prompt", tmp_path / "out.png")


def test_native_gif_downgrade_detection(tmp_path: Path):
    gif_provider = OpenAINativeGifProvider(api_key="test-key")

    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.text = '{"error": {"message": "Parameter output_format is not supported", "code": "unsupported_parameter"}}'
    mock_resp.json.return_value = {
        "error": {
            "message": "Parameter output_format is not supported",
            "code": "unsupported_parameter",
        }
    }

    with patch.object(gif_provider.session, "post", return_value=mock_resp):
        with pytest.raises(ProviderCapabilityError, match="not supported"):
            gif_provider.render_native_gif("prompt", tmp_path / "test.gif")
