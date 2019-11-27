select;
UPDATE public.products SET tickers=array_replace(tickers, 'ES35U9', 'MFXIc1') where tickers[5]='ES35U9';
