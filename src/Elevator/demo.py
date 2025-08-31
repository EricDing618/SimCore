from src.Elevator.core import *

from typing import Generator

import pprint

def demo():
    heap = []
    counter = itertools.count()
    # 创建大楼
    building = Building(
        floor_range=(Floor(-4),Floor(101)),
        start_time='2023/01/01 08:00:00',
        name='柳京饭店'
    )

    # 楼层高度特例
    special_floors = [
        Floor(1,5)
    ]
    for f in special_floors:
        building.floor_range[f.fid] = f

    # 创建电梯
    elevator1 = Elevator(eid=0, max_weight=1000, building=building, name='左', speed=2.5)
    elevator2 = Elevator(eid=1, max_weight=1000, building=building, name='右',speed=2.5)

    # 添加电梯到大楼
    building.elevators = (elevator1, elevator2)

    # 创建乘客
    # 创建乘客（使用整数楼层编号）
    passenger1 = Passenger(pid=1, weight=7000, building=building, from_floor=1, to_floor=5, name='Peter', appear_time='2023/01/01 08:00:10', call_eid=0)
    passenger2 = Passenger(pid=2, weight=80, building=building, from_floor=2, to_floor=6, name='Dick', appear_time='2023/01/01 08:05:20', call_eid=0)

    # 添加乘客到大楼
    building.passengers = [passenger1, passenger2]

    execute = building.execute('FCFS')
    #pprint.pprint(list(execute),indent=4,depth=4)
    for event in execute:
        heapq.heappush(heap,(event['relative_time'], next(counter), event))

    while heap:
        _time, _count, event = heapq.heappop(heap)
        event_type_:str = event['event_type']
        time_:str = event['time']
        building_:Building = event['building']
        elevator_:Elevator = event['elevator']
        passenger_:Passenger = event['passenger']
        floor_:Floor = event['floor']
        match event_type_:
            case 'start':
                print(f"[{time_}] {building_.name}(bid: {building_.bid})模拟开始")
            case 'elevator_idle':
                print(f"[{time_}] 电梯 {elevator_.name}(eid: {elevator_.eid}) 空闲")
            case 'elevator_arrive':
                print(f"[{time_}] 电梯 {elevator_.name}(eid: {elevator_.eid}) 到达 {floor_.fid} 层（速度：{elevator_.speed} m/s）")
            case 'call_elevator':
                print(f"[{time_}] 乘客 {passenger_.name}(pid: {passenger_.pid}) 在楼层 {floor_.fid} 呼叫电梯 {elevator_.name}(eid: {elevator_.eid})（计划），目标楼层 {passenger_.to_floor}，质量 {passenger_.weight}kg")
            case 'passenger_board':
                print(f"[{time_}] 乘客 {passenger_.name}(pid: {passenger_.pid}) 上电梯 {elevator_.name}(eid: {elevator_.eid})")
            case 'passenger_alight':
                print(f"[{time_}] 乘客 {passenger_.name}(pid: {passenger_.pid}) 下电梯 {elevator_.name}(eid: {elevator_.eid})，到达楼层 {passenger_.to_floor}")
            case 'elevator_outweight':
                print(f"[{time_}] 电梯 {elevator_.name}(eid: {elevator_.eid}) 超载！最大载重 {elevator_.max_weight}kg，乘客{passenger_.name}(pid: {passenger_.pid})无法上电梯")
            case 'end':
                print(f"[{time_}] 模拟结束，共计运行 {Tool.time_difference_seconds(building_.start_time, time_)} 秒")
            case 'invalid':
                print(f"[{time_}] 无效事件，信息：{event}")
            case _:
                print(f"[{time_}] 未知事件类型: {event_type_}")

if __name__ == "__main__":
    demo()