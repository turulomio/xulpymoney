import logging
from decimal import Decimal
from xulpymoney.libxulpymoney import AccountOperation, Comment, Money
from xulpymoney.libxulpymoneyfunctions import qdatetime, qleft
from xulpymoney.libmanagers import ObjectManager_With_IdDatetime_Selectable
from xulpymoney.libxulpymoneytypes import eMoneyCurrency, eConcept, eComment
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import QObject
## Class to manage CDF daily contracts.

class HlContract(QObject):
    def __init__(self, mem, investment):
        QObject.__init__(self)
        self.mem=mem
        self.init__create(None, None, Decimal('0'), Decimal('0'), Decimal('0'), Decimal('0'), None, None, None, None, 1)
        self.investment=investment

    def __repr__(self):
        return (self.tr("HLContract {} for {} at {}").format(self.id, self.investment.name,  self.datetime))


    ## Creates a copy of the current object. It's not a pointer to the object
    def copy(self):
        return HlContract(self.mem, self.investment).init__create(self.id, self.datetime, self.guarantee, self.adjustment, self.commission, self.interest, self.guarantee_ao, self.adjustment_ao, self.commission_ao, self.interest_ao, self.currency_conversion)

    def init__db_row(self,  row):
        return self.init__create(row['id'], row['datetime'], row['guarantee'], row['adjustment'], row['commission'], row['interest'], row['guarantee_ao'], row['adjustment_ao'], row['interest_ao'], row['commission_ao'], row['currency_conversion'])
        
    def init__create(self, id, dt, guarantee, adjustment, commission, interest, guarantee_ao, adjustment_ao, interest_ao, commission_ao, currency_conversion):
        self.id=id
        self.datetime=dt
        self.guarantee=guarantee
        self.adjustment=adjustment
        self.commission=commission
        self.interest=interest
        self.guarantee_ao=guarantee_ao
        self.adjustment_ao=adjustment_ao
        self.interest_ao=interest_ao
        self.commission_ao=commission_ao
        self.currency_conversion=currency_conversion
        return self
        
    def init__from_accountoperation(self, accountoperation):
        """AccountOperation is a object, and must have id_conceptos share of sale or purchase. 
        IO returned is an object already created in investments_all()"""
        cur=self.mem.con.cursor()
        cur.execute("select id_inversiones,id_operinversiones from opercuentasdeoperinversiones where id_opercuentas=%s", (accountoperation.id, ))
        if cur.rowcount==0:
            cur.close()
            return None
        row=cur.fetchone()
        cur.close()
        investment=self.mem.data.investments.find_by_id(row['id_inversiones'])
        return investment.op.find(row['id_operinversiones'])
        
    ## Returns a Money object with the self.guarantee amount
    def mGuarantee(self, type):
        money=Money(self.mem, self.guarantee, self.investment.product.currency)
        if type==eMoneyCurrency.Product:
            return money
        elif type==eMoneyCurrency.Account:
            return money.convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==eMoneyCurrency.User:
            return money.convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
    
    ## Returns a Money object 
    def mAdjustment(self, type):
        money=Money(self.mem, self.adjustment, self.investment.product.currency)
        if type==eMoneyCurrency.Product:
            return money
        elif type==eMoneyCurrency.Account:
            return money.convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==eMoneyCurrency.User:
            return money.convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)

    ## Returns a Money object 
    def mCommission(self, type):
        money=Money(self.mem, self.commission, self.investment.product.currency)
        if type==eMoneyCurrency.Product:
            return money
        elif type==eMoneyCurrency.Account:
            return money.convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==eMoneyCurrency.User:
            return money.convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)
    
    ## Returns a Money object 
    def mInterest(self, type):
        money=Money(self.mem, self.interest, self.investment.product.currency)
        if type==eMoneyCurrency.Product:
            return money
        elif type==eMoneyCurrency.Account:
            return money.convert_from_factor(self.investment.account.currency, self.currency_conversion)
        elif type==eMoneyCurrency.User:
            return money.convert_from_factor(self.investment.account.currency, self.currency_conversion).local(self.datetime)

    ## Removes from database contract, and all operaccounts asociated
    def delete_from_db(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from high_low_contract where id=%s", (self.id, ))
        cur.close()
        if self.guarantee_ao!=None:
            AO=AccountOperation(self.mem, self.guarantee_ao)
            AO.borrar()
        if self.adjustment_ao!=None:
            AO=AccountOperation(self.mem, self.adjustment_ao)
            AO.borrar()
        if self.interest_ao!=None:
            AO=AccountOperation(self.mem, self.interest_ao)
            AO.borrar()
        if self.commission_ao!=None:
            AO=AccountOperation(self.mem, self.commission_ao)
            AO.borrar()
        

    def find_by_mem(self, investment, id):
        """
            Searchs in mem (needed investments_all())
            invesment is an Investment object
            id is the invesmentoperation to find
        """
        for i in self.mem.data.investments:
            if investment.id==i.id:
                found=i.op.find(id)
                if found!=None:
                    return found
        logging.warning ("Investment operation {} hasn't been found in mem".format(id))
        return None

    ## Save this HlContract. If self.id==None inserts else updates.
    ## Database stores product amounts y product currency amount
    def save(self):
        # Use current _ao before changing them to delete at the end of the process
        old_guarantee_ao=self.guarantee_ao
        old_adjustment_ao=self.adjustment_ao
        old_interest_ao=self.interest_ao
        old_commission_ao=self.commission_ao

        # Save
        cur=self.mem.con.cursor()
        if self.id==None:#insertar
            cur.execute("insert into high_low_contract(datetime, investments_id, guarantee, adjustment, commission, interest, currency_conversion) values (%s, %s, %s, %s, %s, %s, %s) returning id", 
                (self.datetime, self.investment.id,  self.guarantee, self.adjustment, self.commission, self.interest, self.currency_conversion))
            self.id=cur.fetchone()[0]
            self.investment.hlcontractmanager.append(self)
        else:
            cur.execute("update high_low_contract set datetime=%s, guarantee=%s, adjustment=%s, commission=%s, interest=%s, currency_conversion=%s where id=%s", 
                (self.datetime,  self.guarantee, self.adjustment, self.commission, self.interest, self.currency_conversion, self.id))

        # Creates new AO
        comment=Comment(self.mem).encode(eComment.HlContract, self)
        if self.guarantee!=0:
            concepto=self.mem.conceptos.find_by_id(eConcept.HlGuaranteeReturned) if self.guarantee>0 else self.mem.conceptos.find_by_id(eConcept.HlGuaranteePaid)
            guarantee_AO=AccountOperation(self.mem, self.datetime, concepto, concepto.tipooperacion, self.mGuarantee(eMoneyCurrency.Account).amount, comment, self.investment.account, None)
            guarantee_AO.save()
            self.guarantee_ao=guarantee_AO.id
        else:
            self.guarantee_ao=None#To reset guarantee_ao in database and avoid fk errors
        if self.adjustment!=0:
            concepto=self.mem.conceptos.find_by_id(eConcept.HlAdjustmentIincome) if self.adjustment>0 else self.mem.conceptos.find_by_id(eConcept.HlAdjustmentExpense)
            adjustment_AO=AccountOperation(self.mem, self.datetime, concepto, concepto.tipooperacion, self.mAdjustment(eMoneyCurrency.Account).amount, comment, self.investment.account, None)
            adjustment_AO.save()
            self.adjustment_ao=adjustment_AO.id
        else:
            self.adjustment_ao=None#To reset guarantee_ao in database and avoid fk errors
        if self.interest!=0:
            concepto=self.mem.conceptos.find_by_id(eConcept.HlInterestPaid) if self.adjustment>0 else self.mem.conceptos.find_by_id(eConcept.HlInterestReceived)
            interest_AO=AccountOperation(self.mem, self.datetime, concepto, concepto.tipooperacion, self.mInterest(eMoneyCurrency.Account).amount, comment, self.investment.account, None)
            interest_AO.save()
            self.interest_ao=interest_AO.id
        else:
            self.interest_ao=None#To reset guarantee_ao in database and avoid fk errors
        if self.commission!=0:
            concepto=self.mem.conceptos.find_by_id(eConcept.HlCommission)
            commission_AO=AccountOperation(self.mem, self.datetime, concepto, concepto.tipooperacion, -self.mCommission(eMoneyCurrency.Account).amount, comment, self.investment.account, None)
            commission_AO.save()
            self.commission_ao=commission_AO.id
        else:
            self.commission_ao=None#To reset guarantee_ao in database and avoid fk errors

        cur.execute("update high_low_contract set guarantee_ao=%s, adjustment_ao=%s, interest_ao=%s, commission_ao=%s where id=%s", 
                (self.guarantee_ao, self.adjustment_ao, self.interest_ao, self.commission_ao, self.id))
        cur.close()

        #Delete old AO. This made me change foreign key to NO ACTION.NO ACTION allows the check to be deferred until later in the transaction
        if old_guarantee_ao!=None:
            AO=AccountOperation(self.mem, old_guarantee_ao)
            AO.borrar()
        if old_adjustment_ao!=None:
            AO=AccountOperation(self.mem, old_adjustment_ao)
            AO.borrar()
        if old_interest_ao!=None:
            AO=AccountOperation(self.mem, old_interest_ao)
            AO.borrar()
        if old_commission_ao!=None:
            AO=AccountOperation(self.mem, old_commission_ao)
            AO.borrar()

        self.investment.hlcontractmanager.order_by_datetime()

class HlContractManagerHeterogeneus(ObjectManager_With_IdDatetime_Selectable):
    def __init__(self, mem):
        ObjectManager_With_IdDatetime_Selectable.__init__(self)        
        self.mem=mem

    ## Returns the sum of guarantees
    def mGuarantees(self, type):
        currency=self.investment.resultsCurrency(type)
        r=Money(self.mem, 0, currency)
        for o in self.arr:
            r=r+o.mGuarantee(type)
        return r        
    ## Returns the sum of adjustments
    def mAdjustments(self, type):
        currency=self.investment.resultsCurrency(type)
        r=Money(self.mem, 0, currency)
        for o in self.arr:
            r=r+o.mAdjustment(type)
        return r        
    ## Returns the sum of interest
    def mInterests(self, type):
        currency=self.investment.resultsCurrency(type)
        r=Money(self.mem, 0, currency)
        for o in self.arr:
            r=r+o.mInterest(type)
        return r        
    ## Returns the sum of commissions
    def mCommissions(self, type):
        currency=self.investment.resultsCurrency(type)
        r=Money(self.mem, 0, currency)
        for o in self.arr:
            r=r+o.mCommission(type)
        return r
        
    ## Removes from array and from database
    def delete_from_db(self, obj):
        obj.delete_from_db()
        ObjectManager_With_IdDatetime_Selectable.remove(self, obj)
        
class HlContractManagerHomogeneus(HlContractManagerHeterogeneus, QObject):
    def __init__(self, mem, investment):
        QObject.__init__(self)
        HlContractManagerHeterogeneus.__init__(self, mem)
        self.investment=investment

    ## Function that acts like a constructor
    ## @param sql, to get from high_low_contract table, for example: select * from high_low_contract order by datetime;
    def init__from_db(self, sql):
        self.clean()
        cur=self.mem.con.cursor()
        cur.execute(sql)
        for row in cur:
            hl=HlContract(self.mem, self.investment).init__db_row(row)
            self.append(hl)
        cur.close()
        return self

    ## @param table
    ## @param type eMoneyCurrency 
    def myqtablewidget(self, table, type):
        table.setColumnCount(5)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr("Date and time" )))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr("Adjustment" )))
        table.setHorizontalHeaderItem(2, QTableWidgetItem(self.tr("Guarantee" )))
        table.setHorizontalHeaderItem(3, QTableWidgetItem(self.tr("Interest" )))
        table.setHorizontalHeaderItem(4, QTableWidgetItem(self.tr("Commission" )))
        table.applySettings()
        table.clearContents()
        table.setRowCount(self.length()+1)
        for i, o in enumerate(self.arr):
            table.setItem(i, 0, qdatetime(o.datetime, self.mem.localzone))
            table.setItem(i, 1, o.mAdjustment(type).qtablewidgetitem())
            table.setItem(i, 2, o.mGuarantee(type).qtablewidgetitem())
            table.setItem(i, 3, o.mInterest(type).qtablewidgetitem())
            table.setItem(i, 4, o.mCommission(type).qtablewidgetitem())
        table.setItem(self.length(), 0, qleft(self.tr("TOTAL")))
        table.setItem(self.length(), 1, self.mAdjustments(type).qtablewidgetitem())
        table.setItem(self.length(), 2, self.mGuarantees(type).qtablewidgetitem())
        table.setItem(self.length(), 3, self.mInterests(type).qtablewidgetitem())
        table.setItem(self.length(), 4, self.mCommissions(type).qtablewidgetitem())
