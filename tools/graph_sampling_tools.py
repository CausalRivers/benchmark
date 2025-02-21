__all__ = [
    "add_one_random_node",
    "combine_far_apart",
    "get_all_subgraphs",
    "get_all_sink_cases",
    "get_longest_path",
    "check_corr_character",
    "select_confounder_samples",
    "all_extensions",
]

import random
from itertools import combinations

import networkx as nx
import numpy as np


# TODO The sampling algorithms are inefficient for higher number of nodes. FIX this with proper algorithms.
# TODO Create a single random process for this tool to control the randomness -> reproducibility.
# TODO Add a seed to the random processes.


def add_one_random_node(G, candidates):
    """
    Adds a disconnected node from specified graph to every candidate.
    """
    new_samples = []
    # We add a random node with degree 0 (disconnected)
    possible_additions = list(nx.isolates(G))
    for sample in candidates:
        # draw random item from possible additions
        addition = random.choice(possible_additions)
        # check if this is connected (also if it is already included.)
        new_samples.append(tuple(list(sample) + [addition]))
    return new_samples


def combine_far_apart(G, candidates):
    """
    Selects 2 candidates to be joint to a single candidate by maximizing the geopgrapic means between them
    The aim is to make them completely disconnected in this way.
    TODO this needs an update. Inefficient.
    """
    new_samples = []
    geographic_means = []

    for sample in candidates:
        y = np.mean([G.nodes[x]["p"][0] for x in sample])
        x = np.mean([G.nodes[x]["p"][1] for x in sample])
        geographic_means.append(np.array([y, x]))

    for n, sample in enumerate(candidates):
        # search for the most distant:
        start = geographic_means[n]
        dist = 0
        current_best = None
        for m, point in enumerate(geographic_means):
            if np.mean((start - point) ** 2) > dist:
                dist = np.mean((start - point) ** 2)
                current_best = m
        new_samples.append(tuple(sorted(sample + candidates[current_best])))

    return set(new_samples)


def get_all_subgraphs(G: nx.Graph, n_vars: int = 5) -> list[set[int]]:
    """
    Samples all possible subgraphs with a specified number of nodes from a given graph.

    Parameters:
        G (nx.Graph): The input graph from which subgraphs are to be sampled.
        n_vars (int): The number of nodes each subgraph should contain. Default is 5.

    Returns:
        list (list[int]): A list of subgraphs, where each subgraph is represented as a list of node IDs.

    Notes:
        This function may produce suboptimal results and could be improved for efficiency.
        TODO update the graph sampling. Its suboptimal.
    """
    full_stack = []

    for start_node in list(G.nodes):
        no_graphs = False
        # graph stack holds all possible current extensions from the start node onwards.
        graph_stack = [[start_node]]
        for step in range(n_vars - 1):
            # checks for all possible extensions for all current subgraphs in the graph stack
            res = [item for sublist in [all_extensions(g, G) for g in graph_stack] for item in sublist]
            if len(res) > 0:
                # extensions
                graph_stack = res
            else:
                no_graphs = True

        if not no_graphs:
            full_stack.append(graph_stack)

    # There might be many double graphs so we remove them by
    # sorting ids and removing doubles via set.
    return list(set(tuple(sorted(i)) for i in [item for sublist in full_stack for item in sublist]))


def get_all_sink_cases(G, n_vars=12, restrict=15):
    """
    Gets all sink cases (All to one) for a given graph
    """
    full_stack = []
    for start_node in list(G.nodes):
        extensions = list(G.predecessors(start_node))
        if len(extensions) >= (n_vars - 1):
            all_samples = list(combinations(extensions, n_vars - 1))
            all_samples = [[start_node] + list(x) for x in all_samples]
            full_stack.append(all_samples[:restrict])
    return [item for sublist in full_stack for item in sublist]


def get_longest_path(sub_G, measure="km"):
    """
    Gets the longest distance of specified measurement of a given sample
    """
    lengths = []
    for start in sub_G.nodes:
        for end in sub_G.nodes:
            connections = list(nx.all_simple_edge_paths(sub_G, start, end))
            for x in connections:
                distances = [sub_G.edges[step[0], step[1]][measure] for step in x]
                if None in distances:
                    return np.inf
                else:
                    lengths.append(sum([sub_G.edges[step[0], step[1]][measure] for step in x]))
    return max(lengths)


def check_corr_character(sub_G, measure=[["lag_median", 10], ["lag_var", 1000]]):
    """
    Check if a candidate graph confirms with specified measurements.
    """
    for edge in sub_G.edges:
        info = sub_G.edges[edge]
        for category in measure:
            if not (info[category[0]] < category[1]):
                return False
    return True


def select_confounder_samples(G, n_vars):
    """
    Gets all samples from G where a single node has multiple sucessors and removes it.
    """
    conf = [x for x in G.nodes if len(list(G.successors(x))) > 1]
    potential_list = get_all_subgraphs(G, n_vars=n_vars)

    samples = []
    for con in conf:
        candidates = [x for x in potential_list if con in x]
        for succ in list(G.successors(con)):
            candidates = [x for x in candidates if succ in x]
        # remove confounder from set
        samples.append([tuple([y for y in x]) for x in candidates])
    samples = [item for sublist in samples for item in sublist]
    return samples


def all_extensions(current_G: nx.Graph, G: nx.Graph, succ: bool = True):
    """
    Adds all possible extension to a given graph sample based on the main graph.
    """
    extensions = []
    for node in current_G:
        # we all connected node we add a extended graph.
        [extensions.append(x) for x in list(G.predecessors(node)) if x not in current_G]

        if succ:
            [extensions.append(x) for x in list(G.successors(node)) if x not in current_G]
    return [current_G + [ex] for ex in set(extensions)]
