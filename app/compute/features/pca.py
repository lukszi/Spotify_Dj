import numpy as np


def run_pca_and_reduce_dimensions(data: np.array, n_components: int) -> np.array:
    """
    Perform principal component analysis on the given data and reduce the dimensions
    :param data: the data to perform PCA on
    :param n_components: the number of components to keep
    :return: the reduced data
    """
    components = pca(data)
    return reduce_dimensions(data, components, n_components)


def pca(data: np.array) -> np.array:
    """
    Perform principal component analysis on the given data
    :param data: the data to perform PCA on
    :return: the principal components of the data
    """
    # Standardize the data
    data = data - np.mean(data, axis=0)
    # Calculate the covariance matrix
    covariance_matrix = np.cov(data, rowvar=False)
    # Calculate the eigenvectors and eigenvalues of the covariance matrix
    eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)
    # Sort the eigenvectors by eigenvalue
    sorted_indices = np.argsort(eigenvalues)[::-1]
    eigenvectors = eigenvectors[:, sorted_indices]
    # Return the principal components
    return eigenvectors


def reduce_dimensions(data: np.array, components: np.array, n_components: int) -> np.array:
    """
    Reduce the dimensions of the data using the given principal components
    :param data: the data to reduce
    :param components: eigenvectors of the covariance matrix sorted by eigenvalue
    :param n_components: the number of components to keep
    :return: the reduced data
    """
    eigenvector_subset = components[:, 0:n_components]
    return np.dot(eigenvector_subset.transpose(), data.transpose()).transpose()

