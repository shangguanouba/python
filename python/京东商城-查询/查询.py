import pymysql
from pymysql import connect


class JD(object):
    def __init__(self):
        # 创建connection连接
        self.conn = connect(host='127.0.0.1', port=3306, user='root', password='yjhh.com', database='jing_dong', charset='utf8')
        # 获得cursor对象
        self.cursor = self.conn.cursor()

    def __del__(self):
        # 关闭cursor对象
        self.cursor.close()
        self.conn.close()

    def execute_sql(self, sql):
        self.cursor.execute(sql)
        for temp in self.cursor.fetchall():
            print(temp)

    def show_all_itmes(self):
        sql = "select * from goods;"
        self.execute_sql(sql)

    def show_cates(self):
        sql = "select name from goods_cates;"
        self.execute_sql(sql)

    def show_brands(self):
        sql = "select name from goods_brands;"
        self.execute_sql(sql)

    def add_brands(self):
        item_name = input("输入名称：")
        sql = """insert into goods_brands (name) values ("%s")""" % item_name
        self.cursor.execute(sql)
        self.conn.commit()

    def get_info_by_name(self):
        find_name = input("请输入名称：")
        sql = "select * from goods where name=%s"
        self.cursor.execute(sql, [find_name])

    @staticmethod
    def print_menu():
        print ( "-------京东-------" )
        print ( "1.所有商品" )
        print ( "2.所有商品分类" )
        print ( "3.所有商品品牌分类" )
        print ( "4.添加商品分类" )
        print("5.根据名字查询")
        return input ( "请输入你的选择：" )

    def run(self):

        while True:
            num = self.print_menu()
            if num == "1":
                self.show_all_itmes()
            elif num == "2":
                self.show_cates()
            elif num == "3":
                self.show_brands()
            elif num == "4":
                self.add_brands()
            elif num == "5":
                self.get_info_by_name()
            else:
                print("输入有误，请重新选择：")


def main():
    jd = JD()
    jd.run()


if __name__ == '__main__':
    main()