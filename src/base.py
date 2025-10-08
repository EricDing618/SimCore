from __future__ import annotations
from datetime import datetime, timedelta

class SimCoreBaseObject:
    def __init__(self):
        self.timeline = Timeline()

class Timeline:
    '''时间线类，管理时间，每个实例都有一个起始时间'''
    def __init__(self, start_time:str='1970/01/01 00:00:00'):
        self.last_time = self.current_time = start_time
    def update_from(self, target:SimCoreBaseObject):
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
    
# 应对特殊环境
class Floor(SimCoreBaseObject): ...