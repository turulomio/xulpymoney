# -*- coding: UTF-8 -*-
from mod_python import util
import time
from core import *
from xul import *
from translate import _


def index(req):
    con=Conection()
    form=util.FieldStorage(req)    
    checked=""
    if form.has_key('inactivas'):
        if form['inactivas']=="on":
            checked = 'checked="true"'
            listado=Inversion().xul_listado("select id_inversiones, fechadividendo, dividendo, in_activa, inversion, entidadbancaria, inversiones_saldo(id_inversiones,'"+str(datetime.date.today())+"') as saldo, inversion_actualizacion(id_inversiones,'"+str(datetime.date.today())+"') as actualizacion, inversion_pendiente(id_inversiones,'"+str(datetime.date.today())+"')  as pendiente, inversion_invertido(id_inversiones,'"+str(datetime.date.today())+"')  as invertido from inversiones, cuentas, entidadesbancarias where cuentas.id_entidadesbancarias=entidadesbancarias.id_entidadesbancarias and cuentas.id_cuentas=inversiones.id_cuentas order by inversion;")
        else:
            listado=Inversion().xul_listado("select id_inversiones, fechadividendo, dividendo, in_activa, inversion, entidadbancaria, inversiones_saldo(id_inversiones,'"+str(datetime.date.today())+"') as saldo, inversion_actualizacion(id_inversiones,'"+str(datetime.date.today())+"') as actualizacion, inversion_pendiente(id_inversiones,'"+str(datetime.date.today())+"')  as pendiente,  inversion_invertido(id_inversiones,'"+str(datetime.date.today())+"')  as invertido from inversiones, cuentas, entidadesbancarias where cuentas.id_entidadesbancarias=entidadesbancarias.id_entidadesbancarias and cuentas.id_cuentas=inversiones.id_cuentas and in_activa='t' order by inversion;")
    else:
            listado=Inversion().xul_listado("select id_inversiones, fechadividendo, dividendo, in_activa, inversion, entidadbancaria, inversiones_saldo(id_inversiones,'"+str(datetime.date.today())+"') as saldo, inversion_actualizacion(id_inversiones,'"+str(datetime.date.today())+"') as actualizacion, inversion_pendiente(id_inversiones,'"+str(datetime.date.today())+"')  as pendiente,  inversion_invertido(id_inversiones,'"+str(datetime.date.today())+"')  as invertido from inversiones, cuentas, entidadesbancarias where cuentas.id_entidadesbancarias=entidadesbancarias.id_entidadesbancarias and cuentas.id_cuentas=inversiones.id_cuentas and in_activa='t' order by inversion;")
    
    con.close()    
    req.content_type="application/vnd.mozilla.xul+xml"
    req.write(xulheaderwindowmenu(_("Xulpymoney > Inversiones > Listado")))
    req.write('    <script>')
    req.write('    <![CDATA[')
    req.write('    function checkbox_submit(){')
    req.write('       if (document.getElementById("checkbox").checked==true) {')
    req.write('         location=\'inversion_listado.py?inactivas=on\';')
    req.write('       } else {')
    req.write('         location=\'inversion_listado.py\';')
    req.write('       } ')
    req.write('    }')
    req.write('    ]]>')
    req.write('    </script>')
    
    
    req.write('    <vbox  flex="1">')
    req.write('    <label id="titulo" flex="0" value="'+_('Estado de las inversiones')+'" />')
    req.write('    <checkbox id="checkbox" label="'+_('¿Mostrar las inversiones inactivas?')+'" '+checked+'  oncommand="checkbox_submit()" style="text-align: center;" />')
    req.write(listado)
    req.write('    </vbox>')
    req.write('    </window>')
