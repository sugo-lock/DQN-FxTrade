import numpy as np
import csv
from trade import trade
from dqn_agent import DQNAgent
from datetime import datetime as dt

if __name__ == "__main__":
    # parameters
    n_epochs = 10000

    # environment, agent
    env = trade()
    agent = DQNAgent(env.enable_actions)

    #histrical data
    f = open('./data/USDJPY1_201810.csv', 'r')
    reader = csv.reader(f)
    header = next(reader)
    
    HisData=[]
    for row in reader:
        HisData.append(row)
    
    #log file
    fout = open('./logs/train_log.txt', 'w')
    
    # variables
    prft=0
    for e in range(n_epochs):
        cnt=0
        loss=0
        trade_cnt=0
        state_t = []
        env.reset()
        for row in HisData:
            env.updateRate(float(row[5]))  #candle_foot_end
            YmdHM = row[0] + "-" + row[1]
            tm = dt.strptime(YmdHM, '%Y.%m.%d-%H:%M')
            env.updateTime(float(tm.day), float(tm.hour), float(tm.minute))  #day, hour, min
            
            if (len(env.ratebuff_zscore) == env.rate_buffsize):
                # observe environme
                state_t_1, reward_t, terminal = env.observe()
                
                if state_t != []:
                    # execute action in environment
                    action_t = agent.select_action(state_t, agent.exploration)
                    env.execute_action(action_t)

                    # store experience
                    agent.store_experience(state_t, action_t, reward_t, state_t_1, terminal)

                    # experience replay
                    agent.experience_replay()
                    #log
                    loss += agent.current_loss
                    trade_cnt +=1
                    #env.dispProfit()
                    #env.dispCash()
                
                state_t = state_t_1
        agent.exploration /= ( (1 + n_epochs)/n_epochs)
        #agent.learning_rate /= ( (1 + n_epochs)/n_epochs)
        prft+=env.reward
        if trade_cnt != 0:
            loss_avr = '{:.2f}'.format(loss/trade_cnt)
        else:
            loss_avr = "non"
        # for log
#        print("epoch:",e,",\t cash:",'{:.2f}'.format(env.cash),",\t inprft:",'{:.2f}'.format(env.longpos.unrealized_profit+env.shortpos.unrealized_profit) ,"\t loss=", '{:.2f}'.format(loss/frame) ) #  ??? "\t prft_avr:", prft/(e+1)
        print("epoch:",e,",\t profit:",'{:.2f}'.format(env.cash - env.cash_init + env.shortpos.unrealized_profit + env.longpos.unrealized_profit),"\t loss=", loss_avr, "\ttrd_cnt:"+str(trade_cnt) ) #  ??? "\t prft_avr:", prft/(e+1)
        fout.write( str(loss_avr)+'\n' )

    # save model
    agent.save_model()
    
    #log file close
    fout.close()