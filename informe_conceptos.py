# -*- coding: UTF-8 -*-
from mod_python import util
import sys
from xul import *
from core import *

def index(req):
    def page():
        s=xulheaderwindowmenu("Xulpymoney > Informe > Conceptos")
        s=s+'<script><![CDATA[\n'

        s=s+'function cmbconceptos_submit(){\n'
        s=s+'    var cmbconceptos=document.getElementById("cmbconceptos").value;\n'
        s=s+'    location="informe_conceptos.psp?id_conceptos="+ cmbconceptos.split(";")[0];\n'
        s=s+'}\n'

        s=s+']]></script>\n'
        s=s+'<vbox  flex="5">\n'
        s=s+'<label id="titulo" value="Informe de conceptos"/>\n'
        s=s+cmbconcepto
        s=s+lstConceptos
        s=s+'</vbox>\n'
        s=s+xulfoot()
        return s

    form=util.FieldStorage(req)    
    
    req.content_type="application/vnd.mozilla.xul+xml"
    
    con=Conection()
    cmbconcepto=Concepto().cmb('select * from conceptos where id_tiposoperaciones in (1,2) order by concepto',  int(form['id_conceptos']),  True)
    lstConceptos=Concepto().xultree_informe(form['id_conceptos'])
    con.close()
    return page()
