## -*- coding: utf-8 -*-
from decimal import *
dividendwithholding=Decimal('0.21')
taxcapitalappreciation=Decimal('0.21')
localcurrency='EUR'
localzone='Europe/Madrid'
indicereferencia=79329#myquotesid 79329#ibex  =75540#"^STOXX50E"=81083#"^GSPC"
#        return self.currentIndex
#CONFIGURE MYQUOTES
host='127.0.0.1'
dbname='myquotes'
user='postgres'
password='xxx'
port=5432
myquoteslib='/usr/lib/myquotes'
