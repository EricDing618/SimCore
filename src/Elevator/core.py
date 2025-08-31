from __future__ import annotations
from datetime import datetime, timedelta
from typing import Literal

import time
import heapq, itertools

class Timeline:
    '''时间线类，管理时间，每个实例都有一个起始时间'''
    def __init__(self, start_time:str='1970/01/01 00:00:00'):
        self.last_time = self.current_time = start_time
    def update_from(self, target:Building|Elevator|Passenger|Floor|Event):
        self.last_time = self.current_time
        self.current_time = target.timeline.current_time
    def update(self, addsec:int=0, new_time:str=None):
        self.last_time = self.current_time
        if new_time:
            self.current_time = new_time
        else:
            self.current_time = Tool.add_seconds_to_datetime(self.current_time, addsec)
    
class Tool:
    '''工具类，包含一些通用方法'''
    @staticmethod
    def myrange(a: int, b: int):
        '''返回一个整数范围的列表'''
        if a > b:
            return range(b, a + 1)
        return range(a, b + 1)
    @staticmethod
    def total_height(a: int, b: int, floor_range: dict[int, Floor]):
        '''计算电梯在两个楼层之间运行的总高度，忽略0层'''
        if a == b:
            return 0
        if a > b:
            a, b = b, a
        return sum(floor_range[f].height for f in Tool.myrange(a, b-1) if f != 0)
    @staticmethod
    def time_difference_seconds(time_str1, time_str2):
        """
        计算两个时间字符串之间的秒数差（time_str2 - time_str1，需自行外加绝对值abs()）
        
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
        self.timeline = Timeline(self.start_time)

    def event(self, 
                 event_type: Literal['start',
                                     'call_elevator',
                                     'elevator_arrive',
                                     'passenger_board',
                                     'passenger_alight',
                                     'elevator_idle',
                                     'elevator_outweight',
                                     'end',
                                     'invalid']='elevator_idle',
                 elevator: Elevator=None,
                 passenger: Passenger=None,
                 floor: Floor=None,
                 time_host:Building|Elevator|Passenger|Floor=None
                 ) -> dict[str, str|int|Building|Elevator|Passenger|Floor]:
        '''
        event_type类型：
        - 'start': 开始模拟
        - 'call_elevator': 乘客呼叫电梯
        - 'elevator_arrive': 电梯到达楼层
        - 'passenger_board': 乘客上电梯
        - 'passenger_alight': 乘客下电梯
        - 'elevator_idle': 电梯空闲
        - 'elevator_outweight': 电梯超载
        - 'end': 结束模拟
        - 'invalid': 无效事件
        '''
        match event_type:
            case 'elevator_outweight':
                assert elevator is not None, "elevator_outweight事件必须指定电梯"
                assert passenger is not None, "elevator_outweight事件必须指定乘客"
            case 'call_elevator'|'passenger_board'|'passenger_alight':
                assert elevator is not None, f"{event_type}事件必须指定电梯"
                assert passenger is not None, f"{event_type}事件必须指定乘客"
                assert floor is not None, f"{event_type}事件必须指定楼层"
                if event_type=='call_elevator':
                    if Tool.time_difference_seconds(elevator.last_active_time, passenger.timeline.current_time) >= elevator.idle_time:
                        elevator.timeline.update(elevator.idle_time)
                        if not elevator.is_idle:
                            return self.event('elevator_idle', elevator=elevator, time_host=elevator)
                if event_type=='passenger_board':
                    if not elevator.add_passenger(passenger):
                        event_type = 'elevator_outweight'
                        elevator.timeline.update(new_time=elevator.timeline.last_time)
                if event_type=='passenger_alight':
                    if not elevator.remove_passenger(passenger):
                        event_type = 'invalid'
                        elevator.timeline.update(new_time=elevator.timeline.last_time)
            case 'elevator_arrive':
                assert elevator is not None, "elevator_arrive事件必须指定电梯"
                assert floor is not None, "elevator_arrive事件必须指定楼层"
            case 'elevator_idle':
                assert elevator is not None, "elevator_idle事件必须指定电梯"
                elevator.is_idle = True

        self.time = time_host.timeline.current_time

        # 为了校准end事件
        if Tool.time_difference_seconds(self.building.timeline.current_time, self.time) > 0:
            self.building.timeline.update_from(time_host)
        self.relative_time = Tool.time_difference_seconds(self.start_time,self.time)
        self.event_type = event_type
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
        self.timeline = Timeline(self.appear_time)
        self.call_eid = call_eid

        assert Tool.time_difference_seconds(self.building.start_time, self.appear_time) >= 0, "乘客出现时间必须在模拟开始时间之后"
        assert self.call_eid in [i.eid for i in self.building.elevators], f"eid {self.call_eid}不存在"
    def __repr__(self):
        return f'Passenger(pid={self.pid}, weight={self.weight}, name={self.name}, from_floor={self.from_floor}, to_floor={self.to_floor})'
    

class Floor:
    '''楼层，负数表示地下，注意忽略0层'''
    def __init__(self, 
                 fid: int, 
                 height: float=3.0,  # 楼层高度，单位米
                 ):
        self.fid = fid
        self.height = height
        self.timeline = Timeline()
    
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
                 idle_time:int|float = 300 # 空闲时间，单位秒

                 ):
        self.eid = eid
        self.name = name if name else eid
        self.max_weight = max_weight
        self.current_weight = 0
        self.passengers: list[Passenger] = []
        self.building = building
        self.timeline = Timeline(self.building.timeline.current_time)
        self.speed = speed #速度，单位(m/s)
        self.height = height
        self.current_floor = 1  # 初始楼层，默认为1楼
        self.idle_time = idle_time # 空闲时间，单位秒
        self.last_active_time = self.timeline.current_time
        self.is_idle = True
    def add_passenger(self, passenger: Passenger):
        if self.current_weight + passenger.weight <= self.max_weight:
            self.passengers.append(passenger)
            self.current_weight += passenger.weight
            self.is_idle = False
            return True
        return False
    def remove_passenger(self, passenger: Passenger):
        if passenger in self.passengers:
            if len(self.passengers) == 1: # 最后一个乘客
                self.last_active_time = passenger.timeline.current_time
                self.is_idle = True
            self.passengers.remove(passenger)
            self.current_weight -= passenger.weight
            return True
        return False
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
        self.start_time = start_time
        self.timeline = Timeline(self.start_time)
        self.t = Tool()
        self.floor_range = {f: Floor(f) for f in self.t.myrange(floor_range[0].fid,floor_range[1].fid) if f != 0}
        self.elevators = elevators
        self.passengers:list[Passenger] = []
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
            elevator.current_floor = current_floor
            yield self.eventman.event('elevator_arrive', elevator=elevator, floor=Floor(elevator.current_floor), time_host=elevator)
            yield self.eventman.event('elevator_idle', elevator=elevator, time_host=elevator)

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
        yield self.eventman.event('start', time_host=self)
        # 电梯待命
        yield from self.elevator_initpark()
        # 使用 sorted 对乘客按出现时间排序
        sorted_passengers = sorted(
            self.passengers,
            key=lambda p: self.t.time_difference_seconds(self.start_time, p.appear_time)
        )
        # 处理乘客
        match method:
            case "FCFS":
                # 处理排序后的乘客
                for i in range(len(sorted_passengers)):
                    passenger = sorted_passengers[i]
                    # 找到指定的电梯
                    elevator = next((e for e in self.elevators if e.eid == passenger.call_eid), None)
                    #print(elevator)

                    if elevator:
                        # 乘客呼叫电梯
                        yield self.eventman.event(
                            'call_elevator',
                            elevator=elevator,
                            passenger=passenger,
                            floor=self.floor_range[passenger.from_floor],  # 获取Floor对象
                            time_host=passenger
                        )
                        # 检查电梯是否已经在乘客所在楼层
                        if elevator.current_floor == passenger.from_floor:  # 这里已经是整数比较
                            elevator.timeline.update_from(passenger)
                            yield self.eventman.event(
                                'passenger_board',
                                elevator,
                                passenger,
                                passenger.from_floor,
                                passenger
                            )
                        else:
                            elevator.timeline.update_from(passenger)
                            # 如果电梯不在乘客所在楼层，需要先移动到该楼层
                            # 计算移动时间
                            travel_time = self.t.total_height(
                                elevator.current_floor, 
                                passenger.from_floor,  # 使用整数楼层编号
                                self.floor_range
                            ) / elevator.speed
                            
                            # 电梯移动到乘客楼层
                            elevator.timeline.update(travel_time)
                            # 更新电梯位置
                            elevator.current_floor = passenger.from_floor
                            yield self.eventman.event(
                                'elevator_arrive',
                                elevator=elevator,
                                floor=self.floor_range[passenger.from_floor],  # 获取Floor对象
                                time_host=elevator
                            )
        
        yield self.eventman.event('end', time_host=self)