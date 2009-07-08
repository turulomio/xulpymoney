# -*- coding: UTF-8  -*-
from fecha import *
from formato import *

def xulheader():
    s=       '<?xml version="1.0" encoding="UTF-8" ?>\n'
    s=s +  '<?xml-stylesheet href="xul.css" type="text/css"?>\n'
    return s


def xulheaderwindowmenu(title):
    s=xulheader() + xulventanaymenu(title)
    return str(s)

def xulventanaymenu(title):
    s='<window id="main" title="'+ title +'"       xmlns="http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul">\n'
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
    s=s +  '      <menu label="Bancos">\n'
    s=s +  '         <menupopup>\n'
    s=s +  '            <menuitem label="Listado"  class="menuitem-iconic"  image="images/toggle_log.png" onclick="location=\'bancoslistado.psp\';" />\n'
    s=s +  '         </menupopup>\n'
    s=s +  '      </menu>\n'
    s=s +  '      <menu label="Cuentas">\n'
    s=s +  '         <menupopup>\n'
    s=s +  '            <menuitem label="Listado" onclick="location=\'cuentaslistado.psp\';"   class="menuitem-iconic"  image="images/toggle_log.png"/>\n'
    s=s +  '            <menuitem label="Evolución de saldos"/>\n'
    s=s +  '            <menuitem label="Listado de tarjetas"  onclick="location=\'tarjetaslistado.psp\';"   class="menuitem-iconic"  image="images/visa.png"/>\n'
    s=s +  '            <menuitem label="Transferencia bancaria"  onclick="location=\'cuenta_transferencia.psp\';"  class="menuitem-iconic"  image="images/hotsync.png" />\n'
    s=s +  '         </menupopup>\n'
    s=s +  '      </menu>\n'
    s=s +  '      <menu label="Inversiones">\n'
    s=s +  '         <menupopup>\n'
    s=s +  '            <menuitem label="Estado"  onclick="location=\'inversionessaldo.psp\';"  class="menuitem-iconic"  image="images/toggle_log.png"/>\n'
    s=s +  '            <menuitem label="Compra / Venta"  onclick="location=\'inversion_compraventa.psp\';"  class="menuitem-iconic"  image="images/toggle_log.png"/>\n'
    s=s +  '            <menuitem label="Clasificación" onclick="location=\'inversionesinformacion.psp\';"/>\n'
    s=s +  '            <menuitem label="Histórico" onclick="location=\'inversion_historico.psp\';" class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '         </menupopup>\n'
    s=s +  '      </menu>\n'
    s=s +  '      <menu label="Informes">\n'
    s=s +  '         <menupopup>\n'
    s=s +  '            <menuitem label="Clasificación" onclick="location=\'inversionesinformacion.psp\';"  class="menuitem-iconic" image="images/cakes.png" />\n'
    s=s +  '            <menuitem label="Total" onclick="location=\'informe_total.psp\';"  class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '         </menupopup>\n'
    s=s +  '    </menu>\n'    
    s=s +  '    <menu label="Ayuda">\n'
    s=s +  '      <menupopup>\n'
    s=s +  '        <menuitem label="Acerca de"  onclick="location=\'about.psp\';"  class="menuitem-iconic" image="images/history.png" />\n'
    s=s +  '      </menupopup>\n'
    s=s +  '    </menu>\n'
    s=s +  '  </menubar>\n'
    s=s +  '</toolbox>\n'
    return s


def treecell_euros(importe):
    if importe>=0:
        s='<treecell label="'+euros(importe)+'" />\n';
    else:
        s='<treecell properties="negative" label="'+euros(importe)+'" />\n';
    return s
    
def treecell_tpc(importe):
    if importe>=0:
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
        s='<treecell properties="alert" label="'+euros(importealerta)+'" />\n';
    else:
        s='<treecell label="'+euros(importealerta)+'" />\n';        
    return s
    
def treecell_euros_alerta_venta(importeactual, importealerta, tpcalerta):
    """
        Función que pone una celda en alerta dependiendo si varia un tanto por ciento del importe alerta para comprar
        Es decir si va desde menor del importealerta hasta un tpc del importe alerta
    """
    if importeactual >= importealerta*(1-tpcalerta):
        s='<treecell properties="alert" label="'+euros(importealerta)+'" />\n';
    else:
        s='<treecell label="'+euros(importealerta)+'" />\n';        
    return s


def combo_ano(inicio,fin, selected,  js=True):
    s="<hbox>"
    s=s + '<label value="Selecciona un año"/>\n'
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
