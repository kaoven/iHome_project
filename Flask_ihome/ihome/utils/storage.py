# -*- coding: utf-8 -*-

from qiniu import Auth, put_file, put_data


# 需要填写你的 Access Key 和 Secret Key
access_key = 'uzc59bVURbUbazey9vrexXKocNKBUN8NuLijk57N'
secret_key = '-9lenw28jU2REojvGkcsEPWk5Nm9V2HIVqb5Nkts'


def storage_image(file_data):
    """
    上传到七牛服务器
    :param file_data:  要上传的文件的二进制数据
    :return: 正常:返回七牛保存的文件名
    """
    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    bucket_name = 'ihome'

    # # 上传到七牛后保存的文件名, 我们不指定名字，由七牛决定文件名
    key = None

    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)

    # 上传文件的数据
    ret, info = put_data(token, key, file_data)
    # print(info)
    # print("*"*10)
    # print(ret)

    # 判断是否上传成功
    if info.status_code == 200:
        # 表示上传成功
        # 获取七牛保存的文件名
        file_name = ret.get("key")
        return file_name
    else:
        # 上传失败
        # return None
        raise Exception("上传七牛失败")

