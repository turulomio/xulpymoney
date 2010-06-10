<%
from core import *
from xul import *

con=Conection()
cd=ConectionDirect()
row=cd.con.Execute("select * from opercuentas, conceptos where opercuentas.id_conceptos=conceptos.id_conceptos and  id_opercuentas="+ form["id_opercuentas"]).GetRowAssoc(0)
cmbconcepto=Concepto().cmb('select * from conceptos where id_tiposoperaciones in (1,2) order by concepto',  row['id_conceptos'],  False)

req.content_type="application/vnd.mozilla.xul+xml"
req.write(xulheaderwindowmenu("Xulpymoney > Cuenta > Operación > Modificar"))
con.close()
cd.close()
%>
<script>
<![CDATA[
function modificar(){
    if (check_data()==false){
        return;
    }
    var xmlHttp;    
    var sp=document.getElementById("cmbconceptos").value.split(";")
    var importe=document.getElementById("importe").value;
    var id_conceptos=sp[0];
    var id_tiposoperaciones=sp[1];
    var comentario= document.getElementById("comentario").value;
    var fecha = document.getElementById("fecha").value;
    spfecha=fecha.split("-");
    var id_opercuentas=<%=form['id_opercuentas']%>;
    var id_cuentas=<%=row['id_cuentas']%>;
    var url="ajax/cuentaoperacion_modificar.py?id_opercuentas="+id_opercuentas+"&fecha="+fecha+"&id_conceptos="+id_conceptos+"&id_tiposoperaciones="+id_tiposoperaciones+"&importe="+importe+"&comentario="+comentario+"&id_cuentas="+id_cuentas;
    xmlHttp=new XMLHttpRequest();
    xmlHttp.onreadystatechange=function(){
        if(xmlHttp.readyState==4){
            var ale=xmlHttp.responseText;
            location="cuenta_informacion.py?id_cuentas="+ id_cuentas + "&year=" + spfecha[0] + "&month=" + spfecha[1];
        }
    }

    xmlHttp.open("GET",url,true);
    xmlHttp.send(null);
}

function check_data(){
    resultado=true;    
    //Comprueba si es un float
    var textbox=document.getElementById("importe")
    if (!/^[-+]?[0-9]+(\.[0-9]+)?$/.test(textbox.value)){
        textbox.setAttribute("style", "color: green; background-color: red;")
        //textbox.style.color = "#FFAA88";
        alert("El importe no es un número decimal");
        resultado=false;
    }
    //Comprueba si tiene comillas
    if (/[\'\"]/.test(document.getElementById("comentario").value)){//"'
        alert("No se puede meter ningún tipo de comilla");
        resultado=false;
    }   
    //Comprueba la logica de GI
    if (document.getElementById("cmbconceptos").value.split(";")[1]==1 && document.getElementById("importe").value>0){
        alert("El importe debe ser negativo ya que el concepto seleccionado es un gasto");
        resultado=false;
    }          
    if (document.getElementById("cmbconceptos").value.split(";")[1]==2 && document.getElementById("importe").value<0){
        alert("El importe debe ser positivo ya que el concepto seleccionado es un ingreso");
        resultado=false;
    }        
    return resultado;
}


]]>
</script>
<label id="titulo" value="Modificar una operación de cuenta" />
<vbox flex="5">
<grid pack="center">
    <columns>
        <column flex="1" />
        <column flex="1" />
    </columns>
    <rows>
        <row>
            <label id="negrita" value="Fecha"/>
            <datepicker id="fecha" type="grid"  firstdayofweek="1" value="<%=str(row['fecha'])[:-12]%>"/>
        </row>
        <row>
            <label id="negrita" value="Concepto"/>
            <%=cmbconcepto %>
        </row>
        <row>
            <label id="negrita" value="Importe"/>
            <textbox id="importe" value="<%=row['importe'] %>"/>
        </row>
        <row>
            <label id="negrita" value="Comentario"/>
            <textbox id="comentario" value="<%=row['comentario'] %>"/>
        </row>
    </rows>
</grid>
    <button label="Aceptar" oncommand="modificar();"/>

</vbox>
</window>