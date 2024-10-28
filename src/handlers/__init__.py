from .base import base_router
from .registration import registration_router
from .task import task_router

routers = (base_router, registration_router, task_router)
