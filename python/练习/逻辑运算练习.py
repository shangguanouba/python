# 定义两个整数变量python_score、c_score，编写程序判断成绩
# 只要有一门成绩》60就算合格
python_score = int(input("python成绩："))
c_score = int(input("C成绩："))
if python_score >60 or c_score>60:
    print("合格")
else:
    print("不合格")

# 在开发中，通常希望某个条件不满足时，执行一些代码，可以使用 not
# 另外，如果需要拼接复杂的逻辑计算条件时，同样也可能使用到 not