# import re
# import torch
# import torch.nn as nn
# from torchvision.models import ResNet
# from torchvision.models.resnet import BasicBlock
# import torch.nn.functional as F

# class Resnet(nn.Module):

#     def __init__(self, 
#                  base_model, 
#                  n_classes =12, 
#                  n_bands = 4, 
#                  p_dropout = 0.25, 
#                  unfreeze = False,
#                  headless = False):
#         """
#         Parameters
#         ----------
#         base_model: nn.Module
#             A variant of ResNet, preferably from torchvision.models, or similar.
#         n_classes: int
#             Number of classes.
#         n_bands: int
#             Number of input bands.
#         p_dropout: float
#             Drop out probability
#         unfreeze: None, or List
#             If not None, must be a list of parameter names which should not be frozen.
#             If you want to train all model parameters then just leave this argument as None.
#         headless: bool
#             If True, then the network will have no classification head, and thus will only 
#             return the final extracted features. If False, the model will use the classification
#             head and return class logit scores.
#         """
        
#         # super().__init__()

#         # self.headless = headless
#         # self.dropout = nn.Dropout(p=p_dropout)

#         # # Define high-resolution model
#         # self.highres_model = base_model
#         # if n_bands != 3:
#         #     self.highres_model.conv1 = nn.Conv2d(n_bands, 64, kernel_size=7, stride=2, padding=3, bias=False)

#         # # Save `in_features` before replacing `fc` layer
#         # self.highres_in_features = self.highres_model.fc.in_features
#         # if headless:
#         #     self.highres_model.fc = nn.Identity()  # Replace classification head for headless mode

#         # # Define low-resolution model
#         # self.lowres_model = base_model
#         # if n_bands != 3:
#         #     self.lowres_model.conv1 = nn.Conv2d(n_bands, 64, kernel_size=7, stride=2, padding=3, bias=False)

#         # # Save `in_features` before replacing `fc` layer
#         # self.lowres_in_features = self.lowres_model.fc.in_features
#         # if headless:
#         #     self.lowres_model.fc = nn.Identity()  # Replace classification head for headless mode

#         # # Combined feature dimension
#         # self.num_lowres_levels = 4
#         # combined_feature_dim = self.highres_in_features + self.num_lowres_levels * self.lowres_in_features
#         # if not headless:
#         #     self.fc = nn.Linear(combined_feature_dim, n_classes)

#         # # Unfreeze parameters if specified
#         # if unfreeze:
#         #     self.set_parameter_requires_grad(unfreeze)

#         super().__init__()
#         self.headless = headless
#         self.dropout = nn.Dropout(p=p_dropout)
        
#         # Define high-resolution model
#         self.highres_model = base_model
#         if n_bands != 3:
#             self.highres_model.conv1 = nn.Conv2d(n_bands, 64, kernel_size=7, stride=2, padding=3, bias=False)
#         self.highres_in_features = self.highres_model.fc.in_features
#         if headless:
#             self.highres_model.fc = nn.Identity()
        
#         # Define low-resolution model
#         self.lowres_model = base_model
#         if n_bands != 3:
#             self.lowres_model.conv1 = nn.Conv2d(n_bands, 64, kernel_size=7, stride=2, padding=3, bias=False)
#         self.lowres_in_features = self.lowres_model.fc.in_features
#         if headless:
#             self.lowres_model.fc = nn.Identity()
        
#         # Adjust fc layer based on combined feature dimensions
#         combined_feature_dim = self.highres_in_features + self.lowres_in_features * 2  # Two low-res levels
#         if not headless:
#             # self.fc = nn.Linear(combined_feature_dim, n_classes)
#             print(f"n_classes:{n_classes}")
#             self.fc = nn.Linear(combined_feature_dim, n_classes)
        
#         # Unfreeze pretrained parameters if needed
#         if unfreeze:
#             self.set_parameter_requires_grad(unfreeze)
        
#     def set_parameter_requires_grad(self, unfreeze):
#         for name, param in self.model.named_parameters():
#             if name not in unfreeze:
#                 param.requires_grad = False
            
#     # def forward(self, x_highres):
#     #     # Generate low-resolution inputs
#     #     x_lowres_levels = [
#     #         F.interpolate(x_highres, scale_factor=sf, mode='bilinear', align_corners=False)
#     #         for sf in [0.5, 0.25, 0.125, 0.0625] # 
#     #     ]

#     #     # Process high-resolution input
#     #     x_highres = self.highres_model.conv1(x_highres)
#     #     x_highres = self.highres_model.bn1(x_highres)
#     #     x_highres = self.highres_model.relu(x_highres)
#     #     x_highres = self.highres_model.maxpool(x_highres)
#     #     x_highres = self.highres_model.layer1(x_highres)
#     #     x_highres = self.dropout(x_highres)
#     #     x_highres = self.highres_model.layer2(x_highres)
#     #     x_highres = self.dropout(x_highres)
#     #     x_highres = self.highres_model.layer3(x_highres)
#     #     x_highres = self.dropout(x_highres)
#     #     x_highres = self.highres_model.layer4(x_highres)
#     #     x_highres = self.dropout(x_highres)
#     #     x_highres = F.adaptive_avg_pool2d(x_highres, (1, 1))
#     #     x_highres = torch.flatten(x_highres, 1)

#     #     # Debugging highres feature shape
#     #     # print(f"x_highres shape: {x_highres.shape}")

#     #     # Process low-resolution levels
#     #     lowres_features = []
#     #     for i, x_lowres in enumerate(x_lowres_levels):
#     #         x_lowres = self.lowres_model.conv1(x_lowres)
#     #         x_lowres = self.lowres_model.bn1(x_lowres)
#     #         x_lowres = self.lowres_model.relu(x_lowres)
#     #         x_lowres = self.lowres_model.maxpool(x_lowres)
#     #         x_lowres = self.lowres_model.layer1(x_lowres)
#     #         x_lowres = self.dropout(x_lowres)
#     #         x_lowres = self.lowres_model.layer2(x_lowres)
#     #         x_lowres = self.dropout(x_lowres)
#     #         x_lowres = self.lowres_model.layer3(x_lowres)
#     #         x_lowres = self.dropout(x_lowres)
#     #         x_lowres = self.lowres_model.layer4(x_lowres)
#     #         x_lowres = self.dropout(x_lowres)
#     #         x_lowres = F.adaptive_avg_pool2d(x_lowres, (1, 1))
#     #         x_lowres = torch.flatten(x_lowres, 1)

#     #         # Debugging lowres feature shape
#     #         # print(f"x_lowres[{i}] shape: {x_lowres.shape}")

#     #         lowres_features.append(x_lowres)

#     #     # Concatenate features
#     #     combined_features = torch.cat([x_highres] + lowres_features, dim=1)

#     #     # Debugging combined features shape
#     #     # print(f"Combined features shape: {combined_features.shape}")

#     #     # Pass through classification head if not headless
#     #     if not self.headless:
#     #         combined_features = self.fc(combined_features)

#     #     return combined_features

#     def forward(self, x_highres):
#         # Generate low-resolution inputs (keep three resolutions)
#         x_lowres_levels = [
#             F.interpolate(x_highres, scale_factor=sf, mode='bilinear', align_corners=False)
#             for sf in [0.5, 0.25]  # Only two low-res levels
#         ]

#         # Process high-resolution input
#         x_highres = self.highres_model.conv1(x_highres)
#         x_highres = self.highres_model.bn1(x_highres)
#         x_highres = self.highres_model.relu(x_highres)
#         x_highres = self.highres_model.maxpool(x_highres)
#         x_highres = self.highres_model.layer1(x_highres)
#         x_highres = self.dropout(x_highres)
#         x_highres = self.highres_model.layer2(x_highres)
#         x_highres = self.dropout(x_highres)
#         x_highres = self.highres_model.layer3(x_highres)
#         x_highres = self.dropout(x_highres)
#         x_highres = self.highres_model.layer4(x_highres)
#         x_highres = self.dropout(x_highres)
#         x_highres = F.adaptive_avg_pool2d(x_highres, (1, 1))
#         x_highres = torch.flatten(x_highres, 1)

#         # Process low-resolution levels
#         lowres_features = []
#         for x_lowres in x_lowres_levels:
#             x_lowres = self.lowres_model.conv1(x_lowres)
#             x_lowres = self.lowres_model.bn1(x_lowres)
#             x_lowres = self.lowres_model.relu(x_lowres)
#             x_lowres = self.lowres_model.maxpool(x_lowres)
#             x_lowres = self.lowres_model.layer1(x_lowres)
#             x_lowres = self.dropout(x_lowres)
#             x_lowres = self.lowres_model.layer2(x_lowres)
#             x_lowres = self.dropout(x_lowres)
#             x_lowres = self.lowres_model.layer3(x_lowres)
#             x_lowres = self.dropout(x_lowres)
#             x_lowres = self.lowres_model.layer4(x_lowres)
#             x_lowres = self.dropout(x_lowres)
#             x_lowres = F.adaptive_avg_pool2d(x_lowres, (1, 1))
#             x_lowres = torch.flatten(x_lowres, 1)
#             lowres_features.append(x_lowres)

#         # Concatenate features (x_highres and low-resolution features)
#         combined_features = torch.cat([x_highres] + lowres_features, dim=1)

#         # Debugging combined features shape
#         # print(f"Combined features shape: {combined_features.shape}")

#         # Pass through classification head if not headless
#         if not self.headless:
#             combined_features = self.fc(combined_features)

#         return combined_features

    
# class HeadlessResnet(Resnet):
#     def __init__(self,
#                  base_model, 
#                  n_classes, 
#                  n_bands = 4, 
#                  p_dropout = 0.3):
#         print(f"n_classes HeadlessResnet: {n_classes}")
#         super().__init__(base_model=base_model, 
#                          n_classes=12, 
#                          n_bands = n_bands, 
#                          p_dropout = p_dropout, 
#                          headless = True)

import re
import torch
import torch.nn as nn
from torchvision.models import ResNet
from torchvision.models.resnet import BasicBlock

class Resnet(nn.Module):

    def __init__(self, 
                 base_model, 
                 base_model_lowres, 
                 n_classes = 17, 
                 n_bands = 4, 
                 p_dropout = 0.25, 
                 unfreeze = False,
                 headless = False):
        # print(f"base_model: {base_model}")
        """
        Parameters
        ----------
        base_model: nn.Module
            A variant of ResNet, preferably from torchvision.models, or similar.
        n_classes: int
            Number of classes.
        n_bands: int
            Number of input bands.
        p_dropout: float
            Drop out probability
        unfreeze: None, or List
            If not None, must be a list of parameter names which should not be frozen.
            If you want to train all model parameters then just leave this argument as None.
        headless: bool
            If True, then the network will have no classification head, and thus will only 
            return the final extracted features. If False, the model will use the classification
            head and return class logit scores.
        """
        
        super().__init__()
        
        self.headless = headless
        resnet = base_model
        self.dropout = nn.Dropout(p = p_dropout)

        if n_bands != 3:
            resnet.conv1 = nn.Conv2d(n_bands, 
                                     64, 
                                     kernel_size=7, 
                                     stride=2, 
                                     padding=3, 
                                     bias=False)
        
        if self.headless:
            # if headless we delete the classification head
            del resnet.fc
        else:
            # need to change head to have the correct # of classes
            resnet.fc = nn.Linear(
                      in_features = resnet.fc.in_features, 
                      out_features = n_classes
            )
            
        self.model = resnet
        
        # unfreeze pretrained parameters
        if unfreeze:
            self.set_parameter_requires_grad(unfreeze)
        
    def set_parameter_requires_grad(self, unfreeze):
        for name, param in self.model.named_parameters():
            if name not in unfreeze:
                param.requires_grad = False
            
    def forward(self, x):
        res = []
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

        if not self.headless:
            x = self.model.avgpool(x)
            x = torch.flatten(x, 1)
            x = self.model.fc(x)
                
        return x

        # x_highres = self.highres_model.conv1(x_highres)
        # x_highres = self.highres_model.bn1(x_highres)
        # x_highres = self.highres_model.relu(x_highres)
        # x_highres = self.highres_model.maxpool(x_highres)

        # x_highres = self.highres_model.layer1(x_highres)
        # x_highres = self.dropout(x_highres)
        # x_highres = self.highres_model.layer2(x_highres)
        # x_highres = self.dropout(x_highres)
        # x_highres = self.highres_model.layer3(x_highres)
        # x_highres = self.dropout(x_highres)
        # x_highres = self.highres_model.layer4(x_highres)
        # x_highres = self.dropout(x_highres)

        # x_lowres = self.lowres_model.conv1(x_lowres)
        # x_lowres = self.lowres_model.bn1(x_lowres)
        # x_lowres = self.lowres_model.relu(x_lowres)
        # x_lowres = self.lowres_model.maxpool(x_lowres)

        # x_lowres = self.lowres_model.layer1(x_lowres)
        # x_lowres = self.dropout(x_lowres)
        # x_lowres = self.lowres_model.layer2(x_lowres)
        # x_lowres = self.dropout(x_lowres)
        # x_lowres = self.lowres_model.layer3(x_lowres)
        # x_lowres = self.dropout(x_lowres)
        # x_lowres = self.lowres_model.layer4(x_lowres)
        # x_lowres = self.dropout(x_lowres)

        # combined_features = torch.cat((x_highres, x_lowres), dim=1)

        # if not self.headless:
        #     combined_features = self.highres_model.avgpool(combined_features)
        #     combined_features = torch.flatten(combined_features, 1)
        #     combined_features = self.fc(combined_features)

        # return combined_features
    
class HeadlessResnet(Resnet):
    def __init__(self,
                 base_model, 
                 n_classes, 
                 n_bands = 4, 
                 p_dropout = 0.3):
        
        super().__init__(base_model=base_model, 
                         n_classes=17, 
                         n_bands = n_bands, 
                         p_dropout = p_dropout, 
                         headless = True)