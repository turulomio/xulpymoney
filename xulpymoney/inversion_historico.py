# -*- coding: UTF-8 -*-
from mod_python import util
import time
from core import *
from translate import  _
from xul import *

def index(req):
    def page():
        s=xulheaderwindowmenu("Histórico de inversiones")

        s=s+'<script>\n'
        s=s+'<![CDATA[\n'
         
        s=s+'function cmb_submit(){\n'
        s=s+'    cmb=document.getElementById("cmbanos");\n'
        s=s+'    location=\'inversion_historico.py?cmbanos=\'+ cmb.getItemAtIndex(cmb.selectedIndex).label;\n'
        s=s+'}\n'


        s=s+']]>\n'
        s=s+'</script>\n'
        s=s+'<vbox  flex="5">\n'
        s=s+'<label id="titulo" value="Informe histórico de inversiones" />\n'
        s=s+combo
        s=s+listadorendimientos


        s=s+'<tabbox orient="vertical" flex="1">\n'
        s=s+'<tabs>\n'
        s=s+'<tab label="Inversiones" />\n'
        s=s+'<tab label="Dividendos" />\n'
        s=s+'</tabs>\n'
        s=s+'<tabpanels flex="1">\n'
        s=s+'<vbox>\n'
        s=s+listadoinversiones
        s=s+'</vbox>\n'
        s=s+'<vbox>\n'
        s=s+listadodividendos
        s=s+'</vbox>\n'
        s=s+'</tabpanels>\n'
        s=s+'</tabbox>\n'

        s=s+'</vbox>\n'
        s=s+'</window>\n'
        return s

    form=util.FieldStorage(req)    
    con=Conection()
    
    if form.has_key('cmbanos'):
       cmbanos=int(form['cmbanos'])
    else:
        cmbanos=datetime.date.today().year
    combo=combo_ano(Total().primera_fecha_con_datos_usuario().year, datetime.date.today().year,  cmbanos)
    listadoinversiones = Total().xultree_historico_inversiones(cmbanos, True)
    listadodividendos = Total().xultree_historico_dividendos(cmbanos)
    listadorendimientos = Total().xultree_historico_rendimientos(cmbanos)
    con.close()
    
    req.content_type="application/vnd.mozilla.xul+xml"
    return page()
