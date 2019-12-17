# 注意：定义好函数之后，只表示这个函数封装了一段代码
# 如果不主动调用函数，函数不会主动执行


def sum_2_num(num1, num2):
    """两个数求和"""
    return num1 + num2
    # 注意：return表示返回，下方的代码不会执行

result = sum_2_num ( 23, 45 )
print("计算结果：%d"% result)
