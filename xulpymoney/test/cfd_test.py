import datetime
import unittest
import logging
from decimal import Decimal
from xulpymoney.libxulpymoney import Investment, MemXulpymoney, InvestmentOperation, InvestmentOperationHomogeneusManager, OperationType, OperationTypeManager, Product
from xulpymoney.libxulpymoneytypes import eOperationType

class TestXulpymoneyData(unittest.TestCase):
#    def setUp(self):
#        self.app = app
#        self.mem=mem
#        self.frmMain=frmMain 

    def test_actualizar(self):
        mem=MemXulpymoney()
        account=None
        product=Product(mem)
        product.high_low=True
        tiposoperaciones=OperationTypeManager(mem)
        tiposoperaciones.append(OperationType().init__create( "Purchase of shares", eOperationType.SharesPurchase))
        tiposoperaciones.append(OperationType().init__create( "Sale of shares", eOperationType.SharesSale))
        tiposoperaciones.append(OperationType().init__create( "Added of shares", eOperationType.SharesAdd))
        inv=Investment(mem).init__create("CDF Ibex", None, account,  product, None, True, 1)

        #Compro 0.1 y 0.1 y Vendo 0.1
        inv.op=InvestmentOperationHomogeneusManager(mem, inv)
        inv.op.append(InvestmentOperation(mem).init__create(tiposoperaciones.find_by_id(eOperationType.SharesPurchase), datetime.datetime.now(), inv,  Decimal("0.1"), 0, 0, 8000, "", True, 1, 1 ))
        inv.op.append(InvestmentOperation(mem).init__create(tiposoperaciones.find_by_id(eOperationType.SharesPurchase), datetime.datetime.now(), inv,  Decimal("0.1"), 0, 0, 8000, "", True, 1, 1 ))
        inv.op.append(InvestmentOperation(mem).init__create(tiposoperaciones.find_by_id(eOperationType.SharesSale), datetime.datetime.now(), inv,  Decimal("-0.1"), 0, 0, 8000, "", True, 1, 1 ))
        inv.op_actual, inv.op_historica = inv.op.get_current_and_historical_operations(test_suite=True)
        self.assertEqual(Decimal("0.1"), inv.op_actual.shares())
        
        #Vendo -0.1 y -0.1 y Compro 0.1
        inv.op=InvestmentOperationHomogeneusManager(mem, inv)
        inv.op.append(InvestmentOperation(mem).init__create(tiposoperaciones.find_by_id(eOperationType.SharesSale), datetime.datetime.now(), inv,  Decimal("-0.1"), 0, 0, 8000, "", True, 1, 1 ))
        inv.op.append(InvestmentOperation(mem).init__create(tiposoperaciones.find_by_id(eOperationType.SharesSale), datetime.datetime.now(), inv,  Decimal("-0.1"), 0, 0, 8000, "", True, 1, 1 ))
        inv.op.append(InvestmentOperation(mem).init__create(tiposoperaciones.find_by_id(eOperationType.SharesPurchase), datetime.datetime.now(), inv,  Decimal("+0.1"), 0, 0, 8000, "", True, 1, 1 ))
        inv.op_actual, inv.op_historica = inv.op.get_current_and_historical_operations(test_suite=True)
        self.assertEqual(Decimal("-0.1"), inv.op_actual.shares())
        
        #Compro 0.3 y 0.2 y Vemdo 0.7
        inv.op=InvestmentOperationHomogeneusManager(mem, inv)
        inv.op.append(InvestmentOperation(mem).init__create(tiposoperaciones.find_by_id(eOperationType.SharesPurchase), datetime.datetime.now(), inv,  Decimal("0.3"), 0, 0, 8000, "", True, 1, 1 ))
        inv.op.append(InvestmentOperation(mem).init__create(tiposoperaciones.find_by_id(eOperationType.SharesPurchase), datetime.datetime.now(), inv,  Decimal("0.2"), 0, 0, 8000, "", True, 1, 1 ))
        inv.op.append(InvestmentOperation(mem).init__create(tiposoperaciones.find_by_id(eOperationType.SharesSale), datetime.datetime.now(), inv,  Decimal("-0.7"), 0, 0, 8000, "", True, 1, 1 ))
        inv.op.append(InvestmentOperation(mem).init__create(tiposoperaciones.find_by_id(eOperationType.SharesPurchase), datetime.datetime.now(), inv,  Decimal("0.1"), 0, 0, 8000, "", True, 1, 1 ))
        inv.op_actual, inv.op_historica = inv.op.get_current_and_historical_operations(test_suite=True)
        self.assertEqual(Decimal("-0.1"), inv.op_actual.shares())
        self.assertEqual(1, inv.op_actual.length())

if __name__ == '__main__':
    
    logFormat = "%(asctime)s.%(msecs)03d %(levelname)s %(message)s [%(module)s:%(lineno)d]"
    dateFormat='%F %I:%M:%S'
    logging.basicConfig(level=logging.DEBUG, format=logFormat, datefmt=dateFormat)

    unittest.main()
