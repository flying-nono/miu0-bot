from nonebot import get_driver
from pydantic import BaseModel
import os


class Config(BaseModel):
    plugin_dir:str = os.path.dirname(__file__)
    
plugin_config = Config.parse_obj(get_driver().config)

# print(os.path.dirname(__file__))
# /root/bot/miu0-bot/src/plugins/maimai_web