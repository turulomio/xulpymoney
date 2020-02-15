-- Remove derivative inneceary concepts
UPDATE public.opercuentas SET id_conceptos=68 where id_conceptos=69;
UPDATE public.opercuentas SET id_conceptos=70 where id_conceptos=71;
DELETE FROM public.conceptos WHERE id_conceptos in (69,71,73,74);
UPDATE public.conceptos SET concepto='Derivatives. Daily adjustment' WHERE id_conceptos=68;
UPDATE public.conceptos SET concepto='Derivatives. Daily guarantee' WHERE id_conceptos=70;
