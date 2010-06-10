# -*- coding: UTF-8 -*-
from mod_python import util
import datetime
from core import *
from xul import *

def index(req):
    def page():
        s=xulheaderwindowmenu("Xulpymoney > Entidades Bancarias > Listado")
        s=s+'<script>'
        s=s+'<![CDATA['
        s=s+'function checkbox_submit(){'
        s=s+'    if (document.getElementById("checkbox").checked==true) {'
        s=s+'        location=\'eb_listado.py?inactivas=on\';'
        s=s+'    } else {'
        s=s+'        location=\'eb_listado.py\';'
        s=s+'    } '
        s=s+'}'
        s=s+']]>'
        s=s+'</script>'
    
        s=s+'<vbox  flex="6">'
        s=s+'<label id="titulo" flex="0.5" value="Listado de entidades bancarias" />'
        s=s+'<checkbox id="checkbox" label="¿Mostrar las entidades bancarias inactivas?" '+checked+' oncommand="checkbox_submit()" style="text-align: center;" />'
        s=s+listado
        s=s+'</vbox>'
        s=s+'</window>'
        return s

    form=util.FieldStorage(req)    
    con=Conection()
    checked=""
    if form.has_key('inactivas'):
        if form['inactivas']=="on":
            checked = 'checked="true"'
            listado = EntidadBancaria().xultree(True,datetime.date.today())
        else:
            listado = EntidadBancaria().xultree(False,datetime.date.today())
    else:
        listado = EntidadBancaria().xultree(False,datetime.date.today()) 
    con.close()
    req.content_type="application/vnd.mozilla.xul+xml"
    return page()
