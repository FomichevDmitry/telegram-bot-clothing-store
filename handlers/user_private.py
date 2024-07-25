import asyncio

from aiogram import F, types, Router, Bot
from aiogram.filters import CommandStart

from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import (
    orm_add_to_cart,
    orm_add_user,
)

from filters.chat_types import ChatTypeFilter
from handlers.menu_processing import get_menu_content
from kbds.inline import MenuCallBack, get_callback_btns


YOOKASSA_TEST_TOKEN = '381764678:TEST:87977'

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name="main")

    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)


async def add_to_cart(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    user = callback.from_user
    await orm_add_user(
        session,
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=None,
    )
    await orm_add_to_cart(session, user_id=user.id, product_id=callback_data.product_id)
    await callback.answer("Товар добавлен в корзину.")


@user_private_router.callback_query(MenuCallBack.filter())
async def user_menu(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):

    if callback_data.menu_name != 'order':
        if callback_data.menu_name == "add_to_cart":
            await add_to_cart(callback, callback_data, session)
            return

        media, reply_markup = await get_menu_content(
            session,
            level=callback_data.level,
            menu_name=callback_data.menu_name,
            category=callback_data.category,
            page=callback_data.page,
            product_id=callback_data.product_id,
            user_id=callback.from_user.id,
        )

        await callback.message.edit_media(media=media, reply_markup=reply_markup)
        await callback.answer()
    else:
        await callback.message.delete()

        # price = await get_menu_content(
        #     session,
        #     level=callback_data.level,
        #     menu_name=callback_data.menu_name,
        #     category=callback_data.category,
        #     page=callback_data.page,
        #     product_id=callback_data.product_id,
        #     user_id=callback.from_user.id,
        # )

        price = 900 * 100

        prices = [types.LabeledPrice(label="RUB", amount=price)]
        await callback.message.answer_invoice(
            title=f"Заказ на {price}₽",
            description=f"Оплата заказа на сумму {price}₽ в боте Магазин Джинса",
            prices=prices,
            provider_token=YOOKASSA_TEST_TOKEN,
            payload=f'oplata_{price}',
            currency="rub"
        )


@user_private_router.pre_checkout_query()
async def check_payload(precheck: types.PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(precheck.id, ok=True)


@user_private_router.message(F.content_type.in_({'successful_payment'}))
async def successful_pay(message: types.Message):
    if message.successful_payment.invoice_payload.startswith('oplata_'):
        text = '💵 Ваш платеж успешно зачислен!\n\n⌛️ *Подождите, оформляем заказ...*'

        msg = await message.answer(text)

        await asyncio.sleep(1.5)

        text = f'''
🚀 *Ваш заказ успешно оформлен! Можете отследить статус заказа в профиле!*
                '''

        await msg.edit_text(text)
