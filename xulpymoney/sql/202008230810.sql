-- Dividends
ALTER TABLE public.dividends RENAME COLUMN id_inversiones TO investments_id;

-- Accounts operations of Investments operations
ALTER TABLE public.opercuentasdeoperinversiones RENAME TO investmentsaccountsoperations;
ALTER TABLE public.investmentsaccountsoperations RENAME COLUMN id_operinversiones TO investmentsoperations_id;
ALTER TABLE public.investmentsaccountsoperations RENAME COLUMN id_inversiones TO investments_id;
ALTER TABLE public.investmentsaccountsoperations RENAME CONSTRAINT opercuentasdeoperinversiones_pk TO investmentsaccountsoperations_pk;
DROP SEQUENCE seq_operinversioneshistoricas ;