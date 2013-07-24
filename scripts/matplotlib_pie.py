# -*- coding: utf-8 -*-
from pylab import *
import sys, common

#parametros 1 labels
#           2 value
#           3 titlte
#	    4 explode
#	    5 unit
#	    6 filename
#python /usr/share/myquotes/scripts/matplotlib_pie.py 'Cuentas bancarias, depósitos y fondos de dinero o monetarios#ETF Inversos#Renta fija#P. Pensiones e inversiones hasta un 50% en renta variable, fondos alternativos y renta fija#P. Pensiones e inversiones hasta un 100% en renta variable y acciones#Productos apalancados (Warrants, Turbos, Inline, Futuros, CFDs...)' '140716.913693001#32844.015#3999.99999999997#9576.26990045999#482756.783#2437.94' 'Patrimonio clasificado por tipo de inversión' '0.15#0#0#0#0#0' '€' /root/.xulpymoney/graphTPC.png
# make a square figure and axes
matplotlib.rcParams['font.size'] = 10
fig=figure (None)
fig.canvas.set_window_title(sys.argv[3]) 
ax = axes([0.1, 0.1, 0.8, 0.8])
unit=(sys.argv[5]).decode('UTF-8')

fracs = common.stralmohadilla2arr(sys.argv[2],"f")
labels = common.stralmohadilla2arr(sys.argv[1],"s")
explode= common.stralmohadilla2arr(sys.argv[4],"f")
patches, texts, autotexts =pie(fracs, explode=explode, labels=labels, labeldistance=100, pctdistance=1.1, autopct='%1.1f%%', shadow=True)

for i in range(len(labels)):
        labels[i]=labels[i]+". {0} € ({1})".format(round(fracs[i], 2),autotexts[i].get_text())


fig.canvas.set_window_title(sys.argv[3].decode('UTF-8'))
#legend( labels,loc=8)
figlegend(patches,labels,"lower center")
if len(sys.argv)==7:
	extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
	fig.set_dpi(40)
        fig.savefig(sys.argv[6], bbox_inches=extent.expanded(1.6, 1.7))
else:
        show()



