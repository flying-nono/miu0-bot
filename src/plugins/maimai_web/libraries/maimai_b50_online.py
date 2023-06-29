import nonebot

from PIL import Image
from typing import Union

from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from .maimai_b50 import generate50
from .maimai_api import _get_b50_json
from .maimai_models import UserInfo
from ..config import plugin_config


app: FastAPI = nonebot.get_app()

app.mount("/web", StaticFiles(directory=plugin_config.plugin_dir+"/web"))
'''设置获取静态资源文件的路由和文件目录'''

templates = Jinja2Templates(directory=plugin_config.plugin_dir+"/web")
    

@app.get("/")
async def index(request: Request):
    context = {"request":request}
    return templates.TemplateResponse("index.html",context=context)


@app.post("/b50/image")
async def get_b50(qq:str=Form(''),username:str=Form('')):
    if qq != '':
        payload = {"qq":qq,'b50':True}
        value = qq
    else:
        payload = {"username":username,'b50':True}
        value = username
    
    output, success = await generate50(payload,value)

    if success == 400:
        return "未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。"
    elif success == 403:
        return "该用户禁止了其他人获取数据。"

    b50_img = Image.open(output)

    b50_img_path = plugin_config.plugin_dir+f"/b50temp/{value}.png"

    b50_img.save(b50_img_path)

    return FileResponse(b50_img_path)

