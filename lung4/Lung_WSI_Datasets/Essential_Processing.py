import os
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from sklearn.utils import shuffle  # 随机打乱数据
from torchvision import transforms

'''
    
    本数据集需要在预处理时进行统一调整
'''

# 数据文件的基本路径
Data_Dir = "./Original Data"
Train_Dir = os.path.join(Data_Dir, "Train0")
Test_Dir = os.path.join(Data_Dir, "Test0")

Class_Name = ["aca", "scc"]
Tumor_Class = dict((k, v) for v, k in enumerate(Class_Name))
# print(Tumor_Class)

## 读取数据，并进行存储
def Read_Data(Data_Dir):
    Images = []
    Labels = []
    for cls in os.listdir(Data_Dir):
        for img in os.listdir(Data_Dir +'/' +  cls):
            Images.append(Data_Dir + '/' + cls + '/' + img)
            Labels.append(Tumor_Class[cls])

    # Images, Labels = shuffle(Images, Labels)
    return Images, Labels

## 绘制数据的比例
def Draw_Scale(Train_Labels, Test_Labels):
    Data_Labels = Train_Labels + Test_Labels
    # 绘制各个类别的比例
    plt.figure(figsize = (7, 6))
    color_cls = ['#4285f4', '#ea4335']  # 各类别的颜色
    plt.rcParams.update({'font.size': 14})
    plt.pie([len([x for x in Data_Labels if x == Class_Name[0]]),
             len([x for x in Data_Labels if x == Class_Name[1]])
             # len([x for x in Data_Labels if x == Class_Name[2]]),
             # len([x for x in Data_Labels if x == Class_Name[3]])
             ],
            labels = Class_Name, colors = color_cls, autopct = '%.1f%%',
            explode = (0.025, 0.025), startangle = 30)
    plt.title("Scale of Classes")

    # 绘制训练集和测试集的比例
    plt.figure(figsize = (7, 6))
    color_cls = ['#4285f4', '#ea4335']
    plt.rcParams.update({'font.size': 14})
    plt.pie([len(Train_Labels), len(Test_Labels)],
            labels = ["Train", "Test"], colors = color_cls, autopct = '%.1f%%',
            explode = (0.05, 0), startangle = 30)
    plt.title("Scale of Split")

    plt.show()

## 选取图像进行展示
def Visualize_samples():
    plt.figure(figsize = (12, 4))
    plt.rc('font', family = "Times New Roman")
    plt.suptitle("Samples of All Classes", fontsize = 24)
    for idx, cls in enumerate(os.listdir(Train_Dir)):
        img = os.listdir(os.path.join(Train_Dir, cls))[0]  # 选取类别排序后的第一张
        img_path = os.path.join(Train_Dir, cls, img)
        # print(img_path)
        loc = int('14' + str(idx + 1))
        # print(loc)
        plt.subplot(loc)
        plt.imshow(cv.imread(img_path))
        plt.title(cls)
        plt.axis('off')
    plt.show()
    print("已成功展示各类别MRI图像样本！")

## 展示图像的基本属性
''' 各个图像的格式相同，都是三通道，但尺寸不同 '''
def Basic_characters(Images):
    num = len(Test_Images)
    for i in range(num):
        img = cv.imread(Images[i])
        print("第{}张图像，维度是{}，格式是{}".format(i + 1, img.shape, img.dtype))


if __name__ == '__main__':
    ## 从文件中读取数据
    Train_Images, Train_Labels = Read_Data(Train_Dir)
    Test_Images, Test_Labels = Read_Data(Test_Dir)

    ## 绘制数据的组成比例
    # Draw_Scale(Train_Labels, Test_Labels)
    ## 选取数据进行展示
    # Visualize_samples()
    ## 展示图像的一些基本属性
    # Basic_characters(Test_Images)