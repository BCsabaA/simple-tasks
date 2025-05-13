from simple_db_handler import Database, Table, Field
from models import Task, Comment, TaskType, Status

import datetime

DATE_FORMAT = '%Y-%m-%d'

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
    if data['comment'] != '':
        create_comment_from_dict(task_id, data['comment'])

def create_comment_from_dict(task_id: int, comment: str):
    db.insert(
        Comment(
            task_id=task_id,
            text=comment
        )
    )

def update_task_status_from_dict(
        task_id: int,
        data: dict):
    db.update(
        Task,
        task_id,
        {
            'status': data['status_id'],
        }
    )

def get_tasks():
    date_today = str(datetime.date.today())
    sql = f'update tasks set status = 3 where date(deadline) < "{date_today}" and status = 1;'
    tasks = db.execute(sql)
    return db.read(Task, order_by=['start_date', 'priority'])

def get_active_tasks():
    date_today = datetime.datetime.today()
    all_tasks = get_tasks()
    active_tasks = []
    for task in all_tasks:
        if (
            datetime.datetime.strptime(task.start_date, DATE_FORMAT) <= date_today and
            datetime.datetime.strptime(task.deadline, DATE_FORMAT) >= date_today):
            active_tasks.append(task)
        if int(task.status) == 3 or int(task.status) == 2:
            active_tasks.append(task)
            print('task:', task)
            print('start date:', datetime.datetime.strptime(task.start_date, DATE_FORMAT))
            print('today', date_today)
            print('deadline:', datetime.datetime.strptime(task.deadline, DATE_FORMAT))
            print('status:', task.status, type(task.status))
    return active_tasks
    

def get_task_by_id(id: int) -> Task:
    return db.read(Task, {'id': id})[0]

def delete_task(task: Task):
    db.delete(Task, task.id)

def delete_all_tasks():
    db.execute('delete from comments')
    db.execute('delete from tasks')

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
    


