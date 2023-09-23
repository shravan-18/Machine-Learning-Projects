# Toxic Comment Classification using NLP

![TensorFlow](https://img.shields.io/badge/TensorFlow-Deep%20Learning-orange.svg)
![NLP](https://img.shields.io/badge/NLP-Natural%20Language%20Processing-brightgreen.svg)
![Python](https://img.shields.io/badge/Python-3.x-blue.svg)

This project focuses on classifying toxic comments using Natural Language Processing (NLP) techniques. The goal is to develop a model that can identify and flag comments containing offensive or harmful content.

## Dataset

In this project, I use the Kaggle Toxic Comment Classification Challenge dataset, which includes a large collection of Wikipedia comments labeled with various toxicity categories, such as toxic, severe toxic, obscene, threat, insult, and identity hate. The dataset can be found [here](https://www.kaggle.com/c/jigsaw-toxic-comment-classification-challenge/data).

### Dataset Structure
- `train.csv`: The training dataset containing comments and their corresponding labels.
- `test.csv`: The test dataset for evaluation.
- `test_labels.csv`: Labels for the test set.
- `sample_submission.csv`: A sample submission file for the Kaggle competition.

## Requirements

To run this project, you'll need the following libraries and tools:
- Python 3.x
- Jupyter Notebook (for running the notebooks)
- pandas
- numpy
- scikit-learn
- NLTK (Natural Language Toolkit)
- TensorFlow or PyTorch (for deep learning models)
- [Kaggle API](https://github.com/Kaggle/kaggle-api) for downloading the dataset (optional)

You can install the required Python packages using `pip`:

## Usage

1. Clone this repository: git clone https://github.com/shravan-18/Toxic-Comment-Classification.git
2. Navigate to the project directory: cd Toxic-Comment-Classification
3. Download the Kaggle dataset (train.csv, test_labels.csv and test.csv) and place them in the project's root directory.
4. Open and run the Jupyter Notebook or Python scripts to train and evaluate different NLP models for toxic comment classification.

## Models and Approaches

- We use Natural Language Processing to process the comments and use Neural Networks to train the data for classification
- Neural Network Layers - Embedded, Bidirectional, LSTM and Dense Layers
- NLP - Text Vectorization

## Evaluation

- Model results at the end of 5 epochs - train_loss: 0.0493 and val_loss: 0.0477
- Test results:
      Recall: 0.706926167011261
      Accuracy: 0.9825831651687622
      Categorical Accuracy: 0.7331995964050293

## Contributing

Contributions and improvements are welcome! If you'd like to contribute to this project, please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them to your branch.
4. Create a pull request with a clear description of your changes.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- Kaggle for providing the Toxic Comment Classification Challenge dataset.
- [Nicholas Renotte] (https://www.youtube.com/watch?v=ZUqB-luawZg&list=PLgNJO2hghbmiXg5d4X8DURJP9yv9pgjIu&index=5) for the inspiring tutorial.
- [https://github.com/nicknochnack]

Feel free to reach out if you have any questions or suggestions!
