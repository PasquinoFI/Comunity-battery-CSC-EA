"""
post processing
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle as pkl


with open('mensili npv 1.pkl', 'rb') as f: res = pkl.load(f)
with open('mensili shced 1.pkl', 'rb') as f: resched = pkl.load(f)

# =============================================================================
# with open('mensili npv 2.pkl', 'rb') as f: res = pkl.load(f)
# with open('mensili shced 2.pkl', 'rb') as f: resched = pkl.load(f)
# =============================================================================

c_size = [80,135,205] # 3 cer
year = ['Low','High'] # 2 PUN
bess_cost = [200,400,600] # 3 costi batteria
bess_size = np.arange(20,320,20)
ACs = np.arange(5,55,5)
c_label = {80:'40 %', 135:'60 %', 205:'80 %'}
ss_label = {80:'38 %', 135:'34 %', 205:'30 %'}

### 1 esempio vari ACs
ACs = [5,15,25,35,45]
c = 80
y = 'Low'
bs = 80
bc = 400

plt.figure(dpi=1000)
for ac in ACs:
    npv = res[c][y][bs][ac][bc]['NPV']
    x = np.arange(len(npv))
    plt.plot(x,npv,label=f"ac = {ac}")
plt.legend()
plt.title(f"sc = {c_label[c]} year = {y} b_size = {bs}kWh b_cost = {bc} €/kWh")
plt.grid()
plt.xlim(x[0],x[-1])
#plt.ylim(-20000,80000)
plt.xlabel("Time [y]")
plt.ylabel("Net Present Value [€]")
plt.show()


## npv-bess_size per vari ac
bc = 200
plt.figure(dpi=1000,figsize=(18,8))
n=1
for y in year:
    for c in c_size:
        plt.subplot(2,3,n)
        x = bess_size
        plt.title(f"CN = {c} EP = {y}")
        for ac in ACs:
            npv = []
            for bs in bess_size: 
                npv.append(res[c][y][bs][ac][bc]['NPV2'][-1])
            plt.plot(x,npv,label=f"{ac}")
        plt.legend(title='AC [€/MWh]')
        plt.xlabel("BESS size [kWh]")
        plt.ylabel("Net Present Value* [€]")
        plt.grid()
        plt.xlim(0,300)
        n+=1
plt.tight_layout()
plt.show()
            
        
### trova gli AC ottimali x ogni scenario!!!
ACs_opt = {}
for c in c_size:
    ACs_opt[c] = {}
    for y in year:
        ACs_opt[c][y] = {}
        for bs in bess_size:
            ACs_opt[c][y][bs] = {}
            for bc in bess_cost:         
                npv_opt=-99999999999999999999999999999999999
                for ac in ACs:   
                    npv = res[c][y][bs][ac][bc]['NPV2'][-1]
                    if npv > npv_opt:
                        npv_opt = npv
                        ac_opt = ac
                ACs_opt[c][y][bs][bc] = ac_opt
                
                
                
### npv-bess_size su ac ottimali
plt.figure(dpi=1000,figsize=(18,8))
n=1
for y in year:
    for bc in bess_cost:
        plt.subplot(2,3,n)
        plt.title(f"EP = {y} BC = {bc} €/kWh")
        for c in c_size:
            x = bess_size
            npv = []
            for bs in bess_size:
                ac = ACs_opt[c][y][bs][bc]
                #ac = 20
                npv.append(res[c][y][bs][ac][bc]['NPV2'][-1])
            plt.plot(x,npv,label=c)
        plt.legend(title="CN")
        plt.grid()
        plt.xlim(0,300)
        plt.xlabel("BESS size [kWh]")
        plt.ylabel("Net Present Value* [€]")
        n+=1
plt.tight_layout()
plt.show()
        
        
### trova le taglie ottimali x ogni scenario!!!
bess_opt = {}
for c in c_size:
    bess_opt[c] = {}
    for y in year:
        bess_opt[c][y] ={}
        for bc in bess_cost:
            bs_opt = 0
            npv_opt=-99999999999999999999999999999999999
            for bs in bess_size:
                ac = ACs_opt[c][y][bs][bc]
                npv = res[c][y][bs][ac][bc]['NPV2'][-1]
                if npv > npv_opt:
                    bs_opt = bs
                    npv_opt = npv
            bess_opt[c][y][bc] = bs_opt
                
  
### npv-time su taglie ottiamali
plt.figure(dpi=1000,figsize=(18,8))
n=1
for y in year:
    for bc in bess_cost:
        plt.subplot(2,3,n)
        plt.title(f"EP = {y} BC = {bc} €/kWh")
        for c in c_size:
            bs = bess_opt[c][y][bc]
            ac = ACs_opt[c][y][bs][bc]
            npv = res[c][y][bs][ac][bc]['NPV']
            x = np.arange(len(npv))
            if bs == 20:
                plt.plot(x,np.zeros(len(x)),label=f"{c_label[c]} - 0 kWh")
            else:              
                plt.plot(x,npv,label=f"{c_label[c]} - {bs} kWh")
        plt.plot(x,np.zeros(len(x)),color='k')    
        plt.legend(title="CSC$_0$ - BESS optimal size")
        plt.grid()
        plt.xlabel("Time [y]")
        plt.ylabel("Net Present Value [€]")
        plt.xlim(x[0],x[-1])
        n+=1
       # plt.ylim(-120000,120000)
plt.tight_layout() 
plt.show()

        
        
### di quanto aumenta l'autoconsumo!?!?

        
        
        
        
#%% perchè un AC è ottimale?!?!?!?
                
## ac ottimali vs b_size in vari scenari
for y in year:
    for bc in bess_cost:
        
        plt.figure(dpi=1000)
        plt.title(f"EP = {y} BC = {bc} €/kWh")
        
        
        for c in c_size:
            
            x = bess_size
            ac = []
            for bs in bess_size:
                ac.append(ACs_opt[c][y][bs][bc])
            plt.plot(x,ac,label=c_label[c])
        
        plt.legend(title="REC self-consumption")
        plt.grid()
        plt.xlabel("BESS size [kWh]")
        plt.ylabel("Optimal AC [€/MWh/2]")
        plt.ylim(0,60)
        plt.show()
            

#%% CSC e EA
plt.figure(dpi=1000,figsize=(18,8))
n=1
for y in year:
    for c in c_size:
        plt.subplot(2,3,n)
        ea = []
        csc = []
        for bs in bess_size:
         #   ac = ACs_opt[c][y][bs][bc]
            ac =30
            csc.append(resched[c][y][bs][ac]['csc'].sum()/20)
            ea.append(resched[c][y][bs][ac]['ea'].sum()/20)
            
        x = bess_size
        plt.plot(x,ea,label='EA')
        plt.plot(x,csc,label='CSC')
        plt.plot(x,np.array(ea)+np.array(csc),label='Tot')
        plt.legend()
        plt.xlabel('BESS size [kWh]')
        plt.ylabel('Gain [€/year]')
        plt.grid()
        plt.title(f"CN = {c} EP = {y}")
        plt.ylim(0,7000)
        plt.xlim(0,300)
        n+=1
plt.tight_layout() 
plt.show()


         
#%% SC SS ?!?!?
def soc_ch_di(soc):
    ch = np.zeros(len(soc)-1)
    di = np.zeros(len(soc)-1)
    for h,s in enumerate(soc[1:]):        
        if s > soc[h]:
            ch[h] = s-soc[h]
        if s < soc[h]:
            di[h] = soc[h]-s
    return(ch,di)


into_grid = {}
from_grid = {}
plt.figure(dpi=1000)
plt.rcParams.update({'font.size': 10})
c_size = [80,135,205]
col=0
for c in c_size:
    surplus_TX = np.array(pd.read_csv(f"100kWp {c}c surplus.csv")['Surplus MWh']) # MWh
    needs_TX = np.array(pd.read_csv(f"100kWp {c}c needs.csv")['Needs MWh']) # MWh
    surplus = np.tile(surplus_TX, 20)
    needs = np.tile(needs_TX, 20)
            
    y = 'Low'
    
    sc = [int(c_label[c][:2])]
    ss = [int(ss_label[c][:2])]
    
    into_grid[c] = {}
    into_grid[c]['tot'] = [surplus.sum()]
    into_grid[c]['BESS'] = [0]
    into_grid[c]['REC'] = [surplus.sum()]
    into_grid[c]['max'] = [max(surplus)]
    
    from_grid[c] = {}
    from_grid[c]['tot'] = [needs.sum()]
    from_grid[c]['BESS'] = [0]
    from_grid[c]['REC'] = [needs.sum()]
    from_grid[c]['max'] = [max(needs)]
    
    

    for bs in bess_size:
        
      #  ac = ACs_opt[c][y][bs][bc]
        ac = 30
        soc = resched[c][y][bs][ac]['soc']
        ch,di = soc_ch_di(soc)
        
        sc0 = int(c_label[c][:2])
        ss0 = int(ss_label[c][:2])
        
        sum0 = surplus.sum()
        ssum0 = needs.sum()        

        surplus2 = surplus-ch
        surplus2[surplus2<0] = 0 # ovviamnete se carico più di quanto è il surplus non conta per l'autoconsumo
        surplus3 = di-needs
        surplus3[surplus3<0] = 0
        
        into_grid[c]['BESS'].append(surplus3.sum())
        into_grid[c]['REC'].append(surplus2.sum())
        into_grid[c]['tot'].append((np.maximum(0,surplus-ch ) + np.maximum(di-needs,0)).sum())
        into_grid[c]['max'].append(max((np.maximum(0,surplus-ch ) + np.maximum(di-needs,0))))
        
        needs2 = needs-di
        needs2[needs2<0] = 0 # ovviamnete se scarico più di quanto c'è bisogno non conta per l'autosufficienza
        needs3 = ch-surplus
        needs3[needs3<0] = 0
         
        from_grid[c]['BESS'].append(needs3.sum())
        from_grid[c]['REC'].append(needs2.sum())
        from_grid[c]['tot'].append((np.maximum(0,needs-di ) + np.maximum(0,ch-surplus)).sum())
        from_grid[c]['max'].append(max((np.maximum(0,needs-di ) + np.maximum(0,ch-surplus))))
         
        sum2 = surplus2.sum()
        ssum2 = needs2.sum()
        
        sc2 = 100 - (sum2/sum0) * (100-sc0) 
        ss2 = 100 - (ssum2/ssum0) * (100-ss0)  #???
        
        sc.append(sc2)
        ss.append(ss2)
        
    x = np.insert(bess_size, 0, 0)
    
    colors = ['tab:red','tab:green','tab:orange']

    plt.plot(x,sc,label=f" CSC$_0$ = {c_label[c]}",color=colors[col])
    plt.plot(x,ss,label=f" CSS$_0$ = {ss_label[c]}",color=colors[col],ls='--')
    col+=1
    
plt.xlabel('BESS size [kWh]')
plt.ylabel('CSC and CSS [%]')
plt.grid()
plt.xlim(0,300)
plt.ylim(0,100)


colors = ["tab:red","tab:green","tab:orange"]
labels = [80,135,205]
from matplotlib.lines import Line2D
legend_lines = [Line2D([0], [0], color=c, lw=2) for c in colors]
legend1 = plt.legend(legend_lines, labels, ncol=1, title='Customer number')
plt.gca().add_artist(legend1)

style = ["-","--"]
labels = ["Collective-Self-Consumption","Collective-Self-Sufficiency"]
legend_lines = [Line2D([0], [0], linestyle=s, lw=2, color='k') for s in style]
legend1 = plt.legend(legend_lines, labels, ncol=1)
plt.gca().add_artist(legend1)


plt.show()


### grafici vari into grid e from grid
for c in c_size:
    plt.figure(dpi=1000)
    plt.plot(x,into_grid[c]['tot'],label='Into grid')
    plt.plot(x,into_grid[c]['BESS'],label='Into grid by BESS')
    plt.plot(x,into_grid[c]['REC'],label='Into grid by REC')
    plt.grid()
    plt.xlabel('BESS size [kWh]')
    plt.legend()
    plt.ylabel('Electricity [MWh/20y]')
    plt.xlim(x[0],x[-1])
    plt.ylim(0,)
   # plt.title(f"sc = {c_label[c]} y = {y}")
    plt.show()

    plt.figure(dpi=1000)
    plt.plot(x,from_grid[c]['tot'],label='From grid')
    plt.plot(x,from_grid[c]['BESS'],label='From grid by BESS')
    plt.plot(x,from_grid[c]['REC'],label='From grid by REC')
    plt.grid()
    plt.xlabel('BESS size [kWh]')
    plt.legend()
    plt.ylabel('Electricity [MWh/20y]')
    plt.xlim(x[0],x[-1])
    plt.ylim(0,)
   # plt.title(f"sc = {c_label[c]} y = {y}")
    plt.show()
    
# =============================================================================
#     plt.figure(dpi=1000)
#     plt.plot(x,into_grid[c]['max'],label='max into grid')
#     plt.plot(x,from_grid[c]['max'],label='max from grid')
#     plt.grid()
#     plt.xlabel('BESS size [kWh]')
#     plt.legend()
#     plt.ylabel('[MWh/h]')
#     plt.xlim(x[0],x[-1])
#     plt.ylim(0,0.25)
#    # plt.title(f"sc = {c_label[c]} y = {y}")
#     plt.show()
#     
# =============================================================================
    
    



# =============================================================================
# from scipy.stats import gaussian_kde
# # pdf into grid test
# plt.figure(dpi=1000)
# dati=surplus
# kde = gaussian_kde(dati)
# x = np.linspace(np.min(dati), np.max(dati), 1000)
# pdf = kde(x)
# plt.plot(x, pdf,label='Into grid no BESS')
# dati=np.maximum(0,surplus-ch ) + np.maximum(di-needs,0)
# kde = gaussian_kde(dati)
# x = np.linspace(np.min(dati), np.max(dati), 1000)
# pdf = kde(x)
# plt.plot(x, pdf, label='Into grid BESS')
# plt.xlabel('Into grid [MWh]')
# plt.ylabel('Probability Density Function')
# plt.title('')
# plt.grid(True)
# plt.xlim(0,0.2)
# plt.legend()
# plt.show()
# 
# # pdf from grid test
# plt.figure(dpi=1000)
# dati=needs
# kde = gaussian_kde(dati)
# x = np.linspace(np.min(dati), np.max(dati), 1000)
# pdf = kde(x)
# plt.plot(x, pdf,label='From grid no BESS')
# dati=np.maximum(0,needs-di ) + np.maximum(0,ch-surplus)
# kde = gaussian_kde(dati)
# x = np.linspace(np.min(dati), np.max(dati), 1000)
# pdf = kde(x)
# plt.plot(x, pdf, label='From grid BESS')
# plt.xlabel('From grid [MWh]')
# plt.ylabel('Probability Density Function')
# plt.title('')
# plt.grid(True)
# plt.xlim(0,0.2)
# plt.legend()
# plt.show()
# =============================================================================
        





