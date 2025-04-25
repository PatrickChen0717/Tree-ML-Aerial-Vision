from .metrics import EpochMetrics
import torch.nn as nn
import numpy as np
import torch
import json
import sys
import os

class ModelTrainer():
    
    def __init__(self, 
                 num_epochs, 
                 classes, 
                 model, 
                 device, 
                 loaders, 
                 criterion, 
                 optimizer, 
                 f_name, 
                 scheduler = None, 
                 weights_path = './data/weights/image_classifier', 
                 save_results = None, 
                 print_cl_met = True, 
                 minimum_lr = 0.0): 
        """ 
        Parameters
        ----------
        model : nn.Module
            Model to train.
        device : str
            Device used to train the model. Either 'cpu' or 'cuda'.
        loaders : dict
            Dictionary containing generator functions used to load data for each batch.
        criterion : function
            A callable loss function.
        optimizer : torch.optim
            Optimizer function.
        epoch : int
            Integer value indicating the current epoch.
        logits : list
            List used to track the logits over the course of model training.
        scheduler : optional, torch.optim.lr_scheduler
            Scheduler function used to modify the learning rate during training.
        """
        
        
        self.results = save_results
        self.print_class_metrics = print_cl_met
        self.w_path = weights_path
        self.epochs = num_epochs
        self.model = model
        self.device = device
        self.loaders = loaders
        self.criterion = criterion
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.file_name = f_name
        self.classes = classes
        self.sig = nn.Sigmoid()
        
        self.sched_name = type(self.scheduler).__name__
        if self.sched_name not in ['StepLR', 'ExponentialLR', 'CyclicLR', 'ReduceLROnPlateau', 'NoneType']:
            m = "Scheduler %s is not currently supported. See 'trainModel' for how the others are implemented so you can add %s appropriately."
            raise TypeError(m % (self.sched_name, self.sched_name))
        
        self.current_epoch = 0
        self.minimum_lr = minimum_lr
        # loss values after each batch
        self.train_loss_per_batch = []
        self.val_loss_per_batch = []
        # loss averaged across the epoch
        self.training_losses = []
        self.val_losses = []
        
        # set tracking lists for metrics
        self.logits_tracker = []
        self.f1_tracker = []
        self.classwise_f1 = []
        self.classwise_r = []
        self.classwise_p = []
        self.classwise_j = []
        self.jaccard_tracker = []
        self.hamming_tracker = []
        self.coverage_tracker = []
        self.lrap_tracker = []
        self.ranking_loss_tracker = []
        self.zero_one_tracker = []
        self.sample_f1_tracker = []
        self.macro_recall_tracker = []
        self.macro_prec_tracker = []
        self.macro_map_tracker = []
        self.micro_map_tracker = []

    @property
    def current_lr(self):
        return self.optimizer.param_groups[0]['lr']
    
    def save_weights(self): 
        print(f"w_path: {self.w_path}") 
        if not os.path.exists(self.w_path):
            print("The path does not exist, creating it.")
            os.makedirs(self.w_path, exist_ok=True)

        if self.f1_tracker[-1] == np.max(np.array(self.f1_tracker)):
            print(self.w_path + '/%s_Boost.pt' % self.file_name)
            torch.save(self.model.state_dict(), 
                       self.w_path + '/%s_Boost.pt' % self.file_name)
            torch.save(self.model.state_dict(), 
                       'weights/%s.pt' % self.file_name)
            print('Saving weights case 1')

        else:
            print(self.w_path + '/%s_NoBoost.pt' % self.file_name)
            torch.save(self.model.state_dict(), 
                       self.w_path + '/%s_NoBoost.pt' % self.file_name)
            torch.save(self.model.state_dict(), 
                       'weights/%s.pt' % self.file_name)
            print('Saving weights case 2')

    def init_epoch(self, i):
        print('*' * 50)
        print('*' * 50)
        print('EPOCH: %d' % int(i+1))
        print('*' * 50)
        print('*' * 50)

        self.epoch_preds_val = []
        self.epoch_labels_val = []
        self.epoch_probabilites = []

    def get_loaded(self, loaded):
        img_batch = loaded[0]
        label_batch = loaded[1]
        # print(f"Processed label_batch shape: {label_batch.shape}")
        lbl_batch = label_batch.to(self.device)
        if isinstance(img_batch, list) and len(img_batch) > 1:
            img_batch = [img.to(self.device).float() for img in img_batch]

        else:
            img_batch = img_batch.to(self.device).float()

        # print(f"Processed lbl_batch shape: {lbl_batch.shape}")

        img_batch = img_batch.to(self.device).float()
        # print(f"Processed img_batch shape: {img_batch.shape}")
        return img_batch, lbl_batch

    def getLoss(self):
        # print(f"Output shape (self.out): {self.out.shape}")
        if isinstance(self.out, list) and len(self.out) > 1:
            self.out = [o.to(self.device) for o in self.out]
        else:
            self.out = self.out.to(self.device)
        # print(f"self.criterion:{self.criterion}")
        return self.criterion(self.out, 
                              self.lbl_batch
                                 )
    
    def getPreds(self):
        if len(self.out) > 1 and isinstance(self.out, list):
            self.pred_out = np.array(self.sig(self.out[0]).cpu() > 0.5, 
                                     dtype=float)
        else:
            self.pred_out = np.array(self.sig(self.out).cpu() > 0.5, 
                                     dtype=float)
            
    def init_phase(self):
        # Turn on or off training mode depending on phase
        self.model.train(True if self.phase == 'training' else False)

        # empty list to track losses in the epoch
        return []
    
    def trainModel(self):
        """Runs a training loop for a single epoch.
        """

        epoch_loss = self.init_phase()

        if self.scheduler is not None:
            print('Current LR: %.5f' % self.current_lr)

        # loop through all batches to perform an epoch
        for loaded in self.loaders[self.phase]:
            epoch_loss = self.train_step(loaded, epoch_loss)
        
        mean_loss = np.mean(np.array(epoch_loss))
        print("*" * 20)
        print('Training loss for epoch %d : ' % int(self.current_epoch + 1), 
              mean_loss)
        print()

        # update scheduler
        if self.sched_name in ['StepLR', 'ExponentialLR']:
            if self.scheduler.get_last_lr()[0] > self.minimum_lr:
                self.scheduler.step()

        self.training_losses.append(mean_loss)

    def train_step(self, loaded, epoch_loss):
        '''Performs a single batch step in a training epoch'''
        
        # get training data
        self.img_batch, self.lbl_batch = self.get_loaded(loaded)
        
        # reset gradients
        self.optimizer.zero_grad()

        # process batch through network
        self.out = self.model(self.img_batch)

        # get loss value
        loss_val = self.getLoss()

        # track loss for the given epoch
        epoch_loss.append(loss_val.item())
        self.train_loss_per_batch.append(loss_val.item())

        # backpropagation
        loss_val.backward()

        # update the parameters
        self.optimizer.step()

        # cyclic updates across batchs
        if self.sched_name in ['CyclicLR']:
            self.scheduler.step()
    
        return epoch_loss
        
    def validateModel(self):
        """Runs a validation loop for a single epoch.
        """
        epoch_loss = self.init_phase()

        # loop through all batches
        with torch.no_grad():

            for loaded in self.loaders[self.phase]:
                epoch_loss = self.valStep(loaded, epoch_loss)
                
            print("*" * 20)
            print('Validation loss for epoch %d : ' % int(self.current_epoch + 1), 
                  np.mean(np.array(epoch_loss)))
            print()

            self.val_losses.append(np.mean(np.array(epoch_loss)))
            
    def valStep(self, loaded, epoch_loss):
        self.img_batch, self.lbl_batch = self.get_loaded(loaded)

        # process batch through network
        self.out = self.model(self.img_batch)

        # threshold the probabilities in order to get the predictions
        self.getPreds()

        # store information needed for metric calcs
        self.store_val_output()

        # calculate loss
        loss_val = self.getLoss()

        # track loss
        epoch_loss.append(loss_val.item())
        self.val_loss_per_batch.append(loss_val.item())
        
        return epoch_loss
        
    def store_val_output(self):
        """Stores information needed for metric calculations."""
        # the lists of epoch_x are re-created during each init_epoch call
        if len(self.out) > 1 and isinstance(self.out, list):
            self.epoch_probabilites.extend(self.out[0].cpu().numpy().tolist())
        else:
            self.epoch_probabilites.extend(self.out.cpu().numpy().tolist())
        self.epoch_labels_val.extend(self.lbl_batch.cpu().numpy().tolist())
        self.epoch_preds_val.extend(self.pred_out.tolist())
    
    def run(self):
        for i in range(self.epochs):
            self.init_epoch(i)

            # switch between training and validation
            for phase in ['training', 'validation']:
                self.phase = phase
                
                # run training for the epoch
                if self.phase == 'training':
                    print('*********TRAINING PHASE*********')
                    self.trainModel()
                # run validation for the epoch
                else:
                    print('*********VALIDATION PHASE*********')
                    self.validateModel()

                # if validating then calc metrics and print+store them
                if self.phase == 'validation':
                    self.store_metrics()
                    
            # check if highest F1 score so far, if so we save the weights
            self.file_name = f"epoch_{i}"
            self.save_weights()
            
            self.current_epoch = int(i+1)
        
        return self.model

    def store_metrics(self):
        # calc all metrics only during validation phase
        metrics_ = EpochMetrics(np.array(self.epoch_labels_val), 
                                np.array(self.epoch_preds_val), 
                                np.array(self.epoch_probabilites),
                                self.classes,
                                self.print_class_metrics)()
        
        # store metrics so we can track them across epochs
        # can also use different metrics to determine when to save
        # weights. Currently using F1 score.
        self.f1_tracker.append(metrics_[0])
        self.classwise_f1.append(metrics_[1])
        self.classwise_r.append(metrics_[2])
        self.classwise_p.append(metrics_[3])
        self.hamming_tracker.append(metrics_[4])
        self.coverage_tracker.append(metrics_[5])
        self.lrap_tracker.append(metrics_[6])
        self.zero_one_tracker.append(metrics_[7])
        self.sample_f1_tracker.append(metrics_[8])
        self.macro_recall_tracker.append(metrics_[9])
        self.macro_prec_tracker.append(metrics_[10])
        self.macro_map_tracker.append(metrics_[11])
        self.micro_map_tracker.append(metrics_[12])