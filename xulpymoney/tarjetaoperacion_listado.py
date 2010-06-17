# -*- coding: UTF-8 -*-
from core import *
from xul import *

def index(req):
    form=req.form
    #Consultas BD
    c=ConectionDirect()
    
    if form.has_key('id_tarjetas'):
        id_tarjetas=form['id_tarjetas']
    else:
        util.redirect(req, 'tarjetaslistado.py')
    
    req.content_type="application/vnd.mozilla.xul+xml"
    req.write(xulheaderwindowmenu("Listado de operaciones con tarjeta"))
    
    nombreTarjeta=c.con.Execute("select tarjeta from tarjetas where id_tarjetas="+ str(id_tarjetas)).GetRowAssoc(0)["tarjeta"]   


    req.write('<script><![CDATA[\n')
    req.write('var id_opertarjetas=0;\n')

    req.write('var suma=0;\n')
    req.write('var lista=new Array();\n')
    req.write('var puntlista=0;\n')
    req.write('function borrar(){\n')
    req.write('    var xmlHttp;        \n')
    req.write('    var id_tarjetas='+str(form['id_tarjetas'])+';\n')
    req.write('    var url=\'ajax/tarjetaoperacion_borrar.py?id_opertarjetas=\' + id_opertarjetas ;\n')
    req.write('    xmlHttp=new XMLHttpRequest();\n')
    req.write('    xmlHttp.onreadystatechange=function(){\n')
    req.write('        if(xmlHttp.readyState==4){\n')
    req.write('            var ale=xmlHttp.responseText;\n')
    req.write('            location="tarjetaoperacion_listado.py?id_tarjetas="+ id_tarjetas;\n')
    req.write('        }\n')
    req.write('    }\n')
    req.write('    xmlHttp.open("GET",url,true);\n')
    req.write('    xmlHttp.send(null);\n')
    req.write('}\n')

    req.write('function go_opertarjetas_insertar(){\n')
    req.write('    var id_tarjetas='+str(form['id_tarjetas'])+';\n')
    req.write('    location="tarjetaoperacion_insertar.py?id_tarjetas="+ id_tarjetas ;\n')
    req.write('}\n')

    req.write('function pagar(){\n')
    req.write('    var xmlHttp;        \n')
    req.write('    var id_tarjetas='+str(form['id_tarjetas'])+';\n')
    req.write('    var fechapago = document.getElementById("fechapago").value;\n')
    req.write("    var url='ajax/tarjeta_pagar.py?lista=' + lista + '&suma='+suma + '&id_tarjetas='+ id_tarjetas + '&fechapago='+ fechapago;\n")
    req.write('    xmlHttp=new XMLHttpRequest();\n')
    req.write('    xmlHttp.onreadystatechange=function(){\n')
    req.write('        if(xmlHttp.readyState==4){\n')
    req.write('            var ale=xmlHttp.responseText;\n')
    req.write('            location="tarjetaoperacion_listado.py?id_tarjetas="+ id_tarjetas;\n')
    req.write('        }\n')
    req.write('    }\n')
    req.write('    xmlHttp.open("GET",url,true);\n')
    req.write('    xmlHttp.send(null);\n')
    req.write('}\n')

    req.write('function tree_getid(){\n')
    req.write('   var tree = document.getElementById("tree");\n')
    req.write('   var selection = tree.contentView.getItemAtIndex(tree.currentIndex);\n')
    req.write('   id_opertarjetas = selection.firstChild.firstChild.getAttribute("label");\n')
    req.write('}\n')

    req.write('function show_selected()\n')
    req.write('{\n')
    req.write('suma=0;\n')
    req.write('puntlista=0;\n')
    req.write('lista=new Array();\n')
    req.write('var start = new Object();\n')
    req.write('var end = new Object();\n')
    req.write('var tree = document.getElementById("tree");\n')
    req.write('var lblsum = document.getElementById("lblsum");\n')
    req.write('var numRanges = tree.view.selection.getRangeCount();\n')
    req.write('for (var t = 0; t < numRanges; t++){\n')
    req.write('  tree.view.selection.getRangeAt(t,start,end);\n')
    req.write('  for (var v = start.value; v <= end.value; v++){\n')
    req.write('    suma= suma + parseFloat(tree.view.getCellText(v,tree.columns.getNamedColumn("importe")).split(" ")[0]); \n')
    req.write('    lista[puntlista]=parseInt(tree.view.getCellText(v,tree.columns.getNamedColumn("id")) );\n')
    req.write('    puntlista=puntlista+1;\n')
    
    req.write('  }\n')
    req.write('}\n')
    req.write('lblsum.value="El siguiente pago será de : " + suma + " €. Seleccione una fecha y pulse pagar."; \n')
    req.write('}\n')



    req.write(']]></script>\n')

    req.write('<popupset>\n')
    req.write('    <popup id="treepopup" >\n')
    req.write('        <menuitem label="Nueva operación de tarjeta" oncommand="go_opertarjetas_insertar();" class="menuitem-iconic"  image="images/item_add.png"/>\n')
    req.write('        <menuitem label="Modificar la operación de tarjeta"  oncommand=\'location="tarjetasoperacion_modificar.py?id_cuentas=" + idcuenta  + "&amp;ibm=modificar&amp;regresando=0";\'   class="menuitem-iconic"  image="images/toggle_log.png"/>\n')
    req.write('        <menuitem label="Borrar la operación de tarjeta"  oncommand=\'borrar();\'  class="menuitem-iconic" image="images/eventdelete.png"/>\n')
    req.write('        <menuseparator/>\n')
    req.write('        <menuitem label="Realizar un pago"  oncommand="location=\'cuentasinformacion.py?id_cuentas=\' + idcuenta;"/>\n')
    req.write('    </popup>\n')
    req.write('</popupset>\n')

    req.write('<vbox align="center">\n')
    req.write('   <label id="titulo"  value="Listado de operaciones con tarjeta" />\n')
    req.write('  <label id="subtitulo" flex="0" value="'+nombreTarjeta+'" />\n')
    req.write('</vbox>\n')
    req.write('<vbox flex="1">\n')
    req.write('    <tree id="tree" flex="8"  context="treepopup"  onselect="tree_getid(); show_selected();">\n')
    req.write('        <treecols>\n')
    req.write('            <treecol id="id" label="Id" flex="1" style="text-align: left" hidden="true" />\n')
    req.write('            <treecol label="Fecha" flex="1" style="text-align: left"/>\n')
    req.write('            <treecol label="Concepto" flex="2" style="text-align: left"/>\n')
    req.write('            <treecol id="importe" label="Importe" flex="1" style="text-align: right"/>\n')
    req.write('            <treecol label="Comentario" flex="3" style="text-align: left"/>\n')
    req.write('        </treecols>\n')
    req.write('        <treechildren>\n')

    sumsaldos=0
    sql="SELECT opertarjetas.id_opertarjetas, opertarjetas.fecha, conceptos.concepto, opertarjetas.importe, comentario from opertarjetas, conceptos, tarjetas where tarjetas.id_tarjetas=opertarjetas.id_tarjetas and opertarjetas.id_conceptos=conceptos.id_conceptos and opertarjetas.pagado=false and opertarjetas.id_tarjetas="+str(id_tarjetas)+" order by fecha;"
    curs=c.con.Execute(sql); 
    s=''
    while not curs.EOF:
        row = curs.GetRowAssoc(0)   
        s=s+   '            <treeitem>\n'
        s=s+   '                <treerow>\n'
        s=s+   '                    <treecell label="'+ str(row["id_opertarjetas"])+ '" />\n'
        s=s+   '                    <treecell label="'+ str(row["fecha"])[:-12]+ '" />\n'
        s=s+   '                    <treecell label="'+ utf82xul(str(row["concepto"]))+ '" />\n'
        s=s+   '                    ' +    treecell_euros(row['importe']);
        s=s+   '                    <treecell label="'+ utf82xul(str(row["comentario"]))+ '" />\n'
        s=s+   '                </treerow>\n'
        s=s+   '            </treeitem>\n'
        curs.MoveNext()     
    curs.Close()
    req.write(s)
    c.close()

    req.write('        </treechildren>\n')
    req.write('    </tree>\n')
    req.write('    <hbox>\n')
    req.write('        <label flex="1"  id="lblsum" style="text-align: center;font-weight : bold;" value="Para hacer un pago de tarjeta selecciones las operaciones a pagar, ponga una fecha y pulse pagar" />        \n')
    req.write('        <datepicker id="fechapago" type="grid"  firstdayofweek="1"/>\n')
    req.write('        <button label="Pagar" oncommand="pagar();"/>\n')
    req.write('    </hbox>\n')
    req.write('</vbox>\n')
    req.write('</window>\n')
    
