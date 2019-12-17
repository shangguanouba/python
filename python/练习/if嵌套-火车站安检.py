# 定义布尔型变量 has_ticket表示是否有车票
has_ticket = True
# 定义整型变量 knife_length表示刀的长度 单位：厘米
knife_length = int(40)
# 首先判断是否有车票
if has_ticket:
    print("车票检查通过，请进行安检")
    # 安检检查刀的长度，超过20厘米不允许进站
    if knife_length<=20:
        print("请进站")
    else:
        print("您携带的道具长%d厘米，不允许进站" % knife_length)
else:print("请先购买车票")
# 如果没有车票不许进站