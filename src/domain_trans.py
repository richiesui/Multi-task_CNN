import tensorflow as tf
import numpy as np
from data_loader_direct import DataLoader
from my_losses import *
from model import *
import time
import math
import os
import cv2
from estimator_rui import estimator_rui

class domain_trans:
    '''
    A wrapper function which create data, model and loss according to input type
    '''
    def __init__(self,trainer):
        self.trainer = trainer

    
    def forward_wrapper(self,domain_transfer_dir,scope_name,output_src):
        '''
        A wrapper function for domain transfer.
        Generate dataloader, model, loss and its own summary
        '''

        weight_gen = 5000
        weight_disc = 1000

        _, output_dom, data_dict_dom = self.trainer.forward_wrapper(domain_transfer_dir,scope_name,is_training=True,is_reuse=True,with_loss=False,test_input=True)

        #=========================
        #GAN for domain adaptation
        #=========================

        with tf.variable_scope("disc_model") as scope:
            disc_real = discriminator(output_src[1],num_encode=4)
            disc_fake = discriminator(output_dom[1],num_encode=4,is_training=True, is_reuse=True)

        import pdb;pdb.set_trace()

        #Consturct loss
        gen_loss = -tf.reduce_mean(tf.log(disc_fake))
        disc_loss = -tf.reduce_mean(tf.log(disc_real) + tf.log(1. - disc_fake))

        #Construct discriminator
        optim_adv = tf.train.AdamOptimizer(self.trainer.opt.learning_rate2, self.trainer.opt.beta1)
        train_adv = slim.learning.create_train_op(disc_loss, optim_adv, variables_to_train=tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, 'disc_model'))

        #Construct summaries
        tf.summary.image('domain/image' , \
                            data_dict_dom['image'])
        pred_landmark_dom = self.trainer.parse_output_landmark(output_dom)
        pred_landmark_dom = tf.expand_dims(tf.reduce_sum(pred_landmark_dom,3),axis=3)
        tf.summary.image('domain_lm_img' , \
                            pred_landmark_dom)
        tf.summary.scalar('losses/gen_loss', gen_loss)
        tf.summary.scalar('losses/disc_loss', disc_loss)
        
        return gen_loss,disc_loss,train_adv