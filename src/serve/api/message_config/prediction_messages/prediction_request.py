from pydantic import BaseModel

class PredictionRequest(BaseModel):
    features: list[float]

    class Config:
        extra = "ignore"
