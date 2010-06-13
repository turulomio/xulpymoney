# -*- coding: UTF-8 -*-
from mod_python import util
import time,  calendar
from core import *
from xul import *
from translate import _

def index(req):
    con=Conection().open()
    titulo=_("Xulpymoney > Informes > Informe TAE")
    req.content_type="application/vnd.mozilla.xul+xml"
    req.write(xulheaderwindowmenu(titulo))

    req.write('<vbox  flex="5">\n')
    req.write('<label id="titulo" value="'+titulo+'" />\n')
    req.write('<hbox>\n')
    req.write('</hbox>\n')

    req.write('<tree id="informegi" flex="1">\n')
    req.write('    <treecols>\n')
    req.write('        <treecol  label="Año" flex="1"  style="text-align: center"/>\n')
    req.write('        <treecol label="Saldo inicial" flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Ganancia" flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Gasto anual" flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="TAE" flex="1" style="text-align: right"/>\n')
    req.write('    </treecols>\n')
    req.write('    <treechildren>\n')
    
    for i in range(Total().primera_fecha_con_datos_usuario().year,  datetime.date.today().year+1):
        si=Total().saldo_total(datetime.date(i, 1, 1))
        sf=Total().saldo_total(datetime.date(i, 12, 31))
        req.write('     <treeitem>\n')
        req.write('         <treerow>\n')
        req.write('             <treecell label="'+str(i)+'"/>\n')
        req.write('             ' + treecell_euros(si))
        req.write('             ' + treecell_euros(sf-si))
        req.write('             ' + treecell_euros(float(Total().gastos_anuales(i))))
        req.write('             ' + treecell_tpc(Total().tae_anual(si,  sf)))
        req.write('         </treerow>\n')
        req.write('     </treeitem>\n')
    con.Close()

    req.write('    </treechildren>\n')
    req.write('</tree>\n')
    req.write('</vbox>\n')
    req.write('</window>\n')
