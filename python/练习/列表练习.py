name_list=["zhangsan","lisi","wangwu"]
# 1.取值和索引
print(name_list[2])
# 知道数据内容，提取索引位置
print(name_list.index("zhangsan"))
# 2.修改
name_list[1] = "李四"
print(name_list[1])
# 3.增加
name_list.insert(2,"zhaoliu") #insert 可以向列表指定位置追加数据
name_list.append("王小二")  #append可以向列表末尾追加数据
tem_list = ["张伟","张飞","刘备"]
name_list.extend(tem_list)  # extend可以把其他列表中的完整内容最佳到当前列表的末尾
# 4.删除
name_list.remove("wangwu") # remove方法可以从列表中删除指定数据 ,重复的元素会删除第一次出现的元素
name_list.pop(0) # pop方法默认可以把列表中最后一个元素删除，可以指定要删除元素的索引
#name_list.clear() # clear 方法可以清空列表
del name_list[1]  # del 关键字本质上是用来将一个变量从内存中删除的
list_len = len(name_list)


print(name_list)