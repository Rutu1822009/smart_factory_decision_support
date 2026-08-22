import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor


# ==================================================
# CREATE INVENTORY ML MODEL
# ==================================================

def create_inventory_model():

    history = pd.read_csv(
        "data/inventory_history.csv"
    )

    # Convert date
    history["date"] = pd.to_datetime(
        history["date"]
    )

    # Create day feature
    history["day"] = (
        history["date"] - history["date"].min()
    ).dt.days

    # Input features
    X = history[
        [
            "day",
            "material"
        ]
    ]

    # Target
    y = history["consumption"]

    # Categorical feature
    categorical_features = [
        "material"
    ]

    # Numerical feature
    numeric_features = [
        "day"
    ]

    # Preprocessor
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

    # Random Forest Regression
    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )

    # Pipeline
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

    return ml_model, history


# ==================================================
# PREDICT 7-DAY DEMAND
# ==================================================

def predict_inventory_demand():

    ml_model, history = create_inventory_model()

    # Last historical date
    latest_date = history["date"].max()

    # Starting day for future prediction
    latest_day = history["day"].max()

    results = []

    # Predict for each material
    materials = history[
        "material"
    ].unique()

    for material in materials:

        total_demand = 0

        # Predict next 7 days
        for i in range(1, 8):

            future_day = (
                latest_day + i
            )

            future_data = pd.DataFrame(
                {
                    "day": [future_day],
                    "material": [material]
                }
            )

            prediction = ml_model.predict(
                future_data
            )[0]

            total_demand += prediction

        results.append(
            {
                "material": material,
                "predicted_7_day_demand": round(
                    total_demand
                )
            }
        )

    return pd.DataFrame(results)


# ==================================================
# INVENTORY DECISION ANALYSIS
# ==================================================

def inventory_decision():

    inventory = pd.read_csv(
        "data/inventory.csv"
    )

    demand = predict_inventory_demand()

    result = inventory.merge(
        demand,
        on="material",
        how="left"
    )

    # Expected stock after 7 days
    result["expected_stock_after_7_days"] = (
        result["current_stock"]
        - result["predicted_7_day_demand"]
    )

    # Reorder quantity
    result["recommended_reorder"] = (
        result["predicted_7_day_demand"]
        + result["min_stock"]
        - result["current_stock"]
    )

    result["recommended_reorder"] = (
        result["recommended_reorder"]
        .clip(lower=0)
    )

    # Decision
    decisions = []

    for _, row in result.iterrows():

        if (
            row["expected_stock_after_7_days"]
            < row["min_stock"]
        ):

            decisions.append(
                "⚠️ Reorder Recommended"
            )

        else:

            decisions.append(
                "✅ Stock Sufficient"
            )

    result["decision"] = decisions

    return result