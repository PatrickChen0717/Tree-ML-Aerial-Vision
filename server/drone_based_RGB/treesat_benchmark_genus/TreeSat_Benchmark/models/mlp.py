import torch.nn.functional as F
from .resnet import HeadlessResnet
import torch.nn as nn
import torch

class FullyConnectedNetwork(nn.Module):
    """Multi-layer perceptron model. Bascially just uses fully connected
    layers rather than 3x3 convs. Only can work with very small images,
    otherwise the number of weights in the model will be way too high given
    that each layer is fully connected.
    """
    def __init__(self, input_size, n_bands, p_drop = 0.3, n_class=0):
        super().__init__()
        
        self.fc1 = nn.Linear(input_size*input_size*n_bands, 512)
        self.fc2 = nn.Linear(512,512)
        self.fc3 = nn.Linear(512, 512)

        self.dropout = nn.Dropout(p_drop)
        
        # set n_class to 0 if we want headless model
        self.n_class = n_class
        if n_class:
            self.head = nn.Sequential(
                                  nn.Linear(512, 1024),
                                  nn.ReLU(),
                                  nn.Dropout(p = p_drop),
                                  nn.Linear(1024, 12)
            )
        
        
    def forward(self,x):
        # flatten image input
        _, c, h, w = x.shape
        x = x.view(-1, c*h*w) # [batch, c*h*w]
        
        x = F.relu(self.fc1(x)) # [batch, 512]
        x = self.dropout(x)
        x = F.relu(self.fc2(x)) # [batch, 512]
        x = self.dropout(x)
        x = F.relu(self.fc3(x)) # [batch, 512]
        
        if self.n_class:
            x = self.head(x)
        
        return x
    
    
class ResNetMLP(nn.Module):
    """Model with 2 branches of Resnet and MLP. 
    """
    def __init__(self, 
                 base_model_resnet,
                 n_bands_res,
                 input_size_mlp, 
                 n_bands_mlp, 
                 n_class,
                 p_drop = 0.3):
        super().__init__()
        
        self.resnet = HeadlessResnet(base_model_resnet,
                                     n_class, 
                                     n_bands_res, 
                                     p_drop)
        self.avgpool = nn.AdaptiveAvgPool2d(1)
        
        self.mlp = FullyConnectedNetwork(input_size_mlp, 
                                         n_bands_mlp, 
                                         p_drop)

        self.head = nn.Sequential(
                                  nn.Linear(512+512, 2048),
                                  nn.ReLU(),
                                  nn.Dropout(p = p_drop),
                                  nn.Linear(2048, 12)
        )
        
    def forward(self, x):
        x1 = x[0] # Aerial
        x2 = x[1] # Sentinel
        
        x1 = self.resnet(x1) # [batch, 512, h, w]
        x1 = self.avgpool(x1) # [batch, 512, 1, 1]
        x1 = torch.flatten(x1, 1) # [batch, 512]
        
        x2 = self.mlp(x2) # [batch, 512]
        
        x = torch.cat([x1, x2], dim = 1).squeeze() # [batch, 512*3]
        
        x = self.head(x) # [batch, n_class]
        
        return x
    
    
class ResNetMLP2(nn.Module):
    """Model with 3 branches of ResNet and 2 seperate MLP.
    """
    def __init__(self, 
                 base_model_resnet,
                 n_bands_res,
                 input_size_mlp, 
                 n_bands_mlp, 
                 n_class = 12,
                 p_drop = 0.3):
        super().__init__()
        
        self.resnet = HeadlessResnet(base_model_resnet,
                                     n_class, 
                                     n_bands_res, 
                                     p_drop)
        self.avgpool = nn.AdaptiveAvgPool2d(1)
        
        self.mlps2 = FullyConnectedNetwork(input_size_mlp, 
                                           n_bands_mlp[0], 
                                           p_drop)
        self.mlps1 = FullyConnectedNetwork(input_size_mlp, 
                                           n_bands_mlp[1], 
                                           p_drop)

        self.head = nn.Sequential(
                                  nn.Linear(512+512+512, 2048),
                                  nn.ReLU(),
                                  nn.Dropout(p = p_drop),
                                  nn.Linear(2048, 12)
        )
        
    def forward(self, x):
        x1 = x[0] # Aerial
        x2 = x[1] # Sentinel2
        x3 = x[2] # Sentinel1
        
        x1 = self.resnet(x1) # [batch, 512, h, w]
        x1 = self.avgpool(x1) # [batch, 512, 1, 1]
        x1 = torch.flatten(x1, 1) # [batch, 512]
        
        x2 = self.mlps2(x2) # [batch, 512]
        x3 = self.mlps1(x3) # [batch, 512]
        
        x = torch.cat([x1, x2, x3], dim = 1).squeeze() # [batch, 512*3]
        
        x = self.head(x) # [batch, n_class]
        
        return x