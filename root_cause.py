import pandas as pd


def analyze_root_causes(
    machines,
    quality,
    inventory
):

    findings = []

    # ----------------------------------
    # Machine Downtime Analysis
    # ----------------------------------

    highest_machine = machines.loc[
        machines["downtime_hours"].idxmax()
    ]

    if highest_machine["downtime_hours"] >= 10:

        findings.append(
            f"⚙️ Possible Cause: "
            f"{highest_machine['machine']} has high downtime "
            f"({highest_machine['downtime_hours']} hours). "
            f"Maintenance or machine inspection is recommended."
        )

    # ----------------------------------
    # Quality Analysis
    # ----------------------------------

    highest_defect = quality.loc[
        quality["defect_rate"].idxmax()
    ]

    if highest_defect["defect_rate"] >= 5:

        findings.append(
            f"❌ Possible Cause: "
            f"{highest_defect['line']} has a high defect rate "
            f"({highest_defect['defect_rate']}%). "
            f"Check machine calibration and quality parameters."
        )

    # ----------------------------------
    # Inventory Analysis
    # ----------------------------------

    low_stock = inventory[
        inventory["current_stock"]
        < inventory["min_stock"]
    ]

    for _, row in low_stock.iterrows():

        findings.append(
            f"📦 Possible Production Risk: "
            f"{row['material']} stock is below minimum level. "
            f"Material shortage may affect production."
        )

    # ----------------------------------
    # No Major Issue
    # ----------------------------------

    if not findings:

        findings.append(
            "✅ No major operational root-cause indicators detected."
        )

    return findings
