from PyQt5.QtCore import QObject
from datetime import date
from xulpymoney.datetime_functions import dtaware_day_end_from_date
from xulpymoney.libmanagers import ObjectManager
from xulpymoney.objects.percentage import Percentage
from xulpymoney.objects.quote import Quote
from xulpymoney.ui.myqtablewidget import qcenter, qdate, qleft, qnumber, wdgBool
class EstimationDPS:
    """Dividends por acción"""
    def __init__(self, mem):
        self.mem=mem
        self.product=None#pk
        self.year=None#pk
        self.date_estimation=None
        self.source=None
        self.estimation=None
        self.manual=None
        
    def __repr__(self):
        return "EstimationDPS: Product {0}. Year {1}. Estimation {2}".format(self.product.id, self.year, self.estimation)
        
    def init__create(self, product, year, date_estimation, source, manual, estimation):
        self.product=product
        self.year=year
        self.date_estimation=date_estimation
        self.source=source
        self.manual=manual
        self.estimation=estimation
        return self

    def init__from_db(self, product,  currentyear):
        """Saca el registro  o uno en blanco si no lo encuentra, que fueron pasados como parámetro"""
        cur=self.mem.con.cursor()
        cur.execute("select estimation, date_estimation ,source,manual from estimations_dps where id=%s and year=%s", (product.id, currentyear))
        if cur.rowcount==1:
            row=cur.fetchone()
            self.init__create(product, currentyear, row['date_estimation'], row['source'], row['manual'], row['estimation'])
            cur.close()
        else:
            self.init__create(product, currentyear, None, None, None, None)
        return self
            
            
    def borrar(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from estimations_dps where id=%s and year=%s", (self.product.id, self.year))
        cur.close()
            
    def save(self):
        """Función que comprueba si existe el registro para insertar o modificarlo según proceda"""
        cur=self.mem.con.cursor()
        cur.execute("select count(*) from estimations_dps where id=%s and year=%s", (self.product.id, self.year))
        if cur.fetchone()[0]==0:
            cur.execute("insert into estimations_dps(id, year, estimation, date_estimation, source, manual) values (%s,%s,%s,%s,%s,%s)", (self.product.id, self.year, self.estimation, self.date_estimation, self.source, self.manual))
        elif self.estimation!=None:            
            cur.execute("update estimations_dps set estimation=%s, date_estimation=%s, source=%s, manual=%s where id=%s and year=%s", (self.estimation, self.date_estimation, self.source, self.manual, self.product.id, self.year))
        cur.close()
        
    def percentage(self):
        """Hay que tener presente que lastyear (Objeto Quote) es el lastyear del año actual
        Necesita tener cargado en id el lastyear """
        return Percentage(self.estimation, self.product.result.basic.last.quote)
        
class EstimationEPS:
    """Beneficio por acción. Earnings per share Beneficio por acción. Para los calculos usaremos
    esto, aunque sean estimaciones."""

    def __init__(self, mem):
        self.mem=mem
        self.product=None#pk
        self.year=None#pk
        self.date_estimation=None
        self.source=None
        self.estimation=None
        self.manual=None
        
    def init__create(self, product, year, date_estimation, source, manual, estimation):
        self.product=product
        self.year=year
        self.date_estimation=date_estimation
        self.source=source
        self.manual=manual
        self.estimation=estimation
        return self

    def init__from_db(self, product,  currentyear):
        """Saca el registro  o uno en blanco si no lo encuentra, que fueron pasados como parámetro"""
        cur=self.mem.con.cursor()
        cur.execute("select estimation, date_estimation ,source,manual from estimations_eps where id=%s and year=%s", (product.id, currentyear))
        if cur.rowcount==1:
            row=cur.fetchone()
            self.init__create(product, currentyear, row['date_estimation'], row['source'], row['manual'], row['estimation'])
            cur.close()
        else:
            self.init__create(product, currentyear, None, None, None, None)
        return self
            
            
    def borrar(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from estimations_eps where id=%s and year=%s", (self.product.id, self.year))
        cur.close()
            
    def save(self):
        """Función que comprueba si existe el registro para insertar o modificarlo según proceda"""
        cur=self.mem.con.cursor()
        cur.execute("select count(*) from estimations_eps where id=%s and year=%s", (self.product.id, self.year))
        if cur.fetchone()[0]==0:
            cur.execute("insert into estimations_eps(id, year, estimation, date_estimation, source, manual) values (%s,%s,%s,%s,%s,%s)", (self.product.id, self.year, self.estimation, self.date_estimation, self.source, self.manual))
        elif self.estimation!=None:            
            cur.execute("update estimations_eps set estimation=%s, date_estimation=%s, source=%s, manual=%s where id=%s and year=%s", (self.estimation, self.date_estimation, self.source, self.manual, self.product.id, self.year))
        cur.close()
        
        
    def PER(self, last_year_quote_of_estimation):
        """Price to Earnings Ratio"""
        try:
            return last_year_quote_of_estimation.quote/self.estimation
        except:
            return None
class EstimationDPSManager(ObjectManager, QObject):
    def __init__(self, mem,  product):
        ObjectManager.__init__(self)
        QObject.__init__(self)
        self.arr=[]
        self.mem=mem   
        self.product=product
    
    def estimacionNula(self, year):
        return EstimationDPS(self.mem).init__create(self.product, year, date.today(), "None Estimation", None, None)
    
    def load_from_db(self):
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute( "select * from estimations_dps where id=%s order by year", (self.product.id, ))
        for row in cur:
            self.arr.append(EstimationDPS(self.mem).init__from_db(self.product, row['year']))
        cur.close()            
        
    def find(self, year):
        """Como puede no haber todos los años se usa find que devuelve una estimacion nula sino existe"""
        for e in self.arr:
            if e.year==year:
                return e
        return self.estimacionNula(year)
            
    def currentYear(self):
        return self.find(date.today().year)

    def dias_sin_actualizar(self):
        """Si no hay datos devuelve 1000"""
        self.sort()
        try:
            ultima=self.arr[len(self.arr)-1].date_estimation
            return (date.today()-ultima).days
        except:
            return 1000

    def sort(self):
        self.arr=sorted(self.arr, key=lambda c: c.year,  reverse=False)         
        
    def myqtablewidget(self, wdg):
        wdg.table.setColumnCount(6)
        wdg.table.setHorizontalHeaderItem(0, qcenter(self.tr("Year")))
        wdg.table.setHorizontalHeaderItem(1, qcenter(self.tr("Estimation")))
        wdg.table.setHorizontalHeaderItem(2, qcenter(self.tr("Percentage")))
        wdg.table.setHorizontalHeaderItem(3, qcenter(self.tr("Estimation date")))
        wdg.table.setHorizontalHeaderItem(4, qcenter(self.tr("Source")))
        wdg.table.setHorizontalHeaderItem(5, qcenter(self.tr("Manual")))
        self.sort()  
        wdg.applySettings()
        wdg.table.clearContents()
        wdg.table.setRowCount(len(self.arr))
        for i, e in enumerate(self.arr):
            wdg.table.setItem(i, 0, qcenter(str(e.year)))
            wdg.table.setItem(i, 1, self.product.money(e.estimation).qtablewidgetitem(6))
            wdg.table.setItem(i, 2, e.percentage().qtablewidgetitem())
            wdg.table.setItem(i, 3, qdate(e.date_estimation))
            wdg.table.setItem(i, 4, qleft(e.source))
            wdg.table.setCellWidget(i, 5, wdgBool(e.manual))

        wdg.table.setCurrentCell(len(self.arr)-1, 0)
        wdg.table.setFocus()

class EstimationEPSManager(ObjectManager, QObject):
    def __init__(self, mem,  product):
        ObjectManager.__init__(self)
        QObject.__init__(self)
        self.arr=[]
        self.mem=mem   
        self.product=product
    
    def estimacionNula(self, year):
        return EstimationEPS(self.mem).init__create(self.product, year, date.today(), "None Estimation", None, None)
    
    def load_from_db(self):
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute( "select * from estimations_eps where id=%s order by year", (self.product.id, ))
        for row in cur:
            self.arr.append(EstimationEPS(self.mem).init__from_db(self.product, row['year']))
        cur.close()            
        
    def find(self, year):
        """Como puede no haber todos los años se usa find que devuelve una estimacion nula sino existe"""
        for e in self.arr:
            if e.year==year:
                return e
        return self.estimacionNula(year)
            
    def currentYear(self):
        return self.find(date.today().year)

    def dias_sin_actualizar(self):
        ultima=date(1990, 1, 1)
        for k, v in self.dic.items():
            if v.date_estimation>ultima:
                ultima=v.date_estimation
        return (date.today()-ultima).days
        
        
    def sort(self):
        self.arr=sorted(self.arr, key=lambda c: c.year,  reverse=False)         
        
    def myqtablewidget(self, wdg):
        wdg.table.setColumnCount(6)
        wdg.table.setHorizontalHeaderItem(0, qcenter(self.tr("Year")))
        wdg.table.setHorizontalHeaderItem(1, qcenter(self.tr("Estimation")))
        wdg.table.setHorizontalHeaderItem(2, qcenter(self.tr("PER")))
        wdg.table.setHorizontalHeaderItem(3, qcenter(self.tr("Estimation date")))
        wdg.table.setHorizontalHeaderItem(4, qcenter(self.tr("Source")))
        wdg.table.setHorizontalHeaderItem(5, qcenter(self.tr("Manual")))
        self.sort()     
        wdg.applySettings()
        wdg.table.clearContents()
        wdg.table.setRowCount(len(self.arr))
        for i, e in enumerate(self.arr):
            wdg.table.setItem(i, 0, qcenter(str(e.year)))
            wdg.table.setItem(i, 1, self.product.money(e.estimation).qtablewidgetitem())       
            wdg.table.setItem(i, 2, qnumber(e.PER(Quote(self.mem).init__from_query(self.product, dtaware_day_end_from_date(date(e.year, 12, 31), self.product.stockmarket.zone.name)))))
            wdg.table.setItem(i, 3, qdate(e.date_estimation))
            wdg.table.setItem(i, 4, qleft(e.source))
            wdg.table.setCellWidget(i, 5, wdgBool(e.manual)) 
        wdg.table.setCurrentCell(len(self.arr)-1, 0)
        wdg.table.setFocus()
