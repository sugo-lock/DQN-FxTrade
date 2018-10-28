from __future__ import division

import argparse
import os
import csv
from trade import trade
import matplotlib.pyplot as plt
from dqn_agent import DQNAgent
from datetime import datetime as dt

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

    # environmet, agent
    env = trade()
    agent = DQNAgent(env.enable_actions)
    agent.load_model(args.model_path)

    # variables
    state_t_1, reward_t = env.observe()

    #historucal data
    f = open('./data/USDJPY1_201805-201810.csv', 'r')
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
        state_t_1, reward_t = env.observe()
        
        state_t = state_t_1
        # execute action in environment
        action_t = agent.select_action(state_t, agent.exploration)
        env.execute_action(action_t)

        #log
        env.dispState()