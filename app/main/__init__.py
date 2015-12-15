from flask import Blueprint

main = Blueprint('main',__name__)

from . import views,errors # 放在末尾、因为在view.py和error.py中还要导入蓝本main，所以需要避免循环依赖

# 程序中创建一个子包，用于保存蓝本。蓝本就创建于这个构造文件
