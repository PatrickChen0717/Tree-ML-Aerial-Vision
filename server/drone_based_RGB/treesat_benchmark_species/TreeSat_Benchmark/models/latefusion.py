import torch
import torch.nn as nn
from .resnet import Resnet
from .custom_blocks import BasicBlock1x1
from torchvision.models.resnet import ResNet
    
class Resnet3x3And1x1(Resnet):
    """Model with 2 or 3 branches. 1 Resnet, and either 1 or 2 (based on 
    number of inputs) 1x1 Resnets (so a regular Resnet but all 3x3 convs 
    replaced with 1x1 convs).
    """
    def __init__(self, 
                 base_model, 
                 n_classes, 
                 n_bands, 
                 p_dropout = 0.25, 
                 unfreeze = False,
                 headless = True):
    
    
        super().__init__(base_model,
                         12, 
                         n_bands[0], 
                         p_dropout, 
                         unfreeze,
                         headless)
        self.n_bands = n_bands
        
        self.model2 = ResNet(BasicBlock1x1, [2, 2, 2, 2])
        self.model2.conv1 = nn.Conv2d(n_bands[1], 
                                      64, 
                                      kernel_size=3, 
                                      stride=1, 
                                      padding=1, 
                                      bias=False)
        total_feats = 512*2
        
        # here we decide whether to add the 3rd branch or not
        if len(n_bands) == 3:
            self.model3 = ResNet(BasicBlock1x1, [2, 2, 2, 2])
            self.model3.conv1 = nn.Conv2d(n_bands[2], 
                                          64, 
                                          kernel_size=3, 
                                          stride=1, 
                                          padding=1, 
                                          bias=False)
            total_feats += 512

        self.model2.fc = nn.Linear(total_feats, 12)
        
    def spatial_branch(self, x):
        """Should use usual Resnet for aerial. Aerial has more spatial
        information so will make more sense to use 3x3 convs.
        """
        x = self.model.conv1(x)
        x = self.model.bn1(x)
        x = self.model.relu(x)
        x = self.model.maxpool(x)

        x = self.model.layer1(x)
        x = self.dropout(x)
        
        x = self.model.layer2(x)
        x = self.dropout(x)
        
        x = self.model.layer3(x)
        x = self.dropout(x)
        
        x = self.model.layer4(x)
        x = self.dropout(x)
        
        x = self.model.avgpool(x)
        x = torch.flatten(x, 1)
        
        return x

    def spectral_branch(self, model, x):
        """Should use Resnet that has only 1x1 convs for Sentinel. Sentinel has more 
        spectral information so will make more sense to use 1x1 convs.
        """
        x = model.conv1(x)
        x = model.bn1(x)
        x = model.relu(x)

        x = model.layer1(x)
        x = self.dropout(x)
        
        x = model.layer2(x)
        x = self.dropout(x)
        
        x = model.layer3(x)
        x = self.dropout(x)
        
        x = model.layer4(x)
        x = self.dropout(x)
        
        x = model.avgpool(x)
        x = torch.flatten(x, 1)
        
        return x
    
    def forward(self, x):
        x1 = x[0]
        x2 = x[1]
        if len(x) == 3:
            x3 = x[2]
        
        x1 = self.spatial_branch(x1)
        x2 = self.spectral_branch(self.model2, x2)
        
        # if we have a third mode then feed it through
        if len(self.n_bands) == 3:
            x3 = self.spectral_branch(self.model3, x3)
            x = torch.cat([x1, x2, x3], dim = 1)
        else:
            x = torch.cat([x1, x2], dim = 1)

        x = self.model2.fc(x)
                
        return x