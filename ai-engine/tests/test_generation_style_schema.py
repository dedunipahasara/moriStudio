import pytest
from pydantic import ValidationError

from app.api.schemas.generation_schema import GenerationRequest


def test_style_defaults_to_auto_for_existing_clients():
    request = GenerationRequest(prompt="A red panda")
    assert request.style == "auto"


@pytest.mark.parametrize(
    "style",
    ["auto", "photorealistic", "3d_cartoon", "anime", "digital_art", "product_photo"],
)
def test_supported_styles_are_accepted(style):
    request = GenerationRequest(prompt="A red panda", style=style)
    assert request.style == style


def test_unknown_style_is_rejected():
    with pytest.raises(ValidationError):
        GenerationRequest(prompt="A red panda", style="unknown")
