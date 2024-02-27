"""
BESS SCHEDULING model
"""

import numpy as np
import gurobipy as gp

def scheduling_EA(Cmax,Cmin,SoC_0,PUN,PC_ratio,OeM_cost):
    """"

    Parameters
    ----------
    Cmax : float > 0
        Maximum battery capacity [MWh]
    Cmin : 0 < float < Cmax 
        Minimum battery capacity [MWh]
    SoC_0 : Cmin < float < Cmax
        Battery capacity at time 0
    PUN : list or numpy array of float. Len(PUN) define the number of timesteps to be scheduled
         [€/MWh] 
    PC_ratio : float > 0
        Power / Cmax ratio
    OeM_cost : float > 0
        cost of charge and discharge 1 MWh/h

    Returns
    -------
    b Battery scheduling [MWh/h]
    soc Battery SoC [MWh]
    cf Cash Flow [€]

    """
    
    # Creazione modello
    m = gp.Model("Scheduling")
    T = len(PUN)
    
    # Variabili del problema
    B = m.addVars( T, lb=-PC_ratio*Cmax, ub=PC_ratio*Cmax, vtype=gp.GRB.CONTINUOUS, name='B') # Battery scheduling [MWh/h]
    abs_B = m.addVars( T, lb=0, vtype=gp.GRB.CONTINUOUS, name='abs_B') # Absolute value of B [MWh/h]
    SoC = m.addVars( T+1, lb=Cmin, ub=Cmax, vtype=gp.GRB.CONTINUOUS, name='SoC' ) # SOC [MWh]
    
    # Funzione obiettivo
    profit = -gp.quicksum(B[h]*PUN[h] for h in np.arange(T)) 
    OeM = OeM_cost*gp.quicksum(abs_B[h] for h in np.arange(T))/2
    m.setObjective((profit-OeM), gp.GRB.MAXIMIZE)
    
    # Vincoli
    m.addConstr(SoC[0] == SoC_0) 
    for h in np.arange(T):
        m.addConstr(SoC[h+1] == SoC[h] + B[h])
        m.addConstr(abs_B[h] >= B[h])
        m.addConstr(abs_B[h] >= -B[h])
    
    # Risoluzione del modello
    m.setParam('LogToConsole',0)
    m.optimize()
    
    # Stampa della soluzione ottimale
    b = m.getAttr("x",B).values()
    soc = m.getAttr("x",SoC).values()
    cf = m.objVal
    OeM = OeM.getValue()
    profit = profit.getValue()
    
    return(b,soc,cf,profit,OeM)

def scheduling_EA_TX(Cmax,Cmin,SoC_00,PUN_TX,PC_ratio,OeM_cost,T,X):
    """
    Concatenate X scheduling of length T 
    len(PUN_TX) = X*T
    """
    
    soc_TX = [SoC_00]
    b_TX = []
    cf_TX = []
    profit_TX = []
    OeM_TX = []
    
    for x in range(X):
        
        SoC_0 = soc_TX[-1]
        PUN = PUN_TX[x*T:x*T+T]
        
        b,soc,cf,profit,OeM = scheduling_EA(Cmax, Cmin, SoC_0, PUN, PC_ratio, OeM_cost)
        
        soc_TX += soc[1:]
        b_TX += b
        cf_TX.append(cf)
        profit_TX.append(profit)
        OeM_TX.append(OeM)
        
    return(b_TX,soc_TX,cf_TX,profit_TX,OeM_TX)
      
def scheduling_EA_CSC(Cmax,Cmin,SoC_0,PUN,PC_ratio,OeM_cost,surplus,inc):
    """"

    Parameters
    ----------
    Cmax : float > 0
        Maximum battery capacity [MWh]
    Cmin : 0 < float < Cmax 
        Minimum battery capacity [MWh]
    SoC_0 : Cmin < float < Cmax
        Battery capacity at time 0
    PUN : list or numpy array of float. Len(PUN) define the number of timesteps to be scheduled
         [€/MWh] 
    PC_ratio : float > 0
        Power / Cmax ratio
    OeM_cost : float > 0
        cost of charge and discharge 1 MWh/h
    surplus : list or numpy array of float. Must have the same length of PUN. Rapresent the surplus of energy of a CER. 
        [MWh] 
    inc : incentive that the battery owner obtains by withdrawning CER surplus
        [€/MWh]

    Returns
    -------
    b Battery scheduling [MWh/h]
    soc Battery SoC [MWh]
    cf Cash Flow [€]

    """
    
    # Creazione modello
    m = gp.Model("Scheduling")
    T = len(PUN)
    
    # Variabili del problema
    B = m.addVars( T, lb=-PC_ratio*Cmax, ub=PC_ratio*Cmax, vtype=gp.GRB.CONTINUOUS, name='B') # Battery scheduling [MWh/h]
    B_abs = m.addVars( T, lb=0, vtype=gp.GRB.CONTINUOUS, name='B_abs') # Absolute value of B [MWh/h]
    SoC = m.addVars( T+1, lb=Cmin, ub=Cmax, vtype=gp.GRB.CONTINUOUS, name='SoC' ) # SOC [MWh]
    B_ch =  m.addVars( T, lb=0, vtype=gp.GRB.CONTINUOUS, name='B_ch') # Positive value of B [MWh]
    ch = m.addVars( T, vtype=gp.GRB.BINARY, name='ch') # auxiliary variable for B_ch
    min_B_ch_surplus =  m.addVars( T, lb=0, vtype=gp.GRB.CONTINUOUS, name='min_B_ch_surplus') # min(B_ch,surplus) [MWh]
    SoC = m.addVars( np.arange(T+1), lb=Cmin, ub=Cmax, vtype=gp.GRB.CONTINUOUS, name='SoC' ) # SOC [MWh]
    
    # Funzione obiettivo
    profit = -gp.quicksum(B[h]*PUN[h] for h in np.arange(T)) 
    OeM = OeM_cost*gp.quicksum(B_abs[h] for h in np.arange(T))/2
    incentive = inc*gp.quicksum(min_B_ch_surplus[h] for h in np.arange(T)) 
    
    m.setObjective((profit-OeM+incentive), gp.GRB.MAXIMIZE)
    
    # Vincoli
    m.addConstr(SoC[0] == SoC_0) 
    for h in np.arange(T):
        m.addConstr(SoC[h+1] == SoC[h] + B[h])
        m.addConstr(B_abs[h] >= B[h])
        m.addConstr(B_abs[h] >= -B[h])
        
        m.addConstr(B_ch[h] == B[h]*ch[h])
        m.addConstr(B_ch[h] >= 0)
        
        m.addConstr(min_B_ch_surplus[h] <= B_ch[h])
        m.addConstr(min_B_ch_surplus[h] <= surplus[h])
        # non importa aggiungere anche che sia il più grande possibile visto che è implicito nella funzione obiettivo
    
    # Risoluzione del modello
    m.setParam('LogToConsole',0)
    m.optimize()
    
    # Stampa della soluzione ottimale
    #b = m.getAttr("x",B).values()
    soc = m.getAttr("x",SoC).values()
    #cf = m.objVal
    #OeM = OeM.getValue()
    profit = profit.getValue()
    incentive = incentive.getValue()
    
    #return(b,soc,cf,profit,OeM,incentive)  
    return(soc,profit,incentive)  
    
def scheduling_EA_CSC_TX(Cmax,Cmin,SoC_00,PUN_TX,PC_ratio,OeM_cost,surplus_TX,inc,T,X):
    """
    Concatenate X scheduling of length T 
    len(PUN_TX) = X*T = len(Surplus)
    es: T=24 X=365
    """
    
    soc_TX = np.zeros(T*X+1) #24x365+1
    soc_TX[0] = SoC_00 
    #b_TX = np.zeros(T*X) #24x365
    
    #cf_TX = np.zeros(X) #365
    profit_TX = np.zeros(X) #365
    #OeM_TX = np.zeros(X) #365
    CSC_TX = np.zeros(X) #365
    
    for x in range(X):
        SoC_0 = soc_TX[x*T]
        PUN = PUN_TX[x*T:x*T+T]
        surplus = surplus_TX[x*T:x*T+T]
        
        soc,profit,incentive = scheduling_EA_CSC(Cmax, Cmin, SoC_0, PUN, PC_ratio, OeM_cost,surplus,inc)
        
        profit_TX[x]=profit
        CSC_TX[x]=incentive

        soc_TX[T*x+1:T*x+T+1] = soc[1:]
            
    return(soc_TX,profit_TX,CSC_TX)

def scheduling_EA_CSC22(Cmax,Cmin,SoC_0,PUN,PC_ratio,OeM_cost,surplus,needs,inc):
    """"

    Parameters
    ----------
    Cmax : float > 0
        Maximum battery capacity [MWh]
    Cmin : 0 < float < Cmax 
        Minimum battery capacity [MWh]
    SoC_0 : Cmin < float < Cmax
        Battery capacity at time 0
    PUN : list or numpy array of float. Len(PUN) define the number of timesteps to be scheduled
         [€/MWh] 
    PC_ratio : float > 0
        Power / Cmax ratio
    OeM_cost : float > 0
        cost of charge and discharge 1 MWh/h
    surplus : list or numpy array of float. Must have the same length of PUN. Rapresent the surplus of energy of a CER. 
        [MWh] 
    inc : incentive that the battery owner obtains by withdrawning CER surplus
        [€/MWh]

    Returns
    -------
    b Battery scheduling [MWh/h]
    soc Battery SoC [MWh]
    cf Cash Flow [€]

    """
    
    # Creazione modello
    m = gp.Model("Scheduling")
    T = len(PUN)
    
    # Variabili del problema
    B = m.addVars( T, lb=-PC_ratio*Cmax, ub=PC_ratio*Cmax, vtype=gp.GRB.CONTINUOUS, name='B') # Battery scheduling [MWh/h]
    B_abs = m.addVars( T, lb=0, vtype=gp.GRB.CONTINUOUS, name='B_abs') # Absolute value of B [MWh/h]
    SoC = m.addVars( T+1, lb=Cmin, ub=Cmax, vtype=gp.GRB.CONTINUOUS, name='SoC' ) # SOC [MWh]
    
    B_ch =  m.addVars( T, lb=0, vtype=gp.GRB.CONTINUOUS, name='B_ch') # Positive value of B [MWh]
    B_di =  m.addVars( T, lb=0, vtype=gp.GRB.CONTINUOUS, name='B_di') # Negative value of B (positive) [MWh]
    ch = m.addVars( T, vtype=gp.GRB.BINARY, name='ch') # auxiliary variable for B_ch
    di = m.addVars( T, vtype=gp.GRB.BINARY, name='di') # auxiliary variable for B_di
    
    SoC = m.addVars( np.arange(T+1), lb=Cmin, ub=Cmax, vtype=gp.GRB.CONTINUOUS, name='SoC' ) # SOC [MWh]
    
    # Funzione obiettivo
    profit = -gp.quicksum(B[h]*PUN[h] for h in np.arange(T)) 
    OeM = OeM_cost*gp.quicksum(B_abs[h] for h in np.arange(T))/2
    incentive = inc/2*gp.quicksum(B_ch[h] for h in np.arange(T)) + inc/2*gp.quicksum(B_di[h] for h in np.arange(T)) 
    m.setObjective((profit-OeM+incentive), gp.GRB.MAXIMIZE)
 
    # Vincoli
    m.addConstr(SoC[0] == SoC_0) 
    for h in np.arange(T):
        m.addConstr(SoC[h+1] == SoC[h] + B[h])
        m.addConstr(B_abs[h] >= B[h])
        m.addConstr(B_abs[h] >= -B[h])
        
        m.addConstr(B_ch[h] == B[h]*ch[h])
        m.addConstr(B_ch[h] >= 0)
        
        m.addConstr(B_di[h] == -B[h]*di[h])
        m.addConstr(B_di[h] >= 0)
        
        # preleva solo se c'è surplus e immetti solo se c'è needs!!!
        m.addConstr(B[h] <= surplus[h])
        m.addConstr(B[h] >= -needs[h])
        
    # Risoluzione del modello
    m.setParam('LogToConsole',0)
    m.optimize()
    
    # Stampa della soluzione ottimale
    soc = m.getAttr("x",SoC).values()
    OeM = OeM.getValue()
    profit = profit.getValue()
    incentive = incentive.getValue()
    
    #return(b,soc,cf,profit,OeM,incentive)  
    return(soc,profit,incentive)  

def scheduling_EA_CSC22_TX(Cmax,Cmin,SoC_00,PUN_TX,PC_ratio,OeM_cost,surplus_TX,needs_TX,inc,T,X):
    """
    Concatenate X scheduling of length T 
    len(PUN_TX) = X*T = len(Surplus)
    es: T=24 X=365
    """
    
    soc_TX = np.zeros(T*X+1) #24x365+1
    soc_TX[0] = SoC_00 
    #b_TX = np.zeros(T*X) #24x365
    
    #cf_TX = np.zeros(X) #365
    profit_TX = np.zeros(X) #365
    #OeM_TX = np.zeros(X) #365
    CSC_TX = np.zeros(X) #365
    
    for x in range(X):
        SoC_0 = soc_TX[x*T]
        PUN = PUN_TX[x*T:x*T+T]
        surplus = surplus_TX[x*T:x*T+T]
        needs = needs_TX[x*T:x*T+T]
        
        #b,soc,cf,profit,OeM,incentive = scheduling_EA_CSC(Cmax, Cmin, SoC_0, PUN, PC_ratio, OeM_cost,surplus,inc)
        soc,profit,incentive = scheduling_EA_CSC22(Cmax, Cmin, SoC_0, PUN, PC_ratio, OeM_cost,surplus,needs,inc)
        
        profit_TX[x]=profit
        CSC_TX[x]=incentive
        #OeM_TX[x]=OeM
        #cf_TX[x]=cf
        
        #b_TX[T*x:T*x+T] = b
        soc_TX[T*x+1:T*x+T+1] = soc[1:]
            
    #return(b_TX,soc_TX,cf_TX,profit_TX,OeM_TX,CSC_TX)
    return(soc_TX,profit_TX,CSC_TX)



