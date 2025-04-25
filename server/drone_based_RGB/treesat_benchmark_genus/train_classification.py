import sys
import json
import torch
import warnings
import rasterio
import argparse
import numpy as np
import torch.nn as nn
from TreeSat_Benchmark.trainers.metrics import *
from TreeSat_Benchmark.trainers.augmenter import Augmenter
from TreeSat_Benchmark.trainers.dataloaders import get_dataloader
from TreeSat_Benchmark.models import get_classification_model
from TreeSat_Benchmark.trainers.basetrainer import ModelTrainer
from TreeSat_Benchmark.trainers.utils import get_class_weights, set_up_unfrozen_weights

# python3 train_classification.py -m "Resnet" -v "cuda:0" -s "my_test_model" -c "configs/aer_only/aerial_cyclic_Families_v8_3Bands_no_NIR_Scratch.json" -l "new_training_even.log"
# original: "class_imbal_weights": [1002, 2517, 2598, 2675, 4362, 8482, 2301, 3706, 8475, 8822, 391, 301, 3406, 9344, 188]
# ibw1 case: "class_imbal_weights": [1002, 2517, 2598, 2675, 4362, 8482, 2301, 2000, 8475, 8822, 1000, 301, 3406, 5000, 1000]
# ibw2 case: "class_imbal_weights": [1002, 2517, 2598, 2675, 4362, 8482, 2301, 1500, 8475, 5822, 2000, 301, 3406, 3500, 1500] aug1
# ibw3 case: "class_imbal_weights": [1002, 4517, 3598, 3675, 4362, 5482, 3301, 1000, 8475, 3822, 2000, 301, 3406, 2500, 1500]
# ibw4 case: "class_imbal_weights": [1002, 6517, 5598, 3675, 4362, 5482, 3301, 1000, 8475, 3822, 3000, 301, 3406, 1500, 1500]
# ibw5 case: "class_imbal_weights": [1002, 6517, 5598, 3675, 4362, 5482, 3301, 300, 8475, 1822, 3000, 301, 3406, 2500, 1500]


def main(ap):
    log = True
    
    # load config file
    with open(ap['config']) as file:
        config = json.load(file)
    
    # define GPU or CPU device
    device = torch.device(ap['device'])

    # get class names
    classes = config['classes']
    
    # define augmentations
    augs = {'hflip': {'prob': 0.5},
            'vflip': {'prob': 0.5},
            'rotate': {'degrees': [90, 90],
                       'prob': 0.5}
    }
    augs = Augmenter(augs)

    # load class imbalance information
    if 'class_imbal_weights' in config:
        class_weights = get_class_weights(config).to(device)
    else: class_weights = None
    
    # dataloader parameters
    params = {'batch_size': config['batch_size'],
              'shuffle': True,
              'num_workers': config['num_workers'],
              'drop_last': config['drop_last']}

    # define the base arguments used by all dataloaders
    base_args = {'classes': classes,
                 'return_name' : False,
                 'target_class' : None,
                 'augmenter' : augs}
    
    # get dataloaders
    training = get_dataloader(config, base_args, "train")
    validation = get_dataloader(config, base_args, "val") 
    
    # create generators
    training_generator = torch.utils.data.DataLoader(training, **params)
    validation_generator = torch.utils.data.DataLoader(validation, **params)
    
    generators = {'training': training_generator,
                  'validation': validation_generator
                  }
    
    # loss function
    criterion = nn.BCEWithLogitsLoss(weight = class_weights)
    
    # select model
    unfreeze = False if 'unfreeze' not in config else True
    model = get_classification_model(ap['model'], classes, config)
    model.to(device)
    params_to_train = model.parameters()
    # for fine tuning we can choose to unfreeze only upper layers
    if unfreeze:
        params_to_train = set_up_unfrozen_weights(model)
    
    print('Using:', device)
    
    # define optimizer
    optimizer = torch.optim.AdamW(params_to_train, lr=config['lr'], betas=(0.9, 0.999), 
                                  eps=1e-08, weight_decay=0.01, amsgrad=False)
    
    # define LR scheduler
    scheduler = torch.optim.lr_scheduler.CyclicLR(optimizer, base_lr=config["base_lr"], 
                                                  max_lr=config['lr'], 
                                                  step_size_up=config["step_size_up"],
                                                  mode="triangular2",
                                                  cycle_momentum=False)
    
    # open log file
    if log:
        old_stdout = sys.stdout
        log_file = open(ap['log_file'], "w")
        sys.stdout = log_file
    
        # print training settings to log
        p_settings(config, ap)
    
    # train the model
    t = ModelTrainer(config['epochs'], 
                     classes, 
                     model, 
                     device, 
                     generators, 
                     criterion, 
                     optimizer, 
                     ap['save_name'], 
                     scheduler, 
                     config['weights_path']
                     )
    model = t.run()
    
    # close the log file
    if log:
        sys.stdout = old_stdout
        log_file.close()
    
def add_arguments():
    ap = argparse.ArgumentParser(prog='Classification Trainer', description='Classification Trainer')
    ap.add_argument('-c', '--config', type=str, required = True,
            help='Give the path to the config file.')
    ap.add_argument('-m', '--model', default='Resnet',
            help='Name of the model to use for training See TreeSat_Benchmark.models.__init__ for all possible options.')
    ap.add_argument('-s', '--save_name',  type=str, required = True,
            help='Name of the output weights file.')
    ap.add_argument('-v', '--device',  type=str, required = True,
            help='Name of the desired device for training (e.g. cpu or cuda:1)')
    ap.add_argument('-l', '--log_file',  type=str, required = True,
            help='full path and file name of the log file storing performance scores across epochs.')
    
    args = vars(ap.parse_args())
    return args

def p_settings(config, ap):
    print("Settings for %s" % ap["save_name"])
    print("-" * 30)
    print("Model: {}".format(config['model']))
    print("Epochs: {}".format(config['epochs']))
    print("Batch size: {}".format(config['batch_size']))
    print("Maximum LR: {}".format(config['lr']))
    print("Base LR: {}".format(config['base_lr']))
    print("Step LR Up: {}".format(config['step_size_up']))
        
    print()
    print("*" * 50)
    print("*" * 50)
    print()

if __name__ == '__main__':
    
    warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning)

    args = add_arguments()
    main(args)