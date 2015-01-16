from libxulpymoney import *
class Update:
    """DB update system
    Cuando vaya a crear una nueva modificaci´on pondre otro if con menor que current date para uqe se ejecute solo una vez al final, tendra que 
    poner al final self.me.set_database_version(current date)
    
    To check if this class works fine, you must use a subversion 
        Subversion      DBVersion
        1702                None
    
    El sistema update sql ya tiene globals y  mete la versi´on de la base de datos del desarrollador, no obstante,
    El desarrollador deber´a meter por c´odigo todos los cambios, ha ser preferible usando objetos.7
    
    AFTER EXECUTING I MUST RUN SQL UPDATE SCRIPT TO UPDATE FUTURE INSTALLATIONS
    
    OJO EN LOS REEMPLAZOS MASIVOS PORQUE UN ACTIVE DE PRODUCTS LUEGO PASA A LLAMARSE AUTOUPDATE PERO DEBERA MANTENERSSE EN SU MOMENTO TEMPORAL
    """
    def __init__(self, mem):
        self.mem=mem
        
        self.dbversion=self.get_database_version()     
        if self.dbversion==None:
            self.set_database_version(200912310000)
        if self.dbversion<201001010000:
            self.set_database_version(201001010000)
        if self.dbversion<201412280840:
            cur=self.mem.con.cursor()
            cur.execute("update products set isin=%s where id=%s;", ("LU0252634307", 81693))
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201412280840)
        if self.dbversion<201412280940:
            cur=self.mem.con.cursor()
            cur.execute("alter table inversiones rename in_activa to active;")
            cur.execute("alter table cuentas rename cu_activa to active;")
            cur.execute("alter table tarjetas rename tj_activa to active;")
            cur.execute("alter table entidadesbancarias rename eb_activa to active;")
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201412280940)
        if self.dbversion<201412290741:
            cur=self.mem.con.cursor()
            cur.execute("alter table products drop column system;")
            cur.execute("alter table products drop column deletable;")
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201412290741)
        if self.dbversion<201412290753:
            cur=self.mem.con.cursor()
            cur.execute("alter table inversiones rename mystocksid to products_id;")
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201412290753)
        if self.dbversion<201501102221:
            cur=self.mem.con.cursor()
            cur.execute("update products set type=%s, ticker=%s, obsolete=%s where id=%s;", (1, "CIN.MC", True, 75202))
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201501102221)
        if self.dbversion<201501110635:
            cur=self.mem.con.cursor()
            cur.execute("update products set isin=%s where id=%s;", ("LU0171289225", 75042))
            cur.execute("update products set isin=%s, obsolete=%s where id=%s;", ("ES0147623039",True,  75258))
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201501110635)
        if self.dbversion<201501130928:
            cur=self.mem.con.cursor()
            cur.execute("update products set priorityhistorical=%s where type=2 and char_length(isin)>0", ([8, ], ))#Todos los fondos con isin deben estar en morning star
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201501130928)      
        if self.dbversion<201501131001:
            cur=self.mem.con.cursor()
            cur.execute("update products set active=true where priorityhistorical[1]=8 and active=false;")
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201501131001)     
        if self.dbversion<201501140855:
            cur=self.mem.con.cursor()
            cur.execute("alter table products drop column active;")
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201501140855)            
        if self.dbversion<201501141359:
            cur=self.mem.con.cursor()
            cur.execute("update products set ticker=Null where ticker='None';")
            cur.execute("update products set ticker=Null where ticker='';")
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201501141359)    
        if self.dbversion<201501141403:
            cur=self.mem.con.cursor()
            cur.execute("update products set obsolete=%s where id=%s;", (True, 76962))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 76515))
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201501141403)    
        if self.dbversion<201501142025:
            cur=self.mem.con.cursor()
            cur.execute("update products set obsolete=%s where id=%s;", (True, 75538))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 78069))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 77255))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 75392))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 75792))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 75506))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 76215))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 75205))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 75259))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 76806))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 78050))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 74966))
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201501142025)    
        if self.dbversion<201501151022:
            cur=self.mem.con.cursor()
            cur.execute("update products set priority=%s where id=79329", ([1, ], ))#Todos los fondos con isin deben estar en morning star
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201501151022)   
        if self.dbversion<201501151153:
            cur=self.mem.con.cursor()
            cur.execute("update products set pci='p' where name ilike '%put%' and type=5;")#Warrants put to put
            cur.execute("update products set apalancado=1 where type=5;")#Leverage to variable for all warrants
            cur.execute("update products set obsolete=true where  name like '%/11 %' and type=5;")#Old warrants to obsolete
            cur.execute("update products set obsolete=true where  name like '%/12 %' and type=5;")#Old warrants to obsolete
            cur.execute("update products set obsolete=true where  name like '%/13 %' and type=5;")#Old warrants to obsolete
            cur.execute("update products set obsolete=true where  name like '%/14 %' and type=5;")#Old warrants to obsolete
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201501151153)   
        if self.dbversion<201501160640:
            cur=self.mem.con.cursor()
            cur.execute("""insert into products (id, name,  isin,  currency,  type,  agrupations,   web, address,  phone, mail, tpc, pci,  apalancado, id_bolsas, ticker, priority, priorityhistorical , comentario,  obsolete) values 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (81701, 'Abengoa B',  'ES0105200002', 'EUR', 1, '|IBEX|MERCADOCONTINUO|', None, None, None, None, 100, 'c',0, 1, 'ABG-P.MC',[1, ],[3, ], None, False))
            cur.execute("update products set agrupations=%s where id=%s", ( '|IBEX|MERCADOCONTINUO|',81111 ))
            cur.execute("update products set agrupations=%s where id=%s", ( '|MERCADOCONTINUO|',81115 ))
            cur.execute("update products set agrupations=%s where id=%s", ( '|MERCADOCONTINUO|',79397 ))
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201501160640)                 
        print ("**** Database already updated")
   
    def get_database_version(self):
        """REturns None or an Int"""
        cur=self.mem.con.cursor()
        cur.execute("select value from globals where id_globals=1;")
        if cur.rowcount==0:
            cur.close()
            return None
        resultado=cur.fetchone()['value']
        cur.close()
        self.dbversion=int(resultado)
        return self.dbversion
        
    def set_database_version(self, valor):
        """Tiene el commit"""
        print ("**** Updating database from {} to {}".format(self.dbversion, valor))
        cur=self.mem.con.cursor()
        if self.dbversion==None:
            cur.execute("insert into globals (id_globals,global,value) values (%s,%s,%s);", (1,"Version", valor ))
        else:
            cur.execute("update globals set global=%s, value=%s where id_globals=1;", ("Version", valor ))
        cur.close()        
        self.dbversion=valor
        self.mem.con.commit()
