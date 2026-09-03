from agents.query_router import route_query
from agents.inventory_agent import inventory_agent
from agents.machine_agent import machine_agent
from agents.production_agent import production_agent
from agents.quality_agent import quality_agent
from agents.factory_manager_agent import factory_manager_agent


def format_inventory(result):
    if "error" in result:
        return f"Inventory Agent error: {result['error']}"

    if result.get("type") == "lowest_stock":
        return (
            f"📦 **Lowest Stock Material**\n\n"
            f"- Material: **{result['material']}**\n"
            f"- Current stock: **{result['current_stock']}**\n"
            f"- Minimum stock: **{result['min_stock']}**\n\n"
            f"💡 **Recommendation:** This material should be prioritized for reordering."
        )

    if result.get("type") == "highest_stock":
          return (
            f"📦 **Highest Stock Material**\n\n"
            f"- Material: **{result['material']}**\n"
            f"- Current stock: **{result['current_stock']}**\n"
            f"- Minimum stock: **{result['min_stock']}**\n\n"
            f"💡 **Status:** This material currently has the highest stock level."
        )

    materials = result.get("low_stock_materials", [])

    if not materials:
        return "✅ All materials have sufficient stock. No reordering is required."

    answer = f"📦 **{len(materials)} materials need reordering:**\n\n"

    for item in materials:
        answer += (
            f"- **{item['material']}** — "
            f"Current stock: {item['current_stock']}, "
            f"Minimum stock: {item['min_stock']}\n"
        )

    answer += "\n💡 **Recommendation:** Reorder these materials to avoid stock shortages."

    return answer


def format_machine(result):
    if "error" in result:
        return f"Machine Agent error: {result['error']}"

    # Highest downtime
    if result.get("type") == "highest_downtime":
        return (
            f"⚙️ **Highest Downtime Machine**\n\n"
            f"- Machine: **{result['machine']}**\n"
            f"- Downtime: **{result['downtime_hours']} hours**\n"
            f"- Status: **{result['status']}**\n\n"
            f"💡 **Recommendation:** Inspect this machine and perform maintenance if required."
        )

    # Stopped machines
    if result.get("type") == "stopped_machines":
        machines = result.get("machines", [])

        if not machines:
            return "✅ No machines are currently stopped."

        answer = "🛑 **Stopped Machines**\n\n"

        for machine in machines:
            answer += (
                f"- **{machine['machine']}** — "
                f"Downtime: {machine['downtime_hours']} hours\n"
            )

        answer += (
            "\n💡 **Recommendation:** "
            "Check the stopped machines and perform maintenance."
        )

        return answer

    # Maintenance
    if result.get("type") == "maintenance":
        machines = result.get("machines", [])

        if not machines:
            return "✅ No machines currently require maintenance attention."

        answer = "🛠️ **Machines Requiring Attention**\n\n"

        for machine in machines:
            answer += (
                f"- **{machine['machine']}** — "
                f"Status: {machine['status']}, "
                f"Downtime: {machine['downtime_hours']} hours\n"
            )

        answer += (
            "\n💡 **Recommendation:** "
            "Inspect these machines and schedule maintenance."
        )

        return answer

    # General machine status
    status = result.get("status_summary", {})
    attention = result.get("machines_requiring_attention", 0)

    return (
        f"⚙️ **Machine Status**\n\n"
        f"- Total machines: **{result.get('total_machines', 0)}**\n"
        f"- Running: **{status.get('Running', 0)}**\n"
        f"- Stopped: **{status.get('Stopped', 0)}**\n"
        f"- Machines requiring attention: **{attention}**"
    )


def format_production(result):
    if "error" in result:
        return f"Production Agent error: {result['error']}"

    # Highest production
    if result.get("type") == "highest_production":
        return (
            f"🏭 **Highest Production Part**\n\n"
            f"- Part: **{result['part']}**\n"
            f"- Production: **{result['production']:,} units**\n\n"
            f"💡 **Status:** This part has the highest production output."
        )

    # Lowest production
    if result.get("type") == "lowest_production":
        return (
            f"🏭 **Lowest Production Part**\n\n"
            f"- Part: **{result['part']}**\n"
            f"- Production: **{result['production']:,} units**\n\n"
            f"💡 **Recommendation:** Review the production performance of this part."
        )

    # Achievement
    if result.get("type") == "achievement":
        return (
            f"🏭 **Production Achievement**\n\n"
            f"- Total production: **{result['total_production']:,} units**\n"
            f"- Target: **{result['total_target']:,} units**\n"
            f"- Achievement: **{result['achievement_percentage']:.1f}%**\n"
            f"- Status: **{result['status']}**"
        )

    # General production status
    achievement = result.get("achievement_percentage", 0)

    return (
        f"🏭 **Production Status**\n\n"
        f"- Total production: **{result.get('total_production', 0):,} units**\n"
        f"- Target: **{result.get('total_target', 0):,} units**\n"
        f"- Achievement: **{achievement:.1f}%**\n"
        f"- Status: **{result.get('status', 'Unknown')}**"
    )


def format_quality(result):
    if "error" in result:
        return f"Quality Agent error: {result['error']}"

    # Highest defect line
    if result.get("type") == "highest_defect":
        return (
            f"🔍 **Highest Defect Rate Line**\n\n"
            f"- Line: **{result['line']}**\n"
            f"- Average defect rate: **{result['defect_rate']:.2f}%**\n\n"
            f"💡 **Recommendation:** Inspect this production line and identify the root cause of defects."
        )

    # Average defect rate
    if result.get("type") == "average_defect":
        return (
            f"🔍 **Average Defect Rate**\n\n"
            f"- Average defect rate: **{result['average_defect_rate']:.2f}%**\n\n"
            f"💡 **Status:** Monitor quality performance regularly."
        )

    # Quality status
    if result.get("type") == "quality_status":
        return (
            f"🔍 **Quality Status**\n\n"
            f"- Quality records: **{result['total_records']}**\n"
            f"- Average defect rate: **{result['average_defect_rate']:.2f}%**\n"
            f"- Status: **{result['quality_status']}**"
        )

    # General quality status
    return (
        f"🔍 **Quality Status**\n\n"
        f"- Quality records: **{result.get('total_records', 0)}**\n"
        f"- Average defect rate: **{result.get('average_defect_rate', 0):.2f}%**\n"
        f"- Status: **{result.get('quality_status', 'Unknown')}**"
    )


def format_factory(result):
    if "error" in result:
        return f"Factory Manager Agent error: {result['error']}"

    production = result.get("production", {})
    machine = result.get("machine", {})
    inventory = result.get("inventory", {})
    quality = result.get("quality", {})
    recommendations = result.get("recommendations", [])

    machine_status = machine.get("status_summary", {})

    answer = (
        "🏭 **Overall Factory Status**\n\n"
        f"### 🏭 Production\n"
        f"- Production: **{production.get('total_production', 0):,} / "
        f"{production.get('total_target', 0):,} units**\n"
        f"- Achievement: **{production.get('achievement_percentage', 0):.1f}%**\n"
        f"- Status: **{production.get('status', 'Unknown')}**\n\n"
        
        f"### ⚙️ Machines\n"
        f"- Total: **{machine.get('total_machines', 0)}**\n"
        f"- Running: **{machine_status.get('Running', 0)}**\n"
        f"- Stopped: **{machine_status.get('Stopped', 0)}**\n\n"

        f"### 📦 Inventory\n"
        f"- Total materials: **{inventory.get('total_materials', 0)}**\n"
        f"- Low-stock materials: **{inventory.get('low_stock_count', 0)}**\n\n"

        f"### 🔍 Quality\n"
        f"- Average defect rate: **{quality.get('average_defect_rate', 0):.2f}%**\n"
        f"- Status: **{quality.get('quality_status', 'Unknown')}**\n"
    )

    if recommendations:
        answer += "\n### 🤖 Recommendations\n"
        for recommendation in recommendations:
            answer += f"- {recommendation}\n"

    return answer


def run_agent(query):
    """
    Main controller for routing user queries
    to the appropriate factory agent.
    """

    agent = route_query(query)

    if agent == "inventory":
        result = inventory_agent(query)
        return format_inventory(result)

    elif agent == "machine":
        result = machine_agent(query)
        return format_machine(result)

    elif agent == "production":
        result = production_agent(query)
        return format_production(result)

    elif agent == "quality":
        result = quality_agent(query)
        return format_quality(result)

    elif agent == "factory_manager":
        result = factory_manager_agent()
        return format_factory(result)

    else:
        return "❌ No suitable agent found for this question."