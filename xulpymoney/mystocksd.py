#!/usr/bin/python3
import  sys,    multiprocessing,  gettext, os

sys.path.append("/usr/lib/myquotes")
from libxulpymoney import *
from config import *
from conjuntos import *
from yahoo import *
from bolsamadridfondos import *
from bonoaleman import *
from indices import *
  
gettext.bindtextdomain('myquotes','/usr/share/locale/')
gettext.textdomain('myquotes')

try:
    os.remove("/tmp/myquotes.log")
except:
    pass


if __name__ == '__main__':
    cfg=ConfigMyStock()
    if len(sys.argv)>1:
        if sys.argv[1]=="debug":
            log("STARTING", "Debugging")
            cfg.debug=True


    con=cfg.connect_myquotesd()
    cur = con.cursor()   
    cur2 = con.cursor()   

    con.commit()
    if Global(self.cfg).get_database_init_date(cur)=='2000-01-01':
        Global(self.cfg).set_database_init_date(cur, str(datetime.date.today()))  
        con.commit()
    cfg.actualizar_memoria(cur)
    cfg.dbinitdate=Global(self.cfg).get_database_init_date(cur)
    cfg.carga_ia(cur)
    cur.close()                
    cur2.close()                
    cfg.disconnect_myquotesd(con)
    
    wy=WorkerYahoo(cfg)
    p1 = multiprocessing.Process(target=wy.start, args=())
    p1.start()
    
#    wbmf=WorkerBolsaMadridFondos(cfg)
#    p2 = multiprocessing.Process(target=wbmf.start, args=())
#    p2.start()
#
#    wyi=WorkerYahooInactive(cfg)
#    p1in = multiprocessing.Process(target=wyi.start, args=())
#    p1in.start()

#    wba=WorkerBonoAleman(cfg)
#    p3 = multiprocessing.Process(target=wba.start, args=())
#    p3.start()

    wib=WorkerIndices(cfg)
    p4 = multiprocessing.Process(target=wib.start, args=())
    p4.start()

