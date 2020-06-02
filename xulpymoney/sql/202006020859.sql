
-- Products inserts
insert into public.products (name,  isin,  currency,  type,  agrupations, web, 
            address,  phone, mail, percentage, pci, leveraged, 
            decimals, stockmarkets_id, tickers, comment, obsolete, high_low, id ) values (
            'CFD Futuro Euro Stoxx 50', NULL, 'EUR', 12, '', '', 
            '', '', '', 100, 'c', 10, 
            2, 10, ARRAY[NULL,NULL,NULL,NULL,'STXEc1'], '', false, true
            , 81753);

-- Products updates
update public.products set name='FUTURO EURO STOXX', isin=NULL, currency='EUR', type=13, agrupations='', web='', 
            address='', phone='', mail='', percentage=100, pci='p', leveraged=10, 
            decimals=2, stockmarkets_id=10, tickers=ARRAY[NULL,NULL,NULL,NULL,'STXEc1'], comment='', obsolete=false,high_low=true 
            where id=81738;
update public.products set name='CFD DAX 30', isin=NULL, currency='EUR', type=12, agrupations='', web='', 
            address='', phone='', mail='', percentage=100, pci='c', leveraged=25, 
            decimals=2, stockmarkets_id=5, tickers=ARRAY[NULL,NULL,NULL,NULL,'DE30'], comment='', obsolete=false,high_low=true 
            where id=81752;
