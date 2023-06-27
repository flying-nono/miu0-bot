from PIL import Image, ImageFilter, ImageDraw, ImageFont
from typing import Dict, List
from io import BytesIO
from nonebot import get_driver

import os
import random
import time

from .maimai_api import _get_b50_json
from .maimai_models import ChartInfo, BestList

from ..config import Config

plugin_config = Config.parse_obj(get_driver().config)


class DrawBest:
    def __init__(self, sdBest:BestList, dxBest:BestList, username:str):
        random.seed(time.time())
        self.sdBest = sdBest
        self.dxBest = dxBest
        self.username = username
        self.sdRating = 0
        self.dxRating = 0
        for sd in sdBest:
            self.sdRating += sd.ra
        for dx in dxBest:
            self.dxRating += dx.ra
        self.playerRating = self.sdRating + self.dxRating
        self.pic_dir = plugin_config.plugin_dir+'/static/mai/pic/'
        self.cover_dir = plugin_config.plugin_dir+'/static/mai/cover/'
        self.frame_dir = plugin_config.plugin_dir+'/static/mai/frame/'
        self.b50_img = Image.open(self.pic_dir+"b50_bg.png").convert("RGBA") # size=(2200, 2400)
        self.frameList = ["209507","306103","200501","309213","100501","105501","105601","159502","200101","250717","306104"]
        # self.frame_img = Image.open(self.frame_dir+"UI_Frame_209507.png").convert("RGBA") # size=(1080, 452)
        self.frame_img = Image.open(self.frame_dir+f"UI_Frame_{random.choice(self.frameList)}.png").convert("RGBA")
        self.img:Image.Image
        self.border = (110, 80)
        self.itemsize = (367, 202)
        self.itemgap = (30, 20)
        self.COLUMNS_IMG = []
        for i in range(5):
            self.COLUMNS_IMG.append(self.border[0] + (self.itemsize[0] + self.itemgap[0]) * i)
        self.ROWS_IMG = []
        for i in range(7):
            self.ROWS_IMG.append(self.border[1] + (self.itemsize[1] + self.itemgap[1]) * i)
        for i in range(3):
            self.ROWS_IMG.append(self.border[1]*2 + self.itemsize[1]*7 + self.itemgap[1]*6 + (self.itemsize[1] + self.itemgap[1]) * i)
        self.draw()
        

    def _resizePic(self, img:Image.Image, time:float):
        return img.resize((int(img.size[0] * time), int(img.size[1] * time)))


    def _drawtemp(self, chartInfo:ChartInfo):
        rankPic = 'D C B BB BBB A AA AAA S Sp SS SSp SSS SSSp'.split(' ')
        comboPic = ' FC FCp AP APp'.split(' ')
        syncPic = ' FS FSp FSD FSDp'.split(' ')
        titleFontName = plugin_config.plugin_dir+'/static/font/adobe_simhei.otf'
        Color = [(69, 193, 36), (255, 186, 1), (255, 90, 102), (134, 49, 200), (217, 197, 233)]
        levelTriagle = [(0, 0), (97, 0), (0, 60)]

        pngPath = self.cover_dir + f'{chartInfo.idNum}.png'
        if not os.path.exists(pngPath):
            pngPath = self.cover_dir + '11000.png'
        
        temp = Image.open(pngPath).convert("RGBA")
        temp = self._resizePic(temp, self.itemsize[0]/temp.size[0])
        temp = temp.crop((0, (temp.size[1] - self.itemsize[1]) / 2, self.itemsize[0], (temp.size[1] + self.itemsize[1]) / 2))
        temp = temp.filter(ImageFilter.GaussianBlur(5)) # 高斯模糊
        temp = temp.point(lambda p: int(p * 0.75)) # 减弱亮度

        tempDraw = ImageDraw.Draw(temp)
        tempDraw.polygon(levelTriagle, Color[chartInfo.diff])
        
        if chartInfo.tp == 'SD':
            tpPic = Image.open(self.pic_dir + "SD.png").convert("RGBA")
        elif chartInfo.tp == 'DX':
            tpPic =  Image.open(self.pic_dir + "DX.png").convert("RGBA")
        tpPic = self._resizePic(tpPic, 0.7)
        temp.paste(tpPic, (self.itemsize[0]-tpPic.size[0]-10, 15), tpPic.split()[3])

        tempDraw = ImageDraw.Draw(temp)

        font = ImageFont.truetype(titleFontName, 35, encoding='utf-8')
        title = chartInfo.title
        tempDraw.text((15, self.itemsize[1]//4 + 5 ),title,'white',font)

        font = ImageFont.truetype(titleFontName, 40, encoding='utf-8')
        tempDraw.text((15, self.itemsize[1]*2//4 + 5 ), f'{"%.4f" % chartInfo.achievement}%', 'white', font)

        rankImg = Image.open(self.pic_dir + f'UI_TTR_Rank_{rankPic[chartInfo.scoreId]}.png').convert('RGBA')
        rankImg = self._resizePic(rankImg, 0.4)
        temp.paste(rankImg, (self.itemsize[0]-rankImg.size[0]-20, self.itemsize[1]*2//4 ), rankImg.split()[3])

        if chartInfo.comboId != 0:
            comboImg = Image.open(self.pic_dir + f'UI_MSS_MBase_Icon_{comboPic[chartInfo.comboId]}.png').convert('RGBA')
            comboImg = self._resizePic(comboImg, 1)
            temp.paste(comboImg, (self.itemsize[0]-comboImg.size[0]*2-20, self.itemsize[1]*3//4 - 5 ), comboImg.split()[3])

        if chartInfo.syncId != 0:
            syncImg = Image.open(self.pic_dir + f'UI_MSS_MBase_Icon_{syncPic[chartInfo.syncId]}.png').convert('RGBA')
            syncImg = self._resizePic(syncImg, 1)
            temp.paste(syncImg, (self.itemsize[0]-syncImg.size[0]-20, self.itemsize[1]*3//4 - 5 ), syncImg.split()[3])
        
        font = ImageFont.truetype(titleFontName, 28, encoding='utf-8')
        tempDraw.text((15, self.itemsize[1]*3//4 + 5 ), f'Base: {chartInfo.ds} -> {chartInfo.ra}', 'white', font)

        return temp
    

    def _drawBestList(self, img:Image.Image, sdBest:BestList, dxBest:BestList):
        
        for num in range(len(sdBest)):
            i = num // 5
            j = num % 5
            chartInfo = sdBest[num]
            
            temp = self._drawtemp(chartInfo)

            recBase = Image.new('RGBA', self.itemsize, 'black')
            recBase = recBase.point(lambda p: int(p * 0.8))
            img.paste(recBase, (self.COLUMNS_IMG[j] + 8, self.ROWS_IMG[i] + 8))
            img.paste(temp, (self.COLUMNS_IMG[j] + 4, self.ROWS_IMG[i] + 4))
        
        for num in range(len(dxBest)):
            i = num // 5
            j = num % 5
            chartInfo = dxBest[num]
            
            temp = self._drawtemp(chartInfo)

            recBase = Image.new('RGBA', self.itemsize, 'black')
            recBase = recBase.point(lambda p: int(p * 0.8))
            img.paste(recBase, (self.COLUMNS_IMG[j] + 8, self.ROWS_IMG[i+7] + 8))
            img.paste(temp, (self.COLUMNS_IMG[j] + 4, self.ROWS_IMG[i+7] + 4))


    def _findRaPic(self) -> str:
        num = '11'
        if self.playerRating < 1000:
            num = '01'
        elif self.playerRating < 2000:
            num = '02'
        elif self.playerRating < 4000:
            num = '03'
        elif self.playerRating < 7000:
            num = '04'
        elif self.playerRating < 10000:
            num = '05'
        elif self.playerRating < 12000:
            num = '06'
        elif self.playerRating < 13000:
            num = '07'
        elif self.playerRating < 14000:
            num = '08'
        elif self.playerRating < 14500:
            num = '09'
        elif self.playerRating < 15000:
            num = '10'
        return f'UI_CMN_DXRating_{num}.png'
    
    def _drawRating(self, ratingBaseImg:Image.Image):
        COLOUMS_RATING = [325, 380, 430, 485, 535]
        theRa = self.playerRating
        i = 4
        while theRa:
            digit = theRa % 10
            theRa = theRa // 10
            digitImg = Image.open(self.pic_dir + f'UI_NUM_Drating_{digit}.png').convert('RGBA')
            digitImg = self._resizePic(digitImg, 2)
            ratingBaseImg.paste(digitImg, (COLOUMS_RATING[i] - 20, 34), mask=digitImg.split()[3])
            i = i - 1
        return ratingBaseImg

    def _drawFrame(self, img:Image.Image, playerRating:int, sdRating:int, dxRating:int):
        fesLogo = Image.open(self.pic_dir+"logo.png").convert('RGBA')
        fesLogo = self._resizePic(fesLogo, 0.3)
        img.paste(fesLogo, (35, 50), fesLogo.split()[3])

        ratingBaseImg = Image.open(self.pic_dir + self._findRaPic()).convert('RGBA')
        ratingBaseImg = self._drawRating(ratingBaseImg)
        ratingBaseImg = self._resizePic(ratingBaseImg, 0.3)
        img.paste(ratingBaseImg, (200, 8), ratingBaseImg.split()[3])

        namePlateImg = Image.open(self.pic_dir + 'Name.png').convert('RGBA')
        namePlateImg = namePlateImg.resize((285, 60))
        namePlateDraw = ImageDraw.Draw(namePlateImg)
        FontName = plugin_config.plugin_dir+'/static/font/msyh.ttc'
        font = ImageFont.truetype(FontName, 36, encoding='utf-8')
        # logger.debug(self.username)
        namePlateDraw.text((12, 5), self.username, 'black', font)
        img.paste(namePlateImg, (200, 50), namePlateImg.split()[3])

        shougouImg = Image.open(self.pic_dir + 'UI_CMN_Shougou_Rainbow.png').convert('RGBA')
        shougouDraw = ImageDraw.Draw(shougouImg)
        font2 = ImageFont.truetype(plugin_config.plugin_dir+'/static/font/adobe_simhei.otf', 14, encoding='utf-8')
        playCountInfo = f"SD:{sdRating} + DX:{dxRating} = {playerRating}"
        shougouImgW, shougouImgH = shougouImg.size
        playCountInfoW, playCountInfoH = shougouDraw.textsize(playCountInfo, font2)
        textPos = ((shougouImgW - playCountInfoW - font2.getoffset(playCountInfo)[0]) / 2, 5)
        shougouDraw.text((textPos[0] - 1, textPos[1]), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] + 1, textPos[1]), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0], textPos[1] - 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0], textPos[1] + 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] - 1, textPos[1] - 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] + 1, textPos[1] - 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] - 1, textPos[1] + 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] + 1, textPos[1] + 1), playCountInfo, 'black', font2)
        shougouDraw.text(textPos, playCountInfo, 'white', font2)
        shougouImg = self._resizePic(shougouImg, 1.05)
        img.paste(shougouImg, (200, 110), mask=shougouImg.split()[3])


    def draw(self):
        self._drawBestList(self.b50_img, self.sdBest, self.dxBest)
        self._drawFrame(self.frame_img, self.playerRating, self.sdRating, self.dxRating)
        self.b50_img.thumbnail((1080, 2400))
        self.img = Image.new('RGBA',(1080,self.b50_img.size[1]+self.frame_img.size[1]),'white')

        self.img.paste(self.frame_img, (0,0))
        self.img.paste(self.b50_img, (0,self.frame_img.size[1]))


    def getDir(self):
        return self.img.convert('RGB')


async def generate50(payload:Dict, name:str):
    obj, status = await _get_b50_json(payload)

    if status == 400:
        return None, 400
    if status == 403:
        return None, 403

    sd_best = BestList(35)
    dx_best = BestList(15)
        
    dx: List[Dict] = obj["charts"]["dx"]
    sd: List[Dict] = obj["charts"]["sd"]
    for c in sd:
        sd_best.push_ra(ChartInfo.from_b50json(c))
    for c in dx:
        dx_best.push_ra(ChartInfo.from_b50json(c))
    
    pic = DrawBest(sd_best, dx_best, name).getDir()

    output = BytesIO()
    pic.save(output, format='PNG')

    return output, status

