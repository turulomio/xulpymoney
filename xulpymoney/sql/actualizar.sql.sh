#!/bin/bash
echo "Debe ejecutarse desde el directorio sql"
pg_dump -s -U postgres -h 127.0.0.1 -p  5432 myquotes > myquotes.sql
cat globals.init  >> myquotes.sql
pg_dump -a -U postgres -h 127.0.0.1 -p  5432 myquotes -t investments >> myquotes.sql
pg_dump -a -U postgres -h 127.0.0.1 -p  5432 myquotes -t bolsas >> myquotes.sql
pg_dump -a -U postgres -h 127.0.0.1 -p  5432 myquotes -t dividendosestimaciones >> myquotes.sql
pg_dump -a -U postgres -h 127.0.0.1 -p  5432 myquotes -t dividendospagos >> myquotes.sql
echo "update investments set deletable=true;" >> myquotes.sql



