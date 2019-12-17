# 提示用户输入一个整数
try:
    num = int(input("输入一个整数："))
    # 使用8初一用户输入的整数并且输出
    result = 8/num
    print(result)
except ZeroDivisionError:
    print("除零错误")
except ValueError:
    print("请输入正确的整数")
except Exception as result:
    print("未知错误%s" % result)
else:
    print("尝试成功")
finally:
    prin("无论是否出现错误都会执行的代码")
print("-" * 50)


# 利用异常的传递性，在出程序捕获异常，可以不用关系函数和方法中的异常程序