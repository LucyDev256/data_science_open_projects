# Naive Bayes Classifier

This project implements a Naive Bayes Classifier from scratch using Python and NumPy.

## Overview

Naive Bayes is a probabilistic machine learning algorithm based on Bayes' theorem with strong (naive) independence assumptions between features. It's particularly effective for:
- Text classification
- Spam filtering
- Sentiment analysis
- Document categorization

## Contents

- **Naive_Bayes.ipynb**: Complete tutorial notebook explaining:
  - Introduction to classification problems
  - Mathematical theory behind Naive Bayes
  - Implementation from scratch
  - Step-by-step code walkthrough

## Key Concepts

The classifier uses Bayes' theorem to calculate posterior probabilities:

```
P(C|X) = P(X|C) * P(C) / P(X)
```

Where:
- `C` is the class label
- `X` is the feature vector
- `P(C|X)` is the posterior probability of class given the features

## Implementation

The implementation includes:
- `NaiveBaseClass`: Base class with utility methods
- `NaiveBayes`: Main classifier class with training and prediction methods

### Training
The classifier is trained with a 2D array X (features) and 1D array Y (labels), building a hash table of feature probabilities per class.

### Classification
New data points are classified by multiplying the conditional probabilities of each feature value per class and selecting the class with highest probability.

## Usage

Open the Jupyter notebook `Naive_Bayes.ipynb` to follow the complete tutorial with theory and implementation.

## Source

This implementation is based on the excellent tutorial from [taspinar/siml](https://github.com/taspinar/siml) repository.

## Requirements

- Python 3.x
- NumPy
- Jupyter Notebook

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install numpy jupyter notebook
```

## License

See the main repository LICENSE file.
