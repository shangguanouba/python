# coding:utf-8

from . import api
from ihome.utils.captcha.captcha import captcha
from ihome.utils.response_code import RET
from ihome import redis_store, constants, db
from flask import current_app, jsonify, make_response, request
from ihome.models import User
from ihome.libs.yuntongxun.sms import CCP
# from ihome.tasks.tasks_sms import send_sms
# from ihome.tasks.sms.tasks import send_sms
import random



# GET 127.0.0.1/api/v1.0/image_codes/<image_code_id>
@api.route('/image_codes/<image_code_id>')
def get_image_code(image_code_id):
    """
    获取图片验证
    :param image_code_id: 图片验证码id
    :return: 验证码图片
    """
    # 业务处理
    # 生成图片验证码图片
    name, text, image_data = captcha.generate_captcha()  # 名字，真实文本，图片数据

    # 将验证码真实值和编号保存在redis中
    # redis_store.set('image_code_%s' % image_code_id, text)  # 这是redis字符串
    # redis_store.expire('image_code_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES)  # 设置字符串有效期
    try:
        redis_store.setex('image_code_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)  # key值，有效期，记录值
    except Exception as e:
        # 捕获异常，记录日志
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='sava image code id failed')

    # 返回图片
    resp = make_response(image_data)
    resp.headers['Content_Type'] = 'image/jpg'
    return resp


# GET 127.0.0.1/api/v1.0/sms_codes/<mobile>
@api.route("/sms_codes/<re(r'1[345678]\d{9}'):mobile>")
def get_sms_code(mobile):
    """获取短信验证码"""
    # 获取参数
    image_code = request.args.get('image_code')
    image_code_id = request.args.get('image_code_id')
    # 进行校验
    if not all ([image_code_id, image_code]):
        # 表示参数不完整
        return jsonify(reeno=RET.PARAMERR, errmsg='参数不完整')

    # 业务逻辑处理
    # 从redis中取出真是的图片验证码
    try:
        real_image_code = redis_store.get('image_code_%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron= RET.DBERR, errmsg='redis数据库异常')

    # 判断图片验证码是否过期
    if real_image_code is None:
        # 表示图片验证码已过期
        return jsonify(errno=RET.NODATA, errmsg='图片验证码已过期')

    # 删除redis中的图片验证码，防止用户使用同一个验证码验证多次
    try:
        redis_store.delete('image_code_%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    # 与用户填写的值进行对比
    if real_image_code.lower() != image_code.lower():
        # 表示用户填写的图片验证码错误
        return jsonify(errno=RET.DATAERR, errmsg='图片验证码错误')

    # 判断对于这个手机号的操作，在60秒内有没有之前的记录，如果有，则认为用户操作频繁，不接受处理
    try:
        send_flag = redis_store.get('send_sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            # 表示60秒内之前发送过请求
            return jsonify(errno=RET.REQERR, errmsg='请求过于频繁，请60秒之后重试')

    # 判断手机号是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            # 表示手机号存在
            return jsonify(errno=RET.DATAERR, errmsg='手机号已存在')

    # 如果手机号不存在则生成短信验证码
    sms_code = '%06d' % random.randint(0, 999999)

    # 保存真实的短信验证码
    try:
        redis_store.setex('sms_code_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 保存发送给这个手机号的记录，防止用户在60秒内再次出发短信的操作
        redis_store.setex('send_sms_code_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存短信验证码异常')
    # 发送短信
    try:
        ccp = CCP()
        result = ccp.sendTemplateSMS(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES/60)], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='发送异常')

    # 使用celery异步发送短信，delay函数调用后立即返回
    # send_sms.delay(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES/60)], 1)

    # 发送成功
    if result == 0:
        return jsonify(errno=RET.OK, errmsg='发送成功')
    else:
        return jsonify(errno=RET.THIRDERR, errmsg='发送失败')



