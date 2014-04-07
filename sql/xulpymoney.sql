--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: plpythonu; Type: PROCEDURAL LANGUAGE; Schema: -; Owner: postgres
--

CREATE OR REPLACE PROCEDURAL LANGUAGE plpythonu;


ALTER PROCEDURAL LANGUAGE plpythonu OWNER TO postgres;

SET search_path = public, pg_catalog;

--
-- Name: dblink_pkey_results; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE dblink_pkey_results AS (
	"position" integer,
	colname text
);


ALTER TYPE public.dblink_pkey_results OWNER TO postgres;

--
-- Name: quote_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE quote_type AS (
	code text,
	date date,
	"time" time without time zone,
	zone text,
	quote numeric(100,6)
);


ALTER TYPE public.quote_type OWNER TO postgres;

--
-- Name: cuenta_saldo(integer, date); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION cuenta_saldo(p_id_cuentas integer, p_fechaparametro date) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    recCuentas RECORD;
    resultado numeric(100,2);
BEGIN
    resultado := 0;
    FOR recCuentas IN SELECT * FROM opercuentas where id_cuentas=p_id_cuentas and fecha <= p_fechaparametro LOOP
resultado := resultado + recCuentas.importe;
    END LOOP;
    RETURN resultado;
END;
$$;


ALTER FUNCTION public.cuenta_saldo(p_id_cuentas integer, p_fechaparametro date) OWNER TO postgres;

--
-- Name: cuentas_saldo(date); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION cuentas_saldo(fechaparametro date) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
DECLARE
    recCuentas RECORD;
    resultado numeric(100,2);
BEGIN
    resultado := 0;
    FOR recCuentas IN SELECT * FROM cuentas  LOOP
resultado := resultado + cuenta_saldo(recCuentas.id_cuentas, fechaparametro);
    END LOOP;
    RETURN resultado;
END;
$$;


ALTER FUNCTION public.cuentas_saldo(fechaparametro date) OWNER TO postgres;

--
-- Name: inversion_acciones(integer, date); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION inversion_acciones(p_id_inversiones integer, p_date date) RETURNS numeric
    LANGUAGE plpythonu
    AS $$  resultado=0
  reg=plpy.execute("SELECT acciones from operinversiones where id_inversiones={0} and fecha <='{1}'".format(p_id_inversiones,p_date))
  for row in reg:
    resultado=resultado+row['acciones']
  return resultado

$$;


ALTER FUNCTION public.inversion_acciones(p_id_inversiones integer, p_date date) OWNER TO postgres;

--
-- Name: inversion_acciones_saldo(integer, date, numeric); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION inversion_acciones_saldo(p_id_inversiones integer, p_date date, p_quote_in_p_date numeric) RETURNS numeric[]
    LANGUAGE plpythonu
    AS $$  acciones=0
  reg=plpy.execute("SELECT acciones from operinversiones where id_inversiones={0} and fecha <='{1}'".format(p_id_inversiones,p_date))
  for row in reg:
    acciones=acciones+row['acciones']
  return [acciones,acciones*p_quote_in_p_date]

$$;


ALTER FUNCTION public.inversion_acciones_saldo(p_id_inversiones integer, p_date date, p_quote_in_p_date numeric) OWNER TO postgres;

--
-- Name: inversion_saldo_segun_tpcvariable(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION inversion_saldo_segun_tpcvariable() RETURNS SETOF record
    LANGUAGE plpgsql ROWS 4
    AS $$
DECLARE
re RECORD;
BEGIN
   FOR re in EXECUTE 'SELECT tpcvariable::integer, sum(inversiones_saldo(id_inversiones, date(now())))  FROM inversiones GROUP BY tpcvariable, in_activa HAVING in_activa=True ORDER BY tpcvariable' LOOP
    RETURN next re;
  END LOOP;
  RETURN;
END;
$$;


ALTER FUNCTION public.inversion_saldo_segun_tpcvariable() OWNER TO postgres;

--
-- Name: transferencia(date, integer, integer, numeric, numeric); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION transferencia(p_fecha date, p_cuentaorigen integer, p_cuentadestino integer, p_importe numeric, p_comision numeric) RETURNS void
    LANGUAGE plpgsql
    AS $$DECLARE
    nombrecuentaorigen text;
    nombrecuentadestino text;
BEGIN
    SELECT cuenta INTO nombrecuentaorigen FROM cuentas WHERE id_cuentas=p_cuentaorigen;
    SELECT cuenta INTO nombrecuentadestino FROM cuentas WHERE id_cuentas=p_cuentadestino;

    INSERT INTO opercuentas (fecha, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas) VALUES (p_fecha, 4, 3, -p_importe-p_comision, 'A ' || nombrecuentadestino || ' (Comisión '|| p_comision ||' €)', p_cuentaorigen); 
    INSERT INTO opercuentas (fecha, id_conceptos, id_tiposoperaciones, importe, comentario, id_cuentas) VALUES (p_fecha, 5, 3, p_importe, 'De ' || nombrecuentaorigen, p_cuentadestino);    
END;
$$;


ALTER FUNCTION public.transferencia(p_fecha date, p_cuentaorigen integer, p_cuentadestino integer, p_importe numeric, p_comision numeric) OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: conceptos; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE conceptos (
    id_conceptos integer DEFAULT nextval(('"seq_conceptos"'::text)::regclass) NOT NULL,
    concepto text,
    id_tiposoperaciones integer,
    editable boolean DEFAULT true NOT NULL
);


ALTER TABLE public.conceptos OWNER TO postgres;

SET default_with_oids = true;

--
-- Name: cuentas; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE cuentas (
    id_cuentas integer DEFAULT nextval(('"seq_cuentas"'::text)::regclass) NOT NULL,
    cuenta text,
    id_entidadesbancarias integer,
    cu_activa boolean,
    numerocuenta character varying(24),
    currency text DEFAULT 'EUR'::text NOT NULL
);


ALTER TABLE public.cuentas OWNER TO postgres;

SET default_with_oids = false;

--
-- Name: dividendos; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE dividendos (
    id_dividendos integer DEFAULT nextval(('"seq_dividendos"'::text)::regclass) NOT NULL,
    id_inversiones integer NOT NULL,
    bruto numeric(100,2) NOT NULL,
    retencion numeric(100,2) NOT NULL,
    neto numeric(100,2),
    valorxaccion numeric(100,6),
    fecha date,
    id_opercuentas integer,
    comision numeric(100,2),
    id_conceptos integer DEFAULT 39 NOT NULL
);


ALTER TABLE public.dividendos OWNER TO postgres;

SET default_with_oids = true;

--
-- Name: entidadesbancarias; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE entidadesbancarias (
    id_entidadesbancarias integer DEFAULT nextval(('"seq_entidadesbancarias"'::text)::regclass) NOT NULL,
    entidadbancaria text NOT NULL,
    eb_activa boolean NOT NULL
);


ALTER TABLE public.entidadesbancarias OWNER TO postgres;

SET default_with_oids = false;

--
-- Name: inversiones; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE inversiones (
    id_inversiones integer DEFAULT nextval(('"seq_inversiones"'::text)::regclass) NOT NULL,
    inversion text NOT NULL,
    in_activa boolean DEFAULT true NOT NULL,
    id_cuentas integer NOT NULL,
    venta numeric(100,6) DEFAULT 0 NOT NULL,
    mystocksid integer
);


ALTER TABLE public.inversiones OWNER TO postgres;

SET default_with_oids = true;

--
-- Name: opercuentas; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE opercuentas (
    id_opercuentas integer DEFAULT nextval(('"seq_opercuentas"'::text)::regclass) NOT NULL,
    fecha date NOT NULL,
    id_conceptos integer NOT NULL,
    id_tiposoperaciones integer NOT NULL,
    importe numeric(100,2) NOT NULL,
    comentario text,
    id_cuentas integer NOT NULL
);


ALTER TABLE public.opercuentas OWNER TO postgres;

--
-- Name: opertarjetas; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE opertarjetas (
    id_opertarjetas integer DEFAULT nextval(('"seq_opertarjetas"'::text)::regclass) NOT NULL,
    fecha date,
    id_conceptos integer NOT NULL,
    id_tiposoperaciones integer NOT NULL,
    importe numeric(100,2) NOT NULL,
    comentario text,
    id_tarjetas integer NOT NULL,
    pagado boolean NOT NULL,
    fechapago date,
    id_opercuentas bigint
);


ALTER TABLE public.opertarjetas OWNER TO postgres;

--
-- Name: opercuentastarjetas; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW opercuentastarjetas AS
         SELECT opercuentas.fecha,
            opercuentas.id_conceptos,
            opercuentas.importe
           FROM opercuentas
UNION
         SELECT opertarjetas.fecha,
            opertarjetas.id_conceptos,
            opertarjetas.importe
           FROM opertarjetas;


ALTER TABLE public.opercuentastarjetas OWNER TO postgres;

--
-- Name: VIEW opercuentastarjetas; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON VIEW opercuentastarjetas IS 'Used to get concepts stadistics';


SET default_with_oids = false;

--
-- Name: operinversiones; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE operinversiones (
    id_operinversiones integer DEFAULT nextval(('"seq_operinversiones"'::text)::regclass) NOT NULL,
    id_tiposoperaciones integer,
    id_inversiones integer,
    acciones numeric(100,6),
    importe numeric(100,2),
    impuestos numeric(100,2),
    comision numeric(100,2),
    valor_accion numeric(100,6),
    hora time without time zone DEFAULT '00:00:00'::time without time zone NOT NULL,
    divisa numeric(10,6) DEFAULT NULL::numeric,
    datetime timestamp with time zone,
    comentario text
);


ALTER TABLE public.operinversiones OWNER TO postgres;

--
-- Name: COLUMN operinversiones.hora; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN operinversiones.hora IS 'Es UTC time';


--
-- Name: COLUMN operinversiones.divisa; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN operinversiones.divisa IS 'Campo que calcula el cociente entre la divisa de la divisa de la cuenta bancaria asociada entre la divisa de la inversión es decir EUR/USD. Si eur es la cuenta bancariaa y usd la divisa de la inversión';


--
-- Name: seq_conceptos; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_conceptos
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_conceptos OWNER TO postgres;

--
-- Name: seq_cuentas; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_cuentas
    START WITH 0
    INCREMENT BY 1
    MINVALUE 0
    MAXVALUE 1000000
    CACHE 1;


ALTER TABLE public.seq_cuentas OWNER TO postgres;

--
-- Name: seq_dividendos; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_dividendos
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_dividendos OWNER TO postgres;

--
-- Name: seq_entidadesbancarias; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_entidadesbancarias
    START WITH 0
    INCREMENT BY 1
    MINVALUE 0
    MAXVALUE 100000000
    CACHE 1;


ALTER TABLE public.seq_entidadesbancarias OWNER TO postgres;

--
-- Name: seq_inversiones; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_inversiones
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_inversiones OWNER TO postgres;

--
-- Name: seq_opercuentas; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_opercuentas
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_opercuentas OWNER TO postgres;

--
-- Name: seq_operinversiones; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_operinversiones
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_operinversiones OWNER TO postgres;

--
-- Name: seq_operinversioneshistoricas; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_operinversioneshistoricas
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_operinversioneshistoricas OWNER TO postgres;

--
-- Name: seq_opertarjetas; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_opertarjetas
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_opertarjetas OWNER TO postgres;

--
-- Name: seq_tarjetas; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_tarjetas
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.seq_tarjetas OWNER TO postgres;

SET default_with_oids = true;

--
-- Name: tarjetas; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE tarjetas (
    id_tarjetas integer DEFAULT nextval(('"seq_tarjetas"'::text)::regclass) NOT NULL,
    tarjeta text,
    id_cuentas integer,
    pagodiferido boolean,
    saldomaximo numeric(100,2),
    tj_activa boolean,
    numero text
);


ALTER TABLE public.tarjetas OWNER TO postgres;

--
-- Name: tmpinversionesheredada; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE tmpinversionesheredada (
    id_operinversiones integer NOT NULL,
    id_inversiones integer NOT NULL
)
INHERITS (opercuentas);


ALTER TABLE public.tmpinversionesheredada OWNER TO postgres;

--
-- Name: id_opercuentas; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY tmpinversionesheredada ALTER COLUMN id_opercuentas SET DEFAULT nextval(('"seq_opercuentas"'::text)::regclass);


--
-- Name: conceptos_pk; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY conceptos
    ADD CONSTRAINT conceptos_pk PRIMARY KEY (id_conceptos);


--
-- Name: dividendos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY dividendos
    ADD CONSTRAINT dividendos_pkey PRIMARY KEY (id_dividendos);


--
-- Name: opertarjetas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY opertarjetas
    ADD CONSTRAINT opertarjetas_pkey PRIMARY KEY (id_opertarjetas);


--
-- Name: pk_inversiones; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY inversiones
    ADD CONSTRAINT pk_inversiones PRIMARY KEY (id_inversiones);


--
-- Name: pk_opercuentas; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY opercuentas
    ADD CONSTRAINT pk_opercuentas PRIMARY KEY (id_opercuentas);


--
-- Name: pk_operinversiones; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY operinversiones
    ADD CONSTRAINT pk_operinversiones PRIMARY KEY (id_operinversiones);


--
-- Name: tarjetas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY tarjetas
    ADD CONSTRAINT tarjetas_pkey PRIMARY KEY (id_tarjetas);


--
-- Name: conceptos-id_conceptos-index; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX "conceptos-id_conceptos-index" ON conceptos USING btree (id_conceptos);


--
-- Name: cuentas-id_cuentas-index; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX "cuentas-id_cuentas-index" ON cuentas USING btree (id_cuentas);


--
-- Name: dividendos-id_inversiones-index; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX "dividendos-id_inversiones-index" ON dividendos USING btree (id_inversiones);


--
-- Name: entidadesbancarias-id_entidadesbancarias-index; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX "entidadesbancarias-id_entidadesbancarias-index" ON entidadesbancarias USING btree (id_entidadesbancarias);


--
-- Name: inversiones-id_cuentas-index; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX "inversiones-id_cuentas-index" ON inversiones USING btree (id_cuentas);


--
-- Name: inversiones-id_inversiones-index; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX "inversiones-id_inversiones-index" ON inversiones USING btree (id_inversiones);


--
-- Name: opercuentas-id_cuentas-index; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX "opercuentas-id_cuentas-index" ON opercuentas USING btree (id_cuentas);


--
-- Name: opercuentas-id_opercuentas-index; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX "opercuentas-id_opercuentas-index" ON opercuentas USING btree (id_opercuentas);


--
-- Name: operinversiones-id_inversiones-index; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX "operinversiones-id_inversiones-index" ON operinversiones USING btree (id_inversiones);


--
-- Name: operinversiones-id_operinversiones-index; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX "operinversiones-id_operinversiones-index" ON operinversiones USING btree (id_operinversiones);


--
-- Name: opertarjetas-id_opertarjetas-index; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX "opertarjetas-id_opertarjetas-index" ON opertarjetas USING btree (id_opertarjetas);


--
-- Name: opertarjetas-id_tarjetas-index; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX "opertarjetas-id_tarjetas-index" ON opertarjetas USING btree (id_tarjetas);


--
-- Name: tmpinversionesheredada-id_cuentas-index; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX "tmpinversionesheredada-id_cuentas-index" ON tmpinversionesheredada USING btree (id_cuentas);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

