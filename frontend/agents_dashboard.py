def build_agents_dashboard(agents):
    values=[]
    for agent in agents or []:
        if isinstance(agent,dict):
            values.append(dict(agent))
    return values


def agents_dashboard_count(agents):
    return len(build_agents_dashboard(agents))


def format_agents_dashboard(agents):
    values=build_agents_dashboard(agents)
    if not values:
        return "Agents Dashboard is empty."
    lines=[]
    for agent in values:
        name=agent.get("name",agent.get("id","Unnamed Agent"))
        status=agent.get("status","idle")
        role=agent.get("role","agent")
        lines.append("{} - {} - {}".format(name,status,role))
    return chr(10).join(lines)
