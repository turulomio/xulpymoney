<%
import time
from core import *
from xul import *

req.content_type="application/vnd.mozilla.xul+xml"
req.write(xulheaderwindowmenu("Xulpymoney > Tarjetas > Modificar"))

cd=ConectionDirect()
con=Conection()
row=cd.con.Execute("select * from tarjetas where id_tarjetas="+ form["id_tarjetas"]).GetRowAssoc(0)
cmbcuentas=Cuenta().cmb('id_cuentas','select * from cuentas where cu_activa=true order by cuenta',  row['id_cuentas'],  False)
cd.close()
con.close()
checked=""
if row['pago_diferido']==True:
	checked=' checked="true" '

%>

<script>
<![CDATA[        
function tarjeta_modificar(){
    var xmlHttp;
    xmlHttp=new XMLHttpRequest();
    xmlHttp.onreadystatechange=function(){
        if(xmlHttp.readyState==4){
            var ale=xmlHttp.responseText;
            location="tarjeta_listado.py";
        }
    }
    var id_tarjetas = <%=form['id_tarjetas']%>;
    var tarjeta = document.getElementById("tarjeta").value;
    var id_cuentas = document.getElementById("id_cuentas").value;
    var numero = document.getElementById("numero").value;
    var pago_diferido = document.getElementById("pago_diferido").checked;
    var saldomaximo = document.getElementById("saldomaximo").value;
    var url="ajax/tarjeta_modificar.py?id_tarjetas="+id_tarjetas+"&tarjeta="+tarjeta+"&id_cuentas="+id_cuentas+"&numero="+numero+"&pago_diferido="+pago_diferido+"&saldomaximo="+saldomaximo;
    xmlHttp.open("GET",url,true);
    xmlHttp.send(null);
}
]]>
</script>

<vbox flex="1">
    <label id="titulo" flex="0" value="Modificar tarjeta" />
    <label value="" />
    <hbox flex="1">
    <grid align="center">
        <rows>
        <row><label value="Nombre de la tarjeta"/><hbox><textbox id="tarjeta" value="<%=row["tarjeta"]%>"/></hbox></row>
        <row><label value="Cuenta asociada"/><hbox><%=cmbcuentas%></hbox></row>
        <row><label value="Número de tarjeta" /><hbox><textbox id="numero" value="<%=row["numero"]%>"/></hbox></row>        
        <row><label value="Pago diferido" /><hbox><checkbox id="pago_diferido" <%=checked%>/></hbox></row>
        <row><label value="Saldo máximo" /><hbox><textbox id="saldomaximo" value="<%=row["saldomaximo"]%>"/></hbox></row>
        <row><label value=""/><hbox><button id="cmd" label="Aceptar" onclick="tarjeta_modificar();"/></hbox></row>
        </rows>
    </grid>
    </hbox>
</vbox>
</window>