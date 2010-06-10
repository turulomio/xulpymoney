<%
from core import *
from xul import *

if form.has_key('rango'):
   rango=int(form['rango'])
else:
    util.redirect(req, 'informe_referenciaibex.py')
    
rangostr=str(rango) + " - " + str(rango+1000)
con=Conection()
sql="select tmpoperinversiones.fecha, inversiones.inversion, tmpoperinversiones.importe, floor(ibex35.cierre) as ibex35 from inversiones, tmpoperinversiones, ibex35 where tmpoperinversiones.fecha=ibex35.fecha and inversiones.id_inversiones=tmpoperinversiones.id_inversiones and ibex35.cierre>="+str(rango)+" and ibex35.cierre<"+str(rango+1000)+" order by fecha;"
tree=InversionOperacionTemporal().xultree_referenciaibex(sql)

req.content_type="application/vnd.mozilla.xul+xml"
req.write(xulheaderwindowmenu("Informe de referencia al Ibex35"))
%>

<vbox align="center">
    <label id="titulo"  value="Informe de referencia al Ibex35" />
    <label id="subtitulo"  value="Rango <%=rangostr%>" />
</vbox>
<vbox flex="1">
<%=tree%>
</vbox>
</window>