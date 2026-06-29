from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    predicted_price: float = Field(
        ...,
        description="Predicted selling price of the car in GBP (£).",
        example=12599.75
    )