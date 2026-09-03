import pandas as pd


def production_agent(query=""):
    """
    Production Agent:
    Handles production-related questions such as
    total production, achievement, highest production
    and lowest production.
    """

    try:
        df = pd.read_csv("data/production.csv")

        required_columns = [
            "produced",
            "target"
        ]

        if not all(col in df.columns for col in required_columns):
            return {
                "error": "Required production columns are missing."
            }

        query = query.lower()

        # Highest production by part
        if (
            "highest production" in query
            or "highest produced" in query
            or "most produced" in query
        ):

            if "part" not in df.columns:
                return {
                    "error": "Part column is missing."
                }

            production_by_part = (
                df.groupby("part")["produced"]
                .sum()
            )

            part = production_by_part.idxmax()

            return {
                "type": "highest_production",
                "part": part,
                "production": int(production_by_part.max())
            }

        # Lowest production by part
        if (
            "lowest production" in query
            or "lowest produced" in query
            or "least produced" in query
        ):

            if "part" not in df.columns:
                return {
                    "error": "Part column is missing."
                }

            production_by_part = (
                df.groupby("part")["produced"]
                .sum()
            )

            part = production_by_part.idxmin()

            return {
                "type": "lowest_production",
                "part": part,
                "production": int(production_by_part.min())
            }

        # Achievement
        if (
            "achievement" in query
            or "target achieved" in query
            or "target" in query
        ):

            total_production = int(df["produced"].sum())
            total_target = int(df["target"].sum())

            achievement = (
                total_production / total_target
            ) * 100 if total_target > 0 else 0

            status = (
                "Production target achieved"
                if total_production >= total_target
                else "Production target not achieved"
            )

            return {
                "type": "achievement",
                "total_production": total_production,
                "total_target": total_target,
                "achievement_percentage": round(achievement, 2),
                "status": status
            }

        # General production
        total_production = int(df["produced"].sum())
        total_target = int(df["target"].sum())

        achievement = (
            total_production / total_target
        ) * 100 if total_target > 0 else 0

        status = (
            "Production target achieved"
            if total_production >= total_target
            else "Production target not achieved"
        )

        return {
            "type": "summary",
            "total_production": total_production,
            "total_target": total_target,
            "achievement_percentage": round(achievement, 2),
            "status": status
        }

    except Exception as e:
        return {
            "error": str(e)
        }