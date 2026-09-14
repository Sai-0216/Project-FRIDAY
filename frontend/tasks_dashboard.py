def build_tasks_dashboard(tasks):
    values=[]
    for task in tasks or []:
        if isinstance(task,dict):
            values.append(dict(task))
    return values


def tasks_dashboard_count(tasks):
    return len(build_tasks_dashboard(tasks))


def format_tasks_dashboard(tasks):
    values=build_tasks_dashboard(tasks)
    if not values:
        return "Tasks Dashboard is empty."
    lines=[]
    for task in values:
        name=task.get("name",task.get("title","Unnamed Task"))
        status=task.get("status","pending")
        assignee=task.get("assignee","")
        lines.append("{} - {} - {}".format(name,status,assignee))
    return chr(10).join(lines)
