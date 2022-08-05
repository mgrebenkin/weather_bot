from loguru import logger
import sqlite3
from aiogram.dispatcher.storage import BaseStorage
import typing

from user_types import UserType


class FSMStorage(BaseStorage):

    def __init__(self, db_path: str) -> None:
        super().__init__()
        self.__db_connection: sqlite3.Connection = None
        self.connect_to_db(db_path)


    def connect_to_db(self, db_path: str) -> None:
        try:
            self.__db_connection = sqlite3.connect(db_path)
        except sqlite3.Error as e:
            logger.exception("Ошибка соединения с базой данных пользователей:\n")


    def __dict_factory(self, cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict:
        row_dict = dict()
        for idx, col in enumerate(cursor.description):
            row_dict[col[0]] = row[idx]
        return row_dict


    def __user_factory(self, cursor: sqlite3.Cursor, row: sqlite3.Row) -> UserType:
        row_dict = dict()
        for idx, col in enumerate(cursor.description):
            row_dict[col[0]] = row[idx]

        return UserType(id=row_dict['user'],
            lat=row_dict['lat'],
            lon=row_dict['lon'],
            sending_time=row_dict['sending_time'])


    def resolve_key(self, 
        chat: typing.Union[str, int, None]=None,
        user: typing.Union[str, int, None]=None) -> typing.Tuple:

        chat, user = map(str, self.check_address(chat=chat, user=user))
        try:
            cursor = self.__db_connection.cursor()
            cursor.execute(
                """SELECT * FROM FSMData
                WHERE (chat = :chat) OR (user = :user)""",
                {'chat': chat, 'user': user}
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    """INSERT INTO FSMData(chat, user)
                    VALUES (:chat, :user)""",
                    {'chat': chat, 'user': user}
                )
            self.__db_connection.commit()
            cursor.close()
        except Exception:
            logger.exception("""Ошибка базы данных:\n""")
        return chat, user


    async def set_state(self, *,
        chat: typing.Union[str, int, None]=None, 
        user: typing.Union[str, int, None]=None, 
        state: typing.Optional[typing.AnyStr]=None) -> None:

        try:
            chat, user = self.resolve_key(chat, user)
            cursor = self.__db_connection.cursor()
            cursor.execute(
                """UPDATE FSMData
                SET state = :state
                WHERE (chat = :chat) OR (user = :user)""",
                {'chat': chat, 'user': user, 'state': state})
            self.__db_connection.commit()
            cursor.close()
        except Exception:
            logger.exception("""Ошибка базы данных:\n""")


    async def get_state(self, *, 
        chat: typing.Union[str, int, None]=None, 
        user: typing.Union[str, int, None]=None, 
        default: typing.Optional[str]=None) -> typing.Optional[str]:

        try:   
            chat, user = self.resolve_key(chat, user)
            cursor = self.__db_connection.cursor()
            cursor.execute(
                """SELECT state
                FROM FSMData
                WHERE (user = :user) OR (chat = :chat)""",
                {'chat': chat, 'user': user})
            fetched_state = cursor.fetchone()
            cursor.close()
        except Exception:
            logger.exception("""Ошибка базы данных:\n""")
    
        if (fetched_state is None):
            return default

        return fetched_state[0]


    async def set_data(self, *, 
        chat: typing.Union[str, int, None]=None, 
        user: typing.Union[str, int, None]=None, 
        data: typing.Dict=None) -> None:

        try:    
            chat, user = self.resolve_key(chat, user)
            cursor = self.__db_connection.cursor()
            data.update({'chat': chat, 'user': user})
            cursor.execute(
                f"""UPDATE FSMData
                SET lat = :lat, lon = :lon, sending_time = :sending_time
                WHERE (chat = :chat) OR (user = :user)""",
                data
            )
            self.__db_connection.commit()
            cursor.close()
        except Exception:
            logger.exception("""Ошибка базы данных:\n""")


    async def get_data(self, *, 
        chat: typing.Union[str, int, None]=None, 
        user: typing.Union[str, int, None]=None, 
        default: typing.Optional[typing.Dict]=None) -> typing.Dict:

        try:    
            chat, user = self.resolve_key(chat, user)
            cursor = self.__db_connection.cursor()
            cursor.row_factory = self.__dict_factory
            cursor.execute(
                f"""SELECT lat, lon, sending_time
                FROM FSMData
                WHERE (chat = :chat) OR (user = :user)""",
                {'chat': chat, 'user': user}
            )
            data = cursor.fetchone()  # возвращает словарь
        except Exception:
            logger.exception("""Ошибка базы данных:\n""")
        if data:
            return data
        else:
            return default

    async def update_data(self, *, 
        chat: typing.Union[str, int, None]=None, 
        user: typing.Union[str, int, None]=None, 
        data: typing.Dict=None, **kwargs) -> None:

        try:    
            chat, user = self.resolve_key(chat, user)
            cursor = self.__db_connection.cursor()
            data.update({'chat': chat, 'user': user})
            cursor.execute(
                f"""UPDATE FSMData
                SET lat = :lat, lon = :lon, sending_time = :sending_time
                WHERE (chat = :chat) OR (user = :user)""",
                data)
            self.__db_connection.commit()
            cursor.close()
        except Exception:
            logger.exception("""Ошибка базы данных:\n""")


    async def finish(self, *, 
        chat: typing.Union[str, int, None]=None, 
        user: typing.Union[str, int, None]=None) -> None:

        try:    
            chat, user = self.resolve_key(chat, user)
            cursor = self.__db_connection.cursor()
            cursor.execute(
                """DELETE FROM FSMData
                WHERE (chat = :chat) OR (user = :user)""",
                {'chat': chat, 'user': user}
            )
            self.__db_connection.commit()
            cursor.close()
        except Exception:
            logger.exception("""Ошибка базы данных:\n""")


    async def close(self):
        self.__db_connection.close()

    
    async def has_bucket(self):
        return False


    async def wait_closed(self):
        pass


    async def set_location(self, 
        chat: typing.Union[str, int, None]=None,
        user: typing.Union[str, int, None]=None,
        location: typing.Tuple[float, float]=None) -> None:

        if location:
            loc_data = {'lat': location[0], 'lon': location[1]}
        else:
            loc_data = {'lat': None, 'lon': None}
        self.set_data(user=user, chat=chat, data=loc_data)
            

    async def set_sending_time(self, 
        chat: typing.Union[str, int, None]=None,
        user: typing.Union[str, int, None]=None,
        sending_time: str=None) -> None:
        self.set_data(user=user, 
            chat=chat, 
            data={'sending_time': sending_time})


    async def get_subscribers_set(self) -> set:
        subscribers_set = set()
        try:
            cursor = self.__db_connection.cursor()
            cursor.row_factory = self.__user_factory
            cursor.execute(
                """SELECT user, lat, lon, sending_time
                FROM FSMData
                WHERE state = 'FSMMain:user_subscribed' """
            )
            for item in cursor.fetchall():
                subscribers_set.add(item)
        except Exception:
            logger.exception("""Ошибка базы данных:\n""")

        return subscribers_set



'''Потом пригодится'''
"""IF EXISTS 
            (SELECT * FROM FSMData WHERE (chat = chat) OR (user = user))
            BEGIN
                UPDATE FSMData
                SET state = state
                WHERE (chat = chat) OR (user = user)
            END
            ELSE
            BEGIN
                INSERT INTO FSMData
                VALUES (chat = chat, user = user, state = state)
            END"""
