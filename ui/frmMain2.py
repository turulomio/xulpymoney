import   os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Ui_frmMain2 import *
from frmAbout import *
from frmAccess import *
from wdgInversiones2 import *
from wdgLog import *
 

class frmMain2(QMainWindow, Ui_frmMain2):#    
    def __init__(self, parent = 0,  flags = False):
        """
        Constructor
        
        @param parent The parent widget of this dialog. (QWidget)
        @param name The name of this dialog. (QString)
        @param modal Flag indicating a modal dialog. (boolean)
        """

            
        QMainWindow.__init__(self, None)
        self.setupUi(self)
        self.showMaximized()
        self.setWindowTitle(self.trUtf8("MyStocks 2010-{0} ©".format(version[:4])))
        
        self.cfg=ConfigMyStock()
        
        self.w=QWidget()       
        self.w.setAttribute(Qt.WA_DeleteOnClose) 
        access=frmAccess(self.cfg, 1)
        access.setWindowTitle(self.trUtf8("MyStocks - Acceso"))
        QObject.connect(access.cmdYN, SIGNAL("rejected()"), self, SLOT("close()"))
        access.exec_()
        self.w.close()

        
        
        self.cfg.conms=self.cfg.connect_myquotes()
        self.cfg.actualizar_memoria()
        
        if Global(self.cfg).get_sourceforge_version()>version:
            m=QMessageBox()
            m.setText(QApplication.translate("myquotes","Hay una nueva versión publicada en http://myquotes.sourceforge.net"))
            m.exec_()        
        if Global(self.cfg).get_database_init_date()==str(datetime.date.today()):
            m=QMessageBox()
            m.setText(QApplication.translate("myquotes","La base de datos se acaba de iniciar.\n\nSe necesitan al menos 24 horas de funcionamiento del demonio myquotesd para que esta aplicación tenga todos los datos disponibles."))
            m.exec_()       
        
        self.w=wdgInversiones2(self.cfg,  "select * from investments where name='VACIO' order by name")

        self.layout.addWidget(self.w)
        self.w.show()
        
    def __del__(self):
        print ("Saliendo de la aplicación")
        self.cfg.disconnect_myquotes(self.cfg.conms)
        
    @pyqtSignature("")
    def on_actionAcercaDe_activated(self):
        fr=frmAbout(self.cfg, self)
        fr.open()

                
    @QtCore.pyqtSlot()  
    def on_actionCAC40_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where agrupations like '%|CAC|%' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()                
    @QtCore.pyqtSlot()  
    def on_actionActive_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where active=true order by name")

        self.layout.addWidget(self.w)
        self.w.show()
            
    @QtCore.pyqtSlot()  
    def on_actionCambioNombre_activated(self):
        w=frmCambioNombre(self.cfg)
        w.exec_() 
    
    @QtCore.pyqtSlot()  
    def on_actionDivisas_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where type=6 order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
    @QtCore.pyqtSlot()  
    def on_actionDividendos_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where id in (select distinct(quotes.id) from quotes, estimaciones where quotes.id=estimaciones.id and year=2012  and dpa > 0 );")

        self.layout.addWidget(self.w)
        self.w.on_actionOrdenarDividendo_activated()
        self.w.show()

    @QtCore.pyqtSlot()  
    def on_actionExportar_activated(self):
        os.popen("pg_dump -U postgres -t quotes myquotes | sed -e 's:quotes:export:' | gzip > "+os.environ['HOME']+"/.myquotes/dump-%s.txt.gz" % str(datetime.date.today()))
        m=QMessageBox()
        m.setText(QApplication.translate("Config","Se ha exportado con éxito la tabla quotes"))
        m.exec_()      

    @QtCore.pyqtSlot()  
    def on_actionImportar_activated(self):
        filename=(QFileDialog.getOpenFileName(self, self.tr("Selecciona el fichero a importar"), os.environ['HOME']+ "/.myquotes/", "Gzipped text (*.txt.gz)"))
        inicio=datetime.datetime.now()
        con=self.cfg.connect_myquotes()
        cur = con.cursor()
        print ("Importando la tabla export")
        os.popen("zcat " + filename  + " | psql -U postgres myquotes")
        cur.execute("insert into quotes(select * from export where code||date::text in (select code||date::text from export except select code||date::text from quotes));") #solo los que faltan no los modificados que sería select * en los dos lados
        con.commit()
        estado=cur.statusmessage
        print ("Borrando la tabla export y sus índices")
        cur.execute("drop table export;")
        con.commit()        
        cur.execute("DROP INDEX index_export_unik;")
        con.commit()
        cur.execute("DROP INDEX index_export_unik2;")
        con.commit()
        cur.close()
        self.cfg.disconnect_myquotesd(con)      
        fin=datetime.datetime.now()
        
        m=QMessageBox()
        m.setText("Ha tardado %s y ha salido con mensaje de estado %s" % (str(fin-inicio),  estado))
        m.exec_()            


        
    @QtCore.pyqtSlot()  
    def on_actionNasdaq100_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where agrupations like '%|NASDAQ100|%' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
            
    @QtCore.pyqtSlot()  
    def on_actionMC_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg, "select * from investments where agrupations like '%|MERCADOCONTINUO|%' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
        

    @QtCore.pyqtSlot()  
    def on_actionETF_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where type=4 order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionEurostoxx50_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where agrupations like '%|EUROSTOXX|%' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
        

    @QtCore.pyqtSlot()  
    def on_actionFavoritos_activated(self):
        favoritos=self.cfg.config_load_list(self.cfg.config,"wdgInversiones2",  "favoritos")
        if len(favoritos)==0:
            m=QMessageBox()
            m.setIcon(QMessageBox.Information)
            m.setText(self.trUtf8("No se ha seleccionado ningún favorito"))
            m.exec_()     
            return
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where id in ("+str(favoritos)[1:-1]+") order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()

                        

    @QtCore.pyqtSlot()  
    def on_actionAcciones_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where type=1 order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()          
    @QtCore.pyqtSlot()  
    def on_actionWarrants_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where type=5 order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()          
        
    @QtCore.pyqtSlot()  
    def on_actionWarrantsCall_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where type=5 and pci='c' order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()              
    @QtCore.pyqtSlot()  
    def on_actionWarrantsPut_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where type=5 and pci='p' order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()              
    @QtCore.pyqtSlot()  
    def on_actionWarrantsInline_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where type=5 and pci='i' order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()      
    @QtCore.pyqtSlot()  
    def on_actionFondos_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where type=2 order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()                        

    @QtCore.pyqtSlot()  
    def on_actionDeudaPublica_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where type=7 order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()                        

    @QtCore.pyqtSlot()  
    def on_actionDeudaPrivada_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where type=9 order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()

        
    @QtCore.pyqtSlot()  
    def on_actionRentaFija_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where type in (7,9) order by name, id")

        self.layout.addWidget(self.w)
        self.w.show()

        

    @QtCore.pyqtSlot()  
    def on_actionIbex35_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select  * from investments where agrupations like '%|IBEX|%' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionIndexes_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select  * from investments where type=3 order by id_bolsas,name")

        self.layout.addWidget(self.w)
        self.w.show()        
                
    @QtCore.pyqtSlot()  
    def on_actionSP500_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where agrupations like '%|SP500|%' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
    
    @QtCore.pyqtSlot()  
    def on_actionInversionesDesaparecidas_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where obsolete=true order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
                
    @QtCore.pyqtSlot()  
    def on_actionInversionesSinActualizar_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where id in( select id  from quotes group by id having last(datetime::date)<now()::date-60)")

        self.layout.addWidget(self.w)
        self.w.show()       
    
    @QtCore.pyqtSlot()  
    def on_actionInversionesSinActualizarHistoricos_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg, "select * from investments where id in (select id from quotes  group by id having date_part('microsecond',last(datetime))=4 and last(datetime)<now()-interval '60 days' );")

        self.layout.addWidget(self.w)
        self.w.show()            
        
    @QtCore.pyqtSlot()  
    def on_actionInversionesManual_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where id<0 order by name, id ")

        self.layout.addWidget(self.w)
        self.w.show()
        
    @QtCore.pyqtSlot()  
    def on_actionInversionesSinISIN_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments  where isin is null or isin ='' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()


    @QtCore.pyqtSlot()  
    def on_actionInversionesSinNombre_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments  where name is null or name='' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()

        
    @QtCore.pyqtSlot()  
    def on_actionTablasAuxiliares_activated(self):
        w=frmTablasAuxiliares(self.cfg)
        w.tblTipos_reload()
        w.exec_()

                
    @QtCore.pyqtSlot()  
    def on_actionXetra_activated(self):
        self.w.close()
        self.w=wdgInversiones2(self.cfg,  "select * from investments where agrupations like '%|DAX|%' order by name,id")

        self.layout.addWidget(self.w)
        self.w.show()
        
