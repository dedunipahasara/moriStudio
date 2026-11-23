from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class StylePreset:
    key: str
    label: str
    prompt_suffix: str
    negative_suffix: str
    description: str


STYLE_PRESETS: Dict[str, StylePreset] = {

    # --------------------------------------------------
    # AUTO
    # --------------------------------------------------

    "auto": StylePreset(
        key="auto",
        label="Auto",
        prompt_suffix=(
            "high quality, coherent composition, clear subject, "
            "well-defined details"
        ),
        negative_suffix=(
            "low quality, blurry, pixelated, malformed, "
            "artifacts, watermark, text"
        ),
        description="Use the prompt's own visual direction.",
    ),

    # --------------------------------------------------
    # PHOTOREALISTIC
    # --------------------------------------------------

    "photorealistic": StylePreset(
        key="photorealistic",
        label="Photorealistic",
        prompt_suffix=(
            "photorealistic professional photography, "
            "natural realistic materials and skin texture, "
            "fine hair strands, physically plausible lighting, "
            "natural color grading, crisp subject detail, "
            "realistic shadows, detailed photographic texture, "
            "sharp focus"
        ),
        negative_suffix=(
            "3d render, CGI, cartoon, anime, illustration, doll, "
            "plastic skin, waxy skin, over-smoothed face, "
            "painterly, artificial face, blurry, low detail, "
            "deformed anatomy"
        ),
        description=(
            "Natural-looking photography, portraits, animals "
            "and environments."
        ),
    ),

    # --------------------------------------------------
    # 3D CARTOON
    # --------------------------------------------------

    "3d_cartoon": StylePreset(
        key="3d_cartoon",
        label="3D Cartoon",
        prompt_suffix=(
            "high-end 3D animated character render, "
            "appealing stylized character design, "
            "carefully sculpted forms, detailed soft materials, "
            "finely rendered surface textures, expressive eyes, "
            "professional animation-film lighting, "
            "global illumination, soft contact shadows, "
            "clean polished 3D render, sharp details"
        ),
        negative_suffix=(
            "flat 2d illustration, sketch, line art, low-poly, "
            "crude geometry, plastic-looking flat surfaces, "
            "blurry, noisy, distorted face, malformed hands, "
            "extra limbs, artifacts"
        ),
        description=(
            "Stylized 3D characters, cute animals and animated scenes."
        ),
    ),

    # --------------------------------------------------
    # ANIME
    # --------------------------------------------------

    "anime": StylePreset(
        key="anime",
        label="Anime",
        prompt_suffix=(
            "high-quality anime character illustration, "
            "refined anime art direction, clean confident linework, "
            "expressive detailed eyes, carefully rendered hair, "
            "beautiful cel shading, rich but balanced colors, "
            "polished professional anime artwork"
        ),
        negative_suffix=(
            "photograph, photorealistic skin, 3d CGI, muddy linework, "
            "rough sketch, poorly drawn face, asymmetrical eyes, "
            "extra fingers, blurry, low quality, artifacts, watermark"
        ),
        description=(
            "Anime characters and polished 2D anime illustrations."
        ),
    ),

    # --------------------------------------------------
    # DIGITAL ART
    # --------------------------------------------------

    "digital_art": StylePreset(
        key="digital_art",
        label="Digital Art",
        prompt_suffix=(
            "professional digital concept art, refined composition, "
            "intentional color palette, detailed forms, "
            "controlled painterly rendering, crisp focal subject, "
            "polished artwork"
        ),
        negative_suffix=(
            "unfinished sketch, messy composition, muddy colors, "
            "blurry, low quality, artifacts"
        ),
        description=(
            "Fantasy scenes, concept art and stylized illustrations."
        ),
    ),

    # --------------------------------------------------
    # PRODUCT PHOTOGRAPHY
    # --------------------------------------------------

    "product_photo": StylePreset(
        key="product_photo",
        label="Product Photography",
        prompt_suffix=(
            "premium commercial product photography, "
            "accurate product geometry, clean studio setup, "
            "professional softbox lighting, realistic material "
            "reflections, subtle grounded shadow, crisp edges, "
            "neutral uncluttered background, sharp focus"
        ),
        negative_suffix=(
            "cartoon, anime, illustration, 3d toy appearance, "
            "distorted product shape, extra objects, text, "
            "watermark, blurry, low resolution, artifacts"
        ),
        description=(
            "Clean product images with studio-style lighting."
        ),
    ),
}


# --------------------------------------------------
# GET AVAILABLE STYLES
# --------------------------------------------------

def get_available_styles() -> list[dict]:
    """
    Return all available styles for frontend/API use.
    """

    return [
        {
            "key": preset.key,
            "label": preset.label,
            "description": preset.description,
        }
        for preset in STYLE_PRESETS.values()
    ]


# --------------------------------------------------
# GET STYLE PRESET
# --------------------------------------------------

def get_style(style: str = "auto") -> StylePreset:
    """
    Retrieve a style preset by its key.
    """

    if not isinstance(style, str):
        raise ValueError("Style must be a string.")

    key = style.strip().lower() or "auto"

    try:
        return STYLE_PRESETS[key]

    except KeyError as exc:
        available = ", ".join(STYLE_PRESETS.keys())

        raise ValueError(
            f"Unsupported style '{style}'. "
            f"Available styles: {available}."
        ) from exc


# --------------------------------------------------
# BUILD STYLED PROMPTS
# --------------------------------------------------

def build_styled_prompts(
    prompt: str,
    negative_prompt: str = "",
    style: str = "auto",
) -> tuple[str, str]:
    """
    Combine the user's prompts with the selected style preset.

    Returns:
        tuple[str, str]: enhanced positive prompt,
                         enhanced negative prompt.
    """

    if not isinstance(prompt, str):
        raise ValueError("Prompt must be a string.")

    if not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    if not isinstance(negative_prompt, str):
        raise ValueError("Negative prompt must be a string.")

    preset = get_style(style)

    # Build positive prompt.
    enhanced_prompt = ", ".join(
        part
        for part in (
            prompt.strip(),
            preset.prompt_suffix.strip(),
        )
        if part
    )

    # Build negative prompt.
    negative_parts = [
        part.strip()
        for part in (
            negative_prompt,
            preset.negative_suffix,
        )
        if part and part.strip()
    ]

    enhanced_negative = ", ".join(
        negative_parts
    )

    return enhanced_prompt, enhanced_negative
