import pandas as pd


def generate_alerts():

    production = pd.read_csv("data/production.csv")
    machines = pd.read_csv("data/machines.csv")
    inventory = pd.read_csv("data/inventory.csv")
    quality = pd.read_csv("data/quality.csv")

    alerts = []

    # -----------------------------
    # Machine Alerts
    # -----------------------------

    stopped = machines[
        machines["status"] == "Stopped"
    ]

    for _, machine in stopped.iterrows():

        alerts.append(
            f"🔴 {machine['machine']} is stopped."
        )

    high_downtime = machines[
        machines["downtime_hours"] >= 3
    ]

    for _, machine in high_downtime.iterrows():

        alerts.append(
            f"🔴 {machine['machine']} has high downtime "
            f"of {machine['downtime_hours']} hours."
        )

    # -----------------------------
    # Inventory Alerts
    # -----------------------------

    low_inventory = inventory[
        inventory["current_stock"] < inventory["min_stock"]
    ]

    for _, material in low_inventory.iterrows():

        alerts.append(
            f"🟠 {material['material']} stock is low "
            f"({material['current_stock']} units)."
        )

    # -----------------------------
    # Quality Alerts
    # -----------------------------

    high_defects = quality[
        quality["defect_rate"] >= 8
    ]

    lines = high_defects["line"].unique()

    for line in lines:

        alerts.append(
            f"🟡 {line} has a high defect rate."
        )

    # -----------------------------
    # Production Alerts
    # -----------------------------

    daily = production.groupby("date").agg(
        target=("target", "sum"),
        produced=("produced", "sum")
    ).reset_index()

    daily["achievement"] = (
        daily["produced"] / daily["target"]
    ) * 100

    low_production_days = daily[
        daily["achievement"] < 90
    ]

    for _, day in low_production_days.iterrows():

        alerts.append(
            f"🔵 Production was below 90% "
            f"of target on {day['date']}."
        )

    return alerts


if __name__ == "__main__":

    alerts = generate_alerts()

    print("===================================")
    print("       SMART FACTORY ALERTS")
    print("===================================")

    if alerts:

        for alert in alerts:
            print(alert)

    else:
        print("No alerts. Factory is operating normally.")