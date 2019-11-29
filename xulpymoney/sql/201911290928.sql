-- Removing hlcontracts system
UPDATE public.opercuentas SET comentario='' WHERE id_conceptos IN (68, 69, 70, 71, 72, 73, 74);
DROP TABLE public.high_low_contract;
DROP SEQUENCE public.high_low_contract_seq;
UPDATE public.conceptos SET concepto='Derivatives. Daily gains adjustment' WHERE id_conceptos=68;
UPDATE public.conceptos SET concepto='Derivatives. Daily losses adjustment' WHERE id_conceptos=69;
UPDATE public.conceptos SET concepto='Derivatives. Daily guarantee payment' WHERE id_conceptos=70;
UPDATE public.conceptos SET concepto='Derivatives. Daily guarantee return' WHERE id_conceptos=71;
UPDATE public.conceptos SET concepto='Derivatives. Operation commission' WHERE id_conceptos=72;
UPDATE public.conceptos SET concepto='Derivatives. Paid interest' WHERE id_conceptos=73;
UPDATE public.conceptos SET concepto='Derivatives. Received interest' WHERE id_conceptos=74;
