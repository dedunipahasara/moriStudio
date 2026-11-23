from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class TrainingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    epochs: int = Field(default=5, ge=1, le=100)
    batch_size: int = Field(default=1, ge=1, le=8)
    learning_rate: float = Field(default=0.0002, gt=0, le=0.01)


class TrainingResponse(BaseModel):
    success: bool
    status: str
    message: str
    training_id: Optional[str] = None


class TrainingStatusResponse(BaseModel):
    status: str
    current_epoch: int = 0
    total_epochs: int = 0
    message: str