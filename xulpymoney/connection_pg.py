## @brief Package to manage postgresql connection functionss
## THIS IS FROM XULPYMONEY PACKAGE IF YOU NEED THIS MODULE PLEASE SYNC IT FROM THERE, FOR EXAMPLE
## @code
##       print ("Copying libmanagers.py from Xulpymoney project")
##        os.chdir("your directory)
##        os.remove("connection_pg.py")
##        os.system("wget https://raw.githubusercontent.com/Turulomio/xulpymoney/master/xulpymoney/connection_pg.py  --no-clobber")
##        os.system("sed -i -e '3i ## THIS FILE HAS BEEN DOWNLOADED AT {} FROM https://github.com/Turulomio/xulpymoney/xulpymoney/connection_pg.py.' connection_pg.py".format(datetime.datetime.now()))
## @encode
        
from PyQt5.QtCore import QObject,  pyqtSignal,  QTimer
import datetime
import psycopg2
import psycopg2.extras

class Connection(QObject):
    inactivity_timeout=pyqtSignal()
    def __init__(self):
        QObject.__init__(self)
        
        self.user=None
        self.password=None
        self.server=None
        self.port=None
        self.db=None
        self._con=None
        self._active=False
        
        self.restart_timeout()
        self.inactivity_timeout_minutes=30
        self.init=None
        
    def init__create(self, user, password, server, port, db):
        self.user=user
        self.password=password
        self.server=server
        self.port=port
        self.db=db
        return self
        
    def _check_inactivity(self):
        if datetime.datetime.now()-self._lastuse>datetime.timedelta(minutes=self.inactivity_timeout_minutes):
            self.disconnect()
            self._timerlastuse.stop()
            self.inactivity_timeout.emit()
        print ("Remaining time {}".format(self._lastuse+datetime.timedelta(minutes=self.inactivity_timeout_minutes)-datetime.datetime.now()))

    def cursor(self):
        self.restart_timeout()#Datetime who saves the las use of connection
        return self._con.cursor()
        
    def restart_timeout(self):
        """Resets timeout, usefull in long process without database connections"""
        self._lastuse=datetime.datetime.now()
        
    
    def mogrify(self, sql, arr):
        """Mogrify text"""
        cur=self._con.cursor()
        s=cur.mogrify(sql, arr)
        cur.close()
        return  s
        
    def cursor_one_row(self, sql, arr=[]):
        """Returns only one row"""
        self.restart_timeout()
        cur=self._con.cursor()
        cur.execute(sql, arr)
        row=cur.fetchone()
        cur.close()
        return row        
        
    def cursor_one_column(self, sql, arr=[]):
        """Returns un array with the results of the column"""
        self.restart_timeout()
        cur=self._con.cursor()
        cur.execute(sql, arr)
        for row in cur:
            arr.append(row[0])
        cur.close()
        return arr
        
    def cursor_one_field(self, sql, arr=[]):
        """Returns only one field"""
        self.restart_timeout()
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
        
    def connect(self, connection_string=None):
        """Used in code to connect using last self.strcon"""
        if connection_string==None:
            s=self.connection_string()
        else:
            s=connection_string        
        try:
            self._con=psycopg2.extras.DictConnection(s)
        except psycopg2.Error as e:
            print (e.pgcode, e.pgerror)
            return
        self._active=True
        self.init=datetime.datetime.now()
        self.restart_timeout()
        self._timerlastuse = QTimer()
        self._timerlastuse.timeout.connect(self._check_inactivity)
        self._timerlastuse.start(300000)

    def disconnect(self):
        self._active=False
        if self._timerlastuse.isActive()==True:
            self._timerlastuse.stop()
        self._con.close()

    def is_active(self):
        return self._active

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
