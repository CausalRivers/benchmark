import pickle
import sys
from pathlib import Path

import hydra
import networkx as nx
from omegaconf import DictConfig

sys.path.append("..")
from tools.graph_sampling_tools import add_one_random_node, combine_far_apart, get_all_sink_cases, get_all_subgraphs, get_longest_path, select_confounder_samples

# Here we generate all sub-sampling strategies that we evaluate and some additional ones.
# Additional ones might be added according to need.


# - Random connected
# - Confounding
# - sub-selection with high elevation (not used) or short distance between nodes (used for paper), .
# - All to one node (Sink) ( Not used for paper).
# - All in a line (Causal Ordering
# - One random node + connected graph
# - Disjoint groups


def load_pickle(path: str, verbose: bool = False) -> nx.Graph:
    """
    Loads a pickle file and tests the graph.
    Args:
        path (str): Path to the pickle file.
    Returns:
        nx.Graph: The loaded graph.
    """
    _path = Path(path)
    if not _path.exists():
        raise FileNotFoundError(f"File not found: {path}. Please check if you have downloaded the *product* dataset. Please check the readme!")

    if not _path.is_file():
        raise FileNotFoundError(f"Path is not a file: {path}. Please check if you have downloaded the *product* dataset. Please check the readme!")

    if not _path.suffix == ".p":
        raise FileNotFoundError(f"File is not a pickle file: {path}. Please check if you have downloaded the *product* dataset. Please check the readme!")

    try:
        G = pickle.load(open(_path, "rb"))
    except Exception as e:
        raise Exception(f"Error loading pickle file: {path}. Please check if you have downloaded the *product* dataset. Please check the readme!") from e

    if verbose:
        print(f"Nodes in G[{_path.name}]: {str(len(G.nodes))}")
        print(f"Edges in G[{_path.name}]: {str(len(G.edges))}")

    return G


def save_subgraphs_to_pickle(main_G: nx.Graph, sub_G: nx.Graph, name: str, save_path_structure: Path) -> None:
    """
    Save subgraphs of a main graph to a pickle file.
    This function takes a main graph and a subgraph, extracts the subgraphs from the main graph based on the nodes in the subgraph,
    and saves them to a pickle file.
    Args:
        main_G (nx.Graph): The main graph from which subgraphs will be extracted.
        sub_G (nx.Graph): The subgraph containing the nodes to extract from the main graph.
        name (str): The name to use for the pickle file.
        save_path_structure (Path): The directory path where the pickle file will be saved.
    Returns:
        None
    """
    try:
        pickle.dump([nx.subgraph(main_G, x).copy() for x in sub_G], open(save_path_structure / f"{name}.p", "wb"))
    except Exception as e:
        raise Exception(f"Error saving pickle file: {save_path_structure / f'{name}.p'}. Please check the readme!") from e


@hydra.main(version_base=None, config_path="config", config_name="data_sampling.yaml")
def main(cfg: DictConfig):
    """
    Main function to generate datasets based on different sampling strategies.
    Args:
        cfg (DictConfig): Configuration object containing the following attributes (please check the `config` folder):
            - test_G_path (str): Path to the test graph pickle file.
            - train_G_path (str): Path to the training graph pickle file.
            - flood_G_path (str): Path to the flood graph pickle file.
            - which (str): Specifies which sampling strategy to use. If "ALL", all strategies will be used.
            - n_vars (int): Number of variables (nodes) to consider for subgraph generation.
            - save_path (str): Directory path where the generated datasets will be saved.
            - dist_measure (str): Distance measure to use for the "close" sampling strategy.
            - max_distance (int): Maximum distance for the "close" sampling strategy.
            - g_per_sink (int): Restriction parameter for the "sink" sampling strategy.
    The function performs the following steps:
        1. Loads the graphs from the specified pickle files.
        2. Prints the number of nodes and edges in each graph.
        3. Determines the sampling strategies to use based on the configuration.
        4. Creates the save directory if it does not exist.
        5. Iterates over each sampling strategy and generates subgraphs accordingly.
        6. Saves the generated subgraphs as pickle files in the specified save directory.
    """

    east_G = load_pickle(cfg.test_G_path, verbose=True)
    bav_G = load_pickle(cfg.train_G_path, verbose=True)
    flood_G = load_pickle(cfg.flood_G_path, verbose=True)

    if cfg.which == "ALL":
        to_generate = []
        for x in [3, 5]:
            for y in ["debug_set", "random", "1_random", "root_cause", "confounder", "close"]:
                to_generate.append((y, x))
    else:
        to_generate = [(cfg.which, cfg.n_vars)]

    save_path = Path(cfg.save_path)
    save_path.mkdir(exist_ok=True, parents=True)

    print("-" * 50)
    print("Generating datasets for the following strategies:")
    for x in to_generate:
        print("\tStrategy: " + x[0] + " with " + str(x[1]) + " variables.")
    print("-" * 50)

    ##### Sampling strategies
    for structure, n_vars in to_generate:
        save_path_structure = save_path / f"{structure}_{n_vars}"
        save_path_structure.mkdir(exist_ok=True, parents=True)

        print("Generating dataset for: " + structure + " with " + str(n_vars) + " variables.")
        print("Save path: " + str(save_path_structure))

        match structure:
            case "debug_set":
                east, bav, flood = (get_all_subgraphs(x, n_vars=n_vars)[:5] for x in [east_G, bav_G, flood_G])

            case "random":
                east, bav, flood = (get_all_subgraphs(x, n_vars=n_vars) for x in [east_G, bav_G, flood_G])

            case "1_random":
                east, bav, flood = (get_all_subgraphs(x, n_vars=n_vars - 1) for x in [east_G, bav_G, flood_G])
                east = add_one_random_node(east_G, east)
                bav = add_one_random_node(bav_G, bav)
                flood = []

            case "root_cause":
                east, bav, flood = (get_all_subgraphs(x, n_vars=n_vars) for x in [east_G, bav_G, flood_G])
                east = [x for x in east if nx.dag_longest_path_length(east_G.subgraph(x)) == (n_vars - 1)]
                bav = [x for x in bav if nx.dag_longest_path_length(bav_G.subgraph(x)) == (n_vars - 1)]
                flood = [x for x in flood if nx.dag_longest_path_length(flood_G.subgraph(x)) == (n_vars - 1)]

            case "close":
                east, bav, flood = (get_all_subgraphs(x, n_vars=n_vars) for x in [east_G, bav_G, flood_G])
                east = [x for x in east if get_longest_path(nx.subgraph(east_G, x), measure=cfg.dist_measure) < cfg.max_distance]
                bav = [x for x in bav if get_longest_path(nx.subgraph(bav_G, x), measure=cfg.dist_measure) < cfg.max_distance]
                flood = [x for x in flood if get_longest_path(nx.subgraph(flood_G, x), measure=cfg.dist_measure) < cfg.max_distance]

            case "confounder":
                east = select_confounder_samples(east_G, n_vars)
                bav = select_confounder_samples(bav_G, n_vars)
                flood = select_confounder_samples(flood_G, n_vars)

            case "disjoint":
                print("subset size:" + str(int(n_vars / 2)))
                east, bav, flood = (get_all_subgraphs(x, n_vars=int(n_vars / 2)) for x in [east_G, bav_G, flood_G])
                east = combine_far_apart(east_G, east)
                bav = combine_far_apart(bav_G, bav)
                flood = combine_far_apart(flood_G, flood)

            case "sink":
                east, bav, flood = (get_all_sink_cases(x, n_vars=n_vars, restrict=cfg.g_per_sink) for x in [east_G, bav_G, flood_G])

            case _:
                raise NotImplementedError(f"Sampling strategy not implemented: {structure}")

        print("Number of subgraphs: " + str(len(east)))
        print("Number of subgraphs for finetuning: " + str(len(bav)))
        print("Number of subgraphs for flood area: " + str(len(flood)))

        save_subgraphs_to_pickle(east_G, east, "east", save_path_structure)
        save_subgraphs_to_pickle(bav_G, bav, "bav", save_path_structure)
        save_subgraphs_to_pickle(flood_G, flood, "flood", save_path_structure)


if __name__ == "__main__":
    main()
