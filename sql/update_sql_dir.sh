#!/bin/bash
MYUSER=${1:-postgres}
MYPORT=${2:-5432}
MYHOST=${3:-127.0.0.1}
MSDATABASE=${4:-mystocks}
XULPYMONEYDATABASE=${5:-xulpymoney}

echo "Debe ejecutarse desde el directorio sql"
pg_dump -s -U $MYUSER -h $MYHOST -p $MYPORT $MSDATABASE > mystocks.sql
pg_dump -a -U $MYUSER -h $MYHOST -p $MYPORT $MSDATABASE -t products --insert > mystocks.data
pg_dump -a -U $MYUSER -h $MYHOST -p $MYPORT $MSDATABASE -t bolsas --insert >> mystocks.data
echo "UPDATE products SET deletable=true;" >> mystocks.data
echo "DELETE FROM products WHERE id<=0;" >> mystocks.data
echo "UPDATE products SET active=true WHERE priorityhistorical[1]=3;" >> mystocks.data


pg_dump -s -U $MYUSER -h $MYHOST -p $MYPORT $XULPYMONEYDATABASE > xulpymoney.sql
echo "ALTER SEQUENCE seq_conceptos START WITH 100 RESTART;" >> xulpymoney.sql
