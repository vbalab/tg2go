from aiogram import F, Router, types

from tg2go.bot.handlers.staff.menus.category.category import CategoryMenu
from tg2go.bot.handlers.staff.menus.common import staff_menu
from tg2go.bot.handlers.staff.menus.good.good import GoodMenu
from tg2go.bot.handlers.staff.menus.good.remove import (
    GoodRemoveAction,
    GoodRemoveCallbackData,
)
from tg2go.services.staff.good import StaffGoodService

router = Router()


@router.callback_query(
    GoodRemoveCallbackData.filter(F.action == GoodRemoveAction.Delete)
)
async def GoodRemoveDelete(
    callback_query: types.CallbackQuery,
    callback_data: GoodRemoveCallbackData,
) -> None:
    srv = StaffGoodService.Create()
    await srv.InvalidateGood(callback_data.good_id)

    good = await srv.GetGood(callback_data.good_id)

    await staff_menu.ChangeToNewMenu(
        callback_query=callback_query,
        new_menu=await CategoryMenu(good.category_id),
    )
    await callback_query.answer()


@router.callback_query(GoodRemoveCallbackData.filter(F.action == GoodRemoveAction.Back))
async def GoodRemoveBack(
    callback_query: types.CallbackQuery,
    callback_data: GoodRemoveCallbackData,
) -> None:
    await staff_menu.ChangeToNewMenu(
        callback_query=callback_query,
        new_menu=await GoodMenu(callback_data.good_id),
    )
    await callback_query.answer()
