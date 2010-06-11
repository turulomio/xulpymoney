# -*- coding: UTF-8 -*-
from mod_python import util
import sys
from xul import *
from core import *

def index(req):
    def page():
        s=xulheaderwindowmenu("Información de la Inversión")
        s=s+'<script>\n'
        s=s+'<![CDATA[\n'

        s=s+'function inversion_actualizaroperaciones(){\n'
        s=s+'    var xmlHttp;        \n'
        s=s+'    var id_inversiones='+form['id_inversiones']+';\n'
        s=s+'    var url=\'ajax/inversion_actualizaroperaciones.psp?id_inversiones=\' + id_inversiones ;\n'
        s=s+'    xmlHttp=new XMLHttpRequest();\n'
        s=s+'    xmlHttp.onreadystatechange=function(){\n'
        s=s+'        if(xmlHttp.readyState==4){\n'
        s=s+'            var ale=xmlHttp.responseText;\n'
        s=s+'            location="inversion_informacion.psp?id_inversiones="+ id_inversiones;\n'
        s=s+'        }\n'
        s=s+'    }\n'
        s=s+'    xmlHttp.open("GET",url,true);\n'
        s=s+'    xmlHttp.send(null);\n'
        s=s+'}\n'

        s=s+'function borrar(){\n'
        s=s+'    var xmlHttp;        \n'
        s=s+'    var tree = document.getElementById("treeIOH");\n'
        s=s+'    var id_inversiones='+form['id_inversiones']+';\n'
        s=s+'    var id_operinversiones=tree.view.getCellText(tree.currentIndex,tree.columns.getNamedColumn("id"));\n'
        s=s+'    var url=\'ajax/inversionoperacion_borrar.psp?id_operinversiones=\' + id_operinversiones +\'&id_inversiones=\' + id_inversiones;\n'
        s=s+'    xmlHttp=new XMLHttpRequest();\n'
        s=s+'    xmlHttp.onreadystatechange=function(){\n'
        s=s+'        if(xmlHttp.readyState==4){\n'
        s=s+'            var ale=xmlHttp.responseText;\n'
        s=s+'            alert(ale);\n'
        s=s+'            location="inversion_informacion.psp?id_inversiones="+ id_inversiones;\n'
        s=s+'        }\n'
        s=s+'    }\n'
        s=s+'    xmlHttp.open("GET",url,true);\n'
        s=s+'    xmlHttp.send(null);\n'
        s=s+'}\n'

        s=s+']]>\n'
        s=s+'</script>\n'


        s=s+'<vbox  flex="5">\n'
        s=s+'    <label id="titulo" value="Información de la Inversión" />\n'
        s=s+'    <label id="subtitulo" flex="0" value="'+reg['inversion']+'" />\n'
        s=s+'    <hbox flex="4">\n'
        s=s+'        <tabbox orient="vertical" flex="1">\n'
        s=s+'            <tabs>\n'
        s=s+'                <tab label="Inversión actual" />\n'
        s=s+'                <tab label="Movimientos de inversión" />\n'
        s=s+'                <tab label="Dividendos" />\n'
        s=s+'            </tabs>\n'
        s=s+'            <tabpanels flex="1">\n'
        s=s+'                <vbox>\n'
        s=s+listadoIOT
        s=s+'                </vbox>\n'
        s=s+'                <vbox>\n'
        s=s+listadoIOH
        s=s+'                </vbox>\n'
        s=s+'                <vbox>\n'
        s=s+listadoDiv
        s=s+'                </vbox>\n'
        s=s+'            </tabpanels>\n'
        s=s+'         </tabbox>\n'
        s=s+'    </hbox>\n'
        s=s+'</vbox>\n'
        s=s+xulfoot()
        return s
            
    
    form=util.FieldStorage(req)            
    req.content_type="application/vnd.mozilla.xul+xml"
    
    if form.has_key('id_inversiones')==False:
        sys.exit()
        
    con=Conection()
    cd=ConectionDirect()
    listadoIOT=InversionOperacionTemporal().xultree("SELECT * from tmpoperinversiones where id_Inversiones="+str(form['id_inversiones'])+" order by fecha")
    listadoIOH=InversionOperacionHistorica().xultree("SELECT * from operinversiones where id_Inversiones="+str(form['id_inversiones'])+" order by fecha",  form['id_inversiones'])
    fechapo=InversionOperacionTemporal().fecha_primera_operacion(form['id_inversiones'])
    if fechapo==None:
        listadoDiv=Dividendo().xultree("select id_dividendos, cuenta, fecha, liquido, inversion from dividendos, inversiones, cuentas where  id_dividendos=Null", 0)
    else:
        listadoDiv=Dividendo().xultree("select id_dividendos, cuenta, fecha, liquido, inversion from dividendos, inversiones, cuentas where cuentas.id_cuentas=inversiones.id_cuentas and dividendos.id_inversiones=inversiones.id_inversiones and dividendos.id_inversiones="+str(form['id_inversiones']) + " and fecha >='"+str(fechapo)+"' order by fecha;",  form['id_inversiones'])
    reg=cd.con.Execute("select * from inversiones where id_inversiones="+ str(form['id_inversiones'])).GetRowAssoc(0)
    con.close()
    cd .close()    
    return page()
