# coding=utf-8

# Setter opp søkestier for å kunne importere moduler
import os
import sys
file_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(file_dir)
sys.path.append(project_dir)
#________________________________________________________

# Ønsker du å laste inn data selv i offline og håndtere
# på egenhånd/plotte med mer kontroll kan du kjøre denne filen
# Her kan du fritt bruke numpy og andre pakker og du gjør beregninger selv

import matplotlib.pyplot as plt
import numpy as np
from moduler.load_data import LoadData

data1 = LoadData("P00_matplotlib.txt")
data2 = LoadData("P00_matplotlib2.txt")
data3 = LoadData("P00_matplotlib3.txt")
data4 = LoadData("P00_matplotlib4.txt")

nrows = 3
ncols = 2
sharex = False
fig, ax = plt.subplots(nrows, ncols, sharex=sharex)
fig.suptitle("Figur med flere plott-typer")

# Simuler normalfordeling
# Generer tilfeldige binomialfordelte verdier
bi = np.random.binomial(n=10, p=0.5, size=10000)
ax[0,0].hist(
        bi, 
        #bins = len(bi),
        edgecolor ="black",
        linewidth=0.25,
        histtype ='bar',
        color = "c",
        )

# Beregn statistiske verdier
mean = np.mean(bi)
middle = max(np.bincount(bi))/2
sd = np.std(bi)

# Legg inn akser og tittel
ax[0,0].set_title(f"Erik µ={round(mean,2)} σ={round(sd,2)}")
ax[0,0].set_xlabel("Lysverdier")
ax[0,0].set_ylabel("Antall lysmålinger")

# Tegn inn vertikale linjer
ax[0,0].axvline(x = mean, color = 'k', linestyle="dashed") 
ax[0,0].text(mean, middle, "µ", 
        ha='center', va='center',
        backgroundcolor='white',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=1'))

ax[0,0].axvline(x = mean+sd, color = 'k', linestyle="dashed") 
ax[0,0].text(mean+sd, middle, "µ+σ", 
        ha='center', va='center',
        backgroundcolor='white',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=1'))

ax[0,0].axvline(x = mean-sd, color = 'k', linestyle="dashed") 
ax[0,0].text(mean-sd, middle, "µ-σ", 
        ha='center', va='center',
        backgroundcolor='white',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=1'))


# Plotter data fra flere filer
ax[0,1].hist(data1.Lys, edgecolor="black", linewidth=0.25, histtype='bar', color="c")
ax[1,0].hist(data2.Lys, edgecolor="black", linewidth=0.25, histtype='bar', color= "c")
ax[1,1].hist(data3.Lys, edgecolor="black", linewidth=0.25, histtype='bar', color= "c")
ax[2,0].hist(data4.Lys, edgecolor="black", linewidth=0.25, histtype='bar', color= "c")

plt.tight_layout()
plt.show()












