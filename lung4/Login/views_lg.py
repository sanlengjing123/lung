from django.shortcuts import render, HttpResponse,redirect
from django.http import JsonResponse
from Login import models
from django.contrib.auth import authenticate, login  # 调用自带的登录方法
from django.contrib import messages
import re  # 正则表达式

# Create your views here.
def Mk_data(request):
    ## 创建用户名和密码数据
    login_way = {"User_Name": "kust_sys", "Password": "hjn123"}
    login_way1 = {"User_Name": "bupt_sys", "Password": "hjn456"}
    models.Login_PW.objects.create(**login_way1)  # 将字典拆解成独立的元素作为形参
    # models.Classify_vit_model.objects.filter(id=3).delete()  # 删除数据的操作
    return HttpResponse("插入数据成功！")


def log_index(request):
    # models.Login_PW.objects.all().delete()  # 清空所有的表项
    # i = {"log_flag":"0"}
    # models.Is_login.objects.create(**i)
    return render(request, "login.html")

# 都设置成未登录标志
fl = models.Is_login.objects.get(id=1)
fl.log_flag = 0
fl.save()

## 登录系统
def log_for_bs(request):
    obj = models.Login_PW.objects.all()
    id = []
    U_name = []
    Psw = []
    # 获取要求的账号密码
    for info in obj:
        id.append(info.id)
        U_name.append(info.User_Name)
        Psw.append(info.Password)

    if request.method == 'POST':
        Username = request.POST['Username']
        Password = request.POST['Password']

        if (len(Username) == 0):  # 输入为空时
            Err_message = "请输入账号密码进行登录！"
            return render(request, "login.html", {'Err_message': Err_message})
        elif (Username in U_name):  # 属于已经注册的用户
            if (Password in Psw):  # 账号密码均正确，则登录成功跳转至主页
                fl.log_flag = 1  # 登录标志
                fl.save()
                return redirect("/index/")
            else:  # 密码不正确，说明输入错误
                Err_message = "密码输入错误，请重新输入！"
                return render(request, "login.html", {'Err_message': Err_message})
        else:
            Err_message = "用户不存在，请先注册！"
            return render(request, "login.html", {'Err_message': Err_message})

    return render(request, "login.html")


## 进行注册
def reg_for_bs(request):
    obj = models.Login_PW.objects.all()
    id = []
    U_name = []
    Psw = []
    # 获取要求的账号密码
    for info in obj:
        id.append(info.id)
        U_name.append(info.User_Name)
        Psw.append(info.Password)
    ## 注册时获取到的输入
    if request.method == 'POST':
        Username = request.POST['R_Username']
        Password = request.POST['R_Password']
        Password1 = request.POST['R1_Password']
        my_re = re.compile(r'[A-Za-z]', re.S)  # 匹配所有字母

        if (len(Username) == 0):
            Err_message_R = "请输入内容进行注册！"
            return render(request, "login.html", {'Err_message_R': Err_message_R})
        elif Username in U_name:  # 用户名已存在，之前已经注册过
            Err_message_R = "用户已存在，请返回登录！"
            return render(request, "login.html", {'Err_message_R': Err_message_R})
        else:  # 用户未存在，则进行登录步骤
            res_u = re.findall(my_re, Username)  # 检查账号中的字母
            res_p = re.findall(my_re, Password)  # 检查密码中的字母
            if (len(res_u) != 0) and ('_' in Username) and (bool(re.search(r'\d', Username))):  # 账号满足要求的情况
                if (len(res_p) != 0) and (bool(re.search(r'\d', Password))) and (len(Password) >= 6):  # 密码满足要求
                    if (Password1 == Password):  # 密码验证也符合要求，存入数据库中，并返回登录
                        login_way = {"User_Name": Username, "Password": Password}
                        models.Login_PW.objects.create(**login_way)
                        Err_message_R = "注册成功，请返回登录！"
                        return render(request, "login.html", {'Err_message_R': Err_message_R})

                    else:  # 第二次输入的密码不一致
                        Err_message_R = "两次输入的密码不一致，请重新输入"
                        return render(request, "login.html", {'Err_message_R': Err_message_R})
                else: # 密码不符合要求
                    Err_message_R = "密码的设置不符合要求，请输入字母数字的组合，不能少于6位！"
                    return render(request, "login.html", {'Err_message_R': Err_message_R})
            else:  # 账号不符合要求
                Err_message_R = "账号的设置不符合要求，请输入字母、下划线和数字的组合！"
                return render(request, "login.html", {'Err_message_R': Err_message_R})