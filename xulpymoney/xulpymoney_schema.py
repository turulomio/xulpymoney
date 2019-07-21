## @brief Package to manage creation of a new xulpymoney database
import logging
from PyQt5.QtCore import QObject
from xulpymoney.admin_pg import AdminPG
from xulpymoney.libxulpymoneyfunctions import  package_filename
from xulpymoney.libxulpymoneytypes import eOperationType

## Creates a new xulpymoney database and loads its schema

class XulpymoneyDatabase(AdminPG, QObject):
    def __init__(self, user, password, server, port, newdatabase):
        AdminPG.__init__(self, user, password, server, port)
        QObject.__init__(self)
        self.newdb=newdatabase
        self.newdbcon=None#Filled after connect_to_database newdatabase
        self.error=None
        
    def __del__(self):
        self.con.disconnect()
        self.newdbcon.disconnect()
    
    def log_error(self, error):
        self.error=error
        logging.error(error)

    def create(self):
        if self.con.is_active()==False:
            self.log_error(self.tr("Error conecting to table template1 in database server"))
            return False 
            
        if self.db_exists(self.newdb)==True:
            self.log_error(self.tr("Xulpymoney database already exists"))
            return False

        if self.create_db(self.newdb)==False:
            self.log_error(self.tr("Error creating database. You need to be superuser or maybe it already exist"))
            return False
            
        self.newdbcon=self.connect_to_database(self.newdb)
        
        if self.__load_schema()==False:
            self.log_error(self.tr("Error processing SQL init scripts"))
            return False

        self.newdbcon.commit()
        return True 

    ## In xulpymoney.sql there aren't concepts so we must add them after running it
    ## This strings are tranlatted in hardcoded_strings module
    ## @param newdatabasecon New database connection returned after connect_to_database
    def __load_schema(self):
        filename=package_filename("xulpymoney","sql/xulpymoney.sql")
        self.newdbcon.load_script(filename)
        
        cur= self.newdbcon.cursor()
        cur.execute("insert into public.entidadesbancarias values(3,'{0}', true)".format("Personal Management"))
        cur.execute("insert into public.cuentas values(4,'{0}',3,true,NULL,'EUR')".format("Cash"))
        cur.execute("insert into public.conceptos values(1,'{0}',2,false)".format("Initiating bank account"))
        cur.execute("insert into public.conceptos values(2,'{0}',2,true)".format("Paysheet"))
        cur.execute("insert into public.conceptos values(3,'{0}',1,true)".format("Supermarket"))
        cur.execute("insert into public.conceptos values(4,'{0}',3,false)".format("Transfer. Origin"))
        cur.execute("insert into public.conceptos values(5,'{0}',3,false)".format("Transfer. Destination"))
        cur.execute("insert into public.conceptos values(6,'{0}',2,false)".format("Taxes. Returned"))
        cur.execute("insert into public.conceptos values(7,'{0}',1,true)".format("Gas"))
        cur.execute("insert into public.conceptos values(8,'{0}',1,true)".format("Restaurant"))  
        cur.execute("insert into public.conceptos values(29,'{0}',4,false)".format("Purchase investment product"))
        cur.execute("insert into public.conceptos values(35,'{0}',5,false)".format("Sale investment product"))
        cur.execute("insert into public.conceptos values(37,'{0}',1,false)".format("Taxes. Paid"))
        cur.execute("insert into public.conceptos values(38,'{0}',1,false)".format("Bank commissions"))
        cur.execute("insert into public.conceptos values(39,'{0}',2,false)".format("Dividends"))
        cur.execute("insert into public.conceptos values(40,'{0}',7,false)".format("Credit card billing"))
        cur.execute("insert into public.conceptos values(43,'{0}',6,false)".format("Added shares"))
        cur.execute("insert into public.conceptos values(50,'{0}',2,false)".format("Attendance bonus"))
        cur.execute("insert into public.conceptos values(59,'{0}',1,false)".format("Custody commission"))
        cur.execute("insert into public.conceptos values(62,'{0}',2,false)".format("Dividends. Sale of rights"))
        cur.execute("insert into public.conceptos values(63,'{0}',1,false)".format("Bonds. Running coupon payment"))
        cur.execute("insert into public.conceptos values(65,'{0}',2,false)".format("Bonds. Running coupon collection"))
        cur.execute("insert into public.conceptos values(66,'{0}',2,false)".format("Bonds. Coupon collection"))
        cur.execute("insert into public.conceptos values(67,'{0}',2,false)".format("Credit card refund"))          
        cur.execute("insert into public.conceptos values(68,%s,%s,false)",("HL adjustment income", eOperationType.Income))    
        cur.execute("insert into public.conceptos values(69,%s,%s,false)",("HL adjustment expense", eOperationType.Expense))  
        cur.execute("insert into public.conceptos values(70,%s,%s,false)",("HL Guarantee payment", eOperationType.Expense))  
        cur.execute("insert into public.conceptos values(71,%s,%s,false)",("HL Guarantee return", eOperationType.Income))     
        cur.execute("insert into public.conceptos values(72,%s,%s,false)",("HL Operation commission", eOperationType.Expense))     
        cur.execute("insert into public.conceptos values(73,%s,%s,false)",("HL Paid interest", eOperationType.Expense))     
        cur.execute("insert into public.conceptos values(74,%s,%s,false)",("HL Received interest", eOperationType.Income))   
        cur.execute("insert into public.conceptos values(75,%s,%s,false)",("Rollover Paid", eOperationType.Expense))   
        cur.execute("insert into public.conceptos values(76,%s,%s,false)",("Rollover Received", eOperationType.Income))   
        cur.close()
        return True
