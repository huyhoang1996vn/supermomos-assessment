from fastapi import APIRouter
from .users import usersrouter
from .events import eventsrouter
from .email_status import email_status_router


api_router = APIRouter()
api_router.include_router(usersrouter)
api_router.include_router(eventsrouter)
api_router.include_router(email_status_router)
