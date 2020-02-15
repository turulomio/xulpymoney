from datetime import date
from xulpymoney.objects.assets import Assets
class AnnualTarget:
    def __init__(self, mem):
        self.mem=mem
        self.year=None
        self.percentage=None
        self.lastyear_assests=None
        self.saved_in_db=False #Controls if AnnualTarget is saved in the table annualtargets
    
    ## Fills the object with data from db.
    ## If lastyear_assests=None it gets the assests from db
    def init__from_db(self, year, lastyear_assests=None):
        cur=self.mem.con.cursor()
        
        if lastyear_assests==None:
            self.lastyear_assests=Assets(self.mem).saldo_total(self.mem.data.investments,  date(year-1, 12, 31))
        else:
            self.lastyear_assests=lastyear_assests
        
        cur.execute("select * from annualtargets where year=%s", (year, ))
        if cur.rowcount==0:
            self.year=year
            self.percentage=0
        else:
            row=cur.fetchone()
            self.year=year
            self.percentage=row['percentage']
            self.saved_in_db=True
        cur.close()
        return self
        
    def save(self):
        cur=self.mem.con.cursor()
        if self.saved_in_db==False:
            cur.execute("insert into annualtargets (year, percentage) values (%s,%s)", (self.year, self.percentage))
            self.saved_in_db=True
        else:
            cur.execute("update annualtargets set percentage=%s where year=%s", (self.percentage, self.year))
        cur.close()
        
    ## Returns the amount of tthe annual target
    def annual_balance(self):
        return self.lastyear_assests.amount*self.percentage/100
        
    ## Returns the amount of the monthly target (annual/12)
    def monthly_balance(self):
        return self.annual_balance()/12
