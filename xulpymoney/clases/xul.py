# -*- coding: UTF-8  -*-
from formato import *
import sys
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
    s=s +  '            <menuitem label="'+_('Listado')+'"  class="menuitem-iconic"  image="images/toggle_log.png" onclick="location=\'eb_listado.psp\';" />\n'
    s=s +  '         </menupopup>\n'
    s=s +  '      </menu>\n'
    s=s +  '      <menu label="'+_('Cuentas')+'">\n'
    s=s +  '         <menupopup>\n'
    s=s +  '            <menuitem label="'+_('Listado')+'" onclick="location=\'cuenta_listado.psp\';"   class="menuitem-iconic"  image="images/toggle_log.png"/>\n'
    s=s +  '            <menuitem label="'+_('Listado de tarjetas')+'"  onclick="location=\'tarjeta_listado.psp\';"   class="menuitem-iconic"  image="images/visa.png"/>\n'
    s=s +  '            <menuitem label="'+_('Transferencia bancaria')+'"  onclick="location=\'cuenta_transferencia.psp\';"  class="menuitem-iconic"  image="images/hotsync.png" />\n'
    s=s +  '         </menupopup>\n'
    s=s +  '      </menu>\n'
    s=s +  '      <menu label="'+_('Inversiones')+'">\n'
    s=s +  '         <menupopup>\n'
    s=s +  '            <menuitem label="'+_('Estado')+'"  onclick="location=\'inversion_listado.psp\';"  class="menuitem-iconic"  image="images/toggle_log.png"/>\n'
    s=s +  '            <menuitem label="'+_('Compra / Venta')+'"  onclick="location=\'inversion_compraventa.psp\';"  class="menuitem-iconic"  image="images/toggle_log.png"/>\n'
    s=s +  '            <menuitem label="'+_('Histórico')+'" onclick="location=\'inversion_historico.psp\';" class="menuitem-iconic" image="images/history.png" />\n'
    s= s+ '        <menuseparator/>\n'
    s= s+ '        <menuitem label="'+_('Actualizar en Internet')+'" oncommand="location=\'inversion_actualizar_internet.psp\';"  class="menuitem-iconic"  image="images/hotsync.png" />           \n'
    s=s +  '         </menupopup>\n'
    s=s +  '      </menu>\n'
    s=s +  '      <menu label="'+_('Informes')+'">\n'
    s=s +  '         <menupopup>\n'
    s=s +  '            <menuitem label="'+_('Clasificación')+'" onclick="location=\'inversion_clasificacion.psp\';"  class="menuitem-iconic" image="images/cakes.png" />\n'
    s=s +  '      <menu label="'+_('Conceptos')+'">\n'
    s=s +  '         <menupopup>\n'
    s=s +  '            <menuitem label="'+_('Estudio mensual')+'" onclick="location=\'informe_conceptos_mensual.psp\';"  class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '            <menuitem label="'+_('Evolución histórica')+'" onclick="location=\'informe_conceptos.psp?id_conceptos=1\';"  class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '         </menupopup>\n'
    s=s +  '      </menu>\n'    
    s=s +  '            <menuitem label="'+_('Evolución TAE')+'" onclick="location=\'informe_tae.psp\';"  class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '            <menuitem label="'+_('Referencia a IBEX')+'" onclick="location=\'informe_referenciaibex.psp\';"  class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '            <menuitem label="'+_('Total')+'" onclick="location=\'informe_total.psp\';"  class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '         </menupopup>\n'
    s=s +  '    </menu>\n'    
    s=s +  '    <menu label="'+_('Mantenimiento')+'">\n'
    s=s +  '      <menupopup>\n'
    s=s +  '        <menuitem label="'+_('Datos Ibex 35')+'"  onclick="location=\'mantenimiento_ibex35.psp\';"  class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '        <menuitem label="'+_('Operaciones de inversión')+'"  onclick="location=\'mantenimiento_operinversiones.psp\';"  class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '        <menuitem label="'+_('Tablas auxiliares')+'"  onclick="location=\'mantenimiento_tablas.psp\';" />\n'
    s=s +  '      </menupopup>\n'
    s=s +  '    </menu>\n'    
    s=s +  '    <menu label="'+_('Ayuda')+'">\n'
    s=s +  '      <menupopup>\n'
    s=s +  '        <menuitem label="'+_('Acerca de')+'"  onclick="location=\'about.psp\';"  class="menuitem-iconic" image="images/history.png" />\n'    
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


def combo_ano(inicio,fin, selected,  js=True):
    s="<hbox>"
    s=s + '<label value="'+_('Selecciona un año')+'"/>\n'
    s= s + '<menulist id="cmbanos" label="'+str(fin)+'" oncommand="cmb_submit();">\n'
    s=s + '<menupopup>\n';
    i=inicio
    while (i<=fin):
        if i==selected:
            s=s +  '       <menuitem label="'+str(i)+'" selected="true"/>\n'
        else:
            s=s +  '       <menuitem label="'+str(i)+'"/>\n'
        i=i+1
    s=s +  '     </menupopup>\n'
    s=s + '</menulist>\n'
    s=s + '</hbox>\n'
    return s
