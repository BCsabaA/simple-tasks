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

def get_tasks():
    return db.read(Task, order_by=['start_date', 'priority'])

def get_task_by_id(id: int) -> Task:
    return db.read(Task, {'id': id})

def get_statuses_dict():
    statuses = db.read(Status)
    statuses_dict = {status.id: status.name for status in statuses}
    return statuses_dict

def get_status_options_list(option_id_list:dict[int]=None):
    statuses = db.read(Status)
    status_filter_list = ()
    for status in statuses:
        if option_id_list:
            if status.id in option_id_list:
                status_filter_list += ((str(status.name), status.id, True), )
            else:
                status_filter_list += ((str(status.name), status.id, ), )
        else:
            if status.name == 'not started':
                status_filter_list += ((str(status.name), status.id, True), )
            else:
                status_filter_list += ((str(status.name), status.id), )
    return status_filter_list

def get_status_ids():
    #return db.execute('select id from statuses;')
    statuses = db.read(Status)
    status_ids = []
    for status in statuses:
        status_ids.append(status.id)
    return status_ids

def get_task_comments(id: int) -> list[str]:
    db.read(Comment, filters={'id': id})
    


