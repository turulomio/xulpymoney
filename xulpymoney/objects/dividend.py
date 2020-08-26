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
        self._gross=None
        self.taxes=None
        self._net=None
        self.dpa=None
        self.datetime=None
        self.opercuenta=None
        self._commission=None
        self.concept=None#Puedeser 39 o 62 para derechos selling_price
        self.currency_conversion=None

    def __repr__(self):
        return ("Instancia de Dividend: {0} ({1})".format( self._net, self.id))
        
    def init__create(self,  inversion,  gross,  taxes, net,  dpa,  fecha,  commission,  concept, currency_conversion,  opercuenta=None,  id=None):
        """Opercuenta puede no aparecer porque se asigna al hacer un save que es cuando se crea. Si id=None,opercuenta debe ser None"""
        self.id=id
        self.investment=inversion
        self._gross=gross
        self.taxes=taxes
        self._net=net
        self.dpa=dpa
        self.datetime=fecha
        self.opercuenta=opercuenta
        self._commission=commission
        self.concept=concept
        self.currency_conversion=currency_conversion
        return self
        
    def init__db_row(self, row, inversion,  opercuenta,  concept):
        return self.init__create(inversion,  row['gross'],  row['taxes'], row['net'],  row['dps'],  row['datetime'],   row['commission'],  concept, row['currency_conversion'], opercuenta, row['id'])
        
    def init__db_query(self, id):
        """
            Searches in db dividend, investment from memory, operaccount from db
        """
        row=self.mem.con.cursor_one_row("select * from dividends where id=%s", (id, ))
        from xulpymoney.objects.accountoperation import AccountOperation
        accountoperation=AccountOperation(self.mem,  row['accountsoperations_id'])
        return self.init__db_row(row, self.mem.data.investments.find_by_id(row['investments_id']), accountoperation, self.mem.concepts.find_by_id(row['concepts_id']))
        
    def borrar(self):
        """Borra un dividend, para ello borra el registro de la tabla dividends 
            y el asociado en la tabla accountsoperations
            
            También actualiza el balance de la cuenta."""
        cur=self.mem.con.cursor()
        self.opercuenta.borrar()
        cur.execute("delete from dividends where id_dividends=%s", (self.id, ))
        cur.close()
        
    def gross(self, type=eMoneyCurrency.Product):
        if type==1:
            return Money(self.mem, self._gross, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self._gross, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self._gross, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)

    def net(self, type=eMoneyCurrency.Product):
        if type==1:
            return Money(self.mem, self._net, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self._net, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self._net, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
    def retention(self, type=eMoneyCurrency.Product):
        if type==1:
            return Money(self.mem, self.taxes, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self.taxes, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self.taxes, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
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
            return Money(self.mem, self._commission, self.investment.product.currency)
        elif type==2:
            return Money(self.mem, self._commission, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==3:
            return Money(self.mem, self._commission, self.investment.product.currency).convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
            
    def copy(self ):
        return Dividend(self.mem).init__create(self.investment, self._gross, self.taxes, self._net, self.dpa, self.datetime, self._commission, self.concept, self.currency_conversion, self.opercuenta, self.id)
        
    def neto_antes_impuestos(self):
        return self._gross-self._commission
    
    def save(self):
        """Insertar un dividend y una opercuenta vinculada a la tabla dividends en el campo accountsoperations_id
        
        En caso de que sea actualizar un dividend hay que actualizar los datos de opercuenta y se graba desde aquí. No desde el objeto opercuenta
        
        Actualiza la cuenta 
        """
        from xulpymoney.objects.accountoperation import AccountOperation
        from xulpymoney.objects.comment import Comment
        if self.id==None:#Insertar
            self.opercuenta=AccountOperation(self.mem,  self.datetime,self.concept, self.concept.tipooperacion, self._net, "Transaction not finished", self.investment.account, None)
            self.opercuenta.save()
            self.id=self.mem.con.cursor_one_field("insert into dividends (datetime, dps, gross, taxes, net, investments_id,accountsoperations_id, commission, concepts_id,currency_conversion) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) returning id_dividends", (self.datetime, self.dpa, self._gross, self.taxes, self._net, self.investment.id, self.opercuenta.id, self._commission, self.concept.id, self.currency_conversion))
            self.opercuenta.comment=Comment(self.mem).encode(eComment.Dividend, self)
            self.opercuenta.save()
        else:
            self.opercuenta.datetime=self.datetime
            self.opercuenta.amount=self._net
            self.opercuenta.comment=Comment(self.mem).encode(eComment.Dividend, self)
            self.opercuenta.concept=self.concept
            self.opercuenta.tipooperacion=self.concept.tipooperacion
            self.opercuenta.save()
            self.mem.con.execute("update dividends set datetime=%s, dps=%s, gross=%s, taxes=%s, net=%s, investments_id=%s, accountsoperations_id=%s, commission=%s, concepts_id=%s, currency_conversion=%s where id_dividends=%s", (self.datetime, self.dpa, self._gross, self.taxes, self._net, self.investment.id, self.opercuenta.id, self._commission, self.concept.id, self.currency_conversion, self.id))

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
        cur.execute( sql)#"select * from dividends where investments_id=%s order by datetime", (self.investment.id, )
        for row in cur:
            from xulpymoney.objects.accountoperation import AccountOperation
            inversion=self.mem.data.investments.find_by_id(row['investments_id'])
            oc=AccountOperation(self.mem, row['accountsoperations_id'])
            self.arr.append(Dividend(self.mem).init__db_row(row, inversion, oc, self.mem.concepts.find_by_id(row['concepts_id']) ))
        cur.close()      

    def myqtablewidget(self, wdg,   type=eMoneyCurrency.User):
        hh=[self.tr("Date"), self.tr("Product"), self.tr("Concept"), self.tr("Gross"), self.tr("Withholding"), self.tr("Commission"), self.tr("Net"), self.tr("DPS")]
        data=[]
        for i, o in enumerate(self.arr):
            data.append([
                o.datetime, 
                o.investment.fullName(), 
                o.opercuenta.concept.name, 
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
            wdg.table.setItem(i, 1, qleft(d.opercuenta.concept.name))
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
        
