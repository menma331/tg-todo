from typing import Optional


def singleton(cls):
    """Реализуем декоратор синглтона, дабы предотвратить размножение одинаковых классов."""
    instances = {}

    def decorator(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return decorator


@singleton
class FiniteStateMachine:
    """Самописная машина состояний."""

    def __init__(self):
        self._states = (
            {}
        )  # Хранение текущих состояний пользователей(ключ - telegram id пользователя, значение - состояние)
        self._data = {}  # Хранение данных для каждого пользователя(ключ - telegram id)

    def set_state(self, telegram_id: int, state: str) -> None:
        """Устанавливает состояние для пользователя.

        :param telegram_id: Телеграм id пользователя;
        :param state: Состояние, на которое ставим пользователя."""
        self._states[telegram_id] = state
        if telegram_id not in self._data:
            self._data[telegram_id] = {}

    def get_state(self, telegram_id: int) -> Optional[str]:
        """Возвращает текущее состояние пользователя. Если состояния нет, возвращает None.

        :param telegram_id: Телеграм id пользователя;
        """
        return self._states.get(telegram_id)

    def reset_state(self, telegram_id: int) -> None:
        """Сбрасывает состояние пользователя.

        :param telegram_id: Телеграм id пользователя;
        """
        if telegram_id in self._states:
            del self._states[telegram_id]
        if telegram_id in self._data:
            del self._data[telegram_id]

    def set_data(self, telegram_id: int, key: str, value: any) -> None:
        """Устанавливает данные для текущего состояния пользователя.

        :param telegram_id: Телеграм id пользователя;
        :param key: Ключ для хранения данных;
        :param value: Значение для ключа;
        """
        if telegram_id not in self._data:
            self._data[telegram_id] = {}
        self._data[telegram_id][key] = value

    def get_data(self, telegram_id: int, key: str = None, default=None) -> any:
        """Получает данные пользователя по ключу, если они существуют.

        :param telegram_id: Телеграм id пользователя;
        :param key: ключ значения;
        :param default: Значение, которое возвращается, если данные отсутствуют;
        """
        if not key:
            return self._data.get(telegram_id, {})
        return self._data.get(telegram_id, {}).get(key, default)

    def reset_data(self, telegram_id: int) -> None:
        """Сбрасывает все данные для пользователя.

        :param telegram_id: Телеграм id пользователя;
        """
        if telegram_id in self._data:
            self._data[telegram_id] = {}


fsm = FiniteStateMachine()
