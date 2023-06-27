from typing import List, Dict


class ChartFilter:
    def __init__(self, data, musicdata):
        self.musicdata:List[Dict] = musicdata
        self.data:Dict = self._chartfilter(data)

    def _computeRa(self, ds: float, achievement: float) -> int:
        baseRa = 22.4 
        if achievement < 50:
            baseRa = 7.0
        elif achievement < 60:
            baseRa = 8.0 
        elif achievement < 70:
            baseRa = 9.6 
        elif achievement < 75:
            baseRa = 11.2 
        elif achievement < 80:
            baseRa = 12.0 
        elif achievement < 90:
            baseRa = 13.6 
        elif achievement < 94:
            baseRa = 15.2 
        elif achievement < 97:
            baseRa = 16.8 
        elif achievement < 98:
            baseRa = 20.0 
        elif achievement < 99:
            baseRa = 20.3
        elif achievement < 99.5:
            baseRa = 20.8 
        elif achievement < 100:
            baseRa = 21.1 
        elif achievement < 100.5:
            baseRa = 21.6 

        return int(ds * (min(100.5, achievement) / 100) * baseRa)

    def _computeRate(self, achievement: float) -> str:
        rate = ['d', 'c', 'b', 'bb', 'bbb', 'a', 'aa', 'aaa', 's', 'sp', 'ss', 'ssp', 'sss', 'sssp']
        index = 13
        if achievement < 50:
            index = 0
        elif achievement < 60:
            index = 1
        elif achievement < 70:
            index = 2
        elif achievement < 75:
            index = 3
        elif achievement < 80:
            index = 4
        elif achievement < 90:
            index = 5
        elif achievement < 94:
            index = 6
        elif achievement < 97:
            index = 7
        elif achievement < 98:
            index = 8
        elif achievement < 99:
            index = 9
        elif achievement < 99.5:
            index = 10
        elif achievement < 100:
            index = 11
        elif achievement < 100.5:
            index = 12

        return rate[index]
    
    def _chartfilter(self, data:Dict) -> Dict:
        song_id = data["id"]
        level_index = data["level_index"]
        # song_id,ds,ra,rate
        data["song_id"] = str(song_id)
        for music in self.musicdata:
            if music["id"] == str(song_id):
                data["ds"] = music["ds"][level_index]
                break
        data["ra"] = self._computeRa(data["ds"],data["achievements"])
        data["rate"] = self._computeRate(data["achievements"]) 
        return data
    

class ChartInfo:
    def __init__(self, idNum:str, diff:int, tp:str, achievement:float, ra:int, comboId:int, syncId:int, scoreId:int,
                 title:str, ds:float, lv:str):
        self.idNum = idNum
        self.diff = diff
        self.tp = tp
        self.achievement = achievement
        self.ra = ra
        self.comboId = comboId
        self.syncId = syncId
        self.scoreId = scoreId
        self.title = title
        self.ds = ds
        self.lv = lv

    def __eq__(self, other):
        return self.ra == other.ra
    
    def __lt__(self, other):
        return self.ra < other.ra
    

    @classmethod
    def from_b50json(cls, data):
        rate = ['d', 'c', 'b', 'bb', 'bbb', 'a', 'aa', 'aaa', 's', 'sp', 'ss', 'ssp', 'sss', 'sssp']
        ri = rate.index(data["rate"])
        fc = ['', 'fc', 'fcp', 'ap', 'app']
        fi = fc.index(data["fc"])
        fs = ['', 'fs', 'fsp', 'fsd', 'fsdp']
        fsi = fs.index(data["fs"])
        return cls(
            idNum=str(data["song_id"]),
            title=data["title"],
            diff=data["level_index"],
            ra=data["ra"],
            ds=data["ds"],
            comboId=fi,
            syncId=fsi,
            scoreId=ri,
            lv=data["level"],
            achievement=data["achievements"],
            tp=data["type"]
        )
    
    @classmethod
    def from_totalScorejson(cls, data, musicdata):
        return cls.from_b50json(ChartFilter(data, musicdata).data)
    

class BestList:
    def __init__(self, size:int):
        self.data = []
        self.size = size
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, index):
        return self.data[index]
    
    def push_ra(self, elem:ChartInfo):
        if len(self.data) >= self.size and elem < self.data[-1]:
            return
        self.data.append(elem)
        self.data.sort()
        self.data.reverse()
        while(len(self.data) > self.size):
            del self.data[-1]

    def push_ach(self, elem:ChartInfo):
        if len(self.data) >= self.size and elem.achievement < self.data[-1].achievement:
            return
        self.data.append(elem)
        self.data.sort(key=lambda a:a.achievement)
        self.data.reverse()
        while(len(self.data) > self.size):
            del self.data[-1]

    def pop(self):
        del self.data[-1]

