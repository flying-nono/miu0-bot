import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
# from nonebot.adapters.onebot.v12 import Adapter as ONEBOT_V12Adapter

nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)
# driver.register_adapter(ONEBOT_V12Adapter)

nonebot.load_from_toml("pyproject.toml")

if __name__ == "__main__":
    nonebot.run(app="__mp_main__:app")
