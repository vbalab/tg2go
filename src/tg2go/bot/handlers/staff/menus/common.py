import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from aiogram import types
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError

from tg2go.bot.lib.chat.username import GetChatUserLoggingPart, GetTgUsername
from tg2go.bot.lib.message.image import Image
from tg2go.bot.lib.message.io import ContextIO, DeleteMessage, SendImage, SignIO
from tg2go.db.models.category import Category
from tg2go.db.models.good import Good


class StaffAction(str, Enum):
    pass


@dataclass
class StaffMenu:
    image_dir: Path
    caption: str
    reply_markup: types.InlineKeyboardMarkup | None


class StaffPosition:
    start = "\n\n\n➤ "

    class Label(str, Enum):
        Settings = "Настройки"

    @classmethod
    def _Path(cls, *args: str) -> str:
        parts = [f"[{i}]" for i in args]

        return cls.start + " > ".join(parts)

    @classmethod
    def Settings(cls) -> str:
        return cls._Path(cls.Label.Settings.value)

    @classmethod
    def Category(cls, category: Category) -> str:
        return cls._Path(cls.Label.Settings.value, category.name)

    @classmethod
    def Good(cls, good: Good) -> str:
        return cls._Path(cls.Label.Settings.value, good.category.name, good.name)


def SplitButtonsInTwoColumns(
    plain_buttons: list[types.InlineKeyboardButton],
) -> list[list[types.InlineKeyboardButton]]:
    new_buttons = []

    group = []
    for i, button in enumerate(plain_buttons):
        group.append(button)

        if i % 2 == 1:
            new_buttons.append(group)
            group = []

    if group:
        new_buttons.append(group)

    return new_buttons


class StaffMenuSingleton:
    def __init__(self) -> None:
        self.message: types.Message | None = None

    async def _DeleteMenuMessage(self) -> None:
        if self.message is None:
            return

        await DeleteMessage(
            chat_id=self.message.chat.id,
            message_id=self.message.message_id,
        )

    async def InvalidateMenuMessage(self, new_chat_id: int) -> None:
        if self.message is None:
            return

        if new_chat_id == self.message.chat.id:
            await self._DeleteMenuMessage()
        else:
            username = await GetTgUsername(new_chat_id) or "-/-"
            await self.message.edit_caption(
                caption=f"➤ Управление меню было передано @{username}."
            )

        self.message = None

    async def StoreMenuMessage(self, message: types.Message) -> None:
        self.message = message

    async def SendMenu(self, chat_id: int, menu: StaffMenu) -> types.Message | None:
        await self.InvalidateMenuMessage(chat_id)

        message = await SendImage(
            chat_id=chat_id,
            image_dir=menu.image_dir,
            caption=menu.caption,
            reply_markup=menu.reply_markup,
        )

        if not message:
            logging.error(f"Can't send menu to chat_id={chat_id}")
            return None

        await self.StoreMenuMessage(message)

        return message

    async def ChangeToNewMenu(
        self,
        callback_query: types.CallbackQuery,
        new_menu: StaffMenu,
    ) -> None:
        msg = callback_query.message
        assert isinstance(msg, types.Message)

        if self.message and msg.message_id != self.message.message_id:
            await self.InvalidateMenuMessage(msg.chat.id)

        if self.message is None:
            await self.StoreMenuMessage(msg)

        image = Image(new_menu.image_dir)
        media = types.InputMediaPhoto(
            media=image.GetFileId(),
            caption=new_menu.caption,
            parse_mode="HTML",
        )

        try:
            await msg.edit_media(
                media=media,
                reply_markup=new_menu.reply_markup,
            )
        except (TelegramNetworkError, TelegramBadRequest) as e:
            logging.info(
                f"file_id={image.GetFileId()} is expired. Sending raw image. Error: {e}"
            )

            media.media = image.GetSource()

            updated = await msg.edit_media(
                media=media,
                reply_markup=new_menu.reply_markup,
            )

            if isinstance(updated, types.Message) and updated.photo:
                image.UpdateFileId(updated.photo[-1].file_id)

        part = await GetChatUserLoggingPart(msg.chat.id)
        logging.info(
            f"{part} {SignIO.Out.value}{ContextIO.Doc.value} {repr(media.caption)}"
        )

    async def Close(self) -> None:
        await self._DeleteMenuMessage()


staff_menu = StaffMenuSingleton()
