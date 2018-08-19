## @package xulpymoney
## @brief Package with xulpymoney version information
import datetime

__version__="0.0.1"
__versiondate__=datetime.date(2018,8,19)
version="20180518"

def version_windows():
#    lastpoint="0"
#    if version.find("+")!=-1:
#        lastpoint="1"
    vd=__versiondate__
    return "{}.{}.{}".format(vd.year, vd.month, vd.day)
    
