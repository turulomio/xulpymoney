

class SettingsDB:
    def __init__(self, mem):
        self.mem=mem
    
    def in_db(self, name):
        """Returns true if globals is saved in database"""
        cur=self.mem.con.cursor()
        cur.execute("select value from globals where id=%s", (self.id(name), ))
        num=cur.rowcount
        cur.close()
        if num==0:
            return False
        else:
            return True
  
    def value(self, name, default):
        """Search in database if not use default"""            
        cur=self.mem.con.cursor()
        cur.execute("select value from globals where id=%s", (self.id(name), ))
        if cur.rowcount==0:
            cur.close()
            return default
        else:
            value=cur.fetchone()[0]
            cur.close()
            if value==None:
                return default
            return value
        
    def setValue(self, name, value):
        """Set the global value.
        It doesn't makes a commit, you must do it manually
        value can't be None
        """
        cur=self.mem.con.cursor()
        if self.in_db(name)==False:
            cur.execute("insert into globals (id, global,value) values(%s,%s,%s)", (self.id(name),  name, value))     
        else:
            cur.execute("update globals set global=%s, value=%s where id=%s", (name, value, self.id(name)))
        cur.close()
        self.mem.con.commit()
        
    def id(self,  name):
        """Converts section and name to id of table globals"""
        if name=="Version":
            return 1
        elif name=="Version of products.xlsx":
            return 2
        elif name=="wdgIndexRange/spin":
            return 7
        elif name=="wdgIndexRange/invertir":
            return 8
        elif name=="wdgIndexRange/minimo":
            return 9
        elif name=="wdgLastCurrent/spin":
            return 10
        elif name=="mem/localcurrency":
            return 11
        elif name=="mem/localzone":
            return 12
        elif name=="mem/benchmarkid":
            return 13
        elif name=="mem/dividendwithholding":
            return 14
        elif name=="mem/taxcapitalappreciation":
            return 15
        elif name=="mem/taxcapitalappreciationbelow":
            return 16
        elif name=="mem/gainsyear":
            return 17
        elif name=="mem/favorites":
            return 18
        elif name=="mem/fillfromyear":
            return 19
        elif name=="frmSellingPoint/lastgainpercentage":
            return 20
        elif name=="wdgAPR/cmbYear":
            return 21
        elif name=="wdgLastCurrent/viewmode":
            return 22
        elif name=="strategyLongShort/historicalLong":
            return 23
        elif name=="strategyLongShort/historicalShort":
            return 24
        elif name=="wdgProductRange/spnDown":
            return 25
        elif name=="wdgProductRange/spnGains":
            return 26
        elif name=="wdgProductRange/invest":
            return 27
        elif name=="wdgProductRange/product":
            return 28
        return None
