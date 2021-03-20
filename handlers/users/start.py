from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher import FSMContext

from filters.is_private import IsPrivate
from loader import dp
from middlewares import _
from models import User
from utils.misc import rate_limit, get_current_user
from states.auth import AuthStates
from states.menu import MenuStates
from keyboards.inline import languages, back_callback
from keyboards.default import menu


@dp.message_handler(IsPrivate(), CommandStart(), state='*')
async def start(msg: types.Message, state: FSMContext):
    welcome_message = await msg.answer(_("Привет!"))
    is_created = await User().create_user(tele_id=msg.from_user.id, firstname=msg.from_user.first_name,
                                          lastname=msg.from_user.last_name, username=msg.from_user.username,
                                          welcome_message_id=welcome_message.message_id)
    if is_created:
        await msg.answer(_("Выбери язык: "), reply_markup=languages.keyboard)
        await AuthStates.choose_lang.set()
        await msg.delete()
    else:
        await msg.delete()
        user = await User().select_user_by_tele_id(msg.from_user.id)
        keyboard = await menu.get_keyboard(user)
        msg = await msg.answer(_("Я тебя знаю!"), reply_markup=keyboard)
        await MenuStates.mediate.set()
        await state.update_data(current_msg_text=msg.text, current_msg=msg.message_id)


@rate_limit(10, 'blank')
@dp.callback_query_handler(text_contains='blank', state="*")
async def blank_calls(call: types.CallbackQuery):
    await call.answer(cache_time=60, text=_('Хватит жать - остановись'))
