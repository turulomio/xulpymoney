from PyQt5.QtCore import QObject
from xulpymoney.casts import list2string, string2list_of_integers
from xulpymoney.libmanagers import ObjectManager_With_IdName_Selectable
from xulpymoney.objects.investment import InvestmentManager_from_list_of_ids

class Strategy(QObject):
    def __init__(self, mem=None,name=None,  investments=None, dt_from=None, dt_to=None, id=None):
        QObject.__init__(self)
        self.mem=mem
        self.name=name
        self.investments=investments
        self.dt_from=dt_from
        self.dt_to=dt_to
        self.id=id

    def __repr__(self):
        return ("Strategy '{0}' ({1})".format( self.name, self.id))

    def save(self):
        if self.investments is None:
            investments=""
        else:
            investments=list2string(self.investments.array_of_ids())
        if self.id==None:
            self.mem.con.cursor_one_field("insert into strategies (name, investments, dt_from, dt_to) values (%s,%s,%s,%s) returning id", 
                (self.name, investments,  self.dt_from, self.dt_to))
        else:
            self.mem.con.execute("update cuentas set name=%s, investments=%s, dt_from=%s, dt_to=%s, where id=%s", 
                (self.name, investments,  self.dt_from,  self.dt_to, self.id))

    def delete(self, cur):
        if self.is_deletable()==True:
            cur.execute("delete from cuentas where id_cuentas=%s", (self.id, ))

class StrategyManager(QObject, ObjectManager_With_IdName_Selectable):   
    def __init__(self, mem):
        QObject.__init__(self)
        ObjectManager_With_IdName_Selectable.__init__(self)
        self.mem=mem

def Strategy_from_dict(mem, row):
    r=Strategy(mem)
    r.id=row['id']
    r.name=row['name']
    r.investments=InvestmentManager_from_list_of_ids(mem, string2list_of_integers(row['investments']))
    r.dt_from=row['dt_from']
    r.dt_to=row['dt_to']
    return r

def StrategyManager_from_sql(mem, sql):
    r=StrategyManager(mem)
    for row in mem.con.cursor_rows(sql):
        r.append(Strategy_from_dict(mem, row))
    return r
    
def StrategyManager_all(mem):
    return StrategyManager_from_sql(mem, "select * from strategies order by name")
