from pymysql import connect


def main():
    conn = connect(host='127.0.0.1', port=3306, user='root', password='yjhh.com', database='jing_dong', charset='utf8')
    cu = conn.cursor()
    for i in range(10000):
        cu.execute("insert into test_index values('ha-%d')" % i)
        conn.commit()
    cu.close()
    conn.close()


if __name__ == '__main__':
    main()