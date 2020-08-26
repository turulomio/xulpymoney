from PyQt5.QtCore import QObject
from xulpymoney.decorators import deprecated
from xulpymoney.libmanagers import ObjectManager_With_IdDatetime_Selectable
from xulpymoney.libxulpymoneytypes import eConcept, eComment
from xulpymoney.objects.comment import Comment
from xulpymoney.objects.money import Money

## Class to manage everything relationed with bank accounts operations
class AccountOperation(QObject):
    ## Constructor with the following attributes combination
    ## 1. AccountOperation(mem). Create an account operation with all attributes to None
    ## 2. AccountOperation(mem, id). Create an account operation searching data in the database for an id.
    ## 3. AccountOperation(mem, row, concept, tipooperacion, account). Create an account operation from a db row, generated in a database query
    ## 4. AccountOperation(mem, datetime, concept, tipooperacion, amount,  comment, account, id):. Create account operation passing all attributes
    ## @param mem MemXulpymoney object
    ## @param row Dictionary of a database query cursor
    ## @param concept Concept object
    ## @param tipooperacion OperationType object
    ## @param account Account object
    ## @param datetime Datetime of the account operation
    ## @param amount Decimal with the amount of the operation
    ## @param comment Account operation comment
    ## @param id Integer that sets the id of an accoun operation. If id=None it's not in the database. id is set in the save method
    def __init__(self, *args):
        def init__create(dt, concept, tipooperacion, amount,  comment, cuenta, id):
            self.id=id
            self.datetime=dt
            self.concept=concept
            self.tipooperacion=tipooperacion
            self.amount=amount
            self.comment=comment
            self.account=cuenta
            
        @deprecated
        def init__db_row(row, concept,  tipooperacion, cuenta):
            init__create(row['datetime'],  concept,  tipooperacion,  row['amount'],  row['comment'],  cuenta,  row['id'])

        def init__db_query(accountsoperations_id):
            """Creates a AccountOperation querying database for an accountsoperations_id"""
            cur=self.mem.con.cursor()
            cur.execute("select * from accountsoperations where id=%s", (accountsoperations_id, ))
            for row in cur:
                concept=self.mem.concepts.find_by_id(row['concepts_id'])
                init__db_row(row, concept, concept.tipooperacion, self.mem.data.accounts.find_by_id(row['accounts_id']))
            cur.close()

        QObject.__init__(self)
        self.mem=args[0]
        if  len(args)==1:
            init__create(None, None, None, None, None, None, None)
        if len(args)==2:
            init__db_query(args[1])
        if len(args)==5:
            init__db_row(args[1], args[2], args[3], args[4])
        if len(args)==8:
            init__create(args[1], args[2], args[3], args[4], args[5], args[6], args[7])

    def __repr__(self):
        return "AccountOperation: {}".format(self.id)

    def borrar(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from accountsoperations where id=%s", (self.id, ))
        cur.close()

    def es_editable(self):
        if self.concept==None:
            return False
        if self.concept.id in (eConcept.BuyShares, eConcept.SellShares, 
            eConcept.Dividends, eConcept.CreditCardBilling, eConcept.AssistancePremium,
            eConcept.DividendsSaleRights, eConcept.BondsCouponRunPayment, eConcept.BondsCouponRunIncome, 
            eConcept.BondsCoupon, eConcept.RolloverPaid, eConcept.RolloverReceived):
            return False
        if Comment(self.mem).getCode(self.comment) in (eComment.AccountTransferOrigin, eComment.AccountTransferDestiny, eComment.AccountTransferOriginCommission):
            return False        
        return True
        
    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into accountsoperations (datetime, concepts_id, operationstypes_id, amount, comment, accounts_id) values ( %s,%s,%s,%s,%s,%s) returning id",(self.datetime, self.concept.id, self.tipooperacion.id, self.amount, self.comment, self.account.id))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("update accountsoperations set datetime=%s, concepts_id=%s, operationstypes_id=%s, amount=%s, comment=%s, accounts_id=%s where id=%s", (self.datetime, self.concept.id, self.tipooperacion.id,  self.amount,  self.comment,  self.account.id,  self.id))
        cur.close()

class AccountOperationManagerHeterogeneus(ObjectManager_With_IdDatetime_Selectable, QObject):
    def __init__(self, mem):
        ObjectManager_With_IdDatetime_Selectable.__init__(self)
        QObject.__init__(self)
        self.mem=mem
    
    ## Función que calcula el balance de todas las AccountOperation in eMoneyCurrency.User
    def balance(self):
        r=Money(self.mem, 0, self.mem.localcurrency)
        for o in self.arr:
            if o.account.currency==self.mem.localcurrency:
                r=r+Money(self.mem, o.amount, o.account.currency)
            else:
                r=r+Money(self.mem, o.amount, o.account.currency).convert(self.mem.localcurrency, o.datetime)
        return r

    @deprecated
    def load_from_db(self, sql):
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from accountsoperations"
        for row in cur:        
            co=AccountOperation(self.mem,  row['datetime'], self.mem.concepts.find_by_id(row['concepts_id']), self.mem.tiposoperaciones.find_by_id(row['operationstypes_id']), row['amount'], row['comment'],  self.mem.data.accounts.find_by_id(row['accounts_id']), row['id'])
            self.append(co)
        cur.close()

    @deprecated
    def load_from_db_with_creditcard(self, sql):
        """Usado en unionall accountsoperations y creditcardsoperations y se crea un campo creditcards_id con el id de la tarjeta y -1 sino tiene es decir accountsoperations"""
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select * from accountsoperations"
        fakeid=-999999999#AccountOperationManager is a DictObjectManager needs and id. creditcardsoperation is None, that's what i make a fake id
        for row in cur:
            if row['creditcards_id']==-1:
                comment=row['comment']
            else:
                comment=self.tr("Paid with {0}. {1}").format(self.mem.data.accounts.find_creditcard_by_id(row['creditcards_id']).name, row['comment'] )
            co=AccountOperation(self.mem, row['datetime'], self.mem.concepts.find_by_id(row['concepts_id']), self.mem.tiposoperaciones.find_by_id(row['operationstypes_id']), row['amount'], comment,  self.mem.data.accounts.find_by_id(row['accounts_id']), fakeid)
            self.append(co)
            fakeid=fakeid+1
        cur.close()

    ## Section es donde guardar en el config file, coincide con el nombre del formulario en el que está la tabla
    ## show_accounts muestra la cuenta cuando las accountsoperations son de diversos accounts (Estudios totales)
    def myqtablewidget(self, wdg, show_accounts=False):
        hh=[self.tr("Date"), self.tr("Account"), self.tr("Concept"), self.tr("Amount"), self.tr("Balance"), self.tr("Comment")]
        data=[]
        for o in self.arr:
            data.append([
                o.datetime, 
                o.account.name, 
                o.concept.name, 
                o.account.money(o.amount), 
                None, #Added in additional (Balance)
                Comment(self.mem).decode(o.comment), 
                o
            ])
        wdg.setDataWithObjects(hh, None, data, zonename=self.mem.localzone_name, additional=self.myqtablewidget_additional)
        
    def myqtablewidget_additional(self, wdg):
        balance=0
        for i, o in enumerate(wdg.objects()):
            balance=balance+o.amount
            wdg.table.setItem(i, 4, o.account.money(balance).qtablewidgetitem())#Sets balance after ordering

class AccountOperationManagerHomogeneus(AccountOperationManagerHeterogeneus):
    def __init__(self, mem, account):
        AccountOperationManagerHeterogeneus.__init__(self, mem)
        self.account=account

    def myqtablewidget_lastmonthbalance(self, wdg,    lastmonthbalance):
        hh=[self.tr("Date" ), self.tr("Concept" ), self.tr("Amount" ), self.tr("Balance" ), self.tr("Comment" )]
        data=[]
        data.append(["#crossedout", self.tr("Starting month balance"), "#crossedout", lastmonthbalance, "#crossedout", None])
        for i, o in enumerate(self.arr):
            amount=Money(self.mem, o.amount, self.account.currency)
            lastmonthbalance=lastmonthbalance+amount
            data.append([
                o.datetime, 
                o.concept.name, 
                amount, 
                lastmonthbalance, 
                Comment(self.mem).decode(o.comment), 
                o, 
            ])
        wdg.setDataWithObjects(hh, None, data, zonename=self.mem.localzone_name)

## Clase parar trabajar con las accountsoperations generadas automaticamente por los movimientos de las investments
class AccountOperationOfInvestmentOperation(QObject):
    ## Constructor with the following attributes combination
    ## 1. AccountOperationOfInvestmentOperation(mem). Create an account operation of an investment operation with all attributes to None
    ## 2. AccountOperationOfInvestmentOperation(mem,  datetime,  concept, tipooperacion, amount, comment, cuenta, operinversion, inversion, id). Create an account operation of an investment operation settings all attributes.1
    ## @param mem MemXulpymoney object
    ## @param datetime Datetime of the account operation
    ## @param concept Concept object
    ## @param tipooperacion OperationType object
    ## @param amount Decimal with the amount of the operation
    ## @param comment Account operation comment
    ## @param account Account object
    ## @param operinversion InvestmentOperation object that generates this account operation
    ## @param id Integer that sets the id of an accoun operation. If id=None it's not in the database. id is set in the save method
    def __init__(self, *args):
        def init__create(datetime,  concept, tipooperacion, amount, comment, account, operinversion, inversion, id):
            self.datetime=datetime
            self.concept=concept
            self.tipooperacion=tipooperacion
            self.amount=amount
            self.comment=comment
            self.account=account
            self.operinversion=operinversion
            self.investment=inversion
            self.id=id
        QObject.__init__(self)
        self.mem=args[0]
        if len(args)==1:
            init__create(None, None, None, None, None, None, None, None, None)
        if len(args)==10:
            init__create(args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9])

    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into investmentsaccountsoperations (datetime, concepts_id, operationstypes_id, amount, comment,accounts_id, investmentsoperations_id,investments_id) values ( %s,%s,%s,%s,%s,%s,%s,%s) returning id", (self.datetime, self.concept.id, self.tipooperacion.id, self.amount, self.comment, self.account.id, self.operinversion.id, self.investment.id))
            self.id=cur.fetchone()[0]
        else:
            cur.execute("UPDATE FALTA  set datetime=%s, concepts_id=%s, operationstypes_id=%s, amount=%s, comment=%s, accounts_id=%s where id=%s", (self.datetime, self.concept.id, self.tipooperacion.id,  self.amount,  self.comment,  self.account.id,  self.id))
        cur.close()
        
def AccountOperation_from_row(mem, row): 
    r=AccountOperation(mem)
    r.id=row['id']
    r.datetime=row['datetime']
    r.concept=mem.concepts.find_by_id(row['concepts_id'])
    r.tipooperacion=mem.tiposoperaciones.find_by_id(row['operationstypes_id'])
    r.amount=row['amount']
    r.comment=row['comment']
    r.account=mem.data.accounts.find_by_id(row['accounts_id'])
    return r

def AccountOperationManagerHeterogeneus_from_sql(mem, sql, params=()):
    rows=mem.con.cursor_rows(sql, params)
    r=AccountOperationManagerHeterogeneus(mem)
    for row in rows:
        r.append(AccountOperation_from_row(mem,  row))
    return r
