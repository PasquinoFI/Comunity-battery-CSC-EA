"""
AC vs EA assessing
"""

from scheduling_model2 import scheduling_EA_CSC_TX
from scheduling_model2 import scheduling_EA_CSC
from scheduling_model2 import scheduling_EA_CSC2_TX
from scheduling_model2 import scheduling_EA_CSC2
from scheduling_model2 import scheduling_EA_CSC22
import numpy as np
import pandas as pd
from ageing_model import rainflow
import matplotlib.pyplot as plt

# input batteria
dod = 0.1
PC_ratio = 1
life_cicle = 8000
endlife = 0.7
calendar = 0.005
inc = 100

c_size = [80,135,205] # 3 cer
year = ['Low','High'] # 2 PUN
bess_cost = [200,400,600] # 3 costi batteria
bess_size = np.arange(20,320,20)
ACs = np.arange(5,55,5)
c_label = {80:'40 %', 135:'60 %', 205:'80 %'}
ss_label = {80:'38 %', 135:'34 %', 205:'30 %'}


c=80
y='Low'
C0=0.05
surplus_TX = np.array(pd.read_csv(f"100kWp {c}c surplus.csv")['Surplus MWh']) # MWh
needs_TX = np.array(pd.read_csv(f"100kWp {c}c needs.csv")['Needs MWh']) # MWh
PUN_TX = pd.read_excel(f"{y}.xlsx")['PUN'].values # €/MWh


csc = np.zeros(len(ACs))
ea = np.zeros(len(ACs))
nc = np.zeros(len(ACs))
acost = np.zeros(len(ACs))

for i,ac in enumerate(ACs):
    #soc_TX,profit_TX,CSC_TX,OeM_TX = scheduling_EA_CSC_TX(C0, C0*dod, C0*dod, PUN_TX, PC_ratio, ac,surplus_TX, inc, 24, 365)     
    soc_TX,profit_TX,CSC_TX,OeM_TX = scheduling_EA_CSC2_TX(C0, C0*dod, C0*dod, PUN_TX, PC_ratio, ac,surplus_TX, needs_TX, inc, 24, 365)     
    
    
    nc[i] = rainflow(soc_TX,C0)
    csc[i] = CSC_TX.sum()
    ea[i] = profit_TX.sum()
    acost[i] = OeM_TX.sum()
    
plt.figure(dpi=1000)
plt.plot(ACs,csc,label='CSC')
plt.plot(ACs,ea,label='EA')
plt.plot(ACs,csc+ea,label='EA+CSC')
plt.plot(ACs,acost,label='AC')
plt.legend()
plt.grid()
plt.xlabel("AC [€/kWh/2]")
plt.ylabel("€/y")
plt.show()


plt.figure(dpi=1000)
plt.plot(ACs,nc)
plt.grid()
plt.xlabel("AC [€/kWh/2]")
plt.ylabel("number of cycles / y")
plt.show()


def soc_ch_di(soc):
    ch = np.zeros(len(soc)-1)
    di = np.zeros(len(soc)-1)
    for h,s in enumerate(soc[1:]):        
        if s > soc[h]:
            ch[h] = s-soc[h]
        if s < soc[h]:
            di[h] = soc[h]-s
    return(ch,di)


#%% 4 grafici
from scheduling_model2 import scheduling_EA_CSC22
d = 10
d = 20
#d = 200

PUN = PUN_TX[d*24:d*24+24]
surplus = surplus_TX[d*24:d*24+24]
needs = needs_TX[d*24:d*24+24]

s = 8

#for ac in ACs:
for ac in [20]:
    soc,profit,incentive,OeM = scheduling_EA_CSC(C0, C0*dod, C0*dod, PUN, PC_ratio, ac,surplus, inc)

    
    # Plots
    plt.figure(dpi=1000)
    
    plt.subplot(4,1,1)
    #plt.title(f"AC = {ac}")
    plt.plot(np.arange(len(PUN)),PUN)
    plt.ylabel("[€/MWh]",size=s)
    plt.xlim(0,23)
    plt.xticks([0,6,12,18,24],[0,6,12,18,24])
    plt.grid()
    plt.title("PUN",size=s)
    plt.tick_params(axis='both', labelsize=s)
    
    ch,di = soc_ch_di(soc)
    new_surplus = np.maximum(0,surplus-ch ) + np.maximum(di-needs,0)  
    
    plt.subplot(4,1,2)
    plt.plot(np.arange(len(PUN)),surplus,label='no BESS')
    plt.plot(np.arange(len(PUN)),new_surplus,label='BESS')
    plt.ylabel("[MWh]",size=s)
    plt.legend(loc=1,fontsize=s)
    plt.xlim(0,23)
    plt.xticks([0,6,12,18,24],[0,6,12,18,24])
    plt.grid()
    plt.ylim(-0.01,C0+0.01)
    plt.title("Into grid",size=s)
    plt.tick_params(axis='both', labelsize=s)
    
    new_needs = np.maximum(0,needs-di ) + np.maximum(0,ch-surplus)
    
    plt.subplot(4,1,3)
    plt.plot(np.arange(len(PUN)),needs,label='no BESS')
    plt.plot(np.arange(len(PUN)),new_needs,label='BESS')
    plt.ylabel("[MWh]",size=s)
    plt.legend(loc=1,fontsize=s)
    plt.xlim(0,23)
    plt.xticks([0,6,12,18,24],[0,6,12,18,24])
    plt.grid()
    plt.ylim(-0.01,C0+0.01)
    plt.title("From grid",size=s)
    plt.tick_params(axis='both', labelsize=s)
    
    plt.subplot(4,1,4)
    x2 = np.arange(25)
    plt.plot(np.arange(len(soc)),soc)
    plt.ylabel("[MWh]",size=s)
    plt.xlim(0,23)
    plt.ylim(0,C0+0.01)
    #plt.ylim(-Cmax-0.05,Cmax+0.05)
    plt.xticks([0,6,12,18,24],[0,6,12,18,24])
    plt.grid()
    plt.title("Stato of Charge",size=s)
    plt.tick_params(axis='both', labelsize=s)
    
    
    plt.tight_layout()
    #plt.subplots_adjust(hspace=0.4)
    plt.show()
    
    soc,profit,incentive,OeM = scheduling_EA_CSC22(C0, C0*dod, C0*dod, PUN, PC_ratio, ac,surplus, needs, inc)

    # Plots
    plt.figure(dpi=1000)
    
    plt.subplot(4,1,1)
    #plt.title(f"AC = {ac}")
    plt.plot(np.arange(len(PUN)),PUN)
    plt.ylabel("[€/MWh]",size=s)
    plt.xlim(0,23)
    plt.xticks([0,6,12,18,24],[0,6,12,18,24])
    plt.grid()
    plt.title("PUN",size=s)
    plt.tick_params(axis='both', labelsize=s)
    
    ch,di = soc_ch_di(soc)
    new_surplus = np.maximum(0,surplus-ch ) + np.maximum(di-needs,0)  
    
    plt.subplot(4,1,2)
    plt.plot(np.arange(len(PUN)),surplus,label='no BESS')
    plt.plot(np.arange(len(PUN)),new_surplus,label='BESS')
    plt.ylabel("[MWh]",size=s)
    plt.legend(loc=1,fontsize=s)
    plt.xlim(0,23)
    plt.xticks([0,6,12,18,24],[0,6,12,18,24])
    plt.grid()
    plt.ylim(-0.01,C0+0.01)
    plt.title("Into grid",size=s)
    plt.tick_params(axis='both', labelsize=s)
    
    new_needs = np.maximum(0,needs-di ) + np.maximum(0,ch-surplus)
    
    plt.subplot(4,1,3)
    plt.plot(np.arange(len(PUN)),needs,label='no BESS')
    plt.plot(np.arange(len(PUN)),new_needs,label='BESS')
    plt.ylabel("[MWh]",size=s)
    plt.legend(loc=1,fontsize=s)
    plt.xlim(0,23)
    plt.xticks([0,6,12,18,24],[0,6,12,18,24])
    plt.ylim(-0.01,C0+0.01)
    plt.grid()
    plt.title("From grid",size=s)
    plt.tick_params(axis='both', labelsize=s)
    
    plt.subplot(4,1,4)
    x2 = np.arange(25)
    plt.plot(np.arange(len(soc)),soc)
    plt.ylabel("[MWh]",size=s)
    plt.xlim(0,23)
    #plt.ylim(-Cmax-0.05,Cmax+0.05)
    plt.xticks([0,6,12,18,24],[0,6,12,18,24])
    plt.grid()
    plt.title("Stato of Charge",size=s)
    plt.tick_params(axis='both', labelsize=s)
    plt.ylim(0,C0+0.01)
    
    
    plt.tight_layout()
    #plt.subplots_adjust(hspace=0.4)
    plt.show()
    

    
    