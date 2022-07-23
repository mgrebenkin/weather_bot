from __future__ import annotations
from loguru import logger

import exceptions
from user_types import UserType, UserParametersType
import sqlite3

def user_type_factory(cursor: sqlite3.Cursor, row: sqlite3.Row) -> UserType:
    user_parameters = UserParametersType(*row[1:])
    user = UserType(row[0], 
        user_parameters)
    return user

    
class Subscribers:


    def __init__(self, db_path) -> None:
        self._subscribers_connection: sqlite3.Connection = None
        self._subscribers_cache: dict[int, UserParametersType] = dict()
        self.connect_to_db(db_path)
    

    def connect_to_db(self, db_path: str):
        '''Устанавливает соединение с базой данный и обновляет 
        кэш подписавшихся пользователей
        db_path - адрес файла БД'''

        try:
            self._subscribers_connection = sqlite3.connect(db_path)
            #self._subscribers_connection.row_factory = sqlite3.Row
            self.update_subscribers_cache()
        except sqlite3.Error as e:
            logger.exception("Ошибка соединения с базой данных пользователей:")
        
    
    
    def add_user(self, user: UserType):
        '''Добавляет пользователя в базу данных и кэш'''

        cursor = self._subscribers_connection.cursor()
        cursor.execute(
            '''INSERT INTO subscribers VALUES(?, ?, ?)''', (user.id, *user.parameters)
        )
        self._subscribers_connection.commit()
        self._subscribers_cache.update([user])
        cursor.close()
    
    
    def remove_user(self, user: UserType | int):
        'Убирает пользователя из базы данных и кэша, если он там есть'

        if type(user) == UserType:
            user_id = user.id
        elif type(user) ==  int:
            user_id = user
        else:
            raise exceptions.BadUserId("Неверный идентификатор пользователя")

        cursor = self._subscribers_connection.cursor()
        cursor.execute(
        '''DELETE FROM subscribers WHERE (user_id = ?)''', (user_id, )
        )
        self._subscribers_connection.commit()
        cursor.close()
        self._subscribers_cache.pop(user_id, 0)
        
    

    def update_subscribers_cache(self):
        '''Формирует заново кэш подписчиков по списку из базы данных.'''

        cursor = self._subscribers_connection.cursor()
        cursor.row_factory = user_type_factory
        cursor.execute('''SELECT * FROM subscribers''')
        self._subscribers_cache = dict(cursor.fetchall())
        cursor.close()


    def is_in_subscribers_cache(self, user: UserType | int) -> bool:
        '''Возвращает True, если id пользователя есть в кэше'''

        if type(user) == UserType:
            return user.id in self._subscribers_cache
        elif type(user) == int:
            return user in self._subscribers_cache
        else:
            raise exceptions.BadUserId("Неверный идентификатор пользователя")


    def is_in_subscribers_db(self, user: UserType | int) -> bool:
        '''Возвращает True, если пользователь есть в базе данных'''

        cursor = self._subscribers_connection.cursor()
        if type(user) == UserType:
            user_id = user.id
        elif type(user) == int:
            user_id = user
        else:
            raise exceptions.BadUserId("Неверный идентификатор пользователя")  

        cursor.execute('''SELECT * FROM subscribers WHERE (user_id = ?)''',
                (user_id, ))
        is_found = len(cursor.fetchall()) != 0
        cursor.close()
        return is_found


    def get_subscribers_cache(self) -> dict[int, UserParametersType]:
        '''Возвращает копию кэша подписчиковв'''
        return self._subscribers_cache.copy()

    '''def assign_job(self, user: UserType | int, job: Job):
        if type(user) == UserType:
            user_id = user.id
        elif type(user) == int:
            user_id == user
        else:
            raise exceptions.BadUserId("Неверный идентификатор пользователя")
        self._subscribers_cache[user_id].assigned_job = job'''
    


        
    
