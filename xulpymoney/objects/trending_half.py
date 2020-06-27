from xulpymoney.objects.investment import Investment
from xulpymoney.objects.investmentoperation import InvestmentOperation
from xulpymoney.libxulpymoneytypes import eOperationType
from xulpymoney.datetime_functions import dtaware_now

def print_investment(inv):
    print(inv)
    print(inv.op.print())
    print(inv.op_actual.print())
    print(inv.op_historica.print())
    


def start(mem):
    account=None
    product=mem.data.products.find_by_id(81752)
    expiration=None
    inv=Investment(mem).init__create("DAX ALCISTA",   0,  account, product, expiration, True, False, id=-9999)
    inv.needStatus(1)
    print(inv)
    
    io=InvestmentOperation(mem)
    io.tipooperacion=mem.tiposoperaciones.find_by_id(eOperationType.SharesPurchase)
    io.investment=inv
    io.shares=0.03
    io.impuestos=0
    io.comision=0
    io.valor_accion=12458
    io.datetime=dtaware_now(mem.localzone_name)
    io.currency_conversion=1
    io.show_in_ranges=True   
    io.id=-9999
    
    inv.op.append(io)
    inv.op_actual, inv.op_historica=inv.op.get_current_and_historical_operations()
    print_investment(inv)
