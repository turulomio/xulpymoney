<% 
import sys
from xul import *
from core import *

req.content_type="application/vnd.mozilla.xul+xml"
req.write(xulheaderwindowmenu("Xulpymoney > Informe > Conceptos"))

con=Conection()
cmbconcepto=Concepto().cmb('select * from conceptos where id_tiposoperaciones in (1,2) order by concepto',  int(form['id_conceptos']),  True)
lstConceptos=Concepto().xultree_informe(form['id_conceptos'])
con.close()
%>
<script><![CDATA[

function cmbconceptos_submit(){
    var cmbconceptos=document.getElementById("cmbconceptos").value;
    location="informe_conceptos.psp?id_conceptos="+ cmbconceptos.split(";")[0];
}


]]></script>
<vbox  flex="5">
<label id="titulo" value="Informe de conceptos"/>
<%=cmbconcepto%>
<%=lstConceptos%>
</vbox>
<%
req.write(xulfoot())
%>
