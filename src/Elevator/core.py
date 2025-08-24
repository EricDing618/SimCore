from __future__ import annotations
from datetime import datetime, timedelta
from typing import Literal

import time
import heapq, itertools

class Tool:
    '''工具类，包含一些通用方法'''
    @staticmethod
    def myrange(a: int, b: int):
        '''返回一个整数范围的列表'''
        if a > b:
            return range(b, a + 1)
        return range(a, b + 1)
    @staticmethod
    def total_height(a: int, b: int, floor_range: dict[int, Floor], elevator: Elevator=None):
        '''计算电梯在两个楼层之间运行的总高度，忽略0层'''
        if a == b:
            return 0
        return sum(floor_range[f].height for f in Tool.myrange(a, b) if f != 0) - (elevator.height if elevator else 0)
    @staticmethod
    def time_difference_seconds(time_str1, time_str2):
        """
        计算两个时间字符串之间的秒数差（需自行外加绝对值abs()）
        
        参数:
        time_str1, time_str2: 格式为 "YYYY/MM/DD HH:MM:SS" 的时间字符串
        
        返回:
        两个时间之间的秒数差（绝对值）
        """
        # 定义时间格式
        time_format = "%Y/%m/%d %H:%M:%S"
        
        # 解析时间字符串为 datetime 对象
        dt1 = datetime.strptime(time_str1, time_format)
        dt2 = datetime.strptime(time_str2, time_format)
        
        # 计算时间差（秒数）
        return (dt2 - dt1).total_seconds()
    @staticmethod
    def add_seconds_to_datetime(datetime_str, addsec):
        # 示例使用
        #original_time = '1970/01/01 00:00:00'
        #addsec = 3600  # 增加1小时（3600秒）
        #result = add_seconds_to_datetime(original_time, addsec)
        #print(result)  # 输出: 1970/01/01 01:00:00
        # 将字符串转换为datetime对象
        dt = datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S')
        
        # 添加秒数
        new_dt = dt + timedelta(seconds=addsec)
        
        # 将结果转换回字符串格式
        return new_dt.strftime('%Y/%m/%d %H:%M:%S')
class Event:
    '''事件基类'''
    def __init__(self, 
                 start_time: str='1970/01/01 00:00:00',
                 building: Building=None
                 ):
        self.start_time = start_time
        self.relative_time = 0
        self.building = building

    def event(self, 
                 event_type: Literal['start',
                                     'call_elevator',
                                     'elevator_arrive',
                                     'passenger_board',
                                     'passenger_alight',
                                     'elevator_idle',
                                     'end']='elevator_idle',
                 addsec: int=0,
                 elevator: Elevator=None,
                 passenger: Passenger=None,
                 floor: Floor=None
                 ) -> dict[str, str|int|Building|Elevator|Passenger|Floor]:
        '''
        event_type类型：
        - 'start': 开始模拟
        - 'call_elevator': 乘客呼叫电梯
        - 'elevator_arrive': 电梯到达楼层
        - 'passenger_board': 乘客上电梯
        - 'passenger_alight': 乘客下电梯
        - 'elevator_idle': 电梯空闲
        - 'end': 结束模拟
        '''
        self.relative_time += addsec
        self.event_type = event_type
        self.time = Tool.add_seconds_to_datetime(self.start_time, self.relative_time)
        self.elevator = elevator
        self.passenger = passenger
        self.floor = floor
        #print(self.time)
        return {
            'event_type': self.event_type,
            'time': self.time,
            'building': self.building,
            'elevator': self.elevator,
            'passenger': self.passenger,
            'floor': self.floor,
            'relative_time': self.relative_time
        }

class Passenger:
    '''乘客'''
    def __init__(self,
                 pid: int,
                 weight: int=70,
                 name: str=None,
                 building: Building=None,
                 appear_time: str='1970/01/01 00:00:00',
                 # 乘客所在楼层和目的楼层，注意忽略0层
                 from_floor: int=1,
                 to_floor: int=10,
                 call_eid: int=0
                 ):
        self.pid = pid
        self.weight = weight
        self.building = building
        self.from_floor = from_floor
        self.to_floor = to_floor
        self.name = name if name else '无名氏'
        self.appear_time = appear_time
        self.call_eid = call_eid

        assert Tool.time_difference_seconds(self.building.start_time, self.appear_time) >= 0, "乘客出现时间必须在模拟开始时间之后"
        assert self.call_eid in [i.eid for i in self.building.elevators], f"eid {self.call_eid}不存在"
    def __repr__(self):
        return f'Passenger(pid={self.pid}, weight={self.weight}, name={self.name}, from_floor={self.from_floor}, to_floor={self.to_floor})'
    

class Floor:
    '''楼层，负数表示地下，注意忽略0层'''
    def __init__(self, fid: int, 
                 height: float=3.0,  # 楼层高度，单位米
                 ):
        self.fid = fid
        self.height = height
    
    def __repr__(self):
        return f'Floor(fid={self.fid}, height={self.height})'
    
class Elevator:
    '''电梯'''
    def __init__(self, 
                 eid: int=0,
                 name: str='',
                 max_weight: int=1000,
                 building: Building=None,
                 speed:int|float = 1.0,
                 height:int|float = 3,
                 init_floor: int=1
                 ):
        self.eid = eid
        self.name = name if name else eid
        self.max_weight = max_weight
        self.current_weight = 0
        self.passengers: list[Passenger] = []
        self.building = building
        self.speed = speed #(m/s)
        self.height = height
        self.current_floor = init_floor  # 初始楼层，默认为1楼
    
    def __repr__(self):
        return f'Elevator(eid={self.eid}, max_weight={self.max_weight}, current_weight={self.current_weight}, passengers={self.passengers}, current_floor={self.current_floor})'

class Building:
    '''大楼，也是控制中心，调度其他类型'''
    def __init__(self, 
             floor_range: tuple[Floor, Floor]=None,
             elevators: tuple[Elevator]=None,
             start_time: str='1970/01/01 00:00:00',
             bid: int=0,
             name: str=''
             ):
        self.t = Tool()
        self.floor_range = {f: Floor(f) for f in self.t.myrange(floor_range[0].fid,floor_range[1].fid) if f != 0}
        self.elevators = elevators
        self.passengers:list[Passenger] = []
        self.start_time = start_time
        self.bid = bid
        self.name = name
        self.eventman = Event(self.start_time, self)
        self.waiting_events:list[dict] = []

        assert 0 not in self.floor_range, "楼层范围不能包含0层"
    
    def __repr__(self):
        return f'Building(floor_range={self.floor_range}, elevators={self.elevators}, passengers={self.passengers})'
    
    def get_parking_floors_optimized(self, total_elevators, min_floor, max_floor):
        """
        优化版本：符合实际电梯系统的待命策略 by deepseek
        
        返回:
        待命楼层列表
        """
        if total_elevators == 1:
            # 单个电梯放在中间层
            return [(min_floor + max_floor) // 2]
        
        # 多个电梯的情况
        parking_floors = []
        
        # 第一部电梯总是在1楼（主要出入口）
        parking_floors.append(1)
        
        if total_elevators == 2:
            # 第二部电梯在中间层（您观察到的14楼）
            valid_floors = [f for f in range(min_floor, max_floor + 1) if f != 0]
            middle_index = len(valid_floors) // 2
            parking_floors.append(valid_floors[middle_index])
        
        elif total_elevators >= 3:
            # 最后一部电梯在最高层
            parking_floors.append(max_floor)
            
            # 中间电梯均匀分布
            valid_floors = [f for f in range(min_floor, max_floor + 1) if f != 0]
            for i in range(1, total_elevators - 1):
                position = i / (total_elevators - 1)
                index = round(position * (len(valid_floors) - 1))
                parking_floors.append(valid_floors[index])
        
        return sorted(parking_floors)  # 按楼层排序

    def elevator_initpark(self):
        floor_keys = list(self.floor_range.keys())
        for elevator,current_floor in zip(self.elevators,self.get_parking_floors_optimized(len(self.elevators),floor_keys[0],floor_keys[-1])):
            _eleelevator_current_floor = elevator.current_floor
            elevator.current_floor = current_floor
            total_height = self.t.total_height(_eleelevator_current_floor, elevator.current_floor, self.floor_range, elevator)
            #print(total_height)
            yield self.eventman.event('elevator_arrive',addsec=total_height//elevator.speed, elevator=elevator, floor=Floor(elevator.current_floor))

    def execute(self, method:Literal["FCFS", "SSTF", "LOOK"]="FCFS"):
        '''
        执行调度。  
        method = 
        -  FCFS: 先到先得
        -  SSTF: 最短寻找楼层时间优先
        -  LOOK: 磁盘调度
        '''
        # 开始模拟
        self.method = method
        yield self.eventman.event('start')
        # 电梯待命
        yield from self.elevator_initpark()
        # 处理乘客
        match method:
            case "FCFS":
                # 使用 sorted 对乘客按出现时间排序
                sorted_passengers = sorted(
                    self.passengers,
                    key=lambda p: self.t.time_difference_seconds(self.start_time, p.appear_time)
                )
                
                # 处理排序后的乘客
                for passenger in sorted_passengers:
                    # 找到指定的电梯
                    elevator = next((e for e in self.elevators if e.eid == passenger.call_eid), None)
                    if elevator:
                        # 检查电梯是否已经在乘客所在楼层
                        if elevator.current_floor == passenger.from_floor:  # 这里已经是整数比较
                            yield self.eventman.event(
                                'call_elevator',
                                elevator=elevator,
                                passenger=passenger,
                                floor=self.floor_range[passenger.from_floor]  # 获取Floor对象
                            )
                        else:
                            # 如果电梯不在乘客所在楼层，需要先移动到该楼层
                            # 计算移动时间
                            travel_time = self.t.total_height(
                                elevator.current_floor, 
                                passenger.from_floor,  # 使用整数楼层编号
                                self.floor_range, 
                                elevator
                            ) / elevator.speed
                            
                            # 电梯移动到乘客楼层
                            yield self.eventman.event(
                                'elevator_arrive',
                                addsec=travel_time,
                                elevator=elevator,
                                floor=self.floor_range[passenger.from_floor]  # 获取Floor对象
                            )
                            
                            # 更新电梯位置
                            elevator.current_floor = passenger.from_floor
                            
                            # 乘客呼叫电梯
                            yield self.eventman.event(
                                'call_elevator',
                                elevator=elevator,
                                passenger=passenger,
                                floor=self.floor_range[passenger.from_floor]  # 获取Floor对象
                            )
        
        yield self.eventman.event('end')