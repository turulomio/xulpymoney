<% 
import sys
from xul import *
from core import *

req.content_type="application/vnd.mozilla.xul+xml"
req.write(xulheaderwindowmenu("Xulpymoney > Mantenimiento > Tablas auxiliares"))

con=Conection()
lstConceptos=Concepto().xultree("select * from conceptos, tiposoperaciones where conceptos.id_tiposoperaciones=tiposoperaciones.id_tiposoperaciones order by concepto" )
con.close()
%>

<vbox  flex="5">
<label id="titulo" value="Tablas auxiliares"/>
<hbox flex="4">
<tabbox orient="vertical" flex="1">
<tabs>
<tab label="Conceptos" />
</tabs>
<tabpanels flex="1">
<vbox>
<%=lstConceptos%>
</vbox>
</tabpanels>
</tabbox>

</hbox>

</vbox>
<%
req.write(xulfoot())
%>
