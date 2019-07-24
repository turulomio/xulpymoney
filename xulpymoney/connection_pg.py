## @brief Package to manage postgresql connection functionss
## THIS IS FROM XULPYMONEY PACKAGE IF YOU NEED THIS MODULE PLEASE SYNC IT FROM THERE, FOR EXAMPLE
## @code
##       print ("Copying libmanagers.py from Xulpymoney project")
##        os.chdir("your directory)
##        os.remove("connection_pg.py")
##        os.system("wget https://raw.githubusercontent.com/Turulomio/xulpymoney/master/xulpymoney/connection_pg.py  --no-clobber")
##        os.system("sed -i -e '3i ## THIS FILE HAS BEEN DOWNLOADED AT {} FROM https://github.com/Turulomio/xulpymoney/xulpymoney/connection_pg.py.' connection_pg.py".format(datetime.datetime.now()))
## @encode

import datetime
from psycopg2 import OperationalError
from psycopg2.extras import DictConnection

class Connection:
    def __init__(self):
        self.user=None
        self.password=None
        self.server=None
        self.port=None
        self.db=None
        self._con=None
        self.init=None

    def init__create(self, user, password, server, port, db):
        self.user=user
        self.password=password
        self.server=server
        self.port=port
        self.db=db
        return self

    def cursor(self):
        return self._con.cursor()

    def mogrify(self, sql, arr):
        cur=self._con.cursor()
        s=cur.mogrify(sql, arr)
        cur.close()
        return  s

    def setAutocommit(self, b):
        self._con.autocommit = b


    def cursor_one_row(self, sql, arr=[]):
        cur=self._con.cursor()
        cur.execute(sql, arr)
        row=cur.fetchone()
        cur.close()
        return row

    def cursor_rows(self, sql, arr=[]):
        cur=self._con.cursor()
        cur.execute(sql, arr)
        rows=cur.fetchall()
        cur.close()
        return rows

    def load_script(self, file):
        cur= self._con.cursor()
        procedures  = open(file,'r', encoding='utf-8').read() 
        cur.execute(procedures)
        cur.close()       

    def cursor_one_column(self, sql, arr=[]):
        """Returns un array with the results of the column"""
        cur=self._con.cursor()
        cur.execute(sql, arr)
        for row in cur:
            arr.append(row[0])
        cur.close()
        return arr

    def cursor_one_field(self, sql, arr=[]):
        """Returns only one field"""
        cur=self._con.cursor()
        cur.execute(sql, arr)
        row=cur.fetchone()[0]
        cur.close()
        return row

    def commit(self):
        self._con.commit()

    def rollback(self):
        self._con.rollback()

    def connection_string(self):
        return "dbname='{}' port='{}' user='{}' host='{}' password='{}'".format(self.db, self.port, self.user, self.server, self.password)

    ## Returns an url of the type psql://
    def url_string(self):
        return "psql://{}@{}:{}/{}".format(self.user, self.server, self.port, self.db)

    def connect(self, connection_string=None):
        """Used in code to connect using last self.strcon"""
        if connection_string==None:
            s=self.connection_string()
        else:
            s=connection_string
        try:
            self._con=DictConnection(s)
        except OperationalError as e:
            print('Unable to connect: {}'.format(e))
        self.init=datetime.datetime.now()

    def disconnect(self):
        self._con.close()

    ##Returns if connection is active
    def is_active(self):
        if self._con==None:
            return False
        return True

    def is_superuser(self):
        """Checks if the user has superuser role"""
        res=False
        cur=self.cursor()
        cur.execute("SELECT rolsuper FROM pg_roles where rolname=%s;", (self.user, ))
        if cur.rowcount==1:
            if cur.fetchone()[0]==True:
                res=True
        cur.close()
        return res
        
        
    ## Function to get password user PGPASSWORD environment or ask in console for it
    def get_password(self,  gettext_module=None, gettex_locale=None):
        try:
            import gettext
            t=gettext.translation(gettext_module,  gettex_locale)
            _=t.gettext
        except:
            _=str
        
        from os import environ
        from getpass import getpass
        try:
            self.password=environ['PGPASSWORD']
        except:
            print(_("Write the password for {}").format(self.url_string()))
            self.password=getpass()
        return self.password
        
## Function that adds an argparse argument group with connection parameters
## @param parser Argparse object
## @param gettext_module Gettext module
## @param gettex_locale Locale path
def argparse_connection_arguments_group(parser, gettext_module=None,  gettex_locale=None,  default_user="postgres", default_port=5432, default_server="127.0.0.1",  default_db="postgres"): 
    try:
        import gettext
        t=gettext.translation(gettext_module,  gettex_locale)
        _=t.gettext
    except:
        _=str

    group_db=parser.add_argument_group(_("Postgres database connection parameters"))
    group_db.add_argument('--user', help=_('Postgresql user'), default=default_user)
    group_db.add_argument('--port', help=_('Postgresql server port'), default=default_port)
    group_db.add_argument('--server', help=_('Postgresql server address'), default=default_server)
    group_db.add_argument('--db', help=_('Postgresql database'), default=default_db)
    
## Function that generate the start of a scritp just with connection arguments
def script_with_connection_arguments(name="",  description="", epilog="", version="", gettext_module=None, gettext_locale=None): 
    import argparse
    parser=argparse.ArgumentParser(prog=name, description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=version)
    argparse_connection_arguments_group(parser, gettext_module, gettext_locale)

    global args
    args=parser.parse_args()

    con=Connection()

    con.user=args.user
    con.server=args.server
    con.port=args.port
    con.db=args.db
    
    con.get_password(gettext_module, gettext_locale)
    con.connect()
    return con


if __name__ == "__main__":
    con=script_with_connection_arguments("connection_pg_demo", "This is a connection script demo",  "Developed by Mariano Muñoz", "",  None, None)
    print("Is connection active?",  con.is_active())
    
