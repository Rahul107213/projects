import joblib
import pandas as pd


model =  joblib.load("car_price_prediction_pipeline.pkl")


def prediction(data: dict) -> float:

    df = pd.DataFrame([data])

    pred = model.predict(df)[0]

    return round(float(pred), 2)