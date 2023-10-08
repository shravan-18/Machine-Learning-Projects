# -*- coding: utf-8 -*-
"""watermark-detection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/shravan-18/Machine-Learning-Projects/blob/main/Computer-Vision/Watermark%20Detection/watermark-detection.ipynb
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

import pandas as pd

train = pd.read_csv('/kaggle/input/watermark/train.csv')

test = pd.read_csv('/kaggle/input/watermark/test.csv')

train.head()

train_dir = '/kaggle/input/watermark/train'
test_dir = '/kaggle/input/watermark/test'

train.loc[train['Image'] == '4QLBJ8.jpg']

import os
import random
from PIL import Image
import matplotlib.pyplot as plt

# Get a list of image filenames in the directory
image_files = os.listdir(train_dir)

# Randomly select 6 unique images
random_images = random.sample(image_files, 6)

# Create a subplot with 3 rows and 2 columns
fig, axes = plt.subplots(3, 2, figsize=(10, 10))

# Display the selected images and their labels
for i, image_filename in enumerate(random_images):
    curr_image_path = os.path.join(train_dir, image_filename)

    # Load the image using PIL
    img = Image.open(curr_image_path)

    # Use conditional indexing to retrieve the value from 'Column_B'
    Image_Label = train.loc[train['Image'] == image_filename, 'Label'].values[0]

    # Determine the row and column for this image in the 3x2 grid
    row = i // 2
    col = i % 2

    # Plot the image on the corresponding subplot
    axes[row, col].imshow(img)
    # Set the title of the subplot to the image filename
    axes[row, col].set_title(Image_Label)

# Remove any empty subplots
for i in range(len(image_files), 6):
    row = i // 2
    col = i % 2
    fig.delaxes(axes[row, col])

# Adjust the layout
plt.tight_layout()

# Show the plot
plt.show()

# Randomly select 6 unique images
random_images = random.sample(image_files, 1)[0]

# Create a subplot with 3 rows and 2 columns
fig, axes = plt.subplots(2, 2, figsize=(10, 10))

curr_image_path = os.path.join(train_dir, random_images)

# Load the image using PIL
img = Image.open(curr_image_path)
print(img.size)
# Use conditional indexing to retrieve the value from 'Column_B'
Image_Label = train.loc[train['Image'] == image_filename, 'Label'].values[0]

# Plot the image on the corresponding subplot
axes[0, 0].imshow(img)
# Set the title of the subplot to the image filename
axes[0, 0].set_title('Original')

img = img.resize((300,300))

# Plot the image on the corresponding subplot
axes[0, 1].imshow(img)
# Set the title of the subplot to the image filename
axes[0, 1].set_title('Resized')

pd.DataFrame(train.Label.value_counts())

train.Label = train.Label.astype(str)
test.Label = test.Label.astype(str)

from tensorflow.keras.preprocessing.image import ImageDataGenerator

train_datagen = ImageDataGenerator(rescale = 1./255, validation_split=0.3)

train_generator = train_datagen.flow_from_dataframe(
                    dataframe=train,
                    directory=train_dir,
                    x_col="Image",
                    y_col="Label",
                    target_size=(300, 300),
                    batch_size=100,
                    class_mode="binary",
                    subset='training',
                    shuffle=True,
                    seed = 1
)

val_datagen = ImageDataGenerator(rescale = 1./255, validation_split=0.3)

val_generator = val_datagen.flow_from_dataframe(
                    dataframe=train,
                    directory=train_dir,
                    x_col="Image",
                    y_col="Label",
                    target_size=(300, 300),
                    batch_size=100,
                    class_mode="binary",
                    subset='validation',
                    shuffle=True,
                    seed = 1
)

test_datagen = ImageDataGenerator(rescale = 1./255)

test_generator = val_datagen.flow_from_dataframe(
                    dataframe=test,
                    directory=test_dir,
                    x_col="Image",
                    target_size=(300, 300),
                    batch_size=100,
                    class_mode=None
)

from keras.optimizers import RMSprop

import tensorflow as tf
from tensorflow.keras import layers as L
from tensorflow.keras.models import Model

def create_model(input_shape = (300,300, 3)):

    Inputs = L.Input(shape=input_shape)
    x = L.Conv2D(32, 3, padding="same")(Inputs)
    x = L.MaxPooling2D((2,2))(x)
    x = L.Conv2D(64, 3, padding="same")(x)
    x = L.MaxPooling2D((2,2))(x)
    x = L.Conv2D(64, 3, padding="same")(x)
    x = L.MaxPooling2D((2,2))(x)
    x = L.Conv2D(128, 3, padding="same")(x)
    x = L.MaxPooling2D((2,2))(x)
    x = L.Flatten()(x)
    x = L.Dense(512, activation="relu")(x)
    Outputs = L.Dense(1, activation="sigmoid")(x)

    model = Model(Inputs, Outputs)
    return model

strategy = tf.distribute.MirroredStrategy()
print('Number of devices: {}'.format(strategy.num_replicas_in_sync))

with strategy.scope():
    model_1 = create_model()

model_1.compile(loss = "binary_crossentropy",
               optimizer=RMSprop(learning_rate=0.001),
               metrics=["accuracy"])

model_1.summary()

history = model_1.fit(train_generator,
                    epochs=20,
                    steps_per_epoch = len(train_generator),
                    verbose=1,
                    validation_data = val_generator,
                    validation_steps = len(val_generator))

import matplotlib.pyplot as plt

acc=history.history['accuracy']
val_acc=history.history['val_accuracy']
loss=history.history['loss']
val_loss=history.history['val_loss']


plt.plot( acc)
plt.plot( val_acc)
plt.title('Training and validation accuracy')
plt.figure()

plt.plot(loss)
plt.plot( val_loss)


plt.title('Training and validation loss')
plt.show()

predictions = model_1.predict(test_generator)
predictions

my_list=[]
for pred in predictions:
    if pred >=0.5 :
        my_list.append(1)
    else :
        my_list.append(0)

submission= pd.DataFrame(my_list,columns=['Label'])
submission.head()

submission.value_counts().plot.bar()

# Specify the file path you want to delete
file_path = '/kaggle/working/sub.csv'

try:
    # Attempt to remove the file
    os.remove(file_path)
    print(f"{file_path} has been deleted successfully.")
except OSError as e:
    # Handle any errors, such as if the file doesn't exist
    print(f"Error: {e.filename} - {e.strerror}")

submission.to_csv('/kaggle/working/sub.csv')