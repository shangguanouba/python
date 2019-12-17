# coding:utf-8


from celery import Celery
from ihome.libs.yuntongxun.sms import CCP


# 定义celery对象
celery_app = Celery('ihome', broker='redis://10.168.0.4.1')

@celery_app.task
def send_sms(to, datas, temp_id):
    """发送短信异步任务"""
    ccp = CCP()
    ccp.sendTemplateSMS(to, datas, temp_id)