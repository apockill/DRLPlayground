import random
from pathlib import Path

import cv2
import numpy as np


class Dataset:
    def __init__(self, img_dir, fraction_test_set, load_resolution=None):
        """
        :param img_dir: A directory full of *.png images
        :param fraction_test_set: 0-1, the fraction of images to be put in the test set
        :param load_resolution: (width, height) to load the images at. If None, it will use the original size
        """
        assert 0 <= fraction_test_set < 1, "The fraction test set must be between 0 and 1!"

        self.img_dir = img_dir
        self.fraction_test = fraction_test_set

        self.img_paths = list(Path(self.img_dir).glob("*.png"))
        random.seed(0)
        random.shuffle(self.img_paths)

        if load_resolution is None:
            # Get a sample image in order to figure out the height and width of the dataset samples
            sample_img = cv2.imread(str(self.img_paths[0]))
            assert sample_img is not None, "The Dataset object was unable to load an image!"
            shape = sample_img.shape
            self.height = shape[0]
            self.width = shape[1]
            self.channels = shape[2]
        else:
            self.width = load_resolution[0]
            self.height = load_resolution[1]
            self.channels = 3


    def __len__(self):
        return len(self.img_paths)

    def load(self):

        num_test = len(self) * self.fraction_test

        x_test = []
        x_train = []
        for i, img_path in enumerate(self.img_paths):
            img = cv2.imread(str(img_path))

            if img.shape != (self.height, self.width, self.channels):
                img = cv2.resize(img, (self.width, self.height))
                # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            if i < num_test:
                x_test.append(img)
            else:
                x_train.append(img)

        return np.asarray(x_train), np.asarray(x_test)

