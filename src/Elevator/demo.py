from core import *

if __name__ == "__main__":
    # 创建大楼
    building = Building()

    # 创建电梯
    elevator1 = Elevator(eid=1, max_weight=1000, building=building)
    elevator2 = Elevator(eid=2, max_weight=1000, building=building)

    # 添加电梯到大楼
    building.elevators = (elevator1, elevator2)

    # 创建乘客
    passenger1 = Passenger(pid=1, weight=70, building=building, from_floor=1, to_floor=5)
    passenger2 = Passenger(pid=2, weight=80, building=building, from_floor=2, to_floor=6)

    # 添加乘客到大楼
    building.passengers = [passenger1, passenger2]

    print("Building and components initialized successfully.")