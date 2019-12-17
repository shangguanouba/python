def test(num):
    print("在函数内%d的内存地址%d" %(num, id(num)))
    result = "hello"
    print("函数返回数据的内存地址是%d" % id(result))
    return result

a = 10

print("a 变量的内存地址%d" %id(a))

r = test(a)
print("%s的内存地址%d" % (r, id(r)))
