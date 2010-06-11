# -*- coding: UTF-8 -*-
from mod_python import util
from core import *
from xul import *

def index(req):
    def page():
        s=xulheaderwindowmenu("Tarjetas > Listado")
        s=s+'<script>\n'
        s=s+'<![CDATA[\n'
        s=s+'function checkbox_submit(){\n'
        s=s+'   if (document.getElementById("checkbox").checked==true) {\n'
        s=s+'     location=\'tarjeta_listado.py?inactivas=on\';\n'
        s=s+'   } else {\n'
        s=s+'     location=\'tarjeta_listado.py\';\n'
        s=s+'   } \n'
        s=s+'}\n'
        s=s+']]>\n'
        s=s+'</script>\n'

        s=s+'<vbox  flex="6">\n'
        s=s+'<label id="titulo" flex="0.5" value="Listado de tarjetas de crédito" />\n'
        s=s+'<checkbox id="checkbox" label="¿Mostrar las tarjetas inactivas?" '+checked+' oncommand="checkbox_submit()" style="text-align: center;" />\n'
        s=s+listado
        s=s+'</vbox>\n'
        s=s+'</window>        \n'
        return s

    form=util.FieldStorage(req)    
    con=Conection()
    checked=""
    if form.has_key('inactivas'):
        if form['inactivas']=="on":
            checked = 'checked="true"'
            listado=Tarjeta().xul_listado(True,datetime.date.today())
        else:
            listado=Tarjeta().xul_listado(False,datetime.date.today())
    else:
        listado=Tarjeta().xul_listado(False,datetime.date.today())
    con.close()
    
    req.content_type="application/vnd.mozilla.xul+xml"
    return page()
