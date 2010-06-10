<%
import time
from core import *
from xul import *

#Consultas BD
con=Conection()
hoy=datetime.date.today()
checked=""
id_inversiones=0
if form.has_key('id_inversiones'):
    id_inversiones=form['id_inversiones']

cmbcuentas=Cuenta().cmb('id_cuentas','select * from cuentas where cu_activa=true order by cuenta',  0,  False)
con.close()

req.content_type="application/vnd.mozilla.xul+xml"
req.write(xulheaderwindowmenu("Xulpymoney > Tarjeta > Nueva"))

%>
<script>
<![CDATA[
         
function tarjeta_insert(){
    var xmlHttp;
    xmlHttp=new XMLHttpRequest();
    xmlHttp.onreadystatechange=function(){
        if(xmlHttp.readyState==4){
            var ale=xmlHttp.responseText;
            location="tarjeta_listado.py";
        }
    }
    var id_cuentas = document.getElementById("id_cuentas").value;
    var tarjeta = document.getElementById("tarjeta").value;
    var numero = document.getElementById("numero").value;
    var pago_diferido = document.getElementById("pago_diferido").checked;
    var saldomaximo = document.getElementById("saldomaximo").value;
    var url="ajax/tarjeta_insertar.py?id_cuentas="+id_cuentas+"&tarjeta="+tarjeta+"&numero="+numero+"&pago_diferido="+pago_diferido+"&saldomaximo="+saldomaximo 
    xmlHttp.open("GET",url,true);
    xmlHttp.send(null);
}

]]>
</script>

<vbox flex="1">
    <label id="titulo" flex="0" value="Nueva tarjeta" />
    <label value="" />
    <hbox flex="1">
    <grid align="center">
        <rows>
        <row><label value="Cuenta asociada"/><hbox><%=cmbcuentas%></hbox></row>
        <row><label value="Nombre de la tarjeta"/><hbox><textbox id="tarjeta" value="Nueva tarjeta"/></hbox></row>
        <row><label value="Número de la tarjeta" /><hbox><textbox id="numero" value="XXXXXXXXXXXXXXXXXXX"/></hbox></row>        
        <row><label value="Pago diferido" /><hbox><checkbox id="pago_diferido" /></hbox></row>
        <row><label value="Saldo máximo" /><hbox><textbox id="saldomaximo" value="0"/></hbox></row>
        <row><label value="" /><hbox><button id="cmd" label="Aceptar" onclick="tarjeta_insert();"/></hbox></row>
        </rows>
    </grid>
    </hbox>
</vbox>
</window>