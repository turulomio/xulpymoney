# -*- coding: UTF-8 -*-
import os
from xul import *
from core import *
from translate import  _
def index(req):
    req.content_type="application/vnd.mozilla.xul+xml"
    req.write(xulheaderwindowmenu(_(u"Menú del programa")))
    req.write('<vbox  flex="5">')
    req.write('<label id="titulo" value="Xulpymoney" />')
    req.write('<label value="'+str(version)+'" style="text-align : center; "/>')
    req.write('<label value="Acerca de Xulpymoney - '+str(version)+'" style="color : DarkGrey; text-align : right;" onclick="location=\'about.py\'" />')
    req.write('</vbox>')
    req.write('</window>')
