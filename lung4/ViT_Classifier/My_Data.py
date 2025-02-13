from PIL import Image
import torch
from torch.utils.data import Dataset

'''
    重写Dataset类，用于导入自己的数据集
'''
class WSI_Data(Dataset):
    def __init__(self, Images, Labels, Transform = None):
        self.Images = Images
        self.Labels = Labels
        self.Transform = Transform

    def __len__(self):
        return len(self.Images)  # 返回列表的长度

    def __getitem__(self, item):
        img = Image.open(self.Images[item]).convert('RGB')  # 这里已经转换成了三通道
        # RGB为彩色图片(三通道)，L为灰度图片
        if img.mode != 'RGB':
            raise ValueError("image: {} isn't RGB mode.".format(self.Images[item]))
        label = self.Labels[item]

        if self.Transform is not None:
            img = self.Transform(img)

        return img, label

    @staticmethod  # 定义在类里的函数，不需要表示自身对象的self和自身类的cls
    def collate_fn(batch):
        # 官方实现的default_collate可以参考
        # https://github.com/pytorch/pytorch/blob/67b7e751e6b5931a9f45274653f4f653a4e6cdf6/torch/utils/data/_utils/collate.py
        images, labels = tuple(zip(*batch))

        images = torch.stack(images, dim=0)  # 沿着新的维度对Tensor进行连接
        labels = torch.as_tensor(labels)
        return images, labels
