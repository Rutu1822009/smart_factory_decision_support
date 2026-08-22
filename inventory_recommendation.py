import pandas as pd


def get_inventory_recommendations(inventory):

    recommendations = []

    for _, row in inventory.iterrows():

        current_stock = row["current_stock"]
        minimum_stock = row["min_stock"]
        daily_consumption = row["consumption_per_day"]

        # Stock below minimum
        if current_stock < minimum_stock:

            # Recommended stock for 7 days
            required_stock = daily_consumption * 7

            reorder_quantity = (
                required_stock + minimum_stock
                - current_stock
            )

            recommendations.append({
                "material": row["material"],
                "current_stock": current_stock,
                "minimum_stock": minimum_stock,
                "daily_consumption": daily_consumption,
                "reorder_quantity": max(
                    0,
                    int(reorder_quantity)
                ),
                "status": "Reorder Required"
            })

        else:

            recommendations.append({
                "material": row["material"],
                "current_stock": current_stock,
                "minimum_stock": minimum_stock,
                "daily_consumption": daily_consumption,
                "reorder_quantity": 0,
                "status": "Stock Healthy"
            })

    return pd.DataFrame(recommendations)