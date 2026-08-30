from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Texto do ticket")


class PredictResponse(BaseModel):
    text: str
    intent: str
