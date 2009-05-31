# -*- coding: UTF-8  -*-
import sys
sys.path.append("/usr/local/lib/cuentas/")


from core import *

con=Conection()
#c=InversionActualizacion().xul_treechildren_listado(InversionActualizacion().cursor_listado(57,2008,9))
print Total().saldo_por_tipo_operacion(2008,10,1)
con.close()

