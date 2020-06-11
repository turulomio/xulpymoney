
-- Products inserts
insert into public.products (name,  isin,  currency,  type,  agrupations, web, 
            address,  phone, mail, percentage, pci, leveraged, 
            decimals, stockmarkets_id, tickers, comment, obsolete, high_low, id ) values (
            'CFD CAC 40', NULL, 'EUR', 12, '', '', 
            '', '', '', 100, 'c', 10, 
            2, 3, ARRAY[NULL,NULL,NULL,NULL,'FCEc1'], '', false, true
            , 81754);

-- Products updates
