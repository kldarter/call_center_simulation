# call_center_simulation

## TO DO
- [ ] update run_sim file with explanations
- [ ] add ipysheet widget for user input
- [ ] create multiple runs to compare multiple scenarios
- [ ] add graphic output with histograms
- [ ] put descriptions in new readme for running program
- [X] make repo public
- [X] check program from work laptop for changes (initial calls?)
- [X] trim variables being passed into functions
- [X] put functions into class except for run simulation
- [X] make print output part of run simulation function
- [X] output takes labels from tier values
- [X] generalize labels and comments to remove MSCC language
- [X] get rid of pandas error message
- [X] comment all code
- [X] put in jupyter notebook for users to run
- [X] add requirements.txt file


Call Center Simulation

The Call Center has a limited number of agents and defines a call processes that takes some (random) time. 
Callers arrive at the Call Center at a random time and request an agent.
If one agent is available, they start the call process and wait for it to finish. 
If not, the caller waits until agent is available or their patience runs out.
