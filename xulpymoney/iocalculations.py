## DO NOT DELETE. CONCEPT FUNCTION TO PROCESS OPERATIONS
## NECESITADO PARA DEPURAR
def have_same_sign(number1, number2):
    if (is_positive(number1)==True and is_positive(number2)==True) or (is_positive(number1)==False and is_positive(number2)==False):
        return True
    return False

def is_positive(number):
    if number>=0:
        return True
    return False

def set_sign_of_other_number(number, number_to_change):
    if is_positive(number):
       return abs(number_to_change)
    return -abs(number_to_change)

def process(op):
    cur=[]
    hst=[]

    print("Processing {}. Su suma es {}".format(op, sum(op)))

    for position, io in enumerate(op):
        if len(cur)==0 or have_same_sign(cur[0], io)==True:
            cur.append(io)
        elif have_same_sign(cur[0], io)==False:
            rest=io
            while rest!=0:
                if len(cur)>0:
                    if abs(cur[0])>=abs(rest):
                        hst.append(set_sign_of_other_number(io,rest))
                        if rest+cur[0]!=0:
                            cur.insert(0, rest+cur[0])
                            cur.pop(1)
                        else:
                            cur.pop(0)
                        rest=0
                        break
                    else: #Mayor el resto
                        hst.append(set_sign_of_other_number(io,cur[0]))
                        rest=rest+cur[0]
                        rest=set_sign_of_other_number(io,rest)
                        cur.pop(0)
#                        print("   REST>", rest, "Current", cur, "Historical", hst)
                else:
                    cur.insert(0, rest)
                    break
        print("  + IO", io, "Current", cur, "Historical", hst)
    print("La suma de Current es", sum(cur))
    print("")

process([1,-1,-2,2,3,4,-7,-3,-4,7]) #Exacto
process([1,-2,2,-3,4]) #Cambio signo
process([1,1,-3, -1, 5]) #Cambio signo generando 2 hst
process([529, 1597, 12, 43, 340, 40, 468, 502, 908, 1136, 17, 1118, 114, 122, 147, 588, 646, 725, 1136, 1486, 1935, 2027, 793, 248, 308, -602, -387])
