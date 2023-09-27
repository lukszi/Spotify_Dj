from typing import List

import numpy as np
from python_tsp.heuristics import solve_tsp_local_search


def add_zero_vertex(song_adj_matrix: np.array):
    """
    Add a fully connected 0 distance vertex to the graph
    :param song_adj_matrix:
    :return: copy of song_adj_matrix with the added vertex
    """
    n = len(song_adj_matrix)
    new_matrix = np.zeros((n + 1, n + 1))
    new_matrix[:-1, :-1] = song_adj_matrix
    return new_matrix


def approximate_shp(song_adj_matrix: np.array) -> List[int]:
    """
    Approximate the shortest hamiltonian path by adding a fully connected 0 distance vertex to the graph
    and then solving the traveling salesman problem
    :param song_adj_matrix: The song adjacency matrix
    :return: The approximate shortest hamiltonian path as a list of indices
    """
    original_length = song_adj_matrix.shape[0]

    song_adj_matrix = add_zero_vertex(song_adj_matrix)
    permutation, distance = solve_tsp_local_search(song_adj_matrix, perturbation_scheme="ps5")

    # Remove the added vertex
    permutation = [i for i in permutation if i < original_length]
    return permutation
