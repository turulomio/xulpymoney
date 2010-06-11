#-*- coding: UTF-8 -*-
from mod_python import util
from core import *
def index(req):
    form=util.FieldStorage(req) 
    con=Conection()
    req.write (Inversion().modificar_activa( form['id_inversiones'],  form['activa']))
    con.close()
    
