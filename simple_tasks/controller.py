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
    

