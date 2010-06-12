# -*- coding: UTF-8 -*-
from mod_python import util
from core import *
from xul import *

def index(req):
    def page():
        s=xulheaderwindowmenu("Insertando una operación de cuenta")

        s=s+'<script>\n'
        s=s+'<![CDATA[\n'
        s=s+'function insert(){\n'
        s=s+'    if (check_data()==false){\n'
        s=s+'        return;\n'
        s=s+'    }\n'
        s=s+'    var xmlHttp;    \n'
        s=s+'    var sp=document.getElementById("cmbconceptos").value.split(";")\n'
        s=s+'    var importe=document.getElementById("importe").value;\n'
        s=s+'    var id_conceptos=sp[0];\n'
        s=s+'    var id_tiposoperaciones=sp[1];\n'
        s=s+'    var comentario= document.getElementById("comentario").value;\n'
        s=s+'    var fecha = document.getElementById("fecha").value;\n'
        s=s+'    spfecha=fecha.split("-");\n'
        s=s+'    var id_cuentas='+str(form['id_cuentas'])+';\n'
        s=s+'    var url="ajax/cuentaoperacion_insertar.py?fecha="+fecha+"&id_conceptos="+id_conceptos+"&id_tiposoperaciones="+id_tiposoperaciones+"&importe="+importe+"&comentario="+comentario+"&id_cuentas="+id_cuentas;alert(url);\n'
        s=s+'    xmlHttp=new XMLHttpRequest();\n'
        s=s+'    xmlHttp.onreadystatechange=function(){\n'
        s=s+'        if(xmlHttp.readyState==4){\n'
        s=s+'            var ale=xmlHttp.responseText;alert(ale);\n'
        s=s+'            location="cuentaoperacion_listado.py?id_cuentas="+ id_cuentas + "&year=" + spfecha[0] + "&month=" + spfecha[1];\n'
        s=s+'        }\n'
        s=s+'    }\n'

        s=s+'    xmlHttp.open("GET",url,true);\n'
        s=s+'    xmlHttp.send(null);\n'
        s=s+'}\n'

        s=s+'function check_data(){\n'
        s=s+'    resultado=true;    \n'
        s=s+'    //Comprueba si es un float\n'
        s=s+'    var textbox=document.getElementById("importe")\n'
        s=s+'    if (!/^[-+]?[0-9]+(\.[0-9]+)?$/.test(textbox.value)){\n'
        s=s+'        textbox.setAttribute("style", "color: green; background-color: red;")\n'
        s=s+'        //textbox.style.color = "#FFAA88";\n'
        s=s+'        alert("El importe no es un número decimal");\n'
        s=s+'        resultado=false;\n'
        s=s+'    }\n'
        s=s+'    //Comprueba si tiene comillas\n'
        s=s+'    if (/[\'\"]/.test(document.getElementById("comentario").value)){//Error gettext \"\'\n'
        s=s+'        alert("No se puede meter ningún tipo de comilla");\n'
        s=s+'        resultado=false;\n'
        s=s+'    }   \n'
        s=s+'    //Comprueba la logica de GI\n'
        s=s+'    if (document.getElementById("cmbconceptos").value.split(";")[1]==1 && document.getElementById("importe").value>0){\n'
        s=s+'        alert("El importe debe ser negativo ya que el concepto seleccionado es un gasto");\n'
        s=s+'        resultado=false;\n'
        s=s+'    }          \n'
        s=s+'    if (document.getElementById("cmbconceptos").value.split(";")[1]==2 && document.getElementById("importe").value<0){\n'
        s=s+'        alert("El importe debe ser positivo ya que el concepto seleccionado es un ingreso");\n'
        s=s+'        resultado=false;\n'
        s=s+'    }        \n'
        s=s+'    return resultado;\n'
        s=s+'}\n'


        s=s+']]>\n'
        s=s+'</script>\n'
        s=s+'<label id="titulo" value="Nueva operación de cuenta" />\n'
        s=s+'<vbox flex="5">\n'
        s=s+'<grid pack="center">\n'
        s=s+'    <columns>\n'
        s=s+'        <column flex="1" />\n'
        s=s+'        <column flex="1" />\n'
        s=s+'    </columns>\n'
        s=s+'    <rows>\n'
        s=s+'        <row>\n'
        s=s+'            <label id="negrita" value="Fecha"/>\n'
        s=s+'            <datepicker id="fecha" type="grid"  firstdayofweek="1" value="'+str(year)+'-'+str(month)+'-'+str(day)+'"/>\n'
        s=s+'        </row>\n'
        s=s+'        <row>\n'
        s=s+'            <label id="negrita" value="Concepto"/>\n'
        s=s+cmbconcepto
        s=s+'        </row>\n'
        s=s+'        <row>\n'
        s=s+'            <label id="negrita" value="Importe"/>\n'
        s=s+'            <textbox id="importe"/>\n'
        s=s+'        </row>\n'
        s=s+'        <row>\n'
        s=s+'            <label id="negrita" value="Comentario"/>\n'
        s=s+'            <textbox id="comentario" value="'+comentario+'"/>\n'
        s=s+'        </row>\n'
        s=s+'    </rows>\n'
        s=s+'</grid>\n'
        s=s+'    <button label="Aceptar" oncommand="insert();"/>\n'

        s=s+'</vbox>\n'
        s=s+'</window>        \n'
        return s
    form=util.FieldStorage(req)    
    if form.has_key('concepto'):
        concepto=int(form['concepto'])
    else:
        concepto=""
    
    if form.has_key('year') and form.has_key('month'):
        year=int(form['year'])
        month=int(form['month'])
    else:
        year=datetime.date.today().year
        month=datetime.date.today().month
    day=datetime.date.today().day
    
        
    if form.has_key('comentario'):
        comentario=form['comentario']
    else:
        comentario=""
        
    con=Conection()
    cmbconcepto=Concepto().cmb('select * from conceptos where id_tiposoperaciones in (1,2) order by concepto',  concepto,  False)
    
    req.content_type="application/vnd.mozilla.xul+xml"
    con.close() 
    return page()
