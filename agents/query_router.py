def route_query(query):
    """
    Routes the user's question to the most relevant agent.
    """

    query = query.lower()

    if any(word in query for word in [
        "inventory", "stock", "material", "reorder",
        "shortage", "low stock"
    ]):
        return "inventory"

    elif any(word in query for word in [
        "machine", "failure", "fault", "maintenance",
        "stopped", "downtime"
    ]):
        return "machine"

    elif any(word in query for word in [
        "production", "target", "produced", "forecast",
        "output"
    ]):
        return "production"

    elif any(word in query for word in [
        "quality", "defect", "defects", "defect rate",
        "quality rate"
    ]):
        return "quality"

    elif any(word in query for word in [
        "why", "reason", "problem", "issue",
        "cause", "overall", "factory"
    ]):
        return "factory_manager"

    else:
        return "factory_manager"