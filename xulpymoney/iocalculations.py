#op=[1,-1,-2,2,3,4,-7,-3,-4,7] #Exacto
#op=[1,-2,2,-3,4] #Cambio signo
op=[1,1,-3] #Cambio signo generando 2 hst

cur=[]
hst=[]

for position, io in enumerate(op):
    if sum(cur)>=0 and io>0:
        cur.append(io)
    elif sum(cur)<=0 and io<0:
        cur.append(io)
    elif sum(cur)+io==0:
        cur=[]
        hst.append(io)
    else:
        rest=None
        while rest!=0 or len(cur)==0:
            if rest==None:
                rest=0
            first=cur[0]
            cur.pop(0)
            if (first>0 and first+rest<0) or (first<0 and first+rest>0): #
                hst.append(-first)
                rest=rest+first
                cur.insert(0, rest)
            else: # 
                hst.append(first)
                rest=rest+first
                break

            print("REST", rest, op, cur, hst)
    print(io, op, cur, hst)
    
    