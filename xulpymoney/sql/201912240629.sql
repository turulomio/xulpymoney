-- Adding paydate to dps table and copy data from date column
ALTER TABLE public.dps ADD COLUMN paydate date NOT NULL DEFAULT now();
ALTER TABLE public.dps RENAME COLUMN id TO products_id;
ALTER TABLE public.dps RENAME COLUMN id_dps TO id;
UPDATE public.dps SET paydate = "date";
