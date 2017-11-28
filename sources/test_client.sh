#!/bin/bash
set -x
xulpymoney_bolsamadrid_client --ISIN ES0178430E18 --share --fromdate 2017-09-10
xulpymoney_bolsamadrid_client --ISIN FR0011042753 --etf --fromdate 2017-09-10
xulpymoney_bolsamadrid_client --ISIN ES00000126B2 --ISIN ES0000012932 --publicbond
xulpymoney_bolsamadrid_client --ISIN_XULPYMONEY ES0178430E18 1 --share --fromdate 2017-11-20
xulpymoney_bolsamadrid_client --ISIN_XULPYMONEY FR0011042753 2 --etf --fromdate 2017-11-20
xulpymoney_bolsamadrid_client --ISIN_XULPYMONEY ES00000126B2 3 --ISIN_XULPYMONEY ES0000012932 4 --publicbond
xulpymoney_morningstar_client --TICKER F000002ODD
xulpymoney_morningstar_client --TICKER_XULPYMONEY F000002ODD  5
xulpymoney_bolsamadrid_client --index --ISIN_XULPYMONEY NONENONE 79329 --fromdate 2017-11-19
xulpymoney_bolsamadrid_client --share --ISIN_XULPYMONEY ES0105200416 81093 --ISIN_XULPYMONEY ES0105200002 81701 --ISIN_XULPYMONEY ES0111845014 78269 --ISIN_XULPYMONEY ES0125220311 78281 --ISIN_XULPYMONEY ES0132105018 78325 --ISIN_XULPYMONEY ES0167050915 78327 --ISIN_XULPYMONEY ES0106000013 81441 --ISIN_XULPYMONEY ES0182045312 81700 --ISIN_XULPYMONEY ES0105046009  81704 --ISIN_XULPYMONEY NL0000235190 81699 --ISIN_XULPYMONEY MXP000511016 81444 --ISIN_XULPYMONEY ES0157097017 78333 --ISIN_XULPYMONEY ES0109067019 78334 --ISIN_XULPYMONEY MXP001691213 78381 --ISIN_XULPYMONEY ES0109260531 78383 --ISIN_XULPYMONEY LU0569974404 78346 --ISIN_XULPYMONEY ES0105022000 81690 --ISIN_XULPYMONEY LU0323134006 81101 --ISIN_XULPYMONEY ES0109427734 78384 --ISIN_XULPYMONEY ES0121975017 81102 --ISIN_XULPYMONEY ES0112458312 78398 --ISIN_XULPYMONEY BRBBDCACNPR8 78399 --ISIN_XULPYMONEY ES0113860A34 81104 --ISIN_XULPYMONEY ES0113790531 81103 --ISIN_XULPYMONEY ES0113900J37 81105 --ISIN_XULPYMONEY ES0113307039 81111 --ISIN_XULPYMONEY ES0113679I37 78412 --ISIN_XULPYMONEY MXP370711014 81446 --ISIN_XULPYMONEY ES0114297015 81447 --ISIN_XULPYMONEY ARBRIO010194 81445 --ISIN_XULPYMONEY DE000BAY0017 80820 --ISIN_XULPYMONEY ES0113211835 81112 --ISIN_XULPYMONEY ARP125991090 81424 --ISIN_XULPYMONEY ES0172233118 80839 --ISIN_XULPYMONEY ES0115002018 81426 --ISIN_XULPYMONEY ES0115056139 80840 --ISIN_XULPYMONEY BRBRAPACNOR5 81427 --ISIN_XULPYMONEY BRBRAPACNPR2 80844 --ISIN_XULPYMONEY BRBRKMACNPA4 80845 --ISIN_XULPYMONEY ES0140609019 81113 --ISIN_XULPYMONEY ES0114400007 81429 --ISIN_XULPYMONEY ES0121501318 78415 --ISIN_XULPYMONEY BRCMIGACNPR3 78447 --ISIN_XULPYMONEY ES0117390411 78446 --ISIN_XULPYMONEY ES0105630315 78451 --ISIN_XULPYMONEY ES0119037010 81448 --ISIN_XULPYMONEY ES0119256115 78455 --ISIN_XULPYMONEY ES0158300410 80846 --ISIN_XULPYMONEY BRCPLEACNPB9 78457 --ISIN_XULPYMONEY ES0117160111 78461 --ISIN_XULPYMONEY ES0124204019 78471 --ISIN_XULPYMONEY ES0184140210 81428 --ISIN_XULPYMONEY ES0110047919 78473 --ISIN_XULPYMONEY ES0126775032 81114 --ISIN_XULPYMONEY ES0126501131 78474 --ISIN_XULPYMONEY ES0126962010 78518 --ISIN_XULPYMONEY ES0162600417 78472 --ISIN_XULPYMONEY ES0112501012 81115 --ISIN_XULPYMONEY ES0129743318 78775 --ISIN_XULPYMONEY BRELETACNPB7 81358 --ISIN_XULPYMONEY BRELETACNOR6 81361 --ISIN_XULPYMONEY ES0130960018 81117 --ISIN_XULPYMONEY CLP3710M1090 81363 --ISIN_XULPYMONEY ES0130670112 78880 --ISIN_XULPYMONEY IT0004618465 78881 --ISIN_XULPYMONEY CLP371861061 78885 --ISIN_XULPYMONEY ES0125140A14 78886 --ISIN_XULPYMONEY ES0168561019 78867 --ISIN_XULPYMONEY ES0134950F36 78238 --ISIN_XULPYMONEY ES0122060314 78907 --ISIN_XULPYMONEY ES0118900010 78908 --ISIN_XULPYMONEY ES0136463017 78962 --ISIN_XULPYMONEY ES0137650018 78964 --ISIN_XULPYMONEY ES0140441017 79016 --ISIN_XULPYMONEY ES0141571119 79036 --ISIN_XULPYMONEY ES0143416115 79037 --ISIN_XULPYMONEY ES0116870314 79046 --ISIN_XULPYMONEY ES0141960635 79051 --ISIN_XULPYMONEY BRGGBRACNPR8 79135 --ISIN_XULPYMONEY MX01EL000003 81370 --ISIN_XULPYMONEY ES0130625512 79141 --ISIN_XULPYMONEY ES0171996012 79142 --ISIN_XULPYMONEY MXP4833F1044 81371 --ISIN_XULPYMONEY ES0116920333 79136 --ISIN_XULPYMONEY COT13PA00011 81372 --ISIN_XULPYMONEY ES0108180219 81513 --ISIN_XULPYMONEY ES0177542018 81346 --ISIN_XULPYMONEY ES0144580Y14 81347 --ISIN_XULPYMONEY ES0147561015 79163 --ISIN_XULPYMONEY ES0148396015 79192 --ISIN_XULPYMONEY ES0148224118 81348 --ISIN_XULPYMONEY ES0118594417 79197 --ISIN_XULPYMONEY ES0139140042 79200 --ISIN_XULPYMONEY ES0139140018 77072 --ISIN_XULPYMONEY ES0154653911 81350 --ISIN_XULPYMONEY ES0152768612 81352 --ISIN_XULPYMONEY ES0175290115 79202 --ISIN_XULPYMONEY ES0158480311 81356 --ISIN_XULPYMONEY ES0105027009  81705 --ISIN_XULPYMONEY ES0124244E34 79244 --ISIN_XULPYMONEY ES0161376019 79221 --ISIN_XULPYMONEY ES0184696013 81703 --ISIN_XULPYMONEY ES0152503035 79223 --ISIN_XULPYMONEY ES0176252718 79277 --ISIN_XULPYMONEY ES0105025003   81706 --ISIN_XULPYMONEY ES0154220414 79278 --ISIN_XULPYMONEY ES0164180012 79279 --ISIN_XULPYMONEY ES0116494016 79283 --ISIN_XULPYMONEY MX1BNA060006 79289 --ISIN_XULPYMONEY ES0165515117 75607 --ISIN_XULPYMONEY ES0165359011 79333 --ISIN_XULPYMONEY BRNETCACNPR3 80662 --ISIN_XULPYMONEY ES0161560018 79335 --ISIN_XULPYMONEY ES0166300212 79336 --ISIN_XULPYMONEY ES0150480111 79298 --ISIN_XULPYMONEY ES0142090317 79299 --ISIN_XULPYMONEY ES0169350016 79300 --ISIN_XULPYMONEY BRPETRACNOR9 79343 --ISIN_XULPYMONEY BRPETRACNPR6 79354 --ISIN_XULPYMONEY ES0170884417 75609 --ISIN_XULPYMONEY ES0171743117 75588 --ISIN_XULPYMONEY ES0171743042 79355 --ISIN_XULPYMONEY ES0175438235 79356 --ISIN_XULPYMONEY ES0110944016 81525 --ISIN_XULPYMONEY ES0173908015 81527 --ISIN_XULPYMONEY ES0173093115 79359 --ISIN_XULPYMONEY IT0001178240 81529 --ISIN_XULPYMONEY IT0001178299 81528 --ISIN_XULPYMONEY ES0173358039 81530 --ISIN_XULPYMONEY ES0173365018 81531 --ISIN_XULPYMONEY ES0173516115 79360 --ISIN_XULPYMONEY ES0122761010 81532 --ISIN_XULPYMONEY ES0157261019 81533 --ISIN_XULPYMONEY ES0182870214 81534 --ISIN_XULPYMONEY ES0180918015 81535 --ISIN_XULPYMONEY MX01SA030007 81536 --ISIN_XULPYMONEY ES0143421G11 81537 --ISIN_XULPYMONEY ES0165380017 81514 --ISIN_XULPYMONEY ES0165386014 81515 --ISIN_XULPYMONEY ES0138109014 81516 --ISIN_XULPYMONEY BRSUZBACNPA3 81517 --ISIN_XULPYMONEY ES0178165017 79361 --ISIN_XULPYMONEY ES0147582B12 81518 --ISIN_XULPYMONEY ES0178430E18 78241 --ISIN_XULPYMONEY MXP904131325 81526 --ISIN_XULPYMONEY ES0170885018 81519 --ISIN_XULPYMONEY ES0132945017 81520 --ISIN_XULPYMONEY ES0180850416 81521 --ISIN_XULPYMONEY MXP740471117 81522 --ISIN_XULPYMONEY ES0182170615 81523 --ISIN_XULPYMONEY ES0182280018 78252 --ISIN_XULPYMONEY BRUSIMACNPA6 79416 --ISIN_XULPYMONEY BRUSIMACNOR3 79377 --ISIN_XULPYMONEY BRVALEACNOR0 79382 --ISIN_XULPYMONEY BRVALEACNPA3 79387 --ISIN_XULPYMONEY ES0183746314 79395 --ISIN_XULPYMONEY ES0184262212 79397 --ISIN_XULPYMONEY ES0114820113 81524 --ISIN_XULPYMONEY PEP648014202 79398 --ISIN_XULPYMONEY ES0184591032 79399 --ISIN_XULPYMONEY ES0184933812 79418 --ISIN_XULPYMONEY ES0184940817 79425
xulpymoney_bolsamadrid_client --etf --ISIN_XULPYMONEY ES0105321030 81439 --ISIN_XULPYMONEY ES0105336038 81440 --ISIN_XULPYMONEY ES0105305009 78272 --ISIN_XULPYMONEY ES0105322004 81438 --ISIN_XULPYMONEY ES0106078001 81443 --ISIN_XULPYMONEY ES0142446006 81425 --ISIN_XULPYMONEY LU0274211480 78524 --ISIN_XULPYMONEY LU0292107991 81430 --ISIN_XULPYMONEY LU0292103651 81465 --ISIN_XULPYMONEY LU0322249037 81466 --ISIN_XULPYMONEY LU0292109344 81467 --ISIN_XULPYMONEY LU0292109856 78522 --ISIN_XULPYMONEY LU0292106241 81468 --ISIN_XULPYMONEY LU0411075020 81469 --ISIN_XULPYMONEY LU0292107645 81470 --ISIN_XULPYMONEY LU0292095535 81471 --ISIN_XULPYMONEY LU0380865021 78209 --ISIN_XULPYMONEY LU0274211217 78219 --ISIN_XULPYMONEY LU0292106753 81351 --ISIN_XULPYMONEY LU0411077828 78227 --ISIN_XULPYMONEY LU0592216393 78236 --ISIN_XULPYMONEY LU0274209740 81353 --ISIN_XULPYMONEY LU0292108619 81354 --ISIN_XULPYMONEY LU0411075376 78575 --ISIN_XULPYMONEY LU0322250712 81355 --ISIN_XULPYMONEY LU0476289466 78578 --ISIN_XULPYMONEY LU0322252502 78580 --ISIN_XULPYMONEY LU0490618542 78581 --ISIN_XULPYMONEY LU0322251520 78582 --ISIN_XULPYMONEY LU0411078636 78583 --ISIN_XULPYMONEY LU0411078552 78678 --ISIN_XULPYMONEY LU0328475792 78748 --ISIN_XULPYMONEY LU0274208692 78753 --ISIN_XULPYMONEY ES0139761003 79015 --ISIN_XULPYMONEY FR0007056841 81359 --ISIN_XULPYMONEY FR0010204073 81360 --ISIN_XULPYMONEY FR0007054358 81362 --ISIN_XULPYMONEY FR0010820258 81364 --ISIN_XULPYMONEY FR0010408799 81487 --ISIN_XULPYMONEY FR0010204081 81488 --ISIN_XULPYMONEY FR0010737544 81489 --ISIN_XULPYMONEY FR0010270033 81490 --ISIN_XULPYMONEY FR0010346205 81491 --ISIN_XULPYMONEY FR0010344879 81492 --ISIN_XULPYMONEY FR0010510800 81493 --ISIN_XULPYMONEY FR0010344960 81494 --ISIN_XULPYMONEY FR0010344812 81495 --ISIN_XULPYMONEY FR0010344853 79203 --ISIN_XULPYMONEY FR0010245514 79205 --ISIN_XULPYMONEY FR0010410266 81496 --ISIN_XULPYMONEY FR0010361683 81498 --ISIN_XULPYMONEY FR0010833541 81499 --ISIN_XULPYMONEY FR0010429068 81500 --ISIN_XULPYMONEY FR0010261198 81501 --ISIN_XULPYMONEY FR0010168765 81502 --ISIN_XULPYMONEY FR0010833566 81503 --ISIN_XULPYMONEY FR0010168781 81504 --ISIN_XULPYMONEY FR0010315770 81505 --ISIN_XULPYMONEY FR0010524777 81506 --ISIN_XULPYMONEY FR0010326140 81507 --ISIN_XULPYMONEY FR0010378604 81508 --ISIN_XULPYMONEY FR0010589101 81509 --ISIN_XULPYMONEY FR0010168773 81510 --ISIN_XULPYMONEY LU0496786574 81511 --ISIN_XULPYMONEY FR0010345371 81512 --ISIN_XULPYMONEY FR0010527275 79210 --ISIN_XULPYMONEY FR0011036268 79217 --ISIN_XULPYMONEY FR0010762492 79230 --ISIN_XULPYMONEY FR0007063177 79232 --ISIN_XULPYMONEY FR0011042753 79228 --ISIN_XULPYMONEY FR0010251744 81357
xulpymoney_quefondos_client --TICKER_XULPYMONEY N1750 1

