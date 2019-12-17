# coding:utf-8

from . import api
from ihome.utils.commons import login_required
from flask import g, current_app, request, jsonify, session
from ihome.utils.image_storage import storage
from ihome.utils.response_code import RET
from ihome.models import User
from ihome import db
from ihome.constants import QINIU_URL_DOMAIN


@api.route('/users/avatar', methods=['POST'])
@login_required
def set_user_avatar():
    """
    设置用户头像
    参数： 图片（多媒体表单格式） 用户id （g。user_id）
    :return:
    """
    # 装饰器中的代码已经将user_id保存到g对象，所以视图中可直接读取
    user_id = g.user_id

    # 获取图片
    image_file = request.files.get('avatar')

    if image_file is None:
        return jsonify(errno=RET.PARAMERR, errmsg='未上传图片')

    image_data = image_file.read()

    # 调用七牛上传图片
    try:
        file_name = storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传图片失败')

    # 保存文件名到数据库中
    try:
        User.query.filter_by(id=user_id).update({'avatar_url': file_name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='保存图片信息失败')

    # 保存成功
    avatar_url = QINIU_URL_DOMAIN + file_name
    return jsonify(errno=RET.OK, errmsg='保存成功', data={'avatar_url': avatar_url})


@api.route('/users/name', methods=['PUT'])
@login_required
def change_user_name():
    """
    设置用户名
    参数： 用户名  用户id
    :return:
    """
    # 获取数据
    user_id = g.user_id
    req_date = request.get_json()

    # 校验数据
    if req_date is None:
        return jsonify(errno=RET.PARAMERR, errmsg='参数不完整')

    name = req_date.get('name')

    # 判断是否为空
    if not name:
        return jsonify(errno=RET.PARAMERR, errmsg='用户名不能为空')

    # 保存用户名
    try:
        User.query.filter_by(id=user_id).update({'name': name})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='用户名保存失败')

    # 更新session中的name值
    session['name'] = name

    # 保存成功返回数据
    return jsonify(errno=RET.OK, errmsg='修改成功')


@api.route('/user', methods=['GET'])
@login_required
def get_user_profile():
    """
    个人主页获取个人业务信息
    包括： 头像，手机，用户名
    要求： json格式
    :return:
    """
    # 获取用户信息
    user_id = g.user_id

    # 查询获取用户头像url、手机号、用户名
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户信息失败')
    # user_avatar = user.get('avatar_url')
    # user_mobile = user.get('mobile')
    # user_name = user.get('name')
    # 判断获取的user是否为空
    if user is None:
        return jsonify(errno=RET.NODATA, errmsg='无效操作')

    # 返回数据
    return jsonify(errno=RET.OK, errmsg='OK', data=user.to_dict())


@api.route('/users/auth', methods=['GET'])
@login_required
def get_user_auth():
    """
    获取用户实名认证
    """
    user_id = g.user_id

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取用户实名信息失败')
    if user is None:
        return jsonify(errno=RET.NODATA, errmsg='无效操作')
    return jsonify(errno=RET.OK, errmsg='OK', data=user.auto_to_dict())


@api.route('/users/auth', methods=['POST'])
@login_required
def set_user_auth():
    """
    保存实名认证信息
    参数： 真实名，身份证号
    类型：json
    :return:
    """
    # 获取数据
    user_id = g.user_id
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    real_name = req_data.get('real_name')
    id_card = req_data.get('id_card')

    # 校验数据完整性
    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg='数据不完整')

    try:
        User.query.filter_by(id=user_id, real_name=None, id_card=None).update({'real_name': real_name, 'id_card': id_card})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='实名认证保存失败')
    return jsonify(errno=RET.OK, errmsg='OK')