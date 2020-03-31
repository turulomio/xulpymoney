DELETE FROM public.globals where id=2; --Version products.xlsx
ALTER TABLE public.globals DROP CONSTRAINT pk_globals;
ALTER TABLE public.globals DROP COLUMN id;
ALTER TABLE public.globals ADD PRIMARY KEY (global);