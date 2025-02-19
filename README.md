
# CausalRivers  
#### Scaling up benchmarking of causal discovery for real-world time-series



[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)

This is the official Repo of [CausalRivers](https://openreview.net/forum?id=wmV4cIbgl6), the largest real-world Causal Discovery benchmark for time series to this date.

![alt-text-1](graphics/teaser.webp "title-1") ![alt-text-2](graphics/teaser2.webp "title-2")




### Install
For the core benchmarking package simply run:
```
./install.sh
python 0_generate_datsets.py
```
Alternatively, you can execute the following commands: 
```
conda create -f benchmark_env.yml
wget https://github.com/CausalRivers/benchmark/releases/download/First_release/product.zip
unzip product
rm product.zip
python 0_generate_datsets.py
```



## Functionality:

This is the core benchmarking package, which only holds the core functionality and some tutorials on usage: 

- Tutorial on how to build your graph subset:  [Custom graph sampling](1_custom_graph_sampling.ipynb)
- Tutorial on how to use the benchmark most efficiently:  [Usage](2_tutorial_benchmarking.ipynb)
- Tutorial on how to subselect specific temporal windows with certain weather conditions: [Temporal selections](3_tutorial_subselect_weather_condition.ipynb)
- Some general display of dataset properties that might be interesting for users:  [Data distribution](4_data_distribution.ipynb)
- Graphical documentation as in our [Publication](https://openreview.net/pdf?id=wmV4cIbgl6):  [Graphics generation](graphics)


## Usage
```
Usecase if ready.
```

If you want to reproduce the experimental results further or compare your method under equal conditions, please clone: 
```
git clone https://github.com/CausalRivers/experiments
```

The experiments were conducted on a Slurm Cluster and via Hydra configurations. However, the script can also be used on a single machine.
We forward to the [Experimental Documentation](https://github.com/CausalRivers/benchmark/blob/main/experiments/README.md) for further information.


## High prio todos: 

- Script for data downloading if called (and generally fix install)
- Slim down the tools.
- Properly update the tutorials
- Tutorial on the standard usage (to equalize)


### Maintainers
[@GideonStein](https://github.com/Gideon-Stein).
[@Timozen](https://github.com/Timozen).








