# -*- coding: utf-8 -*-

from qiniu import Auth, put_data, etag
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key
access_key = '4pT5Yt-6ai6mPmGrpT2B0Z36G1C1tqpfo0zIMyg1'
secret_key = 'KkdV8ED0FFhODgvv2v-YRKEeNUqGIgmfgtt7VFzD'


def storage(file_data):
    """
    上传文件到七牛
    :param file_data: 要上传的文件数据
    :return:
    """
    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = 'ihome-shangguan'

    # 上传后保存的文件名
    # key = 'my-python-logo.png'

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    ret, info = put_data(token, None, file_data)

    if info.status_code == 200:
        return ret.get('key')
    else:
        raise Exception('上传七牛失败')


if __name__ == '__main__':
    with open('./1.png', 'rb') as f:
        file_data = f.read()
        storage(file_data)