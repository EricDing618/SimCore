from __future__ import annotations
import time

from src.myutils import add_seconds_to_datetime

class Tool:
    '''工具类，包含一些通用方法'''
    @staticmethod
    def myrange(a: int, b: int):
        '''返回一个整数范围的列表'''
        if a > b:
            return range(b, a + 1)
        return range(a, b + 1)
class Event:
    '''事件基类'''
    def __init__(self, 
                 start_time: str='1970/01/01 00:00:00',
                 building: Building=None
                 ):
        self.start = start_time
        self.building = building

    def event(self, 
                 event_type: str,
                 addsec: int=0,
                 elevator: Elevator=None,
                 passenger: Passenger=None,
                 floor: Floor=None
                 ):
        '''
        event_type类型：
        - 'start': 开始模拟
        - 'call_elevator': 乘客呼叫电梯
        - 'elevator_arrive': 电梯到达楼层
        - 'passenger_board': 乘客上电梯
        - 'passenger_alight': 乘客下电梯
        - 'elevator_idle': 电梯空闲
        '''
        self.event_type = event_type
        self.time = add_seconds_to_datetime(self.start, addsec)
        self.elevator = elevator
        self.passenger = passenger
        self.floor = floor

        return {
            'event_type': self.event_type,
            'time': self.time,
            'building': self.building,
            'elevator': self.elevator,
            'passenger': self.passenger,
            'floor': self.floor
        }

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
    def __init__(self, fid: int, 
                 height: float=3.0,  # 楼层高度，单位米
                 ):
        self.fid = fid
        self.height = height
    
class Elevator:
    '''电梯'''
    def __init__(self, 
                 eid: int=0,
                 max_weight: int=1000,
                 building: Building=None,
                 speed:float = 1.0
                 ):
        self.eid = eid
        self.max_weight = max_weight
        self.current_weight = 0
        self.passengers: list[Passenger] = []
        self.building = building
        self.speed = speed #(m/s)
        self.current_floor = None

class Building:
    '''大楼，也是控制中心，调度其他类型'''
    def __init__(self, 
             floor_range: tuple[Floor, Floor]=None,
             elevators: tuple[Elevator]=None,
             passengers: list[Passenger]=None,
             start_time: str='1970/01/01 00:00:00'
             ):
        self.t = Tool()
        self.floor_range = [Floor(f) for f in self.t.myrange(floor_range[0].fid,floor_range[1].fid+1) if f != 0]
        self.elevators = elevators
        self.passengers = passengers
        self.start_time = start_time
        self.eventman = Event(self.start_time, self)
    
    def __repr__(self):
        return f'Building(floor_range={self.floor_range}, elevators={self.elevators}, passengers={self.passengers})'
    
    def execute(self):
        '''执行调度'''
        yield self.eventman.event('start')
        for elevator in self.elevators:
            elevator.current_floor = self.floor_range[0].fid + round((elevator.eid / (len(self.elevators) - 1))*(self.floor_range[-1].fid - self.floor_range[0].fid))
            yield self.eventman.event('elevator_arrive',addsec=elevator.speed)