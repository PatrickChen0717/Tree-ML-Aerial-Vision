import os
import glob
import json
import torch
import rasterio
import numpy as np
from .utils import *
import torch.nn as nn
from pathlib import Path
from .transforms import *
from .augmenter import Augmenter
import torchvision.transforms as T
from torch.utils.data import Dataset

import albumentations as A
from albumentations.pytorch import ToTensorV2

######################################################################
########################### Base loader class ########################
######################################################################

class MultiModalDataset(Dataset):
    """Base class used for loading either single or multiple modalities."""
    def __init__(self, 
                 img_folders, 
                 json_file,
                 split_file, # expects .lst file
                 classes, 
                 band_means, # nested list
                 band_stds, 
                 return_name = False,
                 target_class = None,
                 augmenter = None):
        print(classes)
        self.return_fn = return_name
        self.classes = classes
        self.augmenter = augmenter
        self.band_means = band_means
        self.band_stds = band_stds

        self.folders = img_folders
        files_list_for_split = open(split_file).read().split()
        
        self.oversample_factor = 5
        self.minority_classes = ["Abies",
                                "Acer",
                                "Alnus",
                                "Betula",
                                # "Cleared",
                                # "Fagus",
                                "Fraxinus",
                                # "Larix",
                                # "Picea",
                                # "Pinus",
                                "Populus",
                                "Prunus",
                                # "Pseudotsuga",
                                # "Quercus",
                                "Tilia"]
        self.augmentations = None
        # self.augmentations = A.Compose([
        #     A.HorizontalFlip(p=0.5),   
        #     A.Rotate(limit=20, p=0.5),    
        #     A.RandomBrightnessContrast(p=0.2), 
        #     A.HueSaturationValue(hue_shift_limit=15, sat_shift_limit=25, val_shift_limit=15, p=0.2),
        #     ToTensorV2()                        
        # ])
        self.augmentations = A.Compose([
            A.HorizontalFlip(p=0.5),   
            A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.1, rotate_limit=20, p=0.5),
            A.RandomBrightnessContrast(brightness_limit=0.4, contrast_limit=0.4, p=0.3), 
            A.HueSaturationValue(hue_shift_limit=20, sat_shift_limit=30, val_shift_limit=20, p=0.3),
            A.GridDistortion(num_steps=5, distort_limit=0.3, p=0.3),
            A.GaussianBlur(blur_limit=(3, 7), p=0.3),
            A.CoarseDropout(max_holes=8, max_height=32, max_width=32, p=0.3),
            ToTensorV2()                        
        ])

        # load image target labels from json file
        with open(json_file) as file:
            print('Opening', json_file)
            jfile = json.load(file)
            subsetted_dict = subset_dict_by_filename(files_list_for_split, jfile)
            self.labels = filter_labels_by_threshold(subsetted_dict, 0.07)
            self.rasterData = list(self.labels.keys())
        
        self.rasterData = self.oversample_minority_classes()

        # get all full image paths
        self.path_patterns = [os.path.join(folder, '%s') 
                              for folder in img_folders]
        
        if target_class is not None:
            raise AssertionError("target_class not implemented")
        
    def oversample_minority_classes(self):
        """Duplicate minority class samples to balance the dataset."""
        oversampled_data = []
        for img_name in self.rasterData:
            label = self.labels[img_name]
            
            if isinstance(label, str):
                class_name = label
            elif isinstance(label, (list, np.ndarray, torch.Tensor)):
                label_index = np.argmax(label) if isinstance(label, (list, np.ndarray)) else torch.argmax(torch.tensor(label)).item()
                class_name = self.classes[label_index]
            else:
                raise ValueError(f"Unexpected label type: {type(label)}")

            if class_name in self.minority_classes:
                # Duplicate samples for minority classes
                # print(f"oversample: {[img_name] * self.oversample_factor}")
                oversampled_data.extend([img_name] * self.oversample_factor)
            else:
                oversampled_data.append(img_name)

        return oversampled_data
    
    def __len__(self):
        return len(self.rasterData)
        
    def perform_transforms(self, imgs_list):
       """A function for performing normalization of all image modalities."""
       raise AssertionError("perform_transforms not implemented")
    
    def augment(self, image):
        """Performs augmentation on one or more image modalities."""
        return self.augmenter([image])[0]
    
    def assert_images_correct(self, image):
        assert image.shape[0] == 4, "Aerial has wrong number of bands."
        
    
    def __getitem__(self, idx):
        # ensure the idx is in a list
        if torch.is_tensor(idx):
            idx = idx.tolist()
        
        # get file name
        img_name = self.rasterData[idx]
        # get all the full paths of the file from different modality folders
        img_paths = [path % img_name for path in self.path_patterns]
        
        # get a list containing all of the image arrays from diff modalities
        imgs = [load_image_and_label(path, 
                                     self.labels,
                                     self.classes)[0]
                for path in img_paths]
        # get the labels
        label = load_image_and_label(img_paths[0], 
                                     self.labels,
                                     self.classes)[1]
        # print(f"self.classes:{self.classes}")
        # print(f"label shape: {label.shape}")
        #ASSUMPTION IS THAT AERIAL IS THE FIRST ELEMENT IN IMGS LIST, THEN S2 THEN S1
        image = self.perform_transforms(imgs)
        
        # apply augmentations
        if self.augmenter is not None:
            image = self.augment(image)
        
        if isinstance(label, torch.Tensor):
            label_index = torch.argmax(label).item() 
        # print(f"Label: {label}, Type: {type(label)}")

        if self.classes[label_index] in self.minority_classes:
            if self.augmentations is not None:
                # print(f"Augment: {self.classes[label_index]}")
                if isinstance(image, torch.Tensor):
                    image = image.permute(1, 2, 0).cpu().numpy() 

                augmented = self.augmentations(image=image)
                image = augmented["image"]

                if isinstance(image, np.ndarray): 
                    image = torch.from_numpy(image).permute(2, 0, 1).float()

        self.assert_images_correct(image)
        # print(f"Final image shape: {image.shape}")
        # print(f"Final label shape: {label.shape}")
        
        if not self.return_fn:
            return image, label
        else:
            return image, label, img_name
    
######################################################################
###################### Loaders for only AERIAL data ##################
######################################################################

class AerialDataset(MultiModalDataset):
    """Loader that loads NIR+RGB aerial data by itself. Only for use with
    networks that will be trained from scratch.
    """
    def perform_transforms(self, imgs_list):
        aer = imgs_list[0]
        # Normalize Aerial
        aer = xform_aer_scratch(aer, self.band_means[0], self.band_stds[0])
        return aer
    
class AerialPTDataset(MultiModalDataset):
    """Loader that loads NIR+RGB aerial data by itself. Only for use with
    networks that have been pretrained and take 4 bands as input.
    
    Note
    ----
    When using a pre-trained network, the input may need to be resized 
    to the same dims as the images the network originally was trained 
    on (e.g. 224x224 for ImageNet). However, some networks (e.g. Resnet) 
    uses GAP before the final FC layer, so the dimensions going into FC 
    will always be 1x512. HOWEVER, if you are using a network that does 
    not downsample to a fixed dimension in the final pooling layer, then 
    you will need to edit a new dataloader that resizes your images.
    """
    def perform_transforms(self, imgs_list):
        aer = imgs_list[0]

        # Normalize Aerial
        aer = xform_aer_pretrained(aer, self.band_means[0], self.band_stds[0])
        return aer
    
class AerialPT3BandsDataset(MultiModalDataset):
    """Loader that loads only RGB aerial data by itself. Only for use with
    networks that have been pretrained and take 3 bands as input.
    """
    def perform_transforms(self, imgs_list):
        aer = imgs_list[0]
        aer = aer[1:] # chop off the NIR band so we have RGB
        # Normalize Aerial
        aer = xform_aer_pretrained(aer, self.band_means[0], self.band_stds[0])
        return aer
    
    def assert_images_correct(self, image):
        assert image.shape[0] == 3, "Aerial has wrong number of bands."
    
class Aerial3BandsScratch(AerialPT3BandsDataset):
    """Loader that loads only RGB bands of the aerial data. Only for use with
    networks that will be trained from scratch.
    """
    def perform_transforms(self, imgs_list):
        aer = imgs_list[0]
        aer = aer[1:] # chop off the NIR band so we have RGB
        # Normalize Aerial
        aer = xform_aer_3bands_scratch(aer, self.band_means[0], self.band_stds[0])
        return aer
    
######################################################################
###################### Loaders for only S2 data ######################
######################################################################

class S2Dataset(MultiModalDataset):
    """Loader that loads only S2 data by itself."""
    def perform_transforms(self, imgs_list):
        s2 = imgs_list[0]
        # Normalize s2
        s2 = xform_s2(s2, self.band_means[0], self.band_stds[0])
        return s2
    
    def assert_images_correct(self, image):
        assert image.shape[0] == 12, "Sentinel-2 has wrong number of bands."
    
######################################################################
###################### Loaders for only S1 data ######################
######################################################################

class S1Dataset(MultiModalDataset):
    """Loader that loads only S1 data by itself."""
    def perform_transforms(self, imgs_list):
        s1 = imgs_list[0]
        s1 = xform_s1(s1, self.band_means[0], self.band_stds[0])
        return s1
    
    def assert_images_correct(self, image):
        assert image.shape[0] == 3, "Sentinel-1 has wrong number of bands."
    
######################################################################
################ Loaders for Aerial with S2 data fusion ##############
######################################################################

class S2Aerial(MultiModalDataset):
    """Used for early fusion of s2 and aerial. 
    
    NOTE
    ----
    Only works if the S2 is upsampled to the same resolution as the aerial 
    imagery beforehand.
    """
    
    def perform_transforms(self, imgs_list):
        aer = imgs_list[0]
        s2 = imgs_list[1]
        
        # Normalize Aerial
        aer = xform_aer_scratch(aer, self.band_means[0], self.band_stds[0])
        
        # Normalize S2
        s2 = xform_s2(s2, self.band_means[1], self.band_stds[1])

        return [aer, s2]
        
    def augment(self, image):
        """Performs augmentation on one or more image modalities."""
        imgs = self.augmenter(image)
        # for early fusion we need to concatenate the images together
        return torch.cat(imgs, dim = 0)
    
    def assert_images_correct(self, image):
        m="Concatenation of Sentinel-2 and aerial has wrong number of bands."
        assert image.shape[0] == 12+4, m
    
        
class S2AerialMiddleLate(S2Aerial):
    """Used for loading middle and late fusion of aerial and S2.
    Images can be DIFFERENT sizes in this one.
    """
    
    def augment(self, image):
        return self.augmenter(image) # should output list w/ len=2
    
    def assert_images_correct(self, image):
        
        assert image[0].shape[0] == 4, "Aerial has wrong number of bands."
        assert image[1].shape[0] == 12, "Sentinel-2 has wrong number of bands."

class S2AerialPT3Band(S2AerialMiddleLate):
    """Used for loading middle and late fusion of aerial and S2.
    Aerial only uses RGB and is to be fed into a pretrained ResNet.
    """
    
    def perform_transforms(self, imgs_list):
        aer = imgs_list[0][1:] # take RGB
        s2 = imgs_list[1]
        
        # Normalize Aerial
        aer = xform_aer_pretrained(aer, self.band_means[0], self.band_stds[0])
        
        # Normalize S2
        s2 = xform_s2(s2, self.band_means[1], self.band_stds[1])

        return [aer, s2]
    
    def assert_images_correct(self, image):
        
        assert image[0].shape[0] == 3, "Aerial has wrong number of bands."
        assert image[1].shape[0] == 12, "Sentinel-2 has wrong number of bands."

    
class S2DatasetTransformer(S2Aerial):
    """Used for loading aerial and S2 where aerial uses Resnet and S2
    uses a Transformer. Assumes ResNet trained from scratch and thus 
    applies TreeSat means/std during normalization.
    """
    
    def augment(self, image):
        imgs = self.augmenter(image)
        aer = imgs[0]
        # need to create a tiled image out of the S2 bands so we can 
        # use it in the transformer such that each band becomes an input token
        s2 = convert_s2_xformer(imgs[1])
        
        return [aer, s2]
        
    def assert_images_correct(self, image):

        assert image[0].shape[0] == 4, "Aerial has wrong number of bands."
        assert image[1].shape[0] == 1, "Error applying convert_s2_xformer function"
        
class S2TransformerAerPT(S2DatasetTransformer):
    """Used for loading aerial and S2 where aerial uses Resnet and S2
    uses a Transformer. Assumes ResNet pre-trained and thus applies 
    ImageNet means/std during normalization. Assumes that aerial has 4 bands.
    """
    def perform_transforms(self, imgs_list):
        aer = imgs_list[0]
        s2 = imgs_list[1]
        
        # Normalize Aerial
        aer = xform_aer_pretrained(aer, self.band_means[0], self.band_stds[0])
        
        # Normalize S2
        s2 = xform_s2(s2, self.band_means[1], self.band_stds[1])

        return [aer, s2]
    
    
class S2TransformerAerPT3Bands(S2DatasetTransformer):
    """Uses a ResNet pretrained on ImageNet for the aerial. Only uses
    3 RGB bands of aerial. S2 is pre-processed for use in a transformer.
    """
    def perform_transforms(self, imgs_list):
        aer = imgs_list[0]
        aer = aer[1:,:,:]# take RGB
        s2 = imgs_list[1]
        
        # Normalize Aerial
        aer = xform_aer_pretrained(aer, self.band_means[0], self.band_stds[0])
        
        # Normalize S2
        s2 = xform_s2(s2, self.band_means[1], self.band_stds[1])
        
        return [aer, s2]
    
    def assert_images_correct(self, image):

        assert image[0].shape[0] == 3, "Aerial has wrong number of bands."
        assert image[1].shape[0] == 1, "Error applying convert_s2_xformer function"
    
######################################################################
############### Loaders for Aerial with S1 data fusion ###############
######################################################################
    
class S1AerialPT3Band(S2AerialMiddleLate):
    """Used for loading middle and late fusion of aerial and S1.
    Aerial only uses RGB and is to be fed into a pretrained ResNet.
    """
    
    def perform_transforms(self, imgs_list):
        aer = imgs_list[0][1:] # take RGB
        s1 = imgs_list[1]
        
        # Normalize Aerial
        aer = xform_aer_pretrained(aer, self.band_means[0], self.band_stds[0])
        
        # Normalize S2
        s1 = xform_s1(s1, self.band_means[1], self.band_stds[1])

        return [aer, s1]
    
    def assert_images_correct(self, image):
        assert image[0].shape[0] == 3, "Wrong number of bands in aerial"
        assert image[1].shape[0] == 3, "Wrong number of bands in s1"


class S1TransformerAerPT3Bands(S2TransformerAerPT):
    def perform_transforms(self, imgs_list):
        aer = imgs_list[0][1:,:,:]# take RGB
        s1 = imgs_list[1]
        
        # Normalize Aerial
        aer = xform_aer_pretrained(aer, self.band_means[0], self.band_stds[0])
        
        # Normalize S2
        s1 = xform_s1(s1, self.band_means[1], self.band_stds[1])

        return [aer, s1]
    
    def augment(self, image):
        imgs = self.augmenter(image)
        aer = imgs[0]
        # need to create a tiled image out of the S1 bands so we can 
        # use it in the transformer such that each band becomes an input token
        s1 = convert_s1_xformer(imgs[1])
        
        return [aer, s1]
    
    def assert_images_correct(self, image):

        assert image[0].shape[0] == 3, "Aerial has wrong number of bands"
        assert image[1].shape[0] == 1, "Error applying convert_s1_xformer"

    
######################################################################
############# Loaders for Aerial with S2 + S1 data fusion ############
######################################################################
    
class S2S1Aerial(MultiModalDataset):
    """Generic dataloader for loading Aerial, S2 and S1 data together.
    Assumes we train Resnet from scratch and thus applies normalization
    using TreeSat mean/std. This means using a normalization function
    which does not use ToTensor from pytorch before applying mean/std norm
    because our mean/std values for TreeSat are calculated on the original
    image values.
    """
    def perform_transforms(self, imgs_list):
        aer = imgs_list[0]
        s2 = imgs_list[1]
        s1 = imgs_list[2]

        # normalize aerial
        aer = xform_aer_scratch(aer, self.band_means[0], self.band_stds[0])
        
        # Normalize S2
        s2 = xform_s2(s2, self.band_means[1], self.band_stds[1])
        
        #normalize S1
        s1 = xform_s1(s1, self.band_means[2], self.band_stds[2])
        
        return [aer, s2, s1]
    
    def augment(self, image):
        """Performs augmentation on one or more image modalities."""
        return self.augmenter(image) # returns list of len=3
    
    def assert_images_correct(self, image):

        assert image[0].shape[0] == 4, "Aerial has wrong number of bands"
        assert image[1].shape[0] == 12, "S2 has wrong number of bands"
        assert image[2].shape[0] == 3, "S1 has wrong number of bands"

    
class S2S1AerialPT(S2S1Aerial):
    """Generic dataloader for loading Aerial, S2 and S1 data together.
    Assumes that Resnet is pretrained and thus applies normalization
    using ImageNet mean/std. Assumes aerial has 4 bands.
    """
    def perform_transforms(self, imgs_list):
        aer = imgs_list[0]
        s2 = imgs_list[1]
        s1 = imgs_list[2]

        # normalize aerial
        aer = xform_aer_pretrained(aer, self.band_means[0], self.band_stds[0])
        
        # Normalize S2
        s2 = xform_s2(s2, self.band_means[1], self.band_stds[1])
        
        #normalize S1
        s1 = xform_s1(s1, self.band_means[2], self.band_stds[2])
        
        return [aer, s2, s1]

class S2S1AerialPT3Band(S2S1AerialPT):
    """Used for middle/late fusion. Aerial has 3 bands and uses imagenet
    normalization.
    """
    def perform_transforms(self, imgs_list):
        aer = imgs_list[0][1:] # RGB
        s2 = imgs_list[1]
        s1 = imgs_list[2]

        # normalize aerial
        aer = xform_aer_pretrained(aer, self.band_means[0], self.band_stds[0])
        
        # Normalize S2
        s2 = xform_s2(s2, self.band_means[1], self.band_stds[1])
        
        #normalize S1
        s1 = xform_s1(s1, self.band_means[2], self.band_stds[2])
        
        return [aer, s2, s1]
    
    def assert_images_correct(self, image):

        assert image[0].shape[0] == 3, "Aerial has wrong number of bands"
        assert image[1].shape[0] == 12, "S2 has wrong number of bands"
        assert image[2].shape[0] == 3, "S1 has wrong number of bands"

    
class S2S1AerialTransformer(S2S1Aerial):
    """Used for late fusion where we use Resnet for aerial and a single xformer 
    for both Sentinel 1 and 2. Thus, S2 and S1 are essentially fused early and then
    late fused with the aerial.
    Here ResNet is trained from scratch so we normalize using TreeSat mean/std.
    """
    
    def augment(self, image):
        aer, s2, s1 =  self.augmenter(image)
        s2_1 = convert_s2_s1_xformer(s2, s1, 4, 3)
        
        return [aer, s2_1]
    
    def assert_images_correct(self, image):

        assert image[0].shape[0] == 4, "Aerial has wrong number of bands"
        assert image[1].shape[0] == 1, "Error applying convert_s2_s1_xformer"

    
class S2S1AerialPTTransformer(S2S1AerialPT):
    """Used for late fusion where we use Resnet for aerial and a single xformer 
    for both Sentinel 1 and 2. Thus, S2 and S1 are essentially fused early and
    fed together through a transformer and then later fused with the aerial.
    Here ResNet is pre-trained so we normalize using ImageNet mean/std.
    """
    def augment(self, image):
        aer, s2, s1 =  self.augmenter(image)
        s2_1 = convert_s2_s1_xformer(s2, s1, 4, 3)
        
        return [aer, s2_1]
    
    def assert_images_correct(self, image):

        assert image[0].shape[0] == 4, "Aerial has wrong number of bands"
        assert image[1].shape[0] == 1, "Error applying convert_s2_s1_xformer"

class S2S1AerialPT3BandTransformer(S2S1AerialPT3Band):
    """Used for late fusion where we use Resnet for aerial and a single xformer 
    for both Sentinel 1 and 2. Thus, S2 and S1 are essentially fused early and
    fed together through a transformer and then later fused with the aerial.
    Here ResNet is pre-trained so we normalize using ImageNet mean/std.
    """
    def augment(self, image):
        aer, s2, s1 =  self.augmenter(image)
        s2_1 = convert_s2_s1_xformer(s2, s1, 4, 3)
        
        return [aer, s2_1]
    
    def assert_images_correct(self, image):

        assert image[0].shape[0] == 3, "Aerial has wrong number of bands"
        assert image[1].shape[0] == 1, "Error applying convert_s2_s1_xformer"
        
######################################################################
####################### Builder functions ############################
######################################################################

def create_aerial(config, base_args, split_file):
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['img_folder']]
    base_args['band_means'] = [config['band_means']]
    base_args['band_stds'] = [config['band_stds']]
        
    return AerialDataset(**base_args)

def create_aerial_pretrained(config, base_args, split_file):
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['img_folder']]
    base_args['band_means'] = [config['band_means']]
    base_args['band_stds'] = [config['band_stds']]
        
    return AerialPTDataset(**base_args)

def create_s2(config, base_args, split_file):
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['img_folder']]
    base_args['band_means'] = [config['band_means']]
    base_args['band_stds'] = [config['band_stds']]
        
    return S2Dataset(**base_args)

def create_s1(config, base_args, split_file):
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['img_folder']]
    base_args['band_means'] = [config['band_means']]
    base_args['band_stds'] = [config['band_stds']]
        
    return S1Dataset(**base_args)

def create_early(config, base_args, split_file):
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['aer_folder'], config['s2_folder']]
    base_args['band_means'] = [config['aer_band_means'], config['s2_band_means']]
    base_args['band_stds'] = [config['aer_band_stds'], config['s2_band_stds']]
        
    return S2Aerial(**base_args)

def create_middlef(config, base_args, split_file):
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['aer_folder'], config['s2_folder']]
    base_args['band_means'] = [config['aer_band_means'], config['s2_band_means']]
    base_args['band_stds'] = [config['aer_band_stds'], config['s2_band_stds']]
        
    return S2AerialMiddleLate(**base_args)

def create_all_modes_middle_late(config, base_args, split_file):
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['aer_folder'], config['s2_folder'], config['s1_folder']]
    base_args['band_means'] = [config['aer_band_means'], config['s2_band_means'], config['s1_band_means']]
    base_args['band_stds'] = [config['aer_band_stds'], config['s2_band_stds'], config['s1_band_stds']]
        
    return S2S1Aerial(**base_args)

def create_s2_aer_pt_3band(config, base_args, split_file):
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['aer_folder'], config['s2_folder']]
    base_args['band_means'] = [config['aer_band_means'], config['s2_band_means']]
    base_args['band_stds'] = [config['aer_band_stds'], config['s2_band_stds']]
    
    return S2AerialPT3Band(**base_args)

def create_s1_aer_pt_3band(config, base_args, split_file):
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['aer_folder'], config['s1_folder']]
    base_args['band_means'] = [config['aer_band_means'], config['s1_band_means']]
    base_args['band_stds'] = [config['aer_band_stds'], config['s1_band_stds']]
    
    return S1AerialPT3Band(**base_args)

def create_s1_xformer_aer3band_pt(config, base_args, split_file):
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['aer_folder'], config['s1_folder']]
    base_args['band_means'] = [config['aer_band_means'], config['s1_band_means']]
    base_args['band_stds'] = [config['aer_band_stds'], config['s1_band_stds']]
    
    return S1TransformerAerPT3Bands(**base_args)

def create_s2_xformer(config, base_args, split_file):
    """Dataloader designed for use with the ResnetAndTransformer model where
    the Resnet is trained from scratch."""
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['aer_folder'], config['s2_folder']]
    base_args['band_means'] = [config['aer_band_means'], config['s2_band_means']]
    base_args['band_stds'] = [config['aer_band_stds'], config['s2_band_stds']]
    
    return S2DatasetTransformer(**base_args)

def create_s2_xformer_aer_pt(config, base_args, split_file):
    """Dataloader designed for use with the ResnetAndTransformer model where
    the Resnet is pretrained.
    """
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['aer_folder'], config['s2_folder']]
    base_args['band_means'] = [config['aer_band_means'], config['s2_band_means']]
    base_args['band_stds'] = [config['aer_band_stds'], config['s2_band_stds']]

    return S2TransformerAerPT(**base_args)

def create_s2_xformer_aer3band_pt(config, base_args, split_file):
    """Dataloader designed for use with the ResnetAndTransformer model where
    the Resnet is pretrained and has only 3 bands.
    """
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['aer_folder'], config['s2_folder']]
    base_args['band_means'] = [config['aer_band_means'], config['s2_band_means']]
    base_args['band_stds'] = [config['aer_band_stds'], config['s2_band_stds']]
    
    return S2TransformerAerPT3Bands(**base_args)

def create_s1_s2_aer_xform(config, base_args, split_file):
    """Dataloader designed for use with the ResnetAndTransformer model where
    the Resnet is trained from scratch."""
    
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['aer_folder'], config['s2_folder'], config['s1_folder']]
    base_args['band_means'] = [config['aer_band_means'], config['s2_band_means'], config['s1_band_means']]
    base_args['band_stds'] = [config['aer_band_stds'], config['s2_band_stds'], config['s1_band_stds']]

    return S2S1AerialTransformer(**base_args)

def create_s1_s2_aerpretrained_xform(config, base_args, split_file):
    """Dataloader designed for use with the ResnetAndTransformer model where
    the Resnet is pretrained on ImageNet with one channel duplicated.
    """
    
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['aer_folder'], config['s2_folder'], config['s1_folder']]
    base_args['band_means'] = [config['aer_band_means'], config['s2_band_means'], config['s1_band_means']]
    base_args['band_stds'] = [config['aer_band_stds'], config['s2_band_stds'], config['s1_band_stds']]
    
    return S2S1AerialPTTransformer(**base_args)

def create_s1_s2_aerpretrained3band_xform(config, base_args, split_file):
    """Dataloader designed for use with the ResnetAndTransformer model where
    the Resnet is pretrained on ImageNet using only RGB.
    """
    
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['aer_folder'], config['s2_folder'], config['s1_folder']]
    base_args['band_means'] = [config['aer_band_means'], config['s2_band_means'], config['s1_band_means']]
    base_args['band_stds'] = [config['aer_band_stds'], config['s2_band_stds'], config['s1_band_stds']]
    
    return S2S1AerialPT3BandTransformer(**base_args)

def create_s1_s2_aer_pt_3band(config, base_args, split_file):
    """Dataloader designed for use with the ResnetAndTwoTransformers model"""
    
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['aer_folder'], config['s2_folder'], config['s1_folder']]
    base_args['band_means'] = [config['aer_band_means'], config['s2_band_means'], config['s1_band_means']]
    base_args['band_stds'] = [config['aer_band_stds'], config['s2_band_stds'], config['s1_band_stds']]

    return S2S1AerialPT3Band(**base_args)

def create_aerial_pt_4bands(config, base_args, split_file):
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['img_folder']]
    base_args['band_means'] = [config['band_means']]
    base_args['band_stds'] = [config['band_stds']]
    
    return AerialPTDataset(**base_args)
    
    
def create_aerial_3bands_scratch(config, base_args, split_file):
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['img_folder']]
    base_args['band_means'] = [config['band_means']]
    base_args['band_stds'] = [config['band_stds']]

    return Aerial3BandsScratch(**base_args)

def create_aerial_3bands_pt(config, base_args, split_file):
    base_args['split_file'] = split_file
    base_args['json_file'] = config['json_file']
    base_args['img_folders'] = [config['img_folder']]
    base_args['band_means'] = [config['band_means']]
    base_args['band_stds'] = [config['band_stds']]

    return AerialPT3BandsDataset(**base_args)

######################################################################
############################# Factory ################################
######################################################################

def get_dataloader(config, base_args, phase):

    # select the function to create the desired dataloader
    loader_dict = {'AerialDataset': create_aerial,
                   'S2Dataset': create_s2,
                   'S1Dataset': create_s1,
                   'Multimodal': create_early,
                   'MiddleFusion': create_middlef,
                   'AllMiddle': create_all_modes_middle_late,
                   'S2AerialPT3Band': create_s2_aer_pt_3band, # sentinel loaded as cx6x6
                   "S1AerialPT3Band": create_s1_aer_pt_3band, # sentinel loaded as cx6x6
                   'S1XformerAerPT3Band': create_s1_xformer_aer3band_pt,
                   'S2Xformer': create_s2_xformer,
                   'S2XformerAerPT': create_s2_xformer_aer_pt,
                   'S2XformerAer3BandPT': create_s2_xformer_aer3band_pt,
                   'S1S2AerialXformerMidLate': create_s1_s2_aer_xform,
                   'S1S2AerialXformerResnetPretrained': create_s1_s2_aerpretrained_xform,
                   'S2S1AerialPT3BandTransformer': create_s1_s2_aerpretrained3band_xform,
                   'S2S1AerialPT3Band': create_s1_s2_aer_pt_3band, # sentinel 6x6, aer 3 band pretr.
                   'AerialPretrained4BandsDataset': create_aerial_pt_4bands,
                   'Aerial3BandsScratch': create_aerial_3bands_scratch,
                   'AerialPT3BandsDataset': create_aerial_3bands_pt
                  }
    loader = config['loader']
    
    # LOAD THE SPLIT
    if phase == "train":
        split_file = config["files_list_train"]
    elif phase == "val":
        split_file = config["files_list_val"]
    elif phase == "test":
        split_file = config["files_list_test"]
    
    # create the dataloader
    dataloader = loader_dict[loader](config, base_args, split_file)
    
    return dataloader