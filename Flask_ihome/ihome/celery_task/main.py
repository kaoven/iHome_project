# coding:utf-8

from celery import Celery
from . import config


# 创建celery的应用对象
app_celery = Celery("ihome")

# 导入celery的配置信息
app_celery.config_from_object(config)


# 搜索celery的异步任务
app_celery.autodiscover_tasks(
    ["ihome.celery_task.sms"]
)