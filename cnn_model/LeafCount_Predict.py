"""
make predictions on new testing images using trained model
"""
import numpy as np
from pathlib import Path
import deepplantphenomics as dpp
import os

class CornLeafRegressor(object):
    model = None
    img_height = 256
    img_width = 256

    def __init__(self, model_dir, batch_size=2):
        """A network which predicts rosette leaf count via a convolutional neural net"""
        
        self.__dir_name = os.path.join(model_dir)
        self.model = dpp.DPPModel(debug=False, load_from_saved=self.__dir_name)
        # Define model hyperparameters
        self.model.set_batch_size(batch_size)
        self.model.set_number_of_threads(1)
        self.model.set_image_dimensions(self.img_height, self.img_width, 3)
        self.model.set_resize_images(True)
        self.model.set_problem_type('regression')
        self.model.set_augmentation_crop(True)
        # Define a model architecture
        self.model.add_input_layer()
        self.model.add_convolutional_layer(filter_dimension=[5, 5, 3, 32], stride_length=1, activation_function='tanh')
        self.model.add_pooling_layer(kernel_size=3, stride_length=2)
        self.model.add_convolutional_layer(filter_dimension=[5, 5, 32, 64], stride_length=1, activation_function='tanh')
        self.model.add_pooling_layer(kernel_size=3, stride_length=2)
        self.model.add_convolutional_layer(filter_dimension=[3, 3, 64, 64], stride_length=1, activation_function='tanh')
        self.model.add_pooling_layer(kernel_size=3, stride_length=2)
        self.model.add_convolutional_layer(filter_dimension=[3, 3, 64, 64], stride_length=1, activation_function='tanh')
        self.model.add_pooling_layer(kernel_size=3, stride_length=2)
        self.model.add_output_layer()

    def forward_pass(self, x):
        y = self.model.forward_pass_with_file_inputs(x)
        return y

    def shut_down(self):
        self.model.shut_down()

def predict(model_dir, test_dir, output_fn):
    testdir = os.path.join(test_dir)
    images = [os.path.join(testdir, name) for name in os.listdir(testdir) if
          os.path.isfile(os.path.join(testdir, name)) & name.endswith('.png')]
    net = CornLeafRegressor(model_dir)
    leaf_counts = net.forward_pass(images)
    net.shut_down()

    f1 = open('%s'%output_fn, 'w')
    for k,v in zip(images, leaf_counts):
        f1.write('%s,%f\n'%(k.split('/')[-1], v))
    f1.close()

import sys
if len(sys.argv)==4:
    predict(*sys.argv[1:])
else:
    print('python LeafCount_Predict.py model_dir, testing_dir, output_fn')
