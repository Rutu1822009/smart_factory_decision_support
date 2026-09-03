import pandas as pd


def machine_agent(query=""):
    """
    Machine Agent:
    Handles machine status, downtime and maintenance-related questions.
    """

    try:
        df = pd.read_csv("data/machines.csv")

        required_columns = [
            "machine",
            "status",
            "downtime_hours"
        ]

        if not all(col in df.columns for col in required_columns):
            return {
                "error": "Required machine columns are missing."
            }

        query = query.lower()

        # Highest downtime
        if "highest downtime" in query or (
            "highest" in query and "downtime" in query
        ):
            machine = df.loc[df["downtime_hours"].idxmax()]

            return {
                "type": "highest_downtime",
                "machine": machine["machine"],
                "downtime_hours": machine["downtime_hours"],
                "status": machine["status"]
            }

        # Stopped machines
        if "stopped" in query or "which machines are stopped" in query:
            stopped = df[df["status"].str.lower() == "stopped"]

            return {
                "type": "stopped_machines",
                "machines": stopped[
                    ["machine", "downtime_hours"]
                ].to_dict(orient="records")
            }

        # Maintenance / attention
        if (
            "maintenance" in query
            or "need attention" in query
            or "needs attention" in query
        ):
            attention = df[
                (df["status"].str.lower() == "stopped")
                | (df["downtime_hours"] > 0)
            ]

            return {
                "type": "maintenance",
                "machines": attention[
                    ["machine", "status", "downtime_hours"]
                ].to_dict(orient="records")
            }

        # General machine status
        status_summary = df["status"].value_counts().to_dict()

        stopped_count = len(
            df[df["status"].str.lower() == "stopped"]
        )

        return {
            "type": "summary",
            "total_machines": len(df),
            "status_summary": status_summary,
            "machines_requiring_attention": stopped_count
        }

    except Exception as e:
        return {
            "error": str(e)
        }