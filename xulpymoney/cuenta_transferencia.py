# -*- coding: UTF-8 -*-
from mod_python import util
import time
from core import *
from xul import *

def index(req):
    def page():
        s=xulheaderwindowmenu("Xulpymoney -> Cuentas -> Transferencia")
        s=s+'<script>\n'
        s=s+'<![CDATA[\n'

        s=s+'function insert(){\n'
        s=s+'    if (check_data()==false){\n'
        s=s+'        return;\n'
        s=s+'    }\n'
        s=s+'    var xmlHttp;    \n'
        s=s+'    var fecha = document.getElementById("fecha").value;\n'
        s=s+'    var cmbcuentaorigen=document.getElementById("cmbcuentaorigen").value;\n'
        s=s+'    var cmbcuentadestino=document.getElementById("cmbcuentadestino").value;\n'
        s=s+'    var importe = document.getElementById("importe").value;\n'
        s=s+'    var comision = document.getElementById("comision").value;\n'
        s=s+'    spfecha=fecha.split("-");\n'
        s=s+'    xmlHttp=new XMLHttpRequest();\n'
        s=s+'    xmlHttp.onreadystatechange=function(){\n'
        s=s+'        if(xmlHttp.readyState==4){\n'
        s=s+'            var ale=xmlHttp.responseText;\n'
        s=s+'            location="cuentaoperacion_listado.py?id_cuentas="+ cmbcuentadestino + "&year=" + spfecha[0] + "&month=" + spfecha[1];\n'
        s=s+'        }\n'
        s=s+'    }\n'
        s=s+'    var url="ajax/cuenta_transferencia.py?cmbcuentaorigen="+cmbcuentaorigen+"&cmbcuentadestino="+cmbcuentadestino+"&fecha="+fecha+"&importe="+importe+"&comision="+comision;\n'
        s=s+'    xmlHttp.open("GET",url,true);\n'
        s=s+'    xmlHttp.send(null);\n'
        s=s+'}\n'

        s=s+'function check_data(){\n'
        s=s+'    var resultado=true;\n'
        s=s+'    if (document.getElementById("cmbcuentaorigen").value==document.getElementById("cmbcuentadestino").value){\n'
        s=s+'        alert("La cuenta origen y destino no pueden ser la misma");\n'
        s=s+'        resultado=false;\n'
        s=s+'    }\n'
        s=s+'    if (document.getElementById("importe").value<=0){\n'
        s=s+'        alert("El importe no puede ser negativo ni cero");\n'
        s=s+'        resultado=false;\n'
        s=s+'    }\n'
        s=s+'    if (document.getElementById("comision").value<0){\n'
        s=s+'        alert("La comision no puede ser negativa");\n'
        s=s+'        resultado=false;\n'
        s=s+'    }\n'
        s=s+'    return resultado;\n'
        s=s+'}\n'
        s=s+']]>\n'
        s=s+'</script>\n'

        s=s+'<vbox  flex="1" pack="center">\n'

        s=s+'<label id="titulo" flex="1" value="Realizar una transferencia" />\n'
        s=s+'<groupbox caption ="Insertar una actualización de inversión" flex="1" border="1">\n'
        s=s+'<grid pack="center">\n'
        s=s+'<columns>\n'
        s=s+'<column flex="2" />\n'
        s=s+'<column flex="2" />\n'
        s=s+'</columns>\n'
        s=s+'<rows>\n'
        s=s+'<row>\n'
        s=s+'    <label value="Selecciona una fecha"/>\n'
        s=s+'<hbox>\n'
        s=s+'    <datepicker id="fecha" type="grid"  firstdayofweek="1" />\n'
        s=s+'</hbox>\n'
        s=s+'</row>\n'
        s=s+'<row><label id="negrita" value="Selecciona una cuenta origen"/>'+cmbcuentaorigen +'</row>\n'
        s=s+'<row><label id="negrita" value="Selecciona una cuenta destino"/>'+cmbcuentadestino+'</row>\n'
        s=s+'<row>\n'
        s=s+'    <label value="Cantidad a transferir" />\n'
        s=s+'<hbox>\n'
        s=s+'    <textbox id="importe" value="0"/>\n'
        s=s+'</hbox>\n'
        s=s+'</row>\n'
        s=s+'<row>\n'
        s=s+'    <label value="Comisión de la transferencia" />\n'
        s=s+'<hbox>\n'
        s=s+'    <textbox id="comision" value="0"/>\n'
        s=s+'</hbox>\n'
        s=s+'</row>\n'
        s=s+'<row>\n'
        s=s+'    <label value="Pulsa para aceptar la transferencia" />\n'
        s=s+'<hbox>\n'
        s=s+'<button id="cmd" label="Aceptar" onclick="insert();"/>\n'
        s=s+'</hbox>\n'
        s=s+'</row>\n'
        s=s+'</rows>\n'
        s=s+'</grid>\n'
        s=s+'</groupbox>\n'
        s=s+'</vbox>\n'
        s=s+'</window>\n'
        return s


    form=util.FieldStorage(req)    
    #Consultas BD
    con=Conection()
    #hoy=datetime.date.today()
    cmbcuentaorigen=Cuenta().cmb('cmbcuentaorigen','select * from cuentas where cu_activa=true order by cuenta',  0,  False)
    cmbcuentadestino=Cuenta().cmb('cmbcuentadestino','select * from cuentas where cu_activa=true order by cuenta',  0,  False)
    con.close()
    
    req.content_type="application/vnd.mozilla.xul+xml"
    return page()
