from xulpymoney.datetime_functions import dtaware
from datetime import time
from xulpymoney.objects.quote import Quote

class Maintenance:
    """Funciones de mantenimiento y ayuda a la programación y depuración"""
    def __init__(self, mem):
        self.mem=mem
        
    def regenera_todas_opercuentasdeoperinversiones(self):
         
        for inv in self.mem.data.investments.arr:
            inv.actualizar_cuentasoperaciones_asociadas()
        self.mem.con.commit()        
        
        
    def show_investments_status(self, date):
        """Shows investments status in a date"""
        datet=dtaware(date, time(22, 00), self.mem.localzone_name)
        sumbalance=0
        print ("{0:<40s} {1:>15s} {2:>15s} {3:>15s}".format("Investments at {0}".format(date), "Shares", "Price", "Balance"))
        for inv in self.mem.data.investments.arr:
            balance=inv.balance(date)
            sumbalance=sumbalance+balance
            acciones=inv.shares(date)
            price=Quote(self.mem).init__from_query(inv.product, datet)
            if acciones!=0:
                print ("{0:<40s} {1:>15f} {2:>15s} {3:>15s}".format(inv.name, acciones, self.mem.localmoney(price.quote),  self.mem.localmoney(balance)))
        print ("{0:>40s} {1:>15s} {2:>15s} {3:>15s}".format("Total balance at {0}".format(date), "","", self.mem.localmoney(sumbalance)))
