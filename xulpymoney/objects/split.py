from PyQt5.QtCore import QObject
from xulpymoney.libmanagers import ObjectManager_With_IdName_Selectable
from xulpymoney.objects.dividend import DividendHomogeneusManager
from xulpymoney.objects.estimation import EstimationDPSManager, EstimationEPSManager
from xulpymoney.objects.dps import DPSManager
from xulpymoney.objects.ohcl import OHCLDailyManager, OHCLDaily
from xulpymoney.objects.quote import QuoteAllIntradayManager
from xulpymoney.ui.myqtablewidget import qdatetime, qright, qleft, qcenter
## Split associated to a product quotes. It's a record in splits table. It doesn't modifie quotes in database. RECOMENDED
class Split:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.product=None
        self.datetime=None
        self.after=None
        self.before=None
        self.comment=None
                
    def __repr__(self):
        return ("Instancia de Split: {0} ({1})".format( self.id, self.id))
        
    def init__create(self, product, datetime, before, after, comment, id=None):
        self.id=id
        self.product=product
        self.datetime=datetime
        self.after=after
        self.before=before
        self.comment=comment
        return self
        
    def init__db_row(self, row, product):
        return self.init__create(product,  row['datetime'],  row['before'], row['after'],   row['comment'],  row['id'])

    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:#Insertar
            cur.execute("insert into splits(products_id,datetime,after,before,comment) values (%s,%s,%s,%s,%s) returning id", (self.product.id, self.datetime, self.after, self.before, self.comment))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update splits set products_id=%s, datetime=%s, after=%s, before=%s, comment=%s where id=%s", (self.product.id, self.datetime, self.after, self.before, self.comment, self.id))
        cur.close()


    def convertShares(self, shares):
        """Function to calculate new shares just pass the number you need to convert"""
        return shares*self.after/self.before
        
    def convertPrices(self, price):
        return price*self.before/self.after
                
    def delete(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from splits where id=%s", (self.id,))
        cur.close()
            
        
    def type(self):
        """Función que devuelve si es un Split o contrasplit"""
        if self.before>self.after:
            return "Contrasplit"
        else:
            return "Split"

class SplitManager(ObjectManager_With_IdName_Selectable, QObject):
    def __init__(self, mem, product):
        ObjectManager_With_IdName_Selectable.__init__(self)
        QObject.__init__(self)
        self.product=product
        self.mem=mem
        
    def init__from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)
        for row in cur:
            self.append(Split(self.mem).init__db_row(row, self.product))
        cur.close()
        return self
            
    def order_by_datetime(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda c: c.product.result.basic.last.datetime,  reverse=False)  
            return True
        except:
            return False
    def myqtablewidget(self, wdg):
        """Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la table
        Devuelve sumatorios"""

        wdg.table.setColumnCount(4)
        wdg.table.setHorizontalHeaderItem(0, qcenter(self.tr("Date" )))
        wdg.table.setHorizontalHeaderItem(1, qcenter(self.tr("Before" )))
        wdg.table.setHorizontalHeaderItem(2, qcenter(self.tr("After" )))
        wdg.table.setHorizontalHeaderItem(3, qcenter(self.tr("Comment" )))
        #DATA  
        wdg.applySettings()
        wdg.table.clearContents()

        wdg.table.setRowCount(len(self.arr))
        for i, o in enumerate(self.arr):
            wdg.table.setItem(i, 0, qdatetime(o.datetime, self.mem.localzone_name))
            wdg.table.setItem(i, 1, qright(o.before))
            wdg.table.setItem(i, 2, qright(o.after))
            wdg.table.setItem(i, 3, qleft(o.comment))
                
    def delete(self, o):
        o.delete()    #Delete from database
        self.remove(o)    #Removes from array
        
    def adjustPrice(self, datetime, price):
        """
            Returns a new price adjusting
        """
        r=price
        for split in reversed(self.arr):
            if datetime<split.datetime:
                r=split.convertPrices(r)
        return r
        
    def adjustOHCLDaily(self, ohcl ):
        r=OHCLDaily(self.mem)
        r.product=ohcl.product
        r.date=ohcl.date
        r.close=self.adjustPrice(ohcl.datetime(), ohcl.close)
        r.open=self.adjustPrice(ohcl.datetime(), ohcl.open)
        r.high=self.adjustPrice(ohcl.datetime(), ohcl.high)
        r.low=self.adjustPrice(ohcl.datetime(), ohcl.low)
        return r

    def adjustOHCLDailyManager(self, set):
        r=OHCLDailyManager(self.mem, self.product)
        for ohcl in set.arr:
            r.append(self.adjustOHCLDaily(ohcl))
        return r

## Class to make calculations with splits or contrasplits, between two datetimes
## This class updates quotes, and investment operations
## It's not recommended. Only useful to update quotes already in database with jumps in splits.
class SplitManual:
    def __init__(self, mem, product, sharesinitial,  sharesfinal,  dtinitial, dtfinal):
        self.mem=mem
        self.initial=sharesinitial
        self.final=sharesfinal
        self.dtinitial=dtinitial
        self.dtfinal=dtfinal
        self.product=product

    def convertShares(self, actions):
        """Function to calculate new shares just pass the number you need to convert"""
        return actions*self.final/self.initial
        
    def convertPrices(self, price):
        return price*self.initial/self.final
    
    def updateQuotes(self):
        """Transforms de price of the quotes of the array"""
        self.quotes=QuoteAllIntradayManager(self.mem)
        self.quotes.load_from_db(self.product)
        for setquoteintraday in self.quotes.arr:
            for q in setquoteintraday.arr:
                if self.dtinitial<=q.datetime and self.dtfinal>=q.datetime:
                    q.quote=self.convertPrices(q.quote)
                    q.save()
                    
    def updateDPS(self):
        set=DPSManager(self.mem, self.product)
        set.load_from_db()
        for d in set.arr:
            if self.dtinitial.date()<=d.date and self.dtfinal.date()>=d.date:
                d.gross=self.convertPrices(d.gross)
                d.save()
        
    def updateEPS(self):
        pass
        
    def updateEstimationsDPS(self):
        set=EstimationDPSManager(self.mem, self.product)
        set.load_from_db()
        for d in set.arr:
            if self.dtinitial.year<=d.year and self.dtfinal.year>=d.year:
                d.estimation=self.convertPrices(d.estimation)
                d.save()
        
    def updateEstimationsEPS(self):
        set=EstimationEPSManager(self.mem, self.product)
        set.load_from_db()
        for d in set.arr:
            if self.dtinitial.year<=d.year and self.dtfinal.year>=d.year:
                d.estimation=self.convertPrices(d.estimation)
                d.save()
        
        
    def updateOperInvestments(self):
        """Transforms de number of shares and its price of the array of InvestmentOperation"""
        for inv in self.mem.data.investments.arr:
            if inv.product.id==self.product.id:
                for oi in inv.op.arr:
                    if self.dtinitial<=oi.datetime and self.dtfinal>=oi.datetime:
                        oi.shares=self.convertShares(oi.shares)
                        oi.valor_accion=self.convertPrices(oi.valor_accion)
                        oi.save(autocommit=False)

        
    def updateDividends(self):
        """Transforms de dpa of an array of dividends"""
        for inv in self.mem.data.investments.arr:
            if inv.product.id==self.product.id:
                dividends=DividendHomogeneusManager(self.mem, inv)
                dividends.load_from_db("select * from dividends where id_inversiones={0} order by fecha".format(inv.id ))  
                for d in dividends.arr:
                    if self.dtinitial<=d.datetime and self.dtfinal>=d.datetime:
                        d.dpa=self.convertPrices(d.dpa)
                    d.save()
        
    def type(self):
        """Función que devuelve si es un Split o contrasplit"""
        if self.initial>self.final:
            return "Contrasplit"
        else:
            return "Split"
            
    def makeSplit(self):
        """All calculates to make the split"""        
        self.updateDPS()
        self.updateEstimationsDPS()
        self.updateEstimationsEPS()
        self.updateOperInvestments()
        self.updateDividends()
        self.updateQuotes()
        self.mem.con.commit()

