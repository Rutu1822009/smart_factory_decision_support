import pandas as pd

production = pd.read_csv("data/production.csv")
machines = pd.read_csv("data/machines.csv")
inventory = pd.read_csv("data/inventory.csv")
quality = pd.read_csv("data/quality.csv")


def get_answer(question):

    question = question.lower()

    # Production
    if "production" in question or "produced" in question:
        total = production["produced"].sum()
        target = production["target"].sum()

        return (
            f"Total production is {total:,} units "
            f"against a target of {target:,} units."
        )

    # Machine
    elif "machine" in question and (
        "downtime" in question or "highest" in question
    ):
        machine = machines.loc[
            machines["downtime_hours"].idxmax(), "machine"
        ]

        downtime = machines["downtime_hours"].max()

        return (
            f"{machine} has the highest downtime "
            f"of {downtime} hours."
        )

    # Stopped machines
    elif "machine" in question and (
        "stop" in question or "closed" in question
    ):
        stopped = machines[
            machines["status"] == "Stopped"
        ]["machine"].tolist()

        return (
            "Stopped machines are: "
            + ", ".join(stopped)
        )

    # Inventory
    elif "inventory" in question or "stock" in question:
        low_stock = inventory[
            inventory["current_stock"] < inventory["min_stock"]
        ]["material"].tolist()

        if low_stock:
            return (
                "Low-stock materials are: "
                + ", ".join(low_stock)
            )

        return "All materials have sufficient stock."

    # Quality
    elif (
        "defect" in question
        or "quality" in question
        or "reject" in question
    ):
        line = quality.groupby("line")[
            "defect_rate"
        ].mean().idxmax()

        rate = quality.groupby("line")[
            "defect_rate"
        ].mean().max()

        return (
            f"{line} has the highest average "
            f"defect rate of {rate:.2f}%."
        )

    else:
        return (
            "Sorry, I could not understand the question. "
            "Try asking about production, machines, inventory or quality."
        )