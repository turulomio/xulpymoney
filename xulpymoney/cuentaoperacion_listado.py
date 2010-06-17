# -*- coding: UTF-8 -*-
from mod_python import util
import datetime
from core import *
from xul import *

def index(req):
    def page():
        s=xulheaderwindowmenu("Información de cuentas")
        s=s+'<script><![CDATA[\n'
        s=s+'var id_opercuentas=0;\n'


        s=s+'function borrar(){\n'
        s=s+'var xmlHttp;        \n'
        s=s+'var fecha = document.getElementById("fecha").value;\n'
        s=s+'spfecha=fecha.split("-");\n'
        s=s+'var id_cuentas='+str(form['id_cuentas'])+';\n'
        s=s+'var url=\'ajax/cuentaoperacion_borrar.py?id_opercuentas=\' + id_opercuentas ;\n'
        s=s+'xmlHttp=new XMLHttpRequest();\n'
        s=s+'xmlHttp.onreadystatechange=function(){\n'
        s=s+'if(xmlHttp.readyState==4){\n'
        s=s+'var ale=xmlHttp.responseText;\n'
        s=s+'location="cuentaoperacion_listado.py?id_cuentas="+ id_cuentas + "&year=" + spfecha[0] + "&month=" + spfecha[1];\n'
        s=s+'}\n'
        s=s+'}\n'

        s=s+'    xmlHttp.open("GET",url,true);\n'
        s=s+'    xmlHttp.send(null);\n'
        s=s+'}\n'

        s=s+'function tree_getid(){\n'
        s=s+'   var tree = document.getElementById("tree");\n'
        s=s+'   var selection = tree.contentView.getItemAtIndex(tree.currentIndex);\n'
        s=s+'   id_opercuentas = selection.firstChild.firstChild.getAttribute("label");\n'
        s=s+'}\n'

        s=s+'function update_list(){\n'
        s=s+'    var cmbcuentas=document.getElementById("cmbcuentas").value;\n'
        s=s+'    var year=document.getElementById("fecha").year;\n'
        s=s+'    var month=document.getElementById("fecha").month+1;\n'
        s=s+'    location="cuentaoperacion_listado.py?id_cuentas="+ cmbcuentas + "&year=" +year + "&month="+ month;\n'
        s=s+'}\n'


        s=s+'function cmbcuentas_submit(){\n'
        s=s+'    var cmbcuentas=document.getElementById("cmbcuentas").value;\n'
        s=s+'    var year=document.getElementById("fecha").year;\n'
        s=s+'    var month=document.getElementById("fecha").month+1;\n'
        s=s+'    location="cuentaoperacion_listado.py?id_cuentas="+ cmbcuentas + "&year=" +year + "&month="+ month;\n'
        s=s+'}\n'
        

        s=s+']]></script>\n'

        s=s+'<vbox align="center">\n'
        s=s+'   <label id="titulo"  value="Listado de operaciones bancarias" />\n'
        s=s+cmbcuentas
        s=s+'   <datepicker id="fecha" type="grid"  firstdayofweek="1" align="center" onchange="update_list();" value="'+str(year)+'-'+str(month)+'-'+str(day)+'"/>\n'
        s=s+'</vbox>\n'
        s=s+listado
        s=s+'</window>\n'
        return s

    form=util.FieldStorage(req)    
    #Consultas BD
    con=Conection()
    
    if form.has_key('year'):
       year=form['year']
       day=1
    else:
       year=datetime.date.today().year
       day=datetime.date.today().day
    
    if form.has_key('month'):
       month=form['month']
    else:
       month=datetime.date.today().month
    
    id_cuentas=form['id_cuentas']
    cur=CuentaOperacion().xul_listado(form['id_cuentas'],year,month)
    cmbcuentas=Cuenta().cmb('cmbcuentas','select * from cuentas where cu_activa=true order by cuenta',  form["id_cuentas"],  True)
    listado = CuentaOperacion().xul_listado( form['id_cuentas'], year,  month)
    con.close()
    
    req.content_type="application/vnd.mozilla.xul+xml"
    return page()
