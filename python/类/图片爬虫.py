import urllib.request
import gevent
from gevent import monkey


monkey.patch_all()


def download(image_name,image_url):
    ret = urllib.request.urlopen(image_url)
    image_content = ret.read()
    with open(image_name, "wb") as f:
        f.write(image_content)


def main():
    gevent.joinall([
        gevent.spawn(download, "2.png", "https://rpic.douyucdn.cn/asrpic/191009/5104369_1547.png"),
        gevent.spawn ( download, "3.png", "https://rpic.douyucdn.cn/asrpic/191009/1235252_1546.png" ),
    ])


if __name__ == '__main__':
    main()