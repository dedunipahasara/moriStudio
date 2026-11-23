from fastapi import APIRouter

from app.services.style_presets import STYLE_PRESETS

router = APIRouter()


@router.get("/styles")
async def list_generation_styles():
    """List supported prompt presets for the local Stable Diffusion model."""
    return {
        "success": True,
        "styles": [
            {
                "key": preset.key,
                "label": preset.label,
                "description": preset.description,
            }
            for preset in STYLE_PRESETS.values()
        ],
        "note": (
            "Styles guide prompt wording for the installed model. They are not "
            "separate specialist models and do not guarantee artifact-free output."
        ),
    }
