<%
import time
from core import *
from xul import *

#Consultas BD
con=Conection()
checked=""
id_inversiones=0
if form.has_key('id_inversiones'):
    id_inversiones=form['id_inversiones']

con.close()

req.content_type="application/vnd.mozilla.xul+xml"
req.write(xulheaderwindowmenu("Xulpymoney > Inversiones > Dividendo > Nuevo"))

%>
<script>
<![CDATA[
function insert(){
    var id_inversiones=<%=id_inversiones%>;
    var fecha = document.getElementById("fecha").value;
    var valorxaccion = document.getElementById("valorxaccion").value;
    var bruto = document.getElementById("bruto").value;
    var retencion = document.getElementById("retencion").value;
    var liquido = document.getElementById("liquido").value;
    var xmlHttp;
    xmlHttp=new XMLHttpRequest();
    xmlHttp.onreadystatechange=function(){
        if(xmlHttp.readyState==4){
            var ale=xmlHttp.responseText;
            location="inversionoperacion_listado.py?id_inversiones="+id_inversiones;
        }
    }
    var url="ajax/dividendo_insertar.py?fecha="+fecha+"&valorxaccion="+valorxaccion+"&bruto="+bruto+"&retencion="+retencion+"&liquido="+liquido+"&id_inversiones="+id_inversiones;
    xmlHttp.open("GET",url,true);
    xmlHttp.send(null);
}

]]>
</script>

<vbox flex="1">
    <label id="titulo" flex="0" value="Nuevo dividendo" />
    <label value="" />
    <hbox flex="1">
    <grid align="center">
        <rows>
        <row><label value="Introduce la fecha"/><hbox><datepicker id="fecha" type="grid"  firstdayofweek="1"/></hbox></row>
        <row><label value="Valor de la acción"/><hbox><textbox id="valorxaccion" value="0"/></hbox></row>
        <row><label value="Importe bruto" /><hbox><textbox id="bruto" value="0"/></hbox></row>        
        <row><label value="Retención" /><hbox><textbox id="retencion" value="0"/></hbox></row>
        <row><label value="Valor líquido" /><hbox><textbox id="liquido" value="0"/></hbox></row>
        <row><label value="" /><hbox><button id="cmd" label="Aceptar" onclick="insert();"/></hbox></row>
        </rows>
    </grid>
    </hbox>
</vbox>
</window>