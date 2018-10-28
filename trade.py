from datetime import datetime


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



class trade:
    def __init__(self):
       # parameters
       self.rate_volatility = 0.0
       self.rate = "non"
#       now=datetime.now()
#       self.day    = now.strftime('%d')
#       self.hour   = now.strftime('%h')
#       self.minute = now.strftime('%m')

       self.leverage = 25 #un used

       self.day    = "non"
       self.hour   = "non"
       self.minute = "non"

       self.longpos = long_position()
       self.shortpos = short_position()
       self.cash  = 500000.0
       self.cash_init = self.cash
       
       self.max_amount = 10

       self.enable_actions = (0, 1, 2)

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
       self.longpos.update_unrealized_profit(self.rate)
       self.shortpos.update_unrealized_profit(self.rate)
       cash_preaction = self.cash

       if action == self.enable_actions[1]:
         #print("long")
         if self.longpos.amount < self.max_amount:
            # long
            if (self.shortpos.amount - posnum) >= 0:
                #short port settlement
                self.cash += self.shortpos.settle(posnum)
            else:
                #short all settlement
                if self.shortpos.amount > 0:
                    self.longpos.get(self.rate, (posnum - self.shortpos.amount))
                    self.cash += self.shortpos.settle(posnum)
                #get long pos
                else:
                    self.longpos.get(self.rate, posnum)
                    self.cash -= posnum * 90  #trade_loss

       elif action == self.enable_actions[2]:
         #print("short")
         if self.shortpos.amount < self.max_amount:
            # short
            if (self.longpos.amount - posnum) >= 0:
                #long port settlement
                self.cash += self.longpos.settle(posnum)
            else:
                #long all settlement
                if self.longpos.amount > 0:
                    self.shortpos.get(self.rate, posnum - self.longpos.amount)
                    self.cash += self.longpos.settle(posnum)
                #get short pos
                else:
                    self.shortpos.get(self.rate, posnum)
                    self.cash -= posnum * 90  #trade_loss
       else:
         # do nothing
         #print("NANI MO SINAI!!")
         pass
       
       self.reward = 0
       self.reward = self.cash - self.cash_init + self.shortpos.unrealized_profit + self.longpos.unrealized_profit

    def updateTime(self, day, hour, minute):
       self.day    = day
       self.hour   = hour
       self.minute = minute

    def updateRate(self, rate):
       if self.rate != "non":
           self.rate_volatility = rate - self.rate
       self.rate = rate

    def dispState(self):
        print(self.day,".",self.hour,":",self.minute, ", ",   "cash:", self.cash)
        print(" long :","pos=", self.longpos.amount, ",\trate=", self.longpos.acquisition_rate,"\tinc_prft=", self.longpos.unrealized_profit )
        print(" short:","pos=", self.shortpos.amount, ",\trate=", self.shortpos.acquisition_rate,"\tinc_prft=", self.shortpos.unrealized_profit )
    
    def dispCash(self):
        print(str(int(self.day))+"."+str(int(self.hour))+":"+str(int(self.minute)), ", ",   "cash:", self.cash, "reword:",self.reward)
    
    def execute_action(self, action):
       self.updatePos(action)

    def observe(self):
       self.state = []
       self.state.append(self.rate_volatility) #0
       #self.state.append(self.day)             #1
       #self.state.append(self.hour)            #2
       #self.state.append(self.minute)          #3
       self.state.append(self.longpos.unrealized_profit)  #4
       self.state.append(self.shortpos.unrealized_profit) #5
       self.state.append(self.longpos.amount)             #6
       self.state.append(self.shortpos.amount)            #7
       return self.state, self.reward

    def reset(self):
       self.rate_volatility = 0.0
       self.longpos = long_position()
       self.shortpos = short_position()
       self.cash  = 500000.0
       self.cash_tmp = self.cash
       self.reward = 0.0

if __name__ == "__main__":
    tradeEnv = trade()
#    
#    tradeEnv.updateRate(112.262)
#    tradeEnv.updatePos(2, 1)
#    tradeEnv.dispState()
#    print("\n")
#    
#    tradeEnv.updateRate(112.162)
#    tradeEnv.updatePos(1, 3)
#    tradeEnv.dispState()
#    print("\n")
#    
#    tradeEnv.updateRate(112.222)
#    tradeEnv.updatePos(1, 5)
#    tradeEnv.dispState()
#    print("\n")
#    
#    tradeEnv.updateRate(112.362)
#    tradeEnv.updatePos(2, 10)
#    tradeEnv.dispState()
#    print("\n")
#    
#    tradeEnv.updateRate(112.125)
#    tradeEnv.updatePos(2, 3)
#   tradeEnv.dispState()
#    print("\n")

#    tradeEnv.updateRate(112.262)
#    tradeEnv.updatePos(1, 10)
#    tradeEnv.dispState()
#    print("\n")

#    tradeEnv.updateRate(112.362)
#    tradeEnv.updatePos(2, 10)
#    tradeEnv.dispState()
#    print("\n")
