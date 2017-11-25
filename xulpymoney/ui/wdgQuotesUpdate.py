from PyQt5.QtWidgets import QWidget,  QApplication
from PyQt5.QtCore import QRegExp,  Qt
from PyQt5.QtGui import QTextCursor
from Ui_wdgQuotesUpdate import Ui_wdgQuotesUpdate
from libxulpymoney import SetProducts, SetQuotes,  Quote,   OHCLDaily, eProductType
import datetime
import os

class wdgQuotesUpdate(QWidget, Ui_wdgQuotesUpdate):
    def __init__(self, mem,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent
        self.arrHistorical=[]
        self.arrIntraday=[]
#        self.pos=0
        self.index=0

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
        QApplication.restoreOverrideCursor()

    def run(self, arr):
#        self.cmdIntraday.setEnabled(False)
#        self.cmdAll.setEnabled(False)
        self.mem.frmMain.setEnabled(False)
        self.mem.frmMain.repaint()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()
        ##### PROCESS #####
        f=open("{}/clients.txt".format(self.mem.dir_tmp), "w")
        for a in arr:
            f.write(" ".join(a) + "\n")
        f.close()
        
        #Pare clients result
        self.quotes=SetQuotes(self.mem)
        os.system("xulpymoney_run_client")
        cr=open("{}/clients_result.txt".format(self.mem.dir_tmp), "r")
        for line in cr.readlines():
            self.txtCR2Q.append(line[:-1])
            if line.find("OHCL")!=-1:
                ohcl=OHCLDaily(self.mem).init__from_client_string(line[:-1])
                if ohcl!=None:
                    for quote in ohcl.generate_4_quotes():
                        if quote!=None:
                            self.quotes.append(quote)
                        self.txtCR2Q.append("    - {}".format (quote))
            if line.find("PRICE")!=-1:
                quote=Quote(self.mem).init__from_client_string(line[:-1])
                if quote!=None:
                    self.quotes.append(quote)
                self.txtCR2Q.append ("    - {}".format (quote))
        cr.close()
        self.quotes.save()
        self.mem.con.commit()
        self.mem.data.load()
        
        self.mem.frmMain.setEnabled(True)
        QApplication.restoreOverrideCursor()

       
    def on_cmdIntraday_released(self):
        self.run(self.arrIntraday)
            
    def on_cmdError_released(self):
        self.txtCR2Q.setFocus()
#        self.txtCR2Q.textCursor() = self.txtCR2Q.textCursor()
        # Setup the desired format for matches
#        format = QtGui.QTextCharFormat()
#        format.setBackground(QtGui.QBrush(QtGui.QColor("red")))
        # Setup the regex engine
        regex = QRegExp( "ERROR")
        # Process the displayed document
        self.index = regex.indexIn(self.txtCR2Q.toPlainText(), self.index+1)
        print(self.index,  self.txtCR2Q.textCursor().position())
        if self.index != -1:
            # Select the matched text and apply the desired format
            self.txtCR2Q.textCursor().setPosition(self.index)
            print(self.index,  self.txtCR2Q.textCursor().position())
            print(self.txtCR2Q.textCursor().movePosition(QTextCursor.PreviousWord, QTextCursor.KeepAnchor, 1))
#            cursor.movePosition(QtGui.QTextCursor.EndOfWord, 1)
#            cursor.mergeCharFormat(format)
            # Move to the next match
#            pos = index + regex.matchedLength()
#            index = regex.indexIn(self.toPlainText(), pos)
        else:
            self.txtCR2Q.textCursor().setPosition(self.index)


    def on_cmdAll_released(self):        
        self.run(self.arrIntraday+self.arrHistorical)
