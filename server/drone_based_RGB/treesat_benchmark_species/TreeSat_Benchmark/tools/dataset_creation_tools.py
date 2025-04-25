'''Functions designed to help the user determine their own subsets of the dataset
'''
import numpy as np

def filter_areas(entry, thr = 0.07):
    """Returns only labels (and their respective areas) which are above a 
    certain threshold of area.
    """
    areas = np.array(entry['areas'])
    lbls = entry['labels']
    idx = np.where(areas > thr)[0]
    areas = areas.tolist()
    areas = [areas[i] for i in idx]
    lbls = [lbls[i] for i in idx]
    
    return lbls, areas


def group_common_classes(meta):
    """Groups polygon labels and areas from a patch that belong to the
    same class.
    """
    labels = meta['label_banr']
    areas = meta['areas']
    unique = np.unique(labels)
    print(f"labels:{labels}")
    idx = [get_index_positions(labels, l) for l in unique]
    
    return create_new_labels(areas, labels, unique, idx)


def create_new_labels(areas, labels, unique, idx):
    """Takes a set of possibly duplicated labels and creates new
    labels and areas by grouping unique classes.
    """
    # make new labels
    new_labels = []
    new_area = []
    
    # sum up the areas
    for j, c in enumerate(unique):
        new_labels.append(c)
        area = np.sum([areas[i] for i in idx[j]])
        new_area.append(area)
        
    return new_labels, new_area

def get_index_positions(list_of_elems, element):
    ''' Returns the indexes of all occurrences of give element in
    the list_of_elems
    '''
    index_pos_list = []
    for i in range(len(list_of_elems)):
        if list_of_elems[i] == element:
            index_pos_list.append(i)
    return index_pos_list


def query_status(js, status, priority, debug = False):
    """Gets all filename and class labels for all patches that match
    the given status and priority levels.
    
    Parameters
    ----------
    js : dictionary
        Dictionary containing metadata for each image patch.
    status : list
        List containing the different statuses that we want to query for.
    priority : list
        List of priority levels we want to allow. 
        0 = the patch is covered by only a single polygon and that polygon is pure
        1 = the patch is covered by more than 1 polygon but all polygons are pure
        2 = the patch is covered by 1 or more polygons which are mixed
        3 = the patch is covered by 1 or more polygons, but the banr and bt labels
        do not match, making it very unclear which labels are correct.
    """
    if not isinstance(status, list):
        m = "'status' must be a list"
        raise AssertionError(m)
    if not isinstance(priority, list):
        m = "'priority' must be a list"
        raise AssertionError(m)
        
    retrieved = {}
    meta = js['metadata']
    for file in meta:
        if file['status'] in status and file['priority'] in priority:
            if debug:
                print(file)
                print()
                
            if len(file['label_banr']) == 1:
                lbls = file['label_banr']
                area = file['areas']
            else:
                lbls, area = group_common_classes(file)
                
            retrieved[file['file']] = {"labels":lbls,"areas":area} 
    
    return retrieved