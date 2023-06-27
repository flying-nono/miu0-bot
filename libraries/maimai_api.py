import aiohttp
from typing import Dict, Tuple, Optional, List

async def _get_b50_json(payload: Dict) -> Tuple[Optional[Dict], int]:
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/player", json=payload) as resp:
        if resp.status == 400:
            return None, 400
        if resp.status == 403:
            return None, 403
        
        obj = await resp.json()
        return obj, 200
    

async def _get_totalscore(qq:str) -> Tuple[Optional[List[Dict]], int] :
    verlist = [
        "maimai",
        "maimai PLUS",
        "maimai GreeN",
        "maimai GreeN PLUS",
        "maimai ORANGE",
        "maimai MURASAKi PLUS",
        "maimai ORANGE PLUS",
        "maimai MURASAKi",
        "maimai PiNK",
        "maimai PiNK PLUS",
        "MiLK PLUS",
        "maimai MiLK",
        "maimai FiNALE",
        "maimai でらっくす",
        "maimai でらっくす PLUS",
        "maimai でらっくす Splash",
        "maimai でらっくす Splash PLUS",
        "maimai でらっくす UNiVERSE",
        "maimai でらっくす UNiVERSE PLUS",
        "maimai でらっくす FESTiVAL",
        "maimai でらっくす FESTiVAL PLUS"]
    payload = {'qq': qq, 'version': verlist}
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/plate", json=payload) as resp:
        if resp.status == 400:
            return None, 400
        if resp.status == 403:
            return None, 403

        obj = await resp.json()
        return obj["verlist"], 200
    

async def _get_musicdata() -> Tuple[Optional[List[Dict]], int]:
    async with aiohttp.request("GET", "https://www.diving-fish.com/api/maimaidxprober/music_data") as resp:
        if resp.status == 400:
            return None, 400
        if resp.status == 403:
            return None, 403

        obj = await resp.json()
        return obj, 200
