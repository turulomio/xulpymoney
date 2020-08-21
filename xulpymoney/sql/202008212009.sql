
ALTER TABLE ONLY public.strategies
    ADD CONSTRAINT strategies_pk PRIMARY KEY (id);

ALTER TABLE public.entidadesbancarias RENAME TO banks;

ALTER TABLE public.banks RENAME COLUMN id_entidadesbancarias TO id;
ALTER TABLE public.banks RENAME COLUMN entidadbancaria TO name;
ALTER TABLE public.banks RENAME CONSTRAINT entidadesbancarias_pk TO banks_pk;
ALTER TABLE public.cuentas RENAME CONSTRAINT cuentas_fk_id_entidadesbancarias TO accounts__banks_id__fk__banks_id;

ALTER SEQUENCE seq_entidadesbancarias RENAME TO banks_seq;

ALTER TABLE public.banks ALTER COLUMN id set DEFAULT nextval('"banks_seq"'::text::regclass);

ALTER TABLE public.cuentas RENAME COLUMN id_entidadesbancarias TO banks_id;