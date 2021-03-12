# -*- coding: utf-8 -*-
"""HW2_20181202.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1meyEfVpfC6nTgFoPwunzM5VRl3te1cDm

#**인공지능개론_HW2_20181202**
*   CNN을 통한 CIFAR10 set classification model 만들기
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision  # to download 'CIFAR10' datasest
import torchvision.transforms as transforms  # to manipulate input data

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import imshow
# %matplotlib inline

"""###0. Define Hyper-parameters and pre-set device on cuda"""

# Device Configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Adjust Dataset classes and channels
# CIFAR10 set은 RGB 이미지 파일이기 때문에 channel = 3
num_classes = 10
in_channel = 3 

# Hyper-parameters
batch_size = 50
max_pool_kernel = 2
learning_rate = 0.0001
num_epochs = 10

"""### 1. Load Data (CIFAR10 set)"""

# 학습과 test에 필요한 데이터를 로드한다
train_data = torchvision.datasets.CIFAR10(root='./datasets',
                                          train=True,
                                          transform=transforms.ToTensor(),
                                          download=True)
test_data = torchvision.datasets.CIFAR10(root='./datasets',
                                       train=False,
                                       transform=transforms.ToTensor(),
                                       download=True)

"""###2. Define Dataloader

  Dataloader loads data from queue while iters loop
"""

train_loader = torch.utils.data.DataLoader(dataset=train_data,
                                          batch_size=64,
                                          shuffle=True)
test_loader = torch.utils.data.DataLoader(dataset=test_data,
                                          batch_size=64,
                                          shuffle=False)

"""###3. Define Model

  1 to 4 layers and Out-layer(총 5가지) / Optimizer = Adam optimizer

  Epoch, Learning rate, Batchsize, Weight initialize 등은 각자 tuning 하여 사용  가능
"""

class ConvNetStep(nn.Module):
  def __init__(self, num_classes=10):
    super(ConvNetStep, self).__init__()
    # < 1-layer >
    self.layer1 = nn.Sequential(
        # 5*5 kernel, 6 channel out, 2 stride
        nn.Conv2d(in_channels=in_channel, out_channels=6, kernel_size=5, stride=1, padding=2),
        nn.BatchNorm2d(num_features=6), # Batch normalization
        nn.ReLU(), # activation : ReLU
        nn.MaxPool2d(kernel_size=max_pool_kernel) # max-pooling : 2*2 kernel
    )
    # < 2-layer >
    self.layer2 = nn.Sequential(
        # 5*5 kernel, 16 channel out, 2 stride
        nn.Conv2d(in_channels=6, out_channels=16, kernel_size=5, stride=1, padding=2),
        nn.BatchNorm2d(num_features=16), # Batch normalization
        nn.ReLU(), # activation : ReLU
        nn.MaxPool2d(kernel_size=max_pool_kernel) # max-pooling : 2*2 kernel
    )
    # < 3-layer >
    self.fc1 = nn.Sequential(
        nn.Linear(in_features=16*8*8, out_features=120), # 120 output
        nn.ReLU() # activation : ReLU
    )
    # < 4-layer >
    self.fc2 = nn.Linear(in_features=120, out_features=84) # 84 output
    # < Out-layer >
    self.fc3 = nn.Linear(in_features=84, out_features=num_classes) # 10 output
    
  def forward(self, x):
    x = self.layer1(x)
    x = self.layer2(x)
    x = self.fc1(x.reshape(x.size(0), -1))
    x = self.fc2(x)
    x = F.softmax(self.fc3(x))
    return x

model = ConvNetStep()

"""### 4. Set Loss & Optimizer"""

model = ConvNetStep().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate) # Adam optimizer 이용

"""###4. Train"""

total_step = len(train_loader)

for epoch in range(num_epochs):
  for i, (img, label) in enumerate(train_loader):
    # Assign Tensors to Configures Devices (gpu)
    img = img.to(device)
    label = label.to(device)

    # Forward propagation
    outputs = model(img)

    # Get Loss, Compute Gradient, Update Parameters
    loss = criterion(outputs, label)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # Print Loss
    if i % 10000 == 0 or (i+1)==len(train_loader):
      print('Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}'.format(epoch+1, num_epochs, i+1, len(train_loader), loss.item()))

"""###5. Save Model and Load Model to test"""

# Save model
torch.save(model.state_dict(),"model.pth")

# Load model
test_model = ConvNetStep().to(device)
test_model.load_state_dict(torch.load("model.pth"))

# Load Model to test
test_model.eval()

with torch.no_grad():
  correct = 0
  
  for img, lab in test_loader:
    img = img.to(device)
    lab = lab.to(device)
    out = test_model(img)
    _, pred = torch.max(out.data, 1)
    correct += (pred == lab).sum().item()

  print("Accuracy of the network on the {} test images: {}%".format(len(test_loader)*batch_size,
                                                                    100 * correct / (len(test_loader) * batch_size)))