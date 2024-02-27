"""
simulationsssssssssssssssssssssssssssssss
"""
      
from NPV import NPV
from NPV import NPV2
import numpy as np
import pandas as pd
import pickle as pkl
from scheduling_concatenate import scheduling_Y
from scheduling_concatenate import scheduling_M
import timeit

tic = timeit.default_timer()

res_npv = {}
res_sched = {}

# simulazioni 323
c_size = [80,135,205] # 3 cer
year = ['Low','High'] # 2 PUN
bess_cost = [200,400,600] # 3 costi batteria
bess_size = np.arange(20,320,20)
ACs = np.arange(5,55,5)

# input batteria
dod = 0.1
PC_ratio = 1
life_cicle = 8000
endlife = 0.8
calendar = 0.005
inc = 110

for strategy in [2]:
    
    for c in c_size:
        res_npv[c] = {}
        res_sched[c] = {}
        surplus_TX = np.array(pd.read_csv(f"100kWp {c}c surplus.csv")['Surplus MWh']) # MWh
        needs_TX = np.array(pd.read_csv(f"100kWp {c}c needs.csv")['Needs MWh']) # MWh
        
        for y in year:
            res_npv[c][y] = {}  
            res_sched[c][y] = {} 
            PUN_TX = pd.read_excel(f"{y}.xlsx")['PUN'].values # €/MWh
            
            for bs in bess_size:
                res_npv[c][y][bs] = {}
                res_sched[c][y][bs] = {}
                
                for ac in ACs:
                    print(f"c={c} y={y} bs={bs} ac={ac}")
                    res_npv[c][y][bs][ac] = {}
                    res_sched[c][y][bs][ac] = {}
                    
                    # annuale
                    cf,repl,soc,ea,csc = scheduling_Y(20,life_cicle,endlife,calendar,bs/1000,dod,PUN_TX,PC_ratio,ac,surplus_TX,needs_TX,inc,strategy=strategy)
                    #mensile
                    #cf,repl,soc,ea,csc = scheduling_M(20,life_cicle,endlife,calendar,bs/1000,dod,PUN_TX,PC_ratio,ac,surplus_TX,needs_TX,inc,strategy=strategy)


                    res_sched[c][y][bs][ac]['soc'] = soc
                    res_sched[c][y][bs][ac]['ea'] = ea
                    res_sched[c][y][bs][ac]['csc'] = csc              
                    
                    for bc in bess_cost:
                        I0 = bs*bc
                        
                        cf2 = cf -repl*I0 # aggiungo le sostituzioni
                        res_npv[c][y][bs][ac][bc] = {}
                        
                        i = 0.05
                        i =  (1 + i)**(1/12) - 1 # mensile
                        
                        # salvo i risultati
                        res_npv[c][y][bs][ac][bc]['NPV'] = NPV(I0,cf2,i)
                        res_npv[c][y][bs][ac][bc]['NPV2'] = NPV2(I0,cf2,i)
                    
                        
    with open(f"mensili npv {strategy}.pkl", 'wb') as f: pkl.dump(res_npv, f)   
    with open(f"mensili shced {strategy}.pkl", 'wb') as f: pkl.dump(res_sched, f) 
    
    # salva in pkl i risultati!!!
    toc = timeit.default_timer()
    print(f"{toc-tic} s")            

    
