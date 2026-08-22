from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER

import pandas as pd


def generate_report():

    production = pd.read_csv(
        "data/production.csv"
    )

    machines = pd.read_csv(
        "data/machines.csv"
    )

    inventory = pd.read_csv(
        "data/inventory.csv"
    )

    quality = pd.read_csv(
        "data/quality.csv"
    )

    cost = pd.read_csv(
        "data/cost.csv"
    )

    energy = pd.read_csv(
        "data/energy.csv"
    )

    # -----------------------------
    # Calculations
    # -----------------------------

    total_target = production["target"].sum()

    total_produced = production["produced"].sum()

    achievement = (
        total_produced / total_target
    ) * 100

    running = (
        machines["status"] == "Running"
    ).sum()

    total_machines = len(machines)

    low_stock = inventory[
        inventory["current_stock"]
        < inventory["min_stock"]
    ]

    total_products = quality["total"].sum()

    total_rejected = quality["rejected"].sum()

    defect_rate = (
        total_rejected / total_products
    ) * 100

    total_cost = (
        cost["material_cost"].sum()
        + cost["labor_cost"].sum()
        + cost["energy_cost"].sum()
        + cost["defect_cost"].sum()
    )

    total_energy = energy[
        "energy_kwh"
    ].sum()

    # -----------------------------
    # PDF
    # -----------------------------

    filename = "Daily_Factory_Report.pdf"

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]

    title_style.alignment = TA_CENTER

    story = []

    story.append(
        Paragraph(
            "SMART FACTORY",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Daily Factory Performance Report",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 20))

    # -----------------------------
    # KPI Table
    # -----------------------------

    data = [
        ["Parameter", "Value"],
        [
            "Total Production",
            f"{total_produced} units"
        ],
        [
            "Production Achievement",
            f"{achievement:.2f}%"
        ],
        [
            "Running Machines",
            f"{running}/{total_machines}"
        ],
        [
            "Low Stock Materials",
            str(len(low_stock))
        ],
        [
            "Defect Rate",
            f"{defect_rate:.2f}%"
        ],
        [
            "Total Production Cost",
            f"Rs. {total_cost:,.0f}"
        ],
        [
            "Total Energy Consumption",
            f"{total_energy:,.0f} kWh"
        ]
    ]

    table = Table(
        data,
        colWidths=[250, 200]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                1,
                colors.grey
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "LEFT"
            )
        ])
    )

    story.append(table)

    story.append(
        Spacer(1, 25)
    )

    # -----------------------------
    # Inventory Section
    # -----------------------------

    story.append(
        Paragraph(
            "Inventory Alerts",
            styles["Heading2"]
        )
    )

    if len(low_stock) > 0:

        for _, row in low_stock.iterrows():

            story.append(
                Paragraph(
                    f"{row['material']} - "
                    f"Current Stock: "
                    f"{row['current_stock']}",
                    styles["BodyText"]
                )
            )

    else:

        story.append(
            Paragraph(
                "No low-stock materials.",
                styles["BodyText"]
            )
        )

    story.append(
        Spacer(1, 15)
    )

    # -----------------------------
    # Machine Section
    # -----------------------------

    story.append(
        Paragraph(
            "Machine Status",
            styles["Heading2"]
        )
    )

    for _, row in machines.iterrows():

        story.append(
            Paragraph(
                f"{row['machine']} - "
                f"{row['status']} - "
                f"Downtime: "
                f"{row['downtime_hours']} hours",
                styles["BodyText"]
            )
        )

    story.append(
        Spacer(1, 15)
    )

    # -----------------------------
    # Final Recommendation
    # -----------------------------

    story.append(
        Paragraph(
            "Management Recommendation",
            styles["Heading2"]
        )
    )

    recommendation = (
        "Monitor low-stock materials, "
        "inspect machines with high downtime, "
        "and improve quality monitoring "
        "for lines with high defect rates."
    )

    story.append(
        Paragraph(
            recommendation,
            styles["BodyText"]
        )
    )

    doc.build(story)

    return filename