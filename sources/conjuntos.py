# -*- coding: UTF-8  -*-
from libmyquotes import *

class Conjuntos(Source):
    def __init__(self,  cfg):
        Source.__init__(self, cfg)
        self.name="CONJUNTOS"
#        self.debug=False
        self.utctime_start=self.utctime(datetime.time(0, 0), 'UTC')
        self.utctime_stop=self.utctime(datetime.time(23, 59), 'UTC')
#        self.cfg.cac40=self.set_cac40_isin()
#        self.cfg.dax=self.set_dax_isin()
#        self.cfg.eurostoxx=self.set_eurostoxx_isin()
#        self.cfg.ibex=self.set_ibex_isin()
#        self.cfg.nyse=self.set_nyse()
