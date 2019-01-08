## @brief Package to manage postgresql admin functionss
## THIS IS FROM XULPYMONEY PACKAGE IF YOU NEED THIS MODULE PLEASE SYNC IT FROM THERE, FOR EXAMPLE
## @code
##       print ("Copying admin_pg.py from Xulpymoney project")
##        os.chdir("your directory)
##        os.remove("admin_pg.py")
##        os.system("wget https://raw.githubusercontent.com/Turulomio/xulpymoney/master/xulpymoney/admin_pg.py  --no-clobber")
##        os.system("sed -i -e '3i ## THIS FILE HAS BEEN DOWNLOADED AT {} FROM https://github.com/Turulomio/xulpymoney/xulpymoney/admin_pg.py.' admin_pg.py".format(datetime.datetime.now()))
## @encode

import io
import logging
from .connection_pg import Connection

class AdminPG:
    def __init__(self, connection):
        """connection is an object Connection to a database"""
        self.con=connection
        
    def connection_template1(self):
        cont=Connection().init__create(self.con.user, self.con.password, self.con.server, self.con.port, "template1")
        cont.connect()
        return cont


    def check_connection(self):
        """It has database parameter, due to I connect to template to create database"""
        try:
            cont=self.connection_template1()
            cont._con.set_isolation_level(0)#Si no no me dejaba
            cont.disconnect()
            return True
        except:
            logging.critical ("Conection to template1 failed")
            return False

    def create_db(self, database):
        """It has database parameter, due to I connect to template to create database"""
        cont=self.connection_template1()
        cont._con.set_isolation_level(0)#Si no no me dejaba
        if cont.is_superuser():
            cur=cont.cursor()
            cur.execute("create database {0};".format(database))
        else:
            logging.critical ("You need to be superuser to create database")
            return False
        
        
    def db_exists(self, database):
        """Hace conexi´on automatica a template usando la con """
        new=Connection().init__create(self.con.user, self.con.password, self.con.server, self.con.port, "template1")
        new.connect()
        new._con.set_isolation_level(0)#Si no no me dejaba            
        cur=new.cursor()
        cur.execute("SELECT 1 AS result FROM pg_database WHERE datname=%s", (database, ))
        
        if cur.rowcount==1:
            cur.close()
            new.disconnect
            return True
        cur.close()
        new.disconnect()
        return False

    def drop_db(self, database):
        """It has database parameter, due to I connect to template to drop database"""
        
        if self.db_exists(database)==False:
            logging.info("Database doesn't exist")
            return True
        
        if self.con.is_superuser():
            new=Connection().init__create(self.con.user, self.con.password, self.con.server, self.con.port, "template1")
            new.connect()
            new._con.set_isolation_level(0)#Si no no me dejaba            
            try:
                cur=new.cursor()
                cur.execute("drop database {0};".format(database))
            except:
                logging.error ("Error in drop()")
            finally:
                cur.close()
                new.disconnect()
                return False
            logging.info("Database droped")
            return True
        else:
            logging.warning ("You need to be superuser to drop a database")
            return False
        

    def load_script(self, file):
        cur= self.con.cursor()
        procedures  = open(file,'r').read() 
        cur.execute(procedures)
        
        self.con.commit()
        cur.close()       
        
        
    def copy(self, con_origin, sql,  table_destiny ):
        """Used to copy between tables, and sql to table_destiny, table origin and destiny must have the same structure"""
        if sql.__class__==bytes:
            sql=sql.decode('UTF-8')
        f=io.StringIO()
        cur_origin=con_origin.cursor()
        cur_origin.copy_expert("copy ({}) to stdout".format(sql), f)
        cur_origin.close()
        f.seek(0)
        cur_destiny=self.con.cursor()
        cur_destiny.copy_from(f, table_destiny)
        cur_destiny.close()
        f.seek(0)
        logging.debug (f.read())
        f.close()
