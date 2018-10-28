import numpy as np
import csv
from trade import trade
from dqn_agent import DQNAgent
from datetime import datetime as dt

if __name__ == "__main__":
    # parameters
    n_epochs = 20

    # environment, agent
    env = trade()
    agent = DQNAgent(env.enable_actions)

    #histrical data
    f = open('data\USDJPY1_20181016.csv', 'r')
    reader = csv.reader(f)
    header = next(reader)
    
    HisData=[]
    for row in reader:
        HisData.append(row)
    
    # variables
    prft=0
    for e in range(n_epochs):
        cnt=0
        loss=0
        frame=0
        env.reset()
        for row in HisData:
            env.updateRate(float(row[5]))  #candle_foot_end
            YmdHM = row[0] + "-" + row[1]
            tm = dt.strptime(YmdHM, '%Y.%m.%d-%H:%M')
            env.updateTime(float(tm.day), float(tm.hour), float(tm.minute))  #day, hour, min
            state_t_1, reward_t = env.observe()

            state_t = state_t_1
            # execute action in environment
            action_t = agent.select_action(state_t, agent.exploration)
            env.execute_action(action_t)
            # observe environment
            #state_t_1, reward_t = env.observe()

            # store experience
            agent.store_experience(state_t, action_t, reward_t, state_t_1)

            # experience replay
            agent.experience_replay()
            
            #log
            loss += agent.current_loss
            frame +=1
            #env.dispState()
            #env.dispCash()
        
        agent.learning_rate /= 1.01
        prft+=env.reward
        # for log
        print("epoch:",e,",\t profit:",'{:.2f}'.format(env.reward),"\t loss=", '{:.2f}'.format(loss/frame) ) #  ??? "\t prft_avr:", prft/(e+1)
        

    # save model
    agent.save_model()
