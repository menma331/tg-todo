from typing import Optional

from database import connection


class UsersDAO:
    """Класс управления данными пользователя в базе данных.

    Данный класс предоставляет методы для добавления новых пользователей,
    получения данных о пользователях по различным критериям.
    """

    @classmethod
    def convert_user_result_to_dict(cls, data: tuple) -> dict:
        """Конвертирует данные о пользователе из кортежа в словарь.

        :param data: Кортеж с данными пользователя из базы данных.
        :return: Словарь с ключами 'id', 'name', 'login', 'telegram_id'.
        """
        result = {
            "id": data[0],
            "name": data[1],
            "login": data[2],
            "telegram_id": data[3],
        }
        return result

    @classmethod
    def get_one_or_none(
        cls, pk: int = None, telegram_id: int = None, login: str = None
    ) -> Optional[dict]:
        """Получает пользователя по идентификатору или возвращает None.

        :param pk: ID пользователя.
        :param telegram_id: Telegram ID пользователя.
        :param login: Логин пользователя.
        :return: Словарь с данными пользователя или None, если пользователь не найден.
        """
        filters = {"id": pk, "telegram_id": telegram_id, "login": login}
        column, value = next(
            ((col, val) for col, val in filters.items() if val is not None),
            (None, None),
        )

        if not column:
            return None

        query = f"SELECT * FROM users WHERE {column} = ?"
        user_data = connection.execute_query(query=query, args=(value,))

        if user_data:
            return cls.convert_user_result_to_dict(data=user_data)

        return None

    @classmethod
    def add_new_user(cls, data: dict) -> Optional[dict]:
        """Добавляет нового пользователя в базу данных.

        :param data: Словарь с данными нового пользователя, должен содержать 'user_name',
                     'login' и 'telegram_id'.
        :return: Словарь с данными добавленного пользователя или None в случае ошибки.
        """
        name = data.get("user_name")
        login = data.get("login")
        telegram_id = data.get("telegram_id")
        query = f"INSERT INTO users (name, login, telegram_id) VALUES (?, ?, ?);"
        connection.execute_query(
            query=query, commit=True, args=(name, login, telegram_id)
        )

        user_id = connection.cursor.lastrowid
        return cls.get_one_or_none(pk=user_id)


class TaskDAO:
    """Класс управления задачами в базе данных.

    Данный класс предоставляет методы для добавления новых задач,
    получения всех задач для пользователя, а также изменения их статуса.
    """

    @classmethod
    def convert_task_result_to_dict(cls, data: tuple) -> dict:
        """Конвертирует данные о задаче из кортежа в словарь.

        :param data: Кортеж с данными задачи из базы данных.
        :return: Словарь с ключами 'id', 'title', 'description', 'telegram_id'.
        """
        result = {
            "id": data[0],
            "title": data[1],
            "description": data[2],
            "telegram_id": data[3],
        }
        return result

    @classmethod
    def add_new_task(cls, data: dict, telegram_id) -> None:
        """Добавляет новую задачу в базу данных.

        :param data: Словарь с данными новой задачи, должен содержать 'task_title'
                     и 'task_description'.
        :param telegram_id: Telegram ID пользователя, которому принадлежит задача.
        """
        title = data.get("task_title")
        description = data.get("task_description")
        status = False

        query = "INSERT INTO tasks (title, description, status, telegram_user_id) VALUES (?, ?, ?, ?);"
        connection.execute_query(
            query=query, commit=True, args=(title, description, status, telegram_id)
        )

    @classmethod
    def get_all_tasks(cls, telegram_id) -> Optional[list]:
        """Получает все задачи пользователя.

        :param telegram_id: Telegram ID пользователя, для которого нужно получить задачи.
        :return: Список словарей с задачами или None, если задач нет.
        """
        query = (
            "SELECT id, title, description, telegram_user_id FROM tasks WHERE telegram_user_id=? "
            "AND status=0 "
            "AND is_deleted=0;"
        )
        tasks_data = connection.execute_query(
            query=query, many=True, args=(telegram_id,)
        )
        if tasks_data:
            return [
                cls.convert_task_result_to_dict(task_data) for task_data in tasks_data
            ]

        return None

    @classmethod
    def mark_task_as_completed(cls, task_id: int, telegram_id: int) -> None:
        """Отмечает задачу как выполненную.

        :param task_id: ID задачи, которую нужно отметить как выполненную.
        :param telegram_id: Telegram ID пользователя, которому принадлежит задача.
        """
        query = "UPDATE tasks SET status=1 WHERE id=? AND telegram_user_id=?;"
        connection.execute_query(query=query, commit=True, args=(task_id, telegram_id))

    @classmethod
    def delete_task(cls, task_id: int, telegram_id: int) -> None:
        """Удаляет задачу.

        :param task_id: ID задачи, которую нужно удалить.
        :param telegram_id: Telegram ID пользователя, которому принадлежит задача.
        """
        query = "UPDATE tasks SET is_deleted=1 WHERE id=? AND telegram_user_id=?;"
        connection.execute_query(query=query, commit=True, args=(task_id, telegram_id))
