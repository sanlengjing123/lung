"""Classification_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Classify import views
from Login import views_lg
from enhance import views_e
urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index),  # 主页面
    path('upload_discriminate/', views.upload_discriminate),  # 图像分类
    path('tumor_info/', views.tumor_info),
    # path('Mk_data/', views_lg.Mk_data),   # 在数据库中插入用户数据
    path('log_for_bs/', views_lg.log_for_bs),  # 登录
    path('reg_for_bs/', views_lg.reg_for_bs),  # 注册
    path('', views_lg.log_index),  # 初始登录页面
    path('log_out/', views.log_out),  # 退出
    path('Mk_data_C/', views.Mk_data_C),  # 在数据库中插入模型数据
    path('enhance_image/', views_e.enhance_image, name='enhance_image'),
]