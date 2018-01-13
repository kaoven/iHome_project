# coding=utf-8


from CCPRestSDK import REST

# 主帐号
accountSid = '8aaf070860e4d30b0160e9d4aaec02e2'

# 主帐号Token
accountToken = '308d812f4d79410f8e19d4d4c95c771d'

# 应用Id
appId = '8aaf070860e4d30b0160e9d4ab6002e9'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'

# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为列表 例如：['12','34']，如不需替换请填 ''
# @param $tempId 模板Id

# def sendTemplateSMS(to,datas,tempId):
#
#
#     #初始化REST SDK
#     rest = REST(serverIP,serverPort,softVersion)
#     rest.setAccount(accountSid,accountToken)
#     rest.setAppId(appId)
#
#     result = rest.sendTemplateSMS(to,datas,tempId)
#     for k,v in result.iteritems():
#
#         if k=='templateSMS' :
#                 for k,s in v.iteritems():
#                     print '%s:%s' % (k, s)
#         else:
#             print '%s:%s' % (k, v)
#
# sendTemplateSMS(手机号码,内容数据,模板Id)


class CCP(object):
    """自行封装的发送短信的工具类，
       使用单例模式实现，意图是让云通讯的工具REST对象的构建只被执行一次
    """
    # 用来保存CCP类的对象
    instance = None

    def __new__(cls):
        if cls.instance is None:
            # 创建CCP类的对象
            cls.instance = super(CCP, cls).__new__(cls)

            # 初始化REST SDK
            cls.instance.rest = REST(serverIP, serverPort, softVersion)
            cls.instance.rest.setAccount(accountSid, accountToken)
            cls.instance.rest.setAppId(appId)

        return cls.instance

    def send_template_sms(self, to, datas, temp_id):
        result = self.rest.sendTemplateSMS(to, datas, temp_id)
        # for k, v in result.iteritems():
        #
        #     if k == 'templateSMS':
        #             for k, s in v.iteritems():
        #                 print '%s:%s' % (k, s)
        #     else:
        #         print '%s:%s' % (k, v)
        status_code = result.get("statusCode")
        if status_code == "000000":
            # 表示发送成功
            return 0
        else:
            # 表示发送短信失败
            return -1


if __name__ == '__main__':
    ccp = CCP()
    ccp.send_template_sms("18516952650", ["1234", 5], 1)

