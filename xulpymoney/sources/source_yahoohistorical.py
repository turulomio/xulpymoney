#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/xulpymoney")
from libxulpymoney import *
"""Este script saca información de la pagina productoscotizados.com"""


class WorkerYahooHistorical(Source):
    """Clase que recorre las inversiones activas y busca la última  que tiene el microsecond 4. Busca en internet los historicals a partir de esa fecha"""
    def __init__(self, mem):
        Source.__init__(self, mem)
        self.mem=mem
        self.id_source=3
        self.ids=[]
        self.name="YAHOOHISTORICAL"
        self.products=SetProducts(self.mem)
        self.products.load_from_db("select * from products where active=true and priorityhistorical[1]=3", True)
        if __name__!='__main__':
            self.pd= QProgressDialog(QApplication.translate("Core","Inserting {} prices of {} investments").format(0, len(self.products.arr)), QApplication.translate("Core","Cancel"), 0,len(self.products.arr))
            self.pd.setModal(True)
            self.pd.setMinimumDuration(0)          
            self.pd.setWindowTitle(QApplication.translate("Core","Updating product prices..."))

    def start(self, sleep=0):
        sumins=0
        for i,  inv in enumerate(self.products.arr):
            if __name__!='__main__':
                self.pd.setValue(i)
                self.pd.update()
                QApplication.processEvents()
                if self.pd.wasCanceled():
                    self.mem.con.rollback()
                    return
                self.pd.update()
                QApplication.processEvents()
                self.pd.update()            
            ultima=inv.fecha_ultima_actualizacion_historica()
            if ultima==datetime.date.today()-datetime.timedelta(days=1):
                continue
            (set, errors)=self.execute(inv, inv.fecha_ultima_actualizacion_historica()+datetime.timedelta(days=1), datetime.date.today())
            (ins, b, m)=set.save(self.name)
            sumins=sumins+ins
            if __name__ == '__main__':
                stri="{0}: {1}/{2} {3}. Inserted: {4}. Modified:{5}             ".format(function_name(self), i+1, len(self.products.arr), inv, ins, m) 
                sys.stdout.write("\b"*1000+stri)
                sys.stdout.flush()
            else:
                stri=QApplication.translate("Core","Inserting {} prices of {} investments").format(sumins, len(self.products.arr))
                self.pd.setLabelText(stri)
            self.mem.con.commit()  
            time.sleep(sleep)#time step
        print("")
        
    def execute(self,  product, inicio, fin):
        """inico y fin son dos dates entre los que conseguir los datos."""
        url='http://ichart.finance.yahoo.com/table.csv?s='+product.ticker+'&a='+str(inicio.month-1)+'&b='+str(inicio.day)+'&c='+str(inicio.year)+'&d='+str(fin.month-1)+'&e='+str(fin.day)+'&f='+str(fin.year)+'&g=d&ignore=.csv'
        (set, error)=(SetQuotes(self.mem), [])
        web=self.download(url, 'YAHOO_HISTORICAL')
        if web==None:
            return (set, error)
        web.readline()
        for i in web.readlines(): 
            i=b2s(i)
            datos=i.split(",")
            fecha=datos[0].split("-")
            date=datetime.date(int(fecha[0]), int(fecha[1]),  int(fecha[2]))
            
            datestart=dt(date,product.stockexchange.starts,product.stockexchange.zone)
            dateends=dt(date,product.stockexchange.closes,product.stockexchange.zone)
            datetimefirst=datestart-datetime.timedelta(seconds=1)
            datetimelow=(datestart+(dateends-datestart)*1/3)
            datetimehigh=(datestart+(dateends-datestart)*2/3)
            datetimelast=dateends+datetime.timedelta(microseconds=4)

            set.append(Quote(self.mem).init__create(product,datetimelast, float(datos[4])))#closes
            set.append(Quote(self.mem).init__create(product,datetimelow, float(datos[3])))#low
            set.append(Quote(self.mem).init__create(product,datetimehigh, float(datos[2])))#high
            set.append(Quote(self.mem).init__create(product, datetimefirst, float(datos[1])))#open
        return (set,  error)

if __name__ == '__main__':
    mem=MemMyStock()
    if len(sys.argv)>2:
        if sys.argv[2]=="debug":
            log("STARTING", "","Debugging")
            mem.debug=True

    mem.connect_xulpymoneyd(sys.argv[1])
    mem.actualizar_memoria()

    w=WorkerYahooHistorical(mem)
    w.start()

    mem.disconnect_xulpymoneyd()
