import datetime
def arr2stralmohadilla(arr):
    resultado=""
    for a in arr:
        resultado=resultado + str(a) + "#"
    return resultado[:-1]
        
def stralmohadilla2arr(string, type="s"  ,  date=None):
    """SE utiliza para matplotlib dsde consola
        #date es un datetime.date() que se usa para saceer el t"""
    arr=string.split("#")
    resultado=[]
    for a in arr:
            if type=="s":
                    resultado.append(a.decode('UTF-8'))
            elif type=="f":
                    resultado.append(float(a))
            elif type=="t":
                    dat=a.split(":")
                    resultado.append(datetime.datetime(date.year, date.month,  date.day, int(dat[0]),int(dat[1])))
            elif type=="dt":
                    resultado.append(datetime.datetime.strptime(a, "%Y/%m/%d %H:%M"))
            elif type=="d":
                    resultado.append(datetime.datetime.strptime(a, "%Y-%m-%d").toordinal())
    return resultado
