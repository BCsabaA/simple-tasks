from simple_db_handler import Database, Table, Field
from models import Task, Comment, TaskType, Status

import datetime


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
        create_comment_from_dict(id, data['comment'])
    return id

def update_task_from_dict(task_id: int, data: dict):
    db.update(
        Task,
        task_id,
        {
            'name': data['name'],
            'description': data['description'],
            'start_date': data['start_date'],
            'deadline': data['deadline'],
            'priority': data['priority'],
            'status': data['status_id'],
        }
    )
    print('update_task_from_dict')
    print(data)
    if data['comment'] != '':
        create_comment_from_dict(task_id, data['comment'])

def create_comment_from_dict(task_id: int, comment: str):
    db.insert(
        Comment(
            task_id=task_id,
            text=comment
        )
    )

def update_task_status_from_dict(task_id: int, data: dict):
    print('***** update_task_status_from_dict *****')
    print(task_id)
    print(data)
    db.update(
        Task,
        task_id,
        {
            'status': data['status_id'],
        }
    )

def get_tasks():
    date_today = str(datetime.date.today())
    print(date_today)
    sql = f'update tasks set status = 3 where date(start_date) < "{date_today}" and status = 1;'
    print(sql)
    tasks = db.execute(sql)
    print(tasks)
    return db.read(Task, order_by=['start_date', 'priority'])

def get_task_by_id(id: int) -> Task:
    return db.read(Task, {'id': id})[0]

def delete_task(task: Task):
    db.delete(Task, task.id)

def get_statuses_dict():
    statuses = db.read(Status)
    statuses_dict = {status.id: status.name for status in statuses}
    return statuses_dict

def get_status_options_list(option_id_list:dict[int]=None, task:Task=None):
    statuses = db.read(Status)
    status_filter_list = ()
    for status in statuses:
        if option_id_list:
            if status.id in option_id_list:
                status_filter_list += ((str(status.name), status.id, True), )
            else:
                status_filter_list += ((str(status.name), status.id, ), )
        elif task:
            if str(status.id).__eq__(str(task.status)) or status.id == task.status:
                status_filter_list += ((str(status.name), status.id, True), )
            else:
                status_filter_list += ((str(status.name), status.id), )
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
    return db.read(Comment, filters={'task_id': id})
    


