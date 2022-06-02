# call_center_simulation

This program runs a simulation of a call center.
The Call Center has a limited number of agents and defines a call processes that takes some time. 
Callers arrive at the Call Center at a random time and request an agent.
If one agent is available, they start the call process and wait for it to finish. 
If not, the caller waits until agent is available or their patience runs out and they hang up.
The simulation results include the abandon rate, the service level, and the average speed of answer.

The parameters define the set up of the call center (agents, call volume, etc) and the mean and standard deviation for the time agents spend on calls.

The simulation.py file contains the simulation object and functions to run and report results of the simulation.

The run_sim.ipynb jupyter notebook defines the simulation parameters and goes through the steps to run the simulation and can be run through mybinder here:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/kldarter/call_center_simulation/HEAD)

