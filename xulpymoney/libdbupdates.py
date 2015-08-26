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
        self.lastcodeupdate=201508242037

   
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
        
    def need_update(self):
        """Returns if update must be done"""
        if self.dbversion>self.lastcodeupdate:
            print ("WARNING. DBVEERSION > LAST CODE UPDATE, PLEASE UPDATE LASTCODEUPDATE IN CLASS")
            
            
        
        if self.dbversion==self.lastcodeupdate:
            return False
        return True
        

    def check_superuser_role(self, username):
        """Checks if the user has superuser role"""
        print ("""DEPRECATED check_superuser_role""")
        res=False
        cur=self.mem.con.cursor()
        cur.execute("SELECT rolsuper FROM pg_roles where rolname=%s;", (username, ))
        if cur.rowcount==1:
            if cur.fetchone()[0]==True:
                res=True
        cur.close()
        return res
        
    def run(self): 
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
            cur.execute("""insert into products (id, name,  isin,  currency,  type,  agrupations,   web, address,  phone, mail, tpc, pci,  apalancado, id_bolsas, ticker, priority, priorityhistorical , comentario,  obsolete) values  (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (81701, 'Abengoa B',  'ES0105200002', 'EUR', 1, '|IBEX|MERCADOCONTINUO|', None, None, None, None, 100, 'c',0, 1, 'ABG-P.MC',[1, ],[3, ], None, False))
            cur.execute("update products set agrupations=%s where id=%s", ( '|IBEX|MERCADOCONTINUO|',81111 ))
            cur.execute("update products set agrupations=%s where id=%s", ( '|MERCADOCONTINUO|',81115 ))
            cur.execute("update products set agrupations=%s where id=%s", ( '|MERCADOCONTINUO|',79397 ))
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201501160640)      
        if self.dbversion<201501160812:
            cur=self.mem.con.cursor()
            cur.execute("""insert into products (id, name,  isin,  currency,  type,  agrupations,   web, address,  phone, mail, tpc, pci,  apalancado, id_bolsas, ticker, priority, priorityhistorical , comentario,  obsolete) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (81702, 'Airbus group',  'NL0000235190', 'EUR', 1, '|CAC|EUROSTOXX|', None, None, None, None, 100, 'c',0, 3, 'AIR.PA',[1, ],[3, ], None, False))
            cur.execute("update products set agrupations=%s where id=%s", ( None,81085 ))
            cur.execute("update products set agrupations=%s where id=%s", ( None,75143 ))
            cur.execute("update products set agrupations=%s where id=%s", ( '|CAC|',78915 ))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 79008))
            cur.execute("update products set ticker=%s, priority=%s, priorityhistorical=%s where id=%s;", ('MUV2.DE',[1, ],[3, ],  80407))
            cur.execute("update products set ticker=%s, priority=%s, priorityhistorical=%s where id=%s;", ('PHIA.AS',[1, ],[3, ],  77096))
            cur.execute("update products set ticker=%s, priority=%s, priorityhistorical=%s where id=%s;", ('SAN.PA',[1, ],[3, ],  79028))
            cur.execute("update products set ticker=%s, priority=%s, priorityhistorical=%s where id=%s;", ('SAP.DE',[1, ],[3, ],  80867))
            cur.execute("update products set ticker=%s, priority=%s, priorityhistorical=%s where id=%s;", ('SU.PA',[1, ],[3, ],  77242))
            cur.execute("update products set ticker=%s, priority=%s, priorityhistorical=%s where id=%s;", ('SIE.DE',[1, ],[3, ],  80920))
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201501160812)     
        if self.dbversion<201501160838:
            cur=self.mem.con.cursor()
            cur.execute("update products set ticker=%s, agrupations=%s, priority=%s, priorityhistorical=%s where id=%s;", ('DPW.DE','|DAX|DEUTSCHEBOERSE|EUROSTOXX|', [1, ],[3, ],  79588))
            cur.execute("update products set agrupations=%s where id=%s", ( None,79008 ))
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201501160838)      
        if self.dbversion<201501170838:
            cur=self.mem.con.cursor()
            cur.execute("update products set obsolete=true where type=2 and id in (select id from products where type=2 except select id from products where type=2 and id in (select distinct (id) from quotes));")#Pone obsoletos fondos que no tengan cotizaciones despues de varios morningstar
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201501170838)      
        if self.dbversion<201501220838:
            cur=self.mem.con.cursor()
            cur.execute("update products set priority=NULL where  2=any(priority);")#Removing priority 2
            cur.execute("update products set priority=%s where  agrupations ilike '%%mercadocontinuo%%';", ([9, ], ))#Asign 9 to mercadocontinuo products
            cur.execute("update products set obsolete=%s where id=%s;", (True, 78175))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 74821))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 77112))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 77343))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 78063))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 78328))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 78862))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 78869))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 79088))
            cur.execute("update products set ticker=%s, priorityhistorical=%s where id=%s;", ('CUN.MC',[3, ],  81428))#priority ya es 9
            cur.execute("update products set ticker=%s, priorityhistorical=%s where id=%s;", ('EGPW.MC',[3, ],  78881))#priority ya es 9
            cur.execute("update products set ticker=%s, priorityhistorical=%s where id=%s;", ('MTF.MC',[3, ],  79221))#priority ya es 9
            cur.execute("update products set ticker=%s, priorityhistorical=%s where id=%s;", ('PSG.MC',[3, ],  79356))#priority ya es 9
            cur.execute("update products set ticker=%s, priorityhistorical=%s where id=%s;", ('NAT.MC',[3, ], 75607))#priority ya es 9
            cur.execute("update products set ticker=%s, priorityhistorical=%s where id=%s;", ('PRM.MC',[3, ],75609 ))#priority ya es 9
            cur.execute("update products set ticker=%s, priorityhistorical=%s where id=%s;", ('COL.MC',[3, ],77072))#priority ya es 9
            cur.execute("update products set ticker=%s, priorityhistorical=%s where id=%s;", ('UBS.MC',[3, ],78252))#priority ya es 9
            cur.execute("update products set ticker=%s, priorityhistorical=%s where id=%s;", ('CPL.MC',[3, ],78446))#priority ya es 9
            cur.execute("update products set ticker=%s, priorityhistorical=%s where id=%s;", ('ALB.MC',[3, ],78461))#priority ya es 9
            cur.execute("update products set ticker=%s, priorityhistorical=%s where id=%s;", ('ENC.MC',[3, ],79141))#priority ya es 9
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201501220838)       
        if self.dbversion<201501222338:
            cur=self.mem.con.cursor()
            cur.execute("update products set ticker=%s, priority=%s, priorityhistorical=%s where id=%s;", ('MT.AS',[1, ],[3, ],  78915))
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201501222338)     
        if self.dbversion<201502111124:
            cur=self.mem.con.cursor()
            cur.execute("update products set name=%s where id=%s;", ('Bono Estado Español 4,20  31012037', 81680))
            cur.execute("insert into products (id, name,  isin,  currency,  type,  agrupations,   web, address,  phone, mail, tpc, pci,  apalancado, id_bolsas, ticker, priority, priorityhistorical , comentario,  obsolete) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (81703, 'Masmovil Ibercom S.A.', 'ES0184696013', 'EUR', 1, '|MERCADOCONTINUO|', 'http://www.ibercom.com', None, None, None, 100, 'c', 0, 1, 'MAS.MC', [9, ],[3, ], None, False ))
            cur.execute("update products set name=%s where id=%s;", ('Telefónica S.A.', 75130))
            cur.execute("update products set name=%s where id=%s;", ('Telefónica S.A.', 78241))
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201502111124)     
        if self.dbversion<201502120609:
            cur=self.mem.con.cursor()
            cur.execute("insert into products (id, name,  isin,  currency,  type,  agrupations,   web, address,  phone, mail, tpc, pci,  apalancado, id_bolsas, ticker, priority, priorityhistorical , comentario,  obsolete) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (81704, 'AENA S.A.', 'ES0105046009 ', 'EUR', 1, '|MERCADOCONTINUO|', 'http://www.aena.es', None, None, None, 100, 'c', 0, 1, 'AENA.MC', [9, ],[3, ], None, False ))
            cur.execute("update products set name=%s, isin=%s, ticker=%s, priority=%s, priorityhistorical=%s where id=%s;",
                    ('3D Systems Corporation','US88554D2053','DDD',[1, ],[3, ],  78596))            
            cur.execute("update products set isin=%s, ticker=%s, priority=%s, priorityhistorical=%s where id=%s;",
                    ('CH0012221716','ABB',[1, ],[3, ],  78545))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 78907))
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201502120609)     
        if self.dbversion<201502120631:
            cur=self.mem.con.cursor()
            cur.execute("update products set obsolete=%s where id=%s;", (False, 78907))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 79807))
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201502120631)     
        if self.dbversion<201502131010:
            cur=self.mem.con.cursor()
            cur.execute("insert into products (id, name,  isin,  currency,  type,  agrupations,   web, address,  phone, mail, tpc, pci,  apalancado, id_bolsas, ticker, priority, priorityhistorical , comentario,  obsolete) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (81705, 'Logista Holdings', 'ES0105027009 ', 'EUR', 1, '|MERCADOCONTINUO|', 'http://www.logista.es', None, None, None, 100, 'c', 0, 1, 'LOG.MC', [9, ],[3, ], None, False ))
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201502131010)     
        if self.dbversion<201503081017:
            cur=self.mem.con.cursor()
            cur.execute("CREATE TABLE annualtargets ( year integer NOT NULL,  percentage numeric(6,2),  CONSTRAINT annualtargets_pk PRIMARY KEY (year)) WITH (  OIDS=FALSE);")
            cur.execute("ALTER TABLE annualtargets OWNER TO postgres;")
            cur.execute("CREATE INDEX annualtargets_index_year ON annualtargets USING btree (year);")
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201503081017)     
            
        if self.dbversion<201503110632: #This corrects what was done in 201501170838 and has not fill all system prices
            cur=self.mem.con.cursor()
            cur.execute("""update products set obsolete=false where id in (81443, 75234, 80854, 80853, 80866, 75341, 81288, 75497, 77335, 77440, 78545, 78172, 79287, 78399, 78381, 78401, 78457, 79015, 79416, 79382, 79387, 75379, 75393, 75847, 77291, 77438, 80494, 79398, 80557, 80844, 80845, 81158, 79854, 78306, 75488, 78209, 79203, 79210, 81359, 81362, 81446, 81444, 81424, 81445, 77096, 74793, 81703, 74816, 74808, 79206, 79372, 79490, 79526, 79629, 79751, 74809, 78748, 74845, 74849, 74851, 74888, 74900, 74823, 74832, 74787, 78575, 81427, 75130, 81358, 79761, 79762, 79963, 79971, 79991, 80007, 80060, 80074, 80075, 80155, 74789, 81361, 81363, 74756, 79468, 79484, 79489, 79509, 79510, 79516, 79517, 79553, 74801, 81278, 75446, 79890, 79891, 79920, 79923, 79925, 80205, 81423, 80215, 80218, 80440, 80722, 80725, 74933, 81085, 75762, 74804, 81704, 75043, 80322, 80323, 75212, 75282, 80856, 80858, 80864, 79487, 80252, 79513, 78596, 81176, 81184, 81272, 81274, 79040, 78907, 79043, 79404, 79409, 75598, 79692, 75646, 79901, 79902, 80946, 80947, 75884, 75914, 75348, 81611, 75586, 75527, 75543, 75544, 75726, 75727, 75728, 75731, 76131, 76138, 76139, 76093, 76095, 76096, 76097, 76267, 76263, 76243, 76372, 76500, 76477, 76685, 76698, 76699, 76700, 76702, 76812, 76814, 76894, 76895, 76896, 76898, 77012, 77015, 77016, 77018, 77022, 77121, 77238, 77246, 77224, 77231, 77349, 77352, 77353, 77502, 77503, 77481, 79132, 77520, 77522, 77638, 77639, 77728, 77998, 78040, 78024, 78025, 78112, 78214, 78280, 78283, 78290, 78295, 78370, 78373, 78495, 78531, 78606, 78607, 78703, 78712, 78777, 78779, 78871, 78874, 78882, 78883, 79102, 79104, 79276, 79294, 79303, 79368, 79453, 79460, 79462, 79438, 78219, 79217, 78885, 79970, 80173, 80326, 80339, 80353, 80481, 80678, 80680, 80919, 80921, 80922, 80923, 80924, 75065, 81151, 81152, 81253, 81153, 81266, 81269, 81598, 81380, 79996, 80182, 81563, 74765, 79961, 81375, 81578, 81505, 76430, 81705, 81695, 81686, 80876, 74788, 76851, 78222, 77210, 75066, 74753, 74759, 77370, 77453, 77555, 77707, 77855, 78098, 78117, 78159, 78160, 78221, 78834, 79078, 80728, 80734, 80735, 80744, 80746, 80748, 80750, 74950, 74934, 74943, 75055, 75061, 75070, 75085, 79350, 79352, 75098, 74998, 75038, 75090, 75093, 75095, 75039, 75071, 75073, 75704, 75110, 81604, 81676, 81659, 81661, 81662, 81663, 81664, 81668, 81669, 81670, 81673, 81674, 81675, 81660, 81671, 81665, 80485, 81667, 81672, 80110, 75122, 75160, 75156, 75158, 75159, 75163, 75169, 75188, 75154, 75157, 75182, 75086, 75087, 75097, 75102, 80321, 80324, 80327, 75199, 77553, 78447, 79377, 79962, 79703, 79177, 74847, 74968, 79019, 76650, 80156, 80206, 80298, 80403, 80503, 80639, 80716, 80727, 81213, 81214, 81241, 81244, 81263, 74792, 74806, 74807, 74820, 74825, 74769, 74790, 78968, 78999, 74852, 79000, 79011, 79175, 79199, 79219, 79224, 79225, 79236, 79237, 79253, 79258, 79264, 79265, 79268, 79296, 79309, 79334, 79348, 79353, 79375, 79376, 79390, 79401, 79402, 79405, 79407, 79415, 79437, 79442, 79455, 79456, 79457, 74881, 79458, 79459, 79464, 79466, 79467, 79554, 79578, 79579, 79580, 79585, 79590, 79591, 79593, 74870, 74983, 79598, 79622, 79623, 79628, 79632, 79633, 79635, 79636, 79697, 79712, 79716, 79720, 79721, 79736, 79737, 79795, 79835, 74891, 74887, 79837, 79838, 79842, 79845, 79846, 79859, 79888, 79934, 79936, 79939, 79941, 79944, 79945, 79948, 79954, 79960, 80005, 80006, 80015, 80016, 80019, 80021, 80022, 80025, 80026, 80051, 80053, 80055, 80056, 80057, 80058, 80059, 80094, 80099, 80102, 74890, 74904, 80106, 80112, 80113, 80116, 80127, 80128, 80168, 80178, 80187, 80191, 80192, 80194, 80196, 80219, 80228, 80231, 80248, 80261, 80263, 80272, 80276, 80279, 80285, 80300, 80305, 80316, 80342, 80354, 80355, 80357, 80368, 74896, 74899, 74928, 74906, 74907, 80388, 80396, 80402, 80405, 80411, 80413, 80418, 80419, 80420, 80429, 80434, 80438, 80449, 80454, 80477, 80483, 80489, 80508, 80524, 80526, 80532, 80535, 80539, 80544, 80565, 80566, 80591, 80600, 80603, 80604, 74924, 74930, 74931, 74932, 74989, 74910, 74922, 74923, 74926, 80607, 80619, 80630, 80631, 80634, 80636, 80641, 80644, 80650, 80651, 80652, 80695, 80696, 80718, 80721, 74944, 74935, 74939, 74954, 74957, 74962, 74963, 80751, 80753, 80800, 80861, 81245, 81249, 81256, 81257, 81277, 81291, 81296, 75018, 74955, 74975, 78952, 78958, 75002, 74999, 75014, 75016, 81600, 81625, 81628, 81630, 81640, 81642, 81643, 81644, 81646, 81657, 81658, 74996, 79007, 79009, 79010, 79012, 79014, 79021, 79023, 79024, 74990, 75032, 75164, 79189, 75078, 75069, 75059, 75074, 74992, 74994, 75194, 75196, 75198, 75200, 75201, 75225, 75226, 75213, 80328, 80329, 80330, 80331, 80517, 80625, 80626, 80627, 75233, 79186, 75235, 75240, 75248, 75249, 75250, 75237, 75239, 75251, 80628, 80629, 80833, 80834, 75241, 75257, 75309, 75298, 75303, 75306, 75307, 75548, 75308, 75328, 75330, 75332, 75299, 75313, 80868, 80869, 80870, 80871, 80872, 81169, 75340, 75345, 75378, 75337, 75356, 79187, 75380, 81170, 81172, 81173, 81174, 81175, 81185, 81186, 81187, 81188, 81189, 81190, 81191, 75391, 75400, 75403, 75404, 81192, 81193, 81194, 81195, 81196, 81197, 81198, 81199, 81217, 81218, 75436, 75428, 75429, 75438, 75440, 75441, 75444, 75447, 75448, 75457, 75455, 81219, 81220, 81270, 81271, 81279, 81280, 81281, 81282, 81283, 81285, 81287, 81289, 81290, 81292, 81293, 81295, 81300, 81302, 81303, 75430, 75487, 75490, 75491, 75505, 75510, 75489, 75513, 74833, 74848, 74874, 74927, 78947, 78948, 78949, 78950, 78951, 78963, 79003, 79006, 79027, 79029, 79038, 79044, 79045, 79050, 79184, 79185, 79190, 79239, 79240, 79241, 79246, 79247, 79248, 79259, 79261, 79263, 79269, 79270, 75483, 75536, 75528, 75552, 75524, 75545, 75537, 75541, 79271, 79274, 79284, 79285, 79311, 79314, 79315, 79318, 79321, 79322, 79324, 79325, 79327, 79328, 79338, 79339, 79340, 79341, 79342, 79344, 79345, 79346, 79347, 79357, 79403, 79417, 79421, 79422, 79429, 79430, 79432, 79433, 79434, 75519, 75520, 75578, 75583, 75556, 75579, 75555, 79497, 79498, 79499, 79501, 79503, 79504, 79505, 79506, 79507, 79515, 79518, 79519, 79539, 79540, 79587, 79589, 79594, 79595, 79596, 79597, 79600, 79602, 79603, 79605, 79606, 79616, 79617, 79619, 79620, 79621, 79624, 79626, 79627, 79630, 79631, 79673, 79674, 79675, 79676, 79681, 79684, 79685, 79686, 79688, 75600, 75601, 75608, 75616, 75634, 75635, 75637, 75596, 75611, 75614, 79693, 79696, 79701, 79702, 79704, 79705, 79706, 79707, 79710, 79717, 79722, 79724, 79725, 79726, 79727, 79728, 75123, 75124, 75129, 75141, 79729, 79730, 79734, 79738, 79777, 79778, 79779, 79780, 79782, 79785, 79792, 79793, 79794, 79798, 79801, 79802, 79803, 75644, 75647, 75643, 75661, 75669, 75673, 75675, 75653, 75657, 75674, 79806, 79808, 79810, 79811, 79812, 79814, 79815, 79816, 79830, 79831, 79832, 79833, 79836, 79839, 79843, 79847, 79848, 79851, 79895, 79896, 79897, 79898, 79899, 75155, 75167, 75175, 75176, 75177, 75178, 75180, 75181, 75193, 79900, 75641, 75652, 75683, 75702, 75686, 75690, 75705, 75730, 75738, 75712, 79919, 79921, 79922, 79927, 79928, 79929, 79931, 79932, 79933, 79937, 79940, 79943, 79947, 80020, 80035, 80040, 80041, 80042, 80045, 80046, 80047, 75197, 75203, 75211, 75214, 75217, 75221, 75224, 75229, 75744, 75756, 75780, 75777, 75749, 75765, 75232, 80050, 80052, 80143, 80144, 80145, 80146, 80147, 80148, 80149, 80150, 80152, 80153, 80154, 80157, 80160, 80341, 80343, 80550, 80883, 80885, 80886, 80887, 80888, 80889, 80890, 80891, 75242, 75244, 75252, 80892, 80893, 75739, 75746, 75787, 75782, 75796, 75798, 75811, 75785, 75791, 75826, 80894, 80895, 80896, 80897, 80898, 80899, 80900, 80901, 80902, 80903, 80904, 80905, 80906, 80907, 80908, 80909, 80910, 80911, 80912, 80913, 80914, 80915, 80916, 80936, 80937, 80938, 80939, 80940, 80941, 80942, 80943, 80944, 80945, 75827, 75828, 75848, 75849, 75851, 80948, 80949, 80950, 80951, 80952, 80953, 80954, 75277, 75279, 75788, 75253, 75260, 75266, 75271, 75272, 75274, 75276, 80955, 80956, 80957, 80958, 80959, 80960, 80961, 80962, 80963, 80964, 80965, 80966, 80967, 80968, 80969, 80970, 80971, 80972, 80973, 80974, 80975, 80996, 80997, 80998, 80999, 81000, 81001, 75830, 75871, 75875, 81613, 75863, 75890, 75895, 75854, 75855, 75857, 75858, 81002, 81003, 81004, 81005, 81006, 81007, 75305, 75311, 75315, 75323, 75324, 75326, 75331, 75336, 81008, 81009, 81010, 81011, 81012, 81013, 81014, 81015, 81016, 81017, 81018, 81019, 81020, 81021, 81025, 81026, 81027, 81028, 81029, 81030, 81031, 75891, 75869, 75870, 75873, 75880, 75882, 75901, 75916, 75927, 75929, 75931, 75935, 75936, 75942, 75943, 75913, 81058, 81059, 81060, 75353, 75339, 75358, 75363, 75367, 75368, 75369, 75371, 75372, 75373, 75374, 75375, 75376, 75377, 75381, 75384, 81063, 81065, 81066, 81067, 81068, 81069, 81070, 81072, 81073, 81086, 81565, 81566, 81587, 81588, 75898, 75928, 75900, 75955, 75964, 75966, 75602, 75977, 75968, 75969, 75970, 81589, 81590, 81591, 75422, 75424, 75385, 75394, 75397, 75402, 75405, 75419, 75421, 75427, 81592, 81607, 81608, 81609, 81610, 81612, 81614, 81615, 81616, 81617, 81618, 81619, 81620, 81621, 81622, 81623, 81624, 81626, 81634, 81637, 81638, 81639, 81647, 81648, 81649, 81650, 81651, 75945, 75948, 75950, 75953, 75978, 75986, 75987, 75989, 76009, 75980, 76020, 76836, 76010, 76018, 81652, 81653, 75432, 75442, 75445, 75451, 75453, 75463, 75466, 75470, 81654, 81655, 81656, 75493, 75494, 75508, 75521, 75522, 75549, 75550, 75551, 75553, 75557, 75560, 75566, 75568, 75569, 75571, 75573, 75576, 75979, 75988, 76019, 76048, 76025, 76045, 75584, 75585, 75591, 75592, 75593, 75603, 75604, 75627, 76296, 75665, 75666, 75668, 75670, 75671, 75672, 75679, 76333, 75734, 75736, 75685, 75691, 75701, 75706, 75707, 75719, 75721, 75723, 76164, 75735, 75747, 75766, 76079, 76092, 76100, 75751, 75752, 75755, 75757, 75763, 75764, 75769, 75770, 75773, 76461, 75783, 75794, 75795, 75805, 75808, 75813, 75821, 75822, 75823, 76540, 75843, 75831, 75833, 75834, 75837, 75841, 75842, 75850, 76582, 75894, 75905, 75912, 75921, 75923, 75926, 75932, 75934, 76116, 76120, 76140, 76149, 76162, 76165, 76125, 76117, 76126, 76163, 75961, 75962, 75963, 75965, 75967, 75974, 75976, 75982, 75985, 75991, 76008, 76011, 76014, 76015, 76060, 76070, 76035, 76036, 76042, 76043, 76044, 76046, 76047, 76058, 76062, 76087, 76099, 76118, 76132, 76178, 76184, 76185, 76186, 76194, 76202, 76214, 76203, 76213, 76192, 76105, 76098, 76101, 76115, 76147, 76119, 76123, 76127, 76128, 76129, 76135, 76144, 76146, 76148, 76150, 76151, 76169, 76166, 76170, 76172, 76174, 76177, 76179, 76182, 76183, 76368, 76219, 76220, 76224, 76228, 76282, 76324, 76328, 76238, 76240, 76242, 76225, 76188, 76190, 76197, 77085, 76218, 76221, 76222, 76223, 76235, 76239, 76241, 80212, 80213, 80214, 80216, 80217, 80433, 76266, 76276, 76269, 76277, 76275, 76244, 76245, 76262, 76315, 76326, 76327, 76331, 76336, 76283, 76325, 76281, 76319, 76329, 76339, 76343, 76285, 76286, 76290, 76292, 76293, 76294, 76295, 76297, 76303, 76311, 76312, 76323, 76334, 76335, 76349, 76350, 76386, 76364, 76376, 76395, 76396, 76409, 76369, 76375, 76385, 76387, 76410, 76360, 76361, 76363, 76367, 76379, 76382, 76389, 76390, 76391, 76392, 76399, 76406, 76407, 76408, 76411, 76412, 76420, 76435, 76637, 76467, 76472, 76413, 76416, 76459, 76460, 76466, 76423, 76437, 76468, 76426, 76428, 76431, 76433, 76434, 76436, 76438, 76441, 76442, 76445, 76451, 76452, 76453, 76454, 76462, 76464, 76465, 76473, 76474, 76475, 76478, 76479, 76481, 76498, 76511, 76513, 76547, 76526, 76512, 76499, 76480, 76484, 76495, 76496, 76497, 76504, 76516, 76518, 76519, 76520, 76521, 76523, 76530, 76539, 76542, 76545, 76548, 76553, 76559, 76560, 76561, 76563, 76564, 76588, 76590, 76572, 76550, 76571, 76554, 76555, 76566, 76567, 76568, 76569, 76573, 76583, 76584, 76585, 76586, 76587, 76589, 76595, 76597, 76599, 76600, 76604, 76606, 76607, 76610, 76602, 76593, 76617, 76622, 76594, 76598, 76601, 76616, 76618, 76619, 76642, 76649, 76624, 76653, 76658, 76665, 76644, 76645, 76640, 76663, 76643, 76625, 76631, 76633, 76634, 76635, 76636, 76638, 76639, 76646, 76647, 76648, 76652, 76666, 76668, 76669, 76673, 76681, 76682, 76683, 76684, 76711, 76689, 76696, 76705, 76706, 76709, 76687, 76695, 76697, 76703, 76717, 76718, 76719, 76736, 76737, 76741, 76744, 76749, 76742, 76750, 76721, 76722, 76726, 76727, 76732, 76733, 76734, 76735, 76743, 76747, 76748, 76753, 76768, 76785, 76763, 76792, 76755, 76761, 76783, 76754, 76759, 76769, 76770, 76771, 76773, 76776, 76777, 76778, 76781, 76782, 76788, 76800, 76802, 76811, 76801, 76808, 76803, 76809, 76813, 76817, 76842, 76854, 76855, 76856, 76840, 76843, 76818, 76819, 76820, 76822, 76823, 76824, 76825, 76826, 76827, 76849, 76850, 76853, 76859, 76863, 76860, 76864, 76865, 76867, 76868, 76869, 76870, 76871, 76876, 76877, 76878, 76879, 76880, 76882, 76883, 76885, 76890, 76891, 76901, 76903, 77024, 76902, 76881, 76886, 76887, 76893, 76899, 76900, 76904, 76907, 76941, 76942, 76943, 76940, 76944, 76908, 76909, 76918, 76919, 76921, 76923, 76924, 76926, 76938, 76939, 76946, 76950, 76956, 76963, 76964, 76974, 76989, 76959, 76965, 76966, 76973, 76975, 76976, 76977, 76978, 76983, 76985, 76986, 76988, 76991, 76994, 77006, 77010, 76993, 77004, 77132, 77011, 76995, 77000, 77002, 77005, 77023, 77025, 77030, 77031, 77032, 77041, 77039, 77064, 77065, 77052, 77066, 77033, 77037, 77040, 77044, 77048, 77062, 77063, 77067, 77068, 77070, 77073, 77071, 77074, 77076, 77077, 77078, 77081, 77082, 77086, 78464, 77093, 77095, 77098, 77101, 77091, 77094, 77092, 77097, 77104, 77109, 77146, 77138, 77141, 77113, 77114, 77119, 77120, 77126, 77127, 77128, 77129, 77133, 77149, 77151, 77154, 77184, 77188, 77153, 77185, 77187, 77281, 77157, 77152, 77155, 77156, 77159, 77160, 77161, 77162, 77163, 77164, 77165, 77166, 77167, 77177, 77178, 77179, 77180, 77181, 77182, 77183, 77198, 77207, 77209, 77197, 77200, 77201, 77205, 77194, 77196, 77206, 77208, 77213, 77215, 77216, 77219, 77220, 77222, 77223, 78711, 77235, 77236, 77239, 77232, 77237, 77241, 77258, 77254, 77261, 77263, 77267, 77268, 77269, 77270, 77275, 77279, 77280, 77283, 77284, 77288, 77293, 77295, 77296, 77334, 77341, 77342, 77340, 77286, 77292, 77339, 77299, 77300, 77302, 77303, 77305, 77306, 77307, 77327, 77338, 77348, 77373, 77374, 77377, 77387, 77391, 77385, 77354, 77355, 77356, 77368, 77369, 77375, 77379, 77381, 77382, 77383, 77386, 77390, 77398, 77405, 77396, 77399, 77426, 77392, 77403, 77411, 77419, 77420, 77421, 77422, 77424, 77433, 77472, 77454, 77442, 77455, 77457, 77429, 77437, 77439, 77447, 77463, 77464, 77465, 77474, 77475, 77484, 77487, 77494, 77495, 77496, 77497, 77498, 77499, 77500, 77501, 77530, 77533, 77527, 77535, 77504, 77505, 77506, 77507, 77508, 77509, 77512, 77518, 77519, 77521, 77534, 77540, 77543, 77544, 77545, 77536, 77554, 77537, 77560, 77563, 77564, 77577, 77581, 77583, 77565, 77566, 77567, 77570, 77571, 77574, 77585, 77598, 77599, 77586, 77587, 77588, 77602, 77589, 77590, 77591, 77593, 77594, 77595, 77597, 77637, 77620, 77606, 77608, 77629, 77635, 77621, 77622, 77623, 77624, 77625, 77626, 77640, 77642, 77644, 77681, 77682, 77696, 77646, 77650, 77651, 77652, 77653, 77654, 77655, 77657, 77659, 77672, 77673, 77674, 77675, 77676, 77679, 77680, 77687, 77688, 77692, 77694, 77697, 77699, 77703, 77708, 77709, 77717, 77723, 77726, 77727, 77731, 77735, 77716, 77698, 77715, 77706, 77710, 77713, 77718, 77719, 77720, 77721, 77722, 77725, 77732, 77733, 77734, 79575, 77767, 77768, 77738, 77771, 77774, 77776, 77778, 77741, 77742, 77743, 77744, 77745, 77746, 77747, 77748, 77759, 77760, 77761, 77769, 77775, 77777, 77779, 77780, 77781, 77783, 77821, 77820, 77782, 77784, 77786, 77787, 77788, 77789, 77790, 77791, 77792, 77793, 77794, 77800, 77801, 77802, 77803, 77804, 77805, 77806, 77810, 77816, 77818, 77819, 77822, 77826, 77827, 77828, 77830, 77840, 77841, 77837, 77849, 77857, 77823, 77831, 77833, 77834, 77835, 77842, 77843, 77844, 77845, 77847, 77848, 79784, 77861, 77862, 77864, 77866, 77868, 77870, 77876, 77890, 77896, 77858, 77859, 77860, 77874, 77875, 77877, 77878, 77879, 77887, 77888, 77889, 77893, 77894, 77895, 79809, 77900, 77903, 77908, 77919, 77915, 77918, 77923, 77938, 77928, 77914, 77997, 77922, 77901, 77902, 77906, 77909, 77910, 77911, 77921, 77930, 77931, 77932, 77933, 77934, 77935, 77936, 77964, 77945, 77951, 77952, 77954, 77965, 77966, 77944, 77947, 77946, 77948, 77939, 77940, 77941, 77942, 77943, 77953, 77956, 77960, 77963, 77969, 77970, 77996, 77999, 78001, 78002, 78003, 77973, 78000, 78279, 77992, 77974, 77975, 77976, 77979, 77980, 77981, 77986, 77987, 77988, 77991, 77993, 77995, 78005, 78006, 78013, 78019, 78038, 78042, 78043, 78028, 78029, 78030, 78031, 78032, 78033, 78034, 78035, 78037, 78039, 78053, 78058, 78051, 78046, 78047, 78049, 78052, 78054, 78055, 78057, 78059, 78062, 78064, 78065, 78077, 78072, 78080, 78101, 78103, 78079, 78104, 78107, 78088, 78102, 78100, 78082, 78084, 78085, 78086, 78087, 78090, 78096, 78109, 78128, 78199, 78149, 78111, 78138, 78150, 78115, 78113, 78114, 78116, 78119, 78120, 78121, 78124, 78125, 78131, 78132, 78134, 78135, 78136, 78137, 78151, 78152, 78155, 78153, 78180, 78154, 78164, 78165, 78168, 78157, 78161, 78162, 78163, 78166, 78167, 78169, 78170, 78171, 78174, 78177, 78178, 78179, 80291, 78182, 78185, 78187, 78192, 78194, 78216, 78217, 78218, 78223, 78228, 78211, 78213, 78183, 78193, 78197, 78200, 78206, 78207, 78227, 78208, 78212, 78224, 78225, 78226, 78233, 78234, 78239, 78245, 78232, 78230, 78240, 78243, 78244, 78246, 78247, 78248, 78255, 78256, 78260, 78262, 78265, 78266, 78267, 80425, 78294, 78282, 78284, 78285, 78289, 78291, 78292, 78302, 78388, 78304, 78305, 78275, 78277, 78297, 78298, 78301, 78303, 78307, 78349, 78308, 78311, 78312, 78337, 78315, 78347, 78309, 78236, 78310, 78313, 78314, 78320, 78321, 78329, 78335, 78336, 78338, 78339, 78340, 78341, 78343, 78344, 78345, 78348, 78352, 78354, 78356, 78359, 78366, 78374, 78375, 78376, 78377, 78360, 78361, 78363, 78364, 78367, 78358, 78362, 78368, 78369, 78414, 78386, 78394, 78396, 78397, 78413, 78416, 78417, 80640, 78389, 78385, 78387, 78390, 78391, 78392, 78393, 78395, 78400, 78404, 78408, 78409, 78411, 78421, 78422, 78423, 78431, 78434, 78436, 78438, 78439, 78430, 78441, 78424, 78425, 78426, 78427, 78428, 78429, 78432, 78433, 78435, 78437, 78440, 78443, 78444, 78469, 78548, 78481, 78482, 78483, 78499, 78475, 78486, 78491, 78476, 78492, 78445, 78448, 78449, 78454, 78460, 78465, 78466, 78467, 78468, 78477, 78479, 78480, 78487, 78494, 78496, 78500, 78515, 78506, 78508, 78511, 78512, 78521, 78525, 78527, 78539, 78516, 78502, 78503, 78504, 78507, 78509, 78510, 78513, 78514, 78517, 78520, 78523, 78526, 78528, 78532, 78533, 78542, 78543, 78544, 78550, 78540, 78541, 78551, 78549, 78552, 78553, 78554, 78555, 78556, 78562, 78570, 78572, 78573, 78564, 78566, 78571, 78574, 78563, 78522, 78557, 78558, 78560, 78561, 78576, 78584, 78586, 78600, 78588, 78599, 78597, 78601, 78585, 78587, 78589, 78590, 78592, 78593, 78594, 78598, 78605, 78608, 78629, 78631, 78642, 78645, 78602, 78633, 78609, 78640, 78603, 78604, 78610, 78619, 78635, 78637, 78641, 78648, 78612, 78613, 78620, 78627, 78628, 78630, 78632, 78634, 78644, 78647, 78691, 78697, 78705, 78708, 78653, 78578, 78580, 78581, 78582, 78583, 78679, 78686, 78688, 78652, 78684, 78685, 78689, 78650, 78658, 78662, 78664, 78670, 78674, 78675, 78677, 78680, 78681, 78682, 78690, 78693, 78701, 78706, 78713, 78714, 78715, 78722, 78729, 78745, 78716, 78718, 78723, 78724, 78725, 78726, 78727, 78728, 78730, 78731, 78734, 78736, 78737, 78738, 78739, 78743, 78763, 78791, 78796, 78797, 78678, 78772, 78776, 78798, 78746, 78749, 78750, 78752, 78762, 78760, 78761, 78767, 78768, 78769, 78771, 78781, 78800, 78812, 78814, 78825, 78836, 78839, 78817, 78821, 78927, 78822, 78827, 78828, 78829, 78804, 78805, 78806, 78809, 78811, 78813, 78815, 78819, 78837, 78873, 78870, 78965, 78753, 78845, 78846, 78853, 78854, 78855, 78856, 78858, 78859, 78863, 78864, 78865, 78866, 78868, 78906, 78910, 78920, 78935, 78939, 78942, 78953, 78926, 78912, 78896, 78897, 78898, 78900, 78901, 78902, 78905, 78932, 78961, 78899, 78917, 78918, 78919, 78923, 78925, 78928, 78929, 78933, 78934, 79004, 79022, 78971, 79087, 78972, 78973, 78991, 79041, 79047, 79048, 78979, 78981, 78982, 78983, 78987, 78989, 78995, 78997, 78998, 78966, 78988, 78994, 79013, 79017, 79018, 79053, 79056, 79057, 79060, 79061, 79064, 79069, 79063, 79070, 79058, 79052, 79055, 79067, 79071, 79077, 79086, 79089, 79096, 79105, 79093, 79095, 79107, 79113, 79091, 79081, 79082, 79083, 79085, 79072, 79079, 79080, 79084, 79090, 79097, 79099, 79100, 79101, 79108, 79109, 79110, 79111, 79112, 79114, 79117, 79125, 79126, 79127, 79128, 79164, 79176, 79179, 79129, 79131, 79134, 79146, 79165, 79168, 79172, 79138, 79167, 79130, 79137, 79143, 79148, 79149, 79152, 79471, 79173, 79133, 79166, 79153, 79154, 79158, 79169, 79170, 79174, 79178, 79180, 79182, 79273, 79254, 79211, 79218, 79213, 79222, 79231, 79233, 79232, 79205, 79230, 79234, 79209, 79226, 79227, 79243, 79301, 79302, 79291, 79312, 79297, 79286, 79358, 79288, 79290, 79292, 79305, 79306, 79307, 79308, 79323, 79326, 79365, 79396, 79411, 79214, 79419, 79378, 79380, 79381, 79383, 79384, 79385, 79882, 79386, 79388, 79370, 79362, 79373, 79389, 79392, 79393, 79414, 79431, 79391, 79394, 79400, 79492, 79494, 79508, 79514, 79521, 79439, 79440, 79441, 79443, 79447, 79448, 79450, 79512, 79527, 79463, 79469, 79470, 79472, 79480, 79491, 79493, 79500, 79543, 79582, 79584, 79599, 79572, 79573, 79625, 79545, 79546, 79548, 79549, 79550, 79551, 79552, 79555, 79556, 79557, 79558, 79576, 79581, 79586, 79544, 79542, 79669, 79700, 79711, 79713, 79667, 79668, 79670, 79671, 79637, 79638, 79639, 79640, 79641, 79642, 79643, 79644, 79647, 79661, 79709, 79634, 79708, 79796, 79850, 79755, 80498, 79756, 79797, 79844, 79849, 79753, 79760, 79763, 79764, 79765, 79766, 79767, 79770, 79771, 79774, 79749, 79750, 79789, 79747, 79758, 79856, 79865, 80068, 79918, 79852, 79853, 79855, 79857, 79864, 79874, 79875, 79876, 79879, 79883, 79884, 79885, 79886, 79889, 79892, 79893, 79894, 79861, 79862, 79887, 79967, 79968, 79975, 80008, 80014, 80024, 79969, 79972, 79976, 79980, 79981, 79982, 79984, 79985, 79988, 79964, 79966, 79990, 79997, 79987, 79992, 79995, 80009, 80010, 80011, 80012, 80013, 80017, 80018, 80071, 80121, 80082, 80096, 80097, 80105, 80162, 80063, 80064, 80065, 80095, 80098, 80062, 80066, 80067, 80091, 80092, 80077, 80129, 80100, 80101, 80111, 80119, 80122, 80123, 80124, 80125, 80126, 80142, 80190, 80207, 80237, 80238, 80163, 80174, 80175, 80166, 80179, 80188, 80195, 80227, 80181, 80200, 80203, 80204, 80233, 80234, 80235, 80236, 80247, 80167, 80169, 80170, 80171, 80172, 80176, 80177, 80209, 80275, 80251, 80255, 80256, 80253, 80310, 80311, 80313, 80264, 80265, 80267, 80270, 80274, 80286, 80287, 80288, 80320, 80249, 80250, 80254, 80294, 80296, 80358, 80312, 80317, 80318, 80319, 80325, 80340, 80344, 80383, 80390, 80410, 80421, 80391, 80394, 80397, 80400, 80406, 80345, 80356, 80387, 80416, 80435, 80408, 80409, 81064, 80412, 80424, 80427, 80431, 80352, 80360, 80382, 80386, 80389, 80422, 80423, 80426, 80428, 80430, 80432, 80459, 80529, 80538, 80455, 80439, 80461, 80474, 80476, 80536, 80549, 80457, 80458, 80470, 80471, 80472, 80473, 80478, 80480, 80482, 80514, 80516, 80486, 80487, 80488, 80490, 80492, 80493, 80523, 80527, 80528, 80533, 80537, 80540, 80547, 80548, 80567, 80589, 80592, 80663, 80554, 80555, 80556, 80558, 80580, 80581, 80582, 80583, 80563, 80590, 80597, 80632, 80642, 80664, 80584, 80585, 80586, 80588, 80621, 80623, 80624, 80593, 80595, 80596, 80598, 80599, 80673, 80697, 80747, 80665, 80666, 80929, 80684, 80686, 80688, 80703, 80704, 80736, 80737, 80739, 80757, 80758, 80759, 80671, 80674, 80675, 80667, 80672, 80707, 80712, 80715, 80745, 80749, 80806, 80823, 80824, 80855, 80859, 80860, 80862, 80760, 80761, 80796, 80802, 80804, 80822, 80847, 80766, 80769, 80793, 80794, 80831, 80832, 80873, 80917, 80918, 80925, 80926, 80927, 80928, 80930, 80931, 80932, 80976, 80977, 80978, 80979, 80980, 80981, 80982, 80983, 80984, 80985, 80986, 80987, 80988, 80989, 81032, 81033, 81035, 81036, 81037, 81038, 81039, 81107, 81108, 81109, 81150, 81022, 81023, 81024, 81154, 81156, 81159, 81162, 81171, 81155, 81157, 81160, 81161, 81242, 81243, 81246, 81247, 81255, 81258, 81297, 81299, 81265, 81259, 81264, 81275, 81298, 81364, 81360, 81487, 81488, 81489, 81490, 81491, 81492, 81493, 81494, 81495, 81496, 81498, 81499, 81351, 81353, 81354, 81355, 81430, 81465, 81466, 81467, 81468, 81469, 81471, 81470, 81425, 81501, 81502, 81564, 81567, 81627, 81593, 81596, 81599, 81601, 81602, 81603, 81605, 81606, 81631, 81632, 81633, 81594, 81595, 81597, 81629, 81636, 81645, 81536, 81522, 81503, 81504, 81506, 81507, 81508, 81509, 81510, 81511, 81512, 81500, 81682, 75990, 76106, 76107, 77001, 77276, 77277, 77278, 77714, 77752, 78317, 78318, 78319, 81702, 79028, 80867, 77242, 80920, 78668, 78671, 78672, 78843, 78985, 78986, 78990, 79026, 79034, 79042, 79956, 80468, 80576, 80577, 80578, 80587, 80594, 80691, 80784, 80995, 79032, 79913, 80491, 76102, 76670, 76674, 76852, 76916, 76917, 77118, 77186, 77195, 77203, 77240, 77477, 77482, 77882, 77978, 76384, 78747, 78754, 77329, 81393, 81395, 81396, 81409, 81415, 81419, 81432, 81433, 81434, 81435, 81437, 75091, 75170, 75465, 76112, 76289, 76298, 76404, 76415, 76417, 76419, 76422, 76398, 76425, 76427, 76429, 76432, 76463, 76469, 76470, 76483, 76486, 76487, 76488, 76489, 76490, 76491, 76492, 76493, 76494, 76505, 76506, 76508, 76509, 76510, 76517, 76522, 80359, 76524, 76531, 76532, 76533, 76534, 76657, 76667, 76675, 76676, 76677, 76678, 76680, 76686, 77150, 77260, 77262, 77266, 77282, 77285, 77287, 77289, 77297, 77298, 77308, 77309, 77310, 77311, 77312, 77314, 77345, 77346, 77361, 77365, 77366, 77367, 77404, 77406, 77407, 77408, 77410, 77412, 77413, 77982, 77983, 77984, 77985, 78004, 78330, 78331, 78355, 78519, 78529, 78530, 78534, 78538, 78546, 78547, 78595, 78611, 78615, 78616, 78710, 78720, 78733, 78740, 78741, 78785, 78787, 78894, 78895, 78914, 78921, 78931, 78938, 78941, 78944, 79059, 79062, 79065, 79068, 79074, 79075, 79076, 79092, 79098, 79103, 79106, 79115, 79116, 79118, 79119, 79120, 79121, 79122, 79123, 79124, 79147, 79257, 79260, 79266, 79293, 79304, 79330, 79612, 79613, 79618, 79645, 79646, 79648, 80037, 80039, 80044, 80049, 80054, 80061, 80069, 80072, 80073, 80076, 80079, 80080, 80086, 80087, 80088, 80109, 80114, 80115, 80117, 80118, 80120, 80130, 80131, 80134, 80135, 80137, 80138, 80139, 80140, 80141, 80151, 80159, 80884, 80161, 80164, 81071, 80165, 80180, 80183, 80184, 80185, 80186, 80189, 80197, 80198, 80199, 80201, 80220, 80221, 80222, 80223, 80224, 80225, 80258, 74758, 74739, 74740, 74757, 74760, 74767, 80259, 80260, 74971, 75103, 75165, 75166, 80262, 75357, 75526, 75722, 76006, 80266, 76257, 77058, 77108, 80268, 80269, 80273, 80277, 77233, 77234, 80282, 80283, 80284, 79139, 80289, 80290, 80292, 80293, 80297, 80299, 80301, 80307, 80308, 80309, 80314, 80315, 80333, 80436, 80437, 80441, 80442, 80443, 80444, 80446, 80501, 80504, 80506, 80507, 80509, 80510, 80511, 80519, 80520, 80521, 80522, 80525, 80534, 80542, 80605, 80606, 80609, 80611, 80612, 80613, 80614, 80615, 80616, 80617, 80618, 80620, 80622, 80633, 80643, 80645, 80646, 80726, 80731, 80743, 80754, 80756, 80762, 80763, 80764, 80777, 80778, 80779, 80781, 80782, 80783, 80687, 80785, 80786, 80787, 80788, 80790, 80792, 80799, 80801, 80805, 80807, 80808, 80809, 80810, 80811, 80812, 80814, 80815, 80826, 80827, 80828, 80993, 80994, 81040, 81041, 81042, 81044, 81045, 81047, 81048, 81049, 81052, 81054, 81055, 81056, 81057, 81061, 81076, 81077, 81079, 81211, 81212, 81215, 81216, 81221, 81224, 81225, 81227, 81228, 81229, 81231, 81232, 81233, 81234, 81235, 81237, 81238, 81239, 81240, 81248, 81316, 81317, 81318, 81319, 81320, 81321, 81322, 81323, 81324, 81325, 81326, 81328, 81331, 81332, 81333, 81334, 81339, 81340, 81341, 81343, 81344, 81345, 81365, 81366, 81386, 81387, 81388, 81389, 81390, 81397, 81399, 81400, 81401, 81403, 81404, 81405, 81406, 81407, 81414, 81416, 81422, 81455, 81456, 81457, 81462, 81482, 81483, 81484, 81485, 81486, 77633, 77649, 77656, 77658, 77663, 77664, 77677, 77678, 77683, 77684, 74853, 74844, 81294, 77686, 77691, 77701, 77724, 77740, 77770, 77772, 77785, 77796, 78415, 78473, 79036, 78964, 78775, 78455, 81699, 81700, 81102, 78333, 78238, 78346, 78383, 78398, 78127, 78471, 79329, 78472, 78518, 76268, 81438, 76821, 77376, 78924, 79574, 80271, 81034, 76264, 76603, 76739, 77211, 77384, 77344, 77582, 76651, 77627, 77020, 75709, 80158, 77578, 81267, 74803, 78962, 80407, 79016, 79588, 79051, 79135, 79163, 79200, 79202, 79136, 79277, 79278, 79279, 79283, 79289, 79298, 79300, 79333, 74785, 79663, 79699, 78231, 80103, 77046, 78524, 81082, 75540, 78094, 80475, 78717, 79788, 77529, 75852, 79520, 79592, 75450, 77347, 79502, 75625, 75732, 75829, 75325, 78649, 75872, 75462, 75638, 75748, 77628, 77739, 78110, 75700, 81276, 77603, 78687, 78751, 79374, 75715, 78830, 77328, 75806, 76990, 75786, 74824, 77904, 77274, 75944, 76557, 78936, 81091, 75930, 79834, 79694, 75295, 81090, 81083, 75302, 75838, 75559, 76029, 75758, 76330, 76701, 76920, 77552, 78083, 78220, 78646, 78810, 79310, 79379, 79335, 81088, 79336, 77580, 75420, 75741, 79465, 78270, 77949, 78903, 76527, 77546, 76258, 74872, 78372, 75322, 76691, 79171, 75278, 76167, 74843, 77456, 76280, 74895, 81087, 80093, 75037, 74993, 74873, 75973, 76720, 76082, 76217, 76738, 76790, 76897, 76981, 78278, 77134, 77301, 77430, 79256, 79343, 80229, 77605, 78017, 78020, 78915, 78967, 80767, 80768, 81286, 74746, 75971, 76081, 79262, 78259, 75006, 78272, 74747, 81691, 81694, 81439, 79354, 79355, 79395, 79399, 79425, 79201, 80662, 80839, 81348, 81350, 81352, 81356, 81370, 81371, 81372, 81447, 78273, 79495, 79533, 79534, 79689, 79690, 80230, 80348, 75136, 81429, 81426, 81514, 81515, 81516, 81517, 81518, 81519, 81520, 81523, 81525, 81526, 81527, 81528, 81529, 81531, 81535, 81537, 81513, 81533, 81701, 81111, 79397, 80846, 78451, 81114, 81104, 81101, 78880, 81346, 81093, 79192, 81530, 78334, 79299, 81534, 80820, 81690, 81521, 79418, 75588, 78867, 81532, 76001, 76002, 76103, 76104, 75284, 75290, 81688, 78269, 79037, 81698, 81428, 78881, 79221, 79356, 75607, 75609, 77072, 78252, 78446, 78461, 79141, 76256, 76259, 76365, 76381, 76383, -7, 76388, 76476, 78241, 76053, 77363, 77466, 77469, 81683, 81440, 81692, 74959, 75147, 79360, 77609, 77611, 77612, 77613, -18, 77617, 77619, 81115, 77883, 77892, 77920, 78016, 78026, 78089, 78091, 78229, 78235, 81681, 81357, 78237, 78253, 81336, 81337, 81338, 75140, 75053, -3, 74791, -6, -8, 81582, -5, 81583, 81585, 79361, 80575, 80579, 75143, 80677, 80685, 80740, 81204, 81410, 81411, 81412, 81043, 75677, 75815, 75816, 75817, 75818, 75866, 75383, 75041, 81092, 81394, 76113, 81685, 81448, 78908, 75867, 75993, 76049, 76414, 76421, 76623, 74967, 81680, 77853, 77856, 75067, 75135, 77880, 81112, 81524, 80515, 79142, 79223, 79046, 78281, 81689, 79331, 79332, 79454, 79486, 79488, 80361, 80635, 80637, 80638, 80877, 80878, 80879, 81436, 80880, 80881, 81113, 75052, 75280, 78474, 78325, 81452, 81454, 81459, 74796, 74797, 74799, 74819, 74827, 74855, 74866, 74868, 76996, 74869, 79244, 78412, 78886, 81480, 75042, 79743, 77199, 74908, 74929, 74936, 74893, 79197, 78327, 81441, 74958, 81684, -9, 79204, 74961, 74965, 74744, 74986, 80840, 81105, 81117, 81347, 78384, 81103, 79228, -4, 81687, 75119, 75120, 81693, 75126, 75128, 75131, 75144, 75162, 75168, 79359, 81127, 79162, 75063, 75127, 75417, 75458, 75580, 75581, 75590, 75630, 75636, 78940, 79746, 79989, 81053, 74795, 75118, 75291, 75300, 75558, 75703, 75710, 75711, 81463, 81472, 75714, 75861, 75862, 75960, 76110, 76133, 76134, 76152, 76153, 76154, 76155, 76156, 76158, 76248, 76249, 76250, 76580, 76581, 76596, 76730, 76731, 76866, 76872, 77753, 77754, 77755, 77756, 77851, 78257, 78258, 78263, 78274, 78316, 81335, 81475, 81584, 81586, 81417, 81418, 74858, 75293, 75390, 79025, 79030, 78380, 78459, 78493, 78577, 78579, 78721, 78742, 81460, 81461, 81473, 81474, 81476, 81477, 81478, 81479, 78744, 75542, 78210, 75236, 78036, 78066, 78831, 78788, 78189, 80852, 79140, 79194, 79317, 79682, 81301, 74784, 74969, 74987, 74991, 74995, 75001, 75044, 75064, 75174, 75184, 75190, 75191, 75192, 75218, 75219, 75220, 75222, 75223, 75228, 75263, 75270, 75273, 75283, 75288, 75319, 75320, 75321, 75343, 75344, 75351, 75352, 75360, 75362, 75366, 75408, 75409, 75410, 75413, 75415, 75416, 75431, 75433, 75437, 75439, 75443, 75449, 75370, 75460, 75464, 75468, 75473, 75474, 75478, 75480, 75482, 75486, 75498, 75499, 75501, 75502, 75518, 75525, 75530, 75564, 75567, 75610, 75613, 75617, 75618, 75623, 75624, 75649, 75655, 75656, 75659, 75660, 75667, 75688, 75689, 75695, 75716, 75718, 75761, 75767, 75768, 75771, 75772, 75775, 75801, 75812, 75814, 75819, 75835, 75844, 75853, 75864, 75865, 75868, 75881, 75889, 75904, 75906, 75908, 75909, 75937, 75939, 75941, 76003, 76005, 76007, 76030, 76032, 76034, 76038, 76051, 76054, 76055, 76056, 76057, 76061, 76075, 76076, 76077, 76083, 76094, 76013, 76159, 76160, 76161, 76204, 76205, 76206, 76207, 76209, 76210, 76211, 76261, 76300, 76302, 76304, 76305, 76309, 76310, 76314, 76316, 76318, 76342, 76347, 76357, 76358, 76393, 76394, 76400, 76403, 76440, 76443, 76447, 76448, 76449, 76450, 76456, 76457, 76458, 76535, 76536, 76537, 76538, 76543, 76544, 76552, 76570, 76575, 76578, 76627, 76628, 76630, 76632, 76641, 76654, 76655, 76656, 76688, 76692, 76704, 76710, 76713, 76714, 76716, 76723, 76728, 76746, 76751, 76758, 76774, 76775, 76779, 76787, 76789, 76793, 76795, 76805, 76816, 76828, 76830, 76832, 76844, 76847, 76873, 76875, 76888, 76892, 76922, 76927, 76930, 76931, 76932, 76933, 76934, 76935, 76947, 76957, 76958, 76980, 76997, 76998, 77008, 77009, 77014, 77017, 77021, 77026, 77028, 77029, 77035, 77050, 77053, 77060, 77061, 77069, 77075, 77084, 77088, 77099, 77102, 77107, 77122, 77123, 77124, 77131, 77135, 77136, 77137, 77139, 77140, 77142, 77143, 77145, 77147, 77169, 77170, 77173, 77174, 77175, 77212, 77214, 77217, 77221, 77225, 77226, 77227, 77228, 77244, 77245, 77315, 77317, 77318, 77319, 77320, 77321, 77322, 77323, 77324, 77325, 77326, 77330, 77331, 77333, 77336, 77337, 77414, 77415, 77427, 77441, 77443, 77459, 77460, 77461, 77462, 77510, 77513, 77514, 77516, 77524, 77556, 77557, 77558, 77559, 77561, 77562, 77569, 77667, 77668, 77669, 77670, 77671, 77757, 77758, 77763, 77764, 77811, 77832, 77838, 77929, 77937, 78007, 78009, 78011, 78012, 78122, 78133, 78139, 78141, 78143, 78144, 78156, 78158, 78173, 78181, 78184, 78188, 78191, 78195, 78196, 78323, 78324, 78403, 78405, 78406, 78418, 78419, 78442, 78450, 78452, 78453, 78462, 78463, 78470, 78484, 78485, 78488, 78501, 78624, 78626, 78654, 78656, 78660, 78661, 78663, 78665, 78666, 78667, 78673, 78676, 78683, 78692, 78694, 78695, 78696, 78698, 78719, 78792, 78795, 78807, 78808, 78816, 78838, 78840, 78848, 78849, 78851, 78857, 78877, 78878, 78879, 78884, 78889, 78890, 78892, 78945, 78954, 78957, 78969, 78970, 78976, 78978, 78980, 78984, 79049, 79054, 79150, 79151, 79155, 79156, 79159, 79160, 79161, 79183, 79188, 79191, 79193, 79195, 79196, 79198, 79207, 79212, 79245, 79252, 79255, 79363, 79366, 79367, 79406, 79408, 79420, 79423, 79426, 79427, 79428, 79436, 79444, 79449, 79452, 79483, 79511, 79522, 79523, 79524, 79525, 79528, 79529, 79531, 79536, 79537, 79541, 79559, 79560, 79561, 79562, 79563, 79564, 79565, 79569, 79570, 79571, 79601, 79609, 79610, 79650, 79651, 79652, 79653, 79655, 79657, 79658, 79665, 79666, 79672, 79683, 79687, 79719, 79731, 79732, 79733, 79735, 79739, 79740, 79745, 79757, 79759, 79773, 79775, 79783, 79791, 79820, 79821, 79828, 79840, 79841, 79858, 79860, 79863, 79870, 79871, 79880, 79904, 80032, 79912, 79914, 79915, 79917, 79924, 79926, 79930, 79942, 79946, 79949, 79950, 80081, 79951, 79955, 79958, 79959, 79973, 79977, 79978, 79986, 79993, 79994, 79999, 80000, 80002, 80003, 80004, 80023, 80029, 80031, 80033, 80034, 80036, 80038, 80090, 80107, 80108, 80226, 80240, 80241, 80242, 80243, 80244, 80245, 80246, 80257, 80335, 80336, 80346, 80349, 80351, 80367, 80371, 80373, 80374, 80378, 80381, 80392, 80393, 80395, 80398, 80399, 80404, 80415, 80417, 80452, 80453, 80456, 80460, 80464, 80465, 80466, 80467, 80469, 80484, 80495, 80496, 80497, 80499, 80500, 80543, 80545, 80551, 80552, 80559, 80564, 80568, 80570, 80571, 80572, 80573, 80574, 80601, 80602, 80657, 80659, 80660, 80661, 80669, 80676, 80679, 80681, 80682, 80692, 80693, 80700, 80708, 80711, 80713, 80714, 80720, 80723, 80741, 80765, 80770, 80771, 80772, 80773, 80775, 80776, 80780, 80829, 80836, 80838, 80841, 80848, 80849, 80851, 80857, 80863, 80882, 80990, 80992, 81080, 81081, 81094, 81098, 81099, 81100, 81116, 81119, 81123, 81124, 81125, 81126, 81128, 81129, 81130, 81132, 81133, 81138, 81141, 81144, 81145, 81306, 81179, 81180, 81181, 81182, 81183, 81201, 81203, 81205, 81206, 81207, 81208, 81250, 81251, 81260, 81261, 81268, 81307, 81310, 81313, 81314, 81315, 81373, 81377, 81378, 81379, 81381, 81382, 81383, 81384, 81385, 81544, 81545, 81546, 81547, 81549, 81553, 81554, 81555, 81556, 81557, 81558, 81559, 81568, 81569, 81570, 81571, 81577, 81581, 74751, 76614, 75737, 75760, 76021, 76023, 76026, 76027, 76028, 76050, 76067, 76068, 76072, 76136, 76137, 76145, 76187, 76189, 76198, 76199, 76200, 76237, 76252, 76253, 76320, 76321, 76322, 76370, 76374, 76377, 76378, 76380, 76612, 76613, 76664, 77350, 77351, 77357, 77358, 77473, 77523, 77526, 77539, 77542, 77575, 77576, 77592, 77601, 77630, 77631, 77632, 77814, 77815, 77863, 77869, 77871, 77872, 77905, 77912, 77957, 77959, 77967, 77971, 78060, 78073, 78099, 78105, 78145, 78146, 78198, 78242, 78249, 78250, 78286, 78287, 78288, 78293, 78300, 78707, 78735, 78888, 78992, 79002, 81413, 80837, 81421, 80001, 80752, 81458)""") 
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201503110632)  

        if self.dbversion<201504121011:
            cur=self.mem.con.cursor()
            cur.execute("update products set obsolete=%s where id=%s;", (True, 74744))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 74959))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 74967))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 75052))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 75053))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 75135))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 75136))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 75140))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 75147))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 75280))
            cur.execute("update products set obsolete=%s where id=%s;", (True, 75284))
            cur.execute("update products set ticker=%s, priority=%s, priorityhistorical=%s where id=%s;", ('TIT.MI',[1, ],[3, ],  75067))
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201504121011)     
            
        if self.dbversion<201504150622:
            cur=self.mem.con.cursor()
            cur.execute("update products set tpc=%s where id=%s;", (0, 76309))
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201504150622)   
        if self.dbversion<201507151008:
            cur=self.mem.con.cursor()#Empty due to check role probes
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201507151008)        
        if self.dbversion<201507291541:
            cur=self.mem.con.cursor()
            cur.execute("alter table operinversiones add column show_in_ranges boolean")
            cur.execute("alter table operinversiones alter column show_in_ranges set default true;")
            cur.execute("update operinversiones set show_in_ranges =true")
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201507291541)         
        if self.dbversion<201507291626:
            cur=self.mem.con.cursor()
            cur.execute("update operinversiones set show_in_ranges=false where id_tiposoperaciones in (5,6)")
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201507291626)         
        if self.dbversion<201508242037:
            cur=self.mem.con.cursor()
            cur.execute("CREATE SEQUENCE simulations_seq  INCREMENT 1  MINVALUE 1  MAXVALUE 9223372036854775807  START 1  CACHE 1;")
            cur.execute("CREATE TABLE simulations(  database text,  id integer NOT NULL DEFAULT nextval('simulations_seq'::regclass),  starting timestamp with time zone,  ending timestamp with time zone,  type integer,  creation timestamp with time zone,  CONSTRAINT simulations_pk PRIMARY KEY (id)) WITH (OIDS=FALSE);")
            cur.close()
            self.mem.con.commit()
            self.set_database_version(201508242037)         
            
            


            
        """       WARNING                    ADD ALWAYS LAST UPDATE CODE                         WARNING
        
        
        AFTER EXECUTING I MUST RUN SQL UPDATE SCRIPT TO UPDATE FUTURE INSTALLATIONS
    
    OJO EN LOS REEMPLAZOS MASIVOS PORQUE UN ACTIVE DE PRODUCTS LUEGO PASA A LLAMARSE AUTOUPDATE PERO DEBERA MANTENERSSE EN SU MOMENTO TEMPORAL"""  
        print ("**** Database already updated")
