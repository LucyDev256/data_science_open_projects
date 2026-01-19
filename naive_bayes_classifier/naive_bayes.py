"""
Naive Bayes Classifier Implementation

This module provides a complete implementation of the Naive Bayes classifier
from scratch using NumPy.

Based on the tutorial from: https://github.com/taspinar/siml
"""

from collections import Counter, defaultdict
import numpy as np


class NaiveBaseClass:
    """Base class with utility methods for Naive Bayes classifier."""
    
    def calculate_relative_occurences(self, list1):
        """
        Calculate relative frequencies of elements in a list.
        
        Args:
            list1: List of elements
            
        Returns:
            Dictionary mapping each unique element to its relative frequency
        """
        no_examples = len(list1)
        ro_dict = dict(Counter(list1))
        for key in ro_dict.keys():
            ro_dict[key] = ro_dict[key] / float(no_examples)
        return ro_dict

    def get_max_value_key(self, d1):
        """
        Get the key with the maximum value in a dictionary.
        
        Args:
            d1: Dictionary with numeric values
            
        Returns:
            Key corresponding to the maximum value
        """
        values = list(d1.values())
        keys = list(d1.keys())
        max_value_index = values.index(max(values))
        max_key = keys[max_value_index]
        return max_key
       
    def initialize_nb_dict(self):
        """Initialize the Naive Bayes dictionary structure for all labels."""
        self.nb_dict = {}
        for label in self.labels:
            self.nb_dict[label] = defaultdict(list)


class NaiveBayes(NaiveBaseClass):
    """
    Naive Bayes Classifier.
    
    This classifier is trained with a 2D array X (dimensions m,n) and a 1D array Y 
    (dimension m). X should have one column per feature (total n) and one row per 
    training example (total m).
    
    After training, a hash table is filled with the class probabilities per feature.
    
    Example:
        >>> import numpy as np
        >>> X = np.array([['sunny', 'hot'], ['rain', 'cold'], ['rain', 'cold']])
        >>> Y = np.array(['no', 'yes', 'yes'])
        >>> nb = NaiveBayes()
        >>> nb.train(X, Y)
        >>> prediction = nb.classify_single_elem(['rain', 'cold'])
        >>> print(prediction)
        'yes'
    """
    
    def train(self, X, Y):
        """
        Train the Naive Bayes classifier on the given data.
        
        Args:
            X: 2D numpy array of shape (m, n) where m is the number of examples
               and n is the number of features
            Y: 1D numpy array of shape (m,) containing the class labels
        """
        self.labels = np.unique(Y)
        no_rows, no_cols = np.shape(X)
        self.initialize_nb_dict()
        self.class_probabilities = self.calculate_relative_occurences(Y)
        
        # Iterate over all classes
        for label in self.labels:
            # Get indices for this class
            row_indices = np.where(Y == label)[0]
            X_ = X[row_indices, :]

            # Collect all feature values for this class
            no_rows_, no_cols_ = np.shape(X_)
            for jj in range(0, no_cols_):
                self.nb_dict[label][jj] += list(X_[:, jj])

        # Transform to relative frequencies
        for label in self.labels:
            for jj in range(0, no_cols):
                self.nb_dict[label][jj] = self.calculate_relative_occurences(
                    self.nb_dict[label][jj]
                )

    def classify_single_elem(self, X_elem):
        """
        Classify a single data point.
        
        Args:
            X_elem: Array-like of feature values
            
        Returns:
            Predicted class label
        """
        Y_dict = {}
        # Determine class probability for each class
        for label in self.labels:
            class_probability = self.class_probabilities[label]
            for ii in range(0, len(X_elem)):
                relative_feature_values = self.nb_dict[label][ii]
                if X_elem[ii] in relative_feature_values.keys():
                    class_probability *= relative_feature_values[X_elem[ii]]
                else:
                    # Feature value not seen in training for this class
                    class_probability *= 0
            Y_dict[label] = class_probability
        return self.get_max_value_key(Y_dict)
    
    def classify(self, X_test):
        """
        Classify multiple data points.
        
        Args:
            X_test: 2D numpy array of shape (m, n) containing test examples
            
        Returns:
            1D numpy array of predicted class labels
        """
        predictions = []
        for i in range(X_test.shape[0]):
            predictions.append(self.classify_single_elem(X_test[i]))
        return np.array(predictions)


if __name__ == "__main__":
    # Example usage and testing
    print("Naive Bayes Classifier - Example")
    print("=" * 60)
    
    # Create sample weather dataset for playing tennis
    X_train = np.array([
        ['sunny', 'hot', 'high', 'weak'],
        ['sunny', 'hot', 'high', 'strong'],
        ['overcast', 'hot', 'high', 'weak'],
        ['rain', 'mild', 'high', 'weak'],
        ['rain', 'cool', 'normal', 'weak'],
        ['rain', 'cool', 'normal', 'strong'],
        ['overcast', 'cool', 'normal', 'strong'],
        ['sunny', 'mild', 'high', 'weak'],
        ['sunny', 'cool', 'normal', 'weak'],
        ['rain', 'mild', 'normal', 'weak'],
        ['sunny', 'mild', 'normal', 'strong'],
        ['overcast', 'mild', 'high', 'strong'],
        ['overcast', 'hot', 'normal', 'weak'],
        ['rain', 'mild', 'high', 'strong']
    ])
    
    Y_train = np.array(['no', 'no', 'yes', 'yes', 'yes', 'no', 'yes', 
                         'no', 'yes', 'yes', 'yes', 'yes', 'yes', 'no'])
    
    # Train classifier
    nb = NaiveBayes()
    nb.train(X_train, Y_train)
    
    print("Training completed!")
    print(f"Classes: {nb.labels}")
    print(f"Class probabilities: {nb.class_probabilities}")
    
    # Test classification
    print("\nTesting classification:")
    test_samples = [
        ['sunny', 'cool', 'high', 'strong'],
        ['overcast', 'hot', 'normal', 'weak'],
        ['rain', 'mild', 'high', 'weak']
    ]
    
    for sample in test_samples:
        prediction = nb.classify_single_elem(sample)
        print(f"  {sample} -> {prediction}")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
