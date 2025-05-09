import torch
import random
import torchvision.transforms as T
import torchvision.transforms.functional as TF

class Augmenter():
    """
    Class to apply augmentations to multiple images such that 
    all undergo identical changes.
    
    Parameters
    ----------
    aug_dict : dict
        Dictionary where keys give the name of augmentation and the
        values provide the parameters.
    
    Examples
    --------
    Import PIL since torch transforms require this format
    >>> from PIL import Image
    
    Provide a dictionary with different probabilities for each augmentation.
    >>> aug = {'hflip': {'prob': 1.0},
    ...        'vflip': {'prob': 0.0},
    ...        'rotate': {'degrees': [0, 360],
    ...                   'prob': 0.0}
    ...    }
    >>> augmenter = Augmenter(aug)
    
    Create a dummy image to flip.
    >>> img = np.zeros((10,10))
    
    Place 255 in the top left corner.
    >>> img[0:2, 0:2] = 255
    
    Convert to PIL
    >>> img = Image.fromarray(img)
    
    Observe how the value of 255 flips after augmenting.
    >>> img = augmenter([img])[0]
    >>> print(np.array(img)[0,9] == 255)
    True
        
    Notes
    -----
    Currently only flips (vertical and horizontal) and rotations 
    are implemented.
    
    """
    def __init__(self, aug_dict):
        
        self.augs = aug_dict
        self.hflip = T.RandomHorizontalFlip(p=1)
        self.vflip = T.RandomVerticalFlip(p=1)
 
    def perform_hflip(self, arrays):
        p = self.augs['hflip']['prob']
        # generate random value between 0-1, if < prob then do aug
        if random.random() <= p:
            for i, array in enumerate(arrays):
                arrays[i] = self.hflip(array)
        return arrays
                    
    def perform_vflip(self, arrays):
        p = self.augs['vflip']['prob']
        if random.random() <= p:
            for i, array in enumerate(arrays):
                arrays[i] = self.vflip(array)
        return arrays
        
    def perform_rot(self, arrays):
        params = self.augs['rotate']
        p = params['prob']
        degrees = params['degrees']

        if random.random() <= p:
            # get the rotation angle
            angle = T.RandomRotation.get_params(degrees)
            for i, array in enumerate(arrays):
                arrays[i] = TF.rotate(array, angle)
                
        return arrays
    
    def __call__(self, arrays):
        """Applies augmentations to a set of arrays.
        
        Parameters
        ----------
        arrays : list
            List of arrays or tensors. For example, multiple images from 
            different modalities which will both be augmented.
            
        Returns
        -------
        arrays : list
            List containing all augmented images.
        """

        if 'hflip' in self.augs:
            arrays = self.perform_hflip(arrays)
                
        if 'vflip' in self.augs:
            arrays = self.perform_vflip(arrays)
                
        if 'rotate' in self.augs:
            arrays = self.perform_rot(arrays)
        
        # returns a list containing all arrays
        return arrays