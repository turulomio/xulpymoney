#!/bin/bash
MYUSER=${1:-postgres}
MYPORT=${2:-5432}
MYHOST=${3:-127.0.0.1}
MSDATABASE=${4:-mystocks}
XULPYMONEYDATABASE=${5:-xulpymoney}

echo "Debe ejecutarse desde el directorio sql"
pg_dump -s -U $MYUSER -h $MYHOST -p $MYPORT $MSDATABASE > myquotes.sql
pg_dump -a -U $MYUSER -h $MYHOST -p $MYPORT $MSDATABASE -t products --insert > myquotes.data
pg_dump -a -U $MYUSER -h $MYHOST -p $MYPORT $MSDATABASE -t bolsas --insert >> myquotes.data
echo "update products set deletable=true;" >> myquotes.data

pg_dump -s -U $MYUSER -h $MYHOST -p $MYPORT $XULPYMONEYDATABASE > xulpymoney.sql


