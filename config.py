import os
from dataclasses import dataclass

@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
    ADMIN_IDS: list = None
    TIMEZONE: str = "Europe/Amsterdam"
    GMT_OFFSET: str = "GMT+1"
    CARD_NUMBER: str = os.getenv("CARD_NUMBER", "5168742012345678")
    
    def __post_init__(self):
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        if admin_ids_str:
            self.ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]
        else:
            self.ADMIN_IDS = []
    
    def is_admin(self, user_id: int) -> bool:
        return user_id in self.ADMIN_IDS

config = Config()