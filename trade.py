from datetime import datetime
import numpy as np

class trade_position:
    def __init__(self):
        self.amount = 0
        self.acquisition_rate = 0
        self.unrealized_profit = 0
        
    def get(self, rate, amount):
        if( ( amount!=0 ) | ( self.amount !=0 ) ):
            self.acquisition_rate = ( (self.amount * self.acquisition_rate) + (rate * amount) )/(self.amount + amount)
            self.amount += amount

class long_position(trade_position):
    def update_unrealized_profit(self, rate):
        self.unrealized_profit = (rate - self.acquisition_rate) * self.amount * 10000
        
    def settle(self, amount):
        if(amount < self.amount):
            profit = (amount/self.amount) * unrealized_profit
            self.unrealized_profit -= profit
            self.amount -= amount
        else:
            profit = self.unrealized_profit
            self.unrealized_profit = 0
            self.amount = 0
            self.acquisition_rate = 0
        return profit

class short_position(trade_position):
    def update_unrealized_profit(self, rate):
        self.unrealized_profit = (self.acquisition_rate - rate) * self.amount * 10000
        
    def settle(self, amount):
        if(amount < self.amount):
            profit = (amount/self.amount) * unrealized_profit
            self.unrealized_profit -= profit
            self.amount -= amount
        else:
            profit = self.unrealized_profit
            self.unrealized_profit = 0
            self.amount = 0
            self.acquisition_rate = 0
        return profit

###
def zscore(x):
    xmean = x.mean()
    xstd  = np.std(x)

    zscore = (x-xmean)/xstd
    return zscore
###


class trade:
    def __init__(self):
       # parameters
       self.rate_diff = 0.0
       self.rate = 0
       self.ratebuff = []
       self.ratebuff_zscore = []
       self.rate_buffsize = 16
#       now=datetime.now()
#       self.day    = now.strftime('%d')
#       self.hour   = now.strftime('%h')
#       self.minute = now.strftime('%m')

       self.leverage = 25 #un used

       self.day    = 0
       self.hour   = 0
       self.minute = 0

       self.env ="vertual" #"vertual" or "real"

       self.longpos = long_position()
       self.shortpos = short_position()
       self.cash  = 500000.0
       self.cash_init = self.cash
       
       self.max_amount = 10

       self.enable_actions = (0, 1, 2)

       self.terminal = 0
       self.reward = 0.0

    def updatePos(self, action, posnum = 10):
       """
       action:               
           0:do nothing
           1:long
           2:short
       posnum:0~10
       """
       #
       profit_tmp = self.cash - self.cash_init + self.shortpos.unrealized_profit + self.longpos.unrealized_profit
       
       self.longpos.update_unrealized_profit(self.rate)
       self.shortpos.update_unrealized_profit(self.rate)
       cash_preaction = self.cash
       self.terminal = 0
       
#       print("act:",action)
       
       if action == self.enable_actions[1]:
         #print("long")
         if self.longpos.amount < self.max_amount:
            # long
            if (self.shortpos.amount - posnum) >= 0:
                #short port settlement
                self.cash += self.shortpos.settle(posnum)
                self.terminal = 1
                if self.env != "vertual":
                    self.cash -= posnum * 90  #trade_loss  pt1
            else:
                #short all settlement
                if self.shortpos.amount > 0:
                    self.longpos.get(self.rate, (posnum - self.shortpos.amount))
                    self.cash += self.shortpos.settle(posnum)
                    self.terminal = 1
                    if self.env != "vertual":
                        self.cash -= posnum * 90  #trade_loss  pt1
                #get long pos
                else:
                    self.longpos.get(self.rate, posnum)
                    self.terminal = 0
                    if self.env != "vertual":
                        self.cash -= posnum * 90  #trade_loss  pt1

       elif action == self.enable_actions[2]:
         #print("short")
         if self.shortpos.amount < self.max_amount:
            # short
            if (self.longpos.amount - posnum) >= 0:
                #long port settlement
                self.cash += self.longpos.settle(posnum)
                self.terminal = 1
                if self.env != "vertual":
                    self.cash -= posnum * 90  #trade_loss  pt1
            else:
                #long all settlement
                if self.longpos.amount > 0:
                    self.shortpos.get(self.rate, posnum - self.longpos.amount)
                    self.cash += self.longpos.settle(posnum)
                    self.terminal = 1
                    if self.env != "vertual":
                        self.cash -= posnum * 90  #trade_loss  pt1
                #get short pos
                else:
                    self.shortpos.get(self.rate, posnum)
                    self.terminal = 0
                    if self.env != "vertual":
                        self.cash -= posnum * 90  #trade_loss pt1
       else:
         # do nothing
         #print("NANI MO SINAI!!")
         pass
       
       self.reward = 0
#       self.reward = self.cash - self.cash_init
       profit = self.cash - self.cash_init + self.shortpos.unrealized_profit + self.longpos.unrealized_profit
       self.reward = profit - profit_tmp

    def updateTime(self, day, hour, minute):
       self.day    = day
       self.hour   = hour
       self.minute = minute

    def updateRate(self, rate):
       self.rate = rate

       if (len(self.ratebuff)+1) > self.rate_buffsize:
           self.ratebuff.pop(0)  #pop index=0
       self.ratebuff.append(rate)
       
       self.ratebuff_zscore = zscore(np.array(self.ratebuff))
       self.ratebuff_zscore.tolist()

    def dispProfit(self):
        print(str(int(self.day))+"."+str(int(self.hour))+":"+str(int(self.minute))+", ",   "cash:", '{:.2f}'.format(self.cash), "in_prft: [L:",'{:.2f}'.format(self.longpos.unrealized_profit),"],[S",'{:.2f}'.format(self.shortpos.unrealized_profit),"]")
        #print(" long :","pos=", self.longpos.amount, ",\trate=", self.longpos.acquisition_rate,"\tinc_prft=", '{:.2f}'.format(self.longpos.unrealized_profit) )
        #print(" short:","pos=", self.shortpos.amount, ",\trate=", self.shortpos.acquisition_rate,"\tinc_prft=", '{:.2f}'.format(self.shortpos.unrealized_profit) )
    
    def dispCash(self):
        print(str(int(self.day))+"."+str(int(self.hour))+":"+str(int(self.minute)), ", ",   "cash:", self.cash, "reword:",self.reward)
    
    def execute_action(self, action):
       self.updatePos(action)

    def observe(self):
       self.state = []
       #self.state +=  self.ratebuff_zscore
       self.state = np.hstack((self.state, self.ratebuff_zscore))
       
#       self.state.append(self.rate_diff) #0
       #self.state.append(self.day)             #1
       #self.state.append(self.hour)            #2
       #self.state.append(self.minute)          #3
#       self.state.append(self.longpos.unrealized_profit)  #14
#       self.state.append(self.shortpos.unrealized_profit) #15
#       self.state.append(self.longpos.amount)             #
#       self.state.append(self.shortpos.amount)            #

       return self.state, self.reward, self.terminal

    def reset(self):
       self.rate_diff = 0.0
       self.ratebuff = []
       self.ratebuff_zscore = []
       self.longpos = long_position()
       self.shortpos = short_position()
       self.cash  = 500000.0
       self.cash_tmp = self.cash
       self.reward = 0.0

#if __name__ == "__main__":
#    tradeEnv = trade()
#    
#    tradeEnv.updateRate(112.262)
#    tradeEnv.updatePos(2, 1)
#    tradeEnv.dispProfit()
#    print("\n")
#    
#    tradeEnv.updateRate(112.162)
#    tradeEnv.updatePos(0, 3)
#    tradeEnv.dispProfit()
#    print("\n")
#    
#    tradeEnv.updateRate(112.222)
#    tradeEnv.updatePos(1, 5)
#    tradeEnv.dispProfit()
#    print("\n")
#    
#    tradeEnv.updateRate(112.362)
#    tradeEnv.updatePos(2, 10)
#    tradeEnv.dispProfit()
#    print("\n")
#    
#    tradeEnv.updateRate(112.125)
#    tradeEnv.updatePos(2, 3)
#   tradeEnv.dispProfit()
#    print("\n")

#    tradeEnv.updateRate(112.262)
#    tradeEnv.updatePos(1, 10)
#    tradeEnv.dispState()
#    print("\n")

#    tradeEnv.updateRate(112.362)
#    tradeEnv.updatePos(2, 10)
#    tradeEnv.dispProfit()
#    print("\n")
