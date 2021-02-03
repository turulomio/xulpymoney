
-- Products inserts
insert into public.products (name,  isin,  currency,  productstypes_id,  agrupations, web, 
            address,  phone, mail, percentage, pci, leverages_id, 
            decimals, stockmarkets_id, tickers, comment, obsolete, high_low, id ) values (
            'FUTURO MINI SP500', NULL, 'USD', 13, '', '', 
            '', '', '', 100, 'c', 50, 
            2, 2, ARRAY[NULL,NULL,NULL,NULL,'ESc1'], '', false, true
            , 81759);

-- Products updates
update public.products set name='CFD SP500', productstypes_id=12 where id=81744;
