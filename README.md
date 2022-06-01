# call_center_simulation

The Call Center has a limited number of agents and defines a call processes that takes some time. 
Callers arrive at the Call Center at a random time and request an agent.
If one agent is available, they start the call process and wait for it to finish. 
If not, the caller waits until agent is available or their patience runs out and they hang up.

The parameters define the set up of the call center (agents, call volume, etc) and the mean and standard deviation for the time agents spend on calls.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/kldarter/call_center_simulation/HEAD)

Files:
requirements.txt
run_sim.ipynb
simulation.py
Todo.md
