from pydantic import BaseModel
import os

class Config(BaseModel):
    plugin_dir:str = os.path.dirname(__file__)
    

# print(os.path.dirname(__file__))
# /root/bot/miu0-bot/src/plugins/test2