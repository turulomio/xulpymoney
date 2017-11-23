#!/bin/bash
set -x
python3 ./bolsamadrid_client.py --ISIN ES0178430E18 --share --fromdate 2017-09-10
python3 ./bolsamadrid_client.py --ISIN FR0011042753 --etf --fromdate 2017-09-10
python3 ./bolsamadrid_client.py --ISIN ES00000126B2 --ISIN ES0000012932 --publicbond

