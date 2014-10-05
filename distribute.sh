#!/bin/bash
DIR=xulpymoney-`cat libxulpymoney.py | grep 'version="'| cut --delimiter='"'  -f 2`
FILE=$DIR.tar.gz
echo "Este script crea el fichero $FILE para ser subido al proyecto"

mkdir -p $DIR
mkdir -p $DIR/i18n
mkdir -p $DIR/images
mkdir -p $DIR/sql
mkdir -p $DIR/test
mkdir -p $DIR/sources
mkdir -p $DIR/ui

cp      Makefile \
        AUTHORS.txt \
        CHANGELOG.txt \
        GPL-3.txt \
        INSTALL.txt \
        RELEASES.txt \
        xulpymoney.py \
        xulpymoney_init.py \
        xulpymoney.desktop \
        xulpymoney.pro \
        libxulpymoney.py \
        $DIR

cp      i18n/*.ts \
        $DIR/i18n

cp      images/*.png \
        images/*.jpg \
        images/*.gif \
        images/xulpymoney.qrc \
        $DIR/images

cp      sources/*.py \
        $DIR/sources

cp      test/*.py \
        $DIR/test

rm      ui/Ui_*
cp      ui/*.py \
        ui/*.ui \
        $DIR/ui

cp      sql/* \
        $DIR/sql

tar cvz $DIR -f $FILE
rm -R $DIR
