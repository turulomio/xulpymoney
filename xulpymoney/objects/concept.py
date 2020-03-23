from PyQt5.QtCore import QObject
from datetime import date, timedelta
from decimal import Decimal
from xulpymoney.libmanagers import ObjectManager_With_IdName_Selectable
from xulpymoney.libxulpymoneytypes import eConcept
## Class to manage operation concepts for expenses, incomes... For example: Restuarant, Supermarket
class Concept:
    ## Constructor with the following attributes combination
    ## 1. Concept(mem). Create a Concept with all attributes to None
    ## 2. Concept(mem, row, tipooperacion). Create a Concept from a db row, generated in a database query
    ## 3. Concept(mem, name, tipooperacion,editable, id). Create a Concept passing all attributes
    ## @param mem MemXulpymoney object
    ## @param row Dictionary of a database query cursor
    ## @param tipooperacion OperationType Bank object
    ## @param name Concept name
    ## @param editable Boolean that sets if a Concept is editable by the user
    ## @param id Integer that sets the id of an Concept. You must set id=None if the Concept is not in the database. id is set in the save method
    def __init__(self, mem=None, name=None, tipooperacion=None, editable=None, id=None):
        self.mem=mem
        self.id=id
        self.name=name
        self.tipooperacion=tipooperacion
        self.editable=editable

    def fullName(self):
        return self.mem.trHS(self.name)

    def __repr__(self):
        return ("Instancia de Concept: {0} -- {1} ({2})".format( self.name, self.tipooperacion.name,  self.id))

    def save(self):
        if self.id==None:
            self.id=self.mem.con.cursor_one_field("insert into conceptos (concepto, id_tiposoperaciones, editable) values (%s, %s, %s) returning id_conceptos", (self.name, self.tipooperacion.id, self.editable))
        else:
            self.mem.con.execute("update conceptos set concepto=%s, id_tiposoperaciones=%s, editable=%s where id_conceptos=%s", (self.name, self.tipooperacion.id, self.editable, self.id))

    def is_deletable(self):
        """Función que devuelve un booleano si una cuenta es borrable, es decir, que no tenga registros dependientes."""
        if self.uses()>0 and self.editable==True:
            return False
        return True
        
    def uses(self):
        """Returns the number of uses in opercuenta and opertarjetas"""
        cur=self.mem.con.cursor()
        cur.execute("select count(*) from opercuentas where id_conceptos=%s", (self.id, ))
        opercuentas=cur.fetchone()[0]
        cur.execute("select count(*) from opertarjetas where id_conceptos=%s", (self.id, ))
        opertarjetas=cur.fetchone()[0]
        cur.close()
        return opercuentas+opertarjetas

    def borrar(self):
        if self.is_deletable():
            cur=self.mem.con.cursor()        
            cur.execute("delete from conceptos where id_conceptos=%s", (self.id, ))
            cur.close()
            return True
        return False

    def media_mensual(self):
        cur=self.mem.con.cursor()
        cur.execute("select datetime from opercuentas where id_conceptos=%s union all select datetime from opertarjetas where id_conceptos=%s order by datetime limit 1", (self.id, self.id))
        res=cur.fetchone()
        if res==None:
            primerafecha=date.today()-timedelta(days=1)
        else:
            primerafecha=res['datetime'].date()
        cur.execute("select sum(importe) as suma from opercuentas where id_conceptos=%s union all select sum(importe) as suma from opertarjetas where id_conceptos=%s", (self.id, self.id))
        suma=Decimal(0)
        for i in cur:
            if i['suma']==None:
                continue
            suma=suma+i['suma']
        cur.close()
        return Decimal(30)*suma/((date.today()-primerafecha).days+1)
        
    def mensual(self,   year,  month):  
        """Saca el gasto mensual de este concepto"""
        cur=self.mem.con.cursor()
        cur.execute("select sum(importe) as suma from opercuentas where id_conceptos=%s and date_part('month',datetime)=%s and date_part('year', datetime)=%s union all select sum(importe) as suma from opertarjetas where id_conceptos=%s  and date_part('month',datetime)=%s and date_part('year', datetime)=%s", (self.id,  month, year,  self.id,  month, year  ))
        suma=0
        for i in cur:
            if i['suma']==None:
                continue
            suma=suma+i['suma']
        cur.close()
        return suma

class ConceptManager(ObjectManager_With_IdName_Selectable, QObject):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        QObject.__init__(self)
        self.mem=mem 

    def load_opercuentas_qcombobox(self, combo):
        """Carga conceptos operaciones 1,2,3, menos dividends y renta fija, no pueden ser editados, luego no se necesitan"""
        for c in self.arr:
            if c.tipooperacion.id in (1, 2, 3, 11):
                if c.id not in (39, 50, 62, 63, 65, 66):
                    combo.addItem("{0} -- {1}".format(  c.name,  c.tipooperacion.name),  c.id  )

    def load_dividend_qcombobox(self, combo,  select=None):
        """Select es un class Concept"""
        for n in (39, 50,  62):
            c=self.find_by_id(n)
            combo.addItem("{0} -- {1}".format(  c.name,  c.tipooperacion.name),  c.id   )
        if select!=None:
            combo.setCurrentIndex(combo.findData(select.id))

    def load_bonds_qcombobox(self, combo,  select=None):
        """Carga conceptos operaciones 1,2,3"""
        for n in (50, 63, 65, 66):
            c=self.find_by_id(n)
            combo.addItem("{0} -- {1}".format(  c.name,  c.tipooperacion.name),  c.id )
        if select!=None:
            combo.setCurrentIndex(combo.findData(select.id))

    def load_futures_qcombobox(self, combo,  select=None):
        for n in (eConcept.RolloverPaid, eConcept.RolloverReceived):
            c=self.find_by_id(n)
            combo.addItem("{0} -- {1}".format(  c.name,  c.tipooperacion.name),  c.id )
        if select!=None:
            combo.setCurrentIndex(combo.findData(select.id))

    def considered_dividends_in_totals(self):
        """El 63 es pago de cupon corrido y no es considerado dividend  a efectos de totales, sino gasto."""
        return[39, 50, 62, 65, 66]


    def ConceptManager_by_operation_type(self, id_tiposoperaciones):
        """SSe usa clone y no init ya que ya están cargados en MEM"""
        resultado=ConceptManager(self.mem)
        for c in self.arr:
            if c.tipooperacion.id==id_tiposoperaciones:
                resultado.append(c)
        return resultado
        
    def ConceptManager_editables(self):
        """SSe usa clone y no init ya que ya están cargados en MEM"""
        resultado=ConceptManager(self.mem)
        for c in self.arr:
            if c.editable==True:
                resultado.append(c)
        return resultado
        
    def percentage_monthly(self, year, month):
        """ Generates an arr with:
        1) Concept:
        2) Monthly expense
        3) Percentage expenses of all conceptos this month
        4) Monthly average from first operation
        
        Returns three fields:
        1) dictionary arr, whith above values, sort by concepto.name
        2) total expenses of all concepts                            
        3) total average expenses of all conceptos
        """
        ##Fills column 0 and 1, 3 and gets totalexpenses
        arr=[]
        totalexpenses=Decimal(0)
        totalmedia_mensual=Decimal(0)
        for v in self.arr:
            thismonth=v.mensual(year, month)
            if thismonth==Decimal(0):
                continue
            totalexpenses=totalexpenses+thismonth
            media_mensual=v.media_mensual()
            totalmedia_mensual=totalmedia_mensual+media_mensual
            arr.append([v, thismonth, None,  media_mensual])
        
        ##Fills column 2 and calculates percentage
        for  v in arr:
            if totalexpenses==Decimal(0):
                v[2]=Decimal(0)
            else:
                v[2]=Decimal(100)*v[1]/totalexpenses
        
        arr=sorted(arr, key=lambda o:o[1])
        return (arr, totalexpenses,  totalmedia_mensual)

    ## @param wdg mqtwObjects
    def mqtw(self, wdg):
        data=[]
        for i, o in enumerate(self.arr):
            data.append([
                o.fullName(), 
                o.tipooperacion.name, 
                o, 
            ])
        wdg.setDataWithObjects(
            [self.tr("Name"), self.tr("Operation type")], 
            None, 
            data
        )

def Concept_from_dict(mem, row):
    tipooperacion=mem.tiposoperaciones.find_by_id(row['id_tiposoperaciones'])
    return Concept(mem, row['concepto'], tipooperacion, row['editable'], row['id_conceptos'])
    
def ConceptManager_from_sql(mem, sql):   
    r=ConceptManager(mem)
    for row in mem.con.cursor_rows(sql):
        r.append(Concept_from_dict(mem, row))
    return r
