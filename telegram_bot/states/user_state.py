from aiogram.fsm.state import StatesGroup, State


class UserRegistration(StatesGroup):
    waiting_name = State()