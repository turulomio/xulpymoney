from csv import reader
from logging import debug
from datetime import date
from xulpymoney.libxulpymoney import QuoteManager, Quote, OHCLDaily
from xulpymoney.libxulpymoneyfunctions import string2date, string2decimal, string2datetime, dtaware, string2time
from xulpymoney.libxulpymoneytypes import eTickerPosition

class InvestingCom(QuoteManager):
    def __init__(self, mem, filename, product=None):
        QuoteManager.__init__(self, mem)
        self.mem=mem
        self.filename=filename
        self.product=product
        self.columns=self.get_number_of_csv_columns()
        if self.product==None: #Several products
            if self.columns==8:
                print("append_from_default")
                self.append_from_default()
            elif self.columns==39:
                print("append_from_portfolio")
                self.append_from_portfolio()
            else:
                debug("The number of columns doesn't match: {}".format(self.columns))
        else:
            print("append_from_historical")
            self.append_from_historical()

    def get_number_of_csv_columns(self):
        columns=0
        with open(self.filename) as csv_file:
            csv_reader = reader(csv_file, delimiter=',')
            for row in csv_reader:
                columns=len(row)
                break
        return columns
        
    ## Used by InvestingCom, to load indexes components, it has 8 columns
    ## 0 Índice 
    ## 1 Símbolo    
    ## 2 Último 
    ## 3 Máximo 
    ## 4 Mínimo 
    ## 5 Var
    ## 6 % Var. 
    ## 7 Hora
    def append_from_default(self):
            with open(self.filename) as csv_file:
                csv_reader = reader(csv_file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    if line_count >0:#Ignores headers line
                        product=self.mem.data.products.find_by_ticker(row[1], eTickerPosition.InvestingCom)
                        if product==None:
                            continue
                        if row[7].find(":")==-1:#It's a date
                            try:
                                quote=Quote(self.mem)
                                quote.product=product
                                date_=string2date(row[7], type=4)
                                quote.datetime=dtaware(date_,quote.product.stockmarket.closes,self.mem.localzone.name)#Without 4 microseconds becaouse is not a ohcl
                                quote.quote=string2decimal(row[2])
                                self.append(quote)
                            except:
                                debug("Error parsing "+ str(row))
                        else: #It's an hour
                            try:
                                quote=Quote(self.mem)
                                quote.product=product
                                time_=string2time(row[7], type=2)
                                quote.datetime=dtaware(date.today(), time_, self.mem.localzone.name)
                                quote.quote=string2decimal(row[3])
                                self.append(quote)
                            except:
                                debug("Error parsing "+ str(row))

                    line_count += 1
            print("Added {} quotes from {} CSV lines".format(self.length(), line_count))
        
    ## 0 Nombre 
    ## 1 Símbolo    
    ## 2 Mercado    
    ## 3 Último
    ## 4    Compra  
    ## 5 Venta  
    ## 6 Horario ampliado   
    ## 7 Horario ampliado (%)   
    ## 8 Apertura   
    ## 9 Anterior   
    ## 10 Máximo    
    ## 11 Mínimo    
    ## 12 Var.  
    ## 13 % var.    
    ## 14 Vol.  
    ## 15 Fecha próx. resultados    
    ## 16  Hora Cap. mercado    Ingresos    Vol. promedio (3m)  BPA PER Beta    Dividendo   Rendimiento 5 minutos   15 minutos  30 minutos  1 hora  5 horas Diario  Semanal Mensual Diario  Semanal Mensual Anual   1 año   3 años
    ## It has 39 columns
    def append_from_portfolio(self):
            with open(self.filename) as csv_file:
                csv_reader = reader(csv_file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    if line_count >0:#Ignores headers line
                        product=self.mem.data.products.find_by_ticker(row[1], eTickerPosition.InvestingCom)
                        if product==None:
                            continue
                        if row[16].find(":")==-1:#It's a date
                            try:
                                quote=Quote(self.mem)
                                quote.product=product
                                date_=string2date(row[16], type=4)
                                quote.datetime=dtaware(date_,quote.product.stockmarket.closes, quote.product.stockmarket.zone.name)#Without 4 microseconds becaouse is not a ohcl
                                quote.quote=string2decimal(row[3])
                                self.append(quote)
                            except:
                                debug("Error parsing "+ str(row))
                        else: #It's an hour
                            try:
                                quote=Quote(self.mem)
                                quote.product=product
                                quote.datetime=string2datetime(row[16], type=7)
                                quote.quote=string2decimal(row[3])
                                self.append(quote)
                            except:
                                debug("Error parsing " + str(row))
                    line_count += 1
            print("Added {} quotes from {} CSV lines".format(self.length(), line_count))      

    ## Imports data from a CSV file with this struct. It has 6 columns
    ## "Fecha","Último","Apertura","Máximo","Mínimo","Vol.","% var."
    ## "22.07.2019","10,074","10,060","10,148","9,987","10,36M","-0,08%"
    def append_from_historical(self):
            with open(self.filename) as csv_file:
                csv_reader = reader(csv_file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    if line_count >0:#Ignores headers line
                        try:
                            ohcl=OHCLDaily(self.mem)
                            ohcl.product=self.product
                            ohcl.date=string2date(row[0], type=3)
                            ohcl.close=string2decimal(row[1])
                            ohcl.open=string2decimal(row[2])
                            ohcl.high=string2decimal(row[3])
                            ohcl.low=string2decimal(row[4])
                            for quote in ohcl.generate_4_quotes():
                                self.append(quote)
                        except:
                            debug("Error parsing" + str(row))
                    line_count += 1
            print("Added {} quotes from {} CSV lines".format(self.length(), line_count))