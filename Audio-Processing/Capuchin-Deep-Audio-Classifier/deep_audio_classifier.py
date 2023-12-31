# -*- coding: utf-8 -*-
"""deep-audio-classifier.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/shravan-18/Machine-Learning-Projects/blob/main/Audio-Processing/Capuchin-Deep-Audio-Classifier/deep-audio-classifier.ipynb

# **Z by HP Unlocked Challenge 3 - Signal Processing**

# **Deep Audio Classifier**

# Install necessary dependencies
"""

!pip install tensorflow-io

"""# Import necessary libraries"""

import os
import matplotlib.pyplot as plt
import tensorflow as tf
import tensorflow_io as tfio

"""# Data Exploration

## Check how the data is, and figure out how to preprocess them
"""

# Define paths to sample audio files
capuchin = '/kaggle/input/z-by-hp-unlocked-challenge-3-signal-processing/Parsed_Capuchinbird_Clips/XC16803-1.wav'
not_capuchin = '/kaggle/input/z-by-hp-unlocked-challenge-3-signal-processing/Parsed_Not_Capuchinbird_Clips/Crickets-chirping-at-night-13.wav'

# Read the contents of a .wav file
file_contents = tf.io.read_file(capuchin)
wav, sample_rate = tf.audio.decode_wav(file_contents, desired_channels=1)
wav, sample_rate

# Check the shapes of the read contents
wav.shape, sample_rate.shape

# Check the datatype of sample rate
print(sample_rate.dtype)

# Convert the datatype of sample rate to int64
sample_rate = tf.cast(sample_rate, tf.int64)
print(sample_rate.dtype)

# Squeeze and remove the trailing axis
wav = tf.squeeze(wav, axis=-1)
wav.shape

# Goes from 44100 Hz to 16000 Hz
wav = tfio.audio.resample(wav, rate_in=sample_rate, rate_out=16000)
wav.shape, wav

# Now that the data has been analyzed, we can create the Data Loader Function now.

"""# Data Loader Function"""

# Data Loading Function as in Tensorflow Documentation to process audio

# Function name - 16k refers to 16000Hz conversion and mono refers to single channel (refer function)

def load_wav_16k_mono(filename):
    file_contents = tf.io.read_file(filename) # Read the .wav file contents
    wav, sample_rate = tf.audio.decode_wav(file_contents, desired_channels=1) # Decode .wav to tensors by channels
    wav = tf.squeeze(wav, axis=-1) # Remove trailing axis
    sample_rate = tf.cast(sample_rate, dtype=tf.int64) # Cast int64 datatype to sample rate
    wav = tfio.audio.resample(wav, rate_in=sample_rate, rate_out=16000) # Goes from 44100 Hz to 16000 Hz
    return wav

"""# Visualize how the waveforms look"""

# Load and preprocess the audio files
cap_wave = load_wav_16k_mono(capuchin)
not_cap_wave = load_wav_16k_mono(not_capuchin)

# Plot capuchin and non-capuchin audio waveforms separately
plt.figure(figsize=(12,5))
plt.subplot(1, 2, 1)
plt.title('Capuchin')
plt.plot(cap_wave)
plt.subplot(1, 2, 2)
plt.title('Not Capuchin')
plt.plot(not_cap_wave)
plt.tight_layout()

# Plot the waveforms together
plt.figure(figsize=(8,4))
plt.plot(cap_wave)
plt.plot(not_cap_wave)

"""# Create Tensorflow Dataset"""

# Define file paths
cap_path = '/kaggle/input/z-by-hp-unlocked-challenge-3-signal-processing/Parsed_Capuchinbird_Clips'
non_cap_path = '/kaggle/input/z-by-hp-unlocked-challenge-3-signal-processing/Parsed_Not_Capuchinbird_Clips'

# Create datasets
cap = tf.data.Dataset.list_files(cap_path+'/*.wav')
non_cap = tf.data.Dataset.list_files(non_cap_path+'/*.wav')

# Check if the dataset is working fine
print(cap.as_numpy_iterator().__next__())
print(non_cap.as_numpy_iterator().__next__())

# Check length of our datasets
len(cap), len(non_cap)

"""# Add labels to the capuchin and non-capuchin datasets"""

# Let capuchin be denoted by 1 and non-capuchin be denoted by 0

# We need as many 1's as there are capuchins and as many 0's as there are non-capuchins
Ones = tf.ones(len(cap))
Zeros = tf.zeros(len(non_cap))

# Assign labels to the dataset using zip, so that each label is assigned inline
positives = tf.data.Dataset.zip((cap, tf.data.Dataset.from_tensor_slices(Ones)))
negatives = tf.data.Dataset.zip((non_cap, tf.data.Dataset.from_tensor_slices(Zeros)))

# Combine positives and negatives
data = positives.concatenate(negatives)
data.as_numpy_iterator().__next__(), len(data)

"""# Determine average length of a Capuchin Bird call"""

# Calculate wave cycle length

lengths = []

for file in os.listdir(cap_path):
    tensor_wave = load_wav_16k_mono(os.path.join(cap_path, file))
    lengths.append(len(tensor_wave))

len(lengths), lengths

"""## Calculate mean, min and max"""

# Mean - (sum(lengths)/len(lengths))
tf.math.reduce_mean(lengths)

# This means on an average, our capuchin bird calls are of length 54156/16000 ~ 3.3 seconds

# Min
tf.math.reduce_min(lengths)

# Max
tf.math.reduce_max(lengths)

"""# More Data exploration

## Play around with data to find out how it is, so that we can convert them to a spectrogram
"""

# Reminder - sample capuchin is stored in capuchin variable
capuchin

wav = load_wav_16k_mono(capuchin)
wav = wav[:48000]
wav

tf.shape(wav)

[48000] - tf.shape(wav)

zp = tf.zeros([48000] - tf.shape(wav), dtype=tf.float32)
zp

wav = tf.concat([zp, wav], axis=0)
wav

s = tf.signal.stft(wav, frame_length=320, frame_step=32)
s

s = tf.abs(s)
s

s = tf.expand_dims(s, axis=-1)
s

"""# Function to convert Audio to Spectrogram"""

# Function to convert Audio to Spectrogram
def convert_to_spectrogram(filepath, label):
    '''We pass in filepath, label into the function so that we can map this to our previously created Dataset,
       which contains data in the form (filepath, label)'''

    wav = load_wav_16k_mono(filepath)
    wav = wav[:48000] # A majority amount of data to preprocess from each audio file
    zero_padding = tf.zeros([48000] - tf.shape(wav), dtype=tf.float32)
    wav = tf.concat([wav, zero_padding], axis=0)
    spectrogram = tf.signal.stft(wav, frame_length=320, frame_step=32)
    spectrogram = tf.abs(spectrogram)
    spectrogram = tf.expand_dims(spectrogram, axis=-1) # For the channels dimension that CNNs need
    return spectrogram, label

# Get a sample spectrogram and visualize it
fp, lbl = data.shuffle(10000).as_numpy_iterator().__next__()
spc, lbl = convert_to_spectrogram(fp, lbl)
plt.figure(figsize=(35, 30))
plt.imshow(tf.transpose(spc)[0])
plt.title(f"Spectrogram for {'Capuchin' if lbl==1 else 'Not Capuchin'}")
plt.show()

# Get a sample spectrogram and visualize it
fp, lbl = data.shuffle(10000).as_numpy_iterator().__next__()
spc, lbl = convert_to_spectrogram(fp, lbl)
plt.figure(figsize=(35, 30))
plt.imshow(tf.transpose(spc)[0])
plt.title(f"Spectrogram for {'Capuchin' if lbl==1 else 'Not Capuchin'}")
plt.show()

"""# Create Data pipeline, and train-test splits"""

# Create Data Pipeline
data = data.map(convert_to_spectrogram)
data = data.cache()
data = data.shuffle(buffer_size=1000)
data = data.batch(16)
data = data.prefetch(8)

# Check length of data
len(data)

# Split into train and test partitions
train = data.take(36)
test = data.skip(36).take(15)

# Test sample batch
sample, label = train.as_numpy_iterator().__next__()
sample.shape, label

"""# Build Deep Learning Model"""

from tensorflow.keras.models import Sequential
from tensorflow.keras import layers as L

# Build a Sequential Model
model = Sequential(name="model")
model.add(L.Conv2D(16, 3, activation="relu", input_shape=(1491, 257, 1)))
model.add(L.MaxPool2D((2,2)))
model.add(L.BatchNormalization())
model.add(L.Conv2D(32, 3, activation="relu"))
model.add(L.MaxPool2D((2,2)))
model.add(L.BatchNormalization())
model.add(L.Flatten())
model.add(L.Dropout(0.15))
model.add(L.Dense(128, activation="relu"))
model.add(L.Dense(1, activation="sigmoid"))

# Compile the model
model.compile(loss="binary_crossentropy",
             optimizer='Adam',
             metrics=["accuracy",
                      tf.keras.metrics.Recall(),
                      tf.keras.metrics.Precision()])

# View the model summary
model.summary()

# Train the model
history = model.fit(train, epochs=10, validation_data=test)

model.save('/kaggle/working/Deep_Audio_Classifier.h5')

# Plot the loss accuracy curves

plt.figure(figsize=(10,3))

plt.subplot(1, 2, 1)
plt.title('Loss')
plt.plot(history.history['loss'], 'b')
plt.plot(history.history['val_loss'], 'r')

plt.subplot(1, 2, 2)
plt.title('Accuracy')
plt.plot(history.history['accuracy'], 'b')
plt.plot(history.history['val_accuracy'], 'r')

plt.tight_layout()

# Plot Precision and Recall Curves

plt.figure(figsize=(10,3))

plt.subplot(1, 2, 1)
plt.title('Precision')
plt.plot(history.history['precision'], 'b')
plt.plot(history.history['val_precision'], 'r')

plt.subplot(1, 2, 2)
plt.title('Recall')
plt.plot(history.history['recall'], 'b')
plt.plot(history.history['val_recall'], 'r')

plt.tight_layout()

"""# Make a prediction on one Batch of Test Data"""

# Get one batch of test data
X_test, y_test = test.as_numpy_iterator().__next__()

# Check the shape of the X_test
X_test.shape

# Make predictions
y_pred = model.predict(X_test)

# Convert the probabilities to classes
y_pred = [1 if prediction>0.99 else 0 for prediction in y_pred] # Use high confidence
y_pred

# Check number of actual capuchin calls in our predictions and original test data
tf.math.reduce_sum(y_test), tf.math.reduce_sum(y_pred)

# Check the classes of the calls in our predictions and original test data
y_pred, y_test.astype(int)

# Comment about the model's performance

"""# Working on Forest Audio to identify Capuchin calls"""

# Build Forest parsing function - load .mp3 files
def load_mp3_16k_mono(filename):
    res = tfio.audio.AudioIOTensor(filename)           # Load the audio
    tensor = res.to_tensor()                           # Convert the tensor
    tensor = tf.math.reduce_sum(tensor, axis=1)/2      # Combine the channels
    sample_rate = res.rate                             # Extract sample rate
    sample_rate = tf.cast(sample_rate, dtype=tf.int64) # Cast int64 datatype
    wav = tfio.audio.resample(                         # Resample to 16KHz
        tensor, rate_in=sample_rate, rate_out=16000
    )

    return wav

"""## **Little Data Exploration to figure out how to work with the Forest Recordings**

#### *Note - Working on only one audio and making predictions on it. Once it seems to be working fine, we move on to working and predicting on all the audio files.*
"""

# Check working with sample Forest recording
mp3 = '/kaggle/input/z-by-hp-unlocked-challenge-3-signal-processing/Forest Recordings/recording_00.mp3'

# Convert to wav
wav = load_mp3_16k_mono(mp3)

# Slice the entire Forest audio into time slices of the same size as our model was trained on
audio_slices = tf.keras.utils.timeseries_dataset_from_array(
                wav, wav, sequence_length=48000, sequence_stride=48000, batch_size=1
            )

samples, index = audio_slices.as_numpy_iterator().__next__() # Fetch a batch
len(audio_slices), samples.shape

''' Here, what we're doing is taking the big audio clip which is in .mp3 format,
    process it and return processed .wav file/ Then we take the .wav file and slice it into windows of
    48000Hz, convert each window to spectrograms each, and make predictions on each spectrogram, and
    return the aggregated output.'''

"""# Convert Forest clips to Spectrogram and convert them to windows"""

def preprocess_mp3(sample, index):
    sample = sample[0] # Take the element
    zero_padding = tf.zeros([48000] - tf.shape(sample), dtype=tf.float32)
    wav = tf.concat([zero_padding, sample], axis=0)
    spectrogram = tf.signal.stft(wav, frame_length=320, frame_step=32)
    spectrogram = tf.abs(spectrogram)
    spectrogram = tf.expand_dims(spectrogram, axis=-1) # For the channels dimension that CNNs need
    return spectrogram, label

audio_slices = tf.keras.utils.timeseries_dataset_from_array(
                wav, wav, sequence_length=48000, sequence_stride=48000, batch_size=1
            )
audio_slices = audio_slices.map(preprocess_mp3)
audio_slices = audio_slices.batch(64)

"""# Make Predictions and group Consecutive Detections

##### *We need to group consecutive detections, as they account to only one call per detection, even if it means the detection length was long*
"""

yhat = model.predict(audio_slices)
yhat = [1 if pred > 0.99 else 0 for pred in yhat] # Use high confidence
yhat.shape, yhat

# Group calls
from itertools import groupby

yhat = [key for key, group in groupby(yhat)]
calls = tf.math.reduce_sum(yhat).numpy()
calls

"""# Work and predict on all the Audio Files"""

results = {}
forest_recordings_path = ;'/kaggle/input/z-by-hp-unlocked-challenge-3-signal-processing/Forest Recordings'

for file in os.listdir(forest_recordings_path):
    # Get File Path
    FILEPATH = os.path.join(forest_recordings_path, file)

    # Preprocess .mp3 files
    wav = load_mp3_16k_mono(FILEPATH)
    audio_slices = tf.keras.utils.timeseries_dataset_from_array(
                wav, wav, sequence_length=48000, sequence_stride=48000, batch_size=1
            )
    audio_slices = audio_slices.map(preprocess_mp3)
    audio_slices = audio_slices.batch(64)

    # Make predictions and group consecutive calls

    yhat = model.predict(audio_slices)
    yhat = [1 if pred > 0.99 else 0 for pred in yhat] # Use high confidence
    yhat = [key for key, group in groupby(yhat)]
    calls = tf.math.reduce_sum(yhat).numpy()

    results[file] = calls

"""# Export Results as .csv file"""

import csv

with open ("capuchinbird_calls_results.csv", "w", newline='') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerow(['Recording', 'Capuchin_Calls'])
    for key, value in results:
        writer.writerow([key, value])