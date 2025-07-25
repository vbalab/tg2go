from aiogram import types
from aiogram.filters import Filter

from tg2go.core.configs.constants import ADMIN_CHAT_IDS, STAFF_CHAT_IDS
from tg2go.db.models.user import User
from tg2go.services.user import UserService


class AdminFilter(Filter):
    async def __call__(self, message: types.Message) -> bool:
        return message.chat.id in ADMIN_CHAT_IDS


class StaffFilter(Filter):
    async def __call__(self, message: types.Message) -> bool:
        return message.chat.id in STAFF_CHAT_IDS


class VerifiedFilter(Filter):
    async def __call__(self, message: types.Message) -> bool:
        srv = UserService.Create()

        verified = await srv.GetUser(
            chat_id=message.chat.id,
            column=User.verified,
        )

        return verified if verified else False


class HasOrderFilter(Filter):
    async def __call__(self, message: types.Message) -> bool:
        srv = UserService.Create()

        current_order_id = await srv.GetUser(
            chat_id=message.chat.id,
            column=User.current_order_id,
        )

        return current_order_id is not None
