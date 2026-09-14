def build_goals_dashboard(goals):
    values=[]
    for goal in goals or []:
        if isinstance(goal,dict):
            values.append(dict(goal))
    return values


def goals_dashboard_count(goals):
    return len(build_goals_dashboard(goals))


def format_goals_dashboard(goals):
    values=build_goals_dashboard(goals)
    if not values:
        return "Goals Dashboard is empty."
    lines=[]
    for goal in values:
        name=goal.get("name",goal.get("title","Unnamed Goal"))
        status=goal.get("status","pending")
        progress=goal.get("progress",0)
        lines.append("{} - {} - {}%".format(name,status,progress))
    return chr(10).join(lines)
