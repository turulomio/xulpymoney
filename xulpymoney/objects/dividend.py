from PyQt5.QtCore import QObject
from datetime import date
from xulpymoney.libmanagers import ObjectManager_With_IdDatetime_Selectable
from xulpymoney.libxulpymoneytypes import eMoneyCurrency, eComment
from xulpymoney.objects.money import Money
from xulpymoney.objects.percentage import Percentage
from xulpymoney.ui.myqtablewidget import qcenter, qleft, qdatetime

class Dividend:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.investment=None
        self.bruto=None
        self.retencion=None
        self.neto=None
        self.dpa=None
        self.datetime=None
        self.opercuenta=None
        self.comision=None
        self.concepto=None#Puedeser 39 o 62 para derechos venta
        self.currency_conversion=None

    def __repr__(self):
        return ("Instancia de Dividend: {0} ({1})".format( self.neto, self.id))
        
    def init__create(self,  inversion,  bruto,  retencion, neto,  dpa,  fecha,  comision,  concepto, currency_conversion,  opercuenta=None,  id=None):
        """Opercuenta puede no aparecer porque se asigna al hacer un save que es cuando se crea. Si id=None,opercuenta debe ser None"""
        self.id=id
        self.investment=inversion
        self.bruto=bruto
        self.retencion=retencion
        self.neto=neto
        self.dpa=dpa
        self.datetime=fecha
        self.opercuenta=opercuenta
        self.comision=comision
        self.concepto=concepto
        self.currency_conversion=currency_conversion
        return self
        
    def init__db_row(self, row, inversion,  opercuenta,  concepto):
        return self.init__create(inversion,  row['bruto'],  row['retencion'], row['neto'],  row['valorxaccion'],  row['fecha'],   row['comision'],  concepto, row['currency_conversion'], opercuenta, row['id_dividends'])
        
    def init__db_query(self, id):
        """
            Searches in db dividend, investment from memory, operaccount from db
        """
        row=self.mem.con.cursor_one_row("select * from dividends where id_dividends=%s", (id, ))
        from xulpymoney.objects.accountoperation import AccountOperation
        accountoperation=AccountOperation(self.mem,  row['id_opercuentas'])
        return self.init__db_row(row, self.mem.data.investments.find_by_id(row['id_inversiones']), accountoperation, self.mem.conceptos.find_by_id(row['id_conceptos']))
        
    def borrar(self):
        """Borra un dividend, para ello borra el registro de la tabla dividends 
            y el asociado en la tabla opercuentas
            
            También actualiza el balance de la cuenta."""
        cur=self.mem.con.cursor()
        self.opercuenta.borrar()
        cur.execute("delete from dividends where id_dividends=%s", (self.id, ))
        cur.close()
        
    def gross(self, type=eMoneyCurrency.Product):
        if type==1:
            return Money(self.mem, self.bruto, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.bruto, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.bruto, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)

    def net(self, type=eMoneyCurrency.Product):
        if type==1:
            return Money(self.mem, self.neto, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.neto, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.neto, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
    def retention(self, type=eMoneyCurrency.Product):
        if type==1:
            return Money(self.mem, self.retencion, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.retencion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.retencion, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
    def dps(self, type=eMoneyCurrency.Product):
        "Dividend per share"
        if type==1:
            return Money(self.mem, self.dpa, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.dpa, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.dpa, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
    def commission(self, type=eMoneyCurrency.Product):
        if type==1:
            return Money(self.mem, self.comision, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.comision, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.comision, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
            
    def copy(self ):
        return Dividend(self.mem).init__create(self.investment, self.bruto, self.retencion, self.neto, self.dpa, self.datetime, self.comision, self.concepto, self.currency_conversion, self.opercuenta, self.id)
        
    def neto_antes_impuestos(self):
        return self.bruto-self.comision
    
    def save(self):
        """Insertar un dividend y una opercuenta vinculada a la tabla dividends en el campo id_opercuentas
        
        En caso de que sea actualizar un dividend hay que actualizar los datos de opercuenta y se graba desde aquí. No desde el objeto opercuenta
        
        Actualiza la cuenta 
        """
        from xulpymoney.objects.accountoperation import AccountOperation
        from xulpymoney.objects.comment import Comment
        if self.id==None:#Insertar
            self.opercuenta=AccountOperation(self.mem,  self.datetime,self.concepto, self.concepto.tipooperacion, self.neto, "Transaction not finished", self.investment.account, None)
            self.opercuenta.save()
            self.id=self.mem.con.cursor_one_field("insert into dividends (fecha, valorxaccion, bruto, retencion, neto, id_inversiones,id_opercuentas, comision, id_conceptos,currency_conversion) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) returning id_dividends", (self.datetime, self.dpa, self.bruto, self.retencion, self.neto, self.investment.id, self.opercuenta.id, self.comision, self.concepto.id, self.currency_conversion))
            self.opercuenta.comentario=Comment(self.mem).encode(eComment.Dividend, self)
            self.opercuenta.save()
        else:
            self.opercuenta.datetime=self.datetime
            self.opercuenta.importe=self.neto
            self.opercuenta.comentario=Comment(self.mem).encode(eComment.Dividend, self)
            self.opercuenta.concepto=self.concepto
            self.opercuenta.tipooperacion=self.concepto.tipooperacion
            self.opercuenta.save()
            self.mem.con.execute("update dividends set fecha=%s, valorxaccion=%s, bruto=%s, retencion=%s, neto=%s, id_inversiones=%s, id_opercuentas=%s, comision=%s, id_conceptos=%s, currency_conversion=%s where id_dividends=%s", (self.datetime, self.dpa, self.bruto, self.retencion, self.neto, self.investment.id, self.opercuenta.id, self.comision, self.concepto.id, self.currency_conversion, self.id))

class DividendHeterogeneusManager(ObjectManager_With_IdDatetime_Selectable, QObject):
    """Class that  groups dividends from a Xulpymoney Product"""
    def __init__(self, mem):
        ObjectManager_With_IdDatetime_Selectable.__init__(self)
        QObject.__init__(self)
        self.setConstructorParameters(mem)
        self.mem=mem
            
    ## Net amount in self.mem.localcurrency
    def net(self):
        r=Money(self.mem, 0, self.mem.localcurrency)
        for d in self.arr:
            r=r+d.net(eMoneyCurrency.User)
        return r

    ## Gross amount in self.mem.localcurrency
    def gross(self):
        r=Money(self.mem, 0, self.mem.localcurrency)
        for d in self.arr:
            r=r+d.gross(eMoneyCurrency.User)
        return r
    ## retention amount in self.mem.localcurrency
    def retention(self):
        r=Money(self.mem, 0, self.mem.localcurrency)
        for d in self.arr:
            r=r+d.retention(eMoneyCurrency.User)
        return r

    ## commission amount in self.mem.localcurrency
    def commission(self):
        r=Money(self.mem, 0, self.mem.localcurrency)
        for d in self.arr:
            r=r+d.commission(eMoneyCurrency.User)
        return r

    def load_from_db(self, sql):    
        del self.arr
        self.arr=[]
        cur=self.mem.con.cursor()
        cur.execute( sql)#"select * from dividends where id_inversiones=%s order by fecha", (self.investment.id, )
        for row in cur:
            from xulpymoney.objects.accountoperation import AccountOperation
            inversion=self.mem.data.investments.find_by_id(row['id_inversiones'])
            oc=AccountOperation(self.mem, row['id_opercuentas'])
            self.arr.append(Dividend(self.mem).init__db_row(row, inversion, oc, self.mem.conceptos.find_by_id(row['id_conceptos']) ))
        cur.close()      

    def myqtablewidget(self, wdg,   type=eMoneyCurrency.User):
        hh=[self.tr("Date"), self.tr("Product"), self.tr("Concept"), self.tr("Gross"), self.tr("Withholding"), self.tr("Commission"), self.tr("Net"), self.tr("DPS")]
        data=[]
        for i, o in enumerate(self.arr):
            data.append([
                o.datetime, 
                o.investment.fullName(), 
                o.opercuenta.concepto.name, 
                o.gross(type), 
                o.retention(type), 
                o.commission(type), 
                o.net(type), 
                o.dps(type), 
                o,
            ])

        wdg.setDataWithObjects(hh, None, data, additional=self.myqtablewidget_additional, zonename=self.mem.localzone_name)

    def myqtablewidget_additional(self, wdg):
        wdg.table.setRowCount(wdg.length()+1)
        wdg.addRow(wdg.length(), [self.tr("Total"), "#crossedout", "#crossedout", self.gross(), self.retention(), self.commission(),self.net(), "#crossedout",], zonename=self.mem.localzone_name)

class DividendHomogeneusManager(DividendHeterogeneusManager):
    def __init__(self, mem, investment):
        DividendHeterogeneusManager.__init__(self, mem)
        self.setConstructorParameters(mem, investment)
        self.investment=investment
        
    ## @param emoneycurrency eMoneyCurrency type
    ## @param current If true only shows dividends from first current operation. If false show all dividends
    def gross(self, emoneycurrency, current):
        r=Money(self.mem, 0, self.investment.resultsCurrency(emoneycurrency))
        for d in self.arr:
            if current==True and self.investment.op_actual.length()>0  and d.datetime<self.investment.op_actual.first().datetime:
                continue
            else:
                r=r+d.gross(emoneycurrency)
        return r

    ## @param emoneycurrency eMoneyCurrency type
    ## @param current If true only shows dividends from first current operation. If false show all dividends
    def net(self, emoneycurrency, current):
        r=Money(self.mem, 0, self.investment.resultsCurrency(emoneycurrency))
        for d in self.arr:
            if current==True and self.investment.op_actual.length()>0 and d.datetime<self.investment.op_actual.first().datetime:
                continue
            else:
                r=r+d.net(emoneycurrency)
        return r

    ## @param emoneycurrency eMoneyCurrency type
    ## @param current If true only shows dividends from first current operation. If false show all dividends
    def percentage_from_invested(self, emoneycurrency, current):
        return Percentage(self.gross(emoneycurrency, current), self.investment.invertido(None, emoneycurrency))

    ## @param emoneycurrency eMoneyCurrency type
    ## @param current If true only shows dividends from first current operation. If false show all dividends
    def percentage_tae_from_invested(self, emoneycurrency, current):
        try:
            dias=(date.today()-self.investment.op_actual.first().datetime.date()).days+1
            return Percentage(self.percentage_from_invested(emoneycurrency, current)*365, dias )
        except:#No first
            return Percentage()
        
    ## Method that fills a qtablewidget with dividend data
    ## @param table QTableWidget
    ## @param emoneycurrency eMoneyCurrency type
    ## @param current If true only shows dividends from first current operation. If false show all dividends
    def myqtablewidget(self, wdg, emoneycurrency, current=True):
        wdg.table.setColumnCount(7)
        wdg.table.setHorizontalHeaderItem(0, qcenter(self.tr("Date" )))
        wdg.table.setHorizontalHeaderItem(1, qcenter(self.tr("Concept" )))
        wdg.table.setHorizontalHeaderItem(2, qcenter(self.tr("Gross" )))
        wdg.table.setHorizontalHeaderItem(3, qcenter(self.tr("Withholding" )))
        wdg.table.setHorizontalHeaderItem(4, qcenter(self.tr("Comission" )))
        wdg.table.setHorizontalHeaderItem(5, qcenter(self.tr("Net" )))
        wdg.table.setHorizontalHeaderItem(6, qcenter(self.tr("DPS" )))
        #DATA  
        wdg.applySettings()
        wdg.table.clearContents()

        currency=self.investment.resultsCurrency(emoneycurrency)

        wdg.table.setRowCount(self.length()+1)
        sumneto=Money(self.mem, 0, currency)
        sumbruto=Money(self.mem, 0, currency)
        sumretencion=Money(self.mem, 0, currency)
        sumcomision=Money(self.mem, 0, currency)
        for i, d in enumerate(self.arr):
            if current==True and self.investment.op_actual.length()>0 and d.datetime<self.investment.op_actual.first().datetime:
                wdg.table.hideRow(i)
                continue
            else:
                wdg.table.showRow(i)
            sumneto=sumneto+d.net(emoneycurrency)
            sumbruto=sumbruto+d.gross(emoneycurrency)
            sumretencion=sumretencion+d.retention(emoneycurrency)
            sumcomision=sumcomision+d.commission(emoneycurrency)
            wdg.table.setItem(i, 0, qdatetime(d.datetime, self.mem.localzone_name))
            wdg.table.setItem(i, 1, qleft(d.opercuenta.concepto.name))
            wdg.table.setItem(i, 2, d.gross(emoneycurrency).qtablewidgetitem())
            wdg.table.setItem(i, 3, d.retention(emoneycurrency).qtablewidgetitem())
            wdg.table.setItem(i, 4, d.commission(emoneycurrency).qtablewidgetitem())
            wdg.table.setItem(i, 5, d.net(emoneycurrency).qtablewidgetitem())
            wdg.table.setItem(i, 6, d.dps(emoneycurrency).qtablewidgetitem())
        wdg.table.setItem(self.length(), 1, qleft(self.tr("TOTAL")))
        wdg.table.setItem(self.length(), 2, sumbruto.qtablewidgetitem())
        wdg.table.setItem(self.length(), 3, sumretencion.qtablewidgetitem())
        wdg.table.setItem(self.length(), 4, sumcomision.qtablewidgetitem())
        wdg.table.setItem(self.length(), 5, sumneto.qtablewidgetitem())
        return (sumneto, sumbruto, sumretencion, sumcomision)
        
