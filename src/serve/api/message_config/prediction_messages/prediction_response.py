from pydantic import BaseModel

class PredictionResponse(BaseModel):
    prediction: float
    model_name: str
