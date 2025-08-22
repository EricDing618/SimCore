from datetime import datetime, timedelta

# 示例使用
#original_time = '1970/01/01 00:00:00'
#addsec = 3600  # 增加1小时（3600秒）
#result = add_seconds_to_datetime(original_time, addsec)
#print(result)  # 输出: 1970/01/01 01:00:00
def add_seconds_to_datetime(datetime_str, addsec):
    # 将字符串转换为datetime对象
    dt = datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S')
    
    # 添加秒数
    new_dt = dt + timedelta(seconds=addsec)
    
    # 将结果转换回字符串格式
    return new_dt.strftime('%Y/%m/%d %H:%M:%S')
