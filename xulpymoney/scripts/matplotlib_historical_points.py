# -*- coding: utf-8 -*-
#parametros 1 title #
#           2 unit #
#	    3 date
#	    4 value
#	    5 file
from pylab import *
import sys, numpy, datetime, common
from matplotlib.dates import *

days    = DayLocator()   # every year
months   = MonthLocator()  # every month
daysfmt = DateFormatter('%Y-%m-%d')

date=datetime
dates = common.stralmohadilla2arr(sys.argv[3],"d")
values = common.stralmohadilla2arr(sys.argv[4],"f")

fig = figure()
fig.canvas.set_window_title(sys.argv[1])
ax = fig.add_subplot(111)
ax.plot_date(dates, values, '-')

# format the ticks
ax.xaxis.set_major_locator(months)
ax.xaxis.set_major_formatter(daysfmt)
ax.xaxis.set_minor_locator(days)
ax.autoscale_view()

# format the coords message box
def price(x): return '$%1.2f'%x
ax.fmt_xdata = DateFormatter('%Y-%m-%d')
ax.fmt_ydata = price
ax.grid(True)

fig.autofmt_xdate()
suptitle(sys.argv[1].decode('UTF-8'), fontsize=24)
#figlegend(ax,labels,"lower center")
if len(sys.argv)==6:
        fig.savefig(sys.argv[5])
else:
        show()
