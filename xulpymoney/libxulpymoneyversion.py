## @package libxulpymoneyversion
## @brief Package with xulpymoney version information
import datetime

version="20180518"

def version_windows():
#    lastpoint="0"
#    if version.find("+")!=-1:
#        lastpoint="1"
    vd=version_date()
    return "{}.{}.{}".format(vd.year, vd.month, vd.day)
    
def version_date():
    versio=version.replace("+","")
    return datetime.date(int(versio[:-4]),  int(versio[4:-2]),  int(versio[6:]))
