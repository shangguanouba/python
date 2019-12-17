# 定义类
class Cat:
    def __init__(self, new_name):
        self.name = new_name
    def eat(self):
        # 哪一个对象调用方法，self就是哪一个对象的引用
        print("%s爱吃鱼" % self.name)

    def drink(self):
        print("%s爱喝水" % self.name)

    def __str__(self):
        return "%s没了" % self.name

# 创建对象
tom = Cat("懒猫")
print(tom)
tom.eat()
tom.drink()


# 再创建一个猫对象
lazy_cat = Cat("dalanmao")
print(lazy_cat.name)
lazy_cat.eat()
lazy_cat.drink()


