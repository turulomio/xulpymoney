from PyQt5.QtCore import QObject
from xulpymoney.libmanagers import ObjectManager_With_IdName_Selectable
from xulpymoney.ui.myqtablewidget import qdatetime, qleft, qcenter
class SimulationManager(ObjectManager_With_IdName_Selectable, QObject):
    def __init__(self, mem):
        ObjectManager_With_IdName_Selectable.__init__(self)
        QObject.__init__(self)
        self.mem=mem
            
    def delete(self, simulation):
        """Deletes from db and removes object from array.
        simulation is an object"""
        simulation.delete()
        self.remove(simulation)

    def load_from_db(self, sql,  original_db):
        cur=self.mem.con.cursor()
        cur.execute(sql)
        for row in cur:
            s=Simulation(self.mem, original_db).init__db_row(row)
            self.append(s)
        cur.close()  
        
    def myqtablewidget(self, wdg):
        wdg.table.setColumnCount(5)
        wdg.table.setHorizontalHeaderItem(0, qcenter(self.tr("Creation" )))
        wdg.table.setHorizontalHeaderItem(1, qcenter(self.tr("Type" )))
        wdg.table.setHorizontalHeaderItem(2, qcenter(self.tr("Database" )))
        wdg.table.setHorizontalHeaderItem(3, qcenter(self.tr("Starting" )))
        wdg.table.setHorizontalHeaderItem(4, qcenter(self.tr("Ending" )))
        wdg.table.clearContents()
        wdg.applySettings()
        wdg.table.setRowCount(self.length())
        for i, a in enumerate(self.arr):
            wdg.table.setItem(i, 0, qdatetime(a.creation, self.mem.localzone_name))
            wdg.table.setItem(i, 1, qleft(a.type.name))
            wdg.table.item(i, 1).setIcon(a.type.qicon())
            wdg.table.setItem(i, 2, qleft(a.simulated_db()))
            wdg.table.setItem(i, 3, qdatetime(a.starting, self.mem.localzone_name))
            wdg.table.setItem(i, 4, qdatetime(a.ending, self.mem.localzone_name))


    
class Simulation:
    def __init__(self,mem, original_db):
        """Types are defined in combo ui wdgSimulationsADd
        database is the database which data is going to be simulated"""
        self.mem=mem
        self.database=original_db
        self.id=None
        self.name=None#self.simulated_db, used to reuse ObjectManager_With_IdName_Selectable
        self.creation=None
        self.type=None
        self.starting=None
        self.ending=None
        
    def init__create(self, type_id, starting, ending):
        """Used only to create a new one"""
        self.type=self.mem.simulationtypes.find_by_id(type_id)
        self.starting=starting
        self.ending=ending
        self.creation=self.mem.localzone.now()
        return self
        
    def simulated_db(self):
        """Returns"""
        return "{}_{}".format(self.database, self.id)    

    def init__db_row(self, row):
        self.id=row['id']
        self.database=row['database']
        self.creation=row['creation']
        self.type=self.mem.simulationtypes.find_by_id(row['type'])
        self.starting=row['starting']
        self.ending=row['ending']
        return self
        
    def save(self):
        cur=self.mem.con.cursor()
        if self.id==None:
            cur.execute("insert into simulations (database, type, starting, ending, creation) values (%s,%s,%s,%s,%s) returning id", (self.database, self.type.id, self.starting, self.ending, self.creation))
            self.id=cur.fetchone()[0]
            self.name=self.simulated_db()
        else:
            cur.execute("update simulations set database=%s, type=%s, starting=%s, ending=%s, creation=%s where id=%s", (self.database, self.type.id, self.starting, self.ending, self.creation, self.id))
        cur.close()

    def delete(self):
        cur=self.mem.con.cursor()
        cur.execute("delete from simulations where id=%s", (self.id, ))
        cur.close()
