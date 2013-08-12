#!/bin/bash
MYUSER=${1:-postgres}
MYPORT=${2:-5432}
MYHOST=${3:-127.0.0.1}
MYDATABASE=${4:-mystocks}

echo "Debe ejecutarse desde el directorio sql"
pg_dump -s -U $MYUSER -h $MYHOST -p $MYPORT $MYDATABASE > myquotes.sql
pg_dump -a -U $MYUSER -h $MYHOST -p $MYPORT $MYDATABASE -t investments > myquotes.data
pg_dump -a -U $MYUSER -h $MYHOST -p $MYPORT $MYDATABASE -t bolsas >> myquotes.data
echo "update investments set deletable=true;" >> myquotes.data



