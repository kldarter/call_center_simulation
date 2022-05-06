import random
import pandas as pd
import simpy
import numpy as np


class CC(object):
    def __init__(self, env, num_agents):
        self.env = env
        self.agents = []

        for num in num_agents:
            self.agents.append(simpy.Resource(env,num))

    def call(self, tier,df,tier_params):
        """The call processes. It takes a ``caller`` process and answers it."""
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

    def caller(self, tier, cc,df,svc_lvl_thresh,tier_params,num_tiers):
        start = self.env.now
        patience = np.random.normal(tier_params['Patience'][tier],60)
        if patience < 1:
            patience = 1
        
        # determine which CSR bucket answers call
        choice = tier

        for count in range(num_tiers-1,tier-1,-1):
            if (len(self.agents[count].queue)==0):
                choice = count

            
        with self.agents[choice].request() as request:
            results = yield request | self.env.timeout(patience)
            df['Offered'][tier] += 1
            end = self.env.now

            if request in results:
                df['Ans_Time'][tier] += (end-start)
                if (end-start) <= svc_lvl_thresh:
                    df['Within_Svc_Lvl'][tier] += 1
                yield self.env.process(cc.call(tier,df,tier_params))
            else:
                df['Abandon'][tier] += 1
    
    def setup(self, cc,t,df,svc_lvl_thresh,tier_params,num_tiers):
        """Create CC, a number of initial callers and keep creating callers
        approx. every ``t`` seconds."""

        total_agents = tier_params['Agents'].sum()
        initial_calls = round(total_agents*.95)
        i = 0
        for i in range(initial_calls):
            tier_rand = random.random()
            
            tier = 0
            for count in range(num_tiers-1,-1,-1):
                if tier_rand < tier_params['Volume'][count]:
                    tier = count
            df['Entered'][tier] += 1

            self.env.process(cc.caller(tier, cc,df,svc_lvl_thresh,tier_params,num_tiers))
            i += 1


        while True:
            exp_t = random.expovariate(t)

            yield self.env.timeout(exp_t)
            tier_rand = random.random()
            
            tier = 0
            for count in range(num_tiers-1,-1,-1):
                if tier_rand < tier_params['Volume'][count]:
                    tier = count
            df['Entered'][tier] += 1

            self.env.process(cc.caller(tier, cc,df,svc_lvl_thresh,tier_params,num_tiers))


def run_Simulation(sim_params,tier_params):

    num_agents = tier_params['Agents']


    T_INTER = sim_params['Arrivals'][0]
    SIM_TIME = sim_params['SIM_TIME'][0]
    svc_lvl_thresh = sim_params['svc_lvl_thresh'][0]
    NUM_SIMS = sim_params['NUM_SIMS'][0]
    i = 0
    master = {'Entered':[],'Offered':[],'Handled':[],'Talk_Time':[],'Ans_Time':[],'Hold_Time':[],'Wrap_Time':[],\
        'Transfer':[],'Abandon':[],'Within_Svc_Lvl':[],'Tier':[],'Iteration':[]}
    master_df = pd.DataFrame(master)
    num_tiers = (len(tier_params))
    s_val = [0] * num_tiers
    tiers = []
    for tier in (tier_params['Tier']):
        tiers.append(tier)

    for i in range(NUM_SIMS):
        iters = [i] * num_tiers
        d = {'Entered':s_val,'Offered':s_val,'Handled':s_val,'Talk_Time':s_val,'Ans_Time':s_val,'Hold_Time':s_val,'Wrap_Time':\
            s_val,'Transfer':s_val,'Abandon':s_val,'Within_Svc_Lvl':s_val,'Tier':tiers,'Iteration':iters}
        df = pd.DataFrame(data=d)
        env = simpy.Environment()
        mscc_sim = CC(env, num_agents)
        env.process(mscc_sim.setup(mscc_sim,T_INTER,df,svc_lvl_thresh,tier_params,num_tiers))
        env.run(until=SIM_TIME)
        master_df = pd.concat([master_df,df],ignore_index=True)
        i += 1

    master_df['Abndn_pct'] = master_df['Abandon']/master_df['Offered']
    master_df['Avg_Talk'] = master_df['Talk_Time']/master_df['Handled']
    master_df['Svc_Lvl'] = master_df['Within_Svc_Lvl']/master_df['Offered']
    master_df['ASA'] = master_df['Ans_Time']/master_df['Handled']

    print(master_df.groupby(['Tier']).mean())

    return master_df

sim_dict = {'Arrivals':1,'SIM_TIME':600,'svc_lvl_thresh':30,'NUM_SIMS':1}
sim_params = pd.DataFrame(sim_dict,index=[0])
tier_params_dict = {'Tier':['T1','T2','T3'],'Talk_mu':[397,487,396],'Wrap_mu':[62,95,79],'Hold_mu':[83,97,87],'Talk_std':[60,79,90],\
    'Wrap_std':[20,40,47],'Hold_std':[20,34,52],'Volume':[0.7,0.97,1],'Patience':[320,480,240],'Transfer':[0.3,0.22,0.34],'Agents':[321,94,9]}
tier_params = pd.DataFrame(tier_params_dict)

results = run_Simulation(sim_params,tier_params)
