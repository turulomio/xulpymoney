#!/usr/bin/python3
import  sys,    multiprocessing,  gettext, os

sys.path.append("/usr/lib/mystocks")
from libxulpymoney import *
 
from conjuntos import *
from yahoo import *
from bolsamadridfondos import *
from bonoaleman import *
from indices import *
  
gettext.bindtextdomain('mystocks','/usr/share/locale/')
gettext.textdomain('mystocks')

try:
    os.remove("/tmp/mystocks.log")
except:
    pass


if __name__ == '__main__':
    mem=MemMyStock()
    if len(sys.argv)>1:
        if sys.argv[1]=="debug":
            log("STARTING", "Debugging")
            mem.debug=True


    con=mem.connect_xulpymoneyd()
    cur = con.cursor()   
    cur2 = con.cursor()   

    con.commit()
    if Global(self.mem).get_database_init_date(cur)=='2000-01-01':
        Global(self.mem).set_database_init_date(cur, str(datetime.date.today()))  
        con.commit()
    mem.actualizar_memoria(cur)
    mem.dbinitdate=Global(self.mem).get_database_init_date(cur)
    mem.carga_ia(cur)
    cur.close()                
    cur2.close()                
    mem.disconnect_xulpymoneyd(con)
    
    wy=WorkerYahoo(mem)
    p1 = multiprocessing.Process(target=wy.start, args=())
    p1.start()
    
#    wbmf=WorkerBolsaMadridFondos(mem)
#    p2 = multiprocessing.Process(target=wbmf.start, args=())
#    p2.start()
#
#    wyi=WorkerYahooInactive(mem)
#    p1in = multiprocessing.Process(target=wyi.start, args=())
#    p1in.start()

#    wba=WorkerBonoAleman(mem)
#    p3 = multiprocessing.Process(target=wba.start, args=())
#    p3.start()

    wib=WorkerIndices(mem)
    p4 = multiprocessing.Process(target=wib.start, args=())
    p4.start()

