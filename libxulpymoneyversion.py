import datetime

version="20170216"

def version_windows():
    lastpoint="0"
    if version.find("+")!=-1:
        lastpoint="1"
        
    versio=version.replace("+","")
    return versio[:-4]+"."+versio[4:-2]+"."+versio[6:]+"."+lastpoint
    
def version_date():
    versio=version.replace("+","")
    return datetime.date(int(versio[:-4]),  int(versio[4:-2]),  int(versio[6:]))
