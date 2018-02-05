from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from glob import glob
import numpy as np
import scipy.misc
import matplotlib.pyplot as plt
import matplotlib
import os
import pandas as pd
import h5py
import tqdm
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import gzip
import os
import pdb
import numpy
from scipy import ndimage

from six.moves import urllib

import h5py
import tqdm


import tensorflow as tf
import pdb

DATA_DIRECTORY = "data"

# Params for celeba
IMAGE_SIZE = 28
NUM_CHANNELS = 1
PIXEL_DEPTH = 255
NUM_LABELS = 10
VALIDATION_SIZE = 30  # Size of the validation set.


# Extract train images
def extract_train_data( norm_shift=False, norm_scale=True):
    """Extract the images into a 4D tensor [image index, y, x, channels].
    Values are rescaled from [0, 255] down to [-0.5, 0.5].
    """
    print('Extracting Train data')
    data = glob(os.path.join("TRAIN_DATA", "*.jpg"))
    data = np.sort(data)

    def imread(path):
        return scipy.misc.imread(path).astype(np.float)

    def resize_width(image, width=28.):
        h, w = np.shape(image)[:2]
        return scipy.misc.imresize(image,[int((float(h)/w)*width),width])

    def center_crop(x, height=28):
        h= np.shape(x)[0]
        j = int(round((h - height)/2.))
        return x[j:j+height,:,:]

    def get_image(image_path, width=28, height=28):
        return center_crop(resize_width(imread(image_path), width = width),height=height)

    def rgb2gray(rgb):

        r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b

        return gray

    test = get_image(data[0],IMAGE_SIZE,IMAGE_SIZE)

    images = np.zeros((len(data),IMAGE_SIZE*IMAGE_SIZE), dtype = np.uint8)
    #pdb.set_trace()


    for i in tqdm.tqdm(range(len(data))):
        #for i in tqdm.tqdm(range(10)):
        image = get_image(data[i], IMAGE_SIZE, IMAGE_SIZE)
        gray = rgb2gray(image)
        images[i] = gray.flatten()

    with h5py.File(''.join(['faces_dataset_train.h5']), 'w') as f:
        dset_face = f.create_dataset("images", data = images)

    with h5py.File(''.join(['faces_dataset_train.h5']), 'r') as hf:
        faces = hf['images'].value

    if norm_scale:
        faces = faces / PIXEL_DEPTH

    print ("faces shape", faces.shape)
    #pdb.set_trace()

    print ("extract_data")

    return faces


# Extract test images
def extract_test_data( norm_shift=False, norm_scale=True):
    """Extract the images into a 4D tensor [image index, y, x, channels].
    Values are rescaled from [0, 255] down to [-0.5, 0.5].
    """
    print('Extracting Test data')

    data = glob(os.path.join("TEST_DATA", "*.jpg"))
    data = np.sort(data)

    def imread(path):
        return scipy.misc.imread(path).astype(np.float)

    def resize_width(image, width=28.):
        h, w = np.shape(image)[:2]
        return scipy.misc.imresize(image,[int((float(h)/w)*width),width])

    def center_crop(x, height=28):
        h= np.shape(x)[0]
        j = int(round((h - height)/2.))
        return x[j:j+height,:,:]

    def get_image(image_path, width=28, height=28):
        return center_crop(resize_width(imread(image_path), width = width),height=height)

    def rgb2gray(rgb):

        r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b

        return gray

    test = get_image(data[0],IMAGE_SIZE,IMAGE_SIZE)


    images = np.zeros((len(data),IMAGE_SIZE*IMAGE_SIZE), dtype = np.uint8)
    #pdb.set_trace()


    for i in tqdm.tqdm(range(len(data))):
        #for i in tqdm.tqdm(range(10)):
        image = get_image(data[i], IMAGE_SIZE, IMAGE_SIZE)
        gray = rgb2gray(image)
        images[i] = gray.flatten()

    with h5py.File(''.join(['faces_dataset_test.h5']), 'w') as f:
        dset_face = f.create_dataset("images", data = images)

    with h5py.File(''.join(['faces_dataset_test.h5']), 'r') as hf:
        faces = hf['images'].value

    if norm_scale:
        faces = faces / PIXEL_DEPTH

    print ("faces shape for test", faces.shape)
    #pdb.set_trace()

    print ("extract_data")

    return faces


# Augment training data
def expend_training_data(images):

    expanded_images = []
    #expanded_labels = []

    j = 0 # counter
    for x in zip(images):
        j = j+1
        if j%100==0:
            print ('expanding data : %03d / %03d' % (j,numpy.size(images,0)))

        # register original data
        expanded_images.append(x)
        #expanded_labels.append(y)
        print ("expanded_images")
        #pdb.set_trace()

        # get a value for the background
        # zero is the expected value, but median() is used to estimate background's value
        bg_value = numpy.median(x) # this is regarded as background's value
        image = numpy.reshape(x, (-1, 28))

        #pdb.set_trace()

        for i in range(4):
            # rotate the image with random degree
            angle = numpy.random.randint(-15,15,1)
            new_img = ndimage.rotate(image,angle,reshape=False, cval=bg_value)

            # shift the image with random distance
            shift = numpy.random.randint(-2, 2, 2)
            new_img_ = ndimage.shift(new_img,shift, cval=bg_value)

            # register new training data
            expanded_images.append(numpy.reshape(new_img_, IMAGE_SIZE*IMAGE_SIZE*3))
            #expanded_labels.append(y)

    # images and labels are concatenated for random-shuffle at each epoch
    # notice that pair of image and label should not be broken
    expanded_train_total_data = expanded_images
    numpy.random.shuffle(expanded_train_total_data)
    print("expanded stuff..print and see")

    #pdb.set_trace()

    return expanded_train_total_data

# Prepare celeba data
def prepare_celeba_data(use_norm_shift=False, use_norm_scale=True, use_data_augmentation=False):
    # Get the data.
    train_data_filename = 'TRAIN_IMAGES'
    test_data_filename = 'TEST_IMAGES'

    # Extract it into numpy arrays.
    train_data = extract_train_data(use_norm_shift, use_norm_scale)
    test_data = extract_test_data(use_norm_shift, use_norm_scale)

    # Generate a validation set.
    validation_data = train_data[:VALIDATION_SIZE, :]
    train_data = train_data[VALIDATION_SIZE:, :]

    # Concatenate train_data & train_labels for random shuffle
    if use_data_augmentation:
        train_total_data = expend_training_data(train_data)
    else:
        train_total_data =train_data

    train_size = train_total_data.shape[0]

    return train_total_data, train_size, validation_data, test_data
