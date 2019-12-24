from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from xulpymoney.datetime_functions import dtaware_day_end_from_date
from  xulpymoney.libmanagers import ObjectManager_With_IdDate
from xulpymoney.objects.ohcl import OHCLDaily, OHCLDailyManager
from xulpymoney.ui.qtablewidgetitems import qcenter
class DPS:
    """Dividend por acción pagados. Se usa para pintar gráficos sin dividends"""
    def __init__(self, mem,  product):
        self.mem=mem
        self.product=product
        self.id=None#id_dps
        self.date=None#pk
        self.gross=None#bruto
        
    def __repr__(self):
        return "DPS. Id: {0}. Gross: {1}".format(self.id, self.gross)
        
    def init__create(self, date, gross, id=None):
        self.date=date
        self.gross=gross
        self.id=id
        return self

    def init__from_db_row(self,  row):
        """Saca el registro  o uno en blanco si no lo encuentra, que fueron pasados como parámetro"""
        return self.init__create(row['date'], row['gross'], row['id_dps'])
        
    def borrar(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from dps where id_dps=%s", (self.id,))
        cur.close()
            
    def save(self):
        """Función que comprueba si existe el registro para insertar o modificarlo según proceda"""
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into dps(date, gross,id) values (%s,%s,%s) returning id_dps", (self.date, self.gross, self.product.id))
            self.id=cur.fetchone()[0]
        else:         
            cur.execute("update dps set date=%s, gross=%s, id=%s where id_dps=%s", (self.date,  self.gross, self.product.id, self.id))
        cur.close()
        
class DPSManager(ObjectManager_With_IdDate):
    def __init__(self, mem,  product):
        ObjectManager_With_IdDate.__init__(self)
        self.mem=mem   
        self.product=product
    
    def load_from_db(self):
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute( "select * from dps where id=%s order by date", (self.product.id, ))
        for row in cur:
            self.arr.append(DPS(self.mem, self.product).init__from_db_row(row))
        cur.close()            
    
    def save(self):
        """
            Saves DPS Without commit
        """            
        for o in self.arr:
            o.save()
        
    def myqtablewidget(self, table):
        table.setColumnCount(2)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("Mem", "Date" )))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("Mem", "Gross" )))
        self.order_by_date()   
        table.applySettings()
        table.clearContents()
        table.setRowCount(len(self.arr))
        for i, e in enumerate(self.arr):
            table.setItem(i, 0, qcenter(str(e.date)))
            table.setItem(i, 1, self.product.currency.qtablewidgetitem(e.gross, 6))       
        table.setCurrentCell(len(self.arr)-1, 0)
    
    def adjustPrice(self, datetime, price):
        """
            Returns a new price adjusting
        """
        r=price
        for dps in self.arr:
            if datetime>dtaware_day_end_from_date(dps.date, self.mem.localzone_name):
                r=r+dps.gross
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


        
