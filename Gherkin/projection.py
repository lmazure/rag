import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import chromadb

def get_vectors_from_chroma(collection):
    """
    Retrieve vectors from a ChromaDB collection.
    
    Args:
        collection: ChromaDB collection object
    
    Returns:
        numpy.ndarray: Matrix of vectors
    """
    # Get all items from the collection
    results = collection.get(include=['embeddings'])
    
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
    Create visualizations for 1D, 2D, and 3D projections, each in a separate figure.
    
    Args:
        vectors (numpy.ndarray): Original high-dimensional vectors
        labels (list): Optional labels for each point
    """
    print(f"vectors: {vectors.shape}", flush=True)
    
    # 1D Projection
    plt.figure(figsize=(12, 8))
    projected_1d, var_1d = project_vectors(vectors, n_components=1)
    plt.scatter(projected_1d, np.zeros_like(projected_1d), alpha=0.5)
    plt.title(f'1D Projection\nExplained Variance: {var_1d:.2%}')
    plt.xlabel('First Principal Component')
    plt.yticks([])
    
    # 2D Projection
    plt.figure(figsize=(12, 8))
    projected_2d, var_2d = project_vectors(vectors, n_components=2)
    plt.scatter(projected_2d[:, 0], projected_2d[:, 1], alpha=0.5)
    plt.title(f'2D Projection\nExplained Variance: {var_2d:.2%}')
    plt.xlabel('First Principal Component')
    plt.ylabel('Second Principal Component')
    if labels is not None:
        for i, label in enumerate(labels):
            plt.annotate(label, (projected_2d[i, 0], projected_2d[i, 1]))
    
    # 3D Projection
    fig = plt.figure(figsize=(12, 8))
    projected_3d, var_3d = project_vectors(vectors, n_components=3)
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(
        projected_3d[:, 0],
        projected_3d[:, 1],
        projected_3d[:, 2],
        alpha=0.5
    )
    ax.set_title(f'3D Projection\nExplained Variance: {var_3d:.2%}')
    ax.set_xlabel('First Principal Component')
    ax.set_ylabel('Second Principal Component')
    ax.set_zlabel('Third Principal Component')
    if labels is not None:
        for i, label in enumerate(labels):
            ax.text(
                projected_3d[i, 0],
                projected_3d[i, 1],
                projected_3d[i, 2],
                label
            )
    
    plt.show()

# Example usage:
def main():    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path="./chromadb/database")
    
    # Get your collection
    collection = client.get_collection("all-MiniLM-L6-v2-Outcome")
    
    # Get vectors from collection
    vectors = get_vectors_from_chroma(collection)
    
    # Optional: Get metadata or IDs to use as labels
    results = collection.get()
    labels = results['documents']  # or use metadata fields
    
    # Visualize projections
    visualize_projections(vectors, labels)

if __name__ == "__main__":
    main()
