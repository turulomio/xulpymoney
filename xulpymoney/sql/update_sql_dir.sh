#!/bin/bash
MYUSER=${1:-postgres}
MYPORT=${2:-5432}
MYHOST=${3:-127.0.0.1}
DATABASE=${4:-xulpymoney}

echo "Debe ejecutarse desde el directorio sql"
pg_dump -s -U $MYUSER -h $MYHOST -p $MYPORT $DATABASE > xulpymoney.sql
pg_dump -a -U $MYUSER -h $MYHOST -p $MYPORT $DATABASE -t products --insert > xulpymoney.products
cat xulpymoney.products| grep -i 'INSERT INTO' | sort >> xulpymoney.sql
rm xulpymoney.products
pg_dump -a -U $MYUSER -h $MYHOST -p $MYPORT $DATABASE -t bolsas --insert > xulpymoney.bolsas
cat xulpymoney.bolsas| grep -i 'INSERT INTO' | sort >> xulpymoney.sql
rm xulpymoney.bolsas
pg_dump -a -U $MYUSER -h $MYHOST -p $MYPORT $DATABASE -t globals --insert > xulpymoney.globals
cat xulpymoney.globals| grep -i 'INSERT INTO' | sort >> xulpymoney.sql
rm xulpymoney.globals
echo "DELETE FROM products WHERE id<=0;" >> xulpymoney.sql
echo "ALTER SEQUENCE seq_conceptos START WITH 100 RESTART;" >> xulpymoney.sql
echo "ALTER SEQUENCE seq_entidadesbancarias START WITH 4 RESTART;" >> xulpymoney.sql
echo "ALTER SEQUENCE seq_cuentas START WITH 5 RESTART;" >> xulpymoney.sql
echo "UPDATE globals set value=NULL where id_globals=6;" >> xulpymoney.sql