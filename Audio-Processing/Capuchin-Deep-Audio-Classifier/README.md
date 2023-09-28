# Capuchin Deep Audio Classifier using Tensorflow

![TensorFlow](https://img.shields.io/badge/TensorFlow-Deep%20Learning-orange.svg)
![Audio_Processing](https://img.shields.io/badge/Audio_Processing-TensorflowIO-brightgreen.svg)
![Python](https://img.shields.io/badge/Python-3.x-blue.svg)

This project focuses on identifying Capuchin Bird calls from a set of Forest audio recordings. The objective is to create a model capable of recognizing and tallying Capuchin Bird vocalizations within a collection of forest audio recordings that also include background noise produced by various other wildlife species.

## Dataset

In this project, I use the Kaggle Z by HP Unlocked Challenge 3 - Signal Processing dataset. The dataset can be found [here](https://www.kaggle.com/datasets/kenjee/z-by-hp-unlocked-challenge-3-signal-processing).

### Dataset Structure
- 'Forest Recordings' - These are the Recordings to use to count the number of Calls within. Each clip is ~3 min and includes a mix of capuchinbird and other sounds.
- 'Parsed_Capuchinbird_Clips' - These are parsed clips that include specific bird calls from Capuchinbirds.
- 'Parsed_Not_Capuchinbird_Clips' - These files are parsed sounds from other animals/birds that are useful in training what is not a Capuchinbird..

## Requirements

To run this project, you'll need the following libraries and tools:
- Python 3.x
- Jupyter Notebook (for running the notebooks)
- pandas
- numpy
- scikit-learn
- TensorflowIO (for processing audio)
- TensorFlow or PyTorch (for deep learning models)
- [Kaggle API](https://github.com/Kaggle/kaggle-api) for downloading the dataset (optional)

You can install the required Python packages using `pip`:

## Usage

1. Clone this repository: git clone https://github.com/shravan-18/Machine-Learning-Projects/new/main/Audio-Processing/Capuchin-Deep-Audio-Classifier.git
2. Navigate to the project directory: cd Toxic-Comment-Classification
3. Download the Kaggle dataset (train.csv, test_labels.csv and test.csv) and place them in the project's root directory.
4. Open and run the Jupyter Notebook or Python scripts to train and evaluate different NLP models for toxic comment classification.

## Models and Approaches

- We use Tensorflow and TensorflowIO to process the audio and use Neural Networks to train the data for identification and classification
- Neural Network Layers - CNN, MaxPooling and Dense Layers

## Evaluation

- Model results at the end of 8 epochs - train_loss: 0.0015 and val_loss: 0.8089
- Test results:
      Recall: 1.0
      Accuracy: 1.0

## Contributing

Contributions and improvements are welcome! If you'd like to contribute to this project, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them to your branch.
4. Create a pull request with a clear description of your changes.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- Kaggle for providing the Z by HP Unlocked Challenge 3 - Signal Processing Challenge dataset.
- [Nicholas Renotte] ([https://www.youtube.com/watch?v=ZUqB-luawZg&list=PLgNJO2hghbmiXg5d4X8DURJP9yv9pgjIu&index=5](https://www.youtube.com/watch?v=ZLIPkmmDJAc&list=PLgNJO2hghbmiXg5d4X8DURJP9yv9pgjIu&index=13)) for the inspiring tutorial.
- [https://github.com/nicknochnack]

Feel free to reach out if you have any questions or suggestions!
