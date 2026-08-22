import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


def create_ml_model():

    production = pd.read_csv(
        "data/production.csv"
    )

    production["date"] = pd.to_datetime(
        production["date"]
    )

    # Date feature
    production["day"] = production["date"].dt.day

    # Features
    X = production[
        [
            "day",
            "target",
            "part",
            "line"
        ]
    ]

    # Target
    y = production["produced"]

    # Categorical features
    categorical_features = [
        "part",
        "line"
    ]

    # Numeric features
    numeric_features = [
        "day",
        "target"
    ]

    # Preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features
            ),
            (
                "numeric",
                "passthrough",
                numeric_features
            )
        ]
    )

    # Random Forest ML model
    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )

    # Complete ML pipeline
    ml_model = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "model",
                model
            )
        ]
    )

    # Train model
    ml_model.fit(
        X,
        y
    )

    return ml_model, production


def forecast_production():

    # Create and train ML model
    ml_model, production = create_ml_model()

    # Latest date
    latest_date = production["date"].max()

    # Next date
    next_date = (
        latest_date
        + pd.Timedelta(days=1)
    )

    # Take latest day's production records
    next_day_data = production[
        production["date"] == latest_date
    ].copy()

    # Change date to next day
    next_day_data["date"] = next_date

    next_day_data["day"] = next_date.day

    # Predict next day's production
    predicted_values = ml_model.predict(
        next_day_data[
            [
                "day",
                "target",
                "part",
                "line"
            ]
        ]
    )

    # Total production prediction
    prediction = round(
        predicted_values.sum()
    )

    return prediction


def forecast_by_part():


    # Create ML model
    ml_model, production = create_ml_model()

    # Latest date
    latest_date = production["date"].max()

    # Next date
    next_date = (
        latest_date
        + pd.Timedelta(days=1)
    )

    # Latest production records
    next_data = production[
        production["date"] == latest_date
    ].copy()

    next_data["date"] = next_date

    next_data["day"] = next_date.day

    # Prediction
    predictions = ml_model.predict(
        next_data[
            [
                "day",
                "target",
                "part",
                "line"
            ]
        ]
    )

    forecasts = pd.DataFrame({
        "part": next_data["part"].values,
        "estimated_production": [
            round(value)
            for value in predictions
        ]
    })

    return forecasts

def evaluate_model():

    ml_model, production = create_ml_model()

    X = production[
        [
            "day",
            "target",
            "part",
            "line"
        ]
    ]

    y = production["produced"]

    predictions = ml_model.predict(X)

    mae = mean_absolute_error(
        y,
        predictions
    )

    r2 = r2_score(
        y,
        predictions
    )

    return mae, r2 

def get_prediction_data():

    ml_model, production = create_ml_model()

    predictions = ml_model.predict(
        production[
            [
                "day",
                "target",
                "part",
                "line"
            ]
        ]
    )

    result = production[
        [
            "date",
            "produced"
        ]
    ].copy()

    result["predicted"] = predictions

    result = result.groupby(
        "date"
    )[[
        "produced",
        "predicted"
    ]].sum()

    result.columns = [
        "Actual Production",
        "ML Predicted Production"
    ]

    return result