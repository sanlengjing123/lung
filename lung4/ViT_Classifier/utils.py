import os
import sys
import pickle
import random

import torch
from tqdm import tqdm

import matplotlib.pyplot as plt

### 写pickle文件
def write_pickle(list_info: list, file_name: str):
    with open(file_name, 'wb') as f:
        pickle.dump(list_info, f)

### 读
def read_pickle(file_name: str) -> list:
    with open(file_name, 'rb') as f:
        info_list = pickle.load(f)
        return info_list

### 训练一个epoch
def train_one_epoch(model, optimizer, data_loader, val_loader, device, epoch):
    model.train()  # 训练模式
    loss_function = torch.nn.CrossEntropyLoss()
    accu_loss = torch.zeros(1).to(device)  # 累计损失
    accu_num = torch.zeros(1).to(device)   # 累计预测正确的样本数
    optimizer.zero_grad()

    sample_num = 0
    data_loader = tqdm(data_loader, file=sys.stdout)  # 显示训练进度条
    for step, data in enumerate(data_loader):
        images, labels = data
        sample_num += images.shape[0]

        pred = model(images.to(device))
        if isinstance(pred, tuple):
            pred = pred[0]  # 如果 pred 是一个元组，取第一个元素

        pred_classes = torch.argmax(pred, dim=1)  # 使用 torch.argmax 来获取预测的类别
        accu_num += torch.eq(pred_classes, labels.to(device)).sum()

        loss = loss_function(pred, labels.to(device))
        loss.backward()
        accu_loss += loss.detach()

        data_loader.desc = "[train epoch {}] loss: {:.3f}, acc: {:.3f}".format(epoch + 1,
                                                                               accu_loss.item() / (step + 1),
                                                                               accu_num.item() / sample_num)
        # 保证loss不会无穷大
        if not torch.isfinite(loss):
            print('WARNING: non-finite loss, ending training ', loss)
            sys.exit(1)

        optimizer.step()  # 更新
        optimizer.zero_grad()  # 梯度清零

    train_loss = accu_loss.item() / (step + 1)
    train_acc = accu_num.item() / sample_num

    val_loss, val_acc = evaluate(model, val_loader, device, loss_function)  # 评估模型

    return train_loss, train_acc, val_loss, val_acc


@torch.no_grad()  # 不计算梯度
def evaluate(model, data_loader, device, loss_function):
    model.eval()  # 评估模式
    accu_num = torch.zeros(1).to(device)   # 累计预测正确的样本数
    accu_loss = torch.zeros(1).to(device)  # 累计损失

    sample_num = 0
    data_loader = tqdm(data_loader, file=sys.stdout)
    for step, data in enumerate(data_loader):
        images, labels = data
        sample_num += images.shape[0]

        pred = model(images.to(device))
        if isinstance(pred, tuple):
            pred = pred[0]  # 如果 pred 是一个元组，取第一个元素

        pred_classes = torch.argmax(pred, dim=1)  # 使用 torch.argmax 来获取预测的类别
        accu_num += torch.eq(pred_classes, labels.to(device)).sum()

        loss = loss_function(pred, labels.to(device))
        accu_loss += loss

        data_loader.desc = "[Test for the Model] loss: {:.3f}, acc: {:.3f}".format(
            accu_loss.item() / (step + 1), accu_num.item() / sample_num)

    val_loss = accu_loss.item() / (step + 1)
    val_acc = accu_num.item() / sample_num

    return val_loss, val_acc
