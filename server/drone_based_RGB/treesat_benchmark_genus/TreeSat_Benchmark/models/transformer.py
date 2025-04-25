from timm.models.vision_transformer import VisionTransformer
from .resnet import HeadlessResnet
import torch.nn as nn
import torch

class HeadlessVIT(VisionTransformer):
    """Vision transformer without the classification head module. Just acts as
    a feature extractor.
    """
    
    def __init__(self,
                 **kwargs):
        
        super().__init__(**kwargs)

        del self.head
    
    def forward(self, x):
        x = self.forward_features(x)
        return x

    
class ResnetAndTransformer(nn.Module):
    """1 Resnet for aerial, 1 Transformer for S2 and S1 (we concatenate 
    them together). So its basically early fusion for the Sentinel data 
    and then late fusion between aerial and Sentinel. 
    
    Note
    ----
    Should use the S2S1AerialTransformer dataloader.
    """
    def __init__(self, 
                 num_classes,
                 # args for Resnet
                 base_model_resnet,
                 n_bands_res = 4, 
                 p_dropout = 0.3,
                 # args for VIT
                 n_bands_vit=1,
                 img_size=18, 
                 patch_size=6, 
                 embed_dim=768, 
                 depth=12,             
                 num_heads=12, 
                 mlp_ratio=4.,             
                 qkv_bias=True
                 ):
        super().__init__()
        
        self.vit = HeadlessVIT(img_size=img_size, patch_size=patch_size, 
                               in_chans=n_bands_vit, num_classes=num_classes,
                               embed_dim=embed_dim, depth=depth, 
                               num_heads=num_heads, mlp_ratio=mlp_ratio, 
                               qkv_bias=qkv_bias)
        self.resnet = HeadlessResnet(base_model_resnet,
                                     num_classes, 
                                     n_bands_res, 
                                     p_dropout)
        
        self.avgpool = nn.AdaptiveAvgPool2d(1)
        
        self.head = nn.Sequential(
                                  nn.Linear(512+embed_dim, 2048),
                                  nn.ReLU(),
                                  nn.Dropout(p = p_dropout),
                                  nn.Linear(2048, 12)
        )
        
    def forward(self, x):
        x1 = x[0] #first should be aerial
        x2 = x[1] #second Sentinel

        # get feature vector from resnet model
        x1 = self.resnet(x1) # [batch, 512, h, w]
        x1 = self.avgpool(x1) # [batch, 512, 1, 1]
        x1 = torch.flatten(x1, 1) # [batch, 512]
        
        x2 = self.vit(x2) # [batch, embed_dim]
        
        x = torch.cat([x1, x2], dim = 1).squeeze() # [batch, embed_dim+512]
        
        x = self.head(x) # [batch, n_class]
        
        return x