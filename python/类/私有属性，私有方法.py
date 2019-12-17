class Women:
    def __init__(self,name):
        self.name = name
        self.__age = 18
    def __secret(self):
        print("%s 的年龄是%d" %(self.name,self.__age))


xiaofang = Women("小芳")
# 私有属性在外部不能被直接使用
#print(xiaofang.__age)
print(xiaofang._Women__age)
# 私有方法不允许在外部直接使用
#xiaofang.__secret()
xiaofang._Women__secret()