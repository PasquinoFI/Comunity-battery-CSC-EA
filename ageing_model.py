"""
cycling ageing
"""

def rainflow(LOC,Cmax):
    
    #https://ieeexplore.ieee.org/document/7741532
    
    # elimination of the plains 
    new=[LOC[0]] # initialise new LOC withouth plains
    for i in range(1,len(LOC)):
        if LOC[i]!=LOC[i-1]:
            new.append(LOC[i])
    LOC=new # new LOC withouth plains
    
    # elimination of what is not a pick or a valley
    def PoV(a,b,c):
        r=0
        if b>=a and b>=c: #peak
            r=1
        if b<=a and b<=c: #valley
            r=1
        return(r)     
    
    new=[LOC[0]] # initialise new LOC without pick or valley         
    for i in range(1,len(LOC)-1):
        r=PoV(LOC[i-1],LOC[i],LOC[i+1])
        if r==1:
            new.append(LOC[i])
    new.append(LOC[len(LOC)-1])
    LOC=new # new LOC without pick or valley
        
    # find half and full cicles and calculate their depth
    hc=[] #depth of half cycles
    fc=[] #depth of full cycles
    stop=0
    while(len(LOC)>3):
        if stop==1:
            break
              
        for i in range(len(LOC)-2):    
            Rx=abs(LOC[i]-LOC[i+1])
            Ry=abs(LOC[i+1]-LOC[i+2])
            if Rx<=Ry: #half cycle finded
                if i==0:
                    hc.append(Rx)
                    LOC.pop(i)
                    break
            if Rx<=Ry: #full cycle finded
                fc.append(Rx)
                LOC.pop(i)
                LOC.pop(i)
                break
            # if only half cicles remain and len(LOC) is still >3 we need break
            if i==len(LOC)-3:
                stop=1
                break
            
    # final cicles control
    for i in range(len(LOC)-1):
        hc.append(abs(LOC[i]-LOC[i+1]))
        
    # calculate the equivalent number of cycles
    n_cycles = 0        
    for c in hc:
        # depth of the cycle / depth of a complete cycle / 2 because it's an half cycle
        n_cycles += 0.5 * c / Cmax          
    for c in fc:
        # depth of the cycle / depth of a complete cycle
        n_cycles += c / Cmax
    
    return(n_cycles)

