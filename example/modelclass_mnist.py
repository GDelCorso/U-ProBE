import torch.nn as nn
import torch.nn.functional as F

class CustomModel(nn.Module):
    def __init__(self):
        super(CustomModel, self).__init__()
        self.fc1 = nn.Linear(28 * 28, 128)
        self.fc2 = nn.Linear(128, 64)
        self.dropout1 = nn.Dropout(p=0.2)  
        self.fc3 = nn.Linear(64, 10)
        self.dropout2 = nn.Dropout(p=0.2)

    def forward(self, x):
        x = x.view(-1, 28 * 28)
        x = F.relu(self.fc1(x))
        x = self.dropout1(x)
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        x = self.dropout2(x)
        return F.log_softmax(x, dim=1)