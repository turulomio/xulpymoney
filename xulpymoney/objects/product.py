from PyQt5.QtCore import QObject
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QProgressDialog
from datetime import datetime, timedelta, date
from logging import debug
from os import system
from xulpymoney.casts import b2s
from xulpymoney.github import get_file_modification_dtaware
from xulpymoney.decorators import deprecated
from xulpymoney.libmanagers import ManagerSelectionMode, ObjectManager_With_IdName_Selectable, ObjectManager_With_Id_Selectable
from xulpymoney.libxulpymoneytypes import eTickerPosition, eProductType, eQColor
from xulpymoney.objects.dps import DPSManager
from xulpymoney.objects.money import Money
from xulpymoney.objects.quote import Quote, QuoteManager, QuotesResult
from xulpymoney.objects.ohcl import OHCLDaily
from xulpymoney.objects.split import SplitManager
from xulpymoney.objects.estimation import EstimationDPSManager, EstimationEPSManager

class Product(QObject):
    def __init__(self, mem):
        QObject.__init__(self)
        self.mem=mem
        self.name=None
        self.isin=None
        self.currency=None #Apunta a un objeto currency
        self.type=None
        self.agrupations=None #Es un objeto AgrupationManager
        self.id=None
        self.web=None
        self.address=None
        self.phone=None
        self.mail=None
        self.percentage=None
        self.mode=None#Anterior mode investmentmode
        self.leveraged=None
        self.stockmarket=None
        self.tickers=[None]*eTickerPosition.length()#Its a list of strings, eTickerPosition is the 
        self.comment=None
        self.obsolete=None
        self.high_low=None#Allow short and long operations
        self.decimals=None
        
        ## Variable with the current product status
        ## 0 No data
        ## 1 Loaded splits and triplete and estimations_dps
        ## 2 Load estimations_eps, dps, eps, ohcls and dividends
        ## 3 Load all quotes
        self.status=0
        
        self.result=None#Variable en la que se almacena QuotesResult
        self.estimations_dps=None#Es un diccionario que guarda objetos estimations_dps con clave el año
        self.estimations_eps=None
        self.dps=None #It's created when loading quotes in quotes result
        self.splits=None #It's created when loading quotes in quotes result
        
    def __repr__(self):
        return "{0} ({1}) de la {2}".format(self.name , self.id, self.stockmarket.name)
                
    def init__db_row(self, row):
        """row es una fila de un pgcursro de investmentes"""
        self.name=row['name'].upper()
        self.isin=row['isin']
        self.currency=row['currency']
        self.type=self.mem.types.find_by_id(row['type'])
        self.agrupations=self.mem.agrupations.clone_from_dbstring(row['agrupations'])
        self.id=row['id']
        self.web=row['web']
        self.address=row['address']
        self.phone=row['phone']
        self.mail=row['mail']
        self.percentage=row['percentage']
        self.mode=self.mem.investmentsmodes.find_by_id(row['pci'])
        self.leveraged=self.mem.leverages.find_by_id(row['leveraged'])
        self.stockmarket=self.mem.stockmarkets.find_by_id(row['stockmarkets_id'])
        self.tickers=row['tickers']
        self.comment=row['comment']
        self.obsolete=row['obsolete']
        self.high_low=row['high_low']
        self.decimals=row['decimals']
        return self


    def init__create(self, name,  isin, currency, type, agrupations, active, web, address, phone, mail, percentage, mode, leveraged, decimals, stockmarket, tickers, comment, obsolete, high_low, id=None):
        self.name=name
        self.isin=isin
        self.currency=currency
        self.type=type
        self.agrupations=agrupations
        self.active=active
        self.id=id
        self.web=web
        self.address=address
        self.phone=phone
        self.mail=mail
        self.percentage=percentage
        self.mode=mode
        self.leveraged=leveraged        
        self.decimals=decimals
        self.stockmarket=stockmarket
        self.tickers=tickers
        self.comment=comment
        self.obsolete=obsolete
        self.high_low=high_low
        return self        

    def init__db(self, id):
        """Se pasa id porque se debe usar cuando todavía no se ha generado."""
        cur=self.mem.con.cursor()
        cur.execute("select * from products where id=%s", (id, ))
        row=cur.fetchone()
        cur.close()
        return self.init__db_row(row)

    def save(self):
        if self.id==None:
            if self.mem.isProductsMaintenanceMode()==True:
                self.id=self.mem.con.cursor_one_field("select max(id)+1 from products")
            else:
                self.id=self.mem.con.cursor_one_field("select min(id)-1 from products")
            self.mem.con.execute(self.sql_insert(returning_id=False))
        else:# update
            self.mem.con.execute(self.sql_update())

        ## @param returning_id True sql with returning id (normal insert). False without returning_id and id inside sql. Used for automatic inserts
    def sql_insert(self, returning_id=True):
        print(self.tickers,  len(self.tickers))
        sql= """insert into public.products (name,  isin,  currency,  type,  agrupations, web, 
            address,  phone, mail, percentage, pci, leveraged, 
            decimals, stockmarkets_id, tickers, comment, obsolete, high_low) values (
            %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s
            ) returning id;"""
        sql_parameters=(self.name, self.isin, self.currency, self.type.id,  self.agrupations.dbstring(), self.web, 
            self.address,  self.phone, self.mail, self.percentage, self.mode.id,  self.leveraged.id, 
            self.decimals, self.stockmarket.id, self.tickers, self.comment, self.obsolete, self.high_low)

        if returning_id==True:
            r=self.mem.con.mogrify(sql, sql_parameters)
        else:
            sql=sql.replace(") values (", ", id ) values (")
            sql=sql.replace(") returning id", ", %s)")
            r=self.mem.con.mogrify(sql, sql_parameters+(self.id, ))
        return b2s(r)

    def sql_update(self):
        sql="""update public.products set name=%s, isin=%s, currency=%s, type=%s, agrupations=%s, web=%s, 
            address=%s, phone=%s, mail=%s, percentage=%s, pci=%s, leveraged=%s, 
            decimals=%s, stockmarkets_id=%s, tickers=%s, comment=%s, obsolete=%s,high_low=%s 
            where id=%s;"""
        sql_parameters= ( self.name,  self.isin,  self.currency,  self.type.id,  self.agrupations.dbstring(),  self.web, 
            self.address,  self.phone, self.mail, self.percentage, self.mode.id,  self.leveraged.id, 
            self.decimals, self.stockmarket.id, self.tickers, self.comment, self.obsolete, self.high_low,  
            self.id)
        return b2s(self.mem.con.mogrify(sql, sql_parameters))

    ## Return if the product has autoupdate in some source
    def has_autoupdate(self):
        if self.obsolete==True:
            return False
        if self.id in self.mem.autoupdate:
            return True
        return False
        
    ## La forma para ver si un objeto no se han cargado valores es que sea None y para borrarlos es ponerlos a None
    ## Variable with the current product status
    ## 0 No data. Tendra los siguientes valores
    ## 1 Loaded splits and triplete and estimations_dps,splits
    ## 2 Load estimations_eps, dps, , dividends, ohcls 
    ## 3 Load all quotes
    
    ## ESTA FUNCION VA AUMENTANDO STATUS SIN MOLESTAR LOS ANTERIORES, SOLO CARGA CUANDO stsatus_to es mayor que self.status
    ## @param statusneeded  Integer with the status needed 
    ## @param downgrade_to Integer with the status to downgrade before checking needed status. If None it does nothing
    def needStatus(self, statusneeded, downgrade_to=None):
        if downgrade_to!=None:
            self.status=downgrade_to
        
        
        if self.status==statusneeded:
            return
        #0
        if self.status==0 and statusneeded==1: #MAIN
            start=datetime.now()
            self.estimations_dps=EstimationDPSManager(self.mem, self)
            self.estimations_dps.load_from_db()
            self.splits=SplitManager(self.mem, self)
            self.splits.init__from_db("select * from splits where products_id={} order by datetime".format(self.id))
            self.result=QuotesResult(self.mem, self)
            self.result.get_basic()
            self.status=1
        elif self.status==0 and statusneeded==2:
            self.needStatus(1)
            self.needStatus(2)
        elif self.status==0 and statusneeded==3:
            self.needStatus(1)
            self.needStatus(2)
            self.needStatus(3)
        elif self.status==1 and statusneeded==2: #MAIN
            start=datetime.now()
            self.estimations_eps=EstimationEPSManager(self.mem, self)
            self.estimations_eps.load_from_db()
            self.dps=DPSManager(self.mem, self)
            self.dps.load_from_db()           
            self.result.get_ohcls()
            debug("Product {} took {} to pass from status {} to {}".format(self.name, datetime.now()-start, self.status, statusneeded))
            self.status=2
        elif self.status==1 and statusneeded==3:
            self.needStatus(2)
            self.needStatus(3)
        elif self.status==2 and statusneeded==3:#MAIN
            start=datetime.now()
            self.result.get_all()
            debug("Product {} took {} to pass from status {} to {}".format(self.name, datetime.now()-start, self.status, statusneeded))
            self.status=3

    def hasSameLocalCurrency(self):
        """
            Returns a boolean
            Check if product currency is the same that local currency
        """
        if self.currency==self.mem.localcurrency:
            return True
        return False

    def is_deletable(self):
        if self.is_system():
            return False
            
        #Search in all investments
        for i in self.mem.data.investments.arr:
            if i.product.id==self.id:
                return False
        
        #Search in benchmark
        if self.mem.data.benchmark.id==self.id:
            return False
        
        return True       

    def is_system(self):
        """Returns if the product is a system product or a user product"""
        if self.id>=0:
            return True
        return False

    ## @return boolen if could be done
    ## NO HACE COMMIT
    def remove(self):     
        if self.is_deletable()==True and self.is_system()==False:
            cur=self.mem.con.cursor()
            cur.execute("delete from quotes where id=%s", (self.id, ))
            cur.execute("delete from estimations_dps where id=%s", (self.id, ))
            cur.execute("delete from estimations_eps where id=%s", (self.id, ))
            cur.execute("delete from dps where id=%s", (self.id, ))
            cur.execute("delete from splits where products_id=%s", (self.id, ))
            cur.execute("delete from opportunities where products_id=%s", (self.id, ))
            cur.execute("delete from products where id=%s", (self.id, ))
            cur.close()
            self.needStatus(0, downgrade_to=0)
            return True
        return False

    def fecha_ultima_actualizacion_historica(self):
        """
            Si es acciones, etf, indexes, warrants, currencies, publicbond, private bond buscará el microsegundo 4
            Si es fondo, plan de pensiones buscará la última cotización
        """
        cur=self.mem.con.cursor()
        if self.type.id in [eProductType.Share, eProductType.ETF, eProductType.Index, eProductType.Warrant, eProductType.Currency, eProductType.PublicBond, eProductType.PrivateBond]:
            cur.execute("select max(datetime)::date as date from quotes where date_part('microsecond',datetime)=4 and id=%s", (self.id, ))
        else:
            cur.execute("select max(datetime)::date as date from quotes where id=%s", (self.id, ))
        dat=cur.fetchone()[0]
        if dat==None:
            resultado=date(self.mem.fillfromyear, 1, 1)
        else:
            resultado=dat
        cur.close()
        return resultado

    ## Returns the highest operation price of all investments in mem of this product
    ## Used in wdgProductRange
    def highest_investment_operation_price(self):
        r=0
        inv=self.mem.data.investments.Investment_merging_current_operations_with_same_product(self)
        for op in inv.op_actual.arr:
            if op.valor_accion>r:
                r=op.valor_accion
        return r
    ## Returns the highest operation price of all investments in mem of this product
    ## Used in wdgProductRange
    ## When you add shares to an invesment operation, sometimes price is 0. Sometimes I want to ignore them
    def lowest_investment_operation_price(self, ignore_zero=True):
        r=100000000
        inv=self.mem.data.investments.Investment_merging_current_operations_with_same_product(self)
        for op in inv.op_actual.arr:
            if op.valor_accion<r:
                if op.valor_accion==0 and ignore_zero==True:
                    continue
                r=op.valor_accion
        return r

    ## Search in Internet for last quote information
    ## @return QuoteManager QuoteManager object with the quotes found in Internet
    def update(self):
        r=QuoteManager(self.mem)
        r.print()
        
    ## REturn a money object with the amount and account currency
    def money(self, amount):
        return Money(self.mem, amount, self.currency)
        
    ## IBEXA es x2 pero esta en el pricio
    ## CFD DAX no está en el precio
    def real_leveraged_multiplier(self):
        if self.type.id in (eProductType.CFD, eProductType.Future):
            return self.leveraged.multiplier
        return 1

    def mqtw_tickers(self, mqtw):
        data=[]
        data.append(["Yahoo", self.tickers[eTickerPosition.Yahoo]])
        data.append(["Morningstar", self.tickers[eTickerPosition.Morningstar]])
        data.append(["Google", self.tickers[eTickerPosition.Google]])
        data.append(["Que Fondos", self.tickers[eTickerPosition.QueFondos]])
        data.append(["Investing.com", self.tickers[eTickerPosition.InvestingCom]])
        mqtw.setData(
            [self.tr("Name"), self.tr("Value")], 
            None, 
            data
        )


## Class to manage products
class ProductManager(ObjectManager_With_IdName_Selectable, QObject):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        QObject.__init__(self)
        self.setSelectionMode(ManagerSelectionMode.List)
        self.mem=mem

    def find_by_isin(self, isin):
        if isin==None:
            return None
        for p in self.arr:
            if p.isin==None:
                continue
            if p.isin.upper()==isin.upper():
                return p
        return None             
        
    ## This method looks inside the manager and return a list with all products with the ticker in the etickerposition
    def find_all_by_ticker(self, ticker, etickerposition):
        r=[]
        if ticker==None:
            return r
        for p in self.arr:
            if p.tickers[etickerposition]==None:
                continue
            if p.tickers[etickerposition].upper()==ticker.upper():
                r.append(p)
        return r          
        
    @deprecated
    def load_from_inversiones_query(self, sql, progress=True):
        """sql es una query sobre la tabla inversiones"""
        cur=self.mem.con.cursor()
        cur.execute(sql)#"Select distinct(products_id) from inversiones"
        ##Conviert cur a lista separada comas
        lista=""
        for row in cur:
            lista=lista+ str(row['products_id']) + ", "
        lista=lista[:-2]
        cur.close()
        
        ##Carga los products
        if len(lista)>0:
            self.load_from_db("select * from products where id in ("+lista+")", progress )

    def load_from_db(self, sql,  progress=False):
        """sql es una query sobre la tabla inversiones
        Carga estimations_dbs, y basic
        """
        self.clean()
        cur=self.mem.con.cursor()
        cur.execute(sql)#"select * from products where id in ("+lista+")" 
        if progress==True:
            pd= QProgressDialog(QApplication.translate("Mem","Loading {0} products from database").format(cur.rowcount),None, 0,cur.rowcount)
            pd.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            pd.setModal(True)
            pd.setWindowTitle(QApplication.translate("Mem","Loading products..."))
            pd.forceShow()
        for rowms in cur:
            if progress==True:
                pd.setValue(cur.rownumber)
                pd.update()
                QApplication.processEvents()
                
            inv=Product(self.mem).init__db_row(rowms)
            self.append(inv)
        cur.close()
        

    ## Passes product.needStatus method to all products in arr
    ## @param needstatus Status needed
    ## @param progress Boolean. If true shows a progress bar
    def needStatus(self, needstatus,  downgrade_to=None, progress=False):
        if progress==True:
            pd= QProgressDialog(self.tr("Loading additional data to {0} products from database").format(self.length()),None, 0,self.length())
            pd.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
            pd.setModal(True)
            pd.setWindowTitle(self.tr("Loading products..."))
            pd.forceShow()
        for i, product in enumerate(self.arr):
            if progress==True:
                pd.setValue(i)
                pd.update()
                QApplication.processEvents()
            product.needStatus(needstatus, downgrade_to)

    def order_by_datetime(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda c: c.result.basic.last.datetime,  reverse=False)  
            return True
        except:
            return False
        
    def order_by_dividend(self):
        """Return a boolean if the sort can be done"""
        try:
            self.arr=sorted(self.arr, key=lambda p: p.estimations_dps.currentYear().percentage(),  reverse=True) 
            return True
        except:
            return False
        
    def order_by_daily_tpc(self):
        """Return a boolean if the sort can be done"""
        try:
            self.arr=sorted(self.arr, key=lambda p: p.result.basic.tpc_diario(),  reverse=True) 
            return True
        except:
            return False
                
    def order_by_annual_tpc(self):
        """Return a boolean if the sort can be done"""
        try:
            self.arr=sorted(self.arr, key=lambda p: p.result.basic.tpc_anual(),  reverse=True) 
            return True
        except:
            return False
            
    ## Fills a qcombobox with product nume in upper case
    ## @param combo QComboBox to fill
    ## @param selected Product object to select in the QComboBox
    def qcombobox_not_obsolete(self, combo,  selected=None):
        self.order_by_name()
        combo.clear()
        for a in self.arr:
            if a.obsolete==False:
                combo.addItem(a.name.upper(), a.id)

        if selected!=None:
            combo.setCurrentIndex(combo.findData(selected.id))

    ## Returns a ProductManager with all products with the type passed as parameter.
    ## @param type ProductType object
    ## @return ProductManager
    def ProductManager_with_same_type(self, type):
        result=ProductManager(self.mem)
        for a in self.arr:
            if a.type.id==type.id:
                result.append(a)
        return result

    ## Generate a new ProductManager object finding ids of parameter array in self.arr
    ## @param arrInt Array of integers to seach in self.arr
    ## @return ProductManager with the products matchind ids in arrInt.
    def ProductManager_with_id_in_list(self, arrInt):
        result=ProductManager(self.mem)
        for i, id in enumerate(arrInt):
            selected=self.mem.data.products.find_by_id(id)
            if selected!=None:
                result.append(selected)
        return result
        

    ## Generate a new ProductManager object with products that contains parameter string
    ## @param s String to seach
    ## @return ProductManager that is a subset of this class
    def ProductManager_contains_string(self, s):
        def find_attribute(att, s):
            if att==None:
                return False
            if att.upper().find(s)!=-1:
                return True
            return False
        # #############################################
        s=s.upper()
        result=ProductManager(self.mem)
        for o in self.arr:
            if find_attribute(o.name, s) or find_attribute(o.isin, s) or any(find_attribute(ticker, s) for ticker in o.tickers) or find_attribute(o.comment, s):
                result.append(o)
        return result
        
    ## Removes a product and return a boolean. NO HACE COMMIT
    def remove(self, o):
        if o.remove():
            ObjectManager_With_Id_Selectable.remove(self, o)
            return True
        return False

    ## Returns products.xlsx modification datetime or None if it can't find it
    def dtaware_internet_products_xlsx(self):
        aware= get_file_modification_dtaware("turulomio","xulpymoney","products.xlsx")
        if aware==None:
            return aware
        else:
            return aware.replace(second=0)#Due to in database globals we only save minutes

    ## Used to find names using translations
    def find_by_name_translations(self, manager, name, translationslanguagemanager,  module):
        for language in translationslanguagemanager.arr:
            translationslanguagemanager.cambiar(language.id, module)
            for o in manager.arr:
                #                print (name, ":",  language.id,  o.name, self.tr( o.name))
                
                if self.tr(o.name)==name:
                    #print ("FOUND",  language.id,  o.name, self.tr(o.name))
                    return o
        return None

    def list_ISIN_XULPYMONEY(self):
        """Returns a list with all products with 3 appends --ISIN_XULPYMONEY ISIN, ID"""
        suf=[]
        for p in self.arr:
            if len(p.isin)>5:
                suf.append("--ISIN_XULPYMONEY")
                suf.append(p.isin)
                suf.append(str(p.id))
        return suf

    ## Move data from product_from to product_to, changing data with the id to the new product id
    ## It will not remove origin product but it will be empty after this move, so if it's a user product could be removed manually.
    ## @param product_from. Must be a user product (id<0). 
    ## @param product_to
    def move_data_between_products(self,  product_from,  product_to):
        cur=self.mem.con.cursor()
        cur.execute("update quotes set id=%s where id=%s",(product_to.id,product_from.id))
        cur.execute("update dps set id=%s where id=%s",(product_to.id,product_from.id))        
        cur.execute("update estimations_dps set id=%s where id=%s",(product_to.id,product_from.id))        
        cur.execute("update estimations_eps set id=%s where id=%s",(product_to.id,product_from.id))      
        cur.execute("update splits set products_id=%s where products_id=%s",(product_to.id,product_from.id))
        cur.execute("update opportunities set products_id=%s where products_id=%s",(product_to.id,product_from.id))
        cur.execute("update inversiones set products_id=%s where products_id=%s",(product_to.id,product_from.id))
        cur.close()

    def myqtablewidget(self, wdg):
        hh=[self.tr("Id"), self.tr("Product"), self.tr("ISIN"), self.tr("Last update"), self.tr("Price"), 
            self.tr("% Daily"), self.tr("% Year to date"), self.tr("% Dividend")]
        
        data=[]
        for i, o in enumerate(self.arr):
            data.append([
                o.id, 
                o.name.upper(), 
                o.isin, 
                o.result.basic.last.datetime, 
                o.result.basic.last.money(), 
                o.result.basic.tpc_diario(), 
                o.result.basic.tpc_anual(), 
                o.estimations_dps.currentYear().percentage(), 
                o, 
            ])

        wdg.setDataWithObjects(hh, None, data, zonename=self.mem.localzone_name, additional=self.myqtablewidget_additional)

    def myqtablewidget_additional(self, wdg):
        for i, o in enumerate(wdg.objects()):
            wdg.table.item(i, 1).setIcon(o.stockmarket.country.qicon())
            if o.estimations_dps.currentYear()==None:
#                wdg.table.setItem(i, 7, Percentage().qtablewidgetitem())
                wdg.table.item(i, 7).setBackground( eQColor.Red)          
#            else:
#                wdg.table.setItem(i, 7, p.estimations_dps.currentYear().percentage().qtablewidgetitem())
            if o.has_autoupdate()==True:#Active
                wdg.table.item(i, 4).setIcon(QIcon(":/xulpymoney/transfer.png"))
            if o.obsolete==True:#Obsolete
                wdg.setRowStrikeOut(i)


## Class to manage source xulpymoney_run_client and other scripts
## Update works creating a file in ____ and theen executing xulpymoney_run_client
class ProductUpdate:
    ## @param mem Memory Singleton
    def __init__(self, mem):
        self.mem=mem
        self.commands=[]
    
    ## Adds a command that will be inserted in  "{}/clients.txt".format(dir_tmp)
    ## Example: self.appendCommand(["xulpymoney_morningstar_client","--TICKER_XULPYMONEY",  p.tickers[eTickerPosition.Morningstar], str(p.id)])       
    def appendCommand(self, command):
        self.commands.append(command)

     ## Generates "{}/clients.txt".format(dir_tmp)
    def __generateCommandsFile(self):
        filename="{}/clients.txt".format(self.mem.dir_tmp)
        f=open(filename, "w")
        for a in self.commands:
            f.write(" ".join(a) + "\n")
        f.close()
        debug("Added {} comandos to {}".format(len(self.commands), filename))

    ## Reads ("{}/clients_result.txt".format(self.mem.dir_tmp), an return a strubg
    def readResults(self):
        f=open("{}/clients_result.txt".format(self.mem.dir_tmp), "r")
        r=f.read()
        f.close()
        return r


    ## Returns a set with all ids of products that are searched in ProductUpdate.setGlobalCommands.
    ##
    ## Developer must change this querys after changeing setGlobalCommands querys.
    ## @param mem. Xulpymoney mem
    ## @return set. Set with integers (products_id)
    @staticmethod
    def generateAutoupdateSet(mem):
        r=set()
        used=""
        ##### BOLSAMADRID #####
        sqls=[
            "select * from products where type in (1,4) and obsolete=false and stockmarkets_id=1 and isin is not null and isin<>'' {} order by name".format(used), 
            "select * from products where type in ({}) and obsolete=false and stockmarkets_id=1 and isin is not null {} order by name".format(eProductType.PublicBond, used), 
            "select * from products where type in ({},{}) and obsolete=false and tickers[{}] is not null {} order by name".format(eProductType.ETF, eProductType.Share, eTickerPosition.postgresql(eTickerPosition.Google), used), 
            "select * from products where type in ({}) and obsolete=false and tickers[{}] is not null order by name".format(eProductType.Index,  eTickerPosition.postgresql(eTickerPosition.Google)), 
            "select * from products where type in ({}) and tickers[{}] is not null and obsolete=false is not null order by name".format(eProductType.Currency,  eTickerPosition.postgresql(eTickerPosition.Yahoo)), 
            "select * from products where type={} and stockmarkets_id=1 and obsolete=false and tickers[{}] is not null {} order by name".format(eProductType.PensionPlan.value, eTickerPosition.postgresql(eTickerPosition.QueFondos), used), 
            "select * from products where tickers[{}] is not null and obsolete=false {} order by name".format(eTickerPosition.postgresql(eTickerPosition.Morningstar),  used)
        ]
        for sql in sqls:
            for row in mem.con.cursor_rows(sql):
                r.add(row['id'])
        return r

    ## Function that executes xulpymoney_run_client and generate a QuoteManager 
    ## Source commands must be created before in file "{}/clients.txt".format(dir_tmp)
    ## Output of the xulpymoney_run_client command is generated in ("{}/clients_result.txt".format(self.mem.dir_tmp),
    ## After run, clears self.command array
    ## @return QuoteManager
    def run(self):        
        self.__generateCommandsFile()
        quotes=QuoteManager(self.mem)
        system("xulpymoney_run_client")
        cr=open("{}/clients_result.txt".format(self.mem.dir_tmp), "r")
        for line in cr.readlines():
            if line.find("OHCL")!=-1:
                ohcl=OHCLDaily(self.mem).init__from_client_string(line[:-1])
                if ohcl!=None:
                    for quote in ohcl.generate_4_quotes():
                        if quote!=None:
                            quotes.append(quote)
            if line.find("PRICE")!=-1:
                quote=Quote(self.mem).init__from_client_string(line[:-1])
                if quote!=None:
                    quotes.append(quote)
        cr.close()
        self.commands=[]
        return quotes

    ## Sets commands for a product update
    def setCommands(self,  product):
        if product.tickers[eTickerPosition.Yahoo]!=None:
            self.appendCommand(["xulpymoney_yahoo_client","--TICKER_XULPYMONEY",  product.tickers[eTickerPosition.Yahoo], str(product.id)])
            
    ## Sets commands for all products
    ## @param all if this boolean it's True, tries to get all products updates. If it's False it tries to get used product in investment, indexes and currencies
    def setGlobalCommands(self, all):
        oneday=timedelta(days=1)
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
            if date.today()>ultima+oneday:#Historical data is always refreshed the next day, so dont work again
                if p.type.id==eProductType.ETF:
                    self.appendCommand(["xulpymoney_bolsamadrid_client","--ISIN_XULPYMONEY",  p.isin, str(p.id),  "--etf","--fromdate", str( p.fecha_ultima_actualizacion_historica()+oneday)])
                elif p.type.id==eProductType.Share:
                    self.appendCommand(["xulpymoney_bolsamadrid_client","--ISIN_XULPYMONEY",  p.isin, str(p.id),"--share","--fromdate", str( p.fecha_ultima_actualizacion_historica()+oneday)])
                    
        self.appendCommand(["xulpymoney_bolsamadrid_client","--share"]+products.ProductManager_with_same_type(self.mem.types.find_by_id(eProductType.Share.value)).list_ISIN_XULPYMONEY()) # SHARES INTRADAY

        self.appendCommand(["xulpymoney_bolsamadrid_client","--etf"]+products.ProductManager_with_same_type(self.mem.types.find_by_id(eProductType.ETF.value)).list_ISIN_XULPYMONEY()) # SHARES INTRADAY

        sql="select * from products where type in ({}) and obsolete=false and stockmarkets_id=1 and isin is not null {} order by name".format(eProductType.PublicBond, used)        
        bm_publicbonds=ProductManager(self.mem)
        bm_publicbonds.load_from_db(sql)    
        self.appendCommand(["xulpymoney_bolsamadrid_client","--publicbond"]+bm_publicbonds.list_ISIN_XULPYMONEY())#MUST BE INTRADAY
        
        ibex=Product(self.mem).init__db(79329)
        self.appendCommand(["xulpymoney_bolsamadrid_client","--ISIN_XULPYMONEY",  ibex.isin, str(ibex.id),"--index","--fromdate", str(ibex.fecha_ultima_actualizacion_historica()+oneday)])

        ##### GOOGLE #####
        sql="select * from products where type in ({},{}) and obsolete=false and tickers[{}] is not null {} order by name".format(eProductType.ETF, eProductType.Share, eTickerPosition.postgresql(eTickerPosition.Google), used)
        debug(sql)
        products=ProductManager(self.mem)
        products.load_from_db(sql)    
        for p in products.arr:
            self.appendCommand(["xulpymoney_google_client","--TICKER_XULPYMONEY",  p.tickers[eTickerPosition.Google], str(p.id), "--STOCKMARKET", str(p.stockmarket.id)])

        ##### GOOGLE INDICES  #####
        sql="select * from products where type in ({}) and obsolete=false and tickers[{}] is not null order by name".format(eProductType.Index,  eTickerPosition.postgresql(eTickerPosition.Google))
        debug(sql)
        products=ProductManager(self.mem)
        products.load_from_db(sql)    
        for p in products.arr:
            self.appendCommand(["xulpymoney_google_client","--TICKER_XULPYMONEY",  p.tickers[eTickerPosition.Google], str(p.id), "--STOCKMARKET", str(p.stockmarket.id)])

        ##### INFOBOLSA CURRENCIES  #####
        sql="select * from products where type in ({}) and tickers[{}] is not null and obsolete=false is not null order by name".format(eProductType.Currency,  eTickerPosition.postgresql(eTickerPosition.Yahoo))
        debug(sql)
        products=ProductManager(self.mem)
        products.load_from_db(sql)    
        for p in products.arr:
            self.appendCommand(["xulpymoney_infobolsa_client","--TICKER_XULPYMONEY",  p.tickers[eTickerPosition.Yahoo], str(p.id), "--STOCKMARKET", str(p.stockmarket.id)])

        ##### QUE FONDOS ####
        sql="select * from products where type={} and stockmarkets_id=1 and obsolete=false and tickers[{}] is not null {} order by name".format(eProductType.PensionPlan.value, eTickerPosition.postgresql(eTickerPosition.QueFondos), used)
        products_quefondos=ProductManager(self.mem)#Total of products_quefondos of an Agrupation
        products_quefondos.load_from_db(sql)    
        for p in products_quefondos.arr:
            ultima=p.fecha_ultima_actualizacion_historica()
            if date.today()>ultima+oneday:#Historical data is always refreshed the next day, so dont work agan
                self.appendCommand(["xulpymoney_quefondos_client","--TICKER_XULPYMONEY",  p.tickers[eTickerPosition.QueFondos], str(p.id),  "--STOCKMARKET", str(p.stockmarket.id)])    
                
        ##### MORNINGSTAR FONDOS #####
        sql="select * from products where type={} and tickers[{}] is not null and obsolete=false {} order by name".format(eProductType.Fund, eTickerPosition.postgresql(eTickerPosition.Morningstar),  used)
        products_morningstar=ProductManager(self.mem)#Total of products_morningstar of an Agrupation
        products_morningstar.load_from_db(sql)    
        for p in products_morningstar.arr:
            ultima=p.fecha_ultima_actualizacion_historica()
            if date.today()>ultima+oneday:#Historical data is always refreshed the next day, so dont work again
                self.appendCommand(["xulpymoney_morningstar_client", "--fund", "--TICKER_XULPYMONEY",  p.tickers[eTickerPosition.Morningstar], str(p.id), "--STOCKMARKET", str(p.stockmarket.id)])         
                
        ##### MORNINGSTAR ETF #####
        sql="select * from products where type={} and tickers[{}] is not null and obsolete=false {} order by name".format(eProductType.ETF, eTickerPosition.postgresql(eTickerPosition.Morningstar),  used)
        products_morningstar=ProductManager(self.mem)#Total of products_morningstar of an Agrupation
        products_morningstar.load_from_db(sql)    
        for p in products_morningstar.arr:
            self.appendCommand(["xulpymoney_morningstar_client", "--etf", "--TICKER_XULPYMONEY",  p.tickers[eTickerPosition.Yahoo], str(p.id), "--STOCKMARKET", str(p.stockmarket.id)])
