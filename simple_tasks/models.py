from simple_db_handler import Table, Field


class TaskType(Table):
    TABLENAME = 'task_types'
    ID = Field('id', int, primary_key=True, autoincrement=True)
    NAME = Field('name', str, unique=True)

    def __init__(self, id=None, name=""):
        self.name = name
        self.id = id
        super().__init__()

    def __str__(self):
        return f'TaskType(id={self.id}, name={self.name})'



class Status(Table):
    TABLENAME = 'statuses'
    ID = Field('id', int, primary_key=True, autoincrement=True)
    NAME = Field('name', str, unique=True)

    def __init__(self, id=None, name=""):
        self.name = name
        self.id = id
        super().__init__()

    def __str__(self):
        return f'Status(id={self.id}, name={self.name})'


class Task(Table):
    TABLENAME = 'tasks'
    ID = Field('id', int, primary_key=True, autoincrement=True)
    NAME = Field('name', str, unique=True)
    TYPE_ID = Field('type_id', int, foreign_key_table='task_types', foreign_key_column='id')
    MAIN_TASK_ID = Field('main_task_id', int)
    DESCRIPTION = Field('description', str)
    START_DATE = Field('start_date', str)
    DEADLINE = Field('deadline', str)
    PRIORITY = Field('priority', int)
    COMPLETION_DATE = Field('completion_date', str)
    STATUS = Field('status', str, foreign_key_table='statuses', foreign_key_column='id')

    def __init__(self, id:int=None, name="", type_id:int=None, main_task_id=None, description="", start_date="", deadline="", priority=0, completion_date="", status:int=1):
        self.name = name
        self.type_id = type_id
        self.main_task_id = main_task_id
        self.description = description
        self.start_date = start_date
        self.deadline = deadline
        self.priority = priority
        self.completion_date = completion_date
        self.status = status
        self.id = id
        super().__init__()

    def __str__(self):
        return f'Task(id={self.id}, name={self.name}, type id={self.type_id}, main task id={self.main_task_id}, description={self.description}, start date={self.start_date}, deadline={self.deadline}, priority={self.priority}, completion date={self.completion_date}, status={self.status})'


class Comment(Table):
    TABLENAME = 'comments'
    ID = Field('id', int, primary_key=True, autoincrement=True)
    TASK_ID = Field('task_id', int, foreign_key_table='tasks', foreign_key_column='id', on_delete= 'CASCADE', on_update='CASCADE')
    TEXT = Field('text', str)

    def __init__(self, id=None, task_id=None, text=""):
        self.task_id = task_id
        self.text = text
        self.id = id
        super().__init__()

    def __str__(self):
        return f'Comment(id={self.id}, task id={self.task_id}, text={self.text})'


class Todo(Table):
    TABLENAME = 'todos'
    ID = Field('id', int, primary_key=True, autoincrement=True)
    TASK_ID = Field('task_id', int, foreign_key_table='tasks', foreign_key_column='id', on_delete= 'CASCADE', on_update='CASCADE')
    DESCRIPTION = Field('description', str)
    DONE = Field('done', bool)

    def __init__(self, id=None, task_id=None, description='', done=False):
        self.id = id
        self.task_id = task_id
        self.description = description
        self.done = done

    def __str__(self):
        return f'Todo({self.id}, {self.task_id}, {self.description}, {self.done})'

    def __repr__(self):
        return f'Todo({self.id}, {self.task_id}, {self.description}, {self.done})'
