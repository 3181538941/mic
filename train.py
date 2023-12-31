#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @author LeoWang
# @date 2023/8/5
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from meta import CustomDataset, Model, MyModel, VoltageSensorModel, Tudui
from utils.dataset_ import get_data_names, split_dataset, deal_1, read_data
from utils.util import get_now, get_uuid
import numpy as np

model = Tudui(4000, 50, 32, [3, 4, 5], 37, 0.5)

def model_test(audio):
    audio = np.array(audio).flatten()
    audio = torch.tensor(audio)

    with torch.no_grad():
        output = model(audio)
        _, predicted = torch.max(output, 1)  # 取得分最高的类别
        return predicted.item()


def train(model, optimizer, criterion, train_loader):
    model.train()
    targets, output, data = None, None, None
    try:
        for batch_idx, (data, targets) in enumerate(train_loader):
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, targets)
            loss.backward()
            optimizer.step()

            if batch_idx % 300 == 0:
                print(f'Loss: {loss.item()}')
    except RuntimeError as e:
        print(e)
        print(targets, data, output)


def begin(train_loader, learning_rate=0.001, momentum=0.9, epoch=10):
    filename = get_now()
    # 创建模型实例
    input_size = 3  # 输入大小，即传感器数量
    hidden_size = 16  # 隐藏层大小，可根据需求调整
    output_size = 1  # 输出大小，即传感器状态

    # files = os.listdir('./models')
    files = 1
    if files:
        # model_path = f"./models/{sorted(files)[-1]}"
        model_path = f"./models/2023-08-06_015426.pth"
        model = torch.load(model_path)

    # 定义损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum)

    # 开始训练
    for epoch in range(epoch):
        print(f'Epoch: {epoch + 1}')
        train(model, optimizer, criterion, train_loader)
        print('---------------------------')
        torch.save(model, f"models/{filename}.pth")

    print("Done!", filename)


from utils.util import timeit


@timeit
def load_dataset(start, end):
    # my = []
    _dataset = CustomDataset()
    DATASET_BASE = './dataset'
    csv_files = [_ for _ in os.listdir(DATASET_BASE) if _.endswith('.csv')]
    for csv_file in csv_files[start:end]:
        target = int(csv_file[:3])
        print(csv_file, target)
        audios = read_data(os.path.join(DATASET_BASE, csv_file))
        _dataset.add_dateset([target] * len(audios), audios)
        # my.append([target, len(audios)] )
    _dataset.to_tensor()
    # print(my)
    # exit(1)
    return _dataset


if __name__ == '__main__':
    # deal_1('./data', os.listdir('data'), './dataset')
    # exit(1)

    batch_size = 16
    learning_rate = 0.01
    momentum = 0.7
    epoch = 20
    dataset = load_dataset(start=0, end=3)
    train_, test_ = split_dataset(dataset, batch_size)
    begin(train_, learning_rate, momentum, epoch)

    # for i in test_:
    #     print(i)
    #     print(i[0], model_test(i[0][0))

    # data = read_data('./dataset/001.csv')
    # dataset = CustomDataset(1, data)
    # test_split(dataset)

    # print(read_data('./dataset/001.csv'))
