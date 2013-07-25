## -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_wdgLog import *
from libxulpymoney import *
import os

class wdgLog(QWidget, Ui_wdgLog):
    def __init__(self, cfg,    parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.cfg=cfg
        self.filtro=''
        self.table.settings("wdgLog",  self.cfg.file_ui)    
        self.timerStatus = QTimer()
        self.timerLog = QTimer()
        QObject.connect(self.timerStatus, SIGNAL("timeout()"), self.updateStatus)    
        QObject.connect(self.timerLog, SIGNAL("timeout()"), self.updateLog)     
        self.updateLog()        
        self.updateStatus()
        self.timerStatus.start(1000)
        self.timerLog.start(20000)
        
    def updateLog(self):
        f=os.popen("cat /tmp/myquotes.log| grep -i '%s'" % self.filtro)
        self.lst.clear()
        self.lst.addItems(f.read().split('\n'))
        f.close()
        self.lblFound.setText(self.tr('{0} registros encontrados'.format(self.lst.count())))
        self.lblLastUpdateLog.setText(self.trUtf8("Última actualización: {0}".format(str(datetime.datetime.now())[:-7])))
    
    def updateStatus(self ):		
        self.table.clearContents()
        now=datetime.datetime.now()
        con=self.cfg.connect_myquotes()
        cur = con.cursor()
        cur.execute("select * from status order by source, process;")
        self.table.setRowCount(cur.rowcount+1)
        numinternet=0
        for row in cur:
            self.table.setItem(cur.rownumber-1, 0, QTableWidgetItem((row['source'])))
            self.table.setItem(cur.rownumber-1, 1, QTableWidgetItem((row['process'])))
            self.table.setItem(cur.rownumber-1, 2, QTableWidgetItem((row['status'])))

            if row['status']=='Working':
                self.table.item(cur.rownumber-1, 2).setBackgroundColor(QColor(148, 255, 148))

            if row['status']=='Downloading error':
                self.table.item(cur.rownumber-1, 2).setBackgroundColor(QColor(255, 148, 148))
            if row['statuschange']!=None:
                self.table.setItem(cur.rownumber-1, 3, qright(str(datetime.datetime.now()-row['statuschange'])[:-7]))

            numinternet=numinternet+row['internets']
            self.table.setItem(cur.rownumber-1, 4, qright(str(row['internets'])))
            
#            icon=QtGui.QIcon()
#            icon.addPixmap(qpixmap_pais(row[0]), QtGui.QIcon.Normal, QtGui.QIcon.Off)    
#            self.table.item(cur.rownumber-1, 1).setIcon(icon)
         
        self.table.setItem(cur.rownumber, 0, qcenter("TOTAL"))
        self.table.setItem(cur.rownumber, 4, qright(str(numinternet)))
        cur.close()     
        self.cfg.disconnect_myquotesd(con)         
        self.lblLastUpdateStatus.setText(self.trUtf8("Última actualización: {0}".format(str(now)[:-7])))
        
    def on_cmd_pressed(self):
        self.filtro=(self.txt.text())
        self.updateLog()

