import pandas as pd


def calculate_impact(machine_name, days):

    # -----------------------------------------
    # Load required datasets
    # -----------------------------------------

    machines = pd.read_csv("data/machines.csv")
    production = pd.read_csv("data/production.csv")
    cost = pd.read_csv("data/cost.csv")

    # -----------------------------------------
    # Find selected machine
    # -----------------------------------------

    machine_data = machines[
        machines["machine"] == machine_name
    ]

    if machine_data.empty:
        return None

    machine = machine_data.iloc[0]

    # -----------------------------------------
    # Existing downtime
    # -----------------------------------------

    existing_downtime = float(
        machine["downtime_hours"]
    )

    # -----------------------------------------
    # Shutdown calculation
    # 1 day = 8 production hours
    # -----------------------------------------

    shutdown_hours = float(days) * 8

    total_downtime = (
        existing_downtime + shutdown_hours
    )

    # -----------------------------------------
    # Production loss calculation
    # -----------------------------------------

    total_production = production[
        "produced"
    ].sum()

    total_target = production[
        "target"
    ].sum()

    total_production_days = production[
        "date"
    ].nunique()

    if total_production_days > 0:
        average_daily_production = (
            total_production /
            total_production_days
        )
    else:
        average_daily_production = 0

    # Production loss based on shutdown days
    estimated_loss = (
        average_daily_production * float(days)
    )

    # Keep loss as a whole number
    estimated_loss = int(round(estimated_loss))

    # -----------------------------------------
    # Factory production impact
    # -----------------------------------------

    if total_production > 0:

        impact_percentage = (
            estimated_loss /
            total_production
        ) * 100

    else:

        impact_percentage = 0

    # -----------------------------------------
    # Cost per unit
    # -----------------------------------------

    total_cost = 0

    cost_columns = [
        "material_cost",
        "labor_cost",
        "energy_cost",
        "defect_cost"
    ]

    for column in cost_columns:

        if column in cost.columns:

            total_cost += cost[column].sum()

    if total_production > 0:

        cost_per_unit = (
            total_cost /
            total_production
        )

    else:

        cost_per_unit = 0

    # -----------------------------------------
    # Financial impact
    # -----------------------------------------

    estimated_cost_impact = (
        estimated_loss *
        cost_per_unit
    )

    # -----------------------------------------
    # Return result
    # -----------------------------------------

    return {

        "machine": machine_name,

        "days": float(days),

        "existing_downtime": existing_downtime,

        "shutdown_hours": shutdown_hours,

        "total_downtime": total_downtime,

        "estimated_loss": estimated_loss,

        "impact_percentage": round(
            impact_percentage,
            2
        ),

        "cost_per_unit": round(
            cost_per_unit,
            2
        ),

        "estimated_cost_impact": round(
            estimated_cost_impact,
            2
        )
    }