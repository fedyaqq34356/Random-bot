import os
from dataclasses import dataclass

@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
    ADMIN_IDS: list = None
    TIMEZONE: str = "Europe/Amsterdam"
    GMT_OFFSET: str = "GMT+1"
    
config = Config()
