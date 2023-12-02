# 安装Django

```shell
pip install django
pip install djangorestframework
pip install django-cors-headers
```

# 每个service的启动顺序

1. 先进入XXX_service目录，启动各个后端服务 (后端端口配置)
2. 端口分配：frontend 8000, user 8001, conference 8002, paper 8003

```shell
cd XXX_service/
python manage.py runserver 800X
```