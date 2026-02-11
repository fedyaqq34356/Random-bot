from aiogram.fsm.state import State, StatesGroup

class GiveawayStates(StatesGroup):
    waiting_text = State()
    waiting_button_text = State()
    waiting_participation_mode = State()
    waiting_main_channel = State()
    waiting_channel_selection = State()
    waiting_channels = State()
    waiting_winners_count = State()
    waiting_publish_time = State()
    waiting_end_condition = State()
    waiting_end_value = State()
    
    selecting_giveaway_to_manage = State()
    managing_participants = State()
    waiting_participant_to_add = State()
    removing_participant = State()
    viewing_participants = State()
    
    selecting_giveaway_to_edit = State()
    editing_giveaway = State()
    editing_text = State()
    editing_winners_count = State()
    editing_button_text = State()
    editing_end_time = State()