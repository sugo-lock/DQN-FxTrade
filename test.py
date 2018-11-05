from __future__ import division

import argparse
import os
import csv
from trade import trade
from dqn_agent import DQNAgent
from datetime import datetime as dt
from matplotlib import pyplot as plt
import math
import numpy as np

def init():
    img.set_array(state_t_1)
    plt.axis("off")
    return img,


#def animate(step):
#    global win, lose
#    global state_t_1, reward_t, terminal

#    if terminal:
#        env.reset()#
#
#        # for log
#        if reward_t == 1:
#            win += 1
#        elif reward_t == -1:
#            lose += 1

#        print("WIN: {:03d}/{:03d} ({:.1f}%)".format(win, win + lose, 100 * win / (win + lose)))

#    else:
#        state_t = state_t_1###

        # execute action in environment
#        action_t = agent.select_action(state_t, 0.0)
#        env.execute_action(action_t)
#
#    # observe environment
#    state_t_1, reward_t, terminal = env.observe()
#
#    # animate
#    img.set_array(state_t_1)
#    plt.axis("off")
#    return img,


if __name__ == "__main__":
    # args
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model_path")
    parser.add_argument("-s", "--save", dest="save", action="store_true")
    parser.set_defaults(save=False)
    args = parser.parse_args()

    #log
    fout = open('./logs/test_log.txt', 'w')
    
    # environmet, agent
    env = trade()
    #env.env="real"
    agent = DQNAgent(env.enable_actions)
    agent.load_model(args.model_path)

    # variables
    state_t_1, reward_t, terminal = env.observe()

    #historucal data
#    f = open('./data/USDJPY1_201805-201810.csv', 'r')
#    f = open('./data/USDJPY1_20181016_range.csv', 'r')
    f = open('./data/USDJPY1_20181004-1008.csv', 'r')
    reader = csv.reader(f)
    header = next(reader)

    HisData=[]
    for row in reader:
        HisData.append(row)
    
    #exec test
    for row in HisData:
        env.updateRate(float(row[5]))  #candle_foot_end
        YmdHM = row[0] + "-" + row[1]
        tm = dt.strptime(YmdHM, '%Y.%m.%d-%H:%M')
        env.updateTime(float(tm.day), float(tm.hour), float(tm.minute))  #day, hour, min
        
        if (len(env.ratebuff) == env.rate_buffsize):
            state_t_1, reward_t, terminal = env.observe()
            
            state_t = state_t_1
            # execute action in environment
            action_t = agent.select_action(state_t, 0.000)
            env.execute_action(action_t)

        #log file
        env.dispProfit()
        fout.write(row[5]+", "+str('{:.2f}'.format(env.cash - env.cash_init + env.longpos.unrealized_profit + env.shortpos.unrealized_profit))+'\n' )
        
        
        
   
    #log file
    fout.close()
    
    #graph
    rate, cash = np.loadtxt("./logs/test_log.txt", delimiter=',' ,unpack=True)
    fig = plt.figure(figsize=(8,6))
    ax1 = fig.add_subplot(211)
    ax1.plot(rate, "o-", color="r", label="rate")
    ax2 = fig.add_subplot(212)
    ax2.plot(cash, "o-", color="b", label="loss")
    plt.show()


        