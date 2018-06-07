### Install

```shell
git clone 
cd simulation-2
```

### Prepare

This project requires `python3`, `python3-pip` and `python3-tk`. They could be installed using the command:

```shell
make prepare
```

Or as alternative:

```shell
sudo apt-get install python3
sudo apt-get install python3-tk
sudo apt-get install python3-pip
```

Now you need to install the python library using pip

```shell
make install
```

That simply performs `pip3 install -r requirements.txt`

If you really feel lucky you could skip this part and simply run the project using one rule of makefile. A subroutine will check the python version installed and will perform `make prepare` for you if no `python3` is found.

### Run

Many option are available to run the project. Type `make help` for a complete list

```
make help

\\ will output

make prepare
    prepare development environment, use only once
make install
    install all python requirements, use only once
make start
    start the simulation as in init.py
make start-fast
    start a fast simulation (results will be less accurate)
make start-normal
    start a default simulation (results can be considerate good)
make start-slow
    this is the best simulation (but it is really slow)
make start-verbose
    start the simulation with verbose flag
make start-debug
    start the simulation using a default test
make start-beautiful
    start the simulation in the browser with a user interface
make start-beautiful-debug
    start the simulation in the browser with a user interface and a default test
make model
    start the model
make analysis
    start the analysis of data
make start-all-in-one
    start a fast simulation then the model and at the end the analysis of data
```

### A fast simulation

The fastest way to test the project is by simply run `make start-all-in-one`

This will perform:
```shell
make check_version
make start-normal
make model
make analysis
```

That will be translated as:
#### make start-normal
```shell
python3 simulator -dt 1000 -r 10 -nodb
```
-*dt 1000*: Run a simulation using dynamic time flag on. This means that for every gamma the network will be simulated for `avg_inter_arrival_time * 1000` seconds.
-*-r 10*: Means 10 repetition for every gamma
-*-nodb*: Ignore debug flag. We are not debugging

The gammas will be the one in the `./simulator/init.py` file.

At the end a new file `stats_nodes.csv` will be created.
For a full list of options see: `simulator init` or run `python simulator --help`.

#### make model
```
python3 model
```
Will run the mathematical model in order to compute the steady state of every quantization matrix. At the end will create a `model.csv` file.

#### make analysis
```shell
python3 analysis
```
Will plot all the graph to analyze the simulation and the model using the file created. 


### Running out of time

Another way to test the project is by copying the `stats-nodes.csv` and `model.csv` in the csv folder and put it in the root folder. This file are the outputs of the simulator and the model.

Now it is possible to plot the graph using
```shell
make analysis
```
or
```shell
python3 analysis
```


### Advanced Configuration
It is possible to modify the `./simulator/init.py` file in order to change the parameters of the network such as: speed, nodes position, queue size, gamma values ... Please remember that this modification but could be rewritten by some script such as `make start-fast` so please use it in combination with: `make start` or `python3 simulator`.

### Testing
Also in the `./simulator/init.py` it is possible to test the network using the tests defined in `./simulator/test.py`. To test the network enable test flag!

Example of `init.py`:
```python
import test

[...]

DEBUG = 1
VERBOSE = 1

DEBUG_POINTS = test.NODE_3_NEAR_1_2

DEBUG_COUNT = [
  0,
  0,
  0
]

DEBUG_TRANSMISSION = test.DEBUG_TRANSMISSION_7
```

The file `test.py` will have:
```python
# Position (x,y) for every node
NODE_3_NEAR_1_2 = [
  (0.401, 0.387),
  (0.801, 0.387),
  (0.601, 0.387)
]

# Use this in combination with NODE_3_NEAR_1_2 meaning node 3 is near node 1 and 2 but 1 and 2 are far away
# Example   1 ------ 3 ------- 2
# Node3 transmits (from 0.1s to 0.2s)
# Node1 cannot transmit (is receaving) so delays his transmission
# Node2 cannot transmit (is receaving) so delays his transmission
# Node1 should start transmitting at time 0.2s
# Node2 should start transmitting at time 0.2s

# Transmissions from Node1 and Node2 should result in a collision
# Transmission from Node3 should be ok (no collision)

DEBUG_TRANSMISSION_7 = [
  [
    (0.15, 100000)
  ],
  [
    (0.13, 100000),
  ],
  [
    (0.10, 100000),
  ]
]
```
