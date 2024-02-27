"""
NPV and NPV transformation
"""
import numpy as np
import matplotlib.pyplot as plt

def NPV(I0,CF,i):
    
    T = len(CF)
    npv = np.zeros(T+1)
    npv[0] = -I0
    
    for t in range(1,T+1):
        npv[t] = npv[t-1] + CF[t-1]/(1+i)**(t-1)
    
    return(npv)
    
    
def NPV2(I0,CF,i):
    
    ### per ora funziona con un solo componenete (che si sostituisce sempre dopo lo stesso numero di anni)
    
    van = NPV(I0,CF,i)
    
    cf2 = np.array(CF.copy(),type(float))
    replacement = []
    
    for y,v in enumerate(van[1:]):
        if v < van[y]:
            replacement.append(y)
            cf2[y] += I0
    if replacement == []:
        lt = len(CF)
    else:
        lt = replacement[0] # lifetime
    fa = sum(1/(1+i)**y for y in range(lt)) 
    cf2 += -I0/fa
    van2 = NPV(0,cf2,i)
    
    return(van2)



# NPV transformation test

# =============================================================================
# i = 0.05
# I0 = 10
# cf = np.array([3,3,3,3,3,-7,3,3,3,3,-7,3,3,3,3,-7,3],type(float))
# 
# van = NPV(I0,cf,i)
# x = np.arange(len(van))
# # calculate new van
# cf2 = cf.copy()
# sostituzioni = []
# for y,v in enumerate(van[1:]):
#     if v < van[y]:
#         sostituzioni.append(y)
#         cf2[y] += I0
#      
# # ammortamento
# lt = sostituzioni[0]   
# 
# fa = sum(1/(1+i)**y for y in range(lt))
# cf2 += -I0/fa
#  
# van2 = NPV(0,cf2,i)
# 
# plt.figure(dpi=1000)
# plt.plot(x,van)
# plt.plot(x,van2)
# plt.xlim(0,x[-1])
# plt.ylim(-I0,20)
# plt.ylabel("Net Present Value [€]")
# plt.xlabel("Year")
# plt.grid()
# plt.show()
# =============================================================================
