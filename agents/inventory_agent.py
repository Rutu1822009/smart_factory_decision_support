import pandas as pd


def inventory_agent(query=""):
    """
    Inventory Agent:
    Handles inventory-related questions such as
    reordering, lowest stock and highest stock.
    """

    try:
        df = pd.read_csv("data/inventory.csv")

        required_columns = [
            "material",
            "current_stock",
            "min_stock"
        ]

        if not all(col in df.columns for col in required_columns):
            return {
                "error": "Required inventory columns are missing."
            }

        query = query.lower()

        result = {}

        result["total_materials"] = len(df)

        # Lowest stock
        if "lowest" in query or "least" in query:

            lowest = df.loc[df["current_stock"].idxmin()]

            return {
                "type": "lowest_stock",
                "material": lowest["material"],
                "current_stock": lowest["current_stock"],
                "min_stock": lowest["min_stock"]
            }

        # Highest stock
        if "highest" in query or "most" in query:

            highest = df.loc[df["current_stock"].idxmax()]

            return {
                "type": "highest_stock",
                "material": highest["material"],
                "current_stock": highest["current_stock"],
                "min_stock": highest["min_stock"]
            }

        # Low-stock / reordering
        low_stock = df[
            df["current_stock"] < df["min_stock"]
        ]

        result["low_stock_count"] = len(low_stock)

        result["low_stock_materials"] = low_stock[
            ["material", "current_stock", "min_stock"]
        ].to_dict(orient="records")

        if len(low_stock) > 0:
            result["status"] = "Some materials need reordering"
        else:
            result["status"] = "Inventory levels are normal"

        return result

    except Exception as e:
        return {
            "error": str(e)
        }