# 输入苹果单价
price = float(input("苹果的单价:" ))
# 输入苹果的重量
weight = float(input("苹果的重量:" ))
"""
价格转换
price = float(price_str )
重量转换
weight = float(weight_str )
计算支付金额  两个字符串之间不能直接用乘法
"""
money = price * weight
print(money)
