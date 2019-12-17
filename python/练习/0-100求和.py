# 定义最终结果的变量
result = 0
# 定义一个整数变量记录循环次数
i = 0
#开始循环
while i <= 100 :
    if i % 2 == 0:
        print(i)
    #每一次循环，都让result和i相加
        result += i
    #处理计数器
    i += 1
print(result)