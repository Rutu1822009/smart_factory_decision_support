from agents.production_agent import production_agent
from agents.machine_agent import machine_agent
from agents.inventory_agent import inventory_agent
from agents.quality_agent import quality_agent


def factory_manager_agent():
    """
    Factory Manager Agent:
    Collects results from all factory agents
    and generates an overall decision.
    """

    production = production_agent()
    machine = machine_agent()
    inventory = inventory_agent()
    quality = quality_agent()

    result = {
        "production": production,
        "machine": machine,
        "inventory": inventory,
        "quality": quality
    }

    recommendations = []

    # Production decision
    if production.get("achievement_percentage", 100) < 100:
        recommendations.append(
            "Production target is not achieved. "
            "Review production performance."
        )

    # Machine decision
    if machine.get("machines_requiring_attention", 0) > 0:
        recommendations.append(
            "Some machines require attention. "
            "Inspect or schedule maintenance."
        )

    # Inventory decision
    if inventory.get("low_stock_count", 0) > 0:
        recommendations.append(
            "Low-stock materials detected. "
            "Reorder required materials."
        )

    # Quality decision
    if quality.get("average_defect_rate", 0) > 2:
        recommendations.append(
            "Defect rate is above the preferred level. "
            "Perform quality inspection."
        )

    if not recommendations:
        recommendations.append(
            "Factory conditions are normal. "
            "No immediate action is required."
        )

    result["recommendations"] = recommendations

    return result