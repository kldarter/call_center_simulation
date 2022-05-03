"""
MSCC Simulation

Scenario:
  The MSCC has a limited number of CSRs and defines
  a call processes that takes some (random) time.

  Callers arrive at the MSCC at a random time. If one CSR
  is available, they start the call process and wait for it
  to finish. If not, they wait until CSR is available.

"""
import random
import pandas as pd
import simpy
import numpy as np


class MSCC(object):
    """The MSCC has a limited number of CSRs to answer calls in parallel

    Callers have to request one of the CSRs. When they got one, they
    can start the call processes and ans for it to finish (which
    takes ``talk_time`` minutes).

    """
    def __init__(self, env, num_csrs):
        self.env = env
        self.csrs = []

        for num in num_csrs:
            self.csrs.append(simpy.Resource(env,num))

    def call(self, tier,df,tier_params):
        """The call processes. It takes a ``caller`` processes and answers it."""
        talk_time = np.random.normal(tier_params['Talk_mu'][tier],tier_params['Talk_std'][tier])
        if talk_time < 0:
            talk_time = 0
        hold_time = np.random.normal(tier_params['Hold_mu'][tier],tier_params['Hold_std'][tier])
        if hold_time <= 0:
            hold_time = 0
        wrap_time = np.random.normal(tier_params['Wrap_mu'][tier],tier_params['Wrap_std'][tier])
        if wrap_time <= 0:
            wrap_time = 0
        call_time = talk_time + hold_time + wrap_time
        df['Talk_Time'][tier] += talk_time
        df['Hold_Time'][tier] += hold_time
        df['Wrap_Time'][tier] += wrap_time
        df['Handled'][tier] += 1

        transfer_prob = random.random()
        if transfer_prob < tier_params['Transfer'][tier]:
            df['Transfer'][tier] += 1
        yield self.env.timeout(call_time)

def caller(env, tier, mscc,df,svc_lvl_thresh,tier_params,num_tiers):
    """The call process - caller arrives at the MSCC
    and requests a CSR.

    It then starts the call process, waits for it to finish and
    leaves.

    """

    start = env.now
    patience = np.random.normal(tier_params['Patience'][tier],60)
    if patience < 1:
        patience = 1
    
    # determine which CSR bucket answers call
    choice = tier

    for count in range(num_tiers-1,tier-1,-1):
        if (len(mscc.csrs[count].queue)==0):
            choice = count

        
    with mscc.csrs[choice].request() as request:
        results = yield request | env.timeout(patience)
        df['Offered'][tier] += 1
        end = env.now

        if request in results:
            df['Ans_Time'][tier] += (end-start)
            if (end-start) <= svc_lvl_thresh:
                df['Within_Svc_Lvl'][tier] += 1
            yield env.process(mscc.call(tier,df,tier_params))
        else:
            df['Abandon'][tier] += 1
    
def setup(env, num_csrs,t,df,svc_lvl_thresh,tier_params,num_tiers):
    """Create MSCC, a number of initial callers and keep creating callers
    approx. every ``t`` seconds."""
    mscc_sim = MSCC(env, num_csrs)

    i = 0
    while True:
        exp_t = random.expovariate(t)

        yield env.timeout(exp_t)
        i += 1
        tier_rand = random.random()
        
        tier = 0
        for count in range(num_tiers-1,-1,-1):
            if tier_rand < tier_params['Volume'][count]:
                tier = count

        env.process(caller(env, tier, mscc_sim,df,svc_lvl_thresh,tier_params,num_tiers))


def run_Simulation(sim_params,tier_params):

    Num_CSRs = tier_params['CSRs']


    T_INTER = sim_params['Arrivals'][0]
    SIM_TIME = sim_params['SIM_TIME'][0]
    svc_lvl_thresh = sim_params['svc_lvl_thresh'][0]
    NUM_SIMS = sim_params['NUM_SIMS'][0]
    i = 0
    master = {'Offered':[],'Handled':[],'Talk_Time':[],'Ans_Time':[],'Hold_Time':[],'Wrap_Time':[],'Transfer':[],'Abandon':[],'Within_Svc_Lvl':[],'Tier':[],'Iteration':[]}
    master_df = pd.DataFrame(master)
    num_tiers = (len(tier_params))
    s_val = [0] * num_tiers
    tiers = list(range(1,num_tiers+1))

    for i in range(NUM_SIMS):
        iters = [i] * num_tiers
        d = {'Offered':s_val,'Handled':s_val,'Talk_Time':s_val,'Ans_Time':s_val,'Hold_Time':s_val,'Wrap_Time':s_val,'Transfer':s_val,'Abandon':s_val,'Within_Svc_Lvl':s_val,'Tier':tiers,'Iteration':iters}
        df = pd.DataFrame(data=d)
        env = simpy.Environment()
        env.process(setup(env, Num_CSRs, T_INTER,df,svc_lvl_thresh,tier_params,num_tiers))
        env.run(until=SIM_TIME)
        master_df = pd.concat([master_df,df],ignore_index=True)
        i += 1

    master_df['Abndn_pct'] = master_df['Abandon']/master_df['Offered']
    master_df['Avg_Talk'] = master_df['Talk_Time']/master_df['Handled']
    master_df['Svc_Lvl'] = master_df['Within_Svc_Lvl']/master_df['Offered']
    master_df['ASA'] = master_df['Ans_Time']/master_df['Handled']

    return master_df

params_dict = {'Arrivals':1,'SIM_TIME':60*30,'svc_lvl_thresh':30,'NUM_SIMS':10}
sim_params = pd.DataFrame(params_dict,index=[0])
tier_params_dict = {'Tier':[1,2,3],'Talk_mu':[397,487,396],'Wrap_mu':[62,95,79],'Hold_mu':[83,97,87],'Talk_std':[60,79,90],'Wrap_std':[20,40,47],'Hold_std':[20,34,52],'Volume':[0.7,0.97,1],'Patience':[320,480,240],'Transfer':[0.3,0.22,0.34],'CSRs':[321,94,9]}
tier_params = pd.DataFrame(tier_params_dict)

results = run_Simulation(sim_params,tier_params)
#print(results)
print(results.groupby(['Tier']).mean())