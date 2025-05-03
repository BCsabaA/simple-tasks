import sqlite3
import logging # TODO add logging
from set_logger import set_logger


LOGGER = set_logger(__name__)


class Database():

    DATABASE = None
    TABLES = []
    def __init__(self, db_name):
        if Database.DATABASE:
            LOGGER.info('class Database: __init__(): Database already exists')
            self.db_name = Database.DATABASE.db_name
            self.conn = Database.DATABASE.conn
            self.cursor = Database.DATABASE.cursor
            return
        self.db_name = db_name
        Database.DATABASE = self
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        # get table names from the database
        Database.TABLES = [self.cursor.execute(f'SELECT name FROM sqlite_master WHERE type="table"').fetchall()[i][0] for i in range(len(self.cursor.execute(f'SELECT name FROM sqlite_master WHERE type="table"').fetchall()))]
        self.close()
        LOGGER.info('class Database: __init__(): Database created')

    def close(self):
        self.conn.close()
        LOGGER.info('class Database: close(): Database closed')

    def commit(self):
        self.conn.commit()
        LOGGER.info(f'class Database: commit(): Database committed')

    def open(self):
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        LOGGER.info(f'class Database: open(): Database opened')

    def rollback(self):
        self.conn.rollback()
        LOGGER.info(f'class Database: rollback(): Database rolled back')

    def execute(self, query):
        if not Database.DATABASE:
            LOGGER.info('class Database: execute(): No database, returning')
            return
        Database.DATABASE.open()
        data = Database.DATABASE.cursor.execute(query).fetchall()
        Database.DATABASE.commit()
        Database.DATABASE.close()
        LOGGER.info(f'class Database: execute(): {query} executed')
        return data

    def read(self, obj_class, filters: dict=None, order_by: list=None):
        table = obj_class.TABLENAME
        if table not in Database.TABLES:
            LOGGER.info(f'class Database: read_table(): {table} not in Database.TABLES')
            return []
        if filters is None:
            filters = {}
        columns = [column for column in obj_class.__dict__.keys() if isinstance(obj_class.__dict__[column], Field)]
        if order_by is None:
            order_by = []
        create_read_query = f'SELECT {", ".join(columns)} FROM {table}'
        if filters:
            create_read_query += ' WHERE '
            for key, value in filters.items():
                create_read_query += f'{key} LIKE ? AND '
            create_read_query = create_read_query[:-5]
        if order_by:
            create_read_query += ' ORDER BY '
            for key in order_by:
                create_read_query += f'{key} ASC, '
            create_read_query = create_read_query[:-2]
        LOGGER.info(f'class Database: read_table(): create_read_query: {create_read_query}')
        if not Database.DATABASE:
            LOGGER.info('class Database: read_table(): No database, returning')
            return
        Database.DATABASE.open()
        Database.DATABASE.cursor.execute(create_read_query, tuple(filters.values()))
        rows = Database.DATABASE.cursor.fetchall()
        Database.DATABASE.close()
        print(columns)
        print(create_read_query)
        print(rows)
        for row in rows:
            print(*row)
        LOGGER.info(f'class Database: read_table(): {table} read')
        return [obj_class(*row) for row in rows]

    def insert(self,obj):
        table = obj.__class__.TABLENAME
        if table not in Database.TABLES:
            obj.parse_object_to_table()
        if obj.__dict__.get('id') == None:
            obj.insert_instance_in_database()

    def insert_many(self, objs):
        objs_create_table = [obj for obj in objs if obj.__class__.TABLENAME not in Database.TABLES]
        for obj in objs_create_table:
            obj.parse_object_to_table()
        for obj in objs:
            if obj.__dict__.get('id') == None:
                obj.insert_instance_in_database()

    def update(self, obj_class, id, data: dict):
        create_update_query = f'UPDATE {obj_class.TABLENAME} SET {", ".join([f'{key}=?' for key in data.keys()])} WHERE id=?'
        if not Database.DATABASE:
            LOGGER.info('class Database: update(): No database, returning')
            return
        Database.DATABASE.open()
        Database.DATABASE.cursor.execute(create_update_query, tuple(data.values()) + (id,))
        Database.DATABASE.commit()
        Database.DATABASE.close()
        LOGGER.info(f'class Database: update(): {obj_class.TABLENAME} {id} updated')

    def delete(self, obj_class, id):
        self.update(obj_class, id, {'deleted': True})
        LOGGER.info(f'class Database: delete(): {obj_class.TABLENAME} {id} deleted')

    def __str__(self):
        return f'Database(name={self.db_name}, tables={self.TABLES} connection={self.conn}, cursor={self.cursor})'


class Table():

    type_map = {
        int: 'INTEGER',
        str: 'TEXT',
        float: 'REAL',
        bool: 'BOOLEAN'
    }

    def __init__(self):
        if not Database.DATABASE:
            LOGGER.info('class Table: __init__(): No database, returning')
            return
        if self.__class__.TABLENAME not in Database.TABLES:
            self.parse_object_to_table()
        
    def __str__(self):
        return f'{self.__class__.__name__}({self.__dict__})'

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def insert_instance_in_database(self):
        columns = ', '.join(field for field in self.__dict__.keys() )
        values = tuple(self.__dict__.values())
        create_insert_query = f'INSERT INTO {self.__class__.TABLENAME}({columns}) VALUES({", ".join("?" for _ in values)})'
        LOGGER.info(f'class Table: insert_instance_in_database(): create_insert_query: {create_insert_query}')
        if not Database.DATABASE:
            LOGGER.info('class Table: insert_instance_in_database(): No database, returning')
            return
        Database.DATABASE.open()
        try:
            Database.DATABASE.cursor.execute(create_insert_query, values)
            Database.DATABASE.commit()
            self.id = Database.DATABASE.cursor.lastrowid
            LOGGER.info(f'class Table: insert_instance_in_database(): {self.__class__.__name__}: {self} inserted')
        except sqlite3.IntegrityError:
            Database.DATABASE.rollback()
            LOGGER.info(f'class Table: insert_instance_in_database(): {self.__class__.__name__}: {self} already exists (IntegrityError on some unique field), skipping')
        Database.DATABASE.close()

    def parse_object_to_table(self):
        fields = (field for field in self.__class__.__dict__.values() if isinstance(field, Field))
        create_table_query = f'CREATE TABLE IF NOT EXISTS {self.__class__.TABLENAME}('
        for field in fields:
            create_table_query += f'{field.name} {self.type_map[field.type]}'
            if field.primary_key:
                create_table_query += ' PRIMARY KEY'
            if field.autoincrement:
                create_table_query += ' AUTOINCREMENT'
            if field.unique:
                create_table_query += ' UNIQUE'
            if field.default is not None:
                create_table_query += f' DEFAULT {field.default}'
            if field.not_null:
                create_table_query += ' NOT NULL'
            if field.foreign_key_table is not None:
                create_table_query += f' REFERENCES {field.foreign_key_table}({field.foreign_key_column})'
            create_table_query += ', '
        create_table_query = create_table_query[:-2] + ')'
        LOGGER.info(f'class Table: parse_object_to_table(): create_table_query: {create_table_query}')
        if not Database.DATABASE:
            LOGGER.info('class Table: parse_object_to_table(): No database, returning')
            return
        Database.DATABASE.open()
        Database.DATABASE.cursor.execute(create_table_query)
        Database.DATABASE.commit()
        Database.DATABASE.close()
        Database.TABLES.append(self.__class__.TABLENAME)
        LOGGER.info(f'class Table: parse_object_to_table(): {self.__class__.__name__} table created')


class Field():
    def __init__(self, name, type, default=None, primary_key=False, autoincrement=False, unique=False, not_null=False, foreign_key_table=None, foreign_key_column=None):
        self.name = name
        self.type = type
        self.default = default
        self.primary_key = primary_key
        self.autoincrement = autoincrement
        self.unique = unique
        self.not_null = not_null
        self.foreign_key_table = foreign_key_table
        self.foreign_key_column = foreign_key_column
        LOGGER.info(f'class Field: __init__(): Field {self.name} created: {self.__dict__}')



class Person(Table):
    TABLENAME = 'persons'
    ID = Field('id', int, primary_key=True, autoincrement=True)
    NAME = Field('name', str)
    AGE = Field('age', int)
    PHONE = Field('phone', int, unique=True)
    DELETED = Field('deleted', bool, default=False)
    CARPLATE = Field('carplate', str, foreign_key_table='cars', foreign_key_column='plate')

    def __init__(self, id=None, name="", age=None, phone=None, deleted=False, carplate=None):
        self.name = name
        self.age = age
        self.phone = phone
        self.deleted = deleted
        self.carplate = carplate
        self.id = id
        super().__init__()
        LOGGER.info(f'class Person: __init__(): Person {self.name} created: {self.__dict__}')

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return f'Person(id={self.id}, name={self.name}, age={self.age}, phone={self.phone}, carplate={self.carplate})'
    
class Car(Table):
    TABLENAME = 'cars'
    ID = Field('id', int, primary_key=True, autoincrement=True)
    PLATE = Field('plate', str, unique=True)
    MODEL = Field('model', str)
    DELETED = Field('deleted', bool, default=False)

    def __init__(self, id=None, plate='', model="", deleted=False):
        self.plate = plate
        self.model = model
        self.deleted = deleted
        self.id = id
        super().__init__()
        LOGGER.info(f'class Car: __init__(): Car {self.plate} created: {self.__dict__}')

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return f'Car(id={self.id}, plate={self.plate}, model={self.model})'


class Country(Table):
    TABLENAME = 'countries'
    ID = Field('id', int, primary_key=True, autoincrement=True)
    NAME = Field('name', str, unique=True)
    SHORTNAME = Field('shortname', str, unique=True)
    DELETED = Field('deleted', bool, default=False)

    def __init__(self, id=None, name="", shortname="", deleted=False):
        self.name = name
        self.shortname = shortname
        self.deleted = deleted
        self.id = id
        super().__init__()
        LOGGER.info(f'class Country: __init__(): Country {self.name} created: {self.__dict__}')

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return f'Country(id={self.id}, name={self.name}, shortname={self.shortname}, deleted={self.deleted})'


def test():
    db = Database('test.db')
    db_table = db.execute('SELECT persons.name, persons.carplate, cars.model FROM persons INNER JOIN cars ON persons.carplate = cars.plate;')
    print(db_table)


if __name__ == '__main__':
    test()
