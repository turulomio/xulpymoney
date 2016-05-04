from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

def qmessagebox_investment_Inactive():
    m=QMessageBox()
    m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
    m.setIcon(QMessageBox.Information)
    m.setText(QApplication.translate("Core","Selected investment is inactive. Your must activate first."))
    m.exec_()   

def qmessagebox_xulpymoney_update_and_superuser():
    m=QMessageBox()
    m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
    m.setIcon(QMessageBox.Information)
    m.setText(QApplication.translate("Core","Xulpymoney needs to be updated. Please login with a superuser role."))
    m.exec_()   
    
def qmessagebox_connexion_error(database, server):
    m=QMessageBox()
    m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
    m.setIcon(QMessageBox.Information)
    m.setText(QApplication.translate("Core","Error conecting to {} database in {} server").format(database, server))
    m.exec_()   

def qmessagebox_connexion_inactivity_timeout(minutes):
    m=QMessageBox()
    m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
    m.setIcon(QMessageBox.Information)
    m.setText(QApplication.translate("Core","Disconnecting due to {} minutes of inactivity.".format(minutes)))
    m.exec_()    

def qmessagebox_connexion_not_superuser():
    m=QMessageBox()
    m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
    m.setIcon(QMessageBox.Information)
    m.setText(QApplication.translate("Core","The role of the user is not an administrator"))
    m.exec_()   

def qmessagebox_developing():
    m=QMessageBox()
    m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
    m.setIcon(QMessageBox.Information)
    m.setText(QApplication.translate("Core", "This option is being developed"))
    m.exec_()    
    
def qmessagebox_error_ordering():
    m=QMessageBox()
    m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
    m.setIcon(QMessageBox.Information)
    m.setText(QApplication.translate("Core", "I couldn't order data due to they have null values"))
    m.exec_()    

def qmessagebox_number_invalid():
    m=QMessageBox()
    m.setWindowIcon(QIcon(":/xulpymoney/coins.png"))
    m.setIcon(QMessageBox.Information)
    m.setText(QApplication.translate("Core", "You have written and invalid number"))
    m.exec_()    
