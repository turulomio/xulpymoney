from PyQt4.QtCore import *
from PyQt4.QtGui import *
from libxulpymoney import *
from Ui_frmTablasAuxiliares import *

class frmTablasAuxiliares(QDialog, Ui_frmTablasAuxiliares):
    def __init__(self, cfg,  parent = None, name = None, modal = False):
        """
        Constructor
        
        @param parent The parent widget of this dialog. (QWidget)
        @param name The name of this dialog. (QString)
        @param modal Flag indicating a modal dialog. (boolean)
        """
        QDialog.__init__(self,  parent)
        if name:
            self.setObjectName(name)
        self.setModal(True)
        self.setupUi(self)
        self.cfg=cfg

        self.tblConceptos.settings("frmTablasAuxiliares",  self.cfg.inifile)
        
        self.conceptos=[]
        self.selConcepto=None
        for c in self.cfg.conceptos.list():
            if c.editable==True:
                self.conceptos.append(c)
 
        self.tblConceptos_reload()
        
#    @QtCore.pyqtSlot()  
#    def on_actionConceptosBorrar_activated(self):
#        id_conceptos= int(self.tblConceptos.item(self.tblConceptos.currentRow(), 0).text())
#        con=self.cfg.connect_xulpymoney()
#        cur =con.cursor()
#        
#        if Concepto(self.cfg).tiene_registros_dependientes(cur, id_conceptos)==False:
#            cur.execute("delete from conceptos where id_conceptos=%s", (id_conceptos, ))
#            con.commit()
#        else:
#            m=QMessageBox()
#            m.setIcon(QMessageBox.Information)
#            m.setText(self.trUtf8("Este conceptos tiene opercuentas y opertarjetas dependientes y no puede ser borrado"))
#            m.exec_()
#        cur.close()     
#        self.cfg.disconnect_xulpymoney(con)
#        self.tblConceptos_reload()
#
    @QtCore.pyqtSlot()  
    def on_actionConceptosNuevo_activated(self):
        print ("Hay que hacer dialogo para concepto y tipo de operacion")
#        concepto=QInputDialog().getText(self,  "gnuOptics > Tablas auxiliares > Nuevo concepto",  "Introduce un nuevo concepto")
#        con=self.cfg.connect_xulpymoney()
#        cur = con.cursor()
#        cur.execute("insert into conceptos(concepto,) values (%s);", (concepto[0], ))
#        con.commit()
#        cur.close()     
#        self.cfg.disconnect_xulpymoney(con)
#        self.tblConceptos_reload()
#        return


    @QtCore.pyqtSlot()  
    def on_actionConceptosModificar_activated(self):
        print ("Hay que hacer dialogo para concepto y tipo de operacion")
#        id_conceptos= int(self.tblConceptos.item(self.tblConceptos.currentRow(), 0).text())
#        con=self.cfg.connect_xulpymoney()
#        cur = con.cursor()        )
#
#        cur.execute("select * from conceptos where id_conceptos=%s", (id_conceptos, ))
#        reg= cur.fetchone()
#        cur.close()               
#        
#        concepto=QInputDialog().getText(self,  "Xulpymoney > Tablas auxiliares > Modificar concepto",  "Modifica el concepto", QLineEdit.Normal,   (reg['concepto']))        
#        
#        cur = con.cursor()
#        cur.execute("update conceptos set concepto=%s where id_conceptos=%s", ((concepto[0]),  id_conceptos ))
#        con.commit()
#        cur.close()     
#        self.cfg.disconnect_xulpymoney(con)
#        self.tblConceptos_reload()
        
    def on_tblConceptos_customContextMenuRequested(self,  pos):
        if self.selConcepto==None:
            self.actionConceptosBorrar.setEnabled(False)
            self.actionConceptosModificar.setEnabled(False)
        else:
            self.actionConceptosBorrar.setEnabled(True)
            self.actionConceptosModificar.setEnabled(True)
        
        menu=QMenu()
        menu.addAction(self.actionConceptosNuevo)
        menu.addAction(self.actionConceptosModificar)
        menu.addAction(self.actionConceptosBorrar)
        menu.exec_(self.tblConceptos.mapToGlobal(pos))

    def on_tblConceptos_itemSelectionChanged(self):
        try:
            for i in self.tblConceptos.selectedItems():#itera por cada item no row.
                self.selConcepto=self.op[i.row()]
        except:
            self.selConcepto=None
        print ("Seleccionado: " +  str(self.selConcepto))
        
    def tblConceptos_reload(self):
        self.tblConceptos.setRowCount(len(self.conceptos));
        for i, c in enumerate(self.conceptos):
            self.tblConceptos.setItem(i, 0, QTableWidgetItem(c.name))
            self.tblConceptos.setItem(i, 1, QTableWidgetItem(c.tipooperacion.name))

        
        
        
