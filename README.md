# call_center_simulation

## TO DO
- [ ] put in jupyter notebook for users to run
- [ ] add requirements.txt file
- [ ] create runs to compare multiple scenarios
- [ ] add graphic output with histograms
- [ ] put descriptions in new readme for running program
- [ ] make repo public
- [X] check program from work laptop for changes (initial calls?)
- [X] trim variables being passed into functions
- [X] put functions into class except for run simulation
- [X] make print output part of run simulation function
- [X] output takes labels from tier values
- [X] generalize labels and comments to remove MSCC language
- [X] get rid of pandas error message
- [X] comment all code


Call Center Simulation

Scenario:
  The Call Center has a limited number of agents and defines
  a call processes that takes some (random) time.

  Callers arrive at the Call Center at a random time. If one
  agent is available, they start the call process and wait for it
  to finish. If not, the caller waits until agent is available.

The Call Center has a limited number of agents to answer 
    calls in parallel

    Callers have to request one of the agents. When they got one, they
    can start the call processes and wait for it to finish.

The call process - caller arrives at the CC
    and requests an agent.

    It then starts the call process, waits for it to finish and
    leaves.
