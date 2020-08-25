CREATE TABLE public.leverages (
    id integer NOT NULL PRIMARY KEY,
    name text NOT NULL,
    multiplier numeric NOT NULL
);


INSERT INTO public.leverages VALUES (-1, 'Variable leverage', -1);
INSERT INTO public.leverages VALUES (1, 'Without leverage', 1);
INSERT INTO public.leverages VALUES (2, 'Leverage x2', 2);
INSERT INTO public.leverages VALUES (3, 'Leverage x3', 3);
INSERT INTO public.leverages VALUES (4, 'Leverage x4', 4);
INSERT INTO public.leverages VALUES (5, 'Leverage x5', 5);
INSERT INTO public.leverages VALUES (10, 'Leverage x10', 10);
INSERT INTO public.leverages VALUES (20, 'Leverage x20', 20);
INSERT INTO public.leverages VALUES (25, 'Leverage x25', 25);
INSERT INTO public.leverages VALUES (50, 'Leverage x50', 50);
INSERT INTO public.leverages VALUES (100, 'Leverage x100', 100);
INSERT INTO public.leverages VALUES (1000, 'Leverage x100', 1000);

ALTER TABLE public.products RENAME COLUMN leveraged TO leverages_id;

ALTER TABLE public.products ADD CONSTRAINT products__leverages_id___fk___leverages__id FOREIGN KEY (leverages_id) REFERENCES public.leverages(id) ON DELETE RESTRICT;

CREATE TABLE public.operationstypes (
    id integer NOT NULL PRIMARY KEY,
    name text NOT NULL
);

INSERT INTO public.operationstypes VALUES (1, 'Expense');
INSERT INTO public.operationstypes VALUES (2, 'Income');
INSERT INTO public.operationstypes VALUES (3, 'Transfer');
INSERT INTO public.operationstypes VALUES (4, 'Purchase of shares');
INSERT INTO public.operationstypes VALUES (5, 'Sale of shares');
INSERT INTO public.operationstypes VALUES (6, 'Shares addition');
INSERT INTO public.operationstypes VALUES (7, 'Credit card billing');
INSERT INTO public.operationstypes VALUES (8, 'Transfer of funds');
INSERT INTO public.operationstypes VALUES (9, 'Transfer of shares origin');
INSERT INTO public.operationstypes VALUES (10, 'Transfer of shares destiny');
INSERT INTO public.operationstypes VALUES (11, 'Derivative management');

ALTER TABLE public.accountsoperations ADD CONSTRAINT accountsoperations__operationstypes_id___fk___operationstypes__id FOREIGN KEY (operationstypes_id) REFERENCES public.operationstypes(id) ON DELETE RESTRICT;
ALTER TABLE public.concepts ADD CONSTRAINT concepts__operationstypes_id___fk___operationstypes__id FOREIGN KEY (operationstypes_id) REFERENCES public.operationstypes(id) ON DELETE RESTRICT;
ALTER TABLE public.creditcardsoperations ADD CONSTRAINT creditcardsoperations__operationstypes_id___fk___operationstypes__id FOREIGN KEY (operationstypes_id) REFERENCES public.operationstypes(id) ON DELETE RESTRICT;
ALTER TABLE public.investmentsoperations ADD CONSTRAINT investmentsoperations__operationstypes_id___fk___operationstypes__id FOREIGN KEY (operationstypes_id) REFERENCES public.operationstypes(id) ON DELETE RESTRICT;

CREATE TABLE public.productstypes (
    id integer NOT NULL PRIMARY KEY,
    name text NOT NULL
);

INSERT INTO public.productstypes VALUES (1, 'Share');
INSERT INTO public.productstypes VALUES (2, 'Fund');
INSERT INTO public.productstypes VALUES (3, 'Index');
INSERT INTO public.productstypes VALUES (4, 'ETF');
INSERT INTO public.productstypes VALUES (5, 'Warrant');
INSERT INTO public.productstypes VALUES (6, 'Currency');
INSERT INTO public.productstypes VALUES (7, 'Public bond');
INSERT INTO public.productstypes VALUES (8, 'Pension plan');
INSERT INTO public.productstypes VALUES (9, 'Private bond');
INSERT INTO public.productstypes VALUES (10, 'Deposit');
INSERT INTO public.productstypes VALUES (11, 'Account');
INSERT INTO public.productstypes VALUES (12, 'CFD');
INSERT INTO public.productstypes VALUES (13, 'Future');


ALTER TABLE public.products RENAME COLUMN type TO productstypes_id;

ALTER TABLE public.products ADD CONSTRAINT products__productstypes_id___fk___productstypes__id FOREIGN KEY (productstypes_id) REFERENCES public.productstypes(id) ON DELETE RESTRICT;


-- FUNCTIONS
CREATE OR REPLACE PROCEDURAL LANGUAGE plpython3u;
DROP FUNCTION public.cuenta_saldo;
DROP FUNCTION public.cuentas_saldo;
DROP FUNCTION public.create_role_if_not_exists(rolename name);
DROP FUNCTION public.is_price_variation_in_time(p_id_products integer, p_percentage double precision, p_datetime timestamp with time zone);
DROP FUNCTION public.last_penultimate_lastyear(INOUT id integer, at_datetime timestamp with time zone, OUT last_datetime timestamp with time zone, OUT last numeric, OUT penultimate_datetime timestamp with time zone, OUT penultimate numeric, OUT lastyear_datetime timestamp with time zone, OUT lastyear numeric);
DROP FUNCTION public.penultimate(INOUT id integer, date date, OUT quote numeric, OUT datetime timestamp with time zone, OUT searched timestamp with time zone);
DROP FUNCTION public.quote(INOUT id integer, INOUT datetime timestamp with time zone, OUT quote numeric, OUT searched timestamp with time zone);




