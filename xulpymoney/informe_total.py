# -*- coding: UTF-8 -*-
from mod_python import util
import time,  calendar
from core import *
from xul import *

def index(req):

    form=util.FieldStorage(req)    

    con=Conection()
    hoy=datetime.date.today()
    
    req.content_type="application/vnd.mozilla.xul+xml"
    req.write(xulheaderwindowmenu("Xulpymoney > Informes > Informe total"))
    
    if form.has_key('cmbanos')==False:
        cmbanos=datetime.date.today().year
    else:
        cmbanos=int(form['cmbanos'])
    
    combo=combo_ano(Total().primera_fecha_con_datos_usuario().year, datetime.date.today().year,  cmbanos)
    
    #Todos estos arrays tienen de indices 0..11 los 12 meses y el 12 la suma
    gastos=[0]*13
    ingresos=[0]*13
    gi=[0]*13
    consolidado=[0]*13
    dividendos=[0]*13
    for i in range(12):
        gastos[i]=Total().saldo_por_tipo_operacion(cmbanos,i+1,1)+Total().saldo_por_tipo_operacion (cmbanos,i+1, 7)#Gastos + Facturación de tarjeta
        dividendos[i]=Dividendo().obtenido_mensual(cmbanos, i+1)
        ingresos[i]=Total().saldo_por_tipo_operacion(cmbanos,i+1,2)-dividendos[i] #Se quitan los dividendos que luego se suman
        consolidado[i]=InversionOperacionHistorica().consolidado_total_mensual(cmbanos,i+1)
        gi[i]=ingresos[i]+dividendos[i]+consolidado[i]+gastos[i]
    
        gastos[12]=gastos[12]+gastos[i];
        dividendos[12]=dividendos[12]+dividendos[i]
        ingresos[12]=ingresos[12]+ingresos[i]
        consolidado[12]=consolidado[12]+consolidado[i];
        gi[12]=gi[12]+gi[i]
    
    mesactual=datetime.date.today().month
    cuentas=[]
    inversiones=[]
    total=[]
    diferencia=[]
    
    fechafinano=str(int(cmbanos-1))+"-12-31"
    saldofinano=Total().saldo_total(fechafinano)
    if datetime.date.today().year==cmbanos:    
        nuevohoy=hoy
        saldohoy=Total().saldo_total(nuevohoy)
    
    else:
        nuevohoy=datetime.date(cmbanos,  12,  31)
        saldohoy=Total().saldo_total(nuevohoy)
    try:
        tae=100*(saldohoy-saldofinano)/saldofinano
    except ZeroDivisionError:
        tae=0
        
    for i in range(12):
        if cmbanos==datetime.date.today().year and mesactual<=i:
            cuentas.append(0)
            inversiones.append(0)
            total.append(0)    
            diferencia.append(0)
        else:
            fecha=datetime.date (cmbanos, i+1, calendar.monthrange(cmbanos, i+1)[1])#Último día de mes.
            cuentas.append(Total().saldo_todas_cuentas(fecha))
            inversiones.append(Total().saldo_todas_inversiones(fecha))
            total.append(inversiones[i]+cuentas[i])
            if i==0:
                diferencia.append(total[i]-saldofinano)
            else:
                diferencia.append(total[i]-total[i-1])
    s=       '<label flex="0"  style="text-align: center;font-weight : bold;" value="Saldo a finales del año '+str(cmbanos-1)+': '+ euros(saldofinano)+'." />\n'       
    s= s +       '<label flex="0"  style="text-align: center;font-weight : bold;" value="Saldo a '+str(nuevohoy)+': '+ euros(saldohoy)+'." />\n'        
    s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="Beneficio en el año '+str(cmbanos)+': '+ euros(saldohoy-saldofinano)+'." />\n'
    s= s + '<label flex="0"  style="text-align: center;font-weight : bold;" value="TAE en el año '+str(cmbanos)+': '+ tpc(tae)+'." />\n'
    con.close() 
    
    req.write('    <script>\n')
    req.write('    <![CDATA[\n')
             
    req.write('    function cmb_submit(){\n')
    req.write('        cmb=document.getElementById("cmbanos");\n')
    req.write('        location=\'informe_total.py?cmbanos=\'+ cmb.getItemAtIndex(cmb.selectedIndex).label;\n')
    req.write('    }\n')
    
    req.write('    ]]>\n')
    req.write('    </script>\n')
    req.write('    <vbox  flex="5">\n')
    req.write('    <label id="titulo" value="Informe de Gastos e Ingresos" />\n')
    req.write(combo)
    req.write('    <tree id="informegi" flex="1">\n')
    req.write('      <treecols>\n')
    req.write('        <treecol id="concepto" label="Concepto " flex="2"  style="text-align: left"/>\n')
    req.write('        <treecol label="Enero     " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Febrero   " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Marzo     " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Abril     " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Mayo      " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Junio     " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Julio     " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Agosto    " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Septiembre" flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Octubre   " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Noviembre " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Diciembre " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Total     " flex="1" style="text-align: right"/>\n')
    req.write('      </treecols>\n')
    req.write('      <treechildren>\n')
    
    req.write('        <treeitem>\n')
    req.write('          <treerow>\n')
    req.write('             <treecell label="Ingresos" />\n')
    for i in range(13):
        req.write( treecell_euros(ingresos[i]))
    print

    req.write('          </treerow>\n')
    req.write('        </treeitem>    \n')
    
    
    req.write('        <treeitem>\n')
    req.write('          <treerow>\n')
    req.write('             <treecell label="Consolidado" />\n')
    
    for i in range(13):
        req.write( treecell_euros(consolidado[i]))
    
    
    req.write('          </treerow>\n')
    req.write('        </treeitem>    \n')
    
    req.write('        <treeitem>\n')
    req.write('          <treerow>\n')
    req.write('             <treecell label="Dividendos" />\n')
    
    for i in range(13):
        req.write( treecell_euros(dividendos[i]))
    
    req.write('          </treerow>\n')
    req.write('        </treeitem>    \n')
    
    
    req.write('        <treeitem>\n')
    req.write('          <treerow>\n')
    req.write('             <treecell label="Gastos" />\n')
    
    for  i in range(13):
        req.write( treecell_euros(gastos[i]))
    
    
    req.write('          </treerow>\n')
    req.write('        </treeitem>    \n')
    
        
    req.write('        <treeitem>\n')
    req.write('          <treerow>\n')
    req.write('          </treerow>\n')
    req.write('        </treeitem>   \n')
    
    req.write('        <treeitem>\n')
    req.write('          <treerow>\n')
    req.write('             <treecell label="I + D + C - G" />\n')
    
    for i in range(13):
        req.write( treecell_euros(gi[i]))
    
    req.write('          </treerow>\n')
    req.write('        </treeitem>    \n')
     
    req.write('      </treechildren>\n')
    req.write('    </tree>\n')
    
    
    req.write('    </vbox>\n')
    req.write('    <vbox  flex="5">\n')
    req.write('    <label id="titulo" value="Posición total" />\n')
    req.write('    <hbox>\n')
    req.write('    </hbox>\n')
    
    req.write('    <tree id="informegi" flex="1">\n')
    req.write('      <treecols>\n')
    req.write('        <treecol id="concepto" label="Concepto " flex="1"  style="text-align: left"/>\n')
    req.write('        <treecol label="Enero     " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Febrero   " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Marzo     " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Abril     " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Mayo      " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Junio     " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Julio     " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Agosto    " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Septiembre" flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Octubre   " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Noviembre " flex="1" style="text-align: right"/>\n')
    req.write('        <treecol label="Diciembre " flex="1" style="text-align: right"/>\n')
    req.write('      </treecols>\n')
    req.write('      <treechildren>\n')
    req.write('        <treeitem>\n')
    req.write('          <treerow>\n')
    req.write('             <treecell label="Cuentas" />\n')

    for  i in range(12):
        req.write( treecell_euros(cuentas[i]))

    req.write('          </treerow>\n')
    req.write('        </treeitem>    \n')
    req.write('        <treeitem>\n')
    req.write('          <treerow>\n')
    req.write('             <treecell label="Inversiones" />\n')
    for i in range (12):
        req.write( treecell_euros(inversiones[i]))
    
    req.write('          </treerow>\n')
    req.write('        </treeitem>    \n')
    req.write('        <treeitem>\n')
    req.write('          <treerow>\n')
    req.write('             <treecell label="Total" />\n')
    
    for i in range(12):
        req.write( treecell_euros(total[i]))
    
    req.write('    </treerow>\n')
    req.write('        </treeitem>    \n')
    req.write('        <treeitem>\n')
    req.write('          <treerow>\n')
    req.write('             <treecell label="Diferencia mensual" />\n')
    
    for i in range(12):
        req.write( treecell_euros(diferencia[i]))
    
    req.write('          </treerow>\n')
    req.write('        </treeitem>    \n')
    req.write('      </treechildren>\n')
    req.write('    </tree>\n')
    req.write(s)
    req.write('    <button label="Pulsa para ver un gráfico de evolución de saldos" oncommand=\'location="informe_total_grafico.py";\'   />\n')
    req.write('    </vbox>\n')
    req.write('    </window>\n')
    
