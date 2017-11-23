#!/bin/bash
set -x
xulpymoney_bolsamadrid_client --ISIN ES0178430E18 --share --fromdate 2017-09-10
xulpymoney_bolsamadrid_client --ISIN FR0011042753 --etf --fromdate 2017-09-10
xulpymoney_bolsamadrid_client --ISIN ES00000126B2 --ISIN ES0000012932 --publicbond
xulpymoney_bolsamadrid_client --ISIN ES0178430E18 --share --fromdate 2017-11-20 --XULPYMONEY 1
xulpymoney_bolsamadrid_client --ISIN FR0011042753 --etf --fromdate 2017-11-20 --XULPYMONEY 2
xulpymoney_bolsamadrid_client --ISIN ES00000126B2 --ISIN ES0000012932 --publicbond --XULPYMONEY 3 --XULPYMONEY 4
xulpymoney_morningstar_client --TICKER F000002ODD
xulpymoney_morningstar_client --TICKER F000002ODD --XULPYMONEY 5
