from argparse import ArgumentParser, RawTextHelpFormatter
from decimal import Decimal

def calcular_ganancia(lista_entradas, lista_acciones, precio_calculo, apalancamiento, call):
    r=0
    for i, entrada in enumerate(lista_entradas):
        if call is True:
            r=r+ (precio_calculo-entrada)*lista_acciones[i]*apalancamiento
        else:
            r=r+ (-precio_calculo+entrada)*lista_acciones[i]*apalancamiento
    return r

def main(arguments=None):
    parser=ArgumentParser( description='Plus minus report', formatter_class=RawTextHelpFormatter)
    parser.add_argument('--apalancamiento', help="Create demo files", action="store",default='10')
    parser.add_argument('--precio_inicial', help="Create demo files", action="store",required=True)
    parser.add_argument('--ganancia', help="Create demo files", action="store",default='100')
    parser.add_argument('--acciones', help="Create demo files", action="store",default='0.2')
    parser.add_argument('--number_call', help="Create demo files", action="store", required=True)
    parser.add_argument('--number_put', help="Create demo files", action="store", required=True)
    parser.add_argument('--direction', help="Create demo files", action="store", choices=["call","put"], required=True)
    parser.add_argument('--step', action="store", default="30")

    args=parser.parse_args(arguments)
    
    precio_inicial=Decimal(args.precio_inicial)
    apalancamiento=Decimal(args.apalancamiento)
    acciones=Decimal(args.acciones)
    ganancia=Decimal(args.ganancia)
    step=Decimal(args.step)
    n_c=int(args.number_call)
    n_p=int(args.number_put)
    if args.direction=="call":
        print ("Inversión alcista")
        call_direction=True
    else:
        print("Inversión bajista")
        call_direction=False
    
    print("Precio inicial:", precio_inicial)
    print("Inversion cada {} puntos".format(step))
    print("Para ganar:", ganancia)
    
    
    call=[]
    acciones_call=[]
    put=[]
    acciones_put=[]
    for i in range(n_c):
        if call_direction is True:
            call.append(precio_inicial+step*i)
        else:
            call.append(precio_inicial+step*(i+1))
        acciones_call.append(acciones)

    for i in range(n_p):
         if call_direction is True:
              put.append(precio_inicial -step*(i+1))
         else:
              put.append(precio_inicial - step*i)
         acciones_put.append(acciones)
         
    #Precios medios
    if len(call)==0:
        call_medio=0
    else:
        call_medio=sum(call)/len(call)
    if len(put)==0:
        put_medio=0
    else:
        put_medio=sum(put)/len(put)

    print("Calls",call, sum(acciones_call), "a", call_medio, "Nominal:", call_medio*sum(acciones_call)*apalancamiento)
    print("Puts",put, sum(acciones_put), "a", put_medio, "Nominal:", put_medio*sum(acciones_put)*apalancamiento)


    results=[]#Tuple precio, ganancia_final y porcentage, ganancia_call, ganancia_put
    for x in range(-1000, 1000):
          ganancia_call=calcular_ganancia(call,acciones_call, precio_inicial+x,apalancamiento, True)
          ganancia_put=calcular_ganancia(put, acciones_put,  precio_inicial+x, apalancamiento, False)
          ganancia_final=ganancia_call+ganancia_put
          
          if ganancia_final>ganancia*Decimal(0.8) and ganancia_final<ganancia*Decimal(1.2):
              results.append([precio_inicial +x, ganancia_final, round((x*100)/precio_inicial,2),ganancia_call, ganancia_put])
              
    results = sorted(results, key=lambda item: item[2])
 
    sel_index=None
    menor_diff=10000
    for i, o in enumerate(results):
          diff=abs(o[1]-ganancia)
          if diff<abs(menor_diff):
              sel_index=i
              menor_diff=diff
    
    precio_venta=results[sel_index][0]
     
    if sel_index is not None:
           print("Ganancia call:", results[sel_index][3],"Ganancia put:", results[sel_index][4])
           print("precio venta:", precio_venta, "Ganancia:", results[sel_index][1], "Porcentage", results[sel_index][2],"%")
    else:
           print("No se encontró resultado")


    #Aviso de inversión de más
    for o in call:
        if precio_inicial<precio_venta and  o>=precio_venta:
                  print("OJO: HAS INVERTIDO DE MAS AL ALZA")
    for o in put:
        if precio_inicial>precio_venta and o<=precio_venta:
                  print("OJO: HAS INVERTIDO DE MAS A LA BAJA")
    
    #Aviso de poder invertir más
    if len(call)>0:
        if precio_inicial<precio_venta and precio_venta-call[len(call)-1]>step:
            print("OJO: PODRÁS INVERTIR OTRA CAPA AL ALZA")
    if len(put)>0:
        if precio_inicial>precio_venta and precio_venta-put[len(put)-1]<-step:
            print("OJO: PODRÁS INVERTIR OTRA CAPA A LA BAJA")
    




if __name__ == "__main__":
    main()
