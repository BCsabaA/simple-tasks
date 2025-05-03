from simple_db_handler import Database, Table, Field
from models import Task, Comment, TaskType, Status


db = Database('simple_tasks/data/tasks.db')

init_task = Task(name='Task 1', type_id=1, description='Description 1', start_date='2021-01-01', deadline='2021-01-02', priority=1, status=1)
init_task2 = Task(name='Task 2', type_id=1, description='Description 2', start_date='2021-02-04', deadline='2021-02-10', priority=1, status=1)
init_task3 = Task(name='Task 3', type_id=1, description='Description 3', start_date='2021-05-07', deadline='2021-05-30', priority=1, status=1)
db.insert_many([init_task, init_task2, init_task3])
init_comment = Comment(task_id=1, text='Comment 1')
init_comment2 = Comment(task_id=1, text='Comment 2')
init_comment3 = Comment(task_id=2, text='Comment 3')
db.insert_many([init_comment, init_comment2, init_comment3])


