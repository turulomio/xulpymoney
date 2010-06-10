<%
import time
from core import *
from xul import *

#Consultas BD
con=Conection()
cmbTO=TipoOperacion().cmb('select * from tiposoperaciones order by tipooperacion',  1,  False)
con.close()

req.content_type="application/vnd.mozilla.xul+xml"
req.write(xulheaderwindowmenu("Xulpymoney > Concepto > Nueva"))

%>
<script>
<![CDATA[
         
function concepto_insert(){
    var xmlHttp;
    xmlHttp=new XMLHttpRequest();
    xmlHttp.onreadystatechange=function(){
        if(xmlHttp.readyState==4){
            var ale=xmlHttp.responseText;
            location="mantenimiento_tablas.psp";
        }
    }
    var id_tiposoperaciones = document.getElementById("cmbtiposoperaciones").value;
    var concepto = document.getElementById("concepto").value;
    var url="ajax/concepto_insertar.psp?id_tiposoperaciones="+id_tiposoperaciones+"&concepto="+concepto; 
    xmlHttp.open("GET",url,true);
    xmlHttp.send(null);
}

]]>
</script>

<vbox flex="1">
    <label id="titulo" flex="0" value="Nuevo concepto" />
    <label value="" />
    <hbox flex="1">
    <grid align="center">
        <rows>
        <row><label value="Concepto"/><hbox><textbox id="concepto" value="Nuevo concepto"/></hbox></row>
        <row><label value="Tipo de operación"/><hbox><%=cmbTO%></hbox></row>
        <row><label value="" /><hbox><button id="cmd" label="Aceptar" onclick="concepto_insert();"/></hbox></row>
        </rows>
    </grid>
    </hbox>
</vbox>
</window>
