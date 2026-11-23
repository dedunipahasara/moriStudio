from typing import Optional
from pydantic import BaseModel


class ModelInfo(BaseModel):
    name: str
    model_type: str
    version: str
    framework: str
    device: str
    loaded: bool
    trained: bool


class ModelStatusResponse(BaseModel):
    available: bool
    message: str
    model: Optional[ModelInfo] = None