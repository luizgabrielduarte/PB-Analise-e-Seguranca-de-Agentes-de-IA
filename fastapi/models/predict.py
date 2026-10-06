from pydantic import BaseModel, ConfigDict, Field


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Texto do ticket"
    )


class PredictResponse(BaseModel):
    text: str
    intent: str


class PredictionResponse(BaseModel):
    id: int
    text: str
    intent: str
    owner_id: int