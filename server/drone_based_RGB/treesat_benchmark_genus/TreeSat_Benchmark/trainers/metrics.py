import torch
import numpy as np
import torch.nn as nn
from sklearn.metrics import (precision_score, 
                             recall_score, 
                             f1_score,
                             hamming_loss,
                             coverage_error,
                             label_ranking_loss,
                             label_ranking_average_precision_score,
                             zero_one_loss,
                             f1_score,
                             average_precision_score,
                             mean_squared_error
                             )

class EpochMetrics():
    """
    Calculates the metrics for all predictions/labels in a single epoch.
    
    Parameters
    ----------
    labels : array
        Ground truth labels.
    preds : array
        Array with binary entries determining which classes are predicted.
    probs : array
        The probability scores calculated by either Softmax or Sigmoid.
    classes : array
        Names of the classes being predicted.
    print_classwise : bool
        Whether to print out classwise metrics or not.
    print_sample : bool
        Whether to print metrics using 'sample' averaging.
    print_micro : bool
        Whether to print metrics using 'micro' averaging.
    print_macro : bool
        Whether to print metrics using 'macro' averaging.
    """
    def __init__(self, labels, preds, probs, classes, print_classwise = True,
                 print_sample = False, print_micro = False, print_macro = True,
                 print_weighted = True):
        
        self.classes = classes

        self.labels = labels
        self.preds = preds
        self.probs = probs
        
        self.print_micro = print_micro
        self.print_sample = print_sample
        self.print_macro = print_macro
        self.print_classwise = print_classwise
        self.print_weighted = print_weighted
    
    def sklearn_metrics(self):
        # get the errors from sklearn
        self.hamming = hamming_loss(self.labels, self.preds)
        self.coverage = coverage_error(self.labels, self.probs)
        self.lrap = label_ranking_average_precision_score(self.labels, self.probs)
        self.zero_one = zero_one_loss(self.labels, self.preds)
        # F1
        self.sample_f1 = f1_score(self.labels, self.preds, average='samples', zero_division=0)
        self.macro_f1 = f1_score(self.labels, self.preds, average='macro', zero_division=0) 
        self.weight_f1 = f1_score(self.labels, self.preds, average='weighted', zero_division=0) 
        self.micro_f1 = f1_score(self.labels, self.preds, average='micro', zero_division=0) 
        self.class_f1 = f1_score(self.labels, self.preds, average=None, zero_division=0) 
        # mAP
        self.macro_map = average_precision_score(self.labels, self.probs, average= 'macro')
        self.micro_map = average_precision_score(self.labels, self.probs, average= 'micro')
        self.weight_map = average_precision_score(self.labels, self.probs, average= 'weighted')
        self.samples_map = average_precision_score(self.labels, self.probs, average= 'samples')
        # precision recall
        self.class_precision = precision_score(self.labels, self.preds, average=None, zero_division=0) # per call
        self.class_recall = recall_score(self.labels, self.preds, average=None, zero_division=0)
        self.micro_precision = precision_score(self.labels.flatten(), self.preds.flatten(), zero_division=0)
        self.micro_recall = recall_score(self.labels.flatten(), self.preds.flatten(), zero_division=0)
        self.macro_r = np.mean(self.class_recall)
        self.macro_p = np.mean(self.class_precision)
        self.weight_recall = recall_score(self.labels, self.preds, average="weighted", zero_division=0)
        self.weight_precision = precision_score(self.labels, self.preds, average="weighted", zero_division=0)
        
    
    def verbose(self):
        # option to print the values on screen
        if self.print_classwise:
            for i in range(len(self.classes)):
                print(self.classes[i])
                print('Recall: ', self.class_recall[i])
                print('Precision: ', self.class_precision[i])
                print('F1: ', self.class_f1[i])
                print()
        
        if self.print_macro:
            print('Macro F1:', self.macro_f1)
            print('Macro precision:', self.macro_p)
            print('Macro recall:', self.macro_r)
            print('Macro mAP:', self.macro_map)
            print()
            
        if self.print_weighted:
            print('Weighted F1:', self.weight_f1)
            print('Weighted precision:', self.weight_precision)
            print('Weighted recall:', self.weight_recall)
            print('Weighted mAP:', self.weight_map)
            print()
        
        if self.print_sample:
            print('Sample F1:', self.sample_f1)
            print('Sample mAP:', self.samples_map)
            print()
        
        if self.print_micro:
            print('Micro F1:', self.micro_f1)
            print('Micro precision:', self.micro_precision)
            print('Micro recall:', self.micro_recall)
            print('Micro mAP:', self.micro_map)
            print()
    
    def __call__(self):
        
        self.sklearn_metrics()
        self.verbose()
        
        output = [self.macro_f1, 
                  self.class_f1, 
                  self.class_recall, 
                  self.class_precision, 
                  self.hamming, 
                  self.coverage, 
                  self.lrap, 
                  self.zero_one,
                  self.sample_f1, 
                  self.macro_r,
                  self.macro_p,
                  self.macro_map,
                  self.micro_map
                 ]
    
        return output
   