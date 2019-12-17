class HouseItem:
    def __init__(self, name, area):
        self.name = name
        self.area = area

    def __str__(self):
        return "[%s]占地面积为%.2f㎡" % (self.name, self.area)


class House:
    def __init__(self, house_type, area):
        self.house_type = house_type
        self.area = area
        # 剩余面积
        self.free_area = area
        # 家具名称列表
        self.item_list = []

    def __str__(self):
        return ("户型： %s\n总面积： %.2f[剩余: %.2f]\n家具： %s"
                % (self.house_type, self.area, self.free_area, self.item_list))

    def add_item(self,item):
        print("要添加的%s" % item)
        # 1.判断家具的面积
        if item.area>self.free_area:
            print("%s的面积太大了，无法添加" % item.name)

            return
        # 2.添加家具的名称到列表中
        self.item_list.append(item.name)
        # 3.计算剩余面积
        self.free_area -= item.area

# 1.创建家具
bed = HouseItem ( "席梦思", 4 )
print ( bed )
chest = HouseItem ( "衣柜", 2 )
print ( chest )
table = HouseItem ( "餐桌", 1.5 )
print ( table )
# 2.创建房子
my_home = House("两室一厅",60)
my_home.add_item(bed)
my_home.add_item(chest)
my_home.add_item(table)
print(my_home)