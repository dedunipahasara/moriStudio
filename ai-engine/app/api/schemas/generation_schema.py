from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------
# Generation Configuration
# --------------------------------------------------

MAX_PROMPT_LENGTH = 4000
MAX_SEED_VALUE = 2147483647

SUPPORTED_WIDTH = 512
SUPPORTED_HEIGHT = 512


# --------------------------------------------------
# Supported Generation Styles
# --------------------------------------------------

GenerationStyle = Literal[
    "auto",
    "photorealistic",
    "3d_cartoon",
    "anime",
    "digital_art",
    "product_photo",
]


# --------------------------------------------------
# Image Generation Request
# --------------------------------------------------

class GenerationRequest(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    prompt: str = Field(
        ...,
        min_length=3,
        max_length=MAX_PROMPT_LENGTH,
        description=(
            "Detailed description of the image to generate. "
            "Maximum 4000 characters."
        ),
        examples=[
            (
                "A beautiful anime fantasy heroine with "
                "long silver hair, violet eyes and "
                "detailed fantasy clothing."
            )
        ],
    )

    negative_prompt: str = Field(
        default="",
        max_length=MAX_PROMPT_LENGTH,
        description=(
            "Visual elements, objects or defects to avoid. "
            "Maximum 4000 characters."
        ),
    )

    style: GenerationStyle = Field(
        default="auto",
        description=(
            "Visual style preset applied to the generation prompt."
        ),
    )

    width: int = Field(
        default=SUPPORTED_WIDTH,
        ge=SUPPORTED_WIDTH,
        le=SUPPORTED_WIDTH,
        description=(
            "Image width. Currently supports 512 pixels."
        ),
    )

    height: int = Field(
        default=SUPPORTED_HEIGHT,
        ge=SUPPORTED_HEIGHT,
        le=SUPPORTED_HEIGHT,
        description=(
            "Image height. Currently supports 512 pixels."
        ),
    )

    seed: Optional[int] = Field(
        default=None,
        ge=0,
        le=MAX_SEED_VALUE,
        description=(
            "Optional random seed. "
            "Use the same seed to reproduce a generation "
            "where possible. Leave empty for a random seed."
        ),
    )


# --------------------------------------------------
# Image Generation Response
# --------------------------------------------------

class GenerationResponse(BaseModel):

    success: bool = Field(
        description=(
            "Indicates whether image generation succeeded."
        ),
    )

    generation_id: Optional[str] = Field(
        default=None,
        description=(
            "Unique identifier assigned to the generated image."
        ),
    )

    status: str = Field(
        description=(
            "Current image generation status."
        ),
    )

    message: str = Field(
        description=(
            "Image generation result message."
        ),
    )

    image_base64: Optional[str] = Field(
        default=None,
        description=(
            "Generated PNG image encoded as Base64."
        ),
    )

    mime_type: Optional[str] = Field(
        default=None,
        description=(
            "Generated image MIME type."
        ),
    )

    seed: Optional[int] = Field(
        default=None,
        description=(
            "Seed used for image generation."
        ),
    )

    style: Optional[str] = Field(
        default=None,
        description=(
            "Applied image generation style."
        ),
    )