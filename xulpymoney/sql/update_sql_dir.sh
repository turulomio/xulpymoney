#!/bin/bash
MYUSER=${1:-postgres}
MYPORT=${2:-5432}
MYHOST=${3:-127.0.0.1}
DATABASE=${4:-xulpymoney}


echo "Introduzca la contraseña de administrador de postgres"
read -s password

echo "Debe ejecutarse desde el directorio sql"
PGPASSWORD=$password pg_dump --no-privileges -s -U $MYUSER -h $MYHOST -p $MYPORT $DATABASE > xulpymoney.sql
PGPASSWORD=$password pg_dump --no-privileges -a -U $MYUSER -h $MYHOST -p $MYPORT $DATABASE -t stockmarkets --insert > xulpymoney.bolsas
cat xulpymoney.bolsas| grep -i 'INSERT INTO' | sort >> xulpymoney.sql
rm xulpymoney.bolsas
PGPASSWORD=$password pg_dump --no-privileges -a -U $MYUSER -h $MYHOST -p $MYPORT $DATABASE -t products --insert > xulpymoney.products
cat xulpymoney.products| grep -i 'INSERT INTO' | sort >> xulpymoney.sql
rm xulpymoney.products
PGPASSWORD=$password pg_dump --no-privileges -a -U $MYUSER -h $MYHOST -p $MYPORT $DATABASE -t globals --insert > xulpymoney.globals
cat xulpymoney.globals| grep -i 'INSERT INTO' | sort >> xulpymoney.sql
rm xulpymoney.globals
echo "DELETE FROM products WHERE id<=0;" >> xulpymoney.sql
echo "ALTER SEQUENCE seq_conceptos START WITH 100 RESTART;" >> xulpymoney.sql
echo "ALTER SEQUENCE seq_entidadesbancarias START WITH 4 RESTART;" >> xulpymoney.sql
echo "ALTER SEQUENCE seq_cuentas START WITH 5 RESTART;" >> xulpymoney.sql
echo "UPDATE globals set value=NULL where id_globals=6;" >> xulpymoney.sql
echo "DELETE FROM globals where id_globals>6;" >> xulpymoney.sql

echo "SELECT create_role_if_not_exists('xulpymoney_admin');" >> xulpymoney.sql
echo "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA PUBLIC TO xulpymoney_admin;" >> xulpymoney.sql
echo "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA PUBLIC TO xulpymoney_admin;" >> xulpymoney.sql

echo "SELECT create_role_if_not_exists('xulpymoney_user');" >> xulpymoney.sql  
echo "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA PUBLIC TO xulpymoney_user;" >> xulpymoney.sql
echo "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA PUBLIC TO xulpymoney_user;" >> xulpymoney.sql
