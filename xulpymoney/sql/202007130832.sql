
-- Products inserts
insert into public.products (name,  isin,  currency,  type,  agrupations, web, 
            address,  phone, mail, percentage, pci, leveraged, 
            decimals, stockmarkets_id, tickers, comment, obsolete, high_low, id ) values (
            'XAU / USD', NULL, 'u', 6, '', '', 
            '', '', '', 100, 'c', 1, 
            2, 2, ARRAY[NULL,NULL,NULL,NULL,'XAU/USD - Oro al contado Dólar estadounidense'], '', false, false
            , 81757);
insert into public.products (name,  isin,  currency,  type,  agrupations, web, 
            address,  phone, mail, percentage, pci, leveraged, 
            decimals, stockmarkets_id, tickers, comment, obsolete, high_low, id ) values (
            'CFD GOLD', NULL, 'USD', 12, '', '', 
            '', '', '', 100, 'c', 100, 
            2, 2, ARRAY[NULL,NULL,NULL,NULL,'XAU/USD - Oro al contado Dólar estadounidense'], '', false, true
            , 81758);

-- Products updates
