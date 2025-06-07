# to_do.py
to_do_list = []

def add_task(task):
    to_do_list.append(task)
    return f"Task added: {task}"

def remove_task(task):
    if task in to_do_list:
        to_do_list.remove(task)
        return f"Task removed: {task}"
    return f"Task not found: {task}"

def list_tasks():
    if not to_do_list:
        return "No tasks in your to-do list."
    return "Your tasks:\n" + "\n".join(f"{idx+1}. {task}" for idx, task in enumerate(to_do_list))
