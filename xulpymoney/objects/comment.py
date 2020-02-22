from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication
from logging import debug
from xulpymoney.casts import string2list_of_integers
from xulpymoney.datetime_functions import dtaware2string
from xulpymoney.libxulpymoneytypes import eComment, eMoneyCurrency
from xulpymoney.objects.dividend import Dividend
from xulpymoney.objects.money import Money
## Class who controls all comments from opercuentas, operinversiones ...
class Comment(QObject):
    def __init__(self, mem):
        QObject.__init__(self)
        self.mem=mem

    ##Obtiene el codigo de un comentario
    def getCode(self, string):
        (code, args)=self.get(string)
        return code        

    def getArgs(self, string):
        """
            Obtiene los argumentos enteros de un comentario
        """
        (code, args)=self.get(string)
        return args

    def get(self, string):
        """Returns (code,args)"""
        string=string
        try:
            number=string2list_of_integers(string, separator=",")
            if len(number)==1:
                code=number[0]
                args=[]
            else:
                code=number[0]
                args=number[1:]
            return(code, args)
        except:
            return(None, None)
            
    ## Function to generate a encoded comment using distinct parameters
    ## Encode parameters can be:
    ## - eComment.DerivativeManagement, hlcontract
    ## - eComment.Dividend, dividend
    ## - eComment.AccountTransferOrigin operaccountorigin, operaccountdestiny, operaccountorigincommission
    ## - eComment.AccountTransferOriginCommission operaccountorigin, operaccountdestiny, operaccountorigincommission
    ## - eComment.AccountTransferDestiny operaccountorigin, operaccountdestiny, operaccountorigincommission
    ## - eComment.CreditCardBilling creditcard, operaccount
    ## - eComment.CreditCardRefund opercreditcardtorefund
    def encode(self, ecomment, *args):
        if ecomment==eComment.InvestmentOperation:
            return "{},{}".format(eComment.InvestmentOperation, args[0].id)
        elif ecomment==eComment.Dividend:
            return "{},{}".format(eComment.Dividend, args[0].id)        
        elif ecomment==eComment.AccountTransferOrigin:
            operaccountorigincommission_id=-1 if args[2]==None else args[2].id
            return "{},{},{},{}".format(eComment.AccountTransferOrigin, args[0].id, args[1].id, operaccountorigincommission_id)
        elif ecomment==eComment.AccountTransferOriginCommission:
            operaccountorigincommission_id=-1 if args[2]==None else args[2].id
            return "{},{},{},{}".format(eComment.AccountTransferOriginCommission, args[0].id, args[1].id, operaccountorigincommission_id)
        elif ecomment==eComment.AccountTransferDestiny:
            operaccountorigincommission_id=-1 if args[2]==None else args[2].id
            return "{},{},{},{}".format(eComment.AccountTransferDestiny, args[0].id, args[1].id, operaccountorigincommission_id)
        elif ecomment==eComment.CreditCardBilling:
            return "{},{},{}".format(eComment.CreditCardBilling, args[0].id, args[1].id)      
        elif ecomment==eComment.CreditCardRefund:
            return "{},{}".format(eComment.CreditCardRefund, args[0].id)        
    
    def validateLength(self, number, code, args):
        if number!=len(args):
            debug("Comment {} has not enough parameters".format(code))
            return False
        return True

    def decode(self, string):
        """Sets the comment to show in app"""
        from xulpymoney.objects.accountoperation import AccountOperation
        try:
            (code, args)=self.get(string)
            if code==None:
                return string

            if code==eComment.InvestmentOperation:
                if not self.validateLength(1, code, args): return string
                io=self.mem.data.investments.findInvestmentOperation(args[0])
                if io==None: return string
                if io.investment.hasSameAccountCurrency():
                    return self.tr("{}: {} shares. Amount: {}. Comission: {}. Taxes: {}").format(io.investment.name, io.shares, io.gross(eMoneyCurrency.Product), io.commission(eMoneyCurrency.Product), io.taxes(eMoneyCurrency.Product))
                else:
                    return self.tr("{}: {} shares. Amount: {} ({}). Comission: {} ({}). Taxes: {} ({})").format(io.investment.name, io.shares, io.gross(eMoneyCurrency.Product), io.gross(eMoneyCurrency.Account),  io.commission(eMoneyCurrency.Product), io.commission(eMoneyCurrency.Account),  io.taxes(eMoneyCurrency.Product), io.taxes(eMoneyCurrency.Account))

            elif code==eComment.AccountTransferOrigin:#Operaccount transfer origin
                if not self.validateLength(3, code, args): return string
                aod=AccountOperation(self.mem, args[1])
                return QApplication.translate("Mem","Transfer to {}").format(aod.account.name)

            elif code==eComment.AccountTransferDestiny:#Operaccount transfer destiny
                if not self.validateLength(3, code, args): return string
                aoo=AccountOperation(self.mem, args[0])
                return QApplication.translate("Mem","Transfer received from {}").format(aoo.account.name)

            elif code==eComment.AccountTransferOriginCommission:#Operaccount transfer origin comision
                if not self.validateLength(3, code, args): return string
                aoo=AccountOperation(self.mem, args[0])
                aod=AccountOperation(self.mem, args[1])
                return QApplication.translate("Mem","Comission transfering {} from {} to {}").format(aoo.account.currency.string(aoo.importe), aoo.account.name, aod.account.name)

            elif code==eComment.Dividend:#Comentario de cuenta asociada al dividendo
                if not self.validateLength(1, code, args): return string
                dividend=Dividend(self.mem).init__db_query(args[0])
                investment=self.mem.data.investments.find_by_id(dividend.investment.id)
                if investment.hasSameAccountCurrency():
                    return QApplication.translate("Mem", "From {}. Gross {}. Net {}.").format(investment.name, dividend.gross(1), dividend.net(1))
                else:
                    return QApplication.translate("Mem", "From {}. Gross {} ({}). Net {} ({}).").format(investment.name, dividend.gross(1), dividend.gross(2), dividend.net(1), dividend.net(2))

            elif code==eComment.CreditCardBilling:#Facturaci´on de tarjeta diferida
                if not self.validateLength(2, code, args): return string
                creditcard=self.mem.data.accounts.find_creditcard_by_id(args[0])
                number=self.mem.con.cursor_one_field("select count(*) from opertarjetas where id_opercuentas=%s", (args[1], ))
                return QApplication.translate("Mem","Billing {} movements of {}").format(number, creditcard.name)

            elif code==eComment.CreditCardRefund:#Devolución de tarjeta
                from xulpymoney.objects.creditcardoperation import CreditCardOperation
                if not self.validateLength(1, code, args): return string
                cco=CreditCardOperation(self.mem).init__db_query(args[0])
                money=Money(self.mem, cco.importe, cco.tarjeta.account.currency)
                return QApplication.translate("Mem","Refund of {} payment of which had an amount of {}").format(dtaware2string(cco.datetime), money)
        except:
            return self.tr("Error decoding comment {}").format(string)

