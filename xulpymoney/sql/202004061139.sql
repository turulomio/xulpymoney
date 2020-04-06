
-- Products inserts
insert into products (name,  isin,  currency,  type,  agrupations, web, 
            address,  phone, mail, percentage, pci, leveraged, 
            decimals, stockmarkets_id, tickers, comment, obsolete, high_low, id ) values (
            'Lyxor MSCI ACWI Gold UCITS C EUR', 'LU0854423687', 'EUR', 4, '', '', 
            '', '', '', 100, 'c', 1, 
            2, 3, ARRAY[NULL,NULL,NULL,NULL,'GLDM.PA'], '', false, false
            , 81751);

