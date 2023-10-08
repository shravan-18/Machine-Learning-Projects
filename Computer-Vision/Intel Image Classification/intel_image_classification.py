# -*- coding: utf-8 -*-
"""intel-image-classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/shravan-18/Machine-Learning-Projects/blob/main/Computer-Vision/Intel%20Image%20Classification/intel-image-classification.ipynb
"""

# # This Python 3 environment comes with many helpful analytics libraries installed
# # It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# # For example, here's several helpful packages to load

# import numpy as np # linear algebra
# import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# # Input data files are available in the read-only "../input/" directory
# # For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

# import os
# for dirname, _, filenames in os.walk('/kaggle/input'):
#     for filename in filenames:
#         print(os.path.join(dirname, filename))

# # You can write up to 20GB to the current directory (/kaggle/working/) that gets preserved as output when you create a version using "Save & Run All"
# # You can also write temporary files to /kaggle/temp/, but they won't be saved outside of the current session

import os

train_dir = '/kaggle/input/intel-image-classification/seg_train/seg_train'
test_dir = '/kaggle/input/intel-image-classification/seg_test/seg_test'
pred_dir = '/kaggle/input/intel-image-classification/seg_pred/seg_pred'

class_names = os.listdir(train_dir)

# View an image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import random

def view_random_image(target_dir, target_class):
  # Setup target directory (we'll view images from here)
  target_folder = target_dir+'/'+target_class

  # Get a random image path
  random_image = random.sample(os.listdir(target_folder), 1)

  # Read in the image and plot it using matplotlib
  img = mpimg.imread(target_folder + "/" + random_image[0])
  plt.imshow(img)
  plt.title(target_class)
  plt.axis("off");

  print(f"Image shape: {img.shape}") # show the shape of the image

#   return img

import random

sample_class = random.sample(class_names, 1)[0]
view_random_image(train_dir, sample_class)

for i in class_names:
    curr_path = os.path.join(train_dir, i)
    print(f"{i}, {len(os.listdir(curr_path))}")

for i in class_names:
    curr_path = os.path.join(test_dir, i)
    print(f"{i}, {len(os.listdir(curr_path))}")

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

train_datagen = ImageDataGenerator(rescale=1./255)
val_datagen = ImageDataGenerator(rescale=1./255)

train_data = train_datagen.flow_from_directory(directory=train_dir,
                                              target_size=(150, 150),
                                              class_mode='categorical',
                                              batch_size=32)

val_data = val_datagen.flow_from_directory(directory=test_dir,
                                              target_size=(150, 150),
                                              class_mode='categorical',
                                              batch_size=32)

import cv2
import numpy as np

images = []

for file in os.listdir(pred_dir):
    img = cv2.imread(os.path.join(pred_dir, file))
    img = cv2.resize(img, (150, 150))
    img = img / 255.0
    images.append(img)

images = np.array(images)

test_datagen = ImageDataGenerator()
test_data = test_datagen.flow(x=images, batch_size=32)

train_data.class_indices

val_data.class_indices

len(class_names)

import tensorflow as tf
from tensorflow.keras import layers as L
from tensorflow.keras.models import Model

def create_model(input_shape = (150, 150, 3)):

    Inputs = L.Input(shape=input_shape)
    x = L.Conv2D(32, 3, padding="same")(Inputs)
    x = L.MaxPooling2D((2,2))(x)
    x = L.Conv2D(64, 3, padding="same")(x)
    x = L.MaxPooling2D((2,2))(x)
    x = L.Conv2D(128, 3, padding="same")(x)
    x = L.MaxPooling2D((2,2))(x)
    x = L.Flatten()(x)
    x = L.Dense(512, activation="relu")(x)
    Outputs = L.Dense(len(class_names), activation="softmax")(x)

    model = Model(Inputs, Outputs)
    return model

strategy = tf.distribute.MirroredStrategy()
print('Number of devices: {}'.format(strategy.num_replicas_in_sync))

# with strategy.scope():
model_1 = create_model()

model_1.compile(loss = "categorical_crossentropy",
               optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
               metrics=["accuracy"])

model_1.summary()

early_stopping = tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=3)

history = model_1.fit(train_data,
                    epochs=6,
                    steps_per_epoch = len(train_data),
                    verbose=1,
                    validation_data = val_data,
                    validation_steps = int(0.25*(len(val_data))),
                    callbacks = [early_stopping])

# Plot the validation and training data separately
def plot_loss_curves(history):
  """
  Returns separate loss curves for training and validation metrics.
  """
  loss = history.history['loss']
  val_loss = history.history['val_loss']

  accuracy = history.history['accuracy']
  val_accuracy = history.history['val_accuracy']

  epochs = range(len(history.history['loss']))

  # Plot loss
  plt.plot(epochs, loss, label='training_loss')
  plt.plot(epochs, val_loss, label='val_loss')
  plt.title('Loss')
  plt.xlabel('Epochs')
  plt.legend()

  # Plot accuracy
  plt.figure()
  plt.plot(epochs, accuracy, label='training_accuracy')
  plt.plot(epochs, val_accuracy, label='val_accuracy')
  plt.title('Accuracy')
  plt.xlabel('Epochs')
  plt.legend();

plot_loss_curves(history)

from tensorflow.keras.optimizers import RMSprop

from tensorflow.keras.applications import ResNet50

# Load the pre-trained ResNet50 model
base_model = ResNet50(weights='imagenet', include_top=False)

# Freeze all layers except the last 10
for layer in base_model.layers[:-10]:
    layer.trainable = False

Inputs = L.Input(shape=(150,150,3))
x = base_model(Inputs)
x = L.GlobalAveragePooling2D()(x)
x = L.Dense(512, activation="relu")(x)
Outputs = L.Dense(len(class_names), activation="softmax")(x)

model_2 = Model(Inputs, Outputs, name="transfer_model")

model_2.compile(loss="categorical_crossentropy",
               optimizer=RMSprop(learning_rate=0.001),
               metrics=["accuracy"])

model_2.summary()

history_2 = model_2.fit(train_data,
                    epochs=10,
                    steps_per_epoch = len(train_data),
                    verbose=1,
                    validation_data = val_data,
                    validation_steps = int(0.25*(len(val_data))))

def pred_and_plot(model, filename, class_names):
    """
    Imports an image located at filename, makes a prediction on it with
    a trained model and plots the image with the predicted class as the title.
    """
    # Import the target image and preprocess it
    img = cv2.imread(pred_dir+'/'+filename)
    img = cv2.resize(img, (150, 150))
    img = img / 255.0

    # Make a prediction
    pred = model.predict(tf.expand_dims(img, axis=0))
#     print(tf.round(pred))
#     print(np.argmax(tf.round(pred)))
#     print(class_names[np.argmax(tf.round(pred))])

#     # Get the predicted class
    pred_class = class_names[np.argmax(tf.round(pred))]

    # Plot the image and predicted class
    plt.imshow(img)
    plt.title(f"Prediction: {pred_class}")
    plt.axis(False);

pred_imgs = os.listdir(pred_dir)
pred_imgs[:5]

pred_sample = random.sample(pred_imgs, 1)[0]
pred_and_plot(model_2, pred_sample, class_names)