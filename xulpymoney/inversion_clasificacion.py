# -*- coding: UTF-8 -*-
from mod_python import util
from core import *
from xul import *
import svg

def index(req):
    form=util.FieldStorage(req)    
    con=Conection()
    cd=ConectionDirect()
    
    req.content_type="application/vnd.mozilla.xul+xml"
    req.write(xulheaderwindowmenu("Xulpymoney > Informes > Clasificación de las inversiones"))
    arrValor=[]

    req.write('        <vbox align="center">\n')
    req.write('            <label id="titulo"  value="Clasificación de las inversiones" />\n')
    req.write('        </vbox>\n')
    req.write('        <vbox flex="1">\n')
    
    total=Total().saldo_total(datetime.date.today())
    sql="select * from inversion_saldo_segun_tpcvariable() as a (tpcvariable integer, suma float);"
    curs=cd.con.Execute(sql); 
    
    sumcuentas=Total().saldo_todas_cuentas(datetime.date.today())
    arrValor.append(("Cuentas bancarias", float(round(sumcuentas, 2))))
    sumsaldos=0
    while not curs.EOF:
        row = curs.GetRowAssoc(0)   
        sumsaldos=sumsaldos+row['suma']
        name= Inversion().nombre_tpcvariable(row["tpcvariable"])
        arrValor.append((name, float(round(row['suma'], 2))))
        curs.MoveNext()     
    curs.Close()
    req.write(Total().grafico_inversion_clasificacion(arrValor))
    con.close()
    
    req.write('        </vbox>\n')
    req.write('        </window>\n')
