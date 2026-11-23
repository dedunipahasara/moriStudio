import pytest

from app.services.style_presets import STYLE_PRESETS, build_styled_prompts, get_style


@pytest.mark.parametrize("style", list(STYLE_PRESETS))
def test_all_styles_build_nonempty_prompts(style):
    prompt, negative = build_styled_prompts("A red panda", "bad hands", style)
    assert "A red panda" in prompt
    assert STYLE_PRESETS[style].prompt_suffix in prompt
    assert "bad hands" in negative


def test_style_is_case_insensitive():
    assert get_style("PHOTOREALISTIC").key == "photorealistic"


def test_unknown_style_is_rejected():
    with pytest.raises(ValueError):
        get_style("not-a-style")
