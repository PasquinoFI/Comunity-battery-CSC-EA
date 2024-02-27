"""
band charts
"""

import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)  # Esempio di dati x
y_curve = np.sin(x)          # Esempio di dati y per la curva originale

Y = 0.5  # La quantità Y di distanza dalla curva originale

y_upper = y_curve + Y
y_lower = y_curve - Y

plt.figure(dpi=1000)
#plt.plot(x, y_curve, label='Curva Originale')
plt.fill_between(x, y_lower, y_upper, alpha=0.5, label='Banda')
plt.legend()
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Grafico 2D con Banda tra due Curve')
plt.grid(True)
plt.show()



AC_opt = {'Low':{
                200:{
                    'acl':np.ones(16)*20,
                    'acu':np.ones(16)*30},
                400:{
                    'acl':[40,40,40,40,40,40,40,40,38,36,34,32,30,28,26,24],
                    'acu':np.ones(16)*50},
                600:{
                    'acl':[44,44,44,44,44,44,42,40,38,36,34,32,30,28,26,24],
                    'acu':np.ones(16)*50}},
            'High':{
                    200:{
                        'acl':np.ones(16)*20,
                        'acu':np.ones(16)*30},
                    400:{
                        'acl':np.ones(16)*40,
                        'acu':np.ones(16)*50},
                    600:{
                        'acl':np.ones(16)*49,
                        'acu':np.ones(16)*51}}}


year = ['Low','High'] # 2 PUN
bess_cost = [200,400,600] # 3 costi batteria
bess_size = np.arange(0,320,20)

for y in year:
    for bc in bess_cost:
        
        plt.figure(dpi=1000)
        plt.title(f"EP = {y} BC = {bc} €/kWh")
        
        x = bess_size
        plt.fill_between(x, AC_opt[y][bc]['acl'], AC_opt[y][bc]['acu'], alpha=0.7, label='Optimal range')
        plt.grid()
        plt.xlabel("BESS size [kWh]")
        plt.ylabel("Optimal AC [€/MWh/2]")
        plt.ylim(0,60)
        plt.legend()
        plt.xlim(0,300)
        plt.show()
            