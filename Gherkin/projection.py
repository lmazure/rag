import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def get_vectors_from_chroma(collection):
    """
    Retrieve vectors from a ChromaDB collection.
    
    Args:
        collection: ChromaDB collection object
    
    Returns:
        numpy.ndarray: Matrix of vectors
    """
    # Get all items from the collection
    results = collection.get()
    
    # Extract embeddings
    vectors = np.array(results['embeddings'])
    return vectors

def project_vectors(vectors, n_components=2):
    """
    Project vectors to lower dimension using PCA.
    
    Args:
        vectors (numpy.ndarray): Original high-dimensional vectors
        n_components (int): Target dimension (1, 2, or 3)
    
    Returns:
        numpy.ndarray: Projected vectors
        float: Explained variance ratio
    """
    # Initialize PCA
    pca = PCA(n_components=n_components)
    
    # Fit and transform the vectors
    projected_vectors = pca.fit_transform(vectors)
    
    # Calculate total explained variance
    explained_variance = np.sum(pca.explained_variance_ratio_)
    
    return projected_vectors, explained_variance

def visualize_projections(vectors, labels=None):
    """
    Create visualizations for 1D, 2D, and 3D projections.
    
    Args:
        vectors (numpy.ndarray): Original high-dimensional vectors
        labels (list): Optional labels for each point
    """
    fig = plt.figure(figsize=(15, 5))
    
    # 1D Projection
    projected_1d, var_1d = project_vectors(vectors, n_components=1)
    ax1 = fig.add_subplot(131)
    ax1.scatter(projected_1d, np.zeros_like(projected_1d), alpha=0.5)
    ax1.set_title(f'1D Projection\nExplained Variance: {var_1d:.2%}')
    ax1.set_xlabel('First Principal Component')
    ax1.set_yticks([])
    
    # 2D Projection
    projected_2d, var_2d = project_vectors(vectors, n_components=2)
    ax2 = fig.add_subplot(132)
    scatter = ax2.scatter(projected_2d[:, 0], projected_2d[:, 1], alpha=0.5)
    ax2.set_title(f'2D Projection\nExplained Variance: {var_2d:.2%}')
    ax2.set_xlabel('First Principal Component')
    ax2.set_ylabel('Second Principal Component')
    
    # 3D Projection
    projected_3d, var_3d = project_vectors(vectors, n_components=3)
    ax3 = fig.add_subplot(133, projection='3d')
    scatter = ax3.scatter(
        projected_3d[:, 0],
        projected_3d[:, 1],
        projected_3d[:, 2],
        alpha=0.5
    )
    ax3.set_title(f'3D Projection\nExplained Variance: {var_3d:.2%}')
    ax3.set_xlabel('First Principal Component')
    ax3.set_ylabel('Second Principal Component')
    ax3.set_zlabel('Third Principal Component')
    
    # Add labels if provided
    if labels is not None:
        for i, label in enumerate(labels):
            if ax2:
                ax2.annotate(label, (projected_2d[i, 0], projected_2d[i, 1]))
            if ax3:
                ax3.text(
                    projected_3d[i, 0],
                    projected_3d[i, 1],
                    projected_3d[i, 2],
                    label
                )
    
    plt.tight_layout()
    plt.show()

# Example usage:
def main():
    import chromadb
    
    # Initialize ChromaDB client
    client = chromadb.Client()
    
    # Get your collection
    collection = client.get_collection("your_collection_name")
    
    # Get vectors from collection
    vectors = get_vectors_from_chroma(collection)
    
    # Optional: Get metadata or IDs to use as labels
    results = collection.get()
    labels = results['ids']  # or use metadata fields
    
    # Visualize projections
    visualize_projections(vectors, labels)

if __name__ == "__main__":
    main()
