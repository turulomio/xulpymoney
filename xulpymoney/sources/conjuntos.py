# -*- coding: UTF-8  -*-
from libmystocks import *

class Conjuntos(Source):
    def __init__(self,  mem):
        Source.__init__(self, mem)
        self.name="CONJUNTOS"
#        self.debug=False
        self.utctime_start=self.utctime(datetime.time(0, 0), 'UTC')
        self.utctime_stop=self.utctime(datetime.time(23, 59), 'UTC')
#        self.mem.cac40=self.set_cac40_isin()
#        self.mem.dax=self.set_dax_isin()
#        self.mem.eurostoxx=self.set_eurostoxx_isin()
#        self.mem.ibex=self.set_ibex_isin()
#        self.mem.nyse=self.set_nyse()
