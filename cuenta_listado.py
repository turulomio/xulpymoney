# -*- coding: UTF-8 -*-
from mod_python import util
from core import *
from xul import *


def index(req):

    def page():
        req.content_type="application/vnd.mozilla.xul+xml"
        s=xulheaderwindowmenu("Cuentas > Listado")

        s=s+'<script>\n'
        s=s+'<![CDATA[\n'

        s=s+'var id cuenta=0;\n'

        s=s+'function checkbox_submit(){\n'
        s=s+'   if (document.getElementById("checkbox").checked==true) {\n'
        s=s+'     location=\'cuenta_listado.py?inactivas=on\';\n'
        s=s+'   } else {\n'
        s=s+'     location=\'cuenta_listado.py\';\n'
        s=s+'   }   \n'
        s=s+'}  \n'

        s=s+']]>\n'
        s=s+'</script>\n'


        s=s+'<vbox  flex="6">\n'
        s=s+'<label id="titulo" flex="0.5" value="Listado de cuentas bancarias" />\n'
        s=s+'<checkbox id="checkbox" label="¿Mostrar todas las cuentas?" '+checked+' oncommand="checkbox_submit()" style="text-align: center;" />\n'
        s=s+listado
        s=s+'</vbox>\n'
        s=s+'</window>\n'
        return s
        
    form=util.FieldStorage(req)  
    #Consultas BD
    con=Conection()
    
    # end
    checked=""
    if form.has_key('inactivas'):
        if form['inactivas']=="on":
            checked = 'checked="true"'
            listado=Cuenta().xul_listado("select id_cuentas, cu_activa, cuenta, entidadesbancarias.entidadbancaria, numero_cuenta, cuentas_saldo(id_cuentas,'"+str(datetime.date.today())+"') as saldo from cuentas, entidadesbancarias where cuentas.id_entidadesbancarias=entidadesbancarias.id_entidadesbancarias order by cuenta")
        else:
            listado=Cuenta().xul_listado("select id_cuentas, cu_activa, cuenta, entidadesbancarias.entidadbancaria, numero_cuenta, cuentas_saldo(id_cuentas,'"+str(datetime.date.today())+"') as saldo from cuentas, entidadesbancarias where cuentas.id_entidadesbancarias=entidadesbancarias.id_entidadesbancarias and cu_activa='t' order by cuenta")
    else:
        listado=Cuenta().xul_listado("select id_cuentas, cu_activa, cuenta, entidadesbancarias.entidadbancaria, numero_cuenta, cuentas_saldo(id_cuentas,'"+str(datetime.date.today())+"') as saldo from cuentas, entidadesbancarias where cuentas.id_entidadesbancarias=entidadesbancarias.id_entidadesbancarias and cu_activa='t' order by cuenta")
    con.close()    
    return page()        
