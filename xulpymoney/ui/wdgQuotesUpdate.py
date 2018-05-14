from PyQt5.QtWidgets import QWidget,  QApplication
from PyQt5.QtCore import QRegExp,  Qt
from PyQt5.QtGui import QTextCursor
from Ui_wdgQuotesUpdate import Ui_wdgQuotesUpdate
from libxulpymoney import ProductManager, QuoteManager,  Product, Quote,   OHCLDaily
from libxulpymoneytypes import eProductType, eTickerPosition
import datetime
import os

class wdgQuotesUpdate(QWidget, Ui_wdgQuotesUpdate):
    def __init__(self, mem,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent
        self.arr=[]
#        self.pos=0
        self.index=0

    def generateList(self, all):
        """
            all is boolean selecting all products
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        oneday=datetime.timedelta(days=1)
        if all==True:
            used=""
        else:
            used=" and id in (select products_id from inversiones) "
        ##### BOLSAMADRID #####
        sql="select * from products where type in (1,4) and obsolete=false and stockmarkets_id=1 and isin is not null and isin<>'' {} order by name".format(used)
        products=ProductManager(self.mem)
        products.load_from_db(sql)    
        for p in products.arr:
            ultima=p.fecha_ultima_actualizacion_historica()
            if datetime.date.today()>ultima+oneday:#Historical data is always refreshed the next day, so dont work again
                if p.type.id==eProductType.ETF:
                    self.arr.append(["xulpymoney_bolsamadrid_client","--ISIN_XULPYMONEY",  p.isin, str(p.id),  "--etf","--fromdate", str( p.fecha_ultima_actualizacion_historica()+oneday)])
                elif p.type.id==eProductType.Share:
                    self.arr.append(["xulpymoney_bolsamadrid_client","--ISIN_XULPYMONEY",  p.isin, str(p.id),"--share","--fromdate", str( p.fecha_ultima_actualizacion_historica()+oneday)])
                    
        self.arr.append(["xulpymoney_bolsamadrid_client","--share"]+products.subset_with_same_type(self.mem.types.find_by_id(eProductType.Share.value)).list_ISIN_XULPYMONEY()) # SHARES INTRADAY

        self.arr.append(["xulpymoney_bolsamadrid_client","--etf"]+products.subset_with_same_type(self.mem.types.find_by_id(eProductType.ETF.value)).list_ISIN_XULPYMONEY()) # SHARES INTRADAY

        sql="select * from products where type in ({}) and obsolete=false and stockmarkets_id=1 and isin is not null {} order by name".format(eProductType.PublicBond, used)        
        bm_publicbonds=ProductManager(self.mem)
        bm_publicbonds.load_from_db(sql)    
        self.arr.append(["xulpymoney_bolsamadrid_client","--publicbond"]+bm_publicbonds.list_ISIN_XULPYMONEY())#MUST BE INTRADAY
        
        ibex=Product(self.mem).init__db(79329)
        self.arr.append(["xulpymoney_bolsamadrid_client","--ISIN_XULPYMONEY",  ibex.isin, str(ibex.id),"--index","--fromdate", str(ibex.fecha_ultima_actualizacion_historica()+oneday)])

        ##### YAHOO #####
        sql="select * from products where type in ({},{},{},{}) and obsolete=false and stockmarkets_id<>1 and tickers[{}] is not null {} order by name".format(eProductType.ETF, eProductType.Share, eProductType.Index, eProductType.Currency, eTickerPosition.postgresql(eTickerPosition.Yahoo), used)
        yahoo=ProductManager(self.mem)
        yahoo.load_from_db(sql)    
        for p in yahoo.arr:
            self.arr.append(["xulpymoney_yahoo_client","--TICKER_XULPYMONEY",  p.tickers[eTickerPosition.Yahoo], str(p.id)])
        ##### GOOGLE #####
        sql="select * from products where type in ({},{},{},{}) and obsolete=false and stockmarkets_id<>1 and tickers[{}] is not null {} order by name".format(eProductType.ETF, eProductType.Share, eProductType.Index, eProductType.Currency, eTickerPosition.postgresql(eTickerPosition.Google), used)
        products=ProductManager(self.mem)
        products.load_from_db(sql)    
        for p in products.arr:
            self.arr.append(["xulpymoney_google_client","--TICKER_XULPYMONEY",  p.tickers[eTickerPosition.Google], str(p.id)])

        ##### QUE FONDOS ####
        sql="select * from products where type={} and stockmarkets_id=1 and obsolete=false and tickers[{}] is not null {} order by name".format(eProductType.PensionPlan.value, eTickerPosition.postgresql(eTickerPosition.QueFondos), used)
        products_quefondos=ProductManager(self.mem)#Total of products_quefondos of an Agrupation
        products_quefondos.load_from_db(sql)    
        for p in products_quefondos.arr:
            ultima=p.fecha_ultima_actualizacion_historica()
            if datetime.date.today()>ultima+oneday:#Historical data is always refreshed the next day, so dont work agan
                self.arr.append(["xulpymoney_quefondos_client","--TICKER_XULPYMONEY",  p.tickers[eTickerPosition.QueFondos], str(p.id)])       
                
        ##### MORNINGSTAR #####
        sql="select * from products where tickers[{}] is not null and obsolete=false {} order by name".format(eTickerPosition.postgresql(eTickerPosition.Morningstar),  used)
        products_morningstar=ProductManager(self.mem)#Total of products_morningstar of an Agrupation
        products_morningstar.load_from_db(sql)    
        for p in products_morningstar.arr:
            ultima=p.fecha_ultima_actualizacion_historica()
            if datetime.date.today()>ultima+oneday:#Historical data is always refreshed the next day, so dont work again
                self.arr.append(["xulpymoney_morningstar_client","--TICKER_XULPYMONEY",  p.tickers[eTickerPosition.Morningstar], str(p.id)])       
        QApplication.restoreOverrideCursor()
        return self.arr

    def run(self, arr):
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
        self.quotes=QuoteManager(self.mem)
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

       
    def on_cmdUsed_released(self):
        self.run(self.generateList(all=False))
            
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
        self.run(self.generateList(all=True))
