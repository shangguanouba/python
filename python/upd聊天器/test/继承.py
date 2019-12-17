class Animal:
    def eat(self):
        print("吃")

    def drink(self):
        print("喝")

    def run(self):
        print("跑")

    def sleep(self):
        print("睡")


class Dog(Animal):
    def jiao(self):
        print("旺旺叫")


class Taidi(Dog):
    def fiy(self):
        print("飞")
    # 子类中重新方法就会重写方法，调用时不再调用父类的方法
    def jiao(self):
        print("嗷嗷叫")
        # 使用 super() 调用父类的方法
        super().jiao()
        # 另外一种调用父类方法，self作为参数传递进来
        Dog.jiao(self)


wangcai = Taidi()
wangcai.eat()
wangcai.drink()
wangcai.run()
wangcai.sleep()
wangcai.jiao()

wangcai.fiy()