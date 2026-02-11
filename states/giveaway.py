from aiogram.fsm.state import State, StatesGroup

class GiveawayStates(StatesGroup):
    waiting_text = State()
    waiting_button_text = State()
    waiting_channels = State()
    waiting_winners_count = State()
    waiting_channel_selection = State()
    waiting_publish_time = State()
    waiting_end_condition = State()
    waiting_end_value = State()
