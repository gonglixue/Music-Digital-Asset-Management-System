from flask import Blueprint

auth = Blueprint('auth',__name__)

from . import views
#from . import watermark
# 这是auth蓝本的包的构造文件。在这个文件里创建了蓝本对象，再从views.py模块中引入路由。
# auth蓝本中定义了与用户认证系统相关的路由
