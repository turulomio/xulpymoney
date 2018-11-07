from PyQt5.QtWidgets import QWidget,  QApplication
from PyQt5.QtCore import QRegExp,  Qt
from PyQt5.QtGui import QTextCursor
from xulpymoney.ui.Ui_wdgQuotesUpdate import Ui_wdgQuotesUpdate
from xulpymoney.libxulpymoney import ProductUpdate

class wdgQuotesUpdate(QWidget, Ui_wdgQuotesUpdate):
    def __init__(self, mem,  parent = None, name = None):
        QWidget.__init__(self,  parent)
        self.setupUi(self)
        self.mem=mem
        self.parent=parent
        self.update=ProductUpdate(self.mem)
        self.index=0

    def run(self):
        self.mem.frmMain.setEnabled(False)
        self.mem.frmMain.repaint()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()
        ##### PROCESS #####
        self.quotes=self.update.run()
        (insertados, ignored, modificados, malos)=self.quotes.save()
        self.mem.con.commit()
        self.txtCR2Q.append(self.update.readResults())
        self.txtCR2Q.append("Quotes added:")
        for q in insertados.arr:
            self.txtCR2Q.append(" - {}".format(q))
        self.txtCR2Q.append("Quoted modified:")
        for q in insertados.arr:
            self.txtCR2Q.append(" - {}".format(q))
        self.mem.data.load()
        
        self.mem.frmMain.setEnabled(True)
        QApplication.restoreOverrideCursor()

    def on_cmdUsed_released(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.update.setGlobalCommands(all=False)
        self.run()
        QApplication.restoreOverrideCursor()

    def on_cmdAll_released(self):        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.update.setGlobalCommands(all=True)
        self.run()
        QApplication.restoreOverrideCursor()
        
    def on_cmdError_released(self):
        self.txtCR2Q.setFocus()
#        self.txtCR2Q.textCursor() = self.txtCR2Q.textCursor()
        # Setup the desired format for matches
#        format = QtGui.QTextCharFormat()
#        format.setBackground(QtGui.QBrush(QtGui.QColor("red")))
        # Setup the regex engine
        regex = QRegExp( "ERROR")
        # Process the displayed document
        self.index = regex.indexIn(self.txtCR2Q.toPlainText(), self.index+1)
        print(self.index,  self.txtCR2Q.textCursor().position())
        if self.index != -1:
            # Select the matched text and apply the desired format
            self.txtCR2Q.textCursor().setPosition(self.index)
            print(self.index,  self.txtCR2Q.textCursor().position())
            print(self.txtCR2Q.textCursor().movePosition(QTextCursor.PreviousWord, QTextCursor.KeepAnchor, 1))
#            cursor.movePosition(QtGui.QTextCursor.EndOfWord, 1)
#            cursor.mergeCharFormat(format)
            # Move to the next match
#            pos = index + regex.matchedLength()
#            index = regex.indexIn(self.toPlainText(), pos)
        else:
            self.txtCR2Q.textCursor().setPosition(self.index)

