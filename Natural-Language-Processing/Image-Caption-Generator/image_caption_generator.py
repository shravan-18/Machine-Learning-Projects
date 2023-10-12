# -*- coding: utf-8 -*-
"""image-caption-generatorrr.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1m-w3rfb2qVLvHNzSoba9y0FLwV4dm7aj

# **Image Caption Generator**

## **Install necessary dependencies**
"""

!pip install tqdm tensorflow tensorflow-gpu keras numpy pillow

"""## **Import Libraries**"""

import string
import numpy as np
from PIL import Image
import os
from pickle import dump, load
import numpy as np
import matplotlib.pyplot as plt
import argparse

from keras.applications.xception import Xception, preprocess_input
from keras.utils import load_img, img_to_array, pad_sequences
from keras.preprocessing.text import Tokenizer
from keras.utils import to_categorical
from keras.models import Model, load_model
from keras.layers import Input, Dense, LSTM, Embedding, Dropout, Add

from tqdm import tqdm_notebook as tqdm
tqdm().pandas()

"""## **Data Exploration and Analysis**"""

# View text file
filename = "/kaggle/input/image-caption-generatorr/python-project-image-caption-generator/Flickr8k_text/Flickr8k.token.txt"
with open(filename) as file:
    for i in range(10):
        line = file.readline()
        if not line:
            break  # Exit the loop if the end of the file is reached
        print(line, end='')  # end='' to avoid extra newline

# So each image has a set of captions mapped to it...

"""## **Creating Functions for Data Preprocessing**"""

def load_doc(filename):
    '''
    Function to read the contents in a file and return it.

    Returns - Contents of input file as a string.
    '''
    with open(filename, 'r') as file:
        text = file.read()
        file.close()
        return text

def get_img_captions(filename):
    '''
    Function to get all the images and their corresponding captions, and map them using
    a dictionary.

    Returns - Mapped dictionary of images with their list of corresponding captions.

    '''
    content = load_doc(filename)    # Load the file contents
    captions = content.split('\n')  # Split file contents based off NewLine
    map_dict = {}                   # Create empty dictionary for mapping images with captions

    for caption in captions[:-1]:
        img, caption = caption.split('\t')     # The image and captions are separated by a tab space
        if img[:-2] not in map_dict:           # Check if image has already been added in dictionary
            map_dict[img[:-2]] = [caption]     # Add image and map current description to it
        else:
            map_dict[img[:-2]].append(caption) # Append caption to list of captions already mapped

    return map_dict

def clean_text(map_dict):
    '''
    Function to clean the caption texts - Lowercasing, remove punctuations and words with numbers

    Returns - Cleaned captions.
    '''
    table = str.maketrans('','',string.punctuation)

    for image, captions in map_dict.items():
        for i, img_caption in enumerate(captions):
            img_caption.replace("-"," ")                     # Replace '-' characters with whitespace
            desc = img_caption.split()                       # Split the string into list

            desc = [word.lower() for word in desc]           # Convert words to lowercase
            desc = [word.translate(table) for word in desc]  # Removes punctuations
            desc = [word for word in desc if len(word)>1]    # Removes hanging words
            desc = [word for word in desc if word.isalpha()] # Removes words with numbers

            img_caption = ''.join(desc)                      # Convert list back to string
            map_dict[image][i] = img_caption                 # Replace old caption with cleaned one

    return map_dict

def build_vocabulary(map_dict):
    '''
    Function to build vocabulary of all unique words.

    Returns - Built vocabulary.
    '''
    vocab = set()

    for key in map_dict.keys():
        [vocab.update(value.split()) for value in map_dict[key]] # Create vocabulary

    return vocab

def save_descriptions(map_dict, filename):
    '''
    Store all the captions mapped to corresponding image in a single file.

    Returns - Text file with descriptions saved.
    '''
    text_lines = []              # Empty list to store lines to write into file

    for img, caption_list in map_dict.items():
        for caption in caption_list:
            text_lines.append(img + "\t" + caption)

    data = '\n'.join(text_lines) # Join the lines based off NewLine
    with open(filename, 'w') as file:
        file.write(data)         # Write data into file
        file.close()

# Make use of the above funtions

dataset_text = "/kaggle/input/image-caption-generatorr/python-project-image-caption-generator/Flickr8k_text"
dataset_images = "/kaggle/input/image-caption-generatorr/python-project-image-caption-generator/Flicker8k_Dataset"

# Set filename
filename = dataset_text + "/" + "Flickr8k.token.txt"

# Loading the file that contains all data and Mapping them into descriptions dictionary
MapDict = get_img_captions(filename)
print("Length of descriptions =" ,len(MapDict))

# Cleaning the captions
MapDict = clean_text(MapDict)

# Build vocabulary
vocabulary = build_vocabulary(MapDict)
print("Length of vocabulary = ", len(vocabulary))

# Saving to file
save_descriptions(MapDict, "/kaggle/working/descriptions.txt")

"""## **Extract features from images**"""

def extract_features(directory):
    '''
    Function to extract features from images in the directory passed as arguement.
    Feature extraction is done using Xception model.

    Returns - Extracted features from images mapped to each image stored in a dictionary.
    '''
    model = Xception(include_top=False, pooling='avg')
    features = {}
    for img in tqdm(os.listdir(directory)):
        filename = directory + "/" + img
        image = Image.open(filename)          # Open image
        image = image.resize((299,299))       # Resize image to Xception's input layer shape
        image = np.expand_dims(image, axis=0) # Expand dimension along initial axis to predict

        #image = preprocess_input(image)
        image = (image/127.5) - 1.            # Preprocess image

        feature = model.predict(image)        # Predict on image and get features
        features[img] = feature               # Append feature to features dictionary
    return features

#2048 feature vector
features = extract_features(dataset_images)
dump(features, open("/kaggle/working/features.p","wb"))

# Load the features
features = load(open("/kaggle/working/features.p","rb"))

"""# **Functions for loading dataset**"""

def get_image_names(filename):
    '''
    Function to get names of all images from the input text file.

    Returns - List of image names.
    '''
    file = load_doc(filename)             # Load file
    images_names = file.split('\n')[:-1]  # Get image names from file
    return images_names

def load_update_captions(filename, image_names):
    '''
    Function to create a dictionary that contains captions for each photo from the list of photos.
    We also append the <start> and <end> identifier for each caption.
    We need this so that our LSTM model can identify the starting and ending of the caption.

    Returns - Dictionary of cleaned captions mapped to corresponding image.
    '''
    file = load_doc(filename)                      # Load file
    updated_captions = {}

    for line in file.split('\n'):
        words = line.split()                       # Split line into list of words
        if len(words)<1:
            continue

        image, image_caption = words[0], words[1:] # Load image and caption

        # Update captions by adding <start> and <end>
        if image in image_names:
            if image not in updated_captions:
                updated_captions[image] = []
            updated_caption = '<start> ' + " ".join(image_caption) + ' <end>'
            updated_captions[image].append(updated_caption)

    return updated_captions

def load_features(image_names):
    '''
    Function to load features of all image names.

    Returns dictionary of loaded features mapped to corresponding image name.
    '''
    all_features = load(open("/kaggle/working/features.p", "rb"))    # Load file
    features = {image: all_features[image] for image in image_names} # Get stored features

    return features


filename = dataset_text + "/" + "Flickr_8k.trainImages.txt"

train_imgs = get_image_names(filename)
train_descriptions = load_update_captions("descriptions.txt", train_imgs)
train_features = load_features(train_imgs)

"""## **Tokenizing Vocabulary**"""

def extract_captions(map_dict):
    '''
    Function to extract captions from image-captions dictionary to list of captions.

    Returns - List of extracted captions
    '''
    all_captions = []
    for key in map_dict.keys():
        [all_captions.append(caption) for caption in map_dict[key]]  # Extract captions
    return all_captions


def create_tokenizer(map_dict):
    '''
    Function to create tokenizer to vectorise text corpus.
    Each integer will represent token in dictionary.

    Returns - Tokenizer fit on the image captions.
    '''
    captions_list = extract_captions(map_dict) # Extract captions
    tokenizer = Tokenizer()                    # Instantiate Tokenizer class object
    tokenizer.fit_on_texts(map_dict)           # Fit the Tokenizer on captions
    return tokenizer

tokenizer = create_tokenizer(train_descriptions)
dump(tokenizer, open('tokenizer.p', 'wb')) # Create tokenizer.p file to store tokenized vector corpus
vocab_size = len(tokenizer.word_index) + 1
print(f"Vocabulary size: {vocab_size}")

# Find out max length of a single caption among all captions
def max_length(map_dict):
    '''
    Function to calculate maximum length of a caption amongst all available captions

    Returns - Length of longest caption
    '''
    caption_list = extract_captions(map_dict)
    return max(len(caption) for caption in caption_list)

max_length = max_length(MapDict)
print(f"Length of longest caption: {max_length}")

"""## **Create Data Generator**"""

def create_sequences(tokenizer, max_length, caption_list, feature):
    '''
    Function to create a sequence input image, input sequence and output word

    Returns - (input image, input sequence and output word)
    '''
    input_image, input_sequence, output_word = list(), list(), list()

    for caption in caption_list:
        seq = tokenizer.texts_to_sequences([caption])[0]
        # Split one sequence into multiple X,y pairs

        for i in range(1, len(seq)):
            # Split into input and output pair
            in_seq, out_seq = seq[:i], seq[i]
            # Pad input sequence
            in_seq = pad_sequences([in_seq], maxlen=max_length)[0]
            # Encode output sequence
            out_seq = to_categorical([out_seq], num_classes=vocab_size)[0]
            # Store the data in the initially created lists
            input_image.append(feature)
            input_sequence.append(in_seq)
            output_word.append(out_seq)

    return np.array(input_image), np.array(input_sequence), np.array(output_word)

def data_generator(map_dict, features, tokenizer, max_length):
    '''
    Data generator, used by model.fit_generator()

    Returns - input-output sequence pairs from the image description.
    '''
    while True:
        for image, caption_list in map_dict.items():
            feature = features[image][0] # Get features of image
            input_image, input_sequence, output_word = create_sequences(
                                                            tokenizer,
                                                            max_length,
                                                            caption_list,
                                                            feature
                                                        )
            yield [[input_image, input_sequence], output_word]

# Checking if everything is working fine
[a,b],c = next(data_generator(train_descriptions, features, tokenizer, max_length))
a.shape, b.shape, c.shape

"""# **Model Creation**

##  To define the structure of the model, we will be using the Keras Model from Functional API. It will consist of three major parts:

> ###  **Feature Extractor** – The feature extracted from the image has a size of 2048, with a dense layer, we will reduce the dimensions to 256 nodes.
>
> ###  **Sequence Processor** – An embedding layer will handle the textual input, followed by the LSTM layer.
>
> ###  **Decoder** – By merging the output from the above two layers, we will process by the dense layer to make the final prediction. The final layer will contain the number of nodes equal to our vocabulary size.
"""

def create_model(vocab_size, max_length):
    '''
    Function to create the deep learning model the image caption generator problem.

    Returns - Keras model instance.
    '''
    inputs1 = Input(shape=(2048,))
    fe1 = Dropout(0.5)(inputs1)
    fe2 = Dense(256, activation='relu')(fe1)

    # LSTM sequence model
    inputs2 = Input(shape=(max_length,))
    se1 = Embedding(vocab_size, 256, mask_zero=True)(inputs2)
    se2 = Dropout(0.5)(se1)
    se3 = LSTM(256)(se2)

    # Merging both models
    decoder1 = Add([fe2, se3])
    decoder2 = Dense(256, activation='relu')(decoder1)
    outputs = Dense(vocab_size, activation='softmax')(decoder2)

    # Create the model
    model = Model(inputs=[inputs1, inputs2], outputs=outputs)
    model.compile(loss='categorical_crossentropy', optimizer='adam')

    print(model.summary())
    plot_model(model, to_file='/kaggle/working/model.png', show_shapes=True)
    return model

# Training the model

print('Dataset: ', len(train_imgs))
print('Descriptions: train=', len(train_descriptions))
print('Photos: train=', len(train_features))
print('Vocabulary Size:', vocab_size)
print('Description Length: ', max_length)

model = create_model(vocab_size, max_length)
epochs = 10
steps_per_epoch = len(train_descriptions)

# making a directory models to save our models
os.mkdir("Models")

for i in range(epochs):
    generator = data_generator(train_descriptions,
                               train_features,
                               tokenizer,
                               max_length)

    model.fit_generator(generator,
                        epochs=epochs,
                        steps_per_epoch=steps_per_epoch,
                        verbose=1)

    model.save("/kaggle/working/Models/model_" + str(i) + ".h5")

"""## **Testing the model**"""

ap = argparse.ArgumentParser()
ap.add_argument('-i', '--image', required=True, help="Image Path")
args = vars(ap.parse_args())
img_path = args['image']

def extract_features(filename, model):
    '''
    Function to extract features from testing image

    Returns - Extracted features.
    '''
    try:
        image = Image.open(filename)
    except:
        print("ERROR: Couldn't open image! Make sure the image path and extension is correct")

    image = image.resize((299,299))  # Resize the image to the same shape we did before
    image = np.array(image)

    # for images that has 4 channels, we convert them into 3 channels
    if image.shape[2] == 4:
        image = image[..., :3]

    image = np.expand_dims(image, axis=0) # Expand dimensions along first axis for predicting
    image = (image/127.5) - 1.            # Preprocess image
    feature = model.predict(image)        # Extract features

    return feature

def word_for_id(integer, tokenizer):
    '''
    Function to return the word mapped to a particular integer by the tokenizer.

    Returns - word encoded by the tokenizer.
    '''
    for word, index in tokenizer.word_index.items():
        if index == integer:
            return word
    return None


def generate_desc(model, tokenizer, photo, max_length):
    '''
    Generates description for the image being predicted.

    Returns - Caption for predicted image.
    '''
    in_text = 'start'

    for i in range(max_length):
        sequence = tokenizer.texts_to_sequences([in_text])[0]   # Convert to sequence
        sequence = pad_sequences([sequence], maxlen=max_length) # Pad sequence
        pred = model.predict([photo,sequence], verbose=0)       # Predict using model
        pred = np.argmax(pred)
        word = word_for_id(pred, tokenizer)                     # Convert predictions to words

        if word is None:
            break
        in_text += ' ' + word
        if word == 'end':
            break

    return in_text

img_path = 'Flicker8k_Dataset/111537222_07e56d5a30.jpg'

max_length = 32
tokenizer = load(open("tokenizer.p","rb"))

model = load_model('/kaggle/working/Models/model_9.h5')
xception_model = Xception(include_top=False, pooling="avg")

photo = extract_features(img_path, xception_model)
description = generate_desc(model, tokenizer, photo, max_length)

img = Image.open(img_path)
print("\n\n")
print(description)
plt.imshow(img)