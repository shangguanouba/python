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
        gevent.spawn(download, "2,jpg", "http://img2.imgtn.bdimg.com/it/u=1014351345,765809171&amp;fm=26&amp;gp=0.jpg"),
        gevent.spawn ( download, "3,jpg", "http://img4.imgtn.bdimg.com/it/u=2465752662,1622343376&amp;fm=26&amp;gp=0.jpg" ),
    ])


if __name__ == '__main__':
    main()