from PyQt5.QtWidgets import QWidget
from Ui_wdgQuotesUpdate import Ui_wdgQuotesUpdate
from libxulpymoney import SetProducts, SetQuotes,  Quote,   OHCLDaily, eProductType
import datetime
import os
#from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor,   as_completed

class wdgQuotesUpdate(QWidget, Ui_wdgQuotesUpdate):
    def __init__(self, mem,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent
        self.arrHistorical=[]
        self.arrIntraday=[]


        
        oneday=datetime.timedelta(days=1)
        ##### BOLSAMADRID #####
        sql="select * from products where type in (1,4) and obsolete=false and stockmarkets_id=1 and isin is not null and isin<>'' order by name"
        products=SetProducts(self.mem)
        products.load_from_db(sql)    
        for p in products.arr:
            ultima=p.fecha_ultima_actualizacion_historica()
            if datetime.date.today()>ultima+oneday:#Historical data is always refreshed the next day, so dont work again
                if p.type.id==eProductType.ETF:
                    self.arrHistorical.append(["xulpymoney_bolsamadrid_client","--ISIN",  p.isin, "--etf","--fromdate", str( p.fecha_ultima_actualizacion_historica()+oneday), "--XULPYMONEY", str(p.id)])
                elif p.type.id==eProductType.Share:
                    self.arrHistorical.append(["xulpymoney_bolsamadrid_client","--ISIN",  p.isin, "--share","--fromdate", str( p.fecha_ultima_actualizacion_historica()+oneday), "--XULPYMONEY", str(p.id)])
        sql="select * from products where type in ({}) and obsolete=false and stockmarkets_id=1 and isin is not null order by name".format(eProductType.PublicBond)        
        print(sql)
        bm_publicbonds=SetProducts(self.mem)
        bm_publicbonds.load_from_db(sql)    
        suf=[]
        for p in bm_publicbonds.arr:
            if len(p.isin)>5:
                suf.append("--ISIN")
                suf.append(p.isin)
                suf.append("--XULPYMONEY")
                suf.append(str(p.id))
        self.arrIntraday.append(["xulpymoney_bolsamadrid_client","--publicbond"]+suf)#MUST BE INTRADAY
                
        ##### MORNINGSTAR #####
        sql="select * from products where priorityhistorical[1]=8 and obsolete=false and ticker is not null order by name"
        products_morningstar=SetProducts(self.mem)#Total of products_morningstar of an Agrupation
        products_morningstar.load_from_db(sql)    
        for p in products_morningstar.arr:
            ultima=p.fecha_ultima_actualizacion_historica()
            if datetime.date.today()>ultima+oneday:#Historical data is always refreshed the next day, so dont work again
                self.arrHistorical.append(["xulpymoney_morningstar_client","--TICKER",  p.ticker, "--XULPYMONEY",  str(p.id)])       
        
    def run(self, arr):
        ##### PROCESS #####
        f=open("/tmp/clients.txt", "w")
        for a in arr:
            f.write(" ".join(a) + "\n")
        f.close()
        
        #Pare clients result
        self.quotes=SetQuotes(self.mem)
        os.system("xulpymoney_run_client")
        f=open("/tmp/clients_result.txt", "r")
        for line in f.readlines():
            if line.find("OHCL")!=-1:
                ohcl=OHCLDaily(self.mem).init__from_client_string(line[:-1])
                for quote in ohcl.generate_4_quotes():
                    self.quotes.append(quote)
            if line.find("PRICE")!=-1:
                self.quotes.append(Quote(self.mem).init__from_client_string(line[:-1]))
        f.close()
        self.quotes.print()
        self.quotes.save()
        self.mem.con.commit()
        self.mem.data.load()

       
    def on_cmdIntraday_released(self):
        self.cmdIntraday.setEnabled(False)
        self.cmdAll.setEnabled(False)
        self.run(self.arrIntraday)
            

    def on_cmdAll_released(self):        
        self.cmdIntraday.setEnabled(False)
        self.cmdAll.setEnabled(False)
        self.run(self.arrIntraday+self.arrHistorical)
