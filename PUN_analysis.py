
"""
descriptive analysis of electricity prices in Italy
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_excel("PUN.xlsx")

df['hour'] = np.tile(np.arange(0,24),365)
a = df.groupby(['hour']).mean()

plt.figure(dpi=1000)
plt.rcParams.update({'font.size': 8})
for year in a:
    plt.plot(a.index,a[year],label=year[4:])
plt.legend()
plt.grid()
plt.xlabel('Hour')
plt.ylabel('Average energy price [€/MWh]')
plt.xlim(0,23)
#plt.ylim(50,220)
plt.xticks([0,2,4,6,8,10,12,14,16,18,20,22],[0,2,4,6,8,10,12,14,16,18,20,22])
plt.show()

n=1
plt.figure(dpi=1000)
plt.rcParams.update({'font.size': 6})
for i in df:
    if i != 'hour' and i != 'PUN_2023*':
        plt.subplot(3,2,n)
        plt.plot(df.index,df[i])
        n +=1
        #plt.ylabel('PUN [€/MWh]')
        plt.grid()
        plt.xlim(0,8760)
        plt.ylim(0,900)
        plt.ylabel('Energy price [€/MWh]')
        plt.title(i[4:])
        plt.xticks(np.arange(12)*24*31,['     J','     F','     M','     A','     M','     J','     J','     A','     S','     O','    N','     D'])

        
plt.tight_layout()
plt.show()
        

