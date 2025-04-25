from pathlib import Path
import numpy as np
import rasterio
import torch

def filter_target_files(targets, full_list):
    """Filters a list of file names and returns only those
    present in the 'targets'.
    
    Parameters:
    -----------
    targets : list
        List of the names which are to be kept from the full_list.
    full_list : list
        List to be filtered.
    """
    if isinstance(targets, str):
        rasterData = [img for img in full_list if targets in Path(img).stem]
    elif isinstance(targets, list):
        rasterData = [img for img in full_list if Path(img).stem in targets]
    
    return rasterData

def subset_dict_by_filename(files_to_subset, dictionary):
    missing_files = [file for file in files_to_subset if file not in dictionary]
    if missing_files:
        print(f"Total missing files: {len(missing_files)}")
        print(f"Missing files in dictionary: {missing_files}")
    return {file : dictionary[file] for file in files_to_subset if file in dictionary}

def filter_labels_by_threshold(labels_dict, area_threshold = 0.07):
    """
    Parameters
    ----------
    labels_dict: dict, {filename1: [(label, area)],
                        filename2: [(label, area), (label, area)],
                        ...
                        filenameN: [(label, area), (label, area)]}
    area_threshold: float
    
    Returns
    -------
    filtered: dict, {filename1: [label],
                     filename2: [label, label],
                     ...
                     filenameN: [label, label]}
    """
    filtered = {}
    
    for img in labels_dict:
        for lbl, area in labels_dict[img]:
            # if area greater than threshold we keep the label
            if area > area_threshold and lbl not in ["Tilia", "Populus", "Prunus"]:
                # init the list of labels for the image
                if img not in filtered:
                    filtered[img] = []
                # add only the label, since we won't use area information further
                filtered[img].append(lbl)
                
    return filtered
                

def convert_one_hot(classes, labels):
    """Converts a list of class indexes to a one-hot
    encoded vector.
    
    Examples:
    ---------
    >>> all_classes = ['grass', 'tree', 'road', 'cloud']
    >>> image_labels = [1, 3]
    >>> print(convert_one_hot(all_classes, image_labels))
    [0, 1, 0, 3]
    
    """
    # # get the one hot encoding vector for the target labels
    # one_hot = torch.zeros(len(classes), dtype = torch.float32)
    # for lab in labels:
    #     # get index from original class list
    #     idx = classes.index(lab)
    #     one_hot[idx] = 1
    # return one_hot

    remove_indices = [-1, -4, -5]
    # print(f"classes: {classes}")
    
    # updated_classes = [cls for i, cls in enumerate(classes) if i not in remove_indices]
    # print(f"updated_classes: {updated_classes}")
    # # Filter labels to exclude the removed classes
    updated_labels = [cls for cls in labels if cls in classes]
    # print(f"updated_labels: {updated_labels}")
    # Initialize one-hot vector for updated classes
    one_hot = torch.zeros(len(classes), dtype=torch.float32)
    
    for lab in updated_labels:
        # Get the new index of the class in the updated list
        idx = classes.index(lab)
        one_hot[idx] = 1
    # print(one_hot)
    return one_hot

def convert_sec_style(classes, labels):

    # get the one hot encoding vector for the target labels
    one_hot = np.zeros((1, 1, len(classes)))
    for lab in labels:
        # get index from original class list
        idx = classes.index(lab)
        one_hot[0,0, idx] = 1.

    return one_hot

def load_image_and_label(img_path, labels, classes, dtype = np.float32):
    '''
    Parameters
    ----------
    img_path : str
        Full path to an image.
    labels: json
        A JSON formatted dictionary mapping image names to labels.
    '''
    # load image file
    with rasterio.open(img_path) as f:
        img = f.read()

    # Take the filename from the file path
    filen = Path(img_path).name
    
    # get the label
    label = labels[filen]
    # print(label)
    
    if len(label) == 0:
        raise AssertionError('No valid label for %s' % filen)
        
    one_hot = convert_one_hot(classes, label)
    
    return img.astype(dtype), one_hot

def convert_s2_s1_xformer(s2, s1, n_height=4, n_width=3):
    """Takes the bands of small sentinel 2 patches (6x6) and stitches them together into
    a grid. Thus, it creates something like an image with 1 band. This is done so that
    when the xformer takes the image as input and splits the image into patches to be
    used as tokens, each band in the original Sentinel image will become a token.
    
    b = 6x6 band
    
     - - - 
    |b b b|
    |b b b|
    |b b b|
    |b b b|
     - - -
    """
    img_size = s2.shape[1]
    
    # just take 9 channels so we have a symmetrical image in the end when we add the 3 S1 bands
    # here we are leaving bands 8A, 1, 9, and 10 out
    s2 = torch.cat([s2[:7], s2[8:10]])
    
    # create the out array
    out = torch.zeros((1, img_size*n_height, img_size*n_width))
    
    # add the S2
    col = 0
    row = 0
    for i, band in enumerate(range(s2.shape[0])):

        if i % 3 == 0 and i != 0:
            #reset col index and increment row index
            col = 0
            row += 6

        out[0, row:row+6, col:col+6] = s2[band]
        col += 6
    
    # add the S1
    col = 0
    row += 6
    for band in range(s1.shape[0]):
        out[0, row:row+6, col:col+6] = s1[band]
        col += 6
    
    return out

def convert_s2_xformer(s2, n_height=3, n_width=3):
    """See convert_s2_s1_xformer above for description.
    
     - - - 
    |b b b|
    |b b b|
    |b b b|
     - - -
    """
    img_size = s2.shape[1]
    
    # just take 9 channels so we have a symmetrical image in the end
    # here we are leaving bands 8A, 1, 9, and 10 out
    s2 = torch.cat([s2[:7], s2[8:10]])
    out = torch.zeros((1, img_size*n_height, img_size*n_width))
    print("O", out.shape)
    col = 0
    row = 0
    for i, band in enumerate(range(s2.shape[0])):

        if i % 3 == 0 and i != 0:
            #reset col index and increment row index
            col = 0
            row += 6

        out[0, row:row+6, col:col+6] = s2[band]
        col += 6
        
    return out

def convert_s1_xformer(s1, n_height=1, n_width=3):
    """See convert_s2_s1_xformer above for description.

     - - - 
    |b b b|
     - - -
    """
    img_size = s1.shape[1]
    
    out = torch.zeros((1, img_size*n_height, img_size*n_width))
    
    col = 0
    row = 0
    for i, band in enumerate(range(s1.shape[0])):

        out[0, row:row+6, col:col+6] = s1[band]
        col += 6
        
    return out

def get_class_weights(config):
    class_weights = config['class_imbal_weights']
    total = np.sum(class_weights)
    weights = torch.tensor(np.array(class_weights) / total)
    weights = 1.0 / weights
    class_weights = weights / weights.sum()
    
    return class_weights

def set_up_unfrozen_weights(model):
    # if we are fine tuning we select the parameters we unfreeze
    params_to_update = []
    # model should already have set the weights that will stay frozen
    # so we just need to loop and find the ones that require_grad
    for name, param in model.named_parameters():
        if param.requires_grad == True:
            params_to_update.append(param)
            
    return params_to_update