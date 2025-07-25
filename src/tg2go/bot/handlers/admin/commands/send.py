from aiogram import F, Router, types
from aiogram.filters.command import Command, CommandObject
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from tg2go.bot.lib.message.filter import AdminFilter
from tg2go.bot.lib.message.io import ContextIO, SendMessage
from tg2go.services.user import UserService

router = Router()


class SendStates(StatesGroup):
    Message = State()


@router.message(Command("send"), StateFilter(None), AdminFilter())
async def CommandSend(
    message: types.Message,
    command: CommandObject,
    state: FSMContext,
) -> None:
    if not command.args or len(command.args.split()) != 1:
        await SendMessage(
            chat_id=message.chat.id,
            text="Укажите username в Telegram:\n/send @vbalab",
            context=ContextIO.UserFailed,
        )
        return

    ctx = UserService.Create()
    chat_id = await ctx.GetChatIdByUsername(command.args.replace("@", "").strip())

    if chat_id is None:
        await SendMessage(
            chat_id=message.chat.id,
            text="Пользователь с такими данными не существует.\nОтмена",
            context=ContextIO.UserFailed,
        )
        await state.clear()
        return

    await SendMessage(chat_id=message.chat.id, text="Введите текст сообщения")

    await state.set_state(SendStates.Message)
    await state.set_data({"chat_id": chat_id})


@router.message(StateFilter(SendStates.Message), F.content_type == "text")
async def CommandSendMessage(message: types.Message, state: FSMContext) -> None:
    assert message.text is not None

    data = await state.get_data()

    output = await SendMessage(chat_id=data["chat_id"], text=message.text)

    if output:
        await SendMessage(chat_id=message.chat.id, text="Успешно")
    else:
        await SendMessage(chat_id=message.chat.id, text="Неудачно")

    await state.clear()
