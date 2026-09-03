import pandas as pd


def calculate_impact(machine_name, days):

    machines = pd.read_csv(
        "data/machines.csv"
    )

    machine = machines[
        machines["machine"] == machine_name
    ]

    if machine.empty:

        return {
            "success": False,
            "message": "Machine not found."
        }

    machine = machine.iloc[0]

    downtime_hours = float(
        machine["downtime_hours"]
    )

    shutdown_hours = days * 8

    total_downtime = (
        downtime_hours + shutdown_hours
    )

    # Production line
    if "line" in machine.index:
        line = machine["line"]
    else:
        line = "Unknown"

    # Estimate production loss
    # Assuming 8-hour production shift
    if "production_per_hour" in machine.index:

        production_per_hour = float(
            machine["production_per_hour"]
        )

        estimated_loss = (
            production_per_hour * shutdown_hours
        )

    else:

        # Fallback estimate
        estimated_loss = shutdown_hours * 100

    # Factory impact percentage
    total_production_capacity = (
        machines["downtime_hours"].sum() + 1
    )

    impact_percentage = (
        shutdown_hours
        / (total_production_capacity + shutdown_hours)
    ) * 100

    return {
        "success": True,
        "machine": machine_name,
        "line": line,
        "days": days,
        "existing_downtime": downtime_hours,
        "shutdown_hours": shutdown_hours,
        "total_downtime": total_downtime,
        "estimated_loss": int(estimated_loss),
        "impact_percentage": round(
            impact_percentage,
            2
        )
    }