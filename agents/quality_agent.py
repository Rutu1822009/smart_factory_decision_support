import pandas as pd


def quality_agent(query=""):
    """
    Quality Agent:
    Handles quality-related questions such as
    defect rate, highest defect line and quality status.
    """

    try:
        df = pd.read_csv("data/quality.csv")

        if "defect_rate" not in df.columns:
            return {
                "error": "Defect rate column is missing."
            }

        query = query.lower()

        average_defect_rate = df["defect_rate"].mean()

        # Highest defect rate by line
        if (
            "highest defect" in query
            or "highest defect rate" in query
            or "worst quality" in query
        ):

            if "line" not in df.columns:
                return {
                    "error": "Line column is missing."
                }

            defect_by_line = (
                df.groupby("line")["defect_rate"]
                .mean()
            )

            line = defect_by_line.idxmax()

            return {
                "type": "highest_defect",
                "line": line,
                "defect_rate": round(
                    float(defect_by_line.max()), 2
                )
            }

        # Average defect rate
        if (
            "average defect" in query
            or "average defect rate" in query
            or "defect rate" in query
        ):

            return {
                "type": "average_defect",
                "average_defect_rate": round(
                    float(average_defect_rate), 2
                )
            }

        # Quality status / defects
        if (
            "quality" in query
            or "defects" in query
            or "defect" in query
        ):

            if average_defect_rate > 5:
                status = "High defect rate"
            elif average_defect_rate > 2:
                status = "Moderate defect rate"
            else:
                status = "Quality is normal"

            return {
                "type": "quality_status",
                "total_records": len(df),
                "average_defect_rate": round(
                    float(average_defect_rate), 2
                ),
                "quality_status": status
            }

        # General quality status
        if average_defect_rate > 5:
            status = "High defect rate"
        elif average_defect_rate > 2:
            status = "Moderate defect rate"
        else:
            status = "Quality is normal"

        return {
            "type": "summary",
            "total_records": len(df),
            "average_defect_rate": round(
                float(average_defect_rate), 2
            ),
            "quality_status": status
        }

    except Exception as e:
        return {
            "error": str(e)
        }