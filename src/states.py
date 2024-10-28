from utils import singleton


@singleton
class BaseStates:
    """Базовы состояния."""
    DEFAULT = "DEFAULT"
    IN_MENU = "IN_MENU"


@singleton
class RegistrationStates:
    """Состояния для регистрации пользователя."""
    WAIT_FOR_NAME = "WAIT_FOR_NAME"
    WAIT_FOR_LOGIN = "WAIT_FOR_LOGIN"

    SUBMIT_NAME = "SUBMIT_NAME"
    SUBMIT_LOGIN = "SUBMIT_LOGIN"


@singleton
class TaskStates:
    """Состояния для управления задачами."""
    WAIT_FOR_TASK_TITLE = "WAIT_FOR_TASK_TITLE"
    WAIT_FOR_TASK_DESCRIPTION = "WAIT_FOR_TASK_DESCRIPTION"

    SUBMIT_TITLE = "SUBMIT_TITLE"
    SUBMIT_DESCRIPTION = "SUBMIT_DESCRIPTION"
    SUBMIT_DELETE_TASK = "SUBMIT_DELETE_TASK"

    LOOK_AT_TASKS = "LOOK_AT_TASKS"


base_states = BaseStates()
reg_states = RegistrationStates()
task_states = TaskStates()
