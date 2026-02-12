from .start import router as start_router
from .giveaway_create import router as create_router
from .giveaway_participate import router as participate_router
from .giveaway_manage import router as manage_router
from .giveaway_edit import router as edit_router
from .telethon_handler import router as telethon_router

routers = [start_router, create_router, participate_router, manage_router, edit_router, telethon_router]