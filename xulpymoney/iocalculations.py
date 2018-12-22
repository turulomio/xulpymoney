op=[1,-1,-2,2,3,4,-7,-3,-4,7]
cur=[]
hst=[]

for io in op:
    if sum(cur)>=0 and io>0:
        cur.append(io)
    elif sum(cur)<=0 and io<0:
        cur.append(io)
    elif sum(cur)+io==0:
        cur=[]
        hst.append(io)

    print(io, op, cur, hst)