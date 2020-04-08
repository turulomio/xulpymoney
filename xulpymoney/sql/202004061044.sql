
-- Products inserts
insert into public.products (name,  isin,  currency,  type,  agrupations, web, 
            address,  phone, mail, percentage, pci, leveraged, 
            decimals, stockmarkets_id, tickers, comment, obsolete, high_low, id ) values (
            'ETFS Physical Swiss Gold', 'DE000A1DCTL3', 'EUR', 4, '', '', 
            '', '', '', 100, 'c', 1, 
            2, 5, ARRAY[NULL,NULL,NULL,NULL,'GZUR.DE'], '', false, false
            , 81749);
insert into public.products (name,  isin,  currency,  type,  agrupations, web, 
            address,  phone, mail, percentage, pci, leveraged, 
            decimals, stockmarkets_id, tickers, comment, obsolete, high_low, id ) values (
            'Source Physical Markets PLC ZT Gold 30.12.2100', 'DE000A1MECS1', 'EUR', 4, '', '', 
            '', '', '', 100, 'c', 1, 
            2, 5, ARRAY[NULL,NULL,NULL,NULL,'8PSG.DE'], '', false, false
            , 81750);

-- Products updates
