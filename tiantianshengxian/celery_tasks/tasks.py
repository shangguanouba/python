from django.core.mail import send_mail
from django.conf import settings
from django.template import loader, RequestContext
from celery import Celery
import time
from django_redis import get_redis_connection
# 在woker端加入django环境初始化
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tiantianshengxian.settings')
django.setup()

from goods.models import GoodsType, IndexGoodsBanner, IndexTypeGoodsBanner, IndexPromotionBanner


# 创建celery类的实际对象
app = Celery('celery_tasks.tasks', broker='redis://10.168.0.4:6379/3')


# 定义任务函数
@app.task
def send_register_active_email(to_email, username, token):
    """发送激活邮件"""
    subject = '云鸡华海欢迎您'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = '<h1>%s,欢迎您成为云鸡华海会员</h1>请点击下面连接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (
    username, token, token)
    send_mail(subject, message, sender, receiver, html_message=html_message)
    time.sleep(5)


@app.task
def generate_static_index_html():
    """产生首页静态页面"""
    # 获取商品种类
    types = GoodsType.objects.all()
    # 获取首页轮播商品信息
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')
    # 获取首页促销活动信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')
    # 获取首页分类商品展示信息
    for type in types:
        # 获取type种类首页分类商品的图片展示信息
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1)
        # 获取type种类首页分类商品的文字展示信息
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0)
        # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文件展示信息
        type.image_banners = image_banners
        type.title_banners = title_banners

    # 组织模板上下文
    context = {'types': types,
               'goods_banners': goods_banners,
               'promotion_banners': promotion_banners}
    # 使用模板
    temp = loader.get_template('static_index.html')  # 加载模板文件，返回模板对象
    static_index_html = temp.render(context)  # 模板渲染
    # 生成首页静态页面
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    with open(save_path, 'w') as f:
        f.write(static_index_html)
