import numpy as np


def expand_cluster(point: int, neighbours: list[int], cluster: int,
                   eps: float, min_pts: int,
                   adjacency_matrix: np.array, labels: np.array, visited: np.array):
    """
    Expand the cluster to include all points that are density-reachable from the core points
    """
    labels[point] = cluster
    while len(neighbours) > 0:
        neighbour = neighbours.pop(0)
        if not visited[neighbour]:
            visited[neighbour] = True
            new_neighbours = list(np.where(adjacency_matrix[neighbour] < eps)[0])
            if len(new_neighbours) >= min_pts:
                neighbours.extend(new_neighbours)
        if labels[neighbour] in [0, -1]:
            labels[neighbour] = cluster


def dbscan(adjacency_matrix: np.array, eps: float, min_pts: int) -> np.array:
    """
    Perform DBSCAN clustering on the given data
    :param adjacency_matrix: the data to cluster
    :param eps: the maximum distance between two samples for one to be considered as in the neighborhood of the other
    :param min_pts: the number of samples in a neighborhood for a point to be considered as a core point
    :return: an array of labels where -1 indicates noise, and 0 to n-1 are the cluster labels
    """
    n = len(adjacency_matrix)
    labels = np.zeros(n, dtype=int)
    visited = np.zeros(n, dtype=bool)
    cluster = 0
    while np.where(visited == False)[0].size > 0:
        # pick a random point
        point = np.random.choice(np.where(visited == False)[0])
        visited[point] = True

        neighbours = list(np.where(adjacency_matrix[point] < eps)[0])
        if len(neighbours) < min_pts:
            labels[point] = -1
        else:
            cluster += 1
            expand_cluster(point, neighbours, cluster, eps, min_pts, adjacency_matrix, labels, visited)
    return labels
