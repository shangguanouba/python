# 定义字符串变量name，输出我的名字 小明，请多多关照
name = "张娟"
print("我的名字叫%s，请多多关照！" % name)
# 定义整数变量student_no,输出：我的学号 00001
student_no = 233
print("我的学号是%06d"% student_no)
# 定义小数price、weight、money，输出 苹果的单价9.00元/斤，购买了5.00斤，需要支付45元
price = 9.55
weight = 5.51
money = price*weight
print("苹果的单价%.2f元/斤，购买了%.2f斤，需要支付%.3f元" % (price, weight, money))
# 定义一个小数scale，输出数据比例是10.00%
scale = 0.75
print("数据比例是%.2f%%" % (scale * 100))