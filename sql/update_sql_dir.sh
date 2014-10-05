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
echo "UPDATE products SET deletable=true;" >> xulpymoney.sql
echo "DELETE FROM products WHERE id<=0;" >> xulpymoney.sql
echo "UPDATE products SET active=true WHERE priorityhistorical[1]=3;" >> xulpymoney.sql
echo "ALTER SEQUENCE seq_conceptos START WITH 100 RESTART;" >> xulpymoney.sql
echo "ALTER SEQUENCE seq_entidadesbancarias START WITH 4 RESTART;" >> xulpymoney.sql
echo "ALTER SEQUENCE seq_cuentas START WITH 5 RESTART;" >> xulpymoney.sql
echo "INSERT INTO globals (id_globals, global, value) values (6, 'Admin mode password', NULL);" >> xulpymoney.sql
