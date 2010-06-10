# -*- coding: UTF-8 -*-
from mod_python import util
import datetime
from core import *
from xul import *

def index(req):
    def page():
        s=xulheaderwindowmenu("Xulpymoney > Inversiones > Actualizar Internet")
        s=s+'<script src="js/validar.js"></script>\n'

        s=s+'<vbox  flex="1">\n'
        s=s+'<label id="titulo" flex="0" value="Actualizar valor de las inversiones en Internet" />\n'
        s=s+'<label id="subtitulo" flex="0" value="Última actualización: '+datetime.datetime.now().isoformat(' ')+'" />\n'
        s=s+listado
        s=s+'</vbox>\n'
        s=s+'</window>\n'
        return s
#    form=util.FieldStorage(req)    
    #Consultas BD
    con=Conection()
    
    listado=Inversion().xul_listado_internet("select internet, id_inversiones, inversion, entidadbancaria,  inversion_actualizacion(id_inversiones,'"+str(datetime.date.today())+"') as actualizacion, compra, inversiones_acciones(id_inversiones,'"+str(datetime.date.today())+"')  as acciones,  venta from inversiones, cuentas, entidadesbancarias where  in_activa=true and cuentas.id_entidadesbancarias=entidadesbancarias.id_entidadesbancarias and cuentas.id_cuentas=inversiones.id_cuentas order by inversion;")
    con.close()    
    req.content_type="application/vnd.mozilla.xul+xml"
    return page()
