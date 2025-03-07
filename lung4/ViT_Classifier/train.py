import os
import math
import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import torch
import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler
from torch.utils.tensorboard import SummaryWriter
from torchvision import transforms
import transforms as trans
import matplotlib.pyplot as plt

from My_Data import WSI_Data
from Lung_WSI_Datasets.Essential_Processing import Read_Data
from vit_model import vit_large_patch32_224_in21k as create_model
from utils import train_one_epoch, evaluate



def main(args):
    device = torch.device(args.device if torch.cuda.is_available() else "cpu")
    print("using device", device)

    if not os.path.exists("./weights"):
        os.makedirs("./weights")

    tb_writer = SummaryWriter()

    Train_Images, Train_Labels = Read_Data(os.path.join(args.data_path, "Train0"))
    Test_Images, Test_Labels = Read_Data(os.path.join(args.data_path, "Test0"))

    trainsize = (224, 224)

    data_transform = {
        "train": transforms.Compose([
            trans.CropCenterSquare(),
            transforms.Resize(trainsize),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.RandomRotation(30),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]),
        "test": transforms.Compose([
            trans.CropCenterSquare(),
            transforms.Resize(trainsize),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
    }

    Train_data = WSI_Data(Train_Images, Train_Labels, data_transform["train"])
    Test_data = WSI_Data(Test_Images, Test_Labels, data_transform["test"])

    batch_size = args.batch_size
    nw = min([os.cpu_count(), batch_size if batch_size > 1 else 0, 8])
    print('Using {} dataloader workers every process'.format(nw))
    Train_loader = torch.utils.data.DataLoader(Train_data,
                                               batch_size=batch_size,
                                               shuffle=True,
                                               num_workers=nw,
                                               collate_fn=Train_data.collate_fn)
    Test_loader = torch.utils.data.DataLoader(Test_data,
                                              batch_size=batch_size,
                                              shuffle=False,
                                              num_workers=nw,
                                              collate_fn=Test_data.collate_fn)

    model = create_model(num_classes=2, has_logits=False).to(device)

    if args.freeze_layers:
        for name, para in model.named_parameters():
            if "head" not in name and "pre_logits" not in name:
                para.requires_grad_(False)
            else:
                print("training {}".format(name))
    pg = [p for p in model.parameters() if p.requires_grad]
    optimizer = optim.SGD(pg, lr=args.lr, momentum=0.9, weight_decay=5E-5)
    Epoch = args.Extra_epochs + args.epochs if args.Resume else args.epochs
    scheduler = lr_scheduler.CosineAnnealingLR(optimizer=optimizer, T_max=Epoch)

    if args.Resume:
        print("Start continue training！")
        Weights_path = args.checkpoints
        Weights_checkpoint = torch.load(Weights_path, map_location=device)
        Weights = Weights_checkpoint["model_state_dict"]
        optimizer.load_state_dict(Weights_checkpoint["optimizer_state_dict"])
        scheduler.load_state_dict(Weights_checkpoint["scheduler_state_dict"])
        start_epoch = Weights_checkpoint["epoch"]
        end_epoch = start_epoch + args.Extra_epochs + 1
    else:
        Weights_path = args.weights
        Weights = torch.load(Weights_path, map_location=device)
        start_epoch = -1
        end_epoch = args.epochs

    if Weights_path != "":
        assert os.path.exists(Weights_path), "weights file: '{}' not exist.".format(Weights_path)
        weights_dict = Weights
        if args.Resume:
            print(model.load_state_dict(weights_dict, strict=False))
        else:
            del_keys = ['head.weight', 'head.bias'] if not model.has_logits else ['pre_logits.fc.weight', 'pre_logits.fc.bias', 'head.weight', 'head.bias']
            for k in del_keys:
                del weights_dict[k]
            print(weights_dict.keys())
            print(model.load_state_dict(weights_dict, strict=False))

    train_losses = []
    train_accuracies = []
    val_losses = []
    val_accuracies = []
    learning_rates = []

    for epoch in range(start_epoch + 1, end_epoch):
        # train，训练一个epoch
        train_loss, train_acc, val_loss, val_acc = train_one_epoch(model=model,
                                                                   optimizer=optimizer,
                                                                   data_loader=Train_loader,
                                                                   val_loader=Test_loader,
                                                                   device=device,
                                                                   epoch=epoch)

        scheduler.step()
        train_losses.append(train_loss)
        train_accuracies.append(train_acc)
        val_losses.append(val_loss)
        val_accuracies.append(val_acc)
        learning_rates.append(optimizer.param_groups[0]["lr"])

        tags = ["train_loss", "train_acc", "val_loss", "val_acc", "learning_rate"]
        tb_writer.add_scalar(tags[0], train_loss, epoch)
        tb_writer.add_scalar(tags[1], train_acc, epoch)
        tb_writer.add_scalar(tags[2], val_loss, epoch)
        tb_writer.add_scalar(tags[3], val_acc, epoch)
        tb_writer.add_scalar(tags[4], optimizer.param_groups[0]["lr"], epoch)

        if (epoch + 1) % 25 == 0:
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "loss": train_loss,
                "scheduler_state_dict": scheduler.state_dict()
            }, "./weights/model-epoch-{}.pth".format(epoch + 1))

    final_test_loss, final_test_acc = evaluate(model=model, data_loader=Test_loader, device=device,
                                               loss_function=torch.nn.CrossEntropyLoss())
    print("最终模型在测试集上的平均精度为%.2f%%" % (final_test_acc * 100))

    # Plotting and saving the curves
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.plot(range(1, len(train_losses) + 1), train_losses, label='Train Loss')
    plt.plot(range(1, len(val_losses) + 1), val_losses, label='Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss')
    plt.legend()
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(range(1, len(train_accuracies) + 1), train_accuracies, label='Train Accuracy')
    plt.plot(range(1, len(val_accuracies) + 1), val_accuracies, label='Validation Accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig('training_validation_curves.jpg')  # Save the figure as JPG
    plt.show()

    # 绘制学习率曲线并保存为单独的图片
    plt.figure()
    plt.plot(range(1, len(learning_rates) + 1), learning_rates, label='Learning Rate')
    plt.xlabel('Epochs')
    plt.ylabel('Learning Rate')
    plt.title('Learning Rate Schedule')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig('learning_rate.jpg')  # Save the figure as JPG
    plt.show()
    



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--num-classes', type=int, default=2)
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--lr', type=float, default=0.001)
    parser.add_argument('--lrf', type=float, default=0.01)
    parser.add_argument('--model-name', default='', help='create model name')
    parser.add_argument('--data-path', type=str, default="../Lung_WSI_Datasets/Original Data")
    parser.add_argument('--weights', type=str, default="./Pretrained_Weights/vit_large_patch32_224_in21k.pth",
                        help='initial weights path')
    parser.add_argument('--freeze-layers', type=bool, default=True)
    parser.add_argument('--device', default='cuda:0', help='device id (i.e. 0 or 0,1 or cpu)')
    parser.add_argument('--Resume', type=bool, default=False)
    parser.add_argument('--Extra-epochs', type=int, default=6)

    opt = parser.parse_args()
    main(opt)
