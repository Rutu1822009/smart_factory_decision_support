import pandas as pd


# ==================================================
# MACHINE FAILURE RISK ANALYSIS
# ==================================================

def predict_machine_risk():

    machines = pd.read_csv(
        "data/machines.csv"
    )

    # Convert maintenance date
    machines["maintenance_due"] = pd.to_datetime(
        machines["maintenance_due"]
    )

    # Current date
    today = pd.Timestamp.today().normalize()

    # Days since maintenance due
    machines["days_overdue"] = (
        today - machines["maintenance_due"]
    ).dt.days

    # Negative values mean maintenance is not overdue
    machines["days_overdue"] = (
        machines["days_overdue"].clip(lower=0)
    )

    risk_levels = []
    recommendations = []

    for _, row in machines.iterrows():

        score = 0

        # Downtime risk
        if row["downtime_hours"] >= 15:
            score += 3

        elif row["downtime_hours"] >= 8:
            score += 2

        elif row["downtime_hours"] >= 4:
            score += 1

        # Machine stopped
        if row["status"] == "Stopped":
            score += 3

        # Maintenance overdue
        if row["days_overdue"] > 7:
            score += 3

        elif row["days_overdue"] > 0:
            score += 2

        # Risk level
        if score >= 5:

            risk = "🔴 High"

            recommendation = (
                "Immediate inspection and preventive "
                "maintenance recommended."
            )

        elif score >= 2:

            risk = "🟠 Medium"

            recommendation = (
                "Schedule maintenance and monitor "
                "machine performance."
            )

        else:

            risk = "🟢 Low"

            recommendation = (
                "Machine condition appears normal. "
                "Continue regular monitoring."
            )

        risk_levels.append(risk)
        recommendations.append(
            recommendation
        )

    machines["failure_risk"] = risk_levels

    machines["recommendation"] = (
        recommendations
    )

    return machines