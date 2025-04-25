import torchvision.models
import numpy as np
from pydoc import locate
from .resnet import *
from .latefusion import *
from .transformer import *
from .mlp import *

def get_classification_model(modelname, classes, config, debug = False):
    model_dict = {'Resnet': create_resnet,
                  "MLP" : create_mlp,
                  "XformerS2Resnet": create_xform_s2_resnet,
                  "XformerS1Resnet": create_xform_s1_resnet,
                  "XformerResnetAllModes": create_xform_resnet_am,
                  "Res3x3AndRes1x1": create_3_1_resnet,
                  "ResMLPOne": create_res_mlp,
                  "ResMLPTwo": create_res_mlp2
                 }
    
    model_builder = model_dict[modelname]
    
    return model_builder(classes, config, debug)
    
def find_n_bands(config, pattern = "_means"):
    """Finds total number of bands across all modalities using config file
    metadata.
    """
    keys = list(config.keys())
    # get all config keys with the pattern
    matches = [k for k in keys if pattern in k]
    # get the length of each list stored in the key
    counts = [len(config[k]) for k in matches]
    
    return np.sum(counts)

def duplicate_pretrained_channel(model):
    """Duplicates the third input channel of a Resnet that has been 
    pre-trained on 3 band ImageNet images. By duplicating the input
    channel's weights we can pass 4 band imagery into the pre-trained model.
    """
    # duplicate one channel
    duplicate = model.state_dict()['conv1.weight'][:,-1,:,:]
    duplicate = duplicate.view(64, 1, 7, 7)
    
    # get the original weights
    orig = model.state_dict()['conv1.weight']
    
    # combine the original and duplicated weights
    combo = torch.cat([orig, duplicate], dim=1)
    
    # assign the new weights to the input layer
    model.conv1.weight = nn.Parameter(combo)
    
    return model

def get_n_aerial_bands(config):
    """Finds the number of aerial bands within the config file metadata.
    """
    if 'band_means' in config:
        n_bands = len(config['band_means'])
    elif 'aer_band_means' in config:
        n_bands = len(config['aer_band_means'])
    else:
        m = "Did not find any aerial data mean/std information in the config."
        raise AssertionError(m)
        
    return n_bands

def load_pytorch_model(config):
    """Loads a pytorch model defined by the "model" argument in the config 
    file
    """
    pretrained = False
    if 'pretrained' in config:
        pretrained = config['pretrained']
    
    # get the base resnet model based on the config "model" argument
    if config['model'] is not None:
        model_base = locate(config['model'])(pretrained)

    # if we use a pretrained resnet but want 4 bands as input, need to duplicate one channel
    n_bands = get_n_aerial_bands(config)
    if 'resnet' in config['model'] and pretrained and n_bands == 4:
        model_base = duplicate_pretrained_channel(model_base)
        
    return model_base

def create_resnet(classes, config, debug):
    """Single Resnet model."""
    unfreeze = None
    if 'unfreeze' in config:
        unfreeze = config['unfreeze']
        
    return Resnet(load_pytorch_model(config), 
                  len(classes),
                  n_bands = len(config['band_means']),
                  p_dropout = config['prob_drop'],
                  unfreeze = unfreeze)

def create_mlp(classes, config, debug):
    return FullyConnectedNetwork(
                                6, 
                                len(config["band_means"]), 
                                config['prob_drop'],
                                len(classes)
    )

def create_xform_s2_resnet(classes, config, debug):
    """Sentinel 2 in xformer and aerial in resnet."""
    return ResnetAndTransformer(len(classes),
                                load_pytorch_model(config),
                                len(config['aer_band_means']),
                                config['prob_drop'],
                                n_bands_vit=1,
                                img_size=18, 
                                patch_size=6, 
                                embed_dim=config["embed_dim"],
                                depth=config["xformer_depth"],             
                                num_heads=config["xformer_heads"], 
                                mlp_ratio=4.,             
                                qkv_bias=True
                               )

def create_xform_s1_resnet(classes, config, debug):
    """Sentinel 1 in xformer and aerial in resnet."""
    return ResnetAndTransformer(len(classes),
                                load_pytorch_model(config),
                                len(config['aer_band_means']),
                                config['prob_drop'],
                                n_bands_vit=1,
                                img_size=(6, 18), 
                                patch_size=6, 
                                embed_dim=config["embed_dim"],
                                depth=config["xformer_depth"],             
                                num_heads=config["xformer_heads"], 
                                mlp_ratio=4.,             
                                qkv_bias=True
                               )

def create_xform_resnet_am(classes, config, debug):
    """Creates 2 branch network. 1 Branch is Resnet, other is ViT. Expects
    that S2 and S1 are both passed to the ViT branch.
    """
    return ResnetAndTransformer(len(classes),
                                load_pytorch_model(config),
                                len(config['aer_band_means']),
                                config['prob_drop'],
                                n_bands_vit=1,
                                img_size=(24, 18), 
                                patch_size=6, 
                                embed_dim=config["embed_dim"],
                                depth=config["xformer_depth"],             
                                num_heads=config["xformer_heads"], 
                                mlp_ratio=4.,             
                                qkv_bias=True
                               )

def create_3_1_resnet(classes, config, debug):
    """Creates 2 or 3 branch model depending on the number of inputs found in
    the config file. 1 branch is vanilla Resnet, other branches
    are Resnets with all 3x3 convs replaced with 1x1 convs.
    """
    
    n_bands = []
    n_bands.append(len(config['aer_band_means']))
    if 's2_band_means' in config:
        n_bands.append(len(config['s2_band_means']))
    if 's1_band_means' in config:
        n_bands.append(len(config['s1_band_means']))
    if len(n_bands) < 2:
        m = "Need at least 2 modalities, only found %d in config file."
        raise AssertionError(m % len(n_bands))
        
    return Resnet3x3And1x1(load_pytorch_model(config), 
                           len(classes), 
                           n_bands = n_bands,
                           p_dropout = config["prob_drop"]
            )


def create_res_mlp(classes, config, debug):
    """Model with 2 branches, 1 Resnet for aerial, and 1 MLP for either
    S1 or S2.
    """
    
    if "s2_band_means" in config:
        n_bands_mlp = len(config["s2_band_means"])
    elif "s1_band_means" in config:
        n_bands_mlp = len(config["s1_band_means"])
    else:
        m = "Could not find n_bands for S2 or S1 in config file."
        raise AssertionError(m)
                 
    return ResNetMLP(load_pytorch_model(config),
                     len(config['aer_band_means']),
                     6, 
                     n_bands_mlp, 
                     len(config["classes"]),
                     p_drop = config["prob_drop"]
                     )

def create_res_mlp2(classes, config, debug):
    """Model with 3 branches, 1 Resnet, 1 MLP for S2 and 1 MLP for S1"""
    n_bands_mlp = []
    if "s2_band_means" in config:
        n_bands_mlp.append(len(config["s2_band_means"]))
    if "s1_band_means" in config:
        n_bands_mlp.append(len(config["s1_band_means"]))
    if len(n_bands_mlp) != 2:
        m = "Only found band information for %d of S2 and S1 in config file."
        raise AssertionError(m % len(n_bands_mlp))
                 
    return ResNetMLP2(load_pytorch_model(config),
                      len(config['aer_band_means']),
                      6, 
                      n_bands_mlp, 
                      len(config["classes"]),
                      p_drop = config["prob_drop"]
                      )