# coding:utf-8


from ihome.celery_task.main import app_celery
from ihome.libs.yuntongxun.sms import CCP


@app_celery.task
def send_sms(to, datas, temp_id):
    ccp = CCP()
    result = ccp.send_template_sms(to,datas,temp_id)
    return result