# -*- coding: utf-8 -*-
"""ela.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1J5eGoTLC20nct1oboaojZH-OB20dRMLL
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
# %matplotlib inline
np.random.seed(2)
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import itertools
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPool2D
from tensorflow.keras.optimizers.legacy import RMSprop
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ReduceLROnPlateau, EarlyStopping
sns.set(style='white', context='notebook', palette='deep')
from PIL import Image
import os
from pylab import *
import re
from PIL import Image, ImageChops, ImageEnhance

def get_imlist(path):
    return [os.path.join(path,f) for f in os.listdir(path) if f.endswith('.jpg') or f.endswith('.png')]

def convert_to_ela_image(path, quality):
    filename = path
    resaved_filename = filename.split('.')[0] + '.resaved.jpg'
    ELA_filename = filename.split('.')[0] + '.ela.png'
    im = Image.open(filename).convert('RGB')
    im.save(resaved_filename, 'JPEG', quality=quality)
    resaved_im = Image.open(resaved_filename)
    ela_im = ImageChops.difference(im, resaved_im)
    extrema = ela_im.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    if max_diff == 0:
        max_diff = 1
    scale = 255.0 / max_diff
    ela_im = ImageEnhance.Brightness(ela_im).enhance(scale)
    return ela_im

!pip install np_utils

from google.colab import drive
drive.mount('/content/drive')

Image.open('/content/drive/MyDrive/dataset/CASIA2/Au/Au_ani_00001.jpg')

convert_to_ela_image('/content/drive/MyDrive/dataset/CASIA2/Au/Au_ani_00001.jpg', 90)

Image.open('/content/drive/MyDrive/dataset/CASIA2/Tp/Tp_D_CRN_M_N_ani00097_ani00001_10099.tif')

convert_to_ela_image('/content/drive/MyDrive/dataset/CASIA2/Tp/Tp_D_CRN_M_N_ani00097_ani00001_10099.tif', 90)

image_size = (128, 128)
def prepare_image(image_path):
    return np.array(convert_to_ela_image(image_path, 90).resize(image_size)).flatten() / 255.0
X = []
Y = []

import random
path = '/content/drive/MyDrive/dataset/CASIA1/Au/'
for dirname, _, filenames in os.walk(path):
  for filename in filenames:
    if filename.endswith('jpg') or filename.endswith('png'):
      full_path = os.path.join(dirname, filename)
      X.append(prepare_image(full_path))
      Y.append(0)
      if len(Y) % 500 == 0:
        print(f'Processing {len(Y)} images')
random.shuffle(X)
X = X[:2100]
Y = Y[:2100]
print(len(X), len(Y))

path = '/content/drive/MyDrive/dataset/CASIA1/Sp/'
for dirname, _, filenames in os.walk(path):
    for filename in filenames:
        if filename.endswith('jpg') or filename.endswith('png'):
            full_path = os.path.join(dirname, filename)
            X.append(prepare_image(full_path))
            Y.append(1)
            if len(Y) % 500 == 0:
                print(f'Processing {len(Y)} images')

print(len(X), len(Y))

X = np.array(X)
Y = to_categorical(Y, 2)
X = X.reshape(-1, 128, 128, 3)
X_train, X_val, Y_train, Y_val = train_test_split(X, Y, test_size = 0.2, random_state=5)

model = Sequential()

model.add(Conv2D(filters = 32, kernel_size = (5,5),padding = 'valid',
                 activation ='relu', input_shape = (128,128,3)))
print("Input: ", model.input_shape)
print("Output: ", model.output_shape)

model.add(Conv2D(filters = 32, kernel_size = (5,5),padding = 'valid',
                 activation ='relu'))
print("Input: ", model.input_shape)
print("Output: ", model.output_shape)

model.add(MaxPool2D(pool_size=(2,2)))

model.add(Dropout(0.25))
print("Input: ", model.input_shape)
print("Output: ", model.output_shape)

model.add(Flatten())
model.add(Dense(256, activation = "relu"))
model.add(Dropout(0.5))
model.add(Dense(2, activation = "softmax"))

model.summary()

optimizer = RMSprop(learning_rate = 0.0005,rho=0.9, epsilon=1e-08, decay=0.0)
model.compile(optimizer = optimizer, loss = 'categorical_crossentropy', metrics = ['accuracy'])
early_stopping = EarlyStopping(monitor = 'val_acc',
                              min_delta = 0,
                              patience = 2,
                              verbose = 0,
                              mode = 'auto')
epochs = 30
batch_size = 100
hist = model.fit(X_train,
                 Y_train,
                 batch_size = batch_size,
                 epochs = epochs,
                validation_data = (X_val, Y_val),verbose=2,
                callbacks = [early_stopping])

# ig, ax = plt.subplots(2,1)
# ax[0].plot(hist.history['loss'], color='b', label="Training loss")
# ax[0].plot(hist.history['val_loss'], color='r', label="validation loss",axes =ax[0])
# legend = ax[0].legend(loc='best', shadow=True)

# ax[1].plot(hist.history['accuracy'], color='b', label="Training accuracy")
# ax[1].plot(hist.history['val_accuracy'], color='r',label="Validation accuracy")
# legend = ax[1].legend(loc='best', shadow=True)

plt.figure()
plt.rcParams['figure.figsize'] = [5, 2]
plot(hist.history['loss'], color='b', label="Training loss", )
plot(hist.history['val_loss'], color='r', label="validation loss")
plt.legend(loc='best', shadow=True)
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.show()

plt.figure()
plt.rcParams['figure.figsize'] = [5, 2]
plot(hist.history['accuracy'], color='b', label="Training accuracy")
plot(hist.history['val_accuracy'], color='r',label="Validation accuracy")
plt.legend(loc='best', shadow=True)
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.show()

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
Y_pred = model.predict(X_val)
Y_pred_classes = np.argmax(Y_pred,axis = 1)
Y_true = np.argmax(Y_val,axis = 1)
confusion_mtx = confusion_matrix(Y_true, Y_pred_classes)
plot_confusion_matrix(confusion_mtx, classes = range(2))