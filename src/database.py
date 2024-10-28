import logging
import sqlite3
from typing import Union

from utils import singleton


@singleton
class Connection:
    """Класс для управления подключением к базе данных SQLite и выполнения запросов.

    Инициализирует подключение к базе данных, создает необходимые таблицы (если их нет),
    а также предоставляет методы для выполнения запросов с возможностью возврата одного или
    множества результатов, а также коммитов изменений.
    """

    def __init__(self, db_name: str):
        """Инициализация соединения с базой данных и создание курсора.

        :param db_name: Название файла базы данных SQLite.
        """
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self._init_database()

    def _init_database(self):
        """Инициализация таблиц базы данных.

        Создает таблицы `users` и `tasks`, если они еще не существуют, а также
        индексы для оптимизации запросов к базе данных.
        """
        query_for_init_users_table = (
            "CREATE TABLE IF NOT EXISTS users("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name VARCHAR(35),"
            "login VARCHAR(60),"
            "telegram_id INTEGER UNIQUE"
            ");"
        )
        query_for_add_creating_index = (
            "CREATE INDEX IF NOT EXISTS idx_telegram_id ON users(telegram_id);"
        )
        self.cursor.execute(query_for_init_users_table)
        self.cursor.execute(query_for_add_creating_index)

        query_for_init_task_table = (
            "CREATE TABLE IF NOT EXISTS tasks("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "title VARCHAR(80) NOT NULL,"
            "description TEXT,"
            "status BOOLEAN,"  # False, если задача не выполнена
            "is_deleted BOOLEAN DEFAULT FALSE,"
            "telegram_user_id INTEGER,"
            "FOREIGN KEY (telegram_user_id) REFERENCES users(telegram_id)"
            ");"
        )
        self.cursor.execute(query_for_init_task_table)
        self.connection.commit()

    def execute_query(
        self, query: str, many: bool = False, commit: bool = False, args: tuple = None
    ) -> Union[tuple, list, None]:
        """Выполняет запрос к базе данных с возможностью возврата одного или нескольких результатов.

        :param query: SQL-запрос для выполнения;
        :param many: Если True, возвращает множество результатов (список), иначе — один результат (кортеж);
        :param commit: Если True, выполняется коммит для сохранения изменений в базе данных;
        :param args: Параметры для подстановки в SQL-запрос.
        :return: Возвращает результат запроса (один кортеж или список кортежей) либо None, если выполняется коммит.
        """
        try:
            result = self.cursor.execute(query, args)
            if commit:
                self.connection.commit()
                return None

            if many:
                return result.fetchall()
            return result.fetchone()

        except sqlite3.DatabaseError as e:
            logging.debug(f"Ошибка выполнения запроса: {e}")
            return None

    def __del__(self):
        """Закрывает соединение и курсор при удалении экземпляра класса или завершении программы."""
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()


# Создание экземпляра соединения с базой данных
connection = Connection(db_name="/src/todo_db.db")
