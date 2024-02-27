from scheduling_model import scheduling_EA_CSC_TX
from scheduling_model import scheduling_EA_CSC22_TX
from ageing_model import rainflow
import numpy as np
import pandas as pd

# concatenaating scheduling model and calculate ageing each months/year

def scheduling_Y(years,cicli_vita,fine_vita,calendar_ageing,Cmax,dod,PUN_TX,PC_ratio,OeM_cost,surplus_TX,needs_TX,inc,strategy):
    
    cf = np.zeros(years)
    repl = np.zeros(years)
    
    nc = 0
    deg = 0
    deg2 = 0
    C0 = Cmax
    
    soc = np.zeros(8760*years+1)
    soc[0] = C0*dod
    ea = np.zeros(365*years)
    csc = np.zeros(365*years)
    
    
    
    for y in range(years):
        
        cfy = 0
        
        # Sostituzione?:
        if C0 < Cmax*fine_vita:
            repl[y] = 1
            deg = 0
            deg2 = 0
            nc = 0
            C0 = Cmax
            
        # Run scheduling_TX       
        if strategy == 1:
            soc_TX,profit_TX,CSC_TX = scheduling_EA_CSC_TX(C0, C0*dod, C0*dod, PUN_TX, PC_ratio, OeM_cost,surplus_TX, inc, 24, 365)    
        if strategy == 2:
            soc_TX,profit_TX,CSC_TX = scheduling_EA_CSC22_TX(C0, C0*dod, C0*dod, PUN_TX, PC_ratio, OeM_cost,surplus_TX, needs_TX, inc, 24, 365) 
            
        
        cfy += np.array(profit_TX).sum() + np.array(CSC_TX).sum()
        
        # Calculate ageing
        nc += rainflow(soc_TX,Cmax)
        deg = nc/cicli_vita * (1-fine_vita)*Cmax 
        deg2 += calendar_ageing*Cmax
        C0 = Cmax - deg - deg2  ### commentare per ageing test1

        cf[y]=cfy
        soc[8760*y+1:8760*y+8760+1] = soc_TX[1:]
        ea[365*y:365*y+365] = profit_TX
        csc[365*y:365*y+365] = CSC_TX       
            
    return(np.array(cf),repl,soc,ea,csc)

def scheduling_M(years,cicli_vita,fine_vita,calendar_ageing,Cmax,dod,PUN_TX,PC_ratio,OeM_cost,surplus_TX,needs_TX,inc,strategy):
    
    cf = np.zeros(years*12)
    repl = np.zeros(years*12)
    
    nc = 0
    deg = 0
    deg2 = 0
    C0 = Cmax
    
    soc = np.zeros(8760*years+1)
    soc[0] = C0*dod
    ea = np.zeros(365*years)
    csc = np.zeros(365*years)
    
    dm = [31,28,31,30,31,30,31,31,30,31,30,31]*years # durata mesi
    dm = [0] + dm
    dm_hours = [x*24 for x in dm] #ore in ogni mese
    dm_cum = [sum(dm[:i+1]) for i in range(len(dm))] # cumulata ore
    dm_hours_cum = [sum(dm_hours[:i+1]) for i in range(len(dm_hours))] # cumulata ore

    cm = 0
    for m in range(years*12):
        
        cfm = 0
        
        # Sostituzione?:
        if C0 < Cmax*fine_vita:
            repl[m] = 1
            deg = 0
            deg2 = 0
            nc = 0
            C0 = Cmax
            
        # seleziona serie mensile e non annuale da passare al simulatore
        m0 = m%12
        PUN_TX_M = PUN_TX[dm_hours_cum[m0]:dm_hours_cum[m0+1]]
        surplus_TX_M = surplus_TX[dm_hours_cum[m0]:dm_hours_cum[m0+1]]
        needs_TX_M = needs_TX[dm_hours_cum[m0]:dm_hours_cum[m0+1]]
        
        # Run scheduling_TX       
        if strategy == 1:
            soc_TX,profit_TX,CSC_TX = scheduling_EA_CSC_TX(C0, C0*dod, C0*dod, PUN_TX_M, PC_ratio, OeM_cost,surplus_TX_M, inc, 24, dm[cm+1])    
        if strategy == 2:
            soc_TX,profit_TX,CSC_TX = scheduling_EA_CSC22_TX(C0, C0*dod, C0*dod, PUN_TX_M, PC_ratio, OeM_cost,surplus_TX_M, needs_TX_M, inc, 24, dm[cm+1]) 
            
        
        cfm += np.array(profit_TX).sum() + np.array(CSC_TX).sum()
        
        # Calculate ageing
        nc += rainflow(soc_TX,Cmax)
        deg = nc/cicli_vita * (1-fine_vita)*Cmax 
        deg2 += calendar_ageing*Cmax/12
        C0 = Cmax - deg - deg2  ### commentare per ageing test1

        cf[m]=cfm
        
        soc[dm_hours_cum[m]+1:dm_hours_cum[m+1]+1] = soc_TX[1:]
        ea[dm_cum[m]:dm_cum[m+1]] = profit_TX
        csc[dm_cum[m]:dm_cum[m+1]] = CSC_TX       
        
        cm += 1

            
    return(np.array(cf),repl,soc,ea,csc)