# -*- coding: UTF-8 -*-
from mod_python import util
import datetime
from core import *
from xul import *

def index(req):
    def page():
        s=s+'<?xml version="1.0" encoding="UTF-8" ?>\n'
        s=s+'<?xml-stylesheet href="xul.css" type="text/css"?>\n'
        s=s+'<?xml-stylesheet href="chrome://global/skin/" type="text/css"?>\n'
        #Se ponen encabezados porque se hace un onload

        s=s+'<window id="main" title="Xulpymoney > Entidades Bancarias > Patrimonio" xmlns="http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul" onload="total();">\n'
        s=s+menu()
        s=s+'<script>\n'
        s=s+'<![CDATA[\n'
        s=s+'function total(){\n'
        s=s+'var tc=Number(document.getElementById("totalcuentas").getAttribute("total"));\n'
        s=s+'var ti=Number(document.getElementById("totalinversiones").getAttribute("total"));\n'
        s=s+'var t=tc+ti\n'
        s=s+'document.getElementById("total").value="Saldo total en la entidad: "+ t + " €";\n'
        s=s+'}\n'
        s=s+']]>\n'
        s=s+'</script>\n'

        s=s+'<vbox  flex="6">\n'
        s=s+'<label id="titulo" flex="0.5" value="Patrimonio en la Entidad Bancaria" />\n'
        s=s+'<label id="subtitulo" flex="0" value="'+regEB['entidadbancaria']+'" />\n'

        s=s+listadocuentas
        s=s+listadoinversiones
        s=s+'<label id="total" flex="0" style="text-align: center;font-weight : bold;"    />\n'
        s=s+'</vbox>\n'
        s=s+'</window>        \n'
        return s

    form=util.FieldStorage(req)    
    con=Conection()
    cd=ConectionDirect()
    regEB=cd.con.Execute("select * from entidadesbancarias where id_entidadesbancarias="+ str(form['id_entidadesbancarias'])).GetRowAssoc(0)
    listadocuentas=Cuenta().xul_listado("select id_cuentas, cu_activa, cuenta, entidadesbancarias.entidadbancaria, numero_cuenta, cuentas_saldo(id_cuentas,'"+str(datetime.date.today())+"') as saldo from cuentas, entidadesbancarias where cuentas.id_entidadesbancarias=entidadesbancarias.id_entidadesbancarias and cu_activa='t' and entidadesbancarias.id_entidadesbancarias="+str(form['id_entidadesbancarias'])+" order by cuenta")
    listadoinversiones=Inversion().xul_listado("select id_inversiones, in_activa, inversion, entidadbancaria, inversiones_saldo(id_inversiones,'"+str(datetime.date.today())+"') as saldo, inversion_actualizacion(id_inversiones,'"+str(datetime.date.today())+"') as actualizacion, inversion_pendiente(id_inversiones,'"+str(datetime.date.today())+"')  as pendiente,  inversion_invertido(id_inversiones,'"+str(datetime.date.today())+"')  as invertido from inversiones, cuentas, entidadesbancarias where cuentas.id_entidadesbancarias=entidadesbancarias.id_entidadesbancarias and cuentas.id_cuentas=inversiones.id_cuentas and in_activa='t' and entidadesbancarias.id_entidadesbancarias="+str(form['id_entidadesbancarias'])+" order by inversion;")
    
    con.close()
    cd.close()
    req.content_type="application/vnd.mozilla.xul+xml"
    return page()

