-- Improving all schema

-- Products
ALTER TABLE public.products RENAME CONSTRAINT investments_pk TO products_pk;
ALTER SEQUENCE investments_seq RENAME TO products_seq;
ALTER TABLE public.products ALTER COLUMN id set DEFAULT nextval('"products_seq"'::text::regclass);

-- Concepts
ALTER TABLE public.conceptos RENAME TO concepts;
ALTER TABLE public.concepts RENAME COLUMN id_conceptos TO id;
ALTER TABLE public.concepts RENAME COLUMN concepto TO name;
ALTER TABLE public.concepts RENAME COLUMN id_tiposoperaciones TO operationstypes_id;
ALTER SEQUENCE seq_conceptos RENAME TO concepts_seq;
ALTER TABLE public.concepts ALTER COLUMN id set DEFAULT nextval('"concepts_seq"'::text::regclass);

-- Accounts
ALTER TABLE public.cuentas RENAME TO accounts;
ALTER TABLE public.accounts RENAME COLUMN id_cuentas TO id;
ALTER TABLE public.accounts RENAME COLUMN cuenta TO name;
ALTER TABLE public.accounts RENAME COLUMN numerocuenta TO number;
ALTER TABLE public.accounts RENAME CONSTRAINT cuentas_pk TO accounts_pk;
ALTER SEQUENCE seq_cuentas RENAME TO accounts_seq;
ALTER TABLE public.accounts ALTER COLUMN id set DEFAULT nextval('"accounts_seq"'::text::regclass);

-- Dividends
ALTER TABLE public.dividends RENAME COLUMN id_dividends TO id;
ALTER TABLE public.dividends RENAME COLUMN bruto TO gross;
ALTER TABLE public.dividends RENAME COLUMN retencion TO taxes;
ALTER TABLE public.dividends RENAME COLUMN neto TO net;
ALTER TABLE public.dividends RENAME COLUMN valorxaccion TO dps;
ALTER TABLE public.dividends RENAME COLUMN fecha TO datetime;
ALTER TABLE public.dividends RENAME COLUMN id_opercuentas TO accountsoperations_id;
ALTER TABLE public.dividends RENAME COLUMN comision TO commission;
ALTER TABLE public.dividends RENAME COLUMN id_conceptos TO concepts_id;
ALTER TABLE public.dividends RENAME CONSTRAINT dividendos_pkey TO dividends_pk;
ALTER SEQUENCE seq_dividendos RENAME TO dividends_seq;
ALTER TABLE public.dividends ALTER COLUMN id set DEFAULT nextval('"dividends_seq"'::text::regclass);

-- Investments
ALTER TABLE public.inversiones RENAME TO investments;
ALTER TABLE public.investments RENAME COLUMN id_inversiones TO id;
ALTER TABLE public.investments RENAME COLUMN inversion TO name;
ALTER TABLE public.investments RENAME COLUMN id_cuentas TO accounts_id;
ALTER TABLE public.investments RENAME COLUMN venta TO selling_price;
ALTER TABLE public.investments RENAME CONSTRAINT pk_inversiones TO investments_pk;
ALTER SEQUENCE seq_inversiones RENAME TO investments_seq;
ALTER TABLE public.investments ALTER COLUMN id set DEFAULT nextval('"investments_seq"'::text::regclass);

-- Accounts operations
ALTER TABLE public.opercuentas RENAME TO accountsoperations;
ALTER TABLE public.accountsoperations RENAME COLUMN id_opercuentas TO id;
ALTER TABLE public.accountsoperations RENAME COLUMN id_conceptos TO concepts_id;
ALTER TABLE public.accountsoperations RENAME COLUMN id_tiposoperaciones TO operationstypes_id;
ALTER TABLE public.accountsoperations RENAME COLUMN importe TO amount;
ALTER TABLE public.accountsoperations RENAME COLUMN comentario TO comment;
ALTER TABLE public.accountsoperations RENAME COLUMN id_cuentas TO accounts_id;
ALTER TABLE public.accountsoperations RENAME CONSTRAINT pk_opercuentas TO accountsoperations_pk;
ALTER SEQUENCE seq_opercuentas RENAME TO accountsoperations_seq;
ALTER TABLE public.accountsoperations ALTER COLUMN id set DEFAULT nextval('"accountsoperations_seq"'::text::regclass);

-- Investments operations
ALTER TABLE public.operinversiones RENAME TO investmentsoperations;
ALTER TABLE public.investmentsoperations RENAME COLUMN id_operinversiones TO id;
ALTER TABLE public.investmentsoperations RENAME COLUMN acciones TO shares;
ALTER TABLE public.investmentsoperations RENAME COLUMN id_tiposoperaciones TO operationstypes_id;
ALTER TABLE public.investmentsoperations RENAME COLUMN impuestos TO taxes;
ALTER TABLE public.investmentsoperations RENAME COLUMN comentario TO comment;
ALTER TABLE public.investmentsoperations RENAME COLUMN id_inversiones TO investments_id;
ALTER TABLE public.investmentsoperations RENAME COLUMN comision TO commission;
ALTER TABLE public.investmentsoperations RENAME COLUMN valor_accion TO price;
ALTER TABLE public.investmentsoperations DROP COLUMN divisa;
ALTER TABLE public.investmentsoperations RENAME CONSTRAINT pk_operinversiones TO investmentsoperations_pk;
ALTER SEQUENCE seq_operinversiones RENAME TO investmentsoperations_seq;
ALTER TABLE public.investmentsoperations ALTER COLUMN id set DEFAULT nextval('"investmentsoperations_seq"'::text::regclass);

-- Credit cards operations
ALTER TABLE public.opertarjetas RENAME TO creditcardsoperations;
ALTER TABLE public.creditcardsoperations RENAME COLUMN id_opertarjetas TO id;
ALTER TABLE public.creditcardsoperations RENAME COLUMN id_conceptos TO concepts_id;
ALTER TABLE public.creditcardsoperations RENAME COLUMN id_tiposoperaciones TO operationstypes_id;
ALTER TABLE public.creditcardsoperations RENAME COLUMN importe TO amount;
ALTER TABLE public.creditcardsoperations RENAME COLUMN comentario TO comment;
ALTER TABLE public.creditcardsoperations RENAME COLUMN id_tarjetas TO creditcards_id;
ALTER TABLE public.creditcardsoperations RENAME COLUMN pagado TO paid;
ALTER TABLE public.creditcardsoperations RENAME COLUMN fechapago TO paid_datetime;
ALTER TABLE public.creditcardsoperations RENAME COLUMN id_opercuentas TO accountsoperations_id;
ALTER TABLE public.creditcardsoperations RENAME CONSTRAINT opertarjetas_pkey TO creditcardsoperations_pk;
ALTER SEQUENCE seq_opertarjetas RENAME TO creditcardsoperations_seq;
ALTER TABLE public.creditcardsoperations ALTER COLUMN id set DEFAULT nextval('"creditcardsoperations_seq"'::text::regclass);


-- Quotes
ALTER TABLE public.quotes RENAME COLUMN id TO products_id;
ALTER TABLE public.quotes RENAME COLUMN id_quotes TO id;

-- Splits
ALTER SEQUENCE splits_id_seq RENAME TO splits_seq;
ALTER TABLE public.splits ALTER COLUMN id set DEFAULT nextval('"splits_seq"'::text::regclass);


-- Credit cards
ALTER TABLE public.tarjetas RENAME TO creditcards;
ALTER TABLE public.creditcards RENAME COLUMN id_tarjetas TO id;
ALTER TABLE public.creditcards RENAME COLUMN tarjeta TO name;
ALTER TABLE public.creditcards RENAME COLUMN id_cuentas TO accounts_id;
ALTER TABLE public.creditcards RENAME COLUMN numero TO number;
ALTER TABLE public.creditcards RENAME COLUMN pagodiferido TO deferred;
ALTER TABLE public.creditcards RENAME COLUMN saldomaximo TO maximumbalance;
ALTER TABLE public.creditcards RENAME CONSTRAINT tarjetas_pkey TO creditcards_pk;
ALTER SEQUENCE seq_tarjetas RENAME TO creditcards_seq;
ALTER TABLE public.creditcards ALTER COLUMN id set DEFAULT nextval('"creditcards_seq"'::text::regclass);


