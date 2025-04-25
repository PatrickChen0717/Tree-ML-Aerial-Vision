"""Functions (and their underlying classes) which perform data preprocessing.
These are used in the dataloaders.
"""

import torchvision.transforms as T
import numpy as np
import torch

########################################################################
# BASE TO TENSOR CLASSES
########################################################################
class ToTensor_(object):
    """Dataset Transform: Convert ndarrays to Tensors and then normalize
    the values.
    """
    def __init__(self, means, stds):
        self.means = means
        self.stds = stds
        
    def normalize(self, data):
        raise AssertionError("Not implemented")

    def __call__(self, data):
        """Convert ndarrays to Tensors. Also performs normalization.
        """
        data = data.astype(np.float32)
        data = torch.from_numpy(data)
        data = self.normalize(data)
        return data
    
########################################################################
# BASE NORMALIZATION CLASS
########################################################################

class Normalize():
    """Base normalization class.
    
    Parameters
    ----------
    val1: array, shape=(n_bands, 1, 1)
        An array containing the mean values for each band
    val2: array, shape=(n_bands, 1, 1)
        An array with the standard deviation values for each band
    n_bands: int, 
        Number of bands in a given image.
    """
    def __init__(self, val1, val2, n_bands):
        self.val1 = val1
        self.val2 = val2
        self.n_bands = n_bands
        
    def reshape(self):
        # reshape function that adds 2 empty dimensions which are needed
        # for the normalization functions
        self.val1 = torch.tensor(self.val1).reshape(self.n_bands,1,1)
        self.val2 = torch.tensor(self.val2).reshape(self.n_bands,1,1)
        
    def __call__(self, data):
        self.reshape()
        data = (data - self.val1) / self.val2
        return data
    
########################################################################
# To Tensor Classes which wrap everything together
########################################################################
    
class ToTensorS2(ToTensor_):
    """Class for Sentinel 2 data."""
    def normalize(self, data):
        data = Normalize(self.means, self.stds, 12)(data)
        return data
    
class ToTensorS1(ToTensor_):
    """Class for Sentinel 1 data."""
    def normalize(self, data):
        data = Normalize(self.means, self.stds, 3)(data)
        return data
    
class ToTensorAerial(ToTensor_):
    """Class for four band aerial data."""
    def normalize(self, data):
        data = Normalize(self.means, self.stds, 4)(data)
        return data
    
class ToTensorAerial3Bands(ToTensorAerial):
    """Class for RGB (or any other 3 band combinations) aerial data."""
    def normalize(self, data):
        data = Normalize(self.means, self.stds, 3)(data)
        return data
    
##############################
####### Functions
##############################

def xform_aer_pretrained(aer, means, stds):
    """Used when we use a pre-trained network from ImageNet."""
    aer = aer.transpose(1, 2, 0)
    norm = [T.ToTensor(),
            T.Normalize(means, stds)
           ]
    xform = T.Compose(norm)
    aer = xform(aer)
    
    return aer

def xform_aer_3bands_scratch(aer, means, stds):
    """Normalizes aerial imagery for a network trained from scratch using
    TreeSat data. Thus we apply treesat mean/std. Since TreeSat mean/std
    were calculated on the raw uint8 image values, their values are in the
    range of 0-255 and thus we do not use T.ToTensor because that would
    convert the raw image values to 0-1 range. Instead we use the custom 
    function defined above.
    """
    transformS2 = ToTensorAerial3Bands(means,
                                       stds)
    aer = transformS2(aer)
    
    return aer

def xform_aer_scratch(aer, means, stds):
    """See xform_aer_3bands_scratch.
    """
    transformS2 = ToTensorAerial(means,
                                 stds)
    aer = transformS2(aer)
    
    return aer

def xform_s2(image, means, stds):
    """See xform_aer_3bands_scratch, same logic applies here."""
    transformS2 = ToTensorS2(means,
                             stds)
    s2 = transformS2(image)
    return s2

def xform_s1(image, means, stds):
    """See xform_aer_3bands_scratch, same logic applies here."""
    transformS1 = ToTensorS1(means,
                             stds)
    image = transformS1(image)
    #image = torch.tensor(image)
    #norm = T.Normalize(means, stds)
    #xform = T.Compose([norm])
    #image = xform(image)

    return image