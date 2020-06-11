
-- Products inserts
insert into public.products (name,  isin,  currency,  type,  agrupations, web, 
            address,  phone, mail, percentage, pci, leveraged, 
            decimals, stockmarkets_id, tickers, comment, obsolete, high_low, id ) values (
            'SMI 20 SUIZA', NULL, 'EUR', 3, '', '', 
            '', '', '', 100, 'c', 1, 
            2, 10, ARRAY[NULL,NULL,NULL,NULL,'SWI20'], '', false, false
            , 81755);
insert into public.products (name,  isin,  currency,  type,  agrupations, web, 
            address,  phone, mail, percentage, pci, leveraged, 
            decimals, stockmarkets_id, tickers, comment, obsolete, high_low, id ) values (
            'CFD SMI 20 SUIZA', NULL, 'EUR', 12, '', '', 
            '', '', '', 100, 'c', 25, 
            2, 10, ARRAY[NULL,NULL,NULL,NULL,'FSMIc1'], '', false, true
            , 81756);

-- Products updates
