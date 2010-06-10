# -*- coding: UTF-8 -*-
from mod_python import util
import time
from core import *
from xul import *


def index(req):
    def page():
        req.content_type="application/vnd.mozilla.xul+xml"
        s=xulheaderwindowmenu("Xulpymoney > Inversiones > Compra / Venta")
        s=s+'<script>\n'
        s=s+'<![CDATA[\n'

        s=s+'var id_inversiones=10;\n'

        s=s+'function tree_getid()\n'
        s=s+'{\n'
        s=s+'  var tree = document.getElementById("tree");\n'
        s=s+'  var selection = tree.contentView.getItemAtIndex(tree.currentIndex);\n'
        s=s+'  id_inversiones = selection.firstChild.firstChild.getAttribute("label");\n'
        s=s+'}\n'

        s=s+']]>\n'
        s=s+'</script>\n'



        s=s+'<vbox  flex="1">\n'
        s=s+'<label id="titulo" flex="0" value="Compra / Venta de inversiones" />\n'
        s=s+listado
        s=s+'</vbox>\n'
        s=s+'</window>\n'
        return s
        
    form=util.FieldStorage(req)    
    
    con=Conection()
    listado=Inversion().xultree_compraventa()
    con.close()
    return page()
