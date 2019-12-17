xiaoming_dict = {"name":"小明"}
# 1.取值
print(xiaoming_dict["name"])
# 2.增加/修改   如果key存在，修改指，key不存在新增键值对
xiaoming_dict["age"]=18
xiaoming_dict["name"]="大明"
# 3.删除
xiaoming_dict.pop("name")
# 4.合并
temp_dict={"height":1.75}
xiaoming_dict.update(temp_dict)
# 5.清空
xiaoming_dict.clear()
print(xiaoming_dict)