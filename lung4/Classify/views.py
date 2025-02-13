import json
import logging
import os
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from PIL import Image

import torch
from torchvision import transforms
from ViT_Classifier.vit_model import vit_large_patch32_224_in21k as Create_model

from Login.models import Is_login
from Classify import models
logger = logging.getLogger(__name__)
# Create your views here.
## 向模型数据库增添数据
def Mk_data_C(request):
    Model_info = {"Name": "Vision Transformer",
                  "Description": "The ViT model is a high-performance image classification model based on deep learning",
                  "Route":"ViT_Classifier/weights/model-epoch-100.pth",
                  "Classes": 2
                  }
    models.ViT_Model.objects.create(**Model_info)  # 将字典拆解成独立的元素作为形参
    # models.Login_PW.objects.filter(id=1).delete()  # 删除数据的操作
    return HttpResponse("插入数据成功！")

# 从数据库读取模型信息
vit = models.ViT_Model.objects.get(id=1)  # 记录对象

### 进行初始化，服务器启动时就加载模型
device = torch.device('cpu')
model = Create_model(num_classes = 2, has_logits = False).to(device)
# 加载模型训练好的权重
#model = torch.nn.DataParallel(model)
#model = model.modules.to(torch.device('cpu'))
path_1 = os.path.dirname(os.path.dirname(__file__))  # 当前路径
path_2 = vit.Route
model_path = os.path.join(path_1, path_2)
model_weights = torch.load(model_path, map_location = lambda storage, loc:storage)
#print(model_weights["model_state_dict"])
#model_weights =  model_weights.pop('CLassify.views')
model.load_state_dict(model_weights["model_state_dict"], strict = False)
model.to('cpu')


#model_weights.pop('head.weight')
#model_weights.pop('head.bias')
# 对数据进行预处理
Img_label = {"肺腺癌-LUAD" : 0, "肺鳞细胞癌-LUSC" : 1}
Data_processing = transforms.Compose([  # 对图像进行转换
        transforms.ToTensor(),  # 转换格式
        transforms.Resize((224, 224)),
    ])

def index(request):
    fl = Is_login.objects.get(id = 1)
    if (fl.log_flag == 0):
        Err_message = "访问系统请先登录！"
        return render(request, "login.html", {'Err_message': Err_message})
    elif (fl.log_flag == 1):
        Suc_message = "登录成功！"
        fl.log_flag = 2  # 登录标志，不用再提示
        fl.save()
        return render(request, "index.html", {'Suc_message': Suc_message})
    else:
        Suc_message = None
        return render(request, "index.html", {'Suc_message': Suc_message})

## 上传图像并进行分类
def upload_discriminate(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':  # 满足ajax请求时
        try:
            file = request.FILES.get("myfile")
            if not file:
                res_dic = {"status": 400, "message": "No file uploaded"}
                return JsonResponse(res_dic)

            img = Image.open(file).convert('RGB')  # 将二进制流转换为图像数据

            save_path = './static/uploads/'
            if not os.path.exists(save_path):  # 检查目录是否存在
                os.makedirs(save_path)  # 如果不存在则创建目录
            img.save(os.path.join(save_path, file.name))  # 保存到相应路径
            img_path = os.path.join('/static/uploads', file.name)

            # 进行分类
            img_tensor = Data_processing(img)
            img_tensor = torch.unsqueeze(img_tensor, dim=0)  # 扩展第一个维度作为 batch
            model.eval()  # 推断模式
            with torch.no_grad():
                output = model(img_tensor)
                if isinstance(output, tuple):
                    output = output[0]  # 提取第一个元素，通常是主要输出张量
                output = torch.squeeze(output.to(device)).cpu()  # 删除大小为1的维度
                predict = torch.softmax(output, dim=0)
                predict_cla = torch.argmax(predict).numpy()

            res = list(Img_label.keys())[predict_cla]
            print(f"本次识别的结果为：{res}")

            res_dic = {"img_path": img_path, "Cla_result": res, "status": 200}
            return JsonResponse(res_dic)

        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            res_dic = {"status": 500, "message": "Internal Server Error"}
            return JsonResponse(res_dic)
    else:
        res_dic = {"status": 405, "message": "Invalid request method"}
        return JsonResponse(res_dic)


## 展示脑肿瘤的相关信息
def tumor_info(request):
    fl = Is_login.objects.get(id=1)
    if (fl.log_flag == 0):
        Err_message = "访问系统请先登录！"
        return render(request, "login.html", {'Err_message': Err_message})
    else:
        return render(request, "tumor_info.html")

## 退出登录
def log_out(request):
    fl = Is_login.objects.get(id=1)
    fl.log_flag = 0
    Err_message = "退出成功！"
    return render(request, "login.html", {'Err_message': Err_message})
