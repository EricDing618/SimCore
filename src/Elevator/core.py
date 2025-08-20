from __future__ import annotations

class Passenger:
    '''乘客'''
    def __init__(self,
                 pid: int,
                 weight: int=70,
                 building: Building=None,
                 # 乘客所在楼层和目的楼层，注意忽略0层
                 from_floor: int=1,
                 to_floor: int=10
                 ):
        self.pid = pid
        self.weight = weight
        self.building = building
        self.from_floor = from_floor
        self.to_floor = to_floor

class Floor:
    '''楼层，负数表示地下，注意忽略0层'''
    def __init__(self, fid: int):
        self.fid = fid
    
class Elevator:
    '''电梯'''
    def __init__(self, 
                 eid: int=0,
                 max_weight: int=1000,
                 building: Building=None
                 ):
        self.eid = eid
        self.max_weight = max_weight
        self.current_weight = 0
        self.passengers: list[Passenger] = []
        self.building = building

class Building:
    '''大楼，也是控制中心，调度其他类型'''
    def __init__(self, 
             floor_range: tuple[Floor, Floor]=None,
             elevators: tuple[Elevator, Elevator]=None,
             passengers: list[Passenger]=None
             ):
        self.floor_range = floor_range
        self.elevators = elevators
        self.passengers = passengers