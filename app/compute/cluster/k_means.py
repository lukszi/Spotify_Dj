import numpy as np


def k_means(data: np.array, k, max_iter=1000):
    # dimensions of data
    n, m = data.shape
    # create random centroids
    centroids = data[np.random.choice(n, k, replace=False)]
    # create labels
    labels = np.zeros(n, dtype=int)
    prev_labels = np.zeros(n)

    for _ in range(max_iter):
        # assign each data point to the closest centroid
        for i in range(n):
            labels[i] = np.argmin(np.linalg.norm(centroids - data[i], axis=1))

        # if labels haven't changed, break
        if np.all(labels == prev_labels):
            break
        prev_labels = labels.copy()

        # update centroids
        for i in range(k):
            centroids[i] = np.mean(data[labels == i], axis=0)

    return centroids, labels


def calculate_silhouette_score(data: np.array, labels: np.array, centroids: np.array) -> float:
    average_intra_cluster_distances = np.zeros(len(centroids))
    for i in range(len(centroids)):
        average_intra_cluster_distances[i] = np.mean(np.linalg.norm(data[labels == i] - centroids[i], axis=1))

    average_inter_cluster_distances = np.zeros(len(centroids))
    for i in range(len(centroids)):
        other_centroids = np.delete(centroids, i, axis=0)
        average_inter_cluster_distances[i] = np.mean(np.linalg.norm(other_centroids - centroids[i], axis=1))

    _average_inter_cluster_distance = b = np.mean(average_inter_cluster_distances)
    _average_intra_cluster_distances = a = np.mean(average_intra_cluster_distances)
    score = (b - a) / max(a, b)
    return score


def find_optimal_k_means_clusters(data: np.array, max_clusters=10) -> (np.array, np.array):
    """
    Find the optimal number of clusters using the silhouette score
    :param data: the data to cluster
    :param max_clusters: the maximum number of clusters to try
    :return the labels of a clustering with the optimal number of clusters
    """
    best_score = -1
    best_centroids = None
    best_labels = None
    for k in range(2, max_clusters+1):
        print(f"Trying {k} clusters")
        centroids, labels = k_means(data, k)
        score = calculate_silhouette_score(data, labels, centroids)
        if score > best_score:
            best_score = score
            best_centroids = centroids
            best_labels = labels
    return best_centroids, best_labels
