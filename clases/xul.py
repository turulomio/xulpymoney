# -*- coding: UTF-8  -*-
from formato import *
import sys,  datetime
sys.path.append("/etc/xulpymoney/")
import config
from translate import  _

def xulheader():
    s=       '<?xml version="1.0" encoding="UTF-8" ?>\n'
    s=s +  '<?xml-stylesheet href="xul.css" type="text/css"?>\n'
    s=s +  '<?xml-stylesheet href="chrome://global/skin/" type="text/css"?>\n'
    return s


def xulheaderwindowmenu(title):
    s=xulheader() + xulventanaymenu(title)
    return str(s)

def xulventanaymenu(title):
    s='<window id="main" title="'+ title +'"       xmlns="http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul"  >\n'
    s= s + menu();
    return s

def xulfoot():
    s=""    
#    s=s + '<statusbar id="ch3-bar" persist="collapsed">\n'
#    s=s + '<statusbarpanel class="statusbarpanel-iconic" id="book-icon"/>\n'
#    s=s + '<statusbarpanel id="status-text" label="Thanks for reading chapter 3" flex="1" crop="right"/>\n'
#    s=s + '<statusbarpanel class="statusbarpanel-iconic" id="book-icon-2"/>\n'
#    s=s + '</statusbar>\n'
    s=s +  '</window>\n'
    return s


def menu():
    s=       '<toolbox>\n'
    s=s +  '   <menubar>\n'
    s=s +  '      <menu label="'+_('Entidades Bancarias')+'">\n'
    s=s +  '         <menupopup>\n'
    s=s +  '            <menuitem label="'+_('Listado')+'"  class="menuitem-iconic"  image="images/toggle_log.png" onclick="location=\'eb_listado.py\';" />\n'
    s=s +  '         </menupopup>\n'
    s=s +  '      </menu>\n'
    s=s +  '      <menu label="'+_('Cuentas')+'">\n'
    s=s +  '         <menupopup>\n'
    s=s +  '            <menuitem label="'+_('Listado')+'" onclick="location=\'cuenta_listado.py\';"   class="menuitem-iconic"  image="images/toggle_log.png"/>\n'
    s=s +  '            <menuitem label="'+_('Listado de tarjetas')+'"  onclick="location=\'tarjeta_listado.py\';"   class="menuitem-iconic"  image="images/visa.png"/>\n'
    s=s +  '            <menuitem label="'+_('Transferencia bancaria')+'"  onclick="location=\'cuenta_transferencia.py\';"  class="menuitem-iconic"  image="images/hotsync.png" />\n'
    s=s +  '         </menupopup>\n'
    s=s +  '      </menu>\n'
    s=s +  '      <menu label="'+_('Inversiones')+'">\n'
    s=s +  '         <menupopup>\n'
    s=s +  '            <menuitem label="'+_('Estado')+'"  onclick="location=\'inversion_listado.py\';"  class="menuitem-iconic"  image="images/toggle_log.png"/>\n'
    s=s +  '            <menuitem label="'+_('Compra / Venta')+'"  onclick="location=\'inversion_compraventa.py\';"  class="menuitem-iconic"  image="images/toggle_log.png"/>\n'
    s=s +  '            <menuitem label="'+_(u'Histórico')+'" onclick="location=\'inversion_historico.py\';" class="menuitem-iconic" image="images/history.png" />\n'
    s= s+ '        <menuseparator/>\n'
    s= s+ '        <menuitem label="'+_('Actualizar en Internet')+'" oncommand="location=\'inversion_actualizar_internet.py\';"  class="menuitem-iconic"  image="images/hotsync.png" />           \n'
    s=s +  '         </menupopup>\n'
    s=s +  '      </menu>\n'
    s=s +  '      <menu label="'+_('Informes')+'">\n'
    s=s +  '         <menupopup>\n'
    s=s +  '            <menuitem label="'+_(u'Clasificación')+'" onclick="location=\'inversion_clasificacion.py\';"  class="menuitem-iconic" image="images/cakes.png" />\n'
    s=s +  '      <menu label="'+_('Conceptos')+'">\n'
    s=s +  '         <menupopup>\n'
    s=s +  '            <menuitem label="'+_('Estudio mensual')+'" onclick="location=\'informe_conceptos_mensual.py\';"  class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '            <menuitem label="'+_(u'Evolución histórica')+'" onclick="location=\'informe_conceptos.py?id_conceptos=1\';"  class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '         </menupopup>\n'
    s=s +  '      </menu>\n'    
    s=s +  '            <menuitem label="'+_(u'Dividendos')+'" onclick="location=\'informe_dividendos.py\';"  class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '            <menuitem label="'+_(u'Evolución TAE')+'" onclick="location=\'informe_tae.py\';"  class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '            <menuitem label="'+_('Referencia a IBEX')+'" onclick="location=\'informe_referenciaibex.py?cmbanos='+str(datetime.date.today().year-4)+'\';"  class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '            <menuitem label="'+_('Total')+'" onclick="location=\'informe_total.py\';"  class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '         </menupopup>\n'
    s=s +  '    </menu>\n'    
    s=s +  '    <menu label="'+_('Mantenimiento')+'">\n'
    s=s +  '      <menupopup>\n'
    s=s +  '        <menuitem label="'+_('Datos Ibex 35')+'"  onclick="location=\'mantenimiento_ibex35.py\';"  class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '        <menuitem label="'+_(u'Operaciones de inversión')+'"  onclick="location=\'mantenimiento_operinversiones.py\';"  class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '        <menuitem label="'+_('Tablas auxiliares')+'"  onclick="location=\'mantenimiento_tablas.py\';" />\n'
    s=s +  '      </menupopup>\n'
    s=s +  '    </menu>\n'    
    s=s +  '    <menu label="'+_('Ayuda')+'">\n'
    s=s +  '      <menupopup>\n'
    s=s +  '        <menuitem label="'+_('Acerca de')+'"  onclick="location=\'about.py\';"  class="menuitem-iconic" image="images/history.png" />\n'    
    s=s +  '        <menuitem label="'+_('Manual de usuario')+'"  onclick="location=\'xulpymoney-'+config.language+'.odt\';"  class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '      </menupopup>\n'
    s=s +  '    </menu>\n'
    s=s +  '  </menubar>\n'
    s=s +  '</toolbox>\n'
    return s


def treecell_euros(importe,  numdec=2):
    if importe>=0:
        s='<treecell label="'+euros(importe, numdec)+'" />\n';
    else:
        s='<treecell properties="negative" label="'+euros(importe, numdec)+'" />\n';
    return s

def treecell(content, property=None):
    if property!=None:
        property=' properties="'+property+'" '
    return '<treecell'+properties+'label="'+str(content)+'" />\n';
    
def treecell_tpc(importe):
    if importe>=0 or round(importe, 1)==-100:
        s='<treecell label="'+tpc(importe)+'" />\n';
    else:
        s='<treecell properties="negative" label="'+tpc(importe)+'" />\n';
    return s
    
def treecell_euros_alerta_compra(importeactual, importealerta, tpcalerta):
    """
        Función que pone una celda en alerta dependiendo si varia un tanto por ciento del importe alerta para comprar
        Es decir si va desde menor del importealerta hasta un tpc del importe alerta
    """
    if importeactual <= importealerta*(1+tpcalerta):
        s='<treecell properties="alert" label="'+euros(importealerta, 3)+'" />\n';
    else:
        s='<treecell label="'+euros(importealerta,  3)+'" />\n';        
    return s
    
def treecell_euros_alerta_venta(importeactual, importealerta, tpcalerta):
    """
        Función que pone una celda en alerta dependiendo si varia un tanto por ciento del importe alerta para comprar
        Es decir si va desde menor del importealerta hasta un tpc del importe alerta
    """
    if importeactual >= importealerta*(1-tpcalerta):
        s='<treecell properties="alert" label="'+euros(importealerta,  3)+'" />\n';
    else:
        s='<treecell label="'+euros(importealerta,  3)+'" />\n';        
    return s


def combo_ano(name, inicio,fin, selected,  js=True):
    """Si js=true, el combo hace un oncommand a la funcion name_submit()"""
    s="<hbox align='center'>\n"
    s= s + '    <label value="'+_('Selecciona un año')+'"/>\n'
    s= s + '    <menulist id="'+name+'" oncommand="'+name+'_submit();">\n'
    s= s + '        <menupopup>\n';
    i=inicio
    while (i<=fin):
        if i==selected:
            s=s +  '            <menuitem label="'+str(i)+'" selected="true"/>\n'
        else:
            s=s +  '            <menuitem label="'+str(i)+'"/>\n'
        i=i+1
    s=s +  '        </menupopup>\n'
    s=s + '    </menulist>\n'
    s=s + '</hbox>\n'
    return s
