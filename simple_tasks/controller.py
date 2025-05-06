from simple_db_handler import Database, Table, Field
from models import Task, Comment, TaskType, Status


db = Database('data/tasks.db')

def create_task_from_dict(data: dict):
    id = db.insert(
        Task(
            name = data['name'],
            description = data['description'],
            start_date = data['start_date'],
            deadline = data['deadline'],
            priority = data['priority'],
        )
    )
    if data['comment'] != '':
        db.insert(
            Comment(
                task_id=id,
                text=data['comment']
            )
        )
    return id

def get_tasks_for_main():
    # TODO: filter and sort relevant tasks
    return db.read(Task)

def get_task_by_id(id: int) -> Task:
    return db.read(Task, {'id': id})

def get_statuses_dict():
    statuses = db.read(Status)
    print(statuses)
    return #statuses_dict


