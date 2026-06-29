from fastapi import FastAPI
from fastapi.responses import JSONResponse

from user_input import UserInput
from prediction import prediction as predict_fn
from Response import PredictionResponse


app = FastAPI(
    title="Car Price Prediction API",
    description="Predict the selling price of a used car using a trained Machine Learning model.",
    version="1.0.0"
)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Car Price Prediction API"
    }


@app.post("/predict", response_model=PredictionResponse)
def predict_price(data: UserInput):

    user_input_dict = {
        "model": data.model,
        "year": data.year,
        "transmission": data.transmission,
        "mileage": data.mileage,
        "fuelType": data.fuelType,
        "tax": data.tax,
        "mpg": data.mpg,
        "engineSize": data.engineSize,
        "Make": data.Make
    }

    try:

        result = predict_fn(user_input_dict)

        return PredictionResponse(predicted_price=result)

    except Exception as e:

        return JSONResponse(
            status_code=500,
            content={
                "error": str(e)
            }
        )