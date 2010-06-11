#-*- coding: UTF-8 -*-
from mod_python import util
from core import *
def index(req):
    form=util.FieldStorage(req)    
    cd=ConectionDirect()
    con=Conection()
    row=cd.con.Execute("select * from tarjetas where id_tarjetas="+form['id_tarjetas']).GetRowAssoc(0)
    comentario="Tarjeta " + row['tarjeta'] + ". Pagos: "+ str(form['lista']) 
    
    CuentaOperacion().insertar(form['fechapago'], 40, 7, form['suma'], comentario, row['id_cuentas']);
    id_opercuentas=CuentaOperacion().id_opercuentas_insertado_en_session()#Se hace asi porque cd no es con
    
    #Modifica el registro y lo pone como pagado y la fecha de pago y añade la opercuenta
    for i in form['lista'].split(","):
        TarjetaOperacion().modificar_fechapago (i,form['fechapago'],id_opercuentas)
    con.close()
    cd.close()
