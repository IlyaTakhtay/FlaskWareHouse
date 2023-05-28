from typing import List

from database.DBcm import DBContextManager

def select(db_config: dict, _sql: str):
    with DBContextManager(db_config) as cursor:

        if cursor is None:
            raise ValueError('Курсор не создан')

        cursor.execute(_sql)
        schema = [column[0] for column in cursor.description]
        result = cursor.fetchall()
    return result,schema
    
def select_dict(dbconfig: dict, _sql:str):
    with DBContextManager(dbconfig) as cursor:

        if cursor is None:
            raise ValueError('Курсор не создан')

        cursor.execute(_sql)
        result = []
        schema = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            result.append(dict(zip(schema, row)))
    return result

def insert(db_config: dict, sql: str):
    with DBContextManager(db_config) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')
        cursor.execute(sql)

def call_proc(dbconfig: dict, proc_name: str, *args):
    with DBContextManager(dbconfig) as cursor:
        if cursor is None:
            raise ValueError('Курсор не курсор')
        param_list = []
        for arg in args:
            print('args=', arg)
            param_list.append(arg)
        res = cursor.callproc(proc_name, param_list)
    return res