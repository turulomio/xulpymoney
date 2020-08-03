-- Adding daily adjustment column
ALTER TABLE public.inversiones ADD COLUMN daily_adjustment boolean NOT NULL DEFAULT FALSE;
update public.inversiones set daily_adjustment=TRUE where id_inversiones in (select id_inversiones from public.inversiones, public.products where products.type in (12,13) and inversiones.products_id=products.id); --cfd and futures type
