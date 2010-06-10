<%
from core import *
from xul import *

con=Conection()
InversionOperacionHistorica().actualizar_todas()
CuentaOperacionHeredadaInversion().actualizar_todas()
con.close()
req.content_type="application/vnd.mozilla.xul+xml"
req.write(xulheaderwindowmenu("Xulpymoney > Mantenimiento > Mantenimiento Operaciones Inversióno"))
%>
<script>
<![CDATA[
         
function update(){
    var xmlHttp;
    xmlHttp=new XMLHttpRequest();
    xmlHttp.onreadystatechange=function(){
        if(xmlHttp.readyState==4){
            var ale=xmlHttp.responseText;
             document.getElementById("resultado").value=ale;
        }
    }
    document.getElementById("resultado").value="Este proceso puede durar unos minutos. Actualizando desde Internet ...";
    document.getElementById("button").disabled=true;
    var url="ajax/mantenimiento_ibex35.py";
    xmlHttp.open("GET",url,true);
    xmlHttp.send(null);
}

]]>
</script>

<vbox align="center">
    <label id="titulo"  value="Mantenimiento operaciones de inversión" />
</vbox>
<label flex="0"  value="" />
<label flex="0"  style="text-align: center;font-weight : bold;" value="En esta pagina se ejecuta el mantenimiento de las operaciones de inversión" />
</window>