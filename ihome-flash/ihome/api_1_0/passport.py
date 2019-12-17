# coding:utf-8

from . import api
from flask import request, jsonify, current_app, session
from ihome.utils.response_code import RET
from ihome import redis_store, db, constants
from ihome.models import User
from sqlalchemy.exc import IntegrityError
import re


@api.route('/users', methods=['POST'])
def register():
    """注册
    请求参数： 手机号，短信验证码，密码, 确认密码
    参数格式：json
    """
    # 获取json数据，返回字典
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    sms_code = req_dict.get('sms_code')
    password = req_dict.get('password')
    password2 = req_dict.get('password2')

    # 校验参数
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 判断手机号格式
    if not re.match(r'1[345678]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机格式不正确')
    if password != password2:
        return jsonify(errno=RET.PARAMERR, errmsg='两次密码不一致')

    # 业务处理：
    # 从redis中取出短信验证码
    try:
        real_sms_code = redis_store.get('sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='读取真实短信验证码失败')

    # 判断短信验证码是否过期
    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码已过期')

    # 删除短信验证码，防止重复验证
    try:
        redis_store.delete('sms_code_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 判断短信验证码是否正确
    if real_sms_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码错误')
    # 判断用户填写的手机号是否注册过
    # try:
    #     user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR, errmsg='数据库异常')
    # else:
    #     if user is not None:
    #         return jsonify(errno=RET.DATAEXIST, errmsg='手机号已注册')

    # 保存用户注册数据到数据库表中
    user = User(name=mobile, mobile=mobile)
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 数据库操作出错后事务回滚
        db.session.rollback()
        # 表示手机号出现了重复值,即手机号已注册
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAEXIST, errmsg='手机号已注册')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询数据库异常')

    # 保存登录状态到session中
    session['name'] = mobile
    session['mobile'] = mobile
    session['user_id'] = user.id
    # 返回结果
    return jsonify(errno=RET.OK, errmsg='注册成功')


@api.route('/sessions', methods=['POST'])
def login():
    """登录
    参数： 手机号，密码
    """
    # 获取参数
    req_dict = request.get_json()
    mobile = req_dict.get('mobile')
    password = req_dict.get('password')

    # 校验参数
    # 参数完整校验
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    # 手机号格式
    if re.match(r'1[345678]\d{9}]', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式不正确')
    # 判断错误次数是否超过限制， 如果超过限制则返回
    user_ip = request.remote_addr  # 获取用户的ip地址
    try:
        access_nums = redis_store.get('access_num_%s' % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums is not None and int(access_nums) >= constants.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR, errmsg='登录次数太多，请稍后重试')

    # 从数据库中根据手机号查询用户的数据对象
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户拾失败')

    # 用数据库的密码与填写的密码进行对比验证
    if user is None or not user.check_password(password):
        # 验证失败返回提示信息，记录错误次数，返回信息
        try:
            redis_store.incr('access_num_s%' % user_ip)
            redis_store.expire('access_num_s%' % user_ip, constants.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='用户或密码错误')

    # 如果验证成功，保存登录状态 在session找中
    session['name'] = user.name
    session['mobile'] = user.mobile
    session['user_id'] = user.id

    return jsonify(errno=RET.OK, errmsg='登录成功')


@api.route('/session', methods=['GET'])
def check_login():
    """检查登录状态"""
    # 尝试从session中获取用户名
    name = session.get('name')
    # 如果session中的用户存在，则表示用户已登录
    if name is not None:
        return jsonify(errno=RET.OK, errmsg='true', data={'name': name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg='false')


@api.route('/session', methods=['DELETE'])
def logout():
    """退出登录"""
    session.clear()
    return jsonify(errno=RET.OK, errmsg='ok')