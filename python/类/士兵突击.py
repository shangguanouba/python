class Gun:
    def __init__(self,model):
        # 1.枪的型号
        self.model = model
        # 2.子弹的数量
        self.bullet_count = 0

    def add_bullte(self,count):
        self.bullet_count += count

    def shoot(self):
        # 1.判断子弹的数量
        if self.bullet_count <= 0:
            print("[%s]没有子弹了。。。"% self.model)
            return
        # 2.发射子弹,-1
        self.bullet_count -= 1
        # 3.提示发射信息
        print("[%s] 突突突。。。[%d]" %(self.model,self.bullet_count))


class Soldier:
    def __init__(self,name):
        self.name = name
        # 枪  新兵没有枪
        self.gun = None
    def fire(self):
        # 1.判断有没有枪
        if self.gun is None:
            print("%s还没有枪" % self.name)
            return
        # 2.高喊口号
        print("重啊。。。%s" % self.name)
        # 3.让子弹装枪
        self.gun.add_bullte(50)
        # 4.让子弹发射
        self.gun.shoot()


# 1.创建枪对象
ak47 = Gun("AK47")


# 2.创建士兵
shibin = Soldier("许三多")
shibin.gun = ak47
shibin.fire()

