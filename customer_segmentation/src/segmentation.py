"""
Customer Segmentation using K-Means Clustering

This script performs customer segmentation analysis using unsupervised learning.
It demonstrates data preprocessing, clustering, and visualization techniques.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')


class CustomerSegmentation:
    """
    A class for performing customer segmentation analysis.
    
    Attributes:
        n_clusters (int): Number of customer segments to create
        random_state (int): Random state for reproducibility
    """
    
    def __init__(self, n_clusters=4, random_state=42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.model = None
        self.scaler = StandardScaler()
        self.data = None
        self.scaled_data = None
        self.labels = None
        
    def load_data(self, filepath):
        """Load customer data from CSV file."""
        self.data = pd.read_csv(filepath)
        print(f"Data loaded: {self.data.shape[0]} customers, {self.data.shape[1]} features")
        return self.data
    
    def preprocess_data(self, features):
        """
        Preprocess data for clustering.
        
        Args:
            features (list): List of feature column names to use for clustering
        """
        # Select relevant features
        X = self.data[features].copy()
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        # Scale features
        self.scaled_data = self.scaler.fit_transform(X)
        print(f"Data preprocessed: {len(features)} features scaled")
        
        return self.scaled_data
    
    def find_optimal_clusters(self, max_clusters=10):
        """
        Find optimal number of clusters using elbow method and silhouette score.
        
        Args:
            max_clusters (int): Maximum number of clusters to test
        """
        inertias = []
        silhouette_scores = []
        
        for k in range(2, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            kmeans.fit(self.scaled_data)
            
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(self.scaled_data, kmeans.labels_))
        
        # Plot elbow curve
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        ax1.plot(range(2, max_clusters + 1), inertias, marker='o')
        ax1.set_xlabel('Number of Clusters')
        ax1.set_ylabel('Inertia')
        ax1.set_title('Elbow Method')
        ax1.grid(True)
        
        ax2.plot(range(2, max_clusters + 1), silhouette_scores, marker='o', color='orange')
        ax2.set_xlabel('Number of Clusters')
        ax2.set_ylabel('Silhouette Score')
        ax2.set_title('Silhouette Score Analysis')
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig('results/visualizations/optimal_clusters.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Optimal clusters analysis completed")
        return inertias, silhouette_scores
    
    def fit(self):
        """Fit K-Means clustering model."""
        self.model = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            n_init=10
        )
        self.labels = self.model.fit_predict(self.scaled_data)
        self.data['Cluster'] = self.labels
        
        print(f"\nClustering completed with {self.n_clusters} clusters")
        print(f"Silhouette Score: {silhouette_score(self.scaled_data, self.labels):.3f}")
        print(f"Davies-Bouldin Index: {davies_bouldin_score(self.scaled_data, self.labels):.3f}")
        
        return self.labels
    
    def get_cluster_profiles(self):
        """Generate cluster profiles with summary statistics."""
        cluster_profiles = self.data.groupby('Cluster').agg({
            'Age': ['mean', 'std'],
            'Annual_Income': ['mean', 'std'],
            'Spending_Score': ['mean', 'std'],
            'Purchase_Frequency': ['mean', 'std']
        }).round(2)
        
        # Add cluster sizes
        cluster_sizes = self.data['Cluster'].value_counts().sort_index()
        
        print("\n=== Cluster Profiles ===")
        print(f"\nCluster Sizes:")
        for cluster, size in cluster_sizes.items():
            print(f"Cluster {cluster}: {size} customers ({size/len(self.data)*100:.1f}%)")
        
        print(f"\n{cluster_profiles}")
        
        # Save profiles
        cluster_profiles.to_csv('results/cluster_profiles.csv')
        
        return cluster_profiles
    
    def visualize_clusters(self):
        """Create visualizations of customer clusters."""
        # 2D scatter plot
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        # Income vs Spending Score
        scatter1 = axes[0, 0].scatter(
            self.data['Annual_Income'],
            self.data['Spending_Score'],
            c=self.labels,
            cmap='viridis',
            alpha=0.6,
            s=50
        )
        axes[0, 0].set_xlabel('Annual Income')
        axes[0, 0].set_ylabel('Spending Score')
        axes[0, 0].set_title('Income vs Spending Score')
        plt.colorbar(scatter1, ax=axes[0, 0], label='Cluster')
        
        # Age vs Spending Score
        scatter2 = axes[0, 1].scatter(
            self.data['Age'],
            self.data['Spending_Score'],
            c=self.labels,
            cmap='viridis',
            alpha=0.6,
            s=50
        )
        axes[0, 1].set_xlabel('Age')
        axes[0, 1].set_ylabel('Spending Score')
        axes[0, 1].set_title('Age vs Spending Score')
        plt.colorbar(scatter2, ax=axes[0, 1], label='Cluster')
        
        # Age vs Income
        scatter3 = axes[1, 0].scatter(
            self.data['Age'],
            self.data['Annual_Income'],
            c=self.labels,
            cmap='viridis',
            alpha=0.6,
            s=50
        )
        axes[1, 0].set_xlabel('Age')
        axes[1, 0].set_ylabel('Annual Income')
        axes[1, 0].set_title('Age vs Income')
        plt.colorbar(scatter3, ax=axes[1, 0], label='Cluster')
        
        # Purchase Frequency vs Spending Score
        scatter4 = axes[1, 1].scatter(
            self.data['Purchase_Frequency'],
            self.data['Spending_Score'],
            c=self.labels,
            cmap='viridis',
            alpha=0.6,
            s=50
        )
        axes[1, 1].set_xlabel('Purchase Frequency')
        axes[1, 1].set_ylabel('Spending Score')
        axes[1, 1].set_title('Purchase Frequency vs Spending Score')
        plt.colorbar(scatter4, ax=axes[1, 1], label='Cluster')
        
        plt.tight_layout()
        plt.savefig('results/visualizations/cluster_scatter_plots.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Visualizations saved to results/visualizations/")


def main():
    """Main execution function."""
    print("=" * 60)
    print("Customer Segmentation Analysis")
    print("=" * 60)
    
    # Initialize segmentation model
    segmentation = CustomerSegmentation(n_clusters=4, random_state=42)
    
    # Load data (Note: You'll need to generate sample data first)
    print("\nNote: Please ensure customer_data.csv exists in the data/ directory")
    print("You can generate sample data using the data generation script")
    
    try:
        # Load data
        data = segmentation.load_data('data/customer_data.csv')
        
        # Preprocess data
        features = ['Age', 'Annual_Income', 'Spending_Score', 'Purchase_Frequency']
        segmentation.preprocess_data(features)
        
        # Find optimal clusters
        print("\nFinding optimal number of clusters...")
        segmentation.find_optimal_clusters(max_clusters=10)
        
        # Fit clustering model
        print("\nFitting clustering model...")
        segmentation.fit()
        
        # Get cluster profiles
        segmentation.get_cluster_profiles()
        
        # Create visualizations
        print("\nGenerating visualizations...")
        segmentation.visualize_clusters()
        
        print("\n" + "=" * 60)
        print("Analysis completed successfully!")
        print("Check the results/ directory for outputs")
        print("=" * 60)
        
    except FileNotFoundError:
        print("\nError: customer_data.csv not found in data/ directory")
        print("Please generate sample data first using the data generation utilities")


if __name__ == "__main__":
    main()
