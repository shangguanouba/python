class Dog:
    def __init__(self,name):
        self.name = name

    def game(self):
        print("够会玩耍")

class XiaoTianQuan(Dog):
    def game(self):
        print("%s会在天上玩耍"% self.name)


class Person:
    def __init__(self,name):
        self.name = name

    def game_with_dog(self,dog):
        print("%s和%s玩耍"% (self.name,dog.name))
        dog.game()


wangcai = XiaoTianQuan("旺财")

xiaoming = Person("小明")

xiaoming.game_with_dog(wangcai)