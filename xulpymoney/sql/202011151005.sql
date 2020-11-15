ALTER TABLE public.strategies ADD COLUMN type integer NOT NULL DEFAULT 1;
ALTER TABLE public.strategies ADD COLUMN additional1 integer;
ALTER TABLE public.strategies ADD COLUMN additional2 integer;
ALTER TABLE public.strategies ADD COLUMN additional3 integer;
ALTER TABLE public.strategies ADD COLUMN additional4 integer;
ALTER TABLE public.strategies ALTER COLUMN investments SET NOT NULL;
ALTER TABLE public.strategies ALTER COLUMN dt_from SET NOT NULL;
ALTER TABLE public.strategies ALTER COLUMN dt_from SET DEFAULT now();

