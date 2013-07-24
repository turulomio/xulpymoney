--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
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
-- Name: quote; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE quote AS (
	id integer,
	datetime timestamp with time zone,
	quote numeric(18,6)
);


ALTER TYPE public.quote OWNER TO postgres;

--
-- Name: quote_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE quote_type AS (
	code text,
	date date,
	"time" time without time zone,
	zone text,
	quote numeric(18,6)
);


ALTER TYPE public.quote_type OWNER TO postgres;

--
-- Name: quotehistoric_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE quotehistoric_type AS (
	code text,
	date date,
	high numeric(18,6),
	low numeric(18,6),
	open numeric(18,6),
	close numeric(18,6),
	volumen numeric(18,6)
);


ALTER TYPE public.quotehistoric_type OWNER TO postgres;

--
-- Name: first_agg(anyelement, anyelement); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION first_agg(anyelement, anyelement) RETURNS anyelement
    LANGUAGE sql IMMUTABLE STRICT
    AS $_$
        SELECT $1;
$_$;


ALTER FUNCTION public.first_agg(anyelement, anyelement) OWNER TO postgres;

--
-- Name: historic(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION historic(p_code text) RETURNS SETOF quotehistoric_type
    LANGUAGE plpythonu
    AS $$  
  reg=plpy.execute("SELECT * FROM quotes WHERE code='" + p_code + "' order by date;")
  resultado=[]
  for i in range(len(reg)):
    if reg[i]["last"]=='close':
      close=reg[i]["close"]
    else:
      close=reg[i][reg[i]["last"]]
    resultado.append( { "code": reg[i]["code"], "date": reg[i]["date"],"high":reg[i]["high"] , "low": reg[i]["low"], "open": reg[i]["open"],"close": close,"volumen": reg[i]["volumen"]   })
  return resultado
$$;


ALTER FUNCTION public.historic(p_code text) OWNER TO postgres;

--
-- Name: intraday(text, date); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION intraday(p_code text, p_date date) RETURNS SETOF quote_type
    LANGUAGE plpythonu
    AS $$  
  reg=plpy.execute("SELECT * FROM quotes WHERE code='" + str(p_code) + "' and date='"+str(p_date)+"';")  
  resultado=[]
  if len(reg)==0:
    return resultado
  else:
    for i in range(24):
      for j in range(60):
        campo=str(i).zfill(2)+str(j).zfill(2)
        time=str(i)+":"+str(j)
        quote=reg[0][campo]
        if quote!=None:
          resultado.append( { "code": p_code, "date": p_date,"time":time , "quote": quote, "zone": reg[0]["zone"]   })
  return resultado

$$;


ALTER FUNCTION public.intraday(p_code text, p_date date) OWNER TO postgres;

--
-- Name: inversion_type(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION inversion_type(p_code text) RETURNS integer
    LANGUAGE plpythonu
    AS $$
  if p_code==None:
    return -1
  reg=plpy.execute("SELECT quotes.* FROM dblink('dbname=myquotes','SELECT type from quotes where code=''"+ p_code+"''')")
  return reg[0]['type']
$$;


ALTER FUNCTION public.inversion_type(p_code text) OWNER TO postgres;

--
-- Name: last_agg(anyelement, anyelement); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION last_agg(anyelement, anyelement) RETURNS anyelement
    LANGUAGE sql IMMUTABLE STRICT
    AS $_$
        SELECT $2;
$_$;


ALTER FUNCTION public.last_agg(anyelement, anyelement) OWNER TO postgres;

--
-- Name: merge_codes(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION merge_codes(main integer, secondary integer) RETURNS integer
    LANGUAGE plpythonu
    AS $$  
  u=plpy.execute("update quotes set id="+str(main) +" where id="+str(secondary))
  ud=plpy.execute("update dividendosestimaciones set id="+str(main) +" where id="+str(secondary))
  dq=plpy.execute("delete from quotes where id="+str(secondary))
  di=plpy.execute("delete from investments where id="+str(secondary))
  dd=plpy.execute("delete from dividendosestimaciones where id="+str(secondary))
  plpy.info("Se han movido %(u)d registros a %(m)s  y borrado %(dq)d de quotes y %(di)d de investments y %(dd)d de dividendosestimaciones" % {"u": u.nrows(), "m": main, "dq": dq.nrows(), "di":di.nrows(),"dd":dd.nrows()} )
$$;


ALTER FUNCTION public.merge_codes(main integer, secondary integer) OWNER TO postgres;

--
-- Name: multiout_simple_setof(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION multiout_simple_setof(n integer, OUT integer, OUT integer) RETURNS SETOF record
    LANGUAGE plpythonu
    AS $$
return [(1, 2)] * n
$$;


ALTER FUNCTION public.multiout_simple_setof(n integer, OUT integer, OUT integer) OWNER TO postgres;

--
-- Name: penultimate(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION penultimate(p_id integer) RETURNS quote
    LANGUAGE plpythonu
    AS $$  
  if p_id==None:
    return { "id": None, "datetime": None, "quote": None }
  regp=plpy.execute("select datetime::date as date from quote({0}, now()::date)".format(p_id))
  if len(regp)==0:
    return { "id": p_id, "datetime": None, "quote": None }
  if regp[0]["date"]==None:
    return { "id": p_id, "datetime": None, "quote": None }
  reg=plpy.execute("select * from quote({0},'{1}'::date-1)".format(p_id,regp[0]["date"]))
  if len(reg)==1:
    return { "id": p_id, "datetime": reg[0]["datetime"], "quote": reg[0]["quote"] }
  else:
    return { "id": p_id, "datetime": None, "quote": None }
$$;


ALTER FUNCTION public.penultimate(p_id integer) OWNER TO postgres;

--
-- Name: penultimate(integer, date); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION penultimate(p_id integer, p_lastdate date) RETURNS quote
    LANGUAGE plpythonu
    AS $$  
  if p_id==None:
    return { "id": None, "datetime": None, "quote": None }
  reg=plpy.execute("select * from quote({0},'{1}'::date-1)".format(p_id,p_lastdate))
  if len(reg)==1:
    return { "id": p_id, "datetime": reg[0]["datetime"], "quote": reg[0]["quote"] }
  else:
    return { "id": p_id, "datetime": None, "quote": None }
$$;


ALTER FUNCTION public.penultimate(p_id integer, p_lastdate date) OWNER TO postgres;

--
-- Name: FUNCTION penultimate(p_id integer, p_lastdate date); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION penultimate(p_id integer, p_lastdate date) IS 'Función que calcula el penultimo valor en días
Se pasa la fecha del ultimo valor y calcula la de ultimo-1=penultimo
Se reduce más de 30 veces el tiempo de ejecución';


--
-- Name: quote(integer, date); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION quote(id integer, p_date date) RETURNS quote
    LANGUAGE plpythonu
    AS $$  
  if id==None:
    return { "id": None, "datetime": None, "quote": None }
  dt=str(p_date)+" 23:59:59+0"
  regq=plpy.execute("select datetime, quote from quote({0},'{1}'::timestamptz)".format(id,dt))
  if len(regq)==1:
    return { "id": id, "datetime": regq[0]["datetime"], "quote": regq[0]["quote"] }
  else:
    return { "id": id, "datetime": None, "quote": None }
    
$$;


ALTER FUNCTION public.quote(id integer, p_date date) OWNER TO postgres;

--
-- Name: quote(integer, timestamp with time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION quote(p_id integer, p_datetime timestamp with time zone) RETURNS quote
    LANGUAGE plpythonu
    AS $$ 
if p_id==None:
    return { "id": None, "datetime": None, "quote": None }
regq=plpy.execute("select quote, datetime from quotes where id={0} and datetime<='{1}' order by datetime desc limit 1".format(p_id,p_datetime))
if len(regq)==1:
  return { "id": p_id, "datetime": regq[0]["datetime"], "quote": regq[0]["quote"] }
else:
  return { "id": p_id, "datetime": None, "quote": None }
    
$$;


ALTER FUNCTION public.quote(p_id integer, p_datetime timestamp with time zone) OWNER TO postgres;

--
-- Name: quote(integer[], timestamp with time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION quote(p_ids integer[], p_datetime timestamp with time zone) RETURNS SETOF quote_type
    LANGUAGE plpythonu
    AS $$ 
  resultado=[]
  regq=plpy.execute(" select id, last(quote), last(datetime) from quotes where id in ({0}) ad datetime<='{1}' group by id".format(str(p_ids)[1:-1],p_datetime))
  for r in regq:
    resultado.append({ "id": r[0], "datetime": r[2], "quote": r[1] })
  return resultado
    
    
$$;


ALTER FUNCTION public.quote(p_ids integer[], p_datetime timestamp with time zone) OWNER TO postgres;

--
-- Name: quote2(integer[], timestamp with time zone); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION quote2(p_ids integer[], p_datetime timestamp with time zone) RETURNS SETOF quote_type
    LANGUAGE plpythonu
    AS $$ 
  resultado=[]
  regq=plpy.execute(" select id, last(quote), last(datetime) from quotes where id in ({0}) ad datetime<='{1}' group by id".format(str(p_ids)[1:-1],p_datetime))
  for r in regq:
    resultado.append({ "id": r[0], "datetime": r[2], "quote": r[1] })
  return resultado
    
    
$$;


ALTER FUNCTION public.quote2(p_ids integer[], p_datetime timestamp with time zone) OWNER TO postgres;

--
-- Name: quote_endmonth(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION quote_endmonth(p_code text) RETURNS SETOF quote_type
    LANGUAGE plpythonu
    AS $$  
  resultado=[]
  regq=plpy.execute("select max(date) from quotes group by date_part('month',date), date_part('year',date) order by date_part('year',date),  date_part('month',date)")
  for date in regq:
    reg=plpy.execute("select * from quote('"+p_code+"', '"+str(date['max'])+"')")
    resultado.append({ "code": p_code, "date": reg[0]["date"],"time":reg[0]["time"] , "quote": reg[0]["quote"], "zone": reg[0]["zone"]   })
  return resultado
$$;


ALTER FUNCTION public.quote_endmonth(p_code text) OWNER TO postgres;

--
-- Name: first(anyelement); Type: AGGREGATE; Schema: public; Owner: postgres
--

CREATE AGGREGATE first(anyelement) (
    SFUNC = first_agg,
    STYPE = anyelement
);


ALTER AGGREGATE public.first(anyelement) OWNER TO postgres;

--
-- Name: last(anyelement); Type: AGGREGATE; Schema: public; Owner: postgres
--

CREATE AGGREGATE last(anyelement) (
    SFUNC = last_agg,
    STYPE = anyelement
);


ALTER AGGREGATE public.last(anyelement) OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: bolsas; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE bolsas (
    id_bolsas integer NOT NULL,
    country text,
    starts time without time zone,
    ends time without time zone,
    name text,
    close time without time zone,
    zone text
);


ALTER TABLE public.bolsas OWNER TO postgres;

--
-- Name: COLUMN bolsas.starts; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN bolsas.starts IS 'Hora de inicio de descargas en UTC';


--
-- Name: COLUMN bolsas.ends; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN bolsas.ends IS 'Hora de finalización de descargas en UTC';


--
-- Name: dividendosestimaciones_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE dividendosestimaciones_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dividendosestimaciones_seq OWNER TO postgres;

--
-- Name: dividendospagos; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE dividendospagos (
    id_dividendospagos integer NOT NULL,
    code text NOT NULL,
    fecha date,
    bruto numeric(18,6)
);


ALTER TABLE public.dividendospagos OWNER TO postgres;

--
-- Name: dividendospagos_id_dividendospagos_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE dividendospagos_id_dividendospagos_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dividendospagos_id_dividendospagos_seq OWNER TO postgres;

--
-- Name: dividendospagos_id_dividendospagos_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE dividendospagos_id_dividendospagos_seq OWNED BY dividendospagos.id_dividendospagos;


--
-- Name: estimaciones; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE estimaciones (
    year integer NOT NULL,
    dpa numeric(18,6) NOT NULL,
    fechaestimacion date,
    fuente text,
    manual boolean,
    id integer NOT NULL,
    bpa numeric(18,6)
);


ALTER TABLE public.estimaciones OWNER TO postgres;

--
-- Name: globals; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE globals (
    id_globals integer NOT NULL,
    global text,
    value text
);


ALTER TABLE public.globals OWNER TO postgres;

--
-- Name: investments; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE investments (
    name text,
    isin text,
    currency text,
    type integer,
    agrupations text,
    active boolean DEFAULT false,
    id integer DEFAULT nextval(('"investments_seq"'::text)::regclass) NOT NULL,
    web text,
    address text,
    phone text,
    mail text,
    tpc integer DEFAULT 100 NOT NULL,
    pci character(1) DEFAULT 'c'::bpchar NOT NULL,
    apalancado integer DEFAULT 0 NOT NULL,
    id_bolsas integer NOT NULL,
    yahoo text,
    priority integer[],
    priorityhistorical integer[],
    comentario text,
    obsolete boolean DEFAULT false NOT NULL,
    deletable boolean DEFAULT true NOT NULL,
    system boolean DEFAULT true NOT NULL
);


ALTER TABLE public.investments OWNER TO postgres;

--
-- Name: COLUMN investments.obsolete; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN investments.obsolete IS 'Comprueba si esta obsoleta la inversión';


--
-- Name: COLUMN investments.deletable; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN investments.deletable IS 'Si es true se puede borrar (por defecto)';


--
-- Name: COLUMN investments.system; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN investments.system IS 'Comprueba si es una inversión gestionada por el sistema o si la ha creado el usuario';


--
-- Name: investments_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE investments_seq
    START WITH 4
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.investments_seq OWNER TO postgres;

--
-- Name: quotes; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE quotes (
    datetime timestamp with time zone,
    quote numeric(18,6),
    id_quotes integer DEFAULT nextval(('"quotes_seq"'::text)::regclass) NOT NULL,
    id integer
);


ALTER TABLE public.quotes OWNER TO postgres;

--
-- Name: quotes_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE quotes_seq
    START WITH 5
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quotes_seq OWNER TO postgres;

--
-- Name: status; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE status (
    source text NOT NULL,
    process text NOT NULL,
    status text,
    internets integer DEFAULT 0,
    statuschange timestamp without time zone
);


ALTER TABLE public.status OWNER TO postgres;

--
-- Name: TABLE status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE status IS 'Tabla que contiene el estado de myquotesd, se borra al arrancar myquotesd y se va rellenando automáticamente';


--
-- Name: viewlast; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW viewlast AS
    SELECT investments.id, quote(investments.id, now()) AS quote FROM investments;


ALTER TABLE public.viewlast OWNER TO postgres;

--
-- Name: id_dividendospagos; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY dividendospagos ALTER COLUMN id_dividendospagos SET DEFAULT nextval('dividendospagos_id_dividendospagos_seq'::regclass);


--
-- Name: bolsas_pk; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY bolsas
    ADD CONSTRAINT bolsas_pk PRIMARY KEY (id_bolsas);


--
-- Name: dividendosestimaciones_pk; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY estimaciones
    ADD CONSTRAINT dividendosestimaciones_pk PRIMARY KEY (year, id);


--
-- Name: investments_pk; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY investments
    ADD CONSTRAINT investments_pk PRIMARY KEY (id);


--
-- Name: pk_globals; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY globals
    ADD CONSTRAINT pk_globals PRIMARY KEY (id_globals);


--
-- Name: pk_status; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY status
    ADD CONSTRAINT pk_status PRIMARY KEY (source, process);


--
-- Name: quotes_pk; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY quotes
    ADD CONSTRAINT quotes_pk PRIMARY KEY (id_quotes);


--
-- Name: dividendosestimaciones_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX dividendosestimaciones_id ON estimaciones USING btree (id);


--
-- Name: investments_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX investments_id ON investments USING btree (id);


--
-- Name: quotes_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX quotes_id ON quotes USING btree (id);


--
-- Name: quotes_id_datetime; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX quotes_id_datetime ON quotes USING btree (id, datetime);


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

--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

--
-- Data for Name: globals; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY globals (id_globals, global, value) FROM stdin;
1	Versión	20100101
2	Consultas a Internet desde inicio del sistema	0
3	Consultas a Internet en esta sessión	0
4	Sourceforge version	0
5	Fecha de inicio de la base de datos	2000-01-01
\.


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

--
-- Data for Name: investments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY investments (name, isin, currency, type, agrupations, active, id, web, address, phone, mail, tpc, pci, apalancado, id_bolsas, yahoo, priority, priorityhistorical, comentario, obsolete, deletable, system) FROM stdin;
CAJASUR MAXIMO GARANTIZADO	ES0164738033	EUR	2	|f_es_BMF|	f	74920					100	c	0	1	None	{2}	\N	ES0164738033||None||False	f	t	t
BK FUTURO IBEX	ES0114794037	EUR	2	|f_es_0055|f_es_BMF|	f	75063	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114794037||es||False	f	t	t
BK SECTOR FINANZAS	ES0114805031	EUR	2	|f_es_0055|f_es_BMF|	f	75127	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114805031||es||False	f	t	t
BK G.RESERVA 40 ANIVERSARIO IV G	ES0114830039	EUR	2	|f_es_0055|f_es_BMF|	f	75417	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114830039||es||False	f	t	t
CUENTA FISCAL ORO	ES0114869037	EUR	2	|f_es_0055|f_es_BMF|	f	75458	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114869037||es||False	f	t	t
BANKINTER DINERO 4	ES0127186031	EUR	2	|f_es_0055|f_es_BMF|	f	75580	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0127186031||es||False	f	t	t
BANKINTER EEUU GARANTIZADO	ES0114873039	EUR	2	|f_es_0055|f_es_BMF|	f	75581	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114873039||es||False	f	t	t
BK FONDVALENCIA MIXTO	ES0114803036	EUR	2	|f_es_0055|f_es_BMF|	f	75589	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114803036||es||False	f	t	t
BANKINTER ENERGIAS RENOVABLES	ES0114871033	EUR	2	|f_es_0055|f_es_BMF|	f	75590	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114871033||es||False	f	t	t
BK MIXTO ESPAÑA 30	ES0114804034	EUR	2	|f_es_0055|f_es_BMF|	f	75595	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114804034||es||False	f	t	t
BK MIXTO ESPAÑA 50	ES0114872031	EUR	2	|f_es_0055|f_es_BMF|	f	75605	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114872031||es||False	f	t	t
BANKINTER ESPANA GARANTIZADO	ES0114832035	EUR	2	|f_es_0055|f_es_BMF|	f	75630	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114832035||es||False	f	t	t
BANKINTER FONDT.40% LARGO PLAZO	ES0147624037	EUR	2	|f_es_0055|f_es_BMF|	f	75636	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147624037||es||False	f	t	t
FONCAIXA PRIVADA FONDO 25		EUR	2	|f_es_BMF|	f	75258					100	c	0	1	None	\N	\N	FONCAIXA PRIVADA FONDO 25||es||False	t	f	t
ERCROS	ES0125140A14	EUR	1	|MERCADOCONTINUO|	t	78886	\N	\N	\N	\N	100	c	0	1	ECR.MC	{1}	{3}	MC#ES0125140A14||es||False	f	f	t
BSN BANIF MULTIFONDOS PREMIER FIMF	\N	\N	\N	\N	f	75052	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	BSN BANIF MULTIFONDOS PREMIER FIMF||None||False	f	f	t
BSN INVERSIONES	\N	\N	\N	\N	f	75053	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	BSN INVERSIONES||None||False	f	f	t
MULTIFONDO2 BANCO PASTOR FIAMM	\N	EUR	\N	\N	f	75135	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MULTIFONDO2 BANCO PASTOR FIAMM||es||True	f	f	t
MULTIFONDO PASTOR FIAMM	\N	EUR	\N	\N	f	75136	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MULTIFONDO PASTOR FIAMM||es||True	f	f	t
BARCLAYS PLAN INVERSION 5	\N	EUR	\N	\N	f	75140	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	BARCLAYS PLAN INVERSION 5||es||True	f	f	t
RENTA 4 PREMIER	\N	EUR	\N	\N	f	75147	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	RENTA 4 PREMIER||es||True	f	f	t
BBV CARTERA SIMCAV	\N	EUR	\N	\N	f	75280	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	BBV CARTERA SIMCAV||es||True	f	f	t
MANUEL PASCUAL SALCEDO S.A.		EUR	1		f	-2					100	c	0	1	None	\N	\N	MANUEL PASCUAL SALCEDO||es||True	f	f	f
CONSULNOR MULTIGESTION ALTENATIVA	ES0123550008	EUR	2	|f_es_BMF|	f	74940					100	c	0	1	None	{2}	\N	ES0123550008||None||False	f	t	t
BANKINTER	ES0113679I37	EUR	1	|IBEX|MERCADOCONTINUO|	t	78412					100	c	0	1	BKT.MC	{1}	{3}	MC#ES0113679I37||es||False	f	f	t
ANTENA 3 TV.	ES0109427734	EUR	1	|MERCADOCONTINUO|	t	78384					100	c	0	1	A3TV.MC	{1}	{3}	MC#ES0109427734||es||False	f	f	t
DINAMIA	ES0126501131	EUR	1	|MERCADOCONTINUO|	f	78474	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0126501131||es||False	f	f	t
Call IBEX 35 inLine | 8000 € | 15/09/11 | I0027	FR0011038918	EUR	5	|SGW|	f	75205	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0027||fr||False	f	f	t
CUENTA FISCAL ORO I	ES0114862032	EUR	2	|f_es_0055|f_es_BMF|	f	76576	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114862032||es||False	f	t	t
BK DINERO	ES0114863030	EUR	2	|f_es_0055|f_es_BMF|	f	78273	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114863030||es||False	f	t	t
COPERNICO IICIICIL	ES0112481009	EUR	2	|f_es_BMF|	f	74942					100	c	0	1	None	{2}	\N	ES0112481009||None||False	f	t	t
Accretive Health Inc.	US00438V1035	USD	1		f	79287					100	c	0	2	AH	\N	\N	NYSE#AH||us||False	f	t	t
ACERINOX	ES0132105018	EUR	1	|IBEX|MERCADOCONTINUO|	t	78325					100	c	0	1	ACX.MC	{1}	{3}	MC#ES0132105018||es||False	f	f	t
F.P. FondBarclays Solidez II		EUR	8		f	75290					0	c	0	1	None	\N	\N	F.P. FondBarclays Solidez II||es||False	f	f	t
DEPOSITO BANKINTER		EUR	10		f	-3					0	c	0	1	None	\N	\N	DEPOSITO BANKINTER||es||True	f	f	f
Warrant Bonus Cap Telefónica 9.4 20121221	NL0009802602	EUR	5	|w_es_BNP|	t	74741					100	i	0	1	None	{5}	\N		f	f	t
WARRANT BONUS CAP PEUGEOT 7.07 20130315	NL0009976596	EUR	5	|w_es_BNP|	t	74742					100	i	0	1		{5}	\N		f	f	t
DERECHOS IBERDROLA		EUR	1		f	-8					100	c	0	1	None	\N	\N	DERECHOS IBERDROLA||None||False	f	f	f
BANKINTER IBEX TOP DIVIDENDO GAR	ES0133594038	EUR	2	|f_es_0055|f_es_BMF|	f	79495	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133594038||es||False	f	t	t
FONDO MULTISELECCION 100	ES0147606034	EUR	2	|f_es_0055|f_es_BMF|	f	79532	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147606034||es||False	f	t	t
FONDO MULTISELECCION 25	ES0180959035	EUR	2	|f_es_0055|f_es_BMF|	f	79533	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180959035||es||False	f	t	t
FONDO MULTISELECCION 50	ES0114762034	EUR	2	|f_es_0055|f_es_BMF|	f	79534	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114762034||es||False	f	t	t
FONDO IBEX GARANTIZADO 2010	ES0114833033	EUR	2	|f_es_0055|f_es_BMF|	f	79689	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114833033||es||False	f	t	t
FONDO BK SECTORES GARANTIZADO	ES0114792031	EUR	2	|f_es_0055|f_es_BMF|	f	79690	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114792031||es||False	f	t	t
BANKINTER TRIPLE INDICE GARANTIZ	ES0170276036	EUR	2	|f_es_0055|f_es_BMF|	f	80230	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170276036||es||False	f	t	t
FONDO BK EUROSTOXX 2012 GARANT.	ES0114839030	EUR	2	|f_es_0055|f_es_BMF|	f	80348	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114839030||es||False	f	t	t
DWS DINER II	ES0125788036	EUR	2	|f_es_BMF|	f	74974					100	c	0	1	None	{2}	\N	ES0125788036||None||False	f	t	t
Accuride Corp.	US00439T2069	USD	1		f	79854					100	c	0	2	ACW	{1}	{3}	NYSE#ACW||us||False	f	t	t
DWS CAPITAL III	ES0125775033	EUR	2	|f_es_BMF|	f	74972					100	c	0	1	None	{2}	\N	ES0125775033||None||False	f	t	t
AUREA	FR0000039232	EUR	1	|EURONEXT|	f	75379	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000039232||fr||False	f	t	t
\N	\N	\N	\N	\N	f	75681	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0130354006||None||False	f	t	t
Bunge Ltd.	\N	USD	1	\N	f	75393	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BG||us||False	f	t	t
PartnerRe Ltd.	\N	USD	1	\N	f	75847	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PRE||us||False	f	t	t
\N	\N	\N	\N	\N	f	76180	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0113824009||None||False	f	t	t
Corning Inc.	\N	USD	1	\N	f	77291	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GLW||us||False	f	t	t
Dril-Quip Inc.	\N	USD	1	\N	f	77438	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DRQ||us||False	f	t	t
\N	\N	\N	\N	\N	f	78061	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	NYSE#CRD||None||False	f	t	t
\N	\N	\N	\N	\N	f	78326	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0114561006||None||False	f	t	t
ABB Ltd.	\N	USD	1	\N	f	78545	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ABB||us||False	f	t	t
\N	\N	\N	\N	\N	f	78651	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0110253038||None||False	f	t	t
Universal Travel Group	\N	USD	1	\N	f	80494	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UTA||us||False	f	t	t
\N	\N	\N	\N	\N	f	81046	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0147102000||None||False	f	t	t
\N	\N	\N	\N	\N	f	81178	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0160990000||None||False	f	t	t
\N	\N	\N	\N	\N	f	81369	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0165144017||None||False	f	t	t
CAJABURGOS EURIBOR	ES0115454037	EUR	2	|BMF|0128|	f	74800	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115454037||es||False	f	t	t
PLUSMADRID 25	ES0170201034	EUR	2	|BMF|0085|	f	76355	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170201034||es||False	f	t	t
CONSULNOR AHORRO	ES0123541007	EUR	2	|BMF|0160|	f	78940	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0123541007||es||False	f	t	t
FIMAP	ES0137603009	EUR	2	|BMF|0182|	f	79162	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137603009||es||False	f	t	t
FONDONORTE	ES0138828035	EUR	2	|BMF|0009|	f	79746	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138828035||es||False	f	t	t
CS DIRECTOR BOND FOCUS	ES0165121031	EUR	2	|BMF|0173|	f	79989	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165121031||es||False	f	t	t
Boston Properties Inc.		USD	1	|SP500|	f	78306					100	c	0	2	BXP	{1}	{3}	NYSE#BXP||us||False	f	t	t
Boston Scientific Corp.		USD	1	|SP500|	f	75488					100	c	0	2	BSX	{1}	{3}	NYSE#BSX||us||False	f	t	t
Lyxor ETF EURO STOXX 50 Daily Leverage	FR0010468983	EUR	4	|e_fr_LYXOR|	t	81394					100	c	2	3	LVE.PA	{1}	{3}	LVE.PA||fr||False	f	f	t
BANESTO BOLSA INTERNACIONAL	ES0138917036	EUR	2	|BMF|0012|	f	76962	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138917036||es||False	f	f	t
FONCAIXA R.F.PRIVADA CORTO PLAZO	ES0137896033	EUR	2	|BMF|0015|	f	79743	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137896033||es||False	f	f	t
IBERCAJA DINERO	ES0147174033	EUR	2	|BMF|0084|	f	80001	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147174033||es||False	f	f	t
IBERCAJA AHORRO DINAMICO	ES0184002030	EUR	2	|BMF|0084|	f	80752	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184002030||es||False	f	f	t
Depósito Estructurado Bankinter		EUR	10		f	-9					100	i	0	1		\N	\N		f	f	f
MERRIL LINCH JAPAN OPORTUNITIES FUND		EUR	2		f	75042					100	c	0	1	None	\N	\N	MERRIL LINCH JAPAN OPORTUNITIES FUND||None||False	f	f	t
Telecomm Italia	IT0003497168	EUR	1	|EUROSTOXX|	f	75067					100	c	0	6	None	\N	\N	IT0003497168||None||False	f	f	t
LYXOR IBEX DOBLE APALANCADO	FR0011042753	EUR	4	|MERCADOCONTINUO|	t	79228					100	c	2	1	IBEXA.MC	{1}	\N	MC#FR0011042753||es||False	f	f	t
SABADELL BS SELECCION ALFA 1	ES0111187003	EUR	2	|f_es_BMF|	f	81423					100	c	0	1	None	{2}	\N	ES0111187003||None||False	f	t	t
Red Eléctrica Corporación	ES0173093115	EUR	1	|IBEX|MERCADOCONTINUO|	f	79359					100	c	0	1	REE.MC	{1}	{3}	MC#ES0173093115||es||False	f	f	t
SFN Group Corp.	\N	USD	1	\N	f	74793	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SFN||us||False	f	t	t
D.B.VALENCIA	ES06139809C2	EUR	1	|MERCADOCONTINUO|	f	74821	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES06139809C2||es||False	f	t	t
Pre-Paid Legal Services Inc.	\N	USD	1	\N	f	74816	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PPD||us||False	f	t	t
Euro Stox 50	\N	EUR	3	\N	t	75540	\N	\N	\N	\N	100	c	0	10	^STOXX50E	{1}	{3}	^STOXX50E||eu||False	f	t	t
Joyou AG	DE000A0WMLD8	EUR	1	|DEUTSCHEBOERSE|	f	74808	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0WMLD8||de||False	f	t	t
ESTORIL SOL P	PTESO0AE0000	EUR	1	|EURONEXT|	f	79206	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTESO0AE0000||pt||False	f	t	t
CIMPOR,SGPS	PTCPR0AM0003	EUR	1	|EURONEXT|	f	79372	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTCPR0AM0003||pt||False	f	t	t
SUMOL COMPAL	PTSML0AM0009	EUR	1	|EURONEXT|	f	79490	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTSML0AM0009||pt||False	f	t	t
GLINTT	PTPAD0AM0007	EUR	1	|EURONEXT|	f	79526	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTPAD0AM0007||pt||False	f	t	t
E.SANTO FIN.NOM	LU0202957089	EUR	1	|EURONEXT|	f	79629	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#LU0202957089||pt||False	f	t	t
IMOB.C GRAO PARA	PTGPA0AP0007	EUR	1	|EURONEXT|	f	79751	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTGPA0AP0007||pt||False	f	t	t
Jungheinrich AG	DE0006219934	EUR	1	|DEUTSCHEBOERSE|	f	74809	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006219934||de||False	f	t	t
DAX XETRA	DE0008469008	EUR	3	\N	t	78094	\N	\N	\N	\N	100	c	0	5	^GDAXI	{1}	{3}	^GDAXI||de||False	f	t	t
Colonia Real Estate AG 	DE0006338007	EUR	1	|DEUTSCHEBOERSE|	f	74845	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006338007||de||False	f	t	t
MBB INDUSTRIES AG	DE000A0ETBQ4	EUR	1	|DEUTSCHEBOERSE|	f	74849	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0ETBQ4||de||False	f	t	t
SYNAXON AG	DE0006873805	EUR	1	|DEUTSCHEBOERSE|	f	74851	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006873805||de||False	f	t	t
SolarWorld AG	DE0005108401	EUR	1	|DEUTSCHEBOERSE|	f	74888	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005108401||de||False	f	t	t
SOLON SE	DE0007471195	EUR	1	|DEUTSCHEBOERSE|	f	74900	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007471195||de||False	f	t	t
FTSE MIB	\N	EUR	3	\N	t	81082	\N	\N	\N	\N	100	c	0	6	FTSEMIB.MI	{1}	{3}	FTSEMIB.MI||it||False	f	t	t
China Mobile Ltd.	\N	USD	1	\N	f	74823	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CHL||us||False	f	t	t
TAM S/A	\N	USD	1	\N	f	74832	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TAM||us||False	f	t	t
Weatherford International Ltd.	\N	USD	1	\N	f	74787	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WFT||us||False	f	t	t
ABENGOA	ES0105200416	EUR	1	|IBEX|MERCADOCONTINUO|	t	81093					100	c	0	1	ABG.MC	{1}	{3}	MC#ES0105200416||es||False	f	t	t
BBVA 4-100 Ibex II FI	ES0113454039	EUR	2	|f_es_BMF|	f	74780					100	c	0	1	None	{2}	\N	ES0113454039||None||False	f	t	t
Altae Private Equity Index FI	ES0163027008	EUR	2	|f_es_BMF|	f	74773					100	c	0	1	None	{2}	\N	ES0163027008||None||False	f	t	t
UNIFOND 2016-III	ES0181398001	EUR	2	|f_es_BMF|	f	81380					100	c	0	1	None	{2}	\N	ES0181398001||None||False	f	t	t
Allianz SE	DE0008404005	EUR	1	|DAX|DEUTSCHEBOERSE|EUROSTOXX|	t	80515					100	c	0	5	ALV.DE	{1}	{3}	DEUTSCHEBOERSE#DE0008404005||de||False	f	f	t
INAPA-INV.P.GESTAO	PTINA0AP0008	EUR	1	|EURONEXT|	f	79761	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTINA0AP0008||pt||False	f	t	t
INAPA-PREF S/ VOTO	PTINA2VP0019	EUR	1	|EURONEXT|	f	79762	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTINA2VP0019||pt||False	f	t	t
B.ESPIRITO SANTO	PTBES0AM0007	EUR	1	|EURONEXT|	f	79963	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTBES0AM0007||pt||False	f	t	t
BANCO BPI	PTBPI0AM0004	EUR	1	|EURONEXT|	f	79971	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTBPI0AM0004||pt||False	f	t	t
MARTIFER	PTMFR0AM0003	EUR	1	|EURONEXT|	f	79991	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTMFR0AM0003||pt||False	f	t	t
BENFICA	PTSLB0AM0010	EUR	1	|EURONEXT|	f	80007	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTSLB0AM0010||pt||False	f	t	t
MOTA ENGIL	PTMEN0AE0005	EUR	1	|EURONEXT|	f	80060	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTMEN0AE0005||pt||False	f	t	t
S.COSTA	PTSCO0AE0004	EUR	1	|EURONEXT|	f	80074	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTSCO0AE0004||pt||False	f	t	t
S.COSTA-PREF	PTSCO0VE0009	EUR	1	|EURONEXT|	f	80075	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTSCO0VE0009||pt||False	f	t	t
VAA VISTA ALEGRE	PTVAA0AE0001	EUR	1	|EURONEXT|	f	80155	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTVAA0AE0001||pt||False	f	t	t
FMC Corp.	\N	USD	1	\N	f	74789	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FMC||us||False	f	t	t
CS RENTA VARIABLE INTER, CLASE B	ES0142538000	EUR	2	|f_es_BMF|	f	79996					100	c	0	1	None	{2}	\N	ES0142538000||None||False	f	t	t
Foncaixa Coop. Soc. Resp. Europa FI	ES0138074036	EUR	2	|f_es_BMF|	f	74978					100	c	0	1	None	{2}	\N	ES0138074036||None||False	f	t	t
Adidas AG	DE000A1EWWW0	EUR	1	|DEUTSCHEBOERSE|	t	80475					100	c	0	5	ADS.DE	{1}	{3}	DEUTSCHEBOERSE#DE000A1EWWW0||de||False	f	t	t
CARREFOUR S.A.	FR0010828137	EUR	1	|CAC|EURONEXT|EUROSTOXX|	f	80252					100	c	0	3	CA.PA	{1}	{3}	EURONEXT#FR0010828137||fr||False	f	t	t
Warrant Bonus Cap Societe Generale 9 20121221	NL0009976562	EUR	5	|w_es_BNP|	t	74745	\N	\N	\N	\N	100	i	0	1	\N	{5}	\N	\N	f	f	t
BBVA	ES0113211835	EUR	1	|EUROSTOXX|IBEX|MERCADOCONTINUO|	t	81112					100	c	0	1	BBVA.MC	{1}	{3}	MC#ES0113211835||es||True	f	f	t
IBERDROLA	ES0144580Y14	EUR	1	|EUROSTOXX|IBEX|MERCADOCONTINUO|	t	81347					100	c	0	1	IBE.MC	{1}	{3}	MC#ES0144580Y14||es||True	f	f	t
Wacker Chemie AG	DE000WCH8881	EUR	1	|DEUTSCHEBOERSE|	t	75852					100	c	0	5	WCH.DE	{1}	{3}	DEUTSCHEBOERSE#DE000WCH8881||de||False	f	t	t
MEDIASET	ES0152503035	EUR	1	|IBEX|MERCADOCONTINUO|	t	79223					100	c	0	1	TL5.MC	{1}	{3}	MC#ES0152503035||es||True	f	f	t
WARRANT BONUS CAP BANCO SANTANDER 3.8 20121221	NL0009802594	EUR	5	|w_es_BNP|	t	81678					100	i	0	1		{5}	\N	U0017	f	f	f
Autostrada	IT0000084027	EUR	1		f	74893					100	c	0	6	AT.MI	{1}	{3}	AT.MI||None||False	f	f	t
Altran technologies		EUR	1		f	74892					100	c	0	5	None	\N	\N	ATC.DE||None||False	t	f	t
Nasdaq 100	US6311011026	USD	3	\N	t	79788	\N	\N	\N	\N	100	c	0	2	^NDX	{1}	{3}	^NDX||us||False	f	t	t
Call IBEX 35 inLine | 8000 € | 14/12/11 | I0038	FR0011081363	EUR	5	|SGW|	f	74846	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0038||fr||False	f	t	t
Call IBEX 35 | 10000 € | 21/09/12 | C3292	FR0011168327	EUR	5	|SGW|	f	74850	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3292||fr||False	f	t	t
Fondespaña Catedrales FI	ES0138442035	EUR	2	|f_es_BMF|	f	74979					100	c	0	1	None	{2}	\N	ES0138442035||None||False	f	t	t
WARRANT BONUS CAP BANCO POPULAR 1.75 20130315	NL0009976588	EUR	5	|w_es_BNP|	t	81677					100	i	1	1		{5}	\N	u0023	f	t	f
CRH PLC	IE0001827041	EUR	1	|EUROSTOXX|	f	81085					100	c	0	13	CRG.IR	{1}	{3}	CRG.IR||ie||False	f	t	t
NATUREX	FR0000054694	EUR	1	|EURONEXT|	f	79468	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000054694||fr||False	f	t	t
PLASTIC OMNIUM	FR0000124570	EUR	1	|EURONEXT|	f	79484	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000124570||fr||False	f	t	t
SCOR SE	FR0010411983	EUR	1	|EURONEXT|	f	79489	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010411983||fr||False	f	t	t
APRR	FR0006807004	EUR	1	|EURONEXT|	f	79509	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0006807004||fr||False	f	t	t
AREVA	FR0011027143	EUR	1	|EURONEXT|	f	79510	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011027143||fr||False	f	t	t
GENERAL ELECTRIC	US3696041033	EUR	1	|EURONEXT|	f	79516	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US3696041033||fr||False	f	t	t
GENERALE DE SANTE	FR0000044471	EUR	1	|EURONEXT|	f	79517	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000044471||fr||False	f	t	t
DEVOTEAM BSAR1112	FR0010379529	EUR	1	|EURONEXT|	f	79553	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010379529||fr||False	f	t	t
FONDESPAÑA CRECIMIENTO	ES0138538030	EUR	2	|f_es_BMF|	f	74980					100	c	0	1	None	{2}	\N	ES0138538030||None||False	f	t	t
Deutsche Bank AG	DE0005140008	EUR	1	|DAX|DEUTSCHEBOERSE|EUROSTOXX|	f	79513					100	c	0	5	DBK.DE	{1}	{3}	DEUTSCHEBOERSE#DE0005140008||de||False	f	t	t
LA FONCIERE VERTE	FR0000039638	EUR	1	|EURONEXT|	f	79890	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000039638||fr||False	f	t	t
RIBER	FR0000075954	EUR	1	|EURONEXT|	f	79891	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000075954||fr||False	f	t	t
ASSYSTEM	FR0000074148	EUR	1	|EURONEXT|	f	79920	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000074148||fr||False	f	t	t
ATARI	FR0010478248	EUR	1	|EURONEXT|	f	79923	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010478248||fr||False	f	t	t
ATOS	FR0000051732	EUR	1	|EURONEXT|	f	79925	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000051732||fr||False	f	t	t
Deutsche Börse AG	DE0005810055	EUR	1	|DAX|DEUTSCHEBOERSE|EUROSTOXX|	f	79520					100	c	0	5	DB1.DE	{1}	{3}	DEUTSCHEBOERSE#DE0005810055||de||False	f	t	t
LEXIBOOK LINGUIST.	FR0000033599	EUR	1	|EURONEXT|	f	80205	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000033599||fr||False	f	t	t
Call IBEX 35 | 10250 € | 20/04/12 | C2132	FR0011145408	EUR	5	|SGW|	f	80208	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C2132||fr||False	f	t	t
Call IBEX 35 | 7000 € | 15/06/12 | B9955	FR0011091446	EUR	5	|SGW|	f	80210	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9955||fr||False	f	t	t
Call IBEX 35 | 7500 € | 15/06/12 | B9956	FR0011091453	EUR	5	|SGW|	f	80211	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9956||fr||False	f	t	t
CLUB MEDITERRANEE	FR0000121568	EUR	1	|EURONEXT|	f	80215	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000121568||fr||False	f	t	t
GL EVENTS	FR0000066672	EUR	1	|EURONEXT|	f	80218	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000066672||fr||False	f	t	t
Deutsche Telekom AG	DE0005557508	EUR	1	|DAX|DEUTSCHEBOERSE|EUROSTOXX|	f	79592					100	c	0	5	DTE.DE	{1}	{3}	DEUTSCHEBOERSE#DE0005557508||de||False	f	t	t
FAYENC.SARREGUEMI.	FR0000031973	EUR	1	|EURONEXT|	f	80440	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000031973||fr||False	f	t	t
ENEL	IT0003128367	EUR	1	|EUROSTOXX|	f	75450					100	c	0	6	ENEL.MI	{1}	{3}	ENEL.MI||it||False	f	t	t
OSIATIS	FR0004044337	EUR	1	|EURONEXT|	f	80722	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004044337||fr||False	f	t	t
Call IBEX 35 | 9750 € | 20/01/12 | B9695	FR0011083740	EUR	5	|SGW|	f	80724	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9695||fr||False	f	t	t
OVERLAP GROUPE	FR0010759530	EUR	1	|EURONEXT|	f	80725	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010759530||fr||False	f	t	t
Franklin Resources Inc.	\N	USD	1	\N	f	74933	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BEN||us||False	f	t	t
DWS VALOR GLOBAL	ES0142392036	EUR	2	|f_es_BMF|	f	74976					100	c	0	1	None	{2}	\N	ES0142392036||None||False	f	t	t
Eurovalencia Ahorro FI	ES0133573032	EUR	2	|f_es_BMF|	f	74977					100	c	0	1	None	{2}	\N	ES0133573032||None||False	f	t	t
Fondocaja Garantizado Futuro I FI	ES0138229036	EUR	2	|f_es_BMF|	f	74982					100	c	0	1	None	{2}	\N	ES0138229036||None||False	f	t	t
Carmignac Euro-Patrimoine	FR0010149179	EUR	2	|CARMIGNAC|	f	81463	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	FR0010149179||fr||False	f	t	t
Carmignac Market Neutral	LU0413372060	EUR	2	|CARMIGNAC|	f	81464	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	LU0413372060||fr||False	f	t	t
Carmignac Investissement (A)	FR0010148981	EUR	2	|CARMIGNAC|	f	81472	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	FR0010148981||fr||False	f	t	t
\N	\N	\N	\N	\N	f	75023	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0159126038||None||False	f	t	t
\N	\N	\N	\N	\N	f	75024	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0158981037||None||False	f	t	t
\N	\N	\N	\N	\N	f	75025	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0147509030||None||False	f	t	t
Call IBEX 35 | 12000 € | 16/03/12 | B7613	FR0011058494	EUR	5	|SGW|	f	75031	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7613||fr||False	f	t	t
GRPE PARTOUCHE DS	FR0011040377	EUR	1	|EURONEXT|	f	75043	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011040377||fr||False	f	t	t
Call IBEX 35 | 10500 € | 16/12/11 | B5142	FR0011002765	EUR	5	|SGW|	f	75114	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B5142||fr||False	f	t	t
\N	\N	\N	\N	\N	f	75106	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0173373038||None||False	f	t	t
\N	\N	\N	\N	\N	f	75108	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0174476038||None||False	f	t	t
\N	\N	\N	\N	\N	f	75109	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0138926037||None||False	f	t	t
\N	\N	\N	\N	\N	f	75111	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0177997030||None||False	f	t	t
\N	\N	\N	\N	\N	f	75112	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0177998038||None||False	f	t	t
\N	\N	\N	\N	\N	f	75113	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0177962034||None||False	f	t	t
\N	\N	\N	\N	\N	f	75492	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	NYSE#KV||None||False	f	t	t
IVU Traffic Technologies AG	DE0007448508	EUR	1	|DEUTSCHEBOERSE|	f	80322	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007448508||de||False	f	t	t
JAXX SE	DE000A0JRU67	EUR	1	|DEUTSCHEBOERSE|	f	80323	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0JRU67||de||False	f	t	t
Electricité de France	FR0010242511	EUR	1	|CAC|	f	75212	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EDF.PA||fr||False	f	t	t
Call IBEX 35 | 9500 € | 16/03/12 | B7615	FR0011058445	EUR	5	|SGW|	f	75281	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7615||fr||False	f	t	t
INTERHYP AG	DE0005121701	EUR	1	|DEUTSCHEBOERSE|	f	75282	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005121701||de||False	f	t	t
METRO AG Vz	DE0007257537	EUR	1	|DEUTSCHEBOERSE|	f	80856	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007257537||de||False	f	t	t
paragon AG	DE0005558696	EUR	1	|DEUTSCHEBOERSE|	f	80858	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005558696||de||False	f	t	t
SAF-HOLLAND S.A.	LU0307018795	EUR	1	|DEUTSCHEBOERSE|	f	80864	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#LU0307018795||de||False	f	t	t
First Sensor AG	DE0007201907	EUR	1	|DEUTSCHEBOERSE|	f	81176	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007201907||de||False	f	t	t
Funkwerk AG	DE0005753149	EUR	1	|DEUTSCHEBOERSE|	f	81184	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005753149||de||False	f	t	t
IBS AG	DE0006228406	EUR	1	|DEUTSCHEBOERSE|	f	81272	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006228406||de||False	f	t	t
KOENIG & BAUER AG	DE0007193500	EUR	1	|DEUTSCHEBOERSE|	f	81274	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007193500||de||False	f	t	t
Kontron AG	DE0006053952	EUR	1	|DEUTSCHEBOERSE|	f	81278	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006053952||de||False	f	t	t
McGraw-Hill Cos.	\N	USD	1	\N	f	79040	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MHP||us||False	f	t	t
Mohawk Industries Inc.	\N	USD	1	\N	f	79043	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MHK||us||False	f	t	t
Seaspan Corp.	\N	USD	1	\N	f	79404	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SSW||us||False	f	t	t
Vina Concha y Toro S.A.	\N	USD	1	\N	f	79409	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VCO||us||False	f	t	t
CRCAM ALP.PROV.CCI	FR0000044323	EUR	1	|EURONEXT|	f	75598	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000044323||fr||False	f	t	t
Stage Stores Inc.	\N	USD	1	\N	f	79692	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SSI||us||False	f	t	t
Call IBEX 35 | 7750 € | 21/10/11 | B9931	FR0011091206	EUR	5	|SGW|	f	75645	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9931||fr||False	f	t	t
TESSI	FR0004529147	EUR	1	|EURONEXT|	f	75646	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004529147||fr||False	f	t	t
HHGregg Inc.	\N	USD	1	\N	f	79901	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HGG||us||False	f	t	t
Demand Media Inc.	\N	USD	1	\N	f	79902	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DMD||us||False	f	t	t
Trex Co. Inc.	\N	USD	1	\N	f	80946	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TREX||us||False	f	t	t
Promotora de Informaciones S.A. Cl A	\N	USD	1	\N	f	80947	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PRIS||us||False	f	t	t
DELHAIZE GROUP	BE0003562700	EUR	1	|EURONEXT|	f	75884	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003562700||be||False	f	t	t
Youbisheng Green Paper AG 	DE000A1KRLR0	EUR	1	|DEUTSCHEBOERSE|	f	75914	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1KRLR0||de||False	f	t	t
ICICI Bank Ltd.	\N	USD	1	\N	f	75348	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IBN||us||False	f	t	t
West Pharmaceutical Services Inc.	\N	USD	1	\N	f	81611	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WST||us||False	f	t	t
\N	\N	\N	\N	\N	f	75992	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0114022009||None||False	f	t	t
Chicago Bridge & Iron Co. N.V.	\N	USD	1	\N	f	75586	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CBI||us||False	f	t	t
Magna International Inc.	\N	USD	1	\N	f	75527	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MGA||us||False	f	t	t
VMware Inc.	\N	USD	1	\N	f	75543	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VMW||us||False	f	t	t
Celanese Corp. Series A	\N	USD	1	\N	f	75544	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CE||us||False	f	t	t
\N	\N	\N	\N	\N	f	76033	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0146792017||None||False	f	t	t
Toll Brothers Inc.	\N	USD	1	\N	f	75726	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TOL||us||False	f	t	t
Goodyear Tire & Rubber Co.	\N	USD	1	\N	f	75727	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GT||us||False	f	t	t
General Electric Co.	\N	USD	1	\N	f	75728	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GE||us||False	f	t	t
Valero Energy Corp.	\N	USD	1	\N	f	75731	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VLO||us||False	f	t	t
FIAT SPA EPAR.RGP	IT0001976429	EUR	1	|EURONEXT|	f	76131	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#IT0001976429||fr||False	f	t	t
FIAT SPA PRIV.RGP	IT0001976411	EUR	1	|EURONEXT|	f	76138	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#IT0001976411||fr||False	f	t	t
GROUPE PARTOUCHE	FR0000053548	EUR	1	|EURONEXT|	f	76139	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000053548||fr||False	f	t	t
\N	\N	\N	\N	\N	f	76130	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	NYSE#JW||None||False	f	t	t
Thompson Creek Metals Co. Inc.	\N	USD	1	\N	f	76093	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TC||us||False	f	t	t
Sovran Self Storage Inc.	\N	USD	1	\N	f	76095	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SSS||us||False	f	t	t
WMS Industries Inc.	\N	USD	1	\N	f	76096	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WMS||us||False	f	t	t
Equity One Inc.	\N	USD	1	\N	f	76097	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EQY||us||False	f	t	t
CORTICEIRA AMORIM	PTCOR0AE0006	EUR	1	|EURONEXT|	f	76267	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTCOR0AE0006||pt||False	f	t	t
AXWAY SOFTWARE	FR0011040500	EUR	1	|EURONEXT|	f	76263	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011040500||fr||False	f	t	t
TransAtlantic Holdings Inc.	\N	USD	1	\N	f	76243	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TRH||us||False	f	t	t
Ross Stores Inc.	\N	USD	1	|NASDAQ100|	f	76372	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	ROST||us||False	f	t	t
ATTIJARIWAFA BANK	MA0000011827	EUR	1	|EURONEXT|	f	76500	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#MA0000011827||fr||False	f	t	t
Hanesbrands Inc.	\N	USD	1	\N	f	76477	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HBI||us||False	f	t	t
Put IBEX 35 | 9000 € | 16/09/11 | B4748	FR0010984666	EUR	5	|SGW|	f	76605	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4748||fr||False	f	t	t
RTI International Metals Inc.	\N	USD	1	\N	f	76685	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RTI||us||False	f	t	t
Jarden Corp.	\N	USD	1	\N	f	76698	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JAH||us||False	f	t	t
Teradyne Inc.	\N	USD	1	\N	f	76699	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TER||us||False	f	t	t
Nu Skin Enterprises Inc. Cl A	\N	USD	1	\N	f	76700	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NUS||us||False	f	t	t
Babcock & Wilcox Co.	\N	USD	1	\N	f	76702	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BWC||us||False	f	t	t
TECHNICOLOR	FR0010918292	EUR	1	|EURONEXT|	f	76812	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010918292||fr||False	f	t	t
THROMBOGENICS	BE0003846632	EUR	1	|EURONEXT|	f	76814	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003846632||be||False	f	t	t
Kinetic Concepts Inc.	\N	USD	1	\N	f	76894	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KCI||us||False	f	t	t
Sysco Corp.	\N	USD	1	\N	f	76895	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SYY||us||False	f	t	t
Annaly Capital Management Inc.	\N	USD	1	\N	f	76896	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NLY||us||False	f	t	t
Marsh & McLennan Cos.	\N	USD	1	\N	f	76898	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MMC||us||False	f	t	t
VEOLIA NV	FR0010979492	EUR	1	|EURONEXT|	f	77012	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010979492||fr||False	f	t	t
RUE DU COMMERCE	FR0004053338	EUR	1	|EURONEXT|	f	77015	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004053338||fr||False	f	t	t
STAG Industrial Inc.	\N	USD	1	\N	f	77016	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STIR||us||False	f	t	t
Moody's Corp.	\N	USD	1	\N	f	77018	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MCO||us||False	f	t	t
Molson Coors Brewing Co. Cl B	\N	USD	1	\N	f	77022	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TAP||us||False	f	t	t
Alliant Energy Corp.	\N	USD	1	\N	f	77121	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LNT||us||False	f	t	t
Call IBEX 35 | 9500 € | 16/09/11 | B4739	FR0010984575	EUR	5	|SGW|	f	77250	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4739||fr||False	f	t	t
SBM OFFSHORE	NL0000360618	EUR	1	|EURONEXT|	f	77238	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000360618||nl||False	f	t	t
SOPHEON	GB0006932171	EUR	1	|EURONEXT|	f	77246	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GB0006932171||nl||False	f	t	t
Chiquita Brands International Inc.	\N	USD	1	\N	f	77224	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CQB||us||False	f	t	t
Emergent Biosolutions Inc.	\N	USD	1	\N	f	77231	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EBS||us||False	f	t	t
America Movil S.A.B. de C.V.	\N	USD	1	\N	f	77349	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AMX||us||False	f	t	t
Morgan Stanley	\N	USD	1	\N	f	77352	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MS||us||False	f	t	t
Cummins Inc.	\N	USD	1	\N	f	77353	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CMI||us||False	f	t	t
NVIDIA Corporation	\N	USD	1	|NASDAQ100|	f	77502	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NVDA||us||False	f	t	t
Vertex Pharmaceuticals Incorporated	US92532F1003	USD	1	|NASDAQ100|	f	77503	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	VRTX||us||False	f	t	t
El Paso Corp.	\N	USD	1	\N	f	77481	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EP||us||False	f	t	t
QEP Resources Inc.	\N	USD	1	\N	f	79132	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#QEP||us||False	f	t	t
DUVEL MOORTGAT	BE0003762763	EUR	1	|EURONEXT|	f	77520	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003762763||be||False	f	t	t
GENERAL ELECT.CERT	BE0004399342	EUR	1	|EURONEXT|	f	77522	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0004399342||be||False	f	t	t
MERCIALYS	FR0010241638	EUR	1	|EURONEXT|	f	77638	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010241638||fr||False	f	t	t
MERSEN	FR0000039620	EUR	1	|EURONEXT|	f	77639	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000039620||fr||False	f	t	t
Reed Elsevier PLC	\N	USD	1	\N	f	77728	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RUK||us||False	f	t	t
POSCO	\N	USD	1	\N	f	77998	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PKX||us||False	f	t	t
Put IBEX 35 | 10000 € | 15/06/12 | B9972	FR0011091610	EUR	5	|SGW|	f	78044	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9972||fr||False	f	t	t
LEO CAPITAL GROWTH	KYG545791009	EUR	1	|EURONEXT|	f	78040	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#KYG545791009||nl||False	f	t	t
Lender Processing Services Inc.	\N	USD	1	\N	f	78024	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LPS||us||False	f	t	t
Greenhill & Co. Inc.	\N	USD	1	\N	f	78025	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GHL||us||False	f	t	t
Call IBEX 35 inLine | 6500 € | 14/03/12 | I0047	FR0011117662	EUR	5	|SGW|	f	78140	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0047||fr||False	f	t	t
Westlake Chemical Corp.	\N	USD	1	\N	f	78112	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WLK||us||False	f	t	t
BAM CONV.PREF	NL0000337335	EUR	1	|EURONEXT|	f	78214	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000337335||nl||False	f	t	t
\N	\N	\N	\N	\N	f	78215	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0157935000||None||False	f	t	t
DXESTX5D	LU0274211217	EUR	1	|MERCADOCONTINUO|	f	78219	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0274211217||es||False	f	t	t
\N	\N	\N	\N	\N	f	78299	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0110012004||None||False	f	t	t
Molina Healthcare Inc.	\N	USD	1	\N	f	78280	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MOH||us||False	f	t	t
AAR Corp.	\N	USD	1	\N	f	78283	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AIR||us||False	f	t	t
Deltic Timber Corp.	\N	USD	1	\N	f	78290	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DEL||us||False	f	t	t
Rite Aid Corp.	\N	USD	1	\N	f	78295	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RAD||us||False	f	t	t
Textron Inc.	\N	USD	1	\N	f	78370	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TXT||us||False	f	t	t
CDI Corp.	\N	USD	1	\N	f	78373	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CDI||us||False	f	t	t
\N	\N	\N	\N	\N	f	78382	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0164529002||None||False	f	t	t
SEMAPA	PTSEM0AM0004	EUR	1	|EURONEXT|	f	78495	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTSEM0AM0004||pt||False	f	t	t
Level 3 Communications Inc.	\N	USD	1	\N	f	78531	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LVLT||us||False	f	t	t
FONCIERE VOLTA	FR0000053944	EUR	1	|EURONEXT|	f	78606	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000053944||fr||False	f	t	t
FORD MOTOR	US3453708600	EUR	1	|EURONEXT|	f	78607	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US3453708600||fr||False	f	t	t
Steelcase Inc. Cl A	\N	USD	1	\N	f	78703	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SCS||us||False	f	t	t
La-Z-Boy Inc.	\N	USD	1	\N	f	78712	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LZB||us||False	f	t	t
Nucor Corp.	\N	USD	1	\N	f	78777	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NUE||us||False	f	t	t
CGI Group Inc. Cl A	\N	USD	1	\N	f	78779	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GIB||us||False	f	t	t
Cosan  Cl A	\N	USD	1	\N	f	78871	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CZZ||us||False	f	t	t
Community Health Systems Inc.	\N	USD	1	\N	f	78874	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CYH||us||False	f	t	t
Call IBEX 35 | 8000 € | 15/06/12 | B9957	FR0011091461	EUR	5	|SGW|	f	78891	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9957||fr||False	f	t	t
Pier 1 Imports Inc.	\N	USD	1	\N	f	78882	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PIR||us||False	f	t	t
Haemonetics Corp.	\N	USD	1	\N	f	78883	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HAE||us||False	f	t	t
ENEL G.P.	IT0004618465	EUR	1	|MERCADOCONTINUO|	f	78881	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#IT0004618465||es||False	f	t	t
ENERSIS	CLP371861061	EUR	1	|MERCADOCONTINUO|	f	78885	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#CLP371861061||es||False	f	t	t
Rollins Inc.	\N	USD	1	\N	f	79102	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ROL||us||False	f	t	t
International Rectifier Corp.	\N	USD	1	\N	f	79104	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IRF||us||False	f	t	t
LYXETFWORDWA	FR0010527275	EUR	1	|MERCADOCONTINUO|	f	79210	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010527275||es||False	f	t	t
MAPFRE D09	ES0624244945	EUR	1	|MERCADOCONTINUO|	f	79215	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0624244945||es||False	f	t	t
LYXIBEX2INVE	FR0011036268	EUR	1	|MERCADOCONTINUO|	f	79217	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0011036268||es||False	f	t	t
VOPAK	NL0009432491	EUR	1	|EURONEXT|	f	79276	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009432491||nl||False	f	t	t
MARTINSA-FAD	ES0161376019	EUR	1	|MERCADOCONTINUO|	f	79221	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0161376019||es||False	f	t	t
PROSEGUR	ES0175438235	EUR	1	|MERCADOCONTINUO|	f	79356	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0175438235||es||False	f	t	t
KBC STRIP	BE0005538096	EUR	1	|EURONEXT|	f	79294	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005538096||be||False	f	t	t
NYRSTAR STRIP (D)	BE0005644183	EUR	1	|EURONEXT|	f	79303	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005644183||be||False	f	t	t
RadioShack Corp.	\N	USD	1	\N	f	79368	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RSH||us||False	f	t	t
Elster Group SE	\N	USD	1	\N	f	79453	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ELT||us||False	f	t	t
Procter & Gamble Co.	\N	USD	1	\N	f	79460	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PG||us||False	f	t	t
BP PLC	\N	USD	1	\N	f	79462	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BP||us||False	f	t	t
FONC.DES REGIONS	FR0000064578	EUR	1	|EURONEXT|	f	79438	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064578||fr||False	f	t	t
SAFT	FR0010208165	EUR	1	|EURONEXT|	f	79487	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010208165||fr||False	f	t	t
EUROVALOR AHORRO GARAN.CLASE A	ES0133563009	EUR	2	|f_es_BMF|	f	80182					100	c	0	1	None	{2}	\N	ES0133563009||None||False	f	t	t
Gruma S.A.B. de C.V.	\N	USD	1	\N	f	79970	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GMK||us||False	f	t	t
elexis AG	DE0005085005	EUR	1	|DEUTSCHEBOERSE|	f	80173	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005085005||de||False	f	t	t
Marcus Corp.	\N	USD	1	\N	f	80326	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MCS||us||False	f	t	t
Inphi Corp.	\N	USD	1	\N	f	80339	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IPHI||us||False	f	t	t
Alamo Group Inc.	\N	USD	1	\N	f	80353	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ALG||us||False	f	t	t
Advanced Vision Technology Ltd.	IL0010837248	EUR	1	|DEUTSCHEBOERSE|	f	80481	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#IL0010837248||de||False	f	t	t
Orad Hi-Tec Systems Ltd.	IL0010838071	EUR	1	|DEUTSCHEBOERSE|	f	80678	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#IL0010838071||de||False	f	t	t
Pfleiderer AG	DE0006764749	EUR	1	|DEUTSCHEBOERSE|	f	80680	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006764749||de||False	f	t	t
\N	\N	\N	\N	\N	f	80835	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0146758018||None||False	f	t	t
SHW AG	DE000A1JBPV9	EUR	1	|DEUTSCHEBOERSE|	f	80919	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1JBPV9||de||False	f	t	t
Singulus Technologies AG	DE0007238909	EUR	1	|DEUTSCHEBOERSE|	f	80921	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007238909||de||False	f	t	t
SinnerSchrader AG	DE0005141907	EUR	1	|DEUTSCHEBOERSE|	f	80922	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005141907||de||False	f	t	t
Sixt AG St	DE0007231326	EUR	1	|DEUTSCHEBOERSE|	f	80923	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007231326||de||False	f	t	t
Sixt AG Vz	DE0007231334	EUR	1	|DEUTSCHEBOERSE|	f	80924	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007231334||de||False	f	t	t
\N	\N	\N	\N	\N	f	81062	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0175420001||None||False	f	t	t
AUX.FERROCAR	ES0121975017	EUR	1	|MERCADOCONTINUO|	f	81102	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0121975017||es||False	f	t	t
BA.VALENCIA	ES0113980F34	EUR	1	|MERCADOCONTINUO|	f	81106	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0113980F34||es||False	f	t	t
BANCA CIVICA	ES0148873005	EUR	1	|MERCADOCONTINUO|	f	81110	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0148873005||es||False	f	t	t
SANTANDER SELEC.PREM.EUROPA	ES0114315031	EUR	2	|BMF|0012|	f	81053	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114315031||es||False	f	t	t
\N	\N	\N	\N	\N	f	81121	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0147050001||None||False	f	t	t
SAG GEST	PTSAG0AE0004	EUR	1	|EURONEXT|	f	81151	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTSAG0AE0004||pt||False	f	t	t
SALVEPAR	FR0000124356	EUR	1	|EURONEXT|	f	81152	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000124356||fr||False	f	t	t
TIE HOLDING	NL0000386985	EUR	1	|EURONEXT|	f	81253	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000386985||nl||False	f	t	t
Francotyp-Postalia Holding AG	DE000FPH9000	EUR	1	|DEUTSCHEBOERSE|	f	81153	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000FPH9000||de||False	f	t	t
Heliad Equity Partners GmbH & Co. KGaA	DE000A0L1NN5	EUR	1	|DEUTSCHEBOERSE|	f	81266	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0L1NN5||de||False	f	t	t
Henkel AG & Co. KGaA Vz	DE0006048432	EUR	1	|DEUTSCHEBOERSE|	f	81269	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006048432||de||False	f	t	t
LYXDOWJIAETF	FR0007056841	EUR	1	|MERCADOCONTINUO|	f	81359	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0007056841||es||False	f	t	t
LYXETFMSCIWL	FR0010315770	EUR	1	|MERCADOCONTINUO|	f	81505	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010315770||es||False	f	t	t
Aaron's Inc.	\N	USD	1	\N	f	81598	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AAN||us||False	f	t	t
CAJA INGENIEROS 2013 GARANTIZADO	ES0119487009	EUR	2	|BMF|0193|	f	74795	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0119487009||es||False	f	t	t
CAIXASABADELL 7 R.V.	ES0142545039	EUR	2	|BMF|0128|	f	75117	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142545039||es||False	f	t	t
CAJA INGENIEROS 2012 2E GARANT.	ES0119486001	EUR	2	|BMF|0193|	f	75118	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0119486001||es||False	f	t	t
CAJASOL FONDOSUR	ES0138942034	EUR	2	|BMF|0128|	f	75289	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138942034||es||False	f	t	t
ALTAE INSTITUCIONES	ES0108903032	EUR	2	|BMF|0085|	f	75291	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108903032||es||False	f	t	t
CAJA MURCIA FONDEPOSITO PLUS	ES0158949034	EUR	2	|BMF|0128|	f	75300	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158949034||es||False	f	t	t
KUTXASEG1	ES0157028038	EUR	2	|BMF|0086|	f	75425	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157028038||es||False	f	t	t
AVIVA CORTO PLAZO	ES0170156030	EUR	2	|BMF|0191|	f	75558	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170156030||es||False	f	t	t
CAIXASABADELL PROTECCIO V	ES0169079037	EUR	2	|BMF|0128|	f	75699	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169079037||es||False	f	t	t
BANKOA 5 ESTRELLAS GARANTIZADO, FI	ES0113966032	EUR	2	|BMF|0035|	f	75703	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113966032||es||False	f	t	t
EUROVALOR GARANTIZADO ORO	ES0133580003	EUR	2	|BMF|0004|	f	75708	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133580003||es||False	f	t	t
EUROVALOR MIXTO-15	ES0138987039	EUR	2	|BMF|0004|	f	75710	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138987039||es||False	f	t	t
FONGARANTIA EUROPA	ES0158772030	EUR	2	|BMF|0113|	f	75711	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158772030||es||False	f	t	t
EUROVALOR PATRIMONIO	ES0133617037	EUR	2	|BMF|0004|	f	75714	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133617037||es||False	f	t	t
BANCA CIVICA AVANZA	ES0165545031	EUR	2	|BMF|0071|	f	75860	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165545031||es||False	f	t	t
FONCAIXA 55 BOLSA JAPON	ES0122056031	EUR	2	|BMF|0015|	f	75861	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122056031||es||False	f	t	t
FONCAIXA 65 BOLSA INDICE ESPAñA	ES0138392032	EUR	2	|BMF|0015|	f	75862	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138392032||es||False	f	t	t
IBERCAJA FONDTESORO CORTO PLAZO	ES0147177036	EUR	2	|BMF|0084|	f	75960	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147177036||es||False	f	t	t
MADRID TELECOMUNICACIONES GLOBAL	ES0159131038	EUR	2	|BMF|0085|	f	75975	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159131038||es||False	f	t	t
BANIF BOLSA GARANTIZADO	ES0164649032	EUR	2	|BMF|0012|	f	75990	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164649032||es||False	f	t	t
BANKPYME MULTI TOP FUNDS	ES0110056035	EUR	2	|BMF|0024|	f	75997	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110056035||es||False	f	t	t
BANKPYME MULTIDINERO	ES0165101033	EUR	2	|BMF|0024|	f	75998	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165101033||es||False	f	t	t
BBK CRECIMIENTO DINAMICO	ES0114381033	EUR	2	|BMF|0095|	f	75999	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114381033||es||False	f	t	t
FONDO VALENCIA LIQUIDEZ D.PUBLIC	ES0139780003	EUR	2	|BMF|0083|	f	76000	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0139780003||es||False	f	t	t
IBERCAJA FUTURO	ES0147185039	EUR	2	|BMF|0084|	f	76001	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147185039||es||False	f	t	t
IBERCAJA FUTURO, CLASE B	ES0147185005	EUR	2	|BMF|0084|	f	76002	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147185005||es||False	f	t	t
Total System Services Inc.	\N	USD	1	\N	f	76430	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TSS||us||False	f	t	t
IBERCAJA RENTA EUROPA	ES0147146031	EUR	2	|BMF|0084|	f	76103	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147146031||es||False	f	t	t
IBERCAJA RENTA FIJA 1 AÑO 1	ES0147045001	EUR	2	|BMF|0084|	f	76104	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147045001||es||False	f	t	t
IBERCAJA RENTA FIJA 1 AÑO 2	ES0147046009	EUR	2	|BMF|0084|	f	76106	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147046009||es||False	f	t	t
IBERCAJA RENTA FIJA 2014	ES0147025003	EUR	2	|BMF|0084|	f	76107	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147025003||es||False	f	t	t
IBERCAJA RENTA INTERNACIONAL	ES0102564038	EUR	2	|BMF|0084|	f	76110	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0102564038||es||False	f	t	t
BARCLAYS BOLSA ESPAñA SELECCION	ES0114180039	EUR	2	|BMF|0063|	f	76133	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114180039||es||False	f	t	t
BARCLAYS BONOS CORPORATIVOS	ES0114166038	EUR	2	|BMF|0063|	f	76134	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114166038||es||False	f	t	t
CAIXAGIRONA EUROBORSA	ES0142470030	EUR	2	|BMF|0006|	f	76141	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142470030||es||False	f	t	t
BARCLAYS GARANTIZADO 19	ES0133756033	EUR	2	|BMF|0063|	f	76143	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133756033||es||False	f	t	t
BARCLAYS BONOS LARGO	ES0138602034	EUR	2	|BMF|0063|	f	76152	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138602034||es||False	f	t	t
BARCLAYS GARANT. GIGANTES MUNDIALES	ES0138295037	EUR	2	|BMF|0063|	f	76153	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138295037||es||False	f	t	t
BARCLAYS GARANTIZADO 2012	ES0125624009	EUR	2	|BMF|0063|	f	76154	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125624009||es||False	f	t	t
IBERCAJA RENTA PLUS	ES0147194031	EUR	2	|BMF|0084|	f	76155	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147194031||es||False	f	t	t
IBERCAJA SANIDAD	ES0147195038	EUR	2	|BMF|0084|	f	76156	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147195038||es||False	f	t	t
IBERCAJA SECTOR INMOBILIARIO	ES0147196036	EUR	2	|BMF|0084|	f	76158	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147196036||es||False	f	t	t
BARCLAYS GARANTIZADO 2013	ES0138971033	EUR	2	|BMF|0063|	f	76247	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138971033||es||False	f	t	t
BARCLAYS GARANTIZADO 8	ES0158322034	EUR	2	|BMF|0063|	f	76248	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158322034||es||False	f	t	t
BARCLAYS GARANTIZADO ACC. ESPAÑA	ES0138520038	EUR	2	|BMF|0063|	f	76249	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138520038||es||False	f	t	t
BARCLAYS GARANTIZADO 1	ES0133551038	EUR	2	|BMF|0063|	f	76250	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133551038||es||False	f	t	t
MARCH PREMIER 70/30	ES0160988038	EUR	2	|BMF|0190|	f	76255	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160988038||es||False	f	t	t
MULTIFONDO AMERICA	ES0165092034	EUR	2	|BMF|0132|	f	76256	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165092034||es||False	f	t	t
MULTIGESTORES	ES0165093032	EUR	2	|BMF|0113|	f	76259	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165093032||es||False	f	t	t
MULTIOPORTUNIDAD	ES0106082037	EUR	2	|BMF|0132|	f	76260	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0106082037||es||False	f	t	t
BARCLAYS GARANTIZADO 16	ES0155814033	EUR	2	|BMF|0063|	f	76362	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155814033||es||False	f	t	t
BARCLAYS TESORERIA	ES0113986030	EUR	2	|BMF|0063|	f	76365	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113986030||es||False	f	t	t
BASKEPLUS	ES0114299037	EUR	2	|BMF|0095|	f	76366	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114299037||es||False	f	t	t
ESPIRITO SANTO ESPAÑA 30	ES0158193039	EUR	2	|BMF|0113|	f	76371	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158193039||es||False	f	t	t
INTERDIN GLOBAL FONDOS	ES0155527031	EUR	2	|BMF|0198|	f	76381	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155527031||es||False	f	t	t
FONDUERO CAPITAL GARANTIZADO 9	ES0138567039	EUR	2	|BMF|0162|	f	76383	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138567039||es||False	f	t	t
GARANTIA PLUS 4	ES0140896038	EUR	2	|BMF|0162|	f	76388	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0140896038||es||False	f	t	t
IBERCAJA GESTION GARANTIZADO 3	ES0146845005	EUR	2	|BMF|0084|	f	76476	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146845005||es||False	f	t	t
IBERCAJA GESTION GARANTIZADO 4	ES0146846003	EUR	2	|BMF|0084|	f	76482	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146846003||es||False	f	t	t
IBERCAJA RENTA FIJA 1 AÑO 3	ES0147047007	EUR	2	|BMF|0084|	f	76579	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147047007||es||False	f	t	t
RURAL VALOR	ES0174407033	EUR	2	|BMF|0140|	f	76580	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174407033||es||False	f	t	t
SABADELL BS AMERICA LATINA  BOLS	ES0173827033	EUR	2	|BMF|0058|	f	76581	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173827033||es||False	f	t	t
ALTAE BOLSA	ES0108846033	EUR	2	|BMF|0085|	f	76596	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108846033||es||False	f	t	t
SABADELL BS INTERES EURO 1	ES0138843034	EUR	2	|BMF|0058|	f	76730	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138843034||es||False	f	t	t
SABADELL BS INTERES EURO 3	ES0161850039	EUR	2	|BMF|0058|	f	76731	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0161850039||es||False	f	t	t
INTERVALOR RENTA	ES0155852033	EUR	2	|BMF|0152|	f	76866	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155852033||es||False	f	t	t
SABADELL BS RENTABILIDAD OBJETIVO 2	ES0111147007	EUR	2	|BMF|0058|	f	76872	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111147007||es||False	f	t	t
CAJA LABORAL GARANTIZADO III	ES0114889035	EUR	2	|BMF|0161|	f	77001	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114889035||es||False	f	t	t
UNIFOND EURIBOR PLUS	ES0181002033	EUR	2	|BMF|0154|	f	77111	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181002033||es||False	f	t	t
CAIXA GALICIA MIX 25	ES0115356034	EUR	2	|BMF|0128|	f	77271	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115356034||es||False	f	t	t
CAIXA GALICIA RENDIMIENTO GARANT	ES0114992037	EUR	2	|BMF|0128|	f	77272	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114992037||es||False	f	t	t
CAIXA GALICIA RENDIMIENTO GTZDO. 2	ES0114998000	EUR	2	|BMF|0128|	f	77273	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114998000||es||False	f	t	t
UBS MIXTO GESTION ACTIVA CLASE I	ES0158316036	EUR	2	|BMF|0185|	f	77276	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158316036||es||False	f	t	t
UBS MIXTO GESTION ACTIVA CLASE P	ES0158316002	EUR	2	|BMF|0185|	f	77277	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158316002||es||False	f	t	t
UBS RENTA GESTION ACTIVA	ES0180933006	EUR	2	|BMF|0185|	f	77278	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180933006||es||False	f	t	t
MANRESA GARANTIT 4	ES0159534009	EUR	2	|BMF|0076|	f	77362	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159534009||es||False	f	t	t
SANTANDER POSITIVO	ES0138361037	EUR	2	|BMF|0012|	f	77363	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138361037||es||False	f	t	t
SANTANDER POSITIVO 2	ES0112735032	EUR	2	|BMF|0012|	f	77364	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112735032||es||False	f	t	t
MANRESA GARANTIT V	ES0117063000	EUR	2	|BMF|0076|	f	77466	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117063000||es||False	f	t	t
AC FONDEPOSITO PLUS	ES0114941034	EUR	2	|BMF|0128|	f	77467	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114941034||es||False	f	t	t
EUROVALOR EUROPA PROTECCION, FI	ES0133845034	EUR	2	|BMF|0004|	f	77468	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133845034||es||False	f	t	t
BBK SOLIDARIA	ES0114186036	EUR	2	|BMF|0095|	f	77469	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114186036||es||False	f	t	t
FONCAIXA 66 BOLSA INDICE SUIZA	ES0138383031	EUR	2	|BMF|0015|	f	77470	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138383031||es||False	f	t	t
AHORRO CORP. FONDTESORO PLUS	ES0107481030	EUR	2	|BMF|0128|	f	77478	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107481030||es||False	f	t	t
BOND MANAGERS FUND	ES0115039036	EUR	2	|BMF|0195|	f	77485	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115039036||es||False	f	t	t
BANESTO BOLSA 30	ES0113659033	EUR	2	|BMF|0012|	f	77486	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113659033||es||False	f	t	t
BANESTO 95% CAPITAL MEJOR OPCION	ES0113746038	EUR	2	|BMF|0012|	f	77488	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113746038||es||False	f	t	t
SMART ALLOCATION FUND	ES0176201038	EUR	2	|BMF|0195|	f	77489	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0176201038||es||False	f	t	t
BANESTO EXTRA AHORRO	ES0134675034	EUR	2	|BMF|0012|	f	77579	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0134675034||es||False	f	t	t
CAJABURGOS MIXTO I	ES0114949037	EUR	2	|BMF|0128|	f	77596	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114949037||es||False	f	t	t
CAJABURGOS SOLUCION 2	ES0169084003	EUR	2	|BMF|0128|	f	77604	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169084003||es||False	f	t	t
BOREAS GLOBAL	ES0114902002	EUR	2	|BMF|0113|	f	77609	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114902002||es||False	f	t	t
MAPFRE FONDTESORO	ES0160634038	EUR	2	|BMF|0121|	f	77611	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160634038||es||False	f	t	t
SANTANDER TESORERO A	ES0112744000	EUR	2	|BMF|0012|	f	77612	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112744000||es||False	f	t	t
VITAL EURO INDICES	ES0184264036	EUR	2	|BMF|0007|	f	77613	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184264036||es||False	f	t	t
VITAL EURO PLUS	ES0184260034	EUR	2	|BMF|0007|	f	77614	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184260034||es||False	f	t	t
VITAL G1	ES0184259036	EUR	2	|BMF|0007|	f	77615	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184259036||es||False	f	t	t
VITAL G3	ES0184263038	EUR	2	|BMF|0007|	f	77616	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184263038||es||False	f	t	t
VITAL INDICES I S.I.M.	ES0184251033	EUR	2	|BMF|0007|	f	77617	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184251033||es||False	f	t	t
VITAL MIXTO	ES0184268037	EUR	2	|BMF|0007|	f	77618	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184268037||es||False	f	t	t
VITAL RENTAS PLUS GARANT.	ES0184252031	EUR	2	|BMF|0007|	f	77619	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184252031||es||False	f	t	t
ESPIRITO SANTO GESTION DINAMICA	ES0133098030	EUR	2	|BMF|0113|	f	77645	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133098030||es||False	f	t	t
CREVAL CAPITAL	ES0124721038	EUR	2	|BMF|0029|	f	77647	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0124721038||es||False	f	t	t
DWS WINFONDO	ES0184717033	EUR	2	|BMF|0142|	f	77648	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184717033||es||False	f	t	t
MADRID GESTION ALTERNATIVA	ES0140941032	EUR	2	|BMF|0085|	f	77660	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0140941032||es||False	f	t	t
GESCOOPERATIVO ALPH.MULTIGESTION	ES0142098005	EUR	2	|BMF|0140|	f	77661	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142098005||es||False	f	t	t
SANTANDER GAR.ACTIVA CONSERVADOR	ES0174951030	EUR	2	|BMF|0012|	f	77662	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174951030||es||False	f	t	t
SEGURFONDO CORTO PLAZO	ES0175413006	EUR	2	|BMF|0098|	f	77665	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175413006||es||False	f	t	t
MANRESA PREMIER	ES0114848031	EUR	2	|BMF|0076|	f	77700	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114848031||es||False	f	t	t
MANRESA MIXT	ES0114463039	EUR	2	|BMF|0076|	f	77702	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114463039||es||False	f	t	t
MANRESA PREMIUM	ES0117141038	EUR	2	|BMF|0076|	f	77704	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117141038||es||False	f	t	t
MARCH BOLSA	ES0160951036	EUR	2	|BMF|0190|	f	77712	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160951036||es||False	f	t	t
TARFONDO	ES0177975036	EUR	2	|BMF|0185|	f	77714	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0177975036||es||False	f	t	t
IBERCAJA DOBLE OPORTUNIDAD	ES0146844032	EUR	2	|BMF|0084|	f	77729	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146844032||es||False	f	t	t
MADRID SECTOR FINANCIERO GLOBAL	ES0140981038	EUR	2	|BMF|0085|	f	77730	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0140981038||es||False	f	t	t
CAJARIOJA GARANTIZADO 2	ES0114549035	EUR	2	|BMF|0128|	f	77749	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114549035||es||False	f	t	t
CAJARIOJA GARANTIZADO 4	ES0122713003	EUR	2	|BMF|0128|	f	77750	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122713003||es||False	f	t	t
MARCH BOLSAS INTER. GARANTIZADO	ES0160943033	EUR	2	|BMF|0190|	f	77751	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160943033||es||False	f	t	t
MARCH DINERO	ES0160985034	EUR	2	|BMF|0190|	f	77752	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160985034||es||False	f	t	t
MARCH RENTA FIJA PRIVADA	ES0160989002	EUR	2	|BMF|0190|	f	77753	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160989002||es||False	f	t	t
MARCH RENTA FIJA PRIVADA 2013	ES0160945004	EUR	2	|BMF|0190|	f	77754	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160945004||es||False	f	t	t
MARCH USA GARANTIZADO	ES0115541031	EUR	2	|BMF|0190|	f	77755	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115541031||es||False	f	t	t
GESCOOPERATIVO MUL. ALTERNATIVAS	ES0158602039	EUR	2	|BMF|0140|	f	77756	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158602039||es||False	f	t	t
OPEN FUND	ES0138906039	EUR	2	|BMF|0125|	f	77839	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138906039||es||False	f	t	t
UBS (ES)STABLE GROWTH IICIICIL	ES0180936009	EUR	2	|BMF|0185|	f	77850	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180936009||es||False	f	t	t
PRIVARY F2 DISCRECIONAL	ES0170862033	EUR	2	|BMF|0083|	f	77851	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170862033||es||False	f	t	t
SANTANDER GAR.GRANDES COMPAÑIAS	ES0175834037	EUR	2	|BMF|0012|	f	77881	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175834037||es||False	f	t	t
PBP RENTA FIJA FLEXIBLE	ES0147140034	EUR	2	|BMF|0182|	f	77883	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147140034||es||False	f	t	t
PLUSMADRID FONDANDALUCIA	ES0170162038	EUR	2	|BMF|0085|	f	77884	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170162038||es||False	f	t	t
UBS (ES) ALPHA SELECT IICIICIL	ES0180935001	EUR	2	|BMF|0185|	f	77885	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180935001||es||False	f	t	t
SIITNEDIF TORDESILLAS IBOP, CLASE M	ES0175977018	EUR	2	|BMF|0216|	f	77886	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175977018||es||False	f	t	t
PRIVAT FOND. GLOBAL	ES0170864039	EUR	2	|BMF|0078|	f	77892	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170864039||es||False	f	t	t
CAM DINERO 1	ES0126534033	EUR	2	|BMF|0127|	f	77913	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126534033||es||False	f	t	t
CAM DINERO AHORRO	ES0107482038	EUR	2	|BMF|0127|	f	77916	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107482038||es||False	f	t	t
CAM DINERO PLATINUM	ES0124553035	EUR	2	|BMF|0127|	f	77917	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0124553035||es||False	f	t	t
CAM EMERGENTES	ES0105142030	EUR	2	|BMF|0127|	f	77920	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105142030||es||False	f	t	t
CAM FUTURO 8 GARANTIZADO	ES0140983034	EUR	2	|BMF|0127|	f	77924	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0140983034||es||False	f	t	t
CAM FUTURO 9 GARANTIZADO	ES0105171039	EUR	2	|BMF|0127|	f	77925	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105171039||es||False	f	t	t
CAM DINERO PREMIER	ES0170668034	EUR	2	|BMF|0127|	f	77927	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170668034||es||False	f	t	t
CAIXA CATALUNYA BORSA EMERGENT	ES0115344030	EUR	2	|BMF|0020|	f	78016	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115344030||es||False	f	t	t
CAIXA CATALUNYA GARANTIT 3-C	ES0114408034	EUR	2	|BMF|0020|	f	78018	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114408034||es||False	f	t	t
FONDO CAJA MURCIA INTERES GARANTIZ. III	ES0139778031	EUR	2	|BMF|0128|	f	78022	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0139778031||es||False	f	t	t
RURAL GARANTIZADO RENTA FIJA I	ES0123974034	EUR	2	|BMF|0140|	f	78026	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0123974034||es||False	f	t	t
FONDO COMMODITY TRIO	ES0140822034	EUR	2	|BMF|0012|	f	78027	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0140822034||es||False	f	t	t
FONDPUEYO	ES0115221030	EUR	2	|f_es_0043|f_es_BMF|	f	77926	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115221030||es||False	f	t	t
CS EUROPEAN SELECT DIVIDEND	ES0143674036	EUR	2	|BMF|0173|	f	78041	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0143674036||es||False	f	t	t
FONCAIXA 102 CARTERA TESORERIA E	ES0137801033	EUR	2	|BMF|0015|	f	78075	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137801033||es||False	f	t	t
CAIXAGIRONA OPORTUNITATS	ES0115414031	EUR	2	|BMF|0006|	f	78078	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115414031||es||False	f	t	t
30-70 EURO INVERSION	ES0184833038	EUR	2	|BMF|0063|	f	78089	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184833038||es||False	f	t	t
A&G TESORERIA	ES0156873004	EUR	2	|BMF|0195|	f	78091	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0156873004||es||False	f	t	t
A.C. DINAMICO	ES0107383038	EUR	2	|BMF|0128|	f	78092	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107383038||es||False	f	t	t
CAIXAGIRONA ESTALVI	ES0138788031	EUR	2	|BMF|0006|	f	78108	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138788031||es||False	f	t	t
BG BOLSA INTERNACIONAL	ES0134608035	EUR	2	|BMF|0110|	f	78205	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0134608035||es||False	f	t	t
ACAPITAL ESTRATEGIA GLOBAL	ES0105234001	EUR	2	|BMF|0217|	f	78229	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105234001||es||False	f	t	t
ACAPITAL MIXTO	ES0105312005	EUR	2	|BMF|0217|	f	78235	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105312005||es||False	f	t	t
ACAPITAL TESORERIA DINAMICA	ES0105297008	EUR	2	|BMF|0217|	f	78237	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105297008||es||False	f	t	t
CAJA INGENIEROS MULTICESTA GARAN	ES0115426035	EUR	2	|BMF|0193|	f	78253	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115426035||es||False	f	t	t
SABADELL BS GARANTIA SUPERIOR 3	ES0158285033	EUR	2	|BMF|0058|	f	78257	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158285033||es||False	f	t	t
SABADELL BS GARANTIA SUPERIOR 4	ES0175262031	EUR	2	|BMF|0058|	f	78258	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175262031||es||False	f	t	t
BEST MORGAN STANLEY	ES0145808004	EUR	2	|BMF|0105|	f	78263	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0145808004||es||False	f	t	t
FONENGIN	ES0138885035	EUR	2	|BMF|0193|	f	78274	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138885035||es||False	f	t	t
AEGON INVERSION MF	ES0147614038	EUR	2	|BMF|0098|	f	78316	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147614038||es||False	f	t	t
AEGON INVERSION MV	ES0147616033	EUR	2	|BMF|0098|	f	78317	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147616033||es||False	f	t	t
AHORRO CORP. ACCIONES	ES0107472039	EUR	2	|BMF|0128|	f	78318	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107472039||es||False	f	t	t
BEST TIMING FUND	ES0114592035	EUR	2	|BMF|0132|	f	78319	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114592035||es||False	f	t	t
BEST TIMING FUND II	ES0114560008	EUR	2	|BMF|0132|	f	78322	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114560008||es||False	f	t	t
CAJA MADRID SELECCION FINANCIERA	ES0105580031	EUR	2	|BMF|0085|	f	78668	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105580031||es||False	f	t	t
CAJA SEGOVIA GARANT.EURIB.MAS 60	ES0105581005	EUR	2	|BMF|0128|	f	78669	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105581005||es||False	f	t	t
CAJABURGOS F.DE F. MOD.VAR 6	ES0117186033	EUR	2	|BMF|0128|	f	78671	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117186033||es||False	f	t	t
CAJABURGOS F.DE F.COSERV.VAR 3	ES0158950032	EUR	2	|BMF|0128|	f	78672	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158950032||es||False	f	t	t
CAIXA GALICIA GESTION CONSERVADO	ES0147597035	EUR	2	|BMF|0128|	f	78843	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147597035||es||False	f	t	t
DWS RENTA	ES0139012035	EUR	2	|BMF|0142|	f	78985	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0139012035||es||False	f	t	t
EDM CARTERA	ES0128331008	EUR	2	|BMF|0049|	f	78986	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0128331008||es||False	f	t	t
EJECUTIVOS GLOBALFOND	ES0128496033	EUR	2	|BMF|0105|	f	78990	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0128496033||es||False	f	t	t
CAJAMAR RENDIMIENTO	ES0122712039	EUR	2	|BMF|0069|	f	78993	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122712039||es||False	f	t	t
ESAF 10	ES0138839032	EUR	2	|BMF|0047|	f	79026	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138839032||es||False	f	t	t
ESAF 70	ES0115073035	EUR	2	|BMF|0047|	f	79034	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115073035||es||False	f	t	t
FONPASTOR DEUDA PUBLICA LARGO	ES0168567008	EUR	2	|BMF|0047|	f	79035	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168567008||es||False	f	t	t
CAIXA CATALUNYA BORSA 12	ES0115287031	EUR	2	|BMF|0020|	f	79039	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115287031||es||False	f	t	t
ESAF GARANT. BOLSA ESPANOLA 3	ES0168656033	EUR	2	|BMF|0047|	f	79042	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168656033||es||False	f	t	t
FONCAIXA PERSONAL TESORERIA EURO	ES0137879039	EUR	2	|BMF|0015|	f	79698	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137879039||es||False	f	t	t
FONDESPAÑA AHORRO	ES0122065032	EUR	2	|BMF|0130|	f	79956	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122065032||es||False	f	t	t
MANRESA DINAMIC	ES0117061038	EUR	2	|BMF|0076|	f	80468	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117061038||es||False	f	t	t
MILLENIUM FUND	ES0162915039	EUR	2	|BMF|0132|	f	80576	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162915039||es||False	f	t	t
MILLENIUM FUND II	ES0162916037	EUR	2	|BMF|0132|	f	80577	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162916037||es||False	f	t	t
MISTRAL FLEXIBLE	ES0164103030	EUR	2	|BMF|0140|	f	80578	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164103030||es||False	f	t	t
PLUSMADRID 15	ES0159141037	EUR	2	|BMF|0085|	f	80587	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159141037||es||False	f	t	t
PBP BOLSA EUROPA	ES0147101036	EUR	2	|BMF|0182|	f	80594	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147101036||es||False	f	t	t
RIVA Y GARCIA SELECCION MODERADA	ES0173982002	EUR	2	|BMF|0131|	f	80689	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173982002||es||False	f	t	t
RURAL 14 GARANTIZADO RENTA FIJA	ES0174229031	EUR	2	|BMF|0140|	f	80691	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174229031||es||False	f	t	t
RURAL MIXTO INTERNACIONAL 50	ES0174382038	EUR	2	|BMF|0140|	f	80784	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174382038||es||False	f	t	t
FONPENEDES INTERES GARANTIT 1	ES0117015034	EUR	2	|BMF|0163|	f	80995	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117015034||es||False	f	t	t
KUTXAAHORRO	ES0157025034	EUR	2	|BMF|0086|	f	81134	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157025034||es||False	f	t	t
MERCHBANC FONDTESORO	ES0162331039	EUR	2	|BMF|0034|	f	81335	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162331039||es||False	f	t	t
MERCHFONDO	ES0162332037	EUR	2	|BMF|0034|	f	81336	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162332037||es||False	f	t	t
MERCHRENTA	ES0162333035	EUR	2	|BMF|0034|	f	81337	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162333035||es||False	f	t	t
METAVALOR	ES0162735031	EUR	2	|BMF|0040|	f	81338	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162735031||es||False	f	t	t
URQUIJO PATRIMONIO PRIVADO 2	ES0161851037	EUR	2	|BMF|0058|	f	81582	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0161851037||es||False	f	t	t
URQUIJO PATRIMONIO PRIVADO 5	ES0161847035	EUR	2	|BMF|0058|	f	81583	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0161847035||es||False	f	t	t
URQUIJO PROGRESION CARTERAS	ES0182281008	EUR	2	|BMF|0058|	f	81584	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182281008||es||False	f	t	t
V & V GESTION ACTIVA	ES0110240001	EUR	2	|BMF|0197|	f	81585	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110240001||es||False	f	t	t
VALORICA ALFA	ES0182753006	EUR	2	|BMF|0223|	f	81586	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182753006||es||False	f	t	t
TURBO Put IBEX 35 | 10250 € | 17/06/11 | 54842	FR0011003268	EUR	5	|SGW|	f	74748	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54842||fr||False	f	t	t
Call IBEX 35 inLine | 7000 € | 14/03/12 | I0048	FR0011117886	EUR	5	|SGW|	f	74749	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0048||fr||False	f	t	t
AREVA ADPCI	FR0010986190	EUR	1	|EURONEXT|	f	74753	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010986190||fr||False	f	t	t
Put IBEX 35 | 7750 € | 20/01/12 | B9945	FR0011091347	EUR	5	|SGW|	f	74754	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9945||fr||False	f	t	t
Call IBEX 35 | 9000 € | 16/12/11 | B5139	FR0011002732	EUR	5	|SGW|	f	74755	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B5139||fr||False	f	t	t
AGEAS (EX-FORTIS)	BE0003801181	EUR	1	|EURONEXT|	f	74759	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003801181||be||False	f	t	t
USEC Inc.	\N	USD	1	\N	f	77370	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#USU||us||False	f	t	t
Boise Inc.	\N	USD	1	\N	f	77453	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BZ||us||False	f	t	t
BESTINVER HEDGE VALUE FUND	ES0114578000	EUR	2	|BMF|0103|	f	77476	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114578000||es||False	f	t	t
BJ's Wholesale Club Inc.	\N	USD	1	\N	f	77555	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BJ||us||False	f	t	t
KBR Inc.	\N	USD	1	\N	f	77707	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KBR||us||False	f	t	t
PerkinElmer Inc.	\N	USD	1	\N	f	77855	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PKI||us||False	f	t	t
Public Storage	\N	USD	1	\N	f	78098	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PSA||us||False	f	t	t
Grupo TMM S.A.B.	\N	USD	1	\N	f	78117	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TMM||us||False	f	t	t
Semgroup Corp. Cl A	\N	USD	1	\N	f	78159	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SEMG||us||False	f	t	t
NACCO Industries Inc. Cl A	\N	USD	1	\N	f	78160	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NC||us||False	f	t	t
Coach Inc.	\N	USD	1	\N	f	78222	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#COH||us||False	f	t	t
ACANTHEDEVBSAOCT11	FR0000346975	EUR	1	|EURONEXT|	f	78221	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000346975||fr||False	f	t	t
Polaris Industries Inc.	\N	USD	1	\N	f	78834	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PII||us||False	f	t	t
CommonWealth REIT	\N	USD	1	\N	f	79078	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CWH||us||False	f	t	t
RENTA 4 MONETARIO	ES0128520006	EUR	2	|f_es_0043|f_es_BMF|	f	74788					0	c	0	1	None	{2}	\N	ES0128520006||es||True	f	f	t
PARROT	FR0004038263	EUR	1	|EURONEXT|	f	80728	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004038263||fr||False	f	t	t
Call IBEX 35 | 7750 € | 20/01/12 | B9943	FR0011091321	EUR	5	|SGW|	f	80729	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9943||fr||False	f	t	t
Call IBEX 35 | 8250 € | 20/01/12 | B9944	FR0011091339	EUR	5	|SGW|	f	80730	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9944||fr||False	f	t	t
Call IBEX 35 | 8750 € | 20/01/12 | B9693	FR0011083724	EUR	5	|SGW|	f	80732	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9693||fr||False	f	t	t
Call IBEX 35 | 9250 € | 20/01/12 | B9694	FR0011083732	EUR	5	|SGW|	f	80733	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9694||fr||False	f	t	t
PARSYS	FR0000062721	EUR	1	|EURONEXT|	f	80734	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000062721||fr||False	f	t	t
PARTNERRE LTD.	BMG6852T1053	EUR	1	|EURONEXT|	f	80735	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#BMG6852T1053||fr||False	f	t	t
PATRIMOINE ET COMM	FR0011027135	EUR	1	|EURONEXT|	f	80744	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011027135||fr||False	f	t	t
PCASBSAR1212	FR0010480723	EUR	1	|EURONEXT|	f	80746	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010480723||fr||False	f	t	t
PERRIER (GERARD)	FR0000061459	EUR	1	|EURONEXT|	f	80748	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000061459||fr||False	f	t	t
PIERRE VACANCES	FR0000073041	EUR	1	|EURONEXT|	f	80750	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000073041||fr||False	f	t	t
THROMBOG STRIP (D)	BE0005604757	EUR	1	|EURONEXT|	f	74950	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005604757||be||False	f	t	t
United Power Technology AG	DE000A1EMAK2	EUR	1	|DEUTSCHEBOERSE|	f	74934	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1EMAK2||de||False	f	t	t
USU Software AG	DE000A0BVU28	EUR	1	|DEUTSCHEBOERSE|	f	74943	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0BVU28||de||False	f	t	t
\N	\N	\N	\N	\N	f	78975	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0113984001||None||False	f	t	t
GAMESA	ES0143416115	EUR	1	|IBEX|MERCADOCONTINUO|	f	79037					100	c	0	1	GAM.MC	{1}	{3}	MC#ES0143416115||es||False	f	f	t
GAS NATURAL	ES0116870314	EUR	1	|IBEX|MERCADOCONTINUO|	t	79046					100	c	0	1	GAS.MC	{1}	{3}	MC#ES0116870314||es||False	f	f	t
Nokia OYJ		EUR	1	|EUROSTOXX|	f	75143					100	c	0	14	None	\N	\N	NOKIA||None||False	f	f	t
BANKINTER DINERO 2	ES0114801030	EUR	2	|f_es_0055|f_es_BMF|	f	76851					0	c	0	1	None	{2}	\N	ES0114801030||es||False	f	f	t
BANKINTER DINERO 3	ES0115155030	EUR	2	|f_es_0055|f_es_BMF|	f	77199	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115155030||es||False	f	f	t
RENTA 4 EUROCASH	ES0173319031	EUR	2	|f_es_0043|f_es_BMF|	f	81421	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173319031||es||False	f	f	t
RENTA 4 PEGASUS	ES0173321003	EUR	2	|f_es_0043|f_es_BMF|	t	81436					100	c	0	1	None	{2}	\N	ES0173321003||es||False	f	f	t
ENAGAS	ES0130960018	EUR	1	|IBEX|MERCADOCONTINUO|	t	81117					100	c	0	1	ENG.MC	{1}	{3}	MC#ES0130960018||es||False	f	f	t
Graphit Kropfmühl Aktie	DE0005896005	EUR	1	|DEUTSCHEBOERSE|	f	75066					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE0005896005||de||False	f	t	t
Eastman Chemical Co.	\N	USD	1	\N	f	75055	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EMN||us||False	f	t	t
XL Group PLC	\N	USD	1	\N	f	75061	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#XL||us||False	f	t	t
IAMGOLD Corp.	\N	USD	1	\N	f	75065	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IAG||us||False	f	t	t
DPL Inc.	\N	USD	1	\N	f	75070	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DPL||us||False	f	t	t
Exxon Mobil Corp.	\N	USD	1	\N	f	75085	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#XOM||us||False	f	t	t
Knight Transportation Inc.	\N	USD	1	\N	f	79350	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KNX||us||False	f	t	t
Regal Entertainment Group Cl A	\N	USD	1	\N	f	79352	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RGC||us||False	f	t	t
Call IBEX 35 | 11500 € | 16/12/11 | B5144	FR0011002781	EUR	5	|SGW|	f	75088	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B5144||fr||False	f	t	t
Put IBEX 35 | 8250 € | 18/05/12 | C1124	FR0011124296	EUR	5	|SGW|	f	75089	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1124||fr||False	f	t	t
Put IBEX 35 | 8750 € | 18/05/12 | C1125	FR0011124304	EUR	5	|SGW|	f	75092	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1125||fr||False	f	t	t
RHODIA	FR0010479956	EUR	1	|EURONEXT|	f	75098	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010479956||fr||False	f	t	t
Call IBEX 35 | 11250 € | 20/05/11 | B4727	FR0010984450	EUR	5	|SGW|	f	75099	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4727||fr||False	f	t	t
Call IBEX 35 | 10750 € | 20/05/11 | B4726	FR0010984443	EUR	5	|SGW|	f	75100	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4726||fr||False	f	t	t
Put IBEX 35 | 7000 € | 21/09/12 | C3296	FR0011168368	EUR	5	|SGW|	f	75104	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3296||fr||False	f	t	t
\N	\N	\N	\N	\N	f	75101	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	EURONEXT#FR0011146539||None||False	f	t	t
Put IBEX 35 | 8250 € | 20/05/11 | B4729	FR0010984476	EUR	5	|SGW|	f	75105	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4729||fr||False	f	t	t
Call IBEX 35 | 9250 € | 20/05/11 | B4723	FR0010984419	EUR	5	|SGW|	f	75107	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4723||fr||False	f	t	t
Michelin	FR0000121261	EUR	1	|CAC|	f	75110					100	c	0	3	ML.PA	{1}	{3}	ML.PA||fr||False	f	t	t
\N	\N	\N	\N	\N	f	75115	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0180944037||None||False	f	t	t
\N	\N	\N	\N	\N	f	75116	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0182151037||None||False	f	t	t
BETA Systems Software AG	DE0005224406	EUR	1	|DEUTSCHEBOERSE|	f	74998	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005224406||de||False	f	t	t
VTG Aktiengesellschaft	DE000VTG9999	EUR	1	|DEUTSCHEBOERSE|	f	75038	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000VTG9999||de||False	f	t	t
BHP Billiton Ltd.	\N	USD	1	\N	f	75090	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BHP||us||False	f	t	t
Flowserve Corp.	\N	USD	1	\N	f	75093	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FLS||us||False	f	t	t
Franco-Nevada Corp.	\N	USD	1	\N	f	75095	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FNV||us||False	f	t	t
Call IBEX 35 | 8250 € | 17/02/12 | B9947	FR0011091362	EUR	5	|SGW|	f	75125	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9947||fr||False	f	t	t
Call IBEX 35 | 8750 € | 17/02/12 | B9948	FR0011091370	EUR	5	|SGW|	f	75132	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9948||fr||False	f	t	t
Call IBEX 35 | 8750 € | 20/05/11 | B4722	FR0010984401	EUR	5	|SGW|	f	75133	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4722||fr||False	f	t	t
Call IBEX 35 | 11750 € | 20/05/11 | B4728	FR0010984468	EUR	5	|SGW|	f	75134	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4728||fr||False	f	t	t
Call IBEX 35 | 7500 € | 18/11/11 | B9933	FR0011091222	EUR	5	|SGW|	f	75137	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9933||fr||False	f	t	t
Call IBEX 35 | 11000 € | 16/12/11 | B5143	FR0011002773	EUR	5	|SGW|	f	75142	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B5143||fr||False	f	t	t
Call IBEX 35 | 9500 € | 17/06/11 | B1774	FR0010936088	EUR	5	|SGW|	f	75145	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B1774||fr||False	f	t	t
Call IBEX 35 | 8500 € | 17/06/11 | B1772	FR0010936062	EUR	5	|SGW|	f	75146	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B1772||fr||False	f	t	t
\N	\N	\N	\N	\N	f	75139	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	NYSE#MOG||None||False	f	t	t
Vtion Wireless Technology AG	DE000CHEN993	EUR	1	|DEUTSCHEBOERSE|	f	75039	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000CHEN993||de||False	f	t	t
Wacker Neuson SE	DE000WACK012	EUR	1	|DEUTSCHEBOERSE|	f	75071	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000WACK012||de||False	f	t	t
WashTec AG	DE0007507501	EUR	1	|DEUTSCHEBOERSE|	f	75073	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007507501||de||False	f	t	t
Call IBEX 35 inLine | 9000 € | 15/09/11 | I0031	FR0011038959	EUR	5	|SGW|	f	75506	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0031||fr||False	f	f	t
IBERCAJA CAPITAL	ES0147165031	EUR	2	|BMF|0084|	f	80837	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147165031||es||False	f	f	t
IBERCAJA BOLSA	ES0147186037	EUR	2	|BMF|0084|	f	81043	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147186037||es||False	f	f	t
WARRANT TELEFONICA Put 12 19/12/2014		EUR	5	|w_fr_SG|	f	74744					100	p	1	3	B7856	\N	\N	SGW#B7856||None||False	f	f	t
British Petroleum BP	GB0007980591	GBP	1		f	75006					100	c	0	4	BP.L	{1}	{3}	BP.L||None||False	f	f	t
ACS	ES0167050915	EUR	1	|IBEX|MERCADOCONTINUO|	t	78327					100	c	0	1	ACS.MC	{1}	{3}	MC#ES0167050915||es||False	f	f	t
Call IBEX 35 inLine | 9000 € | 17/06/11 | I0023	FR0011002351	EUR	5	|SGW|	f	75972	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0023||fr||False	f	f	t
Call IBEX 35 inLine | 8500 € | 17/06/11 | I0024	FR0011002369	EUR	5	|SGW|	f	76215	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0024||fr||False	f	f	t
Call IBEX 35 | 13000 € | 19/12/14 | B7870	FR0011065739	EUR	5	|SGW|	f	76806	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7870||fr||False	f	f	t
FRANCE TELECOM	FR0000133308	EUR	1	|CAC|EURONEXT|EUROSTOXX|	t	76996					100	c	0	3	FTE.PA	{1}	{3}	EURONEXT#FR0000133308||fr||False	f	f	t
TURBO Put IBEX 35 | 11000 € | 16/09/11 | 54982	FR0011057595	EUR	5	|SGW|	f	77255	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54982||fr||False	f	f	t
TURBO Call IBEX 35 | 9000 € | 17/06/11 | 54831	FR0011003151	EUR	5	|SGW|	f	78069	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54831||fr||False	f	f	t
Call IBEX 35 | 11000 € | 19/12/14 | B7869 	\N	EUR	5	\N	f	78050	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	SGW#B7869||es||True	f	f	t
ACCIONA	ES0125220311	EUR	1	|IBEX|MERCADOCONTINUO|	t	78281					100	c	0	1	ANA.MC	{1}	{3}	MC#ES0125220311||es||False	f	f	t
TURBO Call IBEX 35 | 9000 € | 16/09/11 | 54973	FR0011057504	EUR	5	|SGW|	f	75538	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54973||fr||False	f	f	t
iShares S&P 500 Index	\N	USD	4	\N	f	75704	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	IVV||us||False	f	f	t
BANESTO FONBANESTO	\N	EUR	\N	\N	f	74959	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	BANESTO FONBANESTO||es||True	f	f	t
BANESTO GARANTIZADO 2001A	\N	EUR	\N	\N	f	74966	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	BANESTO GARANTIZADO 2001A||es||True	f	f	t
CINTRA	\N	\N	\N	\N	f	75202	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	CIN.MC||None||False	f	f	t
Put IBEX 35 | 5000 € | 19/12/14 | B7872	FR0011065754	EUR	5	|SGW|	f	75392	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7872||fr||False	f	f	t
DEPOSITO LACAIXA	\N	EUR	\N	\N	f	-6	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	DEPOSITO LACAIXA||es||True	f	f	f
DERECHOS BANCO SANTANDER	\N	EUR	\N	\N	f	-7	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	DERECHOS BANCO DE SANTANDER||es||True	f	f	f
BARCLAYS PLAN INVERSION 4	\N	EUR	\N	\N	f	74967	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	BARCLAYS PLAN INVERSION 4||es||True	f	f	t
Carmignac Patrimoine (A)	FR0010135103	EUR	2	|CARMIGNAC|	f	81458	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	FR0010135103||fr||False	f	f	t
\N	\N	\N	\N	\N	f	81177	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0157633001||None||False	f	t	t
\N	\N	\N	\N	\N	f	81305	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0160741007||None||False	f	t	t
\N	\N	\N	\N	\N	f	81367	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0165143001||None||False	f	t	t
RENDICOOP	ES0126535030	EUR	2	|BMF|0140|	f	81417	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126535030||es||False	f	t	t
Carmignac Grande Europe (E)	LU0294249692	EUR	2	|CARMIGNAC|	f	81475	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	LU0294249692||fr||False	f	t	t
Olin Corp.	\N	USD	1	\N	f	81604	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OLN||us||False	f	t	t
ZON MULTIMEDIA	PTZON0AM0006	EUR	1	|EURONEXT|	f	81676	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTZON0AM0006||pt||False	f	t	t
THERMADOR GROUPE	FR0000061111	EUR	1	|EURONEXT|	f	81659	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000061111||fr||False	f	t	t
U10 BSAR 0313	FR0010286542	EUR	1	|EURONEXT|	f	81661	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010286542||fr||False	f	t	t
UBISOFT ENTERTAIN	FR0000054470	EUR	1	|EURONEXT|	f	81662	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000054470||fr||False	f	t	t
ULRIC DE VARENS	FR0000079980	EUR	1	|EURONEXT|	f	81663	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000079980||fr||False	f	t	t
UNIVERS.MULTIMEDIA	FR0000057903	EUR	1	|EURONEXT|	f	81664	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000057903||fr||False	f	t	t
VERMANDOISE SUCR.	FR0000037749	EUR	1	|EURONEXT|	f	81668	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000037749||fr||False	f	t	t
VERNEUIL PARTICIP.	FR0000062465	EUR	1	|EURONEXT|	f	81669	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000062465||fr||False	f	t	t
VETOQUINOL	FR0004186856	EUR	1	|EURONEXT|	f	81670	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004186856||fr||False	f	t	t
WENDEL	FR0000121204	EUR	1	|EURONEXT|	f	81673	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000121204||fr||False	f	t	t
ZCI LIMITED	BMG9887P1068	EUR	1	|EURONEXT|	f	81674	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#BMG9887P1068||fr||False	f	t	t
ZODIAC AEROSPACE	FR0000125684	EUR	1	|EURONEXT|	f	81675	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000125684||fr||False	f	t	t
TRANSICS STR VVPR	BE0005613840	EUR	1	|EURONEXT|	f	81660	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005613840||be||False	f	t	t
VGP STRIP VVPR	BE0005621926	EUR	1	|EURONEXT|	f	81671	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005621926||be||False	f	t	t
VALUE8 CUM PREF	NL0009875483	EUR	1	|EURONEXT|	f	81665	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009875483||nl||False	f	t	t
VERIZON COMM.	US92343V1044	EUR	1	|EURONEXT|	f	81667	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#US92343V1044||nl||False	f	t	t
WAVIN	NL0009412683	EUR	1	|EURONEXT|	f	81672	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009412683||nl||False	f	t	t
RENPROA CHART	ES0173311038	EUR	2	|f_es_0043|f_es_BMF|	f	81418	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173311038||es||False	f	t	t
UNIFOND 2013-VII, FI	ES0181395007	EUR	2	|f_es_BMF|	f	81563					100	c	0	1	None	{2}	\N	ES0181395007||None||False	f	t	t
Bankinter RF 2015 II Garantizado FI	ES0114024005	EUR	2	|f_es_0055|f_es_BMF|	f	74765					100	c	0	1	None	{2}	\N	ES0114024005||None||False	f	t	t
ecotel communication ag	DE0005854343	EUR	1	|DEUTSCHEBOERSE|	f	80110					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE0005854343||de||Falsee4c.de	f	t	t
AYG SYZ Low Volatility IICIICIL	ES0112191004	EUR	2	|f_es_BMF|	f	74774					100	c	0	1	None	{2}	\N	ES0112191004||None||False	f	t	t
FONDO BK MONETARIO ACTIVOS EURO	ES0114821038	EUR	2	|f_es_0055|f_es_BMF|	t	80876					0	c	0	1	None	{2}	\N	ES0114821038||es||False	f	f	t
VOCENTO	ES0114820113	EUR	1	|MERCADOCONTINUO|	f	81524					100	c	0	1	VOC.MC	{1}	{3}	MC#ES0114820113||es||voc.mcFalse	f	f	t
Adolfo Domínguez	ES0106000013	EUR	1	|MERCADOCONTINUO|	t	81441					100	c	0	1	ADZ.MC	{1}	{3}	MC#ES0106000013||es||True	f	f	t
TELEFONICA	ES0178430E18	EUR	1	|EUROSTOXX|IBEX|MERCADOCONTINUO|	t	78241					100	c	0	1	TEF.MC	{1}	{3}	MC#ES0178430E18||es||False	f	f	t
Intel Corporation	US4581401001	USD	1	|NASDAQ100|	t	76113					100	c	0	2	INTC	{1}	{3}	INTC||us||False	f	f	t
RENTA 4 OBLIGACIONES CONVERTIBLES 2011		EUR	9		f	75138					0	c	0	1	None	\N	\N	RENTA 4 OBLIGACIONES CONVERTIBLES 2011||es||True	f	f	t
New York Community Bancorp Inc.	\N	USD	1	\N	f	75122	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NYB||us||False	f	t	t
BPEDI11(78P1)	ES0613790916	EUR	1	|EURONEXT|	f	75160	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#ES0613790916||pt||False	f	t	t
Call IBEX 35 | 12000 € | 16/12/11 | B5145	FR0011002799	EUR	5	|SGW|	f	75148	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B5145||fr||False	f	t	t
Put IBEX 35 | 8000 € | 16/12/11 | B9554	FR0011080837	EUR	5	|SGW|	f	75149	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9554||fr||False	f	t	t
Put IBEX 35 | 9250 € | 20/01/12 | B9700	FR0011083799	EUR	5	|SGW|	f	75152	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9700||fr||False	f	t	t
Put IBEX 35 | 10500 € | 16/12/11 | B5152	FR0011002864	EUR	5	|SGW|	f	75153	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B5152||fr||False	f	t	t
\N	\N	\N	\N	\N	f	75150	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	VOC.MC||None||False	f	t	t
\N	\N	\N	\N	\N	f	75151	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	NYSE#RDS||None||False	f	t	t
DIAGEO	GB0002374006	EUR	1	|EURONEXT|	f	75156	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#GB0002374006||fr||False	f	t	t
OUTSIDE LIVIN DS	FR0011063536	EUR	1	|EURONEXT|	f	75158	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011063536||fr||False	f	t	t
ARCHOS DS	FR0011037357	EUR	1	|EURONEXT|	f	75159	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011037357||fr||False	f	t	t
Yahoo	US9843321061	USD	1	|NASDAQ100|SP500|	t	77553					100	c	0	2	YHOO	{1}	{3}	YHOO||us||False	f	t	t
OENEO	FR0000052680	EUR	1	|EURONEXT|	f	75163	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000052680||fr||False	f	t	t
OL GROUPE	FR0010428771	EUR	1	|EURONEXT|	f	75169	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010428771||fr||False	f	t	t
Put IBEX 35 | 9750 € | 20/01/12 | B9701	FR0011083807	EUR	5	|SGW|	f	75179	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9701||fr||False	f	t	t
Call IBEX 35 | 12250 € | 19/08/11 | B6052	FR0011017771	EUR	5	|SGW|	f	75183	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B6052||fr||False	f	t	t
Call IBEX 35 inLine | 8500 € | 15/09/11 | I0028	FR0011038926	EUR	5	|SGW|	f	75186	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0028||fr||False	f	t	t
CYBERGUN	FR0004031839	EUR	1	|EURONEXT|	f	75188	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004031839||fr||False	f	t	t
ASM INTERNATIONAL	NL0000334118	EUR	1	|EURONEXT|	f	75154	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000334118||nl||False	f	t	t
DOC DATA	NL0000345627	EUR	1	|EURONEXT|	f	75157	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000345627||nl||False	f	t	t
CSM	NL0000852549	EUR	1	|EURONEXT|	f	75182	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000852549||nl||False	f	t	t
\N	\N	\N	\N	\N	f	75189	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	EURONEXT#FR0011147438||None||False	f	t	t
Westag + Getalit AG St	DE0007775207	EUR	1	|DEUTSCHEBOERSE|	f	75086	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007775207||de||False	f	t	t
Gesco AG	DE0005875900	EUR	1	|DEUTSCHEBOERSE|	f	75087	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005875900||de||False	f	t	t
Comarch Software und Beratung AG	DE0007249104	EUR	1	|DEUTSCHEBOERSE|	f	75097	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007249104||de||False	f	t	t
Zapf Creation AG	DE0007806002	EUR	1	|DEUTSCHEBOERSE|	f	75102	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007806002||de||False	f	t	t
IVG Immobilien AG	DE0006205701	EUR	1	|DEUTSCHEBOERSE|	f	80321	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006205701||de||False	f	t	t
3M Co.	US88579Y1010	USD	1	|SP500|	f	77347					100	c	0	2	MMM	{1}	{3}	NYSE#MMM||us||False	f	t	t
Jenoptik AG	DE0006229107	EUR	1	|DEUTSCHEBOERSE|	f	80324	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006229107||de||False	f	t	t
INTERSHOP COMMUNICATIONS AG	DE000A0EPUH1	EUR	1	|DEUTSCHEBOERSE|	f	80327	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0EPUH1||de||False	f	t	t
VASTNED OFF/IND	NL0000288934	EUR	1	|EURONEXT|	f	75199	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000288934||nl||False	f	t	t
BASF SE	DE000BASF111	EUR	1	|DEUTSCHEBOERSE|EUROSTOXX|	f	78649					100	c	0	5	BAS.DE	{1}	{3}	DEUTSCHEBOERSE#DE000BASF111||de||False	f	t	t
AT&T Inc.		USD	1	|SP500|	f	79502					100	c	0	2	T	{1}	{3}	NYSE#T||us||False	f	t	t
PPR	FR0000121485	EUR	1	|CAC|	f	75625					100	c	0	3	PP.PA	{1}	{3}	PP.PA||fr||False	f	t	t
Agilent Technologies Inc.	US00846U1016	USD	1	|SP500|	f	79703					100	c	0	2	A	{1}	{3}	NYSE#A||us||False	f	t	t
Vallourec Usines a Tubes de Lorraine Escaut et Vallourec Reunies	FR0000120354	EUR	1	|CAC|	f	75732					100	c	0	3	VK.PA	{1}	{3}	VK.PA||fr||False	f	t	t
AFLAC Inc.	US0010551028	USD	1	|SP500|	f	75829					100	c	0	2	AFL	{1}	{3}	NYSE#AFL||us||False	f	t	t
AmerisourceBergen Corp.		USD	1	|SP500|	f	75325					100	c	0	2	ABC	{1}	{3}	NYSE#ABC||us||False	f	t	t
AON Corporation		USD	1	|SP500|	f	75872					100	c	0	2	AON	{1}	{3}	NYSE#AON||us||False	f	t	t
Ameren Corp.		USD	1	|SP500|	f	75462					100	c	0	2	AEE	{1}	{3}	NYSE#AEE||us||False	f	t	t
Abercrombie & Fitch Co.		USD	1	|SP500|	f	75638					100	c	0	2	ANF	{1}	{3}	NYSE#ANF||us||False	f	t	t
Applied Materials Inc.	US0382221051	USD	1	|NASDAQ100|SP500|	f	75748					100	c	0	2	AMAT	{1}	{3}	AMAT||us||False	f	t	t
Veolia Environnement	FR0000124141	EUR	1	|CAC|	f	77628					100	c	0	3	VIE.PA	{1}	{3}	VIE.PA||fr||False	f	t	t
Assurant Inc.		USD	1	|SP500|	f	77739					100	c	0	2	AIZ	{1}	{3}	NYSE#AIZ||us||False	f	t	t
Archer Daniels Midland Co.		USD	1	|SP500|	f	78110					100	c	0	2	ADM	{1}	{3}	NYSE#ADM||us||False	f	t	t
BAYER AG	DE000BAY0017	EUR	1	|DAX|DEUTSCHEBOERSE|EUROSTOXX|	f	78687					100	c	0	5	BAYN.DE	{1}	{3}	DEUTSCHEBOERSE#DE000BAY0017||de||False	f	t	t
BMW AG St	DE0005190003	EUR	1	|DAX|DEUTSCHEBOERSE|EUROSTOXX|	f	78751					100	c	0	5	BMW.DE	{1}	{3}	DEUTSCHEBOERSE#DE0005190003||de||False	f	t	t
ENI	IT0003132476	EUR	1	|EUROSTOXX|	f	75715					100	c	0	6	ENI.MI	{1}	{3}	ENI.MI||it||False	f	t	t
DANONE	FR0000120644	EUR	1	|CAC|EURONEXT|EUROSTOXX|	f	79374					100	c	0	3	BN.PA	{1}	{3}	EURONEXT#FR0000120644||fr||False	f	t	t
SAINT GOBAIN	FR0000125007	EUR	1	|CAC|EURONEXT|EUROSTOXX|	f	75700					100	c	0	3	SGO.PA	{1}	{3}	EURONEXT#FR0000125007||fr||False	f	t	t
UNIBAIL-RODAMCO	FR0000124711	EUR	1	|CAC|EURONEXT|EUROSTOXX|	f	81276					100	c	0	3	UL.PA	{1}	{3}	EURONEXT#FR0000124711||fr||False	f	t	t
Wynn Resorts Ltd.	US9831341071	USD	1	|NASDAQ100|SP500|	f	77603					100	c	0	2	WYNN	{1}	{3}	WYNN||us||False	f	t	t
FERROVIAL	ES0118900010	EUR	1	|IBEX|MERCADOCONTINUO|	t	78908					100	c	0	1	FER.MC	{1}	{3}	MC#ES0118900010||es||False	f	f	t
GRIFOLS	ES0171996012	EUR	1	|IBEX|MERCADOCONTINUO|	t	79142					100	c	0	1	GRF.MC	{1}	{3}	MC#ES0171996012||es||False	f	f	t
INDRA A	ES0118594417	EUR	1	|IBEX|MERCADOCONTINUO|	f	79197					100	c	0	1	IDR.MC	{1}	{3}	MC#ES0118594417||es||False	f	f	t
MAPFRE	ES0124244E34	EUR	1	|IBEX|MERCADOCONTINUO|	t	79244					100	c	0	1	MAP.MC	{1}	{3}	MC#ES0124244E34||es||False	f	f	t
Daimler AG	DE0007100000	EUR	1	|DAX|DEUTSCHEBOERSE|EUROSTOXX|	t	79204					100	c	0	5	DAI.DE	{1}	{3}	DEUTSCHEBOERSE#DE0007100000||de||False	f	f	t
BBVA FON-PLAZO 2013 F	ES0115164008	EUR	2	|f_es_0014|f_es_BMF|	f	74858	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115164008||es||False	f	t	t
BBVA BOLSA INDICE JAPON (CUBIERTO)	ES0115160030	EUR	2	|f_es_0014|f_es_BMF|	f	75209	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115160030||es||False	f	t	t
BBVA DESTACADOS BP, FI	ES0113279006	EUR	2	|f_es_0014|f_es_BMF|	f	75215	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113279006||es||False	f	t	t
BBVA EXTRA 10	ES0113969036	EUR	2	|f_es_0014|f_es_BMF|	f	75293	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113969036||es||False	f	t	t
BBVA EUSKOFONDO	ES0113994034	EUR	2	|f_es_0014|f_es_BMF|	f	75390	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113994034||es||False	f	t	t
IBERCAJA CASH 3	ES0147035036	EUR	2	|BMF|0084|	f	76515	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147035036||es||False	f	f	t
BBVA PLAN RENTAS 2012 F	ES0113428033	EUR	2	|f_es_0014|f_es_BMF|	f	79025	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113428033||es||False	f	t	t
BBVA CONSOLIDA GARANTIZADO 3	ES0125461030	EUR	2	|f_es_0014|f_es_BMF|	f	79030	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125461030||es||False	f	t	t
BBVA FON-PLAZO 2012 C	ES0113926036	EUR	2	|f_es_0014|f_es_BMF|	f	79031	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113926036||es||False	f	t	t
BBVA GARANTIZADO 5X5	ES0113552030	EUR	2	|f_es_0014|f_es_BMF|	f	79032	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113552030||es||False	f	t	t
BBVA INVERSION EUROPA II	ES0113854030	EUR	2	|f_es_0014|f_es_BMF|	f	79033	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113854030||es||False	f	t	t
FONDO LIQUIDEZ	ES0137987006	EUR	2	|f_es_0014|f_es_BMF|	f	79913	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137987006||es||False	f	t	t
FONDO DE PERMANENCIA	ES0147609038	EUR	2	|f_es_0014|f_es_BMF|	f	80491	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147609038||es||False	f	t	t
METROPOLIS RENTA	ES0162819033	EUR	2	|f_es_0014|f_es_BMF|	f	80575	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162819033||es||False	f	t	t
MULTIACTIVO GLOBAL	ES0164977037	EUR	2	|f_es_0014|f_es_BMF|	f	80579	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164977037||es||False	f	t	t
QUALITY CARTERA CONSERVADORA BP	ES0172273007	EUR	2	|f_es_0014|f_es_BMF|	f	80677	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0172273007||es||False	f	t	t
QUALITY BRIC	ES0172272033	EUR	2	|f_es_0014|f_es_BMF|	f	80683	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0172272033||es||False	f	t	t
QUALITY CARTERA DECIDIDA BP	ES0157663008	EUR	2	|f_es_0014|f_es_BMF|	f	80685	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157663008||es||False	f	t	t
HERCULES MONETARIO PLUS	ES0144083039	EUR	2	|f_es_0014|f_es_BMF|	f	80740	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0144083039||es||False	f	t	t
LEASETEN RENTA FIJA CORTO	ES0158022030	EUR	2	|f_es_0014|f_es_BMF|	f	81204	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158022030||es||False	f	t	t
QUALITY COMMODITIES	ES0172243000	EUR	2	|f_es_0014|f_es_BMF|	f	81410	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0172243000||es||False	f	t	t
QUALITY MEJORES IDEAS,	ES0110119031	EUR	2	|f_es_0014|f_es_BMF|	f	81411	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110119031||es||False	f	t	t
QUALITY SELECCION EMERGENTES	ES0172262000	EUR	2	|f_es_0014|f_es_BMF|	f	81412	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0172262000||es||False	f	t	t
Abertis Infraestructuras S.A.	ES0111845014	EUR	1	|IBEX|MERCADOCONTINUO|	t	78269					100	c	0	1	ABE.MC	{1}	{3}	MC#ES0111845014||es||False	f	f	t
TEC.REUNIDAS	ES0178165017	EUR	1	|IBEX|MERCADOCONTINUO|	t	79361					100	c	0	1	TRE.MC	{1}	{3}	MC#ES0178165017||es||False	f	f	t
BME	ES0115056139	EUR	1	|IBEX|MERCADOCONTINUO|	t	80840					100	c	0	1	BME.MC	{1}	{3}	MC#ES0115056139||es||False	f	f	t
Banco Santander	ES0113900J37	EUR	1	|EUROSTOXX|IBEX|MERCADOCONTINUO|	t	81105					100	c	0	1	SAN.MC	{1}	{3}	MC#ES0113900J37||es||False	f	f	t
BANCO POPULAR	ES0113790531	EUR	1	|IBEX|MERCADOCONTINUO|	t	81103					100	c	0	1	POP.MC	{1}	{3}	MC#ES0113790531||es||False	f	f	t
CAIXABANK	ES0140609019	EUR	1	|IBEX|MERCADOCONTINUO|	f	81113					100	c	0	1	CABK.MC	{1}	{3}	MC#ES0140609019||es||False	f	f	t
EBRO FOODS S.A.	ES0112501012	EUR	1	|IBEX|MERCADOCONTINUO|	t	81115					100	c	0	1	EBRO.MC	{1}	{3}	MC#ES0112501012||es||False	f	f	t
LYXOR XBEAR ES50	FR0010424143	EUR	4	|e_fr_LYXOR|	t	81092					100	p	2	3	BXX.PA	{1}	{3}	BXX.PA||fr||False	f	f	t
ACC.IBEX ETF	ES0105336038	EUR	4	|MERCADOCONTINUO|	t	81440					100	c	0	1	BBVAI.MC	{1}	\N	MC#ES0105336038||es||False	f	f	t
Clínica Baviera	ES0119037010	EUR	1	|MERCADOCONTINUO|	t	81448					100	c	0	1	CBAV.MC	{1}	{3}	MC#ES0119037010||es||False	f	f	t
IBERCAJA INTERNACIONAL	ES0147184032	EUR	2	|BMF|0084|	f	76053	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147184032||es||False	f	f	t
CAAM Multifondo VaR 6 FI	ES0162943031	EUR	2	|f_es_BMF|	f	74864					100	c	0	1	None	{2}	\N	ES0162943031||None||False	f	t	t
CAI Ahorro Renta Fija 2 FI	ES0115401038	EUR	2	|f_es_BMF|	f	74878					100	c	0	1	None	{2}	\N	ES0115401038||None||False	f	t	t
CAIXA CATALUNYA BOLSA 11 FI	ES0115286033	EUR	2	|f_es_BMF|	f	74882					100	c	0	1	None	{2}	\N	ES0115286033||None||False	f	t	t
IBERCAJA RENTA	ES0147166039	EUR	2	|BMF|0084|	f	76102	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147166039||es||False	f	f	t
DEPOSITO BARCLAYS	\N	EUR	\N	\N	f	-4	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	DEPOSITO BARCLAYS||es||True	f	f	f
DEPOSITO IBERCAJA	\N	EUR	\N	\N	f	-5	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	DEPOSITO IBERCAJA||es||True	f	f	f
Call IBEX 35 inLine | 8000 € | 15/09/11 | I0026	FR0011038900	EUR	5	|SGW|	f	75259	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0026||fr||False	f	f	t
BBV RENTA FIM	\N	EUR	\N	\N	f	75284	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	BBV RENTA FIM||es||True	f	f	t
ALDIDE S.A.		EUR	1		f	-1					100	c	0	1	None	\N	\N	ALDIDE||es||True	t	f	f
Baker Hughes Inc.	US0572241075	USD	1	|SP500|	f	76650					100	c	0	2	BHI	{1}	{3}	NYSE#BHI||us||False	f	t	t
Ball Corp.	US0584981064	USD	1	|SP500|	f	78830					100	c	0	2	BLL	{1}	{3}	NYSE#BLL||us||False	f	t	t
Bank of America Corp.	US0605051046	USD	1	|SP500|	f	77328					100	c	0	2	BAC	{1}	{3}	NYSE#BAC||us||False	f	t	t
Bank of New York Mellon Corp.	US0640581007	USD	1	|SP500|	f	75806					100	c	0	2	BK	{1}	{3}	NYSE#BK||us||False	f	t	t
C.R. Bard Inc.	US0673831097	USD	1	|SP500|	f	76990					100	c	0	2	BCR	{1}	{3}	NYSE#BCR||us||False	f	t	t
Baxter International Inc.	US0718131099	USD	1	|SP500|	f	75786					100	c	0	2	BAX	{1}	{3}	NYSE#BAX||us||False	f	t	t
BB&T CORPORATION	US0549371070	USD	1	|SP500|	f	74824					100	c	0	2	BBT	{1}	{3}	NYSE#BBT||us||False	f	t	t
Beam Inc.	US0737301038	USD	1	|SP500|	f	77904					100	c	0	2	BEAM	{1}	{3}	NYSE#BEAM||us||False	f	t	t
FAIVELEY TRANSPORT	FR0000053142	EUR	1	|EURONEXT|	f	79177	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000053142||fr||False	f	t	t
Eaton Corp.	\N	USD	1	\N	f	74847	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ETN||us||False	f	t	t
DWS CAPITAL IV	ES0125809030	EUR	2	|f_es_BMF|	f	74973					100	c	0	1	None	{2}	\N	ES0125809030||None||False	f	t	t
BANKINTER FONDTESORO LARGO P.	ES0114831037	EUR	2	|f_es_0055|f_es_BMF|	f	75648	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114831037||es||False	f	t	t
BANKINTER RENTA DINAMICA	ES0114860036	EUR	2	|f_es_0055|f_es_BMF|	f	75677	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114860036||es||False	f	t	t
FONDO BANKINTER EUROSTOXX 55 GARANTIZADO	ES0114880034	EUR	2	|f_es_0055|f_es_BMF|	f	75815	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114880034||es||False	f	t	t
FONDO BANKINTER HONG KONG GARANTIZADO	ES0114795034	EUR	2	|f_es_0055|f_es_BMF|	f	75816	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114795034||es||False	f	t	t
FONDO BK CESTA ESPAÑOLA GARANTIZADO	ES0114785035	EUR	2	|f_es_0055|f_es_BMF|	f	75817	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114785035||es||False	f	t	t
BK MEMORIA EUROPA GARANTIZADO	ES0138955036	EUR	2	|f_es_0055|f_es_BMF|	f	75818	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138955036||es||False	f	t	t
FONDO BK SUMA TRIMESTRAL GARANTIZADO	ES0113816039	EUR	2	|f_es_0055|f_es_BMF|	f	75866	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113816039||es||False	f	t	t
FONDO BK TRIPLE SUMA GARANTIZADO	ES0113777033	EUR	2	|f_es_0055|f_es_BMF|	f	75867	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113777033||es||False	f	t	t
FONDO TELEFONICO CORTO PLAZO	ES0138953031	EUR	2	|f_es_0055|f_es_BMF|	f	75959	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138953031||es||False	f	t	t
BANKINTER GESTION ABIERTA	ES0114867031	EUR	2	|f_es_0055|f_es_BMF|	f	75993	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114867031||es||False	f	t	t
BANKINTER GESTION AMBIENTAL	ES0125622037	EUR	2	|f_es_0055|f_es_BMF|	f	75994	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125622037||es||False	f	t	t
BANKINTER HORIZONTE 2019	ES0164527006	EUR	2	|f_es_0055|f_es_BMF|	f	75995	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164527006||es||False	f	t	t
BANKINTER INFLACION PLUS	ES0161361037	EUR	2	|f_es_0055|f_es_BMF|	f	75996	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0161361037||es||False	f	t	t
BANKINTER SMALL-CAPS MID	ES0114784038	EUR	2	|f_es_0055|f_es_BMF|	f	76024	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114784038||es||False	f	t	t
BANKINTER SOLIDARIDAD	ES0115157036	EUR	2	|f_es_0055|f_es_BMF|	f	76049	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115157036||es||False	f	t	t
BANKINTER LONG SHORT	ES0115156038	EUR	2	|f_es_0055|f_es_BMF|	f	76313	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115156038||es||False	f	t	t
BANKINTER QUANT	ES0114755038	EUR	2	|f_es_0055|f_es_BMF|	f	76414	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114755038||es||False	f	t	t
BK FONDO MONETARIO	ES0114868039	EUR	2	|f_es_0055|f_es_BMF|	f	76421	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114868039||es||False	f	t	t
Avery Dennison Corp.		USD	1	|SP500|	f	77274					100	c	0	2	AVY	{1}	{3}	NYSE#AVY||us||False	f	t	t
Avon Products Inc.	US0543031027	USD	1	|SP500|	f	75944					100	c	0	2	AVP	{1}	{3}	NYSE#AVP||us||False	f	t	t
BK INDICE EUROPEO 50	ES0114754031	EUR	2	|f_es_0055|f_es_BMF|	f	76623	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114754031||es||False	f	t	t
BK SELECCION BASICOS GARANTIZADO	ES0113585006	EUR	2	|f_es_0055|f_es_BMF|	f	76670	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113585006||es||False	f	t	t
BK SELECCION BONOS CORPORATIVOS	ES0114857032	EUR	2	|f_es_0055|f_es_BMF|	f	76674	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114857032||es||False	f	t	t
BANKINTER EMERGENTES	ES0113923033	EUR	2	|f_es_0055|f_es_BMF|	f	76852	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113923033||es||False	f	t	t
BANKINTER INDICE AMERICA	ES0114763032	EUR	2	|f_es_0055|f_es_BMF|	f	76916	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114763032||es||False	f	t	t
BANKINTER INDICE JAPON	ES0114104039	EUR	2	|f_es_0055|f_es_BMF|	f	76917	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114104039||es||False	f	t	t
BANKINTER BOLSA GLOBAL	ES0127188037	EUR	2	|f_es_0055|f_es_BMF|	f	77116	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0127188037||es||False	f	t	t
BANKINTER BONOS LARGO PLAZO	ES0114837034	EUR	2	|f_es_0055|f_es_BMF|	f	77118	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114837034||es||False	f	t	t
BANKINTER BRAMEX GARANTIZADO	ES0162940037	EUR	2	|f_es_0055|f_es_BMF|	f	77186	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162940037||es||False	f	t	t
BANKINTER CORPORATIVO	ES0161362035	EUR	2	|f_es_0055|f_es_BMF|	f	77191	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0161362035||es||False	f	t	t
BANKINTER DINERO 1	ES0113921037	EUR	2	|f_es_0055|f_es_BMF|	f	77195	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113921037||es||False	f	t	t
BANKINTER DIVIDENDO EUROPA	ES0114802038	EUR	2	|f_es_0055|f_es_BMF|	f	77203	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114802038||es||False	f	t	t
BANKINTER PRIVATE EQUITY INDEX	ES0137722007	EUR	2	|f_es_0055|f_es_BMF|	f	77240	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137722007||es||False	f	t	t
BK MIXTO EUROPA 50	ES0114877030	EUR	2	|f_es_0055|f_es_BMF|	f	77477	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114877030||es||False	f	t	t
BK PEQUENAS COMPANIAS	ES0114764030	EUR	2	|f_es_0055|f_es_BMF|	f	77482	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114764030||es||False	f	t	t
FONDO BK EUROPA GARANTIZADO	ES0113776035	EUR	2	|f_es_0055|f_es_BMF|	f	77853	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113776035||es||False	f	t	t
BANKINTER HORIZONTE 2029	ES0164585004	EUR	2	|f_es_0055|f_es_BMF|	f	77856	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164585004||es||False	f	t	t
BK EURO DIVIDENDO GARANTIZADO	ES0114791033	EUR	2	|f_es_0055|f_es_BMF|	f	77880	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114791033||es||False	f	t	t
BANKINTER INFLACION NACIONAL GAR	ES0113584009	EUR	2	|f_es_0055|f_es_BMF|	f	77882	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113584009||es||False	f	t	t
FONDO BK RENTA FIJA GARANTIZADO 2012	ES0164542005	EUR	2	|f_es_0055|f_es_BMF|	f	77978	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164542005||es||False	f	t	t
BK BOLSA EURIBEX	ES0138962032	EUR	2	|f_es_0055|f_es_BMF|	f	78268	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138962032||es||False	f	t	t
BK BOLSA EUROPA	ES0114866033	EUR	2	|f_es_0055|f_es_BMF|	f	78271	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114866033||es||False	f	t	t
BK INDICE GANADOR 7	ES0138954039	EUR	2	|f_es_0055|f_es_BMF|	f	78380	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138954039||es||False	f	t	t
BK 2012 GARANTIZADO	ES0114796032	EUR	2	|f_es_0055|f_es_BMF|	f	78459	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114796032||es||False	f	t	t
BK BOLSA ESPAÑA 2	ES0125621039	EUR	2	|f_es_0055|f_es_BMF|	f	78493	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125621039||es||False	f	t	t
BK BOLSA ESPAñA	ES0125631038	EUR	2	|f_es_0055|f_es_BMF|	f	78498	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125631038||es||False	f	t	t
BK SECTOR ENERGIA	ES0114806039	EUR	2	|f_es_0055|f_es_BMF|	f	78577	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114806039||es||False	f	t	t
BK SECTOR TELECOMUNICACIONES	ES0114797030	EUR	2	|f_es_0055|f_es_BMF|	f	78579	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114797030||es||False	f	t	t
BK KILIMANJARO	ES0113550034	EUR	2	|f_es_0055|f_es_BMF|	f	78721	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113550034||es||False	f	t	t
BK MIXTO EUROPA 20	ES0114793039	EUR	2	|f_es_0055|f_es_BMF|	f	78742	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114793039||es||False	f	t	t
BANKINTER GARANTIZADO SUPERACION	ES0133595035	EUR	2	|f_es_0055|f_es_BMF|	f	78744	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133595035||es||False	f	t	t
BANKINTER GAR.SUPERACION 2	ES0114876032	EUR	2	|f_es_0055|f_es_BMF|	f	78747	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114876032||es||False	f	t	t
BK RENTA VARIABLE EUROPEA	ES0114879036	EUR	2	|f_es_0055|f_es_BMF|	f	78754	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114879036||es||False	f	t	t
BANKINTER DEUDA PUBLICA	ES0114786033	EUR	2	|f_es_0055|f_es_BMF|	f	78922	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114786033||es||False	f	t	t
BANKINTER DEUDA PUBLICA II	ES0114858030	EUR	2	|f_es_0055|f_es_BMF|	f	78930	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114858030||es||False	f	t	t
BANKINTER ACUERDO GES.CONS.EMPRE	ES0134612037	EUR	2	|f_es_0055|f_es_BMF|	f	79295	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0134612037||es||False	f	t	t
FONDO BK EMPRESAS CORTO PLAZO	ES0110053032	EUR	2	|f_es_0055|f_es_BMF|	f	79331	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110053032||es||False	f	t	t
FONDO BK EURO TELECOS GARANTIZADO	ES0164950000	EUR	2	|f_es_0055|f_es_BMF|	f	79332	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164950000||es||False	f	t	t
FONDO BANKINTER CONSOLIDACION GARANTIZAD	ES0113815031	EUR	2	|f_es_0055|f_es_BMF|	f	79454	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113815031||es||False	f	t	t
FONDO BANKINTER MULTIFONDO GARANTIZADO	ES0125632036	EUR	2	|f_es_0055|f_es_BMF|	f	79486	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125632036||es||False	f	t	t
BANKINTER BRIC PLUS 2 GARANTIZAD	ES0114838032	EUR	2	|f_es_0055|f_es_BMF|	f	79488	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114838032||es||False	f	t	t
FONDO BK EUROSTOXX 2014 GARANTIZADO	ES0164951008	EUR	2	|f_es_0055|f_es_BMF|	f	80361	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164951008||es||False	f	t	t
FONDO BANKINTER EEUU NASDAQ 100	ES0114105036	EUR	2	|f_es_0055|f_es_BMF|	f	80635	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114105036||es||False	f	t	t
FONDO BANKINTER RENTA FIJA 6 GARANTIZADO	ES0164541007	EUR	2	|f_es_0055|f_es_BMF|	f	80637	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164541007||es||False	f	t	t
BANKINTER BRIC PLUS GARANTIZADO	ES0114874037	EUR	2	|f_es_0055|f_es_BMF|	f	80638	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114874037||es||False	f	t	t
BK ACUERDO DE GESTION DIN.EMPRES	ES0134613035	EUR	2	|f_es_0055|f_es_BMF|	f	80865	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0134613035||es||False	f	t	t
BK ACUERDO GESTION MODERADO EMPR	ES0114696034	EUR	2	|f_es_0055|f_es_BMF|	f	80874	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114696034||es||False	f	t	t
FONDO BK MATERIAS PRIMAS	ES0114103031	EUR	2	|f_es_0055|f_es_BMF|	f	80875	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114103031||es||False	f	t	t
BK GRAN RESERVA 40 ANIVERSARIO	ES0114102033	EUR	2	|f_es_0055|f_es_BMF|	f	80877	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114102033||es||False	f	t	t
BK GRAN RESERVA 40 ANIVERS.III	ES0114875034	EUR	2	|f_es_0055|f_es_BMF|	f	80878	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114875034||es||False	f	t	t
FONDO BK MULTISECTOR GARANTIZADO	ES0114878038	EUR	2	|f_es_0055|f_es_BMF|	f	80879	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114878038||es||False	f	t	t
FONDO BK RENTA FIJA 2014 GARANTIZADO	ES0113983003	EUR	2	|f_es_0055|f_es_BMF|	f	80880	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113983003||es||False	f	t	t
BANKINTER IBEX DEFENSA GARANTIZA	ES0114783030	EUR	2	|f_es_0055|f_es_BMF|	f	80881	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114783030||es||False	f	t	t
ALHAMBRA	ES0108207038	EUR	2	|f_es_0043|f_es_BMF|	f	77329	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108207038||es||False	f	t	t
RENTA 4 ACCIONES MIXTO	ES0173286032	EUR	2	|f_es_0043|f_es_BMF|	f	81393	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173286032||es||False	f	t	t
RENTA 4 ASIA	ES0173313034	EUR	2	|f_es_0043|f_es_BMF|	f	81395	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173313034||es||False	f	t	t
RENTA 4 BOLSA	ES0173394034	EUR	2	|f_es_0043|f_es_BMF|	f	81396	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173394034||es||False	f	t	t
RENTA 4 CARTERA	ES0173362031	EUR	2	|f_es_0043|f_es_BMF|	f	81409	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173362031||es||False	f	t	t
R4 CTA TRADING	ES0173857030	EUR	2	|f_es_0043|f_es_BMF|	f	81415	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173857030||es||False	f	t	t
RENTA 4 DELTA	ES0173317035	EUR	2	|f_es_0043|f_es_BMF|	f	81419	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173317035||es||False	f	t	t
RENTA 4 EUROBOLSA	ES0173385032	EUR	2	|f_es_0043|f_es_BMF|	f	81420	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173385032||es||False	f	t	t
RENTA 4 EUROPA ESTE	ES0128517036	EUR	2	|f_es_0043|f_es_BMF|	f	81431	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0128517036||es||False	f	t	t
RENTA 4 FONDTESORO	ES0173372030	EUR	2	|f_es_0043|f_es_BMF|	f	81432	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173372030||es||False	f	t	t
RENTA 4 GLOBAL	ES0173392038	EUR	2	|f_es_0043|f_es_BMF|	f	81433	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173392038||es||False	f	t	t
RENTA 4 JAPON	ES0173356033	EUR	2	|f_es_0043|f_es_BMF|	f	81434	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173356033||es||False	f	t	t
RENTA 4 LATINOAMERICA	ES0173320039	EUR	2	|f_es_0043|f_es_BMF|	f	81435	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173320039||es||False	f	t	t
RENTA 4 TECNOLOGIA	ES0173364037	EUR	2	|f_es_0043|f_es_BMF|	f	81437	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173364037||es||False	f	t	t
Bemis Co. Inc.		USD	1	|SP500|	f	76557					100	c	0	2	BMS	{1}	{3}	NYSE#BMS||us||False	f	t	t
Big Lots Inc.		USD	1	|SP500|	f	78936					100	c	0	2	BIG	{1}	{3}	NYSE#BIG||us||False	f	t	t
VAA-V.ALEGRE-FUSAO	PTVAA9AE0002	EUR	1	|EURONEXT|	f	80156	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTVAA9AE0002||pt||False	f	t	t
LISGRAFICA	PTLIG0AE0002	EUR	1	|EURONEXT|	f	80206	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTLIG0AE0002||pt||False	f	t	t
COFINA,SGPS	PTCFN0AE0003	EUR	1	|EURONEXT|	f	80298	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTCFN0AE0003||pt||False	f	t	t
EDP RENOVAVEIS	ES0127797019	EUR	1	|EURONEXT|	f	80403	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#ES0127797019||pt||False	f	t	t
GALP ENERGIA-NOM	PTGAL0AM0009	EUR	1	|EURONEXT|	f	80503	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTGAL0AM0009||pt||False	f	t	t
MEDIA CAPITAL	PTGMC0AM0003	EUR	1	|EURONEXT|	f	80639	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTGMC0AM0003||pt||False	f	t	t
OREY ANTUNES ESC.	PTORE0AM0002	EUR	1	|EURONEXT|	f	80716	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTORE0AM0002||pt||False	f	t	t
P.TELECOM	PTPTC0AM0009	EUR	1	|EURONEXT|	f	80727	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTPTC0AM0009||pt||False	f	t	t
SONAE	PTSON0AM0001	EUR	1	|EURONEXT|	f	81213	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTSON0AM0001||pt||False	f	t	t
SONAE CAPITAL	PTSNP0AE0008	EUR	1	|EURONEXT|	f	81214	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTSNP0AE0008||pt||False	f	t	t
SONAECOM,SGPS	PTSNC0AM0006	EUR	1	|EURONEXT|	f	81241	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTSNC0AM0006||pt||False	f	t	t
SPORTING	PTSCP0AM0001	EUR	1	|EURONEXT|	f	81244	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTSCP0AM0001||pt||False	f	t	t
TOYOTA CAETANO	PTSCT0AP0018	EUR	1	|EURONEXT|	f	81263	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTSCT0AP0018||pt||False	f	t	t
FALA	FR0000064222	EUR	1	|EURONEXT|	f	74792	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064222||fr||False	f	t	t
Put IBEX 35 | 8750 € | 20/01/12 | B9699	FR0011083781	EUR	5	|SGW|	f	74805	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9699||fr||False	f	t	t
IGE + XAO	FR0000030827	EUR	1	|EURONEXT|	f	74806	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000030827||fr||False	f	t	t
OXYMETAL BS	FR0010489815	EUR	1	|EURONEXT|	f	74807	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010489815||fr||False	f	t	t
Call IBEX 35 inLine | 7500 € | 14/03/12 | I0050	FR0011117993	EUR	5	|SGW|	f	74815	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0050||fr||False	f	t	t
Put IBEX 35 | 8250 € | 19/08/11 | B6053	FR0011017789	EUR	5	|SGW|	f	74817	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B6053||fr||False	f	t	t
Put IBEX 35 | 9250 € | 17/02/12 | B9711	FR0011083906	EUR	5	|SGW|	f	74818	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9711||fr||False	f	t	t
ARTOIS NOM.	FR0000076952	EUR	1	|EURONEXT|	f	74820	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000076952||fr||False	f	t	t
Put IBEX 35 | 8500 € | 17/06/11 | B1793	FR0010936153	EUR	5	|SGW|	f	74822	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B1793||fr||False	f	t	t
PARIS-ORLEANS	FR0000031684	EUR	1	|EURONEXT|	f	74825	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000031684||fr||False	f	t	t
Call IBEX 35 | 9500 € | 21/09/12 | C3291	FR0011168319	EUR	5	|SGW|	f	74826	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3291||fr||False	f	t	t
Put IBEX 35 | 10750 € | 19/08/11 | B6058	FR0011017839	EUR	5	|SGW|	f	74856	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B6058||fr||False	f	t	t
JK Wohnbau AG	DE000A1E8H38	EUR	1	|DEUTSCHEBOERSE|	f	74769	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1E8H38||de||False	f	t	t
ASML HOLDING	NL0006034001	EUR	1	|EURONEXT|	f	74785	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0006034001||nl||False	f	t	t
Call IBEX 35 | 9750 € | 20/05/11 | B4724	FR0010984427	EUR	5	|SGW|	f	74859	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4724||fr||False	f	t	t
Put IBEX 35 | 6500 € | 21/09/12 | C3295	FR0011168350	EUR	5	|SGW|	f	74860	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3295||fr||False	f	t	t
MEDASYS DS3	FR0011162528	EUR	1	|EURONEXT|	f	74790	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011162528||fr||False	f	t	t
LAGARDERE ACT.BRO.	MC0000120790	EUR	1	|EURONEXT|	f	78968	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#MC0000120790||fr||False	f	t	t
ASSYSTEM BSAR 0713	FR0010356535	EUR	1	|EURONEXT|	f	78999	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010356535||fr||False	f	t	t
BBVA 105 Ibex II FI	ES0184931030	EUR	2	|f_es_BMF|	f	74778					100	c	0	1	None	{2}	\N	ES0184931030||None||False	f	t	t
BANKOA IBEX GARANTIZADO	ES0163028006	EUR	2	|f_es_BMF|	f	74775					100	c	0	1	None	{2}	\N	ES0163028006||None||False	f	t	t
SOMFY SA	FR0000120495	EUR	1	|EURONEXT|	f	74852	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000120495||fr||False	f	t	t
DERICHEBOURG	FR0000053381	EUR	1	|EURONEXT|	f	79000	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000053381||fr||False	f	t	t
ECA	FR0010099515	EUR	1	|EURONEXT|	f	79011	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010099515||fr||False	f	t	t
EDENRED	FR0010908533	EUR	1	|EURONEXT|	f	79019	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010908533||fr||False	f	t	t
Hang Seng	XC0009692762	CNY	3	\N	t	81091	\N	\N	\N	\N	100	c	0	8	^HSI	{1}	{3}	^HSI||cn||False	f	t	t
CSCOM BS11A	FR0010325019	EUR	1	|EURONEXT|	f	79175	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010325019||fr||False	f	t	t
GANTOIS	FR0000064214	EUR	1	|EURONEXT|	f	79199	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064214||fr||False	f	t	t
SYNERGIE	FR0000032658	EUR	1	|EURONEXT|	f	79219	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000032658||fr||False	f	t	t
SYSTAR	FR0000052854	EUR	1	|EURONEXT|	f	79224	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000052854||fr||False	f	t	t
SYSTRAN	FR0004109197	EUR	1	|EURONEXT|	f	79225	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004109197||fr||False	f	t	t
GDS (S) RUSAL	US9098832093	EUR	1	|EURONEXT|	f	79236	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US9098832093||fr||False	f	t	t
GDS MOULINS STRAS.	FR0000064180	EUR	1	|EURONEXT|	f	79237	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064180||fr||False	f	t	t
KESA ELECTRICALS	GB0033040113	EUR	1	|EURONEXT|	f	79253	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#GB0033040113||fr||False	f	t	t
KEYRUS	FR0004029411	EUR	1	|EURONEXT|	f	79258	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004029411||fr||False	f	t	t
KEYRUS BSAAR 2014	FR0010645200	EUR	1	|EURONEXT|	f	79264	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010645200||fr||False	f	t	t
MECELEC BSA 1113	FR0010957621	EUR	1	|EURONEXT|	f	79265	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010957621||fr||False	f	t	t
MEDEA	FR0000063323	EUR	1	|EURONEXT|	f	79268	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000063323||fr||False	f	t	t
NOVAGALI PHARMA	FR0010915553	EUR	1	|EURONEXT|	f	79296	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010915553||fr||False	f	t	t
NYSE EURONEXT	US6294911010	EUR	1	|EURONEXT|	f	79309	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US6294911010||fr||False	f	t	t
Put IBEX 35 | 9250 € | 18/05/12 | C2139	FR0011145473	EUR	5	|SGW|	f	79313	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C2139||fr||False	f	t	t
Put IBEX 35 | 9750 € | 18/05/12 | C2140	FR0011145481	EUR	5	|SGW|	f	79316	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C2140||fr||False	f	t	t
Put IBEX 35 | 10250 € | 18/05/12 | C2141	FR0011145499	EUR	5	|SGW|	f	79319	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C2141||fr||False	f	t	t
Call IBEX 35 | 6500 € | 15/06/12 | C1126	FR0011124312	EUR	5	|SGW|	f	79320	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1126||fr||False	f	t	t
PLANT.TERRES ROUG.	LU0012113584	EUR	1	|EURONEXT|	f	79334	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#LU0012113584||fr||False	f	t	t
INDEX MULTIMEDIA	FR0004061513	EUR	1	|EURONEXT|	f	79348	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004061513||fr||False	f	t	t
ITS GROUP BSAR	FR0010718379	EUR	1	|EURONEXT|	f	79353	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010718379||fr||False	f	t	t
DASSAULT SYSTEMES	FR0000130650	EUR	1	|EURONEXT|	f	79375	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000130650||fr||False	f	t	t
FONCIERE 6 ET 7	FR0010436329	EUR	1	|EURONEXT|	f	79376	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010436329||fr||False	f	t	t
THARREAU IND.	FR0000062739	EUR	1	|EURONEXT|	f	79390	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000062739||fr||False	f	t	t
RISC GROUP	FR0011010198	EUR	1	|EURONEXT|	f	79401	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011010198||fr||False	f	t	t
RODRIGUEZ GROUP	FR0000062994	EUR	1	|EURONEXT|	f	79402	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000062994||fr||False	f	t	t
ROLINCO	NL0000289817	EUR	1	|EURONEXT|	f	79405	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#NL0000289817||fr||False	f	t	t
RORENTO	ANN757371433	EUR	1	|EURONEXT|	f	79407	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#ANN757371433||fr||False	f	t	t
TESFRAN	FR0010358812	EUR	1	|EURONEXT|	f	79415	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010358812||fr||False	f	t	t
FONC EUR LOGISTIQ	FR0000064305	EUR	1	|EURONEXT|	f	79437	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064305||fr||False	f	t	t
FONCIER PARIS BS	FR0010980045	EUR	1	|EURONEXT|	f	79442	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010980045||fr||False	f	t	t
FONCIERE ATLAND	FR0000064362	EUR	1	|EURONEXT|	f	79455	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064362||fr||False	f	t	t
FONCIERE EURIS	FR0000038499	EUR	1	|EURONEXT|	f	79456	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000038499||fr||False	f	t	t
FONCIERE INEA	FR0010341032	EUR	1	|EURONEXT|	f	79457	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010341032||fr||False	f	t	t
FTSE 100	GB0001383545	GBP	3	\N	t	75930	\N	\N	\N	\N	100	c	0	4	^FTSE	{1}	{3}	^FTSE||en||False	f	t	t
Capgemini	FR0000125338	EUR	1	|CAC|	f	74881	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	CAP.PA||fr||False	f	t	t
Put IBEX 35 | 8750 € | 20/05/11 | B4730	FR0010984484	EUR	5	|SGW|	f	74875	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4730||fr||False	f	t	t
FONCIERE SEPRIC	FR0004031292	EUR	1	|EURONEXT|	f	79458	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004031292||fr||False	f	t	t
FONCINEAABSASEP12	FR0010964247	EUR	1	|EURONEXT|	f	79459	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010964247||fr||False	f	t	t
ALPES (COMPAGNIE)	FR0000053324	EUR	1	|EURONEXT|	f	79464	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000053324||fr||False	f	t	t
ALTAMIR AMBOISE	FR0000053837	EUR	1	|EURONEXT|	f	79466	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000053837||fr||False	f	t	t
ALTAREIT	FR0000039216	EUR	1	|EURONEXT|	f	79467	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000039216||fr||False	f	t	t
SANOFI	FR0000120578	EUR	1	|CAC|EURONEXT|EUROSTOXX|	f	79028					100	c	0	3	None	\N	\N	EURONEXT#FR0000120578||fr||False	f	t	t
ENTREP.CONTRACTING	FR0010204321	EUR	1	|EURONEXT|	f	79554	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010204321||fr||False	f	t	t
GPE GROUP PIZZORNO	FR0010214064	EUR	1	|EURONEXT|	f	79578	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010214064||fr||False	f	t	t
GRAINES VOLTZ	FR0000065971	EUR	1	|EURONEXT|	f	79579	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000065971||fr||False	f	t	t
GRAND MARNIER	FR0000038036	EUR	1	|EURONEXT|	f	79580	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000038036||fr||False	f	t	t
GROPEN BSAAR0914	FR0010518688	EUR	1	|EURONEXT|	f	79585	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010518688||fr||False	f	t	t
GROUPE CRIT	FR0000036675	EUR	1	|EURONEXT|	f	79590	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000036675||fr||False	f	t	t
GROUPE EUROTUNNEL	FR0010533075	EUR	1	|EURONEXT|	f	79591	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010533075||fr||False	f	t	t
GROUPE GORGE	FR0000062671	EUR	1	|EURONEXT|	f	79593	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000062671||fr||False	f	t	t
MOBOTIX AG	DE0005218309	EUR	1	|DEUTSCHEBOERSE|	f	74870	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005218309||de||False	f	t	t
Travel24.com AG	DE000A0L1NQ8	EUR	1	|DEUTSCHEBOERSE|	f	74983	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0L1NQ8||de||False	f	t	t
GUYENNE GASCOGNE	FR0000120289	EUR	1	|EURONEXT|	f	79598	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000120289||fr||False	f	t	t
CBO TERRITORIA	FR0010193979	EUR	1	|EURONEXT|	f	79622	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010193979||fr||False	f	t	t
DANE ELEC MEMORY	FR0000036774	EUR	1	|EURONEXT|	f	79623	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000036774||fr||False	f	t	t
DUC	FR0000036287	EUR	1	|EURONEXT|	f	79628	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000036287||fr||False	f	t	t
ELIXENS	FR0000054611	EUR	1	|EURONEXT|	f	79632	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000054611||fr||False	f	t	t
EMME	FR0004155000	EUR	1	|EURONEXT|	f	79633	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004155000||fr||False	f	t	t
ESPACE PRODUCTION	FR0004048072	EUR	1	|EURONEXT|	f	79635	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004048072||fr||False	f	t	t
GROUPE JAJ	FR0004010338	EUR	1	|EURONEXT|	f	79636	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004010338||fr||False	f	t	t
ESR	FR0000072969	EUR	1	|EURONEXT|	f	79697	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000072969||fr||False	f	t	t
ICADE	FR0000035081	EUR	1	|EURONEXT|	f	79712	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000035081||fr||False	f	t	t
ID FUTURE	FR0000060410	EUR	1	|EURONEXT|	f	79716	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060410||fr||False	f	t	t
IDI	FR0000051393	EUR	1	|EURONEXT|	f	79720	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000051393||fr||False	f	t	t
ILIAD	FR0004035913	EUR	1	|EURONEXT|	f	79721	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004035913||fr||False	f	t	t
MEDASYS DS1	FR0011162502	EUR	1	|EURONEXT|	f	79736	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011162502||fr||False	f	t	t
MEDASYS DS2	FR0011162510	EUR	1	|EURONEXT|	f	79737	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011162510||fr||False	f	t	t
NEURONES	FR0004050250	EUR	1	|EURONEXT|	f	79795	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004050250||fr||False	f	t	t
ADCSIIC122014	FR0010561985	EUR	1	|EURONEXT|	f	79835	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010561985||fr||False	f	t	t
Nikkei	\N	JPY	3	\N	t	79834	\N	\N	\N	\N	100	c	0	7	^N225	{1}	{3}	^N225||jp||False	f	t	t
CATERPILLAR CERT	BE0004402377	EUR	1	|EURONEXT|	f	74891	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0004402377||be||False	f	t	t
Put IBEX 35 | 7500 € | 16/03/12 | B9953	FR0011091420	EUR	5	|SGW|	f	74886	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9953||fr||False	f	t	t
CATERING INTL SCES	FR0000064446	EUR	1	|EURONEXT|	f	74887	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064446||fr||False	f	t	t
Call IBEX 35 | 8500 € | 18/11/11 | B9935	FR0011091248	EUR	5	|SGW|	f	74894	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9935||fr||False	f	t	t
AGRICOLE CRAU	FR0000062176	EUR	1	|EURONEXT|	f	79837	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000062176||fr||False	f	t	t
AKKA TECH. BSAAR	FR0010575563	EUR	1	|EURONEXT|	f	79838	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010575563||fr||False	f	t	t
IT LINK	FR0000072597	EUR	1	|EURONEXT|	f	79842	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000072597||fr||False	f	t	t
JACQUET METAL SCE	FR0000033904	EUR	1	|EURONEXT|	f	79845	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000033904||fr||False	f	t	t
JC DECAUX SA.	FR0000077919	EUR	1	|EURONEXT|	f	79846	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000077919||fr||False	f	t	t
KAUFMAN ET BROAD	FR0004007813	EUR	1	|EURONEXT|	f	79859	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004007813||fr||False	f	t	t
KORIAN	FR0010386334	EUR	1	|EURONEXT|	f	79888	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010386334||fr||False	f	t	t
GDF SUEZ	FR0010208488	EUR	1	|CAC|EURONEXT|EUROSTOXX|	f	79663					100	c	0	3	None	\N	\N	EURONEXT#FR0010208488||fr||False	f	t	t
AUDIKA GROUPE	FR0000063752	EUR	1	|EURONEXT|	f	79934	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000063752||fr||False	f	t	t
AUFEMININ.COM	FR0004042083	EUR	1	|EURONEXT|	f	79936	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004042083||fr||False	f	t	t
CRCAM ILLE-VIL.CCI	FR0000045213	EUR	1	|EURONEXT|	f	79939	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000045213||fr||False	f	t	t
FIN.OUEST AFRICAIN	SN0000033192	EUR	1	|EURONEXT|	f	79941	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#SN0000033192||fr||False	f	t	t
GROUPE OPEN	FR0004050300	EUR	1	|EURONEXT|	f	79944	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004050300||fr||False	f	t	t
FIPP	FR0000038184	EUR	1	|EURONEXT|	f	79945	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000038184||fr||False	f	t	t
GROUPE STERIA	FR0000072910	EUR	1	|EURONEXT|	f	79948	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000072910||fr||False	f	t	t
HF	FR0000038531	EUR	1	|EURONEXT|	f	79954	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000038531||fr||False	f	t	t
INDLE FIN.ENTREPR.	FR0000066219	EUR	1	|EURONEXT|	f	79960	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000066219||fr||False	f	t	t
AUSY	FR0000072621	EUR	1	|EURONEXT|	f	79962	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000072621||fr||False	f	t	t
BELVEDERE BSA 2006	FR0010304733	EUR	1	|EURONEXT|	f	80005	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010304733||fr||False	f	t	t
BENETEAU	FR0000035164	EUR	1	|EURONEXT|	f	80006	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000035164||fr||False	f	t	t
BISCUITS GARDEIL	FR0000065435	EUR	1	|EURONEXT|	f	80015	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000065435||fr||False	f	t	t
BONDUELLE BSAAR 14	FR0010490912	EUR	1	|EURONEXT|	f	80016	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010490912||fr||False	f	t	t
CANAL PLUS(STE ED)	FR0000125460	EUR	1	|EURONEXT|	f	80019	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000125460||fr||False	f	t	t
CAPELLI	FR0010127530	EUR	1	|EURONEXT|	f	80021	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010127530||fr||False	f	t	t
NICOX	FR0000074130	EUR	1	|EURONEXT|	f	80022	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000074130||fr||False	f	t	t
PPRNV	FR0011160233	EUR	1	|EURONEXT|	f	80025	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011160233||fr||False	f	t	t
RADIALBSARA18JUL14	FR0010485466	EUR	1	|EURONEXT|	f	80026	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010485466||fr||False	f	t	t
ASSYSTEMBSAARJUL15	FR0010630590	EUR	1	|EURONEXT|	f	80051	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010630590||fr||False	f	t	t
HIOLLE INDUSTRIES	FR0000077562	EUR	1	|EURONEXT|	f	80053	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000077562||fr||False	f	t	t
LDLC.COM	FR0000075442	EUR	1	|EURONEXT|	f	80055	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000075442||fr||False	f	t	t
MEDASYS BS2	FR0011162551	EUR	1	|EURONEXT|	f	80056	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011162551||fr||False	f	t	t
MEDASYS BS3	FR0011162577	EUR	1	|EURONEXT|	f	80057	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011162577||fr||False	f	t	t
METROLOGIC GROUP	FR0000073975	EUR	1	|EURONEXT|	f	80058	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000073975||fr||False	f	t	t
METROPOLE TV	FR0000053225	EUR	1	|EURONEXT|	f	80059	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000053225||fr||False	f	t	t
SODEXO	FR0000121220	EUR	1	|EURONEXT|	f	80094	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000121220||fr||False	f	t	t
SODIFRANCE	FR0000072563	EUR	1	|EURONEXT|	f	80099	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000072563||fr||False	f	t	t
SODITECH ING.	FR0000078321	EUR	1	|EURONEXT|	f	80102	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000078321||fr||False	f	t	t
BROOKFIELD ASSET M	CA1125851040	EUR	1	|EURONEXT|	f	74890	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#CA1125851040||nl||False	f	t	t
CAC 40	FR0003500008	EUR	3	\N	t	79694	\N	\N	\N	\N	100	c	0	3	^FCHI	{1}	{3}	^FCHI||fr||False	f	t	t
Call IBEX 35 inLine | 9000 € | 15/09/11 | I0030	FR0011038942	EUR	5	|SGW|	f	74898	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0030||fr||False	f	t	t
FONCIERE MASSENA	FR0000037210	EUR	1	|EURONEXT|	f	74904	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000037210||fr||False	f	t	t
SOFRAGI	FR0000030140	EUR	1	|EURONEXT|	f	80106	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000030140||fr||False	f	t	t
SOLUCOM	FR0004036036	EUR	1	|EURONEXT|	f	80112	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004036036||fr||False	f	t	t
SOPRA GROUP	FR0000050809	EUR	1	|EURONEXT|	f	80113	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000050809||fr||False	f	t	t
ST DUPONT	FR0000054199	EUR	1	|EURONEXT|	f	80116	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000054199||fr||False	f	t	t
TOUR EIFFEL	FR0000036816	EUR	1	|EURONEXT|	f	80127	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000036816||fr||False	f	t	t
TRIGANO	FR0005691656	EUR	1	|EURONEXT|	f	80128	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0005691656||fr||False	f	t	t
AVENIR FINANCE	FR0004152874	EUR	1	|EURONEXT|	f	80168	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004152874||fr||False	f	t	t
DASSAULT AVIATION	FR0000121725	EUR	1	|EURONEXT|	f	80178	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000121725||fr||False	f	t	t
DMS BSA D	FR0010944884	EUR	1	|EURONEXT|	f	80187	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010944884||fr||False	f	t	t
DURAN	FR0010731414	EUR	1	|EURONEXT|	f	80191	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010731414||fr||False	f	t	t
VALEO	FR0000130338	EUR	1	|EURONEXT|	f	80192	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000130338||fr||False	f	t	t
VALTECH	FR0004155885	EUR	1	|EURONEXT|	f	80194	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004155885||fr||False	f	t	t
VIRBAC	FR0000031577	EUR	1	|EURONEXT|	f	80196	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000031577||fr||False	f	t	t
LDC	FR0000053829	EUR	1	|EURONEXT|	f	80219	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000053829||fr||False	f	t	t
LVL MEDICAL GROUPE	FR0000054686	EUR	1	|EURONEXT|	f	80228	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000054686||fr||False	f	t	t
LESNXCONSTRUCTEURS	FR0004023208	EUR	1	|EURONEXT|	f	80231	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004023208||fr||False	f	t	t
CA TOULOUSE 31 CCI	FR0000045544	EUR	1	|EURONEXT|	f	80248	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000045544||fr||False	f	t	t
CNP ASSURANCES	FR0000120222	EUR	1	|EURONEXT|	f	80261	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000120222||fr||False	f	t	t
COCA-COLA ENTER	US19122T1097	EUR	1	|EURONEXT|	f	80263	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US19122T1097||fr||False	f	t	t
MR BRICOLAGE	FR0004034320	EUR	1	|EURONEXT|	f	80272	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004034320||fr||False	f	t	t
NEOPOST	FR0000120560	EUR	1	|EURONEXT|	f	80276	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000120560||fr||False	f	t	t
NEXANS	FR0000044448	EUR	1	|EURONEXT|	f	80279	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000044448||fr||False	f	t	t
OXIS INTL	US6918294025	EUR	1	|EURONEXT|	f	80285	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US6918294025||fr||False	f	t	t
COFITEM-COFIMUR	FR0000034431	EUR	1	|EURONEXT|	f	80300	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000034431||fr||False	f	t	t
COLAS	FR0000121634	EUR	1	|EURONEXT|	f	80305	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000121634||fr||False	f	t	t
RECYLEX S.A.	FR0000120388	EUR	1	|EURONEXT|	f	80316	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000120388||fr||False	f	t	t
Put IBEX 35 | 7000 € | 21/12/12 | B7862	FR0011065655	EUR	5	|SGW|	f	80338	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7862||fr||False	f	t	t
CYBERNETIX	FR0000036162	EUR	1	|EURONEXT|	f	80342	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000036162||fr||False	f	t	t
Call IBEX 35 | 13000 € | 20/12/13 | B7865	FR0011065689	EUR	5	|SGW|	f	80347	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7865||fr||False	f	t	t
ARCHOS	FR0000182479	EUR	1	|EURONEXT|	f	80354	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000182479||fr||False	f	t	t
BIC	FR0000120966	EUR	1	|EURONEXT|	f	80355	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000120966||fr||False	f	t	t
DNXCORP	FR0010436584	EUR	1	|EURONEXT|	f	80357	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010436584||fr||False	f	t	t
Call IBEX 35 | 8000 € | 21/12/12 | C3303	FR0011168434	EUR	5	|SGW|	f	80362	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3303||fr||False	f	t	t
Call IBEX 35 | 10000 € | 21/12/12 | C1127	FR0011124320	EUR	5	|SGW|	f	80364	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1127||fr||False	f	t	t
Call IBEX 35 | 11500 € | 21/12/12 | B7858	FR0011065614	EUR	5	|SGW|	f	80366	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7858||fr||False	f	t	t
CRCAM SUD R.A.CCI	FR0000045346	EUR	1	|EURONEXT|	f	80368	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000045346||fr||False	f	t	t
EVS BROADC.EQUIPM.	BE0003820371	EUR	1	|EURONEXT|	f	74896	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003820371||be||False	f	t	t
JPMorgan Chase & Co.	\N	USD	1	\N	f	74899	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JPM||us||False	f	t	t
Stryker Corp.	\N	USD	1	\N	f	74928	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SYK||us||False	f	t	t
TURBO Call IBEX 35 | 9500 € | 16/09/11 | 54974	FR0011057512	EUR	5	|SGW|	f	74905	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54974||fr||False	f	t	t
INTLE PLANT.HEVEAS	FR0000036857	EUR	1	|EURONEXT|	f	74906	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000036857||fr||False	f	t	t
PATRIMOINE & COMDS	FR0011049816	EUR	1	|EURONEXT|	f	74907	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011049816||fr||False	f	t	t
Call IBEX 35 | 13000 € | 21/12/12 | B7859	FR0011065622	EUR	5	|SGW|	f	80372	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7859||fr||False	f	t	t
Put IBEX 35 | 5500 € | 21/12/12 | B7861	FR0011065648	EUR	5	|SGW|	f	80379	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7861||fr||False	f	t	t
COTTIN FRERES	FR0000071854	EUR	1	|EURONEXT|	f	80388	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000071854||fr||False	f	t	t
DOCK.PETR.AMBES AM	FR0000065260	EUR	1	|EURONEXT|	f	80396	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000065260||fr||False	f	t	t
DYNACTION	FR0000130353	EUR	1	|EURONEXT|	f	80402	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000130353||fr||False	f	t	t
EGIDE	FR0000072373	EUR	1	|EURONEXT|	f	80405	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000072373||fr||False	f	t	t
EIFFAGE	FR0000130452	EUR	1	|EURONEXT|	f	80411	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000130452||fr||False	f	t	t
ELEC.MADAGASCAR	FR0000035719	EUR	1	|EURONEXT|	f	80413	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000035719||fr||False	f	t	t
ERAMET	FR0000131757	EUR	1	|EURONEXT|	f	80418	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000131757||fr||False	f	t	t
ESI GROUP	FR0004110310	EUR	1	|EURONEXT|	f	80419	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004110310||fr||False	f	t	t
ESPACE PROD BS	FR0010559641	EUR	1	|EURONEXT|	f	80420	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010559641||fr||False	f	t	t
EUROFINS SCIENT.	FR0000038259	EUR	1	|EURONEXT|	f	80429	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000038259||fr||False	f	t	t
EUROMEDIS GROUPE	FR0000075343	EUR	1	|EURONEXT|	f	80434	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000075343||fr||False	f	t	t
FAURECIA	FR0000121147	EUR	1	|EURONEXT|	f	80438	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000121147||fr||False	f	t	t
FERM.CAS.MUN.CANNE	FR0000062101	EUR	1	|EURONEXT|	f	80449	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000062101||fr||False	f	t	t
PCAS BS05 BSAR	FR0010207811	EUR	1	|EURONEXT|	f	80454	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010207811||fr||False	f	t	t
ROBERTET CDV 87	FR0000045619	EUR	1	|EURONEXT|	f	80477	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000045619||fr||False	f	t	t
RUBIS	FR0000121253	EUR	1	|EURONEXT|	f	80483	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000121253||fr||False	f	t	t
FFP	FR0000064784	EUR	1	|EURONEXT|	f	80485	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064784||fr||False	f	t	t
FIAT SPA ORD.RGP	IT0001976403	EUR	1	|EURONEXT|	f	80489	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#IT0001976403||fr||False	f	t	t
GAMELOFT	FR0000079600	EUR	1	|EURONEXT|	f	80508	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000079600||fr||False	f	t	t
GROUPE VIAL	FR0010340406	EUR	1	|EURONEXT|	f	80524	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010340406||fr||False	f	t	t
GUERBET	FR0000032526	EUR	1	|EURONEXT|	f	80526	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000032526||fr||False	f	t	t
GUILLEMOT	FR0000066722	EUR	1	|EURONEXT|	f	80532	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000066722||fr||False	f	t	t
GUY DEGRENNE	FR0004035061	EUR	1	|EURONEXT|	f	80535	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004035061||fr||False	f	t	t
HEXCEL	US4282911084	EUR	1	|EURONEXT|	f	80539	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US4282911084||fr||False	f	t	t
HF BSAAR 02AUG2014	FR0010492694	EUR	1	|EURONEXT|	f	80544	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010492694||fr||False	f	t	t
HUBWOO	FR0004052561	EUR	1	|EURONEXT|	f	80565	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004052561||fr||False	f	t	t
HUIS CLOS	FR0000072357	EUR	1	|EURONEXT|	f	80566	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000072357||fr||False	f	t	t
IMMOB.HOTELIERE	FR0000036980	EUR	1	|EURONEXT|	f	80591	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000036980||fr||False	f	t	t
LA PERLA WORLD	FR0000064917	EUR	1	|EURONEXT|	f	80600	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064917||fr||False	f	t	t
LAFUMA	FR0000035263	EUR	1	|EURONEXT|	f	80603	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000035263||fr||False	f	t	t
LATONIA INVEST.	PA5183021045	EUR	1	|EURONEXT|	f	80604	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#PA5183021045||fr||False	f	t	t
KPN KON	NL0000009082	EUR	1	|EURONEXT|	f	74924	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000009082||nl||False	f	t	t
STADA Arzneimittel AG	DE0007251803	EUR	1	|DEUTSCHEBOERSE|	f	74930	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007251803||de||False	f	t	t
Ultrasonic AG	DE000A1KREX3	EUR	1	|DEUTSCHEBOERSE|	f	74931	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1KREX3||de||False	f	t	t
United Labels AG	DE0005489561	EUR	1	|DEUTSCHEBOERSE|	f	74932	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005489561||de||False	f	t	t
Versatel AG	DE000A0M2ZK2	EUR	1	|DEUTSCHEBOERSE|	f	74989	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0M2ZK2||de||False	f	t	t
SRA International Inc. Cl A	\N	USD	1	\N	f	74910	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SRX||us||False	f	t	t
Yum! Brands Inc.	\N	USD	1	\N	f	74922	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#YUM||us||False	f	t	t
Credit Suisse Group	\N	USD	1	\N	f	74923	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CS||us||False	f	t	t
Cenovus Energy Inc.	\N	USD	1	\N	f	74926	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CVE||us||False	f	t	t
Call IBEX 35 | 7500 € | 16/12/11 | B9940	FR0011091297	EUR	5	|SGW|	f	74946	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9940||fr||False	f	t	t
Call IBEX 35 | 9000 € | 18/11/11 | B9550	FR0011080795	EUR	5	|SGW|	f	74947	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9550||fr||False	f	t	t
Call IBEX 35 | 8000 € | 17/06/11 | B1771	FR0010936054	EUR	5	|SGW|	f	74952	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B1771||fr||False	f	t	t
Call IBEX 35 | 9000 € | 17/06/11 | B1773	FR0010936070	EUR	5	|SGW|	f	74953	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B1773||fr||False	f	t	t
LOCINDUS	FR0000121352	EUR	1	|EURONEXT|	f	80607	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000121352||fr||False	f	t	t
MAUNA KEA TECH	FR0010609263	EUR	1	|EURONEXT|	f	80619	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010609263||fr||False	f	t	t
MAUREL ET PROM	FR0000051070	EUR	1	|EURONEXT|	f	80630	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000051070||fr||False	f	t	t
MAURELETPROMBS	FR0010897082	EUR	1	|EURONEXT|	f	80631	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010897082||fr||False	f	t	t
MECELEC	FR0000061244	EUR	1	|EURONEXT|	f	80634	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000061244||fr||False	f	t	t
MEDIA 6	FR0000064404	EUR	1	|EURONEXT|	f	80636	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064404||fr||False	f	t	t
MEETIC	FR0004063097	EUR	1	|EURONEXT|	f	80641	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004063097||fr||False	f	t	t
MGI COUTIER	FR0000053027	EUR	1	|EURONEXT|	f	80644	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000053027||fr||False	f	t	t
MILLIMAGES	FR0010973479	EUR	1	|EURONEXT|	f	80650	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010973479||fr||False	f	t	t
MONCEY (FIN.) NOM.	FR0000076986	EUR	1	|EURONEXT|	f	80651	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000076986||fr||False	f	t	t
MONDIAL PECHE	FR0000062853	EUR	1	|EURONEXT|	f	80652	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000062853||fr||False	f	t	t
Call IBEX 35 | 6750 € | 20/01/12 | C1094	FR0011123991	EUR	5	|SGW|	f	80690	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1094||fr||False	f	t	t
NRJ GROUP	FR0000121691	EUR	1	|EURONEXT|	f	80695	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000121691||fr||False	f	t	t
NSC GROUPE	FR0000064529	EUR	1	|EURONEXT|	f	80696	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064529||fr||False	f	t	t
Call IBEX 35 | 10750 € | 20/01/12 | B9697	FR0011083765	EUR	5	|SGW|	f	80698	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9697||fr||False	f	t	t
Call IBEX 35 | 11250 € | 20/01/12 | B9698	FR0011083773	EUR	5	|SGW|	f	80699	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9698||fr||False	f	t	t
Call IBEX 35 | 10250 € | 20/01/12 | B9696	FR0011083757	EUR	5	|SGW|	f	80705	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9696||fr||False	f	t	t
OROSDI	FR0000039141	EUR	1	|EURONEXT|	f	80718	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000039141||fr||False	f	t	t
ORPEABSAARAUG2015	FR0010781021	EUR	1	|EURONEXT|	f	80721	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010781021||fr||False	f	t	t
CajaRioja Renta Fija FI	ES0114465034	EUR	2	|f_es_BMF|	f	74918					100	c	0	1	None	{2}	\N	ES0114465034||None||False	f	t	t
Consulnor Selección FI	ES0123563001	EUR	2	|f_es_BMF|	f	74941					100	c	0	1	None	{2}	\N	ES0123563001||None||False	f	t	t
VBH Holding AG St	DE0007600702	EUR	1	|DEUTSCHEBOERSE|	f	74944	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007600702||de||False	f	t	t
Tiffany & Co.	\N	USD	1	\N	f	74935	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TIF||us||False	f	t	t
Regions Financial Corp.	\N	USD	1	\N	f	74939	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RF||us||False	f	t	t
VISA Inc. Cl A	\N	USD	1	\N	f	74954	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#V||us||False	f	t	t
Call IBEX 35 | 8000 € | 16/12/11 | B9552	FR0011080811	EUR	5	|SGW|	f	74956	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9552||fr||False	f	t	t
SAFT NV	FR0010982223	EUR	1	|EURONEXT|	f	74957	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010982223||fr||False	f	t	t
DASSAULT SYST NV	FR0010986935	EUR	1	|EURONEXT|	f	74962	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010986935||fr||False	f	t	t
AREVA CI	FR0011035195	EUR	1	|EURONEXT|	f	74963	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011035195||fr||False	f	t	t
Call IBEX 35 | 10000 € | 17/06/11 | B1775	FR0010936096	EUR	5	|SGW|	f	74984	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B1775||fr||False	f	t	t
PLAST.VAL LOIRE	FR0000051377	EUR	1	|EURONEXT|	f	80751	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000051377||fr||False	f	t	t
SABETON	FR0000060121	EUR	1	|EURONEXT|	f	80753	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060121||fr||False	f	t	t
Put IBEX 35 | 7500 € | 15/06/12 | B9967	FR0011091560	EUR	5	|SGW|	f	80797	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9967||fr||False	f	t	t
Put IBEX 35 | 8000 € | 15/06/12 | B9968	FR0011091578	EUR	5	|SGW|	f	80798	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9968||fr||False	f	t	t
VM MATERIAUX	FR0000066540	EUR	1	|EURONEXT|	f	80800	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000066540||fr||False	f	t	t
Call IBEX 35 | 9000 € | 21/09/12 | C3290	FR0011168301	EUR	5	|SGW|	f	80803	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3290||fr||False	f	t	t
Call IBEX 35 | 8500 € | 15/06/12 | B9958	FR0011091479	EUR	5	|SGW|	f	80816	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9958||fr||False	f	t	t
Call IBEX 35 | 9500 € | 15/06/12 | B9960	FR0011091495	EUR	5	|SGW|	f	80817	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9960||fr||False	f	t	t
Call IBEX 35 | 11500 € | 15/06/12 | B9964	FR0011091537	EUR	5	|SGW|	f	80818	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9964||fr||False	f	t	t
Call IBEX 35 | 12000 € | 15/06/12 | B9965	FR0011091545	EUR	5	|SGW|	f	80819	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9965||fr||False	f	t	t
Put IBEX 35 | 6500 € | 15/06/12 | C3284	FR0011168244	EUR	5	|SGW|	f	80830	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3284||fr||False	f	t	t
XILAM ANIMATION	FR0004034072	EUR	1	|EURONEXT|	f	80861	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004034072||fr||False	f	t	t
SUCR.PITHIVIERS	FR0000033318	EUR	1	|EURONEXT|	f	81245	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000033318||fr||False	f	t	t
THERMOCOMPACT	FR0004037182	EUR	1	|EURONEXT|	f	81249	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004037182||fr||False	f	t	t
TIPIAK	FR0000066482	EUR	1	|EURONEXT|	f	81256	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000066482||fr||False	f	t	t
TIVOLY	FR0000060949	EUR	1	|EURONEXT|	f	81257	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060949||fr||False	f	t	t
UNIBEL	FR0000054215	EUR	1	|EURONEXT|	f	81277	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000054215||fr||False	f	t	t
UNION FIN.FRANCE	FR0000034548	EUR	1	|EURONEXT|	f	81291	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000034548||fr||False	f	t	t
UNION TECH.INFOR.	FR0000074197	EUR	1	|EURONEXT|	f	81296	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000074197||fr||False	f	t	t
Carmignac Emerging Discovery	LU0336083810	EUR	2	|CARMIGNAC|	f	81452	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	LU0336083810||fr||False	f	t	t
Carmignac Innovation	FR0010149096	EUR	2	|CARMIGNAC|	f	81453	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	FR0010149096||fr||False	f	t	t
Carmignac Commodities (A)	LU0164455502	EUR	2	|CARMIGNAC|	f	81454	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	LU0164455502||fr||False	f	t	t
Carmignac Patrimoine (E)	FR0010306142	EUR	2	|CARMIGNAC|	f	81459	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	FR0010306142||fr||False	f	t	t
Carmignac Emerging Patrimoine (A)	LU0592698954	EUR	2	|CARMIGNAC|	f	81460	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	LU0592698954||fr||False	f	t	t
Carmignac Emerging Patrimoine (E)	LU0592699093	EUR	2	|CARMIGNAC|	f	81461	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	LU0592699093||fr||False	f	t	t
Carmignac Investissement (E)	FR0010312660	EUR	2	|CARMIGNAC|	f	81473	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	FR0010312660||fr||False	f	t	t
VERBIO Vereinigte BioEnergie AG	DE000A0JL9W6	EUR	1	|DEUTSCHEBOERSE|	f	74955	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0JL9W6||de||False	f	t	t
Dexia	BE0003796134	EUR	1	\N	f	74975	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	DEXB.BR||be||False	f	t	t
Pride International Inc.	\N	USD	1	\N	f	74968	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PDE||us||False	f	t	t
GrafTech International Ltd.	\N	USD	1	\N	f	78952	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GTI||us||False	f	t	t
Medicis Pharmaceutical Corp.	\N	USD	1	\N	f	78958	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MRX||us||False	f	t	t
BCPS (0.1113585P1)	PTBCP0AMS055	EUR	1	|EURONEXT|	f	75002	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTBCP0AMS055||pt||False	f	t	t
CYBERNETIX	FR0011156306	EUR	1	|EURONEXT|	f	74999	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011156306||fr||False	f	t	t
Call IBEX 35 | 9250 € | 19/08/11 | B6046	FR0011017714	EUR	5	|SGW|	f	75008	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B6046||fr||False	f	t	t
Put IBEX 35 | 8000 € | 17/06/11 | B1792	FR0010936146	EUR	5	|SGW|	f	75013	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B1792||fr||False	f	t	t
FONCIER PARIS FRAN	FR0011167477	EUR	1	|EURONEXT|	f	75014	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011167477||fr||False	f	t	t
CRCAM LOIRE HTE L.	FR0000045239	EUR	1	|EURONEXT|	f	75016	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000045239||fr||False	f	t	t
Carmignac Grande Europe (A)	LU0099161993	EUR	2	|CARMIGNAC|	f	81474	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	LU0099161993||fr||False	f	t	t
Carmignac Euro-Entrepreneurs	FR0010149112	EUR	2	|CARMIGNAC|	f	81476	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	FR0010149112||fr||False	f	t	t
Carmignac Emergents (A)	FR0010149302	EUR	2	|CARMIGNAC|	f	81477	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	FR0010149302||fr||False	f	t	t
Carmignac Global Bond	LU0336083497	EUR	2	|CARMIGNAC|	f	81478	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	LU0336083497||fr||False	f	t	t
Carmignac Sécurité	FR0010149120	EUR	2	|CARMIGNAC|	f	81479	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	FR0010149120||fr||False	f	t	t
Carmignac Cash Plus	LU0336084032	EUR	2	|CARMIGNAC|	f	81480	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	LU0336084032||fr||False	f	t	t
NETGEM	FR0004154060	EUR	1	|EURONEXT|	f	81600	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004154060||fr||False	f	t	t
Fondmapfre Mixto Europa FI	ES0122059035	EUR	2	|f_es_BMF|	f	74981					100	c	0	1	None	{2}	\N	ES0122059035||None||False	f	t	t
INFOTEL	FR0000071797	EUR	1	|EURONEXT|	f	81625	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000071797||fr||False	f	t	t
OENEO BSAR01JUL12	FR0010203299	EUR	1	|EURONEXT|	f	81628	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010203299||fr||False	f	t	t
ROCAMAT	FR0000064255	EUR	1	|EURONEXT|	f	81630	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064255||fr||False	f	t	t
\N	\N	\N	\N	\N	f	75000	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0138313038||None||False	f	t	t
SARTORIUS STED BIO	FR0000053266	EUR	1	|EURONEXT|	f	81640	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000053266||fr||False	f	t	t
SECHE ENVIRONNEM.	FR0000039109	EUR	1	|EURONEXT|	f	81642	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000039109||fr||False	f	t	t
SECHILIENNE SIDEC	FR0000060402	EUR	1	|EURONEXT|	f	81643	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060402||fr||False	f	t	t
\N	\N	\N	\N	\N	f	75003	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0138405032||None||False	f	t	t
\N	\N	\N	\N	\N	f	75004	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0138730033||None||False	f	t	t
SECURIDEV	FR0000052839	EUR	1	|EURONEXT|	f	81644	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000052839||fr||False	f	t	t
SMTPC	FR0004016699	EUR	1	|EURONEXT|	f	81646	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004016699||fr||False	f	t	t
THALES	FR0000121329	EUR	1	|EURONEXT|	f	81657	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000121329||fr||False	f	t	t
THEOLIA	FR0000184814	EUR	1	|EURONEXT|	f	81658	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000184814||fr||False	f	t	t
\N	\N	\N	\N	\N	f	75005	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0140818032||None||False	f	t	t
\N	\N	\N	\N	\N	f	75007	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0146823002||None||False	f	t	t
\N	\N	\N	\N	\N	f	75011	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0146941036||None||False	f	t	t
\N	\N	\N	\N	\N	f	75015	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0147048005||None||False	f	t	t
\N	\N	\N	\N	\N	f	75019	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0147188033||None||False	f	t	t
Lincoln National Corp.	\N	USD	1	\N	f	74996	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LNC||us||False	f	t	t
DST Systems Inc.	\N	USD	1	\N	f	79007	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DST||us||False	f	t	t
Invesco Mortgage Capital Inc.	\N	USD	1	\N	f	79009	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IVR||us||False	f	t	t
Diamondrock Hospitality Co.	\N	USD	1	\N	f	79010	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DRH||us||False	f	t	t
ITT Educational Services Inc.	\N	USD	1	\N	f	79012	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ESI||us||False	f	t	t
Men's Wearhouse Inc.	\N	USD	1	\N	f	79014	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MW||us||False	f	t	t
Manitowoc Co.	\N	USD	1	\N	f	79021	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MTW||us||False	f	t	t
Vishay Intertechnology Inc.	\N	USD	1	\N	f	79023	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VSH||us||False	f	t	t
Actuant Corp. Cl A	\N	USD	1	\N	f	79024	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ATU||us||False	f	t	t
\N	\N	\N	\N	\N	f	75020	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0155859038||None||False	f	t	t
\N	\N	\N	\N	\N	f	75021	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0156728034||None||False	f	t	t
\N	\N	\N	\N	\N	f	75022	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0158346009||None||False	f	t	t
Lafarge	FR0000120537	EUR	1	|CAC|	f	75018					100	c	0	3	None	\N	\N	LG.PA||fr||False	f	t	t
\N	\N	\N	\N	\N	f	75026	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0158982035||None||False	f	t	t
Call IBEX 35 | 11500 € | 17/06/11 | B1778	FR0010936120	EUR	5	|SGW|	f	75045	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B1778||fr||False	f	t	t
Put IBEX 35 | 7500 € | 17/06/11 | B4062	FR0010972570	EUR	5	|SGW|	f	75046	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4062||fr||False	f	t	t
Call IBEX 35 | 11000 € | 17/06/11 | B1777	FR0010936112	EUR	5	|SGW|	f	75047	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B1777||fr||False	f	t	t
Call IBEX 35 | 10500 € | 17/06/11 | B1776	FR0010936104	EUR	5	|SGW|	f	75048	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B1776||fr||False	f	t	t
Call IBEX 35 | 12000 € | 17/06/11 | B1779	FR0010936138	EUR	5	|SGW|	f	75049	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B1779||fr||False	f	t	t
Put IBEX 35 | 9250 € | 19/08/11 | B6055	FR0011017805	EUR	5	|SGW|	f	75050	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B6055||fr||False	f	t	t
Carmignac Investissement Latitude	FR0010147603	EUR	2	|CARMIGNAC|	f	75051	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	FR0010147603||fr||False	f	t	t
\N	\N	\N	\N	\N	f	75027	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0158974032||None||False	f	t	t
\N	\N	\N	\N	\N	f	75028	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0159087032||None||False	f	t	t
\N	\N	\N	\N	\N	f	75029	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0158962037||None||False	f	t	t
\N	\N	\N	\N	\N	f	75030	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0158212037||None||False	f	t	t
\N	\N	\N	\N	\N	f	75033	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0160944031||None||False	f	t	t
\N	\N	\N	\N	\N	f	75034	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0164981039||None||False	f	t	t
\N	\N	\N	\N	\N	f	75035	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0169156033||None||False	f	t	t
\N	\N	\N	\N	\N	f	75036	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0170641031||None||False	f	t	t
Villeroy & Boch AG Vz	DE0007657231	EUR	1	|DEUTSCHEBOERSE|	f	74990	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007657231||de||False	f	t	t
Siemens AG	\N	USD	1	\N	f	75032	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SI||us||False	f	t	t
SK Telecom Co. Ltd.	\N	USD	1	\N	f	75164	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SKM||us||False	f	t	t
Cloud Peak Energy Inc.	\N	USD	1	\N	f	79189	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CLD||us||False	f	t	t
Bouygues	FR0000120503	EUR	1	|CAC|	f	75078	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EN.PA||fr||False	f	t	t
Put IBEX 35 | 6500 € | 16/03/12 | C1100	FR0011124056	EUR	5	|SGW|	f	75060	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1100||fr||False	f	t	t
Call IBEX 35 | 10250 € | 20/05/11 | B4725	FR0010984435	EUR	5	|SGW|	f	75068	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4725||fr||False	f	t	t
GRPE EUROTUNNEL NV	FR0010978825	EUR	1	|EURONEXT|	f	75069	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010978825||fr||False	f	t	t
Put IBEX 35 | 7250 € | 20/04/12 | C1110	FR0011124155	EUR	5	|SGW|	f	75072	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1110||fr||False	f	t	t
D'IETEREN STR (D)	BE0005642161	EUR	1	|EURONEXT|	f	75059	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005642161||be||False	f	t	t
DECEUNINCK	BE0003789063	EUR	1	|EURONEXT|	f	75074	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003789063||be||False	f	t	t
\N	\N	\N	\N	\N	f	75075	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0170612032||None||False	f	t	t
\N	\N	\N	\N	\N	f	75076	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0170649034||None||False	f	t	t
\N	\N	\N	\N	\N	f	75077	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0170792032||None||False	f	t	t
\N	\N	\N	\N	\N	f	75079	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0170821039||None||False	f	t	t
\N	\N	\N	\N	\N	f	75080	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0173266034||None||False	f	t	t
\N	\N	\N	\N	\N	f	75081	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0173395031||None||False	f	t	t
\N	\N	\N	\N	\N	f	75082	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0173267032||None||False	f	t	t
\N	\N	\N	\N	\N	f	75083	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0173363039||None||False	f	t	t
VITA 34 AG	DE000A0BL849	EUR	1	|DEUTSCHEBOERSE|	f	74992	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0BL849||de||False	f	t	t
Volkswagen AG Vz	DE0007664039	EUR	1	|DEUTSCHEBOERSE|	f	74994	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007664039||de||False	f	t	t
ATOS ORIGIN NV	FR0010979658	EUR	1	|EURONEXT|	f	75194	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010979658||fr||False	f	t	t
DU PONT DE NEMOURS	US2635341090	EUR	1	|EURONEXT|	f	75196	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US2635341090||fr||False	f	t	t
HERMES INTL	FR0000052292	EUR	1	|EURONEXT|	f	75198	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000052292||fr||False	f	t	t
HOLOGRAM IND.	FR0000062168	EUR	1	|EURONEXT|	f	75200	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000062168||fr||False	f	t	t
HSBC HOLDINGS	GB0005405286	EUR	1	|EURONEXT|	f	75201	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#GB0005405286||fr||False	f	t	t
Call IBEX 35 | 10250 € | 19/08/11 | B6048	FR0011017730	EUR	5	|SGW|	f	75204	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B6048||fr||False	f	t	t
Put IBEX 35 | 10250 € | 20/01/12 | B9702	FR0011083815	EUR	5	|SGW|	f	75210	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9702||fr||False	f	t	t
Put IBEX 35 | 10750 € | 20/01/12 | B9703	FR0011083823	EUR	5	|SGW|	f	75216	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9703||fr||False	f	t	t
Call IBEX 35 | 8500 € | 16/03/12 | B9556	FR0011080852	EUR	5	|SGW|	f	75230	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9556||fr||False	f	t	t
Call IBEX 35 | 10000 € | 16/03/12 | B7609	FR0011058452	EUR	5	|SGW|	f	75231	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7609||fr||False	f	t	t
I.R.I.S STRIP (D)	BE0005555264	EUR	1	|EURONEXT|	f	75225	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005555264||be||False	f	t	t
IMMOBEL	BE0003599108	EUR	1	|EURONEXT|	f	75226	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003599108||be||False	f	t	t
HUNTER DOUGLAS	ANN4327C1220	EUR	1	|EURONEXT|	f	75213	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#ANN4327C1220||nl||False	f	t	t
InTiCa Systems AG	DE0005874846	EUR	1	|DEUTSCHEBOERSE|	f	80328	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005874846||de||False	f	t	t
InVision Software AG	DE0005859698	EUR	1	|DEUTSCHEBOERSE|	f	80329	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005859698||de||False	f	t	t
ISRA VISION AG	DE0005488100	EUR	1	|DEUTSCHEBOERSE|	f	80330	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005488100||de||False	f	t	t
Jetter AG	DE0006264005	EUR	1	|DEUTSCHEBOERSE|	f	80331	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006264005||de||False	f	t	t
alstria office REIT-AG	DE000A0LD2U1	EUR	1	|DEUTSCHEBOERSE|	f	80517	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0LD2U1||de||False	f	t	t
LPKF Laser & Electronics AG	DE0006450000	EUR	1	|DEUTSCHEBOERSE|	f	80625	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006450000||de||False	f	t	t
MediGene AG	DE0005020903	EUR	1	|DEUTSCHEBOERSE|	f	80626	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005020903||de||False	f	t	t
Medion AG	DE0006605009	EUR	1	|DEUTSCHEBOERSE|	f	80627	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006605009||de||False	f	t	t
EUROCASTLE INVEST.	GB00B01C5N27	EUR	1	|EURONEXT|	f	75233	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GB00B01C5N27||nl||False	f	t	t
EUROPACORP	FR0010490920	EUR	1	|EURONEXT|	f	75235	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010490920||fr||False	f	t	t
Carmignac Court Terme	FR0010149161	EUR	2	|CARMIGNAC|	f	75236	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	FR0010149161||fr||False	f	t	t
EUROSIC	FR0000038200	EUR	1	|EURONEXT|	f	75240	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000038200||fr||False	f	t	t
Call IBEX 35 | 11000 € | 16/09/11 | B4742	FR0010984609	EUR	5	|SGW|	f	75246	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4742||fr||False	f	t	t
Put IBEX 35 | 7500 € | 16/09/11 | B4745	FR0010984633	EUR	5	|SGW|	f	75247	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4745||fr||False	f	t	t
OFI PRI EQ CAP BS1	FR0011077288	EUR	1	|EURONEXT|	f	75248	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011077288||fr||False	f	t	t
OFI PRI EQ CAP BS2	FR0011077296	EUR	1	|EURONEXT|	f	75249	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011077296||fr||False	f	t	t
AFFIPARIS DS	FR0011132992	EUR	1	|EURONEXT|	f	75250	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011132992||fr||False	f	t	t
EXMAR	BE0003808251	EUR	1	|EURONEXT|	f	75237	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003808251||be||False	f	t	t
EXMAR STR VVPR (D)	BE0005633079	EUR	1	|EURONEXT|	f	75239	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005633079||be||False	f	t	t
EXACT HOLDING	NL0000350361	EUR	1	|EURONEXT|	f	75251	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000350361||nl||False	f	t	t
Progress-Werk Oberkirch AG	DE0006968001	EUR	1	|DEUTSCHEBOERSE|	f	80628	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006968001||de||False	f	t	t
ProSiebenSat.1 Media AG	DE0007771172	EUR	1	|DEUTSCHEBOERSE|	f	80629	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007771172||de||False	f	t	t
Phoenix Solar Aktiengesellschaft	DE000A0BVU93	EUR	1	|DEUTSCHEBOERSE|	f	80833	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0BVU93||de||False	f	t	t
Quanmax AG	AT0000A0E9W5	EUR	1	|DEUTSCHEBOERSE|	f	80834	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#AT0000A0E9W5||de||False	f	t	t
Sasol Ltd.	\N	USD	1	\N	f	75241	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SSL||us||False	f	t	t
\N	\N	\N	\N	\N	f	75254	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	NYSE#BF||None||False	f	t	t
TURBO Call IBEX 35 | 8500 € | 16/12/11 | 55089	FR0011092139	EUR	5	|SGW|	f	75255	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#55089||fr||False	f	t	t
Call IBEX 35 | 11250 € | 19/08/11 | B6050	FR0011017755	EUR	5	|SGW|	f	75256	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B6050||fr||False	f	t	t
Call IBEX 35 | 8250 € | 21/10/11 | B9932	FR0011091214	EUR	5	|SGW|	f	75264	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9932||fr||False	f	t	t
Technip		EUR	1		f	75234					100	c	0	3	None	\N	\N	TEC.PA||fr||False	f	t	t
METRO AG St	DE0007257503	EUR	1	|DAX|DEUTSCHEBOERSE|	f	80854					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE0007257503||de||False	f	t	t
Merck KGaA	DE0006599905	EUR	1	|DAX|DEUTSCHEBOERSE|	f	80853					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE0006599905||de||False	f	t	t
Lam Research Corporation	\N	USD	1	|NASDAQ100|	f	75257	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	LRCX||us||False	f	t	t
IMTECH	NL0006055329	EUR	1	|EURONEXT|	f	75309	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0006055329||nl||False	f	t	t
Hewlett-Packard Co.	\N	USD	1	\N	f	75298	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HPQ||us||False	f	t	t
Sumitomo Mitsui Financial Group Inc.	\N	USD	1	\N	f	75303	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SMFG||us||False	f	t	t
Put IBEX 35 | 7000 € | 16/03/12 | C1101	FR0011124064	EUR	5	|SGW|	f	75292	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1101||fr||False	f	t	t
Put IBEX 35 | 9000 € | 16/03/12 | B7620	FR0011058510	EUR	5	|SGW|	f	75297	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7620||fr||False	f	t	t
Call IBEX 35 | 14500 € | 21/12/12 | B7860	FR0011065630	EUR	5	|SGW|	f	75301	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7860||fr||False	f	t	t
FIDUCIAL OFF.SOL.	FR0000061418	EUR	1	|EURONEXT|	f	75306	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000061418||fr||False	f	t	t
FINANCIERE MARJOS	FR0000060824	EUR	1	|EURONEXT|	f	75307	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060824||fr||False	f	t	t
BEAM	US0737301038	EUR	1	|EURONEXT|	f	75548	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#US0737301038||nl||False	f	t	t
FONCIER PARIS FRAN	FR0010304329	EUR	1	|EURONEXT|	f	75308	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010304329||fr||False	f	t	t
ADP	FR0010340141	EUR	1	|EURONEXT|	f	75328	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010340141||fr||False	f	t	t
AEDIAN	FR0004005924	EUR	1	|EURONEXT|	f	75330	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004005924||fr||False	f	t	t
ESPACE PRODUCTION	FR0011067867	EUR	1	|EURONEXT|	f	75332	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011067867||fr||False	f	t	t
Put IBEX 35 | 8000 € | 16/09/11 | B4746	FR0010984641	EUR	5	|SGW|	f	75335	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4746||fr||False	f	t	t
FLORIDIENNE	BE0003215143	EUR	1	|EURONEXT|	f	75299	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003215143||be||False	f	t	t
Conergy AG	DE0006040025	EUR	1	|DEUTSCHEBOERSE|	f	75313	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006040025||de||False	f	t	t
Sartorius AG St	DE0007165607	EUR	1	|DEUTSCHEBOERSE|	f	80868	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007165607||de||False	f	t	t
Sartorius AG Vz	DE0007165631	EUR	1	|DEUTSCHEBOERSE|	f	80869	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007165631||de||False	f	t	t
Schaltbau Holding AG	DE0007170300	EUR	1	|DEUTSCHEBOERSE|	f	80870	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007170300||de||False	f	t	t
SCHULER AG Neue St	DE000A0V9A22	EUR	1	|DEUTSCHEBOERSE|	f	80871	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0V9A22||de||False	f	t	t
secunet Security Networks AG	DE0007276503	EUR	1	|DEUTSCHEBOERSE|	f	80872	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007276503||de||False	f	t	t
euromicron AG	DE000A1K0300	EUR	1	|DEUTSCHEBOERSE|	f	81169	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1K0300||de||False	f	t	t
Call IBEX 35 | 9750 € | 19/08/11 | B6047	FR0011017722	EUR	5	|SGW|	f	75338	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B6047||fr||False	f	t	t
AFFINE	FR0000036105	EUR	1	|EURONEXT|	f	75340	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000036105||fr||False	f	t	t
LANSON-BCC	FR0004027068	EUR	1	|EURONEXT|	f	75345	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004027068||fr||False	f	t	t
Put IBEX 35 | 7750 € | 18/05/12 | C1123	FR0011124288	EUR	5	|SGW|	f	75347	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1123||fr||False	f	t	t
Put IBEX 35 | 8500 € | 15/06/12 | B9969	FR0011091586	EUR	5	|SGW|	f	75349	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9969||fr||False	f	t	t
Call IBEX 35 | 8500 € | 21/09/12 | C3289	FR0011168293	EUR	5	|SGW|	f	75350	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3289||fr||False	f	t	t
Call IBEX 35 inLine | 9000 € | 15/09/11 | I0029	FR0011038934	EUR	5	|SGW|	f	75354	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0029||fr||False	f	t	t
ANF IMMOBILIER	FR0000063091	EUR	1	|EURONEXT|	f	75378	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000063091||fr||False	f	t	t
AEDIFICA	BE0003851681	EUR	1	|EURONEXT|	f	75337	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003851681||be||False	f	t	t
NEDAP	NL0000371243	EUR	1	|EURONEXT|	f	75356	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000371243||nl||False	f	t	t
BOUSSARD GAVAUDAN	GG00B1FQG453	EUR	1	|EURONEXT|	f	75380	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GG00B1FQG453||nl||False	f	t	t
European CleanTech 1 SE	LU0538936351	EUR	1	|DEUTSCHEBOERSE|	f	81170	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#LU0538936351||de||False	f	t	t
exceet Group SE	LU0472835155	EUR	1	|DEUTSCHEBOERSE|	f	81172	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#LU0472835155||de||False	f	t	t
Fabasoft AG	AT0000785407	EUR	1	|DEUTSCHEBOERSE|	f	81173	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#AT0000785407||de||False	f	t	t
Fair Value REIT-AG	DE000A0MW975	EUR	1	|DEUTSCHEBOERSE|	f	81174	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0MW975||de||False	f	t	t
Fielmann AG	DE0005772206	EUR	1	|DEUTSCHEBOERSE|	f	81175	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005772206||de||False	f	t	t
SAP AG	DE0007164600	EUR	1	|DAX|DEUTSCHEBOERSE|EUROSTOXX|	f	80867					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE0007164600||de||False	f	t	t
Salzgitter AG	DE0006202005	EUR	1	|DAX|DEUTSCHEBOERSE|	f	80866					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE0006202005||de||False	f	t	t
Aegon	NL0000303709	EUR	1		f	75341					100	c	0	12	None	\N	\N	AGN.AS||nl||False	f	t	t
Intesa San Paolo	IT0000072618	EUR	1	|EUROSTOXX|	f	75295					100	c	0	6	ISP.MI	{1}	{3}	ISP.MI||it||False	f	t	t
GAGFAH S.A.	LU0269583422	EUR	1	|DEUTSCHEBOERSE|	f	81185	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#LU0269583422||de||False	f	t	t
GEA Group Aktiengesellschaft	DE0006602006	EUR	1	|DEUTSCHEBOERSE|	f	81186	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006602006||de||False	f	t	t
Geratherm Medical AG	DE0005495626	EUR	1	|DEUTSCHEBOERSE|	f	81187	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005495626||de||False	f	t	t
Gerresheimer AG	DE000A0LD6E6	EUR	1	|DEUTSCHEBOERSE|	f	81188	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0LD6E6||de||False	f	t	t
Gerry Weber International AG	DE0003304101	EUR	1	|DEUTSCHEBOERSE|	f	81189	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0003304101||de||False	f	t	t
Gesco AG	DE000A1K0201	EUR	1	|DEUTSCHEBOERSE|	f	81190	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1K0201||de||False	f	t	t
GfK SE	DE0005875306	EUR	1	|DEUTSCHEBOERSE|	f	81191	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005875306||de||False	f	t	t
TURBO Call IBEX 35 | 8000 € | 16/12/11 | 55097	FR0011115682	EUR	5	|SGW|	f	75387	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#55097||fr||False	f	t	t
TURBO Put IBEX 35 | 10500 € | 17/06/11 | 54843	FR0011003276	EUR	5	|SGW|	f	75396	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54843||fr||False	f	t	t
Put IBEX 35 | 7500 € | 19/12/14 | B7873	FR0011065762	EUR	5	|SGW|	f	75398	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7873||fr||False	f	t	t
Call IBEX 35 | 6750 € | 17/02/12 | C1096	FR0011124015	EUR	5	|SGW|	f	75423	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1096||fr||False	f	t	t
Call IBEX 35 | 7250 € | 17/02/12 | C1097	FR0011124023	EUR	5	|SGW|	f	75426	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1097||fr||False	f	t	t
BROOKFIELD CERT A	BE0004601424	EUR	1	|EURONEXT|	f	75391	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0004601424||be||False	f	t	t
BRUNEL INTERNAT	NL0000343432	EUR	1	|EURONEXT|	f	75400	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000343432||nl||False	f	t	t
AMT HOLDING	NL0000886968	EUR	1	|EURONEXT|	f	75403	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000886968||nl||False	f	t	t
AND INTERNATIONAL	NL0000430106	EUR	1	|EURONEXT|	f	75404	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000430106||nl||False	f	t	t
GFT Technologies AG	DE0005800601	EUR	1	|DEUTSCHEBOERSE|	f	81192	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005800601||de||False	f	t	t
Gigaset AG	DE0005156004	EUR	1	|DEUTSCHEBOERSE|	f	81193	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005156004||de||False	f	t	t
Gildemeister AG	DE0005878003	EUR	1	|DEUTSCHEBOERSE|	f	81194	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005878003||de||False	f	t	t
GK Software AG	DE0007571424	EUR	1	|DEUTSCHEBOERSE|	f	81195	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007571424||de||False	f	t	t
Grammer AG	DE0005895403	EUR	1	|DEUTSCHEBOERSE|	f	81196	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005895403||de||False	f	t	t
GRENKELEASING AG	DE0005865901	EUR	1	|DEUTSCHEBOERSE|	f	81197	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005865901||de||False	f	t	t
GSW Immobilien AG	DE000GSW1111	EUR	1	|DEUTSCHEBOERSE|	f	81198	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000GSW1111||de||False	f	t	t
GWB Immobilien AG	DE000A0JKHG0	EUR	1	|DEUTSCHEBOERSE|	f	81199	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0JKHG0||de||False	f	t	t
Hansa Group AG	DE0007608606	EUR	1	|DEUTSCHEBOERSE|	f	81217	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007608606||de||False	f	t	t
Hawesko Holding AG	DE0006042708	EUR	1	|DEUTSCHEBOERSE|	f	81218	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006042708||de||False	f	t	t
Roy Philips Electr	\N	EUR	1	|EUROSTOXX|	f	75446	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	PHIA.AS||nl||False	f	t	t
Mattel Inc.	\N	USD	1	|NASDAQ100|	f	75436	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	MAT||us||False	f	t	t
FONCIERE DES MURS	FR0000060303	EUR	1	|EURONEXT|	f	75428	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060303||fr||False	f	t	t
IPSOS DS	FR0011104942	EUR	1	|EURONEXT|	f	75429	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011104942||fr||False	f	t	t
TURBO Call IBEX 35 | 10000 € | 16/09/11 | 54976	FR0011057538	EUR	5	|SGW|	f	75434	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54976||fr||False	f	t	t
TURBO Put IBEX 35 | 10500 € | 16/09/11 | 54980	FR0011057579	EUR	5	|SGW|	f	75435	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54980||fr||False	f	t	t
FONCIERE LYONNAISE	FR0000033409	EUR	1	|EURONEXT|	f	75438	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000033409||fr||False	f	t	t
ALPHA M.O.S. BS	FR0011073915	EUR	1	|EURONEXT|	f	75440	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011073915||fr||False	f	t	t
EUROFINS SCIENT NV	FR0011159987	EUR	1	|EURONEXT|	f	75441	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011159987||fr||False	f	t	t
FONCIERE R-PARIS	FR0000063265	EUR	1	|EURONEXT|	f	75444	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000063265||fr||False	f	t	t
PRECIA	FR0000060832	EUR	1	|EURONEXT|	f	75447	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060832||fr||False	f	t	t
PSB INDUSTRIES	FR0000060329	EUR	1	|EURONEXT|	f	75448	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060329||fr||False	f	t	t
TURBO Call IBEX 35 | 10000 € | 17/06/11 | 54834	FR0011003185	EUR	5	|SGW|	f	75456	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54834||fr||False	f	t	t
TURBO Put IBEX 35 | 11000 € | 17/06/11 | 54845	FR0011003292	EUR	5	|SGW|	f	75461	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54845||fr||False	f	t	t
Call IBEX 35 | 8000 € | 16/03/12 | B9555	FR0011080845	EUR	5	|SGW|	f	75472	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9555||fr||False	f	t	t
RIO TINTO CERT	BE0004559978	EUR	1	|EURONEXT|	f	75457	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0004559978||be||False	f	t	t
REpower Systems SE	DE0006177033	EUR	1	|DEUTSCHEBOERSE|	f	75455	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006177033||de||False	f	t	t
HCI Capital AG	DE000A0D9Y97	EUR	1	|DEUTSCHEBOERSE|	f	81219	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0D9Y97||de||False	f	t	t
HeidelbergCement AG	DE0006047004	EUR	1	|DEUTSCHEBOERSE|	f	81220	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006047004||de||False	f	t	t
Highlight Communications AG	CH0006539198	EUR	1	|DEUTSCHEBOERSE|	f	81270	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#CH0006539198||de||False	f	t	t
Hugo Boss AG St	DE0005245500	EUR	1	|DEUTSCHEBOERSE|	f	81271	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005245500||de||False	f	t	t
Linde AG	DE0006483001	EUR	1	|DAX|DEUTSCHEBOERSE|	f	81288					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE0006483001||de||False	f	t	t
KROMI Logistik AG	DE000A0KFUJ5	EUR	1	|DEUTSCHEBOERSE|	f	81279	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0KFUJ5||de||False	f	t	t
Krones AG	DE0006335003	EUR	1	|DEUTSCHEBOERSE|	f	81280	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006335003||de||False	f	t	t
KUKA Aktiengesellschaft	DE0006204407	EUR	1	|DEUTSCHEBOERSE|	f	81281	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006204407||de||False	f	t	t
KWS SAAT AG	DE0007074007	EUR	1	|DEUTSCHEBOERSE|	f	81282	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007074007||de||False	f	t	t
LANXESS AG	DE0005470405	EUR	1	|DEUTSCHEBOERSE|	f	81283	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005470405||de||False	f	t	t
Leifheit AG	DE0006464506	EUR	1	|DEUTSCHEBOERSE|	f	81285	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006464506||de||False	f	t	t
Leoni AG	DE0005408884	EUR	1	|DEUTSCHEBOERSE|	f	81287	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005408884||de||False	f	t	t
Lloyd Fonds Aktiengesellschaft	DE0006174873	EUR	1	|DEUTSCHEBOERSE|	f	81289	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006174873||de||False	f	t	t
Loewe AG	DE0006494107	EUR	1	|DEUTSCHEBOERSE|	f	81290	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006494107||de||False	f	t	t
Ludwig Beck AG	DE0005199905	EUR	1	|DEUTSCHEBOERSE|	f	81292	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005199905||de||False	f	t	t
MAGIX AG	DE0007220782	EUR	1	|DEUTSCHEBOERSE|	f	81293	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007220782||de||False	f	t	t
MAN SE Vz	DE0005937031	EUR	1	|DEUTSCHEBOERSE|	f	81295	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005937031||de||False	f	t	t
Manz AG	DE000A0JQ5U3	EUR	1	|DEUTSCHEBOERSE|	f	81300	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0JQ5U3||de||False	f	t	t
Marseille-Kliniken AG	DE0007783003	EUR	1	|DEUTSCHEBOERSE|	f	81302	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007783003||de||False	f	t	t
Masterflex AG	DE0005492938	EUR	1	|DEUTSCHEBOERSE|	f	81303	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005492938||de||False	f	t	t
Red Hat Inc.	\N	USD	1	\N	f	75430	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RHT||us||False	f	t	t
Call IBEX 35 | 10500 € | 16/03/12 | B7610	FR0011058460	EUR	5	|SGW|	f	75475	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7610||fr||False	f	t	t
Call IBEX 35 | 11000 € | 16/03/12 | B7611	FR0011058478	EUR	5	|SGW|	f	75477	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7611||fr||False	f	t	t
Put IBEX 35 | 5000 € | 20/12/13 | B7867	FR0011065705	EUR	5	|SGW|	f	75479	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7867||fr||False	f	t	t
TURBO Put IBEX 35 | 11250 € | 17/06/11 | 54846	FR0011003300	EUR	5	|SGW|	f	75481	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54846||fr||False	f	t	t
ADC SIIC	FR0000065401	EUR	1	|EURONEXT|	f	75487	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000065401||fr||False	f	t	t
ROBECO	NL0000289783	EUR	1	|EURONEXT|	f	75490	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#NL0000289783||fr||False	f	t	t
TAYNINH	FR0000063307	EUR	1	|EURONEXT|	f	75491	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000063307||fr||False	f	t	t
ALDETA	FR0000036634	EUR	1	|EURONEXT|	f	75505	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000036634||fr||False	f	t	t
TURBO Put IBEX 35 | 11500 € | 17/06/11 | 54847	FR0011003318	EUR	5	|SGW|	f	75507	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54847||fr||False	f	t	t
MODELABS	FR0011089937	EUR	1	|EURONEXT|	f	75510	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011089937||fr||False	f	t	t
TURBO Call IBEX 35 | 9750 € | 16/09/11 | 54975	FR0011057520	EUR	5	|SGW|	f	75511	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54975||fr||False	f	t	t
ARSEUS ST VVPR (D)	BE0005617882	EUR	1	|EURONEXT|	f	75489	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005617882||be||False	f	t	t
Ahlers AG St	DE0005009708	EUR	1	|DEUTSCHEBOERSE|	f	75513	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005009708||de||False	f	t	t
\N	\N	\N	\N	\N	f	81376	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0181396005||None||False	f	t	t
Generali Assicurazioni	IT0000062072	EUR	1	|EUROSTOXX|	f	75302	\N	\N	\N	\N	100	c	0	6	\N	\N	\N	G.MI||it||False	f	t	t
Sony Corp.	\N	USD	1	\N	f	74833	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SNE||us||False	f	t	t
Índice de volatilidad	\N	USD	3	\N	t	81090	\N	\N	\N	\N	100	c	0	2	^VIX	{1}	{3}	^VIX||us||False	f	t	t
S&P 500	US78378X1072	USD	3	\N	t	81083	\N	\N	\N	\N	100	c	0	2	^GSPC	{1}	{3}	^GSPC||us||False	f	t	t
Valeant Pharmaceuticals International Inc.	\N	USD	1	\N	f	74848	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VRX||us||False	f	t	t
Cigna Corp.	\N	USD	1	\N	f	74874	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CI||us||False	f	t	t
Timberland Co.	\N	USD	1	\N	f	74927	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TBL||us||False	f	t	t
Exelon Corp.	\N	USD	1	\N	f	78947	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EXC||us||False	f	t	t
Piedmont Natural Gas Co.	\N	USD	1	\N	f	78948	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PNY||us||False	f	t	t
Allied World Assurance Co. Holdings Ltd.	\N	USD	1	\N	f	78949	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AWH||us||False	f	t	t
Berry Petroleum Co. Cl A	\N	USD	1	\N	f	78950	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BRY||us||False	f	t	t
Terex Corp.	\N	USD	1	\N	f	78951	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TEX||us||False	f	t	t
Teledyne Technologies Inc.	\N	USD	1	\N	f	78963	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TDY||us||False	f	t	t
Air Lease Corp.	\N	USD	1	\N	f	79003	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AL||us||False	f	t	t
Domino's Pizza Inc.	\N	USD	1	\N	f	79006	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DPZ||us||False	f	t	t
Plantronics Inc.	\N	USD	1	\N	f	79027	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PLT||us||False	f	t	t
PolyOne Corp.	\N	USD	1	\N	f	79029	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#POL||us||False	f	t	t
Banco Bilbao Vizcaya Argentaria S.A.	\N	USD	1	\N	f	79038	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BBVA||us||False	f	t	t
\N	\N	\N	\N	\N	f	76108	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0147049003||None||False	f	t	t
Lagardere Groupe SCA		EUR	1		f	75497					100	c	0	3	None	\N	\N	MMB.PA||fr||False	f	t	t
DDR Corp.	\N	USD	1	\N	f	79044	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DDR||us||False	f	t	t
Charles River Laboratories International Inc.	\N	USD	1	\N	f	79045	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CRL||us||False	f	t	t
Curtiss-Wright Corp.	\N	USD	1	\N	f	79050	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CW||us||False	f	t	t
Medical Properties Trust Inc.	\N	USD	1	\N	f	79184	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MPW||us||False	f	t	t
Vitamin Shoppe Inc.	\N	USD	1	\N	f	79185	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VSI||us||False	f	t	t
Teekay Corp.	\N	USD	1	\N	f	79186	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TK||us||False	f	t	t
Mercury General Corp.	\N	USD	1	\N	f	79187	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MCY||us||False	f	t	t
Semiconductor Manufacturing International Corp.	\N	USD	1	\N	f	79190	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SMI||us||False	f	t	t
Viacom Inc. Cl A	\N	USD	1	\N	f	79239	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VIA||us||False	f	t	t
Geo Group Inc.	\N	USD	1	\N	f	79240	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GEO||us||False	f	t	t
Minerals Technologies Inc.	\N	USD	1	\N	f	79241	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MTX||us||False	f	t	t
Old National Bancorp	\N	USD	1	\N	f	79246	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ONB||us||False	f	t	t
Kaydon Corp.	\N	USD	1	\N	f	79247	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KDN||us||False	f	t	t
Sunstone Hotel Investors Inc.	\N	USD	1	\N	f	79248	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SHO||us||False	f	t	t
Newmont Mining Corp.	\N	USD	1	\N	f	79259	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NEM||us||False	f	t	t
MetLife Inc.	\N	USD	1	\N	f	79261	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MET||us||False	f	t	t
Kubota Corp.	\N	USD	1	\N	f	79263	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KUB||us||False	f	t	t
INVESCO Ltd.	\N	USD	1	\N	f	79269	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IVZ||us||False	f	t	t
J.M. Smucker Co.	\N	USD	1	\N	f	79270	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SJM||us||False	f	t	t
NSTAR	\N	USD	1	\N	f	75483	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NST||us||False	f	t	t
FUT.CLUBE PORTO	PTFCP0AM0008	EUR	1	|EURONEXT|	f	75536	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTFCP0AM0008||pt||False	f	t	t
TURBO Put IBEX 35 | 11750 € | 17/06/11 | 54848	FR0011003326	EUR	5	|SGW|	f	75515	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54848||fr||False	f	t	t
FROMAGERIES BEL	FR0000121857	EUR	1	|EURONEXT|	f	75528	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000121857||fr||False	f	t	t
Put IBEX 35 | 9250 € | 20/05/11 | B4731	FR0010984492	EUR	5	|SGW|	f	75529	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4731||fr||False	f	t	t
Put IBEX 35 | 9750 € | 20/05/11 | B4732	FR0010984500	EUR	5	|SGW|	f	75531	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4732||fr||False	f	t	t
Put IBEX 35 | 10250 € | 17/02/12 | B9713	FR0011083922	EUR	5	|SGW|	f	75533	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9713||fr||False	f	t	t
Put IBEX 35 | 8500 € | 16/03/12 | B7619	FR0011058502	EUR	5	|SGW|	f	75534	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7619||fr||False	f	t	t
Call IBEX 35 | 10750 € | 20/04/12 | C2133	FR0011145416	EUR	5	|SGW|	f	75535	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C2133||fr||False	f	t	t
Put IBEX 35 | 10250 € | 20/05/11 | B4733	FR0010984518	EUR	5	|SGW|	f	75539	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4733||fr||False	f	t	t
Call IBEX 35 | 7500 € | 17/06/11 | B4061	FR0010972562	EUR	5	|SGW|	f	75547	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4061||fr||False	f	t	t
SIIC PARIS8EME NOM	FR0000077844	EUR	1	|EURONEXT|	f	75552	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000077844||fr||False	f	t	t
FOYER	LU0112960504	EUR	1	|EURONEXT|	f	75524	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#LU0112960504||be||False	f	t	t
ATENOR STRIP (D)	BE0005602736	EUR	1	|EURONEXT|	f	75545	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005602736||be||False	f	t	t
ROY BK OF SCOTLAND	GB0007547838	EUR	1	|EURONEXT|	f	75537	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GB0007547838||nl||False	f	t	t
COLEXON Energy AG	DE0005250708	EUR	1	|DEUTSCHEBOERSE|	f	75541	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005250708||de||False	f	t	t
HollyFrontier Corp.	\N	USD	1	\N	f	79271	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HFC||us||False	f	t	t
Saks Inc.	\N	USD	1	\N	f	79274	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SKS||us||False	f	t	t
Capstead Mortgage Corp.	\N	USD	1	\N	f	79284	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CMO||us||False	f	t	t
B&G Foods Inc.	\N	USD	1	\N	f	79285	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BGS||us||False	f	t	t
Tenaris S.A.	\N	USD	1	\N	f	79311	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TS||us||False	f	t	t
TELUS Corp. Non Voting shares	\N	USD	1	\N	f	79314	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TU||us||False	f	t	t
Shaw Communications Inc. Cl B NV	\N	USD	1	\N	f	79315	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SJR||us||False	f	t	t
Gardner Denver Inc.	\N	USD	1	\N	f	79318	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GDI||us||False	f	t	t
Teco Energy Inc.	\N	USD	1	\N	f	79321	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TE||us||False	f	t	t
Towers Watson & Co. Cl A	\N	USD	1	\N	f	79322	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TW||us||False	f	t	t
Benchmark Electronics Inc.	\N	USD	1	\N	f	79324	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BHE||us||False	f	t	t
Community Bank System Inc.	\N	USD	1	\N	f	79325	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CBU||us||False	f	t	t
Armstrong World Industries Inc.	\N	USD	1	\N	f	79327	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AWI||us||False	f	t	t
HNI Corp.	\N	USD	1	\N	f	79328	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HNI||us||False	f	t	t
Nike Inc. Cl B	\N	USD	1	\N	f	79338	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NKE||us||False	f	t	t
AngloGold Ashanti Ltd.	\N	USD	1	\N	f	79339	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AU||us||False	f	t	t
Kinross Gold Corp.	\N	USD	1	\N	f	79340	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KGC||us||False	f	t	t
Thomas & Betts Corp.	\N	USD	1	\N	f	79341	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TNB||us||False	f	t	t
CPFL Energia S.A.	\N	USD	1	\N	f	79342	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CPL||us||False	f	t	t
Atlantic Power Corp.	\N	USD	1	\N	f	79344	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AT||us||False	f	t	t
Howard Hughes Corp.	\N	USD	1	\N	f	79345	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HHC||us||False	f	t	t
Collective Brands Inc.	\N	USD	1	\N	f	79346	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PSS||us||False	f	t	t
Titan International Inc.	\N	USD	1	\N	f	79347	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TWI||us||False	f	t	t
Worthington Industries Inc.	\N	USD	1	\N	f	79357	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WOR||us||False	f	t	t
Liz Claiborne Inc.	\N	USD	1	\N	f	79403	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LIZ||us||False	f	t	t
Bankrate Inc.	\N	USD	1	\N	f	79417	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RATE||us||False	f	t	t
CH Energy Group Inc. (Holding Co.)	\N	USD	1	\N	f	79421	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CHG||us||False	f	t	t
Empire District Electric Co.	\N	USD	1	\N	f	79422	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EDE||us||False	f	t	t
Heartland Payment Systems Inc.	\N	USD	1	\N	f	79429	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HPY||us||False	f	t	t
ION Geophysical Corp.	\N	USD	1	\N	f	79430	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IO||us||False	f	t	t
Redwood Trust Inc.	\N	USD	1	\N	f	79432	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RWT||us||False	f	t	t
Fortuna Silver Mines Inc.	\N	USD	1	\N	f	79433	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FSM||us||False	f	t	t
CNA Financial Corp.	\N	USD	1	\N	f	79434	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CNA||us||False	f	t	t
First Republic Bank	\N	USD	1	\N	f	75519	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FRC||us||False	f	t	t
SolarWinds Inc.	\N	USD	1	\N	f	75520	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SWI||us||False	f	t	t
Call IBEX 35 | 9250 € | 17/02/12 | B9704	FR0011083831	EUR	5	|SGW|	f	75574	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9704||fr||False	f	t	t
Put IBEX 35 | 10000 € | 16/03/12 | B7616	FR0011058536	EUR	5	|SGW|	f	75577	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7616||fr||False	f	t	t
BOUYGUES NV	FR0010971614	EUR	1	|EURONEXT|	f	75578	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010971614||fr||False	f	t	t
BELVEDERE BSA 2004	FR0010134247	EUR	1	|EURONEXT|	f	75583	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010134247||fr||False	f	t	t
ENVIPCO HOLD. CERT	NL0000349439	EUR	1	|EURONEXT|	f	75556	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#NL0000349439||be||False	f	t	t
BELUGA STRIP	BE0005535068	EUR	1	|EURONEXT|	f	75579	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005535068||be||False	f	t	t
SNS REAAL	NL0000390706	EUR	1	|EURONEXT|	f	75555	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000390706||nl||False	f	t	t
Korn/Ferry International	\N	USD	1	\N	f	79497	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KFY||us||False	f	t	t
Astoria Financial Corp.	\N	USD	1	\N	f	79498	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AF||us||False	f	t	t
Western Alliance Bancorp.	\N	USD	1	\N	f	79499	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WAL||us||False	f	t	t
Arch Chemicals Inc.	\N	USD	1	\N	f	79501	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ARJ||us||False	f	t	t
BT Group PLC	\N	USD	1	\N	f	79503	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BT||us||False	f	t	t
Nexen Inc.	\N	USD	1	\N	f	79504	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NXY||us||False	f	t	t
Pandora Media Inc.	\N	USD	1	\N	f	79505	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#P||us||False	f	t	t
Parker Drilling Co.	\N	USD	1	\N	f	79506	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PKD||us||False	f	t	t
\N	\N	\N	\N	\N	f	75582	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0164528004||None||False	f	t	t
TAL International Group Inc.	\N	USD	1	\N	f	79507	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TAL||us||False	f	t	t
RPC Inc.	\N	USD	1	\N	f	79515	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RES||us||False	f	t	t
China Eastern Airlines Corp. Ltd.	\N	USD	1	\N	f	79518	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CEA||us||False	f	t	t
M.D.C. Holdings Inc.	\N	USD	1	\N	f	79519	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MDC||us||False	f	t	t
PRISA	ES0171743117	EUR	1	|MERCADOCONTINUO|	f	75588	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0171743117||es||False	f	t	t
KapStone Paper & Packaging Corp.	\N	USD	1	\N	f	79539	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KS||us||False	f	t	t
Symetra Financial Corp.	\N	USD	1	\N	f	79540	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SYA||us||False	f	t	t
Quanex Building Products Corp.	\N	USD	1	\N	f	79587	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NX||us||False	f	t	t
Materion Corp.	\N	USD	1	\N	f	79589	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MTRN||us||False	f	t	t
Pinnacle Entertainment Inc.	\N	USD	1	\N	f	79594	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PNK||us||False	f	t	t
KB Home	\N	USD	1	\N	f	79595	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KBH||us||False	f	t	t
Team Health Holding Inc.	\N	USD	1	\N	f	79596	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TMH||us||False	f	t	t
Quiksilver Inc.	\N	USD	1	\N	f	79597	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ZQK||us||False	f	t	t
First Commonwealth Financial Corp. (Pennsylvania)	\N	USD	1	\N	f	79600	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FCF||us||False	f	t	t
Ferro Corp.	\N	USD	1	\N	f	79602	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FOE||us||False	f	t	t
Interline Brands Inc.	\N	USD	1	\N	f	79603	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IBI||us||False	f	t	t
Quaker Chemical Corp.	\N	USD	1	\N	f	79605	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KWR||us||False	f	t	t
Textainer Group Holdings Ltd.	\N	USD	1	\N	f	79606	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TGH||us||False	f	t	t
Green Dot Corp. Cl A	\N	USD	1	\N	f	79616	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GDOT||us||False	f	t	t
Lone Pine Resources Inc.	\N	USD	1	\N	f	79617	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LPR||us||False	f	t	t
Greatbatch Inc.	\N	USD	1	\N	f	79619	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GB||us||False	f	t	t
American Greetings Corp. Cl A	\N	USD	1	\N	f	79620	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AM||us||False	f	t	t
Basic Energy Services Inc.	\N	USD	1	\N	f	79621	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BAS||us||False	f	t	t
Greenbrier Cos.	\N	USD	1	\N	f	79624	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GBX||us||False	f	t	t
Invacare Corp.	\N	USD	1	\N	f	79626	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IVC||us||False	f	t	t
Landauer Inc.	\N	USD	1	\N	f	79627	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LDR||us||False	f	t	t
Petrobras Argentina S.A.	\N	USD	1	\N	f	79630	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PZE||us||False	f	t	t
Primus Guaranty Ltd.	\N	USD	1	\N	f	79631	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PRS||us||False	f	t	t
Panasonic Corp.	\N	USD	1	\N	f	79673	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PC||us||False	f	t	t
CRH PLC	\N	USD	1	\N	f	79674	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CRH||us||False	f	t	t
Salesforce.com Inc.	\N	USD	1	\N	f	79675	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CRM||us||False	f	t	t
Parker Hannifin Corp.	\N	USD	1	\N	f	79676	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PH||us||False	f	t	t
Vanceinfo Technologies Inc.	\N	USD	1	\N	f	79681	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VIT||us||False	f	t	t
HFF Inc. Cl A	\N	USD	1	\N	f	79684	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HF||us||False	f	t	t
Dice Holdings Inc.	\N	USD	1	\N	f	79685	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DHX||us||False	f	t	t
FBL Financial Group Inc.	\N	USD	1	\N	f	79686	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FFG||us||False	f	t	t
Ruby Tuesday Inc.	\N	USD	1	\N	f	79688	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RT||us||False	f	t	t
CYBERGUN DS	FR0011063544	EUR	1	|EURONEXT|	f	75600	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011063544||fr||False	f	t	t
CRCAM BRIE PIC2CCI	FR0010483768	EUR	1	|EURONEXT|	f	75601	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010483768||fr||False	f	t	t
Call IBEX 35 | 7750 € | 17/02/12 | C1098	FR0011124031	EUR	5	|SGW|	f	75606	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1098||fr||False	f	t	t
DELACHAUX	FR0000032195	EUR	1	|EURONEXT|	f	75608	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000032195||fr||False	f	t	t
VALE	US91912E1055	EUR	1	|EURONEXT|	f	75616	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US91912E1055||fr||False	f	t	t
Put IBEX 35 | 8500 € | 21/12/12 | B7863	FR0011065663	EUR	5	|SGW|	f	75628	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7863||fr||False	f	t	t
Put IBEX 35 | 8750 € | 19/08/11 | B6054	FR0011017797	EUR	5	|SGW|	f	75632	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B6054||fr||False	f	t	t
FIN.ETANG BERRE	FR0000062341	EUR	1	|EURONEXT|	f	75634	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000062341||fr||False	f	t	t
FIN.ETANG BERRE PF	FR0000062507	EUR	1	|EURONEXT|	f	75635	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000062507||fr||False	f	t	t
NEXITY	FR0010989772	EUR	1	|EURONEXT|	f	75637	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010989772||fr||False	f	t	t
Call IBEX 35 | 11500 € | 16/09/11 | B4743	FR0010984617	EUR	5	|SGW|	f	75639	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4743||fr||False	f	t	t
Call IBEX 35 | 12000 € | 16/09/11 | B4744	FR0010984625	EUR	5	|SGW|	f	75640	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4744||fr||False	f	t	t
BELUGA	BE0003723377	EUR	1	|EURONEXT|	f	75596	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003723377||be||False	f	t	t
TELENET STRIP	BE0005599700	EUR	1	|EURONEXT|	f	75611	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005599700||be||False	f	t	t
TER BEKE	BE0003573814	EUR	1	|EURONEXT|	f	75614	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003573814||be||False	f	t	t
BANCAJA LIQUIDEZ DEUDA PUBLICA	ES0112899002	EUR	2	|BMF|0083|	f	75542	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112899002||es||False	f	t	t
NATRA	ES0165515117	EUR	1	|MERCADOCONTINUO|	f	75607	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0165515117||es||False	f	t	t
PRIM	ES0170884417	EUR	1	|MERCADOCONTINUO|	f	75609	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0170884417||es||False	f	t	t
Weis Markets Inc.	\N	USD	1	\N	f	79693	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WMK||us||False	f	t	t
Energy Partners Ltd.	\N	USD	1	\N	f	79696	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EPL||us||False	f	t	t
Investment Technology Group Inc.	\N	USD	1	\N	f	79701	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ITG||us||False	f	t	t
Flagstone Reinsurance Holdings Ltd.	\N	USD	1	\N	f	79702	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FSR||us||False	f	t	t
Kronos Worldwide Inc.	\N	USD	1	\N	f	79704	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KRO||us||False	f	t	t
US Gold Corp.	\N	USD	1	\N	f	79705	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UXG||us||False	f	t	t
iSoftStone Holdings Ltd.	\N	USD	1	\N	f	79706	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ISS||us||False	f	t	t
Ennis Inc.	\N	USD	1	\N	f	79707	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EBF||us||False	f	t	t
Callaway Golf Co.	\N	USD	1	\N	f	79710	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ELY||us||False	f	t	t
Vanguard Health Systems Inc.	\N	USD	1	\N	f	79717	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VHS||us||False	f	t	t
Intermec Inc.	\N	USD	1	\N	f	79722	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IN||us||False	f	t	t
Wausau Paper Corp.	\N	USD	1	\N	f	79724	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WPP||us||False	f	t	t
Chesapeake Utilities Corp.	\N	USD	1	\N	f	79725	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CPK||us||False	f	t	t
Central Vermont Public Service Corp.	\N	USD	1	\N	f	79726	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CV||us||False	f	t	t
Viad Corp.	\N	USD	1	\N	f	79727	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VVI||us||False	f	t	t
Tejon Ranch Co.	\N	USD	1	\N	f	79728	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TRC||us||False	f	t	t
Newfield Exploration Co.	\N	USD	1	\N	f	75123	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NFX||us||False	f	t	t
Alexandria Real Estate Equities Inc.	\N	USD	1	\N	f	75124	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ARE||us||False	f	t	t
BHP Billiton PLC	\N	USD	1	\N	f	75129	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BBL||us||False	f	t	t
Telefonica S.A.	\N	USD	1	\N	f	75130	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TEF||us||False	f	t	t
Veolia Environnement S.A.	\N	USD	1	\N	f	75141	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VE||us||False	f	t	t
Duff & Phelps Corp. Cl A	\N	USD	1	\N	f	79729	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DUF||us||False	f	t	t
\N	\N	\N	\N	\N	f	81391	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0176903005||None||False	f	t	t
Universal American Corp.	\N	USD	1	\N	f	79730	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UAM||us||False	f	t	t
Standard Pacific Corp.	\N	USD	1	\N	f	79734	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SPF||us||False	f	t	t
Urstadt Biddle Properties Inc. Cl A	\N	USD	1	\N	f	79738	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UBA||us||False	f	t	t
American Vanguard Corp.	\N	USD	1	\N	f	79777	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AVD||us||False	f	t	t
OneBeacon Insurance Group Ltd. Cl A	\N	USD	1	\N	f	79778	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OB||us||False	f	t	t
PharMerica Corp.	\N	USD	1	\N	f	79779	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PMC||us||False	f	t	t
Fly Leasing Ltd.	\N	USD	1	\N	f	79780	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FLY||us||False	f	t	t
Hilltop Holdings Inc.	\N	USD	1	\N	f	79782	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HTH||us||False	f	t	t
Vaalco Energy Inc.	\N	USD	1	\N	f	79785	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EGY||us||False	f	t	t
MFC Industrial Ltd.	\N	USD	1	\N	f	79792	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MIL||us||False	f	t	t
Valhi Inc.	\N	USD	1	\N	f	79793	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VHI||us||False	f	t	t
Furmanite Corp.	\N	USD	1	\N	f	79794	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FRM||us||False	f	t	t
Sterling Bancorp	\N	USD	1	\N	f	79798	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STL||us||False	f	t	t
E-House (China) Holdings Ltd.	\N	USD	1	\N	f	79801	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EJ||us||False	f	t	t
CBIZ Inc	\N	USD	1	\N	f	79802	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CBZ||us||False	f	t	t
Ciber Inc.	\N	USD	1	\N	f	79803	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CBR||us||False	f	t	t
Google Inc.	US38259P5089	USD	1	|NASDAQ100|	f	75644	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	GOOG||us||False	f	t	t
FISIPE	PTFSP0AE0004	EUR	1	|EURONEXT|	f	75647	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTFSP0AE0004||pt||False	f	t	t
ITT CORPORATION	US4509111021	EUR	1	|EURONEXT|	f	75643	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US4509111021||fr||False	f	t	t
CAMAIEU	FR0004008209	EUR	1	|EURONEXT|	f	75661	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004008209||fr||False	f	t	t
Put IBEX 35 | 10750 € | 20/05/11 | B4734	FR0010984526	EUR	5	|SGW|	f	75662	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4734||fr||False	f	t	t
Put IBEX 35 | 11250 € | 20/05/11 | B4735	FR0010984534	EUR	5	|SGW|	f	75663	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4735||fr||False	f	t	t
TOUAX	FR0000033003	EUR	1	|EURONEXT|	f	75669	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000033003||fr||False	f	t	t
TRANSGENE	FR0005175080	EUR	1	|EURONEXT|	f	75673	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0005175080||fr||False	f	t	t
ROBERTET	FR0000039091	EUR	1	|EURONEXT|	f	75675	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000039091||fr||False	f	t	t
Put IBEX 35 | 8750 € | 17/02/12 | B9710	FR0011083898	EUR	5	|SGW|	f	75680	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9710||fr||False	f	t	t
RECTICEL STRIP (D)	BE0005639134	EUR	1	|EURONEXT|	f	75653	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005639134||be||False	f	t	t
THUNDERBIRD	VGG885761061	EUR	1	|EURONEXT|	f	75657	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#VGG885761061||nl||False	f	t	t
Ahlers AG Vz	DE0005009732	EUR	1	|DEUTSCHEBOERSE|	f	75674	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005009732||de||False	f	t	t
Cedar Realty Trust Inc.	\N	USD	1	\N	f	79806	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CDR||us||False	f	t	t
7 Days Group Holdings Ltd.	\N	USD	1	\N	f	79807	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SVN||us||False	f	t	t
Booz Allen & Hamilton Inc.	\N	USD	1	\N	f	79808	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BAH||us||False	f	t	t
World Wrestling Entertainment Inc. Cl A	\N	USD	1	\N	f	79810	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WWE||us||False	f	t	t
Alliance One International Inc.	\N	USD	1	\N	f	79811	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AOI||us||False	f	t	t
Frontline Ltd.	\N	USD	1	\N	f	79812	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FRO||us||False	f	t	t
Federal Signal Corp.	\N	USD	1	\N	f	79814	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FSS||us||False	f	t	t
Global Cash Access Holdings Inc.	\N	USD	1	\N	f	79815	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GCA||us||False	f	t	t
XO Group Inc.	\N	USD	1	\N	f	79816	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#XOXO||us||False	f	t	t
Medifast Inc.	\N	USD	1	\N	f	79830	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MED||us||False	f	t	t
Envestnet Inc.	\N	USD	1	\N	f	79831	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ENV||us||False	f	t	t
Agree Realty Corp.	\N	USD	1	\N	f	79832	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ADC||us||False	f	t	t
DaVita Inc.	\N	USD	1	\N	f	79833	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DVA||us||False	f	t	t
Kimco Realty Corp.	\N	USD	1	\N	f	79836	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KIM||us||False	f	t	t
Gap Inc.	\N	USD	1	\N	f	79839	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GPS||us||False	f	t	t
Kemet Corp.	\N	USD	1	\N	f	79843	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KEM||us||False	f	t	t
Methode Electronics Inc.	\N	USD	1	\N	f	79847	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MEI||us||False	f	t	t
Radian Group Inc.	\N	USD	1	\N	f	79848	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RDN||us||False	f	t	t
BPZ Resources Inc.	\N	USD	1	\N	f	79851	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BPZ||us||False	f	t	t
OMNOVA Solutions Inc.	\N	USD	1	\N	f	79895	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OMN||us||False	f	t	t
Panhandle Oil & Gas Inc.	\N	USD	1	\N	f	79896	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PHX||us||False	f	t	t
Phoenix Cos. Inc.	\N	USD	1	\N	f	79897	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PNX||us||False	f	t	t
RAIT Financial Trust	\N	USD	1	\N	f	79898	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RAS||us||False	f	t	t
Talbots Inc.	\N	USD	1	\N	f	79899	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TLB||us||False	f	t	t
U-Store-It-Trust	\N	USD	1	\N	f	75155	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#YSI||us||False	f	t	t
Snap-On Inc.	\N	USD	1	\N	f	75167	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SNA||us||False	f	t	t
RPM International Inc.	\N	USD	1	\N	f	75175	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RPM||us||False	f	t	t
Banco Santander-Chile	\N	USD	1	\N	f	75176	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SAN||us||False	f	t	t
Hawaiian Electric Industries Inc.	\N	USD	1	\N	f	75177	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HE||us||False	f	t	t
Visteon Corp.	\N	USD	1	\N	f	75178	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VC||us||False	f	t	t
Mitsubishi UFJ Financial Group Inc.	\N	USD	1	\N	f	75180	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MTU||us||False	f	t	t
St. Jude Medical Inc.	\N	USD	1	\N	f	75181	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STJ||us||False	f	t	t
GOL Linhas Aereas Inteligentes S.A.	\N	USD	1	\N	f	75193	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GOL||us||False	f	t	t
CAI International Inc.	\N	USD	1	\N	f	79900	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CAP||us||False	f	t	t
Liberty Property Trust	\N	USD	1	\N	f	75641	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LRY||us||False	f	t	t
GEROVA Financial Group Ltd.	\N	USD	1	\N	f	75652	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GFC||us||False	f	t	t
ORDINA RIGHT	NL0010021994	EUR	1	|EURONEXT|	f	75683	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0010021994||nl||False	f	t	t
Research In Motion Limited	\N	USD	1	|NASDAQ100|	f	75702	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	RIMM||us||False	f	t	t
Call IBEX 35 | 9000 € | 16/03/12 | B7614	FR0011058437	EUR	5	|SGW|	f	75682	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7614||fr||False	f	t	t
Call IBEX 35 | 10250 € | 18/05/12 | C2137	FR0011145457	EUR	5	|SGW|	f	75684	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C2137||fr||False	f	t	t
NOVAGALI PHARMA	FR0011153394	EUR	1	|EURONEXT|	f	75686	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011153394||fr||False	f	t	t
ROBERTET CI	FR0000045601	EUR	1	|EURONEXT|	f	75690	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000045601||fr||False	f	t	t
SES	LU0088087324	EUR	1	|EURONEXT|	f	75705	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#LU0088087324||fr||False	f	t	t
Call IBEX 35 | 9250 € | 21/10/11 | B7206	FR0011039569	EUR	5	|SGW|	f	75713	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7206||fr||False	f	t	t
STENTYS	FR0010949404	EUR	1	|EURONEXT|	f	75730	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010949404||fr||False	f	t	t
Call IBEX 35 | 8750 € | 20/04/12 | C1106	FR0011124114	EUR	5	|SGW|	f	75733	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1106||fr||False	f	t	t
MODELABS	FR0011061787	EUR	1	|EURONEXT|	f	75738	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011061787||fr||False	f	t	t
SOLVAC STRIP	BE0005612834	EUR	1	|EURONEXT|	f	75712	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005612834||be||False	f	t	t
\N	\N	\N	\N	\N	f	76446	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0165237001||None||False	f	t	t
Overseas Shipholding Group Inc.	\N	USD	1	\N	f	79919	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OSG||us||False	f	t	t
China Yuchai International Ltd.	\N	USD	1	\N	f	79921	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CYD||us||False	f	t	t
GenCorp Inc.	\N	USD	1	\N	f	79922	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GY||us||False	f	t	t
Wesco Aircraft Holdings Inc.	\N	USD	1	\N	f	79927	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WAIR||us||False	f	t	t
Unitil Corp.	\N	USD	1	\N	f	79928	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UTL||us||False	f	t	t
Symmetry Medical Inc.	\N	USD	1	\N	f	79929	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SMA||us||False	f	t	t
GAMCO Investors Inc. Cl A	\N	USD	1	\N	f	79931	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GBL||us||False	f	t	t
Journal Communications Inc. Cl A	\N	USD	1	\N	f	79932	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JRN||us||False	f	t	t
M/I Homes Inc.	\N	USD	1	\N	f	79933	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MHO||us||False	f	t	t
North American Energy Partners Inc.	\N	USD	1	\N	f	79937	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NOA||us||False	f	t	t
One Liberty Properties Inc.	\N	USD	1	\N	f	79940	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OLP||us||False	f	t	t
Dynegy Inc.	\N	USD	1	\N	f	79943	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DYN||us||False	f	t	t
Active Network Inc.	\N	USD	1	\N	f	79947	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ACTV||us||False	f	t	t
Terreno Realty Corp.	\N	USD	1	\N	f	80020	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TRNO||us||False	f	t	t
Global Geophysical Services Inc.	\N	USD	1	\N	f	80035	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GGS||us||False	f	t	t
MagnaChip Semiconductor Corp.	\N	USD	1	\N	f	80040	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MX||us||False	f	t	t
China Ming Yang Wind Power Group Ltd.	\N	USD	1	\N	f	80041	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MY||us||False	f	t	t
Costamare Inc.	\N	USD	1	\N	f	80042	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CMRE||us||False	f	t	t
Vishay Precision Group Inc.	\N	USD	1	\N	f	80045	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VPG||us||False	f	t	t
Federal Agricultural Mortgage Corp. Cl C	\N	USD	1	\N	f	80046	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AGM||us||False	f	t	t
Ampco-Pittsburgh Corp.	\N	USD	1	\N	f	80047	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AP||us||False	f	t	t
Crown Castle International Corp.	\N	USD	1	\N	f	75197	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CCI||us||False	f	t	t
Gammon Gold Inc.	\N	USD	1	\N	f	75203	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GRS||us||False	f	t	t
SunTrust Banks Inc.	\N	USD	1	\N	f	75211	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STI||us||False	f	t	t
Weyerhaeuser Co.	\N	USD	1	\N	f	75214	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WY||us||False	f	t	t
Energizer Holdings Inc.	\N	USD	1	\N	f	75217	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ENR||us||False	f	t	t
Plains Exploration & Production Co.	\N	USD	1	\N	f	75221	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PXP||us||False	f	t	t
Steris Corp.	\N	USD	1	\N	f	75224	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STE||us||False	f	t	t
National Oilwell Varco Inc.	\N	USD	1	\N	f	75229	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NOV||us||False	f	t	t
Call IBEX 35 | 9250 € | 20/04/12 | C1107	FR0011124122	EUR	5	|SGW|	f	75740	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1107||fr||False	f	t	t
EDF ENERGIES NOUV.	FR0011056001	EUR	1	|EURONEXT|	f	75744	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011056001||fr||False	f	t	t
Put IBEX 35 | 8000 € | 20/12/13 | B7868	FR0011065713	EUR	5	|SGW|	f	75745	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7868||fr||False	f	t	t
Call IBEX 35 | 11500 € | 16/03/12 | B7612	FR0011058486	EUR	5	|SGW|	f	75750	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7612||fr||False	f	t	t
Call IBEX 35 | 6750 € | 20/04/12 | C1102	FR0011124072	EUR	5	|SGW|	f	75754	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1102||fr||False	f	t	t
STALLERGENES	FR0000065674	EUR	1	|EURONEXT|	f	75756	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000065674||fr||False	f	t	t
Put IBEX 35 | 8500 € | 16/09/11 | B4747	FR0010984658	EUR	5	|SGW|	f	75779	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4747||fr||False	f	t	t
BELIER	FR0000072399	EUR	1	|EURONEXT|	f	75780	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000072399||fr||False	f	t	t
BEFIMMO-SICAFI	BE0003678894	EUR	1	|EURONEXT|	f	75777	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003678894||be||False	f	t	t
AP ALTERNAT ASSETS	GB00B15Y0C52	EUR	1	|EURONEXT|	f	75749	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GB00B15Y0C52||nl||False	f	t	t
SKW Stahl-Metallurgie Holding AG	DE000SKWM013	EUR	1	|DEUTSCHEBOERSE|	f	75765	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000SKWM013||de||False	f	t	t
Kimberly-Clark Corp.	\N	USD	1	\N	f	75232	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KMB||us||False	f	t	t
Scorpio Tankers Inc.	\N	USD	1	\N	f	80050	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STNG||us||False	f	t	t
Mac-Gray Corp.	\N	USD	1	\N	f	80052	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TUC||us||False	f	t	t
Kenneth Cole Productions Inc. Cl A	\N	USD	1	\N	f	80143	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KCP||us||False	f	t	t
Miller Energy Resources Inc.	\N	USD	1	\N	f	80144	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MILL||us||False	f	t	t
Martha Stewart Living Omnimedia Inc.	\N	USD	1	\N	f	80145	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MSO||us||False	f	t	t
TRC Cos. Inc.	\N	USD	1	\N	f	80146	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TRR||us||False	f	t	t
Lin TV Corp.	\N	USD	1	\N	f	80147	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TVL||us||False	f	t	t
JMP Group Corp.	\N	USD	1	\N	f	80148	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JMP||us||False	f	t	t
Duoyuan Global Water Inc.	\N	USD	1	\N	f	80149	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DGW||us||False	f	t	t
Skilled Healthcare Group Inc. Cl A	\N	USD	1	\N	f	80150	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SKH||us||False	f	t	t
Ambow Education Holding Ltd.	\N	USD	1	\N	f	80152	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AMBO||us||False	f	t	t
Pulse Electronics Corp.	\N	USD	1	\N	f	80153	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PULS||us||False	f	t	t
Imperial Holdings Inc.	\N	USD	1	\N	f	80154	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IFT||us||False	f	t	t
Kingsway Financial Services Inc.	\N	USD	1	\N	f	80157	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KFS||us||False	f	t	t
Paragon Shipping Inc. Cl A	\N	USD	1	\N	f	80160	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PRGN||us||False	f	t	t
The Dolan Co.	\N	USD	1	\N	f	80341	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DM||us||False	f	t	t
USANA Health Sciences Inc.	\N	USD	1	\N	f	80343	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#USNA||us||False	f	t	t
Pzena Investment Management Inc.	\N	USD	1	\N	f	80550	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PZN||us||False	f	t	t
Deutsche Postbank AG	DE0008001009	None	1	|DAX|DEUTSCHEBOERSE|	f	75762					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE0008001009||de||False	f	t	t
National Fuel Gas Co.	\N	USD	1	\N	f	80883	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NFG||us||False	f	t	t
Martin Marietta Materials Inc.	\N	USD	1	\N	f	80885	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MLM||us||False	f	t	t
Hexcel Corp.	\N	USD	1	\N	f	80886	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HXL||us||False	f	t	t
Acuity Brands Inc.	\N	USD	1	\N	f	80887	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AYI||us||False	f	t	t
ProAssurance Corp.	\N	USD	1	\N	f	80888	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PRA||us||False	f	t	t
HealthSouth Corp.	\N	USD	1	\N	f	80889	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HLS||us||False	f	t	t
Covanta Holding Corp.	\N	USD	1	\N	f	80890	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CVA||us||False	f	t	t
USG Corp.	\N	USD	1	\N	f	80891	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#USG||us||False	f	t	t
Tyco International Ltd.	\N	USD	1	\N	f	75242	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TYC||us||False	f	t	t
General Dynamics Corp.	\N	USD	1	\N	f	75244	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GD||us||False	f	t	t
Equity Residential	\N	USD	1	\N	f	75252	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EQR||us||False	f	t	t
Knoll Inc.	\N	USD	1	\N	f	80892	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KNL||us||False	f	t	t
Dycom Industries Inc.	\N	USD	1	\N	f	80893	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DY||us||False	f	t	t
Citrix Systems, Inc	US1773761002	USD	1	|NASDAQ100|	f	75739	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	CTXS||us||False	f	t	t
Cintas Corporation	US1729081059	USD	1	|NASDAQ100|	f	75746	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	CTAS||us||False	f	t	t
BPIDI11(1P10)	PTBPI0AMI043	EUR	1	|EURONEXT|	f	75787	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTBPI0AMI043||pt||False	f	t	t
Put IBEX 35 | 10000 € | 16/09/11 | B4750	FR0010984682	EUR	5	|SGW|	f	75781	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4750||fr||False	f	t	t
BIOALLIANCE PHARMA	FR0010095596	EUR	1	|EURONEXT|	f	75782	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010095596||fr||False	f	t	t
Put IBEX 35 | 10500 € | 16/09/11 | B4751	FR0010984690	EUR	5	|SGW|	f	75784	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4751||fr||False	f	t	t
Call IBEX 35 | 9750 € | 18/05/12 | C1120	FR0011124254	EUR	5	|SGW|	f	75789	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1120||fr||False	f	t	t
NATUREX BS	FR0011128768	EUR	1	|EURONEXT|	f	75796	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011128768||fr||False	f	t	t
UMANIS	FR0010949388	EUR	1	|EURONEXT|	f	75798	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010949388||fr||False	f	t	t
Call IBEX 35 inLine | 9000 € | 14/12/11 | I0041	FR0011081397	EUR	5	|SGW|	f	75799	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0041||fr||False	f	t	t
Call IBEX 35 inLine | 9000 € | 14/12/11 | I0042	FR0011081405	EUR	5	|SGW|	f	75803	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0042||fr||False	f	t	t
Call IBEX 35 | 11750 € | 19/08/11 | B6051	FR0011017763	EUR	5	|SGW|	f	75804	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B6051||fr||False	f	t	t
Put IBEX 35 | 7250 € | 18/05/12 | C1122	FR0011124270	EUR	5	|SGW|	f	75807	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1122||fr||False	f	t	t
FREY DS	FR0011065267	EUR	1	|EURONEXT|	f	75811	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011065267||fr||False	f	t	t
Call IBEX 35 inLine | 8500 € | 14/12/11 | I0040	FR0011081389	EUR	5	|SGW|	f	75824	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0040||fr||False	f	t	t
TKH GROUP	NL0000852523	EUR	1	|EURONEXT|	f	75785	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000852523||nl||False	f	t	t
TOMTOM	NL0000387058	EUR	1	|EURONEXT|	f	75791	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000387058||nl||False	f	t	t
ANTONOV	GB00B3SHND79	EUR	1	|EURONEXT|	f	75826	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GB00B3SHND79||nl||False	f	t	t
Spectrum Brands Holdings Inc.	\N	USD	1	\N	f	80894	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SPB||us||False	f	t	t
American States Water Co.	\N	USD	1	\N	f	80895	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AWR||us||False	f	t	t
Armour Residential REIT Inc.	\N	USD	1	\N	f	80896	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ARR||us||False	f	t	t
\N	\N	\N	\N	\N	f	75820	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0142097007||None||False	f	t	t
Inland Real Estate Corp.	\N	USD	1	\N	f	80897	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IRC||us||False	f	t	t
TrueBlue Inc.	\N	USD	1	\N	f	80898	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TBI||us||False	f	t	t
Ethan Allen Interiors Inc.	\N	USD	1	\N	f	80899	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ETH||us||False	f	t	t
Graphic Packaging Holding Co.	\N	USD	1	\N	f	80900	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GPK||us||False	f	t	t
Kindred Healthcare Inc.	\N	USD	1	\N	f	80901	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KND||us||False	f	t	t
Meritage Homes Corp.	\N	USD	1	\N	f	80902	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MTH||us||False	f	t	t
Mechel OAO	\N	USD	1	\N	f	80903	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MTL||us||False	f	t	t
Rogers Corp.	\N	USD	1	\N	f	80904	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ROG||us||False	f	t	t
Jaguar Mining Inc.	\N	USD	1	\N	f	80905	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JAG||us||False	f	t	t
Flotek Industries Inc.	\N	USD	1	\N	f	80906	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FTK||us||False	f	t	t
ACCO Brands Corp.	\N	USD	1	\N	f	80907	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ABD||us||False	f	t	t
Kenexa Corp.	\N	USD	1	\N	f	80908	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KNXA||us||False	f	t	t
Park Electrochemical Corp.	\N	USD	1	\N	f	80909	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PKE||us||False	f	t	t
Newcastle Investment Corp.	\N	USD	1	\N	f	80910	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NCT||us||False	f	t	t
Tredegar Corp.	\N	USD	1	\N	f	80911	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TG||us||False	f	t	t
iStar Financial Inc.	\N	USD	1	\N	f	80912	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SFI||us||False	f	t	t
Guangshen Railway Co. Ltd.	\N	USD	1	\N	f	80913	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GSH||us||False	f	t	t
Cascade Corp.	\N	USD	1	\N	f	80914	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CASC||us||False	f	t	t
Barnes & Noble Inc.	\N	USD	1	\N	f	80915	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BKS||us||False	f	t	t
Felcor Lodging Trust Inc.	\N	USD	1	\N	f	80916	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FCH||us||False	f	t	t
Premiere Global Services Inc.	\N	USD	1	\N	f	80936	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PGI||us||False	f	t	t
Ramco-Gershenson Properties Trust	\N	USD	1	\N	f	80937	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RPT||us||False	f	t	t
Krispy Kreme Doughnuts Inc.	\N	USD	1	\N	f	80938	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KKD||us||False	f	t	t
Mueller Water Products Inc.	\N	USD	1	\N	f	80939	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MWA||us||False	f	t	t
Checkpoint Systems Inc.	\N	USD	1	\N	f	80940	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CKP||us||False	f	t	t
InterXion Holding N.V.	\N	USD	1	\N	f	80941	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#INXN||us||False	f	t	t
E-Commerce China Dangdang Inc.	\N	USD	1	\N	f	80942	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DANG||us||False	f	t	t
Hyperdynamics Corp.	\N	USD	1	\N	f	80943	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HDY||us||False	f	t	t
LDK Solar Co. Ltd.	\N	USD	1	\N	f	80944	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LDK||us||False	f	t	t
Dynex Capital Inc.	\N	USD	1	\N	f	80945	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DX||us||False	f	t	t
APRIL	FR0004037125	EUR	1	|EURONEXT|	f	75827	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004037125||fr||False	f	t	t
BONDUELLE	FR0000063935	EUR	1	|EURONEXT|	f	75828	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000063935||fr||False	f	t	t
Call IBEX 35 inLine | 8000 € | 14/12/11 | I0039	FR0011081371	EUR	5	|SGW|	f	75836	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0039||fr||False	f	t	t
Put IBEX 35 | 11250 € | 19/08/11 | B6059	FR0011017847	EUR	5	|SGW|	f	75845	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B6059||fr||False	f	t	t
CAST	FR0000072894	EUR	1	|EURONEXT|	f	75848	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000072894||fr||False	f	t	t
VAN DE VELDE	BE0003839561	EUR	1	|EURONEXT|	f	75849	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003839561||be||False	f	t	t
Vossloh AG	DE0007667107	EUR	1	|DEUTSCHEBOERSE|	f	75851	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007667107||de||False	f	t	t
Ormat Technologies Inc.	\N	USD	1	\N	f	80948	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ORA||us||False	f	t	t
Calix Inc.	\N	USD	1	\N	f	80949	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CALX||us||False	f	t	t
Stewart Information Services Corp.	\N	USD	1	\N	f	80950	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STC||us||False	f	t	t
Pilgrim's Pride Corp.	\N	USD	1	\N	f	80951	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PPC||us||False	f	t	t
Summit Hotel Properties Inc.	\N	USD	1	\N	f	80952	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#INN||us||False	f	t	t
GP Strategies Corp.	\N	USD	1	\N	f	80953	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GPX||us||False	f	t	t
Haverty Furniture Cos. Inc.	\N	USD	1	\N	f	80954	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HVT||us||False	f	t	t
Express Scripts, Inc	US3021821000	USD	1	|NASDAQ100|	f	75277	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	ESRX||us||False	f	t	t
FLIR Systems, Inc.	US3024451011	USD	1	|NASDAQ100|	f	75279	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	FLIR||us||False	f	t	t
DELL	US24702R1014	USD	1	|NASDAQ100|	f	75788	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	DELL||us||False	f	t	t
PG&E Corp.	\N	USD	1	\N	f	75253	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PCG||us||False	f	t	t
Pearson PLC	\N	USD	1	\N	f	75260	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PSO||us||False	f	t	t
Petrohawk Energy Corp.	\N	USD	1	\N	f	75266	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HK||us||False	f	t	t
American Campus Communities Inc.	\N	USD	1	\N	f	75271	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ACC||us||False	f	t	t
Harman International Industries Inc.	\N	USD	1	\N	f	75272	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HAR||us||False	f	t	t
MetroPCS Communications Inc.	\N	USD	1	\N	f	75274	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PCS||us||False	f	t	t
Equity Lifestyle Properties Inc.	\N	USD	1	\N	f	75276	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ELS||us||False	f	t	t
Stoneridge Inc.	\N	USD	1	\N	f	80955	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SRI||us||False	f	t	t
SWS Group Inc.	\N	USD	1	\N	f	80956	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SWS||us||False	f	t	t
Ameresco Inc. Cl A	\N	USD	1	\N	f	80957	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AMRC||us||False	f	t	t
Beazer Homes USA Inc.	\N	USD	1	\N	f	80958	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BZH||us||False	f	t	t
SouFun Holdings Ltd.	\N	USD	1	\N	f	80959	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SFUN||us||False	f	t	t
Aeroflex Holding Corp.	\N	USD	1	\N	f	80960	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ARX||us||False	f	t	t
Phoenix New Media Ltd. Cl A	\N	USD	1	\N	f	80961	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FENG||us||False	f	t	t
American Safety Insurance Holdings Ltd.	\N	USD	1	\N	f	80962	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ASI||us||False	f	t	t
AMN Healthcare Services Inc.	\N	USD	1	\N	f	80963	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AHS||us||False	f	t	t
Cogdell Spencer Inc.	\N	USD	1	\N	f	80964	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CSA||us||False	f	t	t
Entercom Communications Corp. Cl A	\N	USD	1	\N	f	80965	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ETM||us||False	f	t	t
Parkway Properties Inc.	\N	USD	1	\N	f	80966	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PKY||us||False	f	t	t
Transportadora de Gas del Sur S.A.	\N	USD	1	\N	f	80967	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TGS||us||False	f	t	t
Speedway Motorsports Inc.	\N	USD	1	\N	f	80968	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TRK||us||False	f	t	t
AG Mortgage Investment Trust Inc.	\N	USD	1	\N	f	80969	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MITT||us||False	f	t	t
Willbros Group Inc.	\N	USD	1	\N	f	80970	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WG||us||False	f	t	t
WNS (Holdings) Ltd.	\N	USD	1	\N	f	80971	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WNS||us||False	f	t	t
Oppenheimer Holdings Inc.	\N	USD	1	\N	f	80972	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OPY||us||False	f	t	t
MarineMax Inc.	\N	USD	1	\N	f	80973	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HZO||us||False	f	t	t
Imation Corp.	\N	USD	1	\N	f	80974	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IMN||us||False	f	t	t
IRSA-Inversiones y Representaciones S.A. GDS	\N	USD	1	\N	f	80975	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IRS||us||False	f	t	t
Industrias Bachoco S.A.B. de C.V.	\N	USD	1	\N	f	80996	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IBA||us||False	f	t	t
Miller Industries Inc.	\N	USD	1	\N	f	80997	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MLR||us||False	f	t	t
Genie Energy Ltd. Cl B	\N	USD	1	\N	f	80998	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GNE||us||False	f	t	t
Aegean Marine Petroleum Network Inc.	\N	USD	1	\N	f	80999	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ANW||us||False	f	t	t
Doral Financial Corp.	\N	USD	1	\N	f	81000	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DRL||us||False	f	t	t
Arlington Asset Investment Corp. Cl A	\N	USD	1	\N	f	81001	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AI||us||False	f	t	t
Checkpoint Software Technologies	IL0010824113	USD	1	|NASDAQ100|	f	75830	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	CHKP||us||False	f	t	t
TONN.FRANCOIS FRES	FR0000071904	EUR	1	|EURONEXT|	f	75871	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000071904||fr||False	f	t	t
FRANCE TELEC NV11	FR0010833467	EUR	1	|EURONEXT|	f	75874	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010833467||fr||False	f	t	t
CESAR	FR0010540997	EUR	1	|EURONEXT|	f	75875	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010540997||fr||False	f	t	t
Aeropostale Inc.	\N	USD	1	\N	f	81613	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ARO||us||False	f	t	t
Call IBEX 35 | 9750 € | 20/04/12 | C1108	FR0011124130	EUR	5	|SGW|	f	75876	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1108||fr||False	f	t	t
Put IBEX 35 | 6750 € | 20/04/12 | C1109	FR0011124148	EUR	5	|SGW|	f	75877	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1109||fr||False	f	t	t
ZENITEL	BE0003806230	EUR	1	|EURONEXT|	f	75863	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003806230||be||False	f	t	t
Pernod Ricard NV	FR0000120693	EUR	1	|CAC|	f	75838					100	c	0	3	RI.PA	{1}	{3}	RI.PA||fr||False	f	t	t
DEVGEN	BE0003821387	EUR	1	|EURONEXT|	f	75890	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003821387||be||False	f	t	t
STOCK VOLTA FIN	NL0009864792	EUR	1	|EURONEXT|	f	75895	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009864792||nl||False	f	t	t
WILEX AG	DE0006614720	EUR	1	|DEUTSCHEBOERSE|	f	75854	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006614720||de||False	f	t	t
WINCOR NIXDORF Aktiengesellschaft	DE000A0CAYB2	EUR	1	|DEUTSCHEBOERSE|	f	75855	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0CAYB2||de||False	f	t	t
Wirecard AG	DE0007472060	EUR	1	|DEUTSCHEBOERSE|	f	75857	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007472060||de||False	f	t	t
Wizcom Technologies Ltd.	IL0010830706	EUR	1	|DEUTSCHEBOERSE|	f	75858	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#IL0010830706||de||False	f	t	t
Hill International Inc.	\N	USD	1	\N	f	81002	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HIL||us||False	f	t	t
Hovnanian Enterprises Inc. Cl A	\N	USD	1	\N	f	81003	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HOV||us||False	f	t	t
Lydall Inc.	\N	USD	1	\N	f	81004	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LDL||us||False	f	t	t
Omega Protein Corp.	\N	USD	1	\N	f	81005	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OME||us||False	f	t	t
Roadrunner Transportation Systems Inc.	\N	USD	1	\N	f	81006	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RRTS||us||False	f	t	t
Unifi Inc.	\N	USD	1	\N	f	81007	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UFI||us||False	f	t	t
Nokia Corp.	\N	USD	1	\N	f	75305	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NOK||us||False	f	t	t
Horizon Lines Inc.	\N	USD	1	\N	f	75311	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HRZ||us||False	f	t	t
Unitrin Inc.	\N	USD	1	\N	f	75315	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UTR||us||False	f	t	t
Rogers Communications Inc. Cl B	\N	USD	1	\N	f	75323	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RCI||us||False	f	t	t
VF Corp.	\N	USD	1	\N	f	75324	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VFC||us||False	f	t	t
PulteGroup Inc.	\N	USD	1	\N	f	75326	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PHM||us||False	f	t	t
Johnson & Johnson	\N	USD	1	\N	f	75331	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JNJ||us||False	f	t	t
HDFC Bank Ltd.	\N	USD	1	\N	f	75336	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HDB||us||False	f	t	t
CryoLife Inc.	\N	USD	1	\N	f	81008	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CRY||us||False	f	t	t
Flagstar Bancorp Inc.	\N	USD	1	\N	f	81009	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FBC||us||False	f	t	t
ReneSola Ltd.	\N	USD	1	\N	f	81010	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SOL||us||False	f	t	t
TAL Education Group	\N	USD	1	\N	f	81011	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#XRS||us||False	f	t	t
Schiff Nutrition International Inc. Cl A	\N	USD	1	\N	f	81012	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WNI||us||False	f	t	t
Alon USA Energy Inc.	\N	USD	1	\N	f	81013	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ALJ||us||False	f	t	t
A. H. Belo Corp. Series A	\N	USD	1	\N	f	81014	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AHC||us||False	f	t	t
MaxLinear Inc.	\N	USD	1	\N	f	81015	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MXL||us||False	f	t	t
Entravision Communications Corp.	\N	USD	1	\N	f	81016	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EVC||us||False	f	t	t
Luby's Inc.	\N	USD	1	\N	f	81017	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LUB||us||False	f	t	t
First BanCorp (Puerto Rico)	\N	USD	1	\N	f	81018	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FBP||us||False	f	t	t
First Marblehead Corp.	\N	USD	1	\N	f	81019	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FMD||us||False	f	t	t
Independence Holding Co.	\N	USD	1	\N	f	81020	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IHC||us||False	f	t	t
Marine Products Corp.	\N	USD	1	\N	f	81021	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MPX||us||False	f	t	t
Christopher & Banks Corp.	\N	USD	1	\N	f	81025	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CBK||us||False	f	t	t
BRT Realty Trust	\N	USD	1	\N	f	81026	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BRT||us||False	f	t	t
L.S. Starrett Co. Cl A	\N	USD	1	\N	f	81027	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SCX||us||False	f	t	t
China Zenix Auto International Ltd.	\N	USD	1	\N	f	81028	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ZX||us||False	f	t	t
Sealy Corp.	\N	USD	1	\N	f	81029	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ZZ||us||False	f	t	t
Capital Trust Inc. Cl A	\N	USD	1	\N	f	81030	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CT||us||False	f	t	t
GMX Resources Inc.	\N	USD	1	\N	f	81031	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GMXR||us||False	f	t	t
Costco Wholesale Corporation	US22160K1051	USD	1	|NASDAQ100|	f	75891	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	COST||us||False	f	t	t
China Life Insurance Co. Ltd.	\N	USD	1	\N	f	75869	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LFC||us||False	f	t	t
Brookfield Asset Management Inc. Cl A	\N	USD	1	\N	f	75870	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BAM||us||False	f	t	t
Ryder System Inc.	\N	USD	1	\N	f	75873	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#R||us||False	f	t	t
White Mountains Insurance Group Ltd.	\N	USD	1	\N	f	75880	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WTM||us||False	f	t	t
Brown & Brown Inc.	\N	USD	1	\N	f	75882	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BRO||us||False	f	t	t
ALSTOM NV	FR0010978791	EUR	1	|EURONEXT|	f	75901	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010978791||fr||False	f	t	t
SILIC NV	FR0011168897	EUR	1	|EURONEXT|	f	75916	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011168897||fr||False	f	t	t
Put IBEX 35 | 6750 € | 18/05/12 | C1121	FR0011124262	EUR	5	|SGW|	f	75917	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1121||fr||False	f	t	t
Put IBEX 35 | 7500 € | 21/09/12 | C3297	FR0011168376	EUR	5	|SGW|	f	75918	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3297||fr||False	f	t	t
Put IBEX 35 | 8000 € | 21/09/12 | C3298	FR0011168384	EUR	5	|SGW|	f	75922	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3298||fr||False	f	t	t
MERCIALYS NV	FR0010997940	EUR	1	|EURONEXT|	f	75927	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010997940||fr||False	f	t	t
MERSEN NV	FR0010978718	EUR	1	|EURONEXT|	f	75929	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010978718||fr||False	f	t	t
RHODIA NV	FR0010980300	EUR	1	|EURONEXT|	f	75931	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010980300||fr||False	f	t	t
EXEL INDUSTRIES	FR0004527638	EUR	1	|EURONEXT|	f	75935	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004527638||fr||False	f	t	t
FIMALAC	FR0000037947	EUR	1	|EURONEXT|	f	75936	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000037947||fr||False	f	t	t
FLEURY MICHON	FR0000074759	EUR	1	|EURONEXT|	f	75942	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000074759||fr||False	f	t	t
GROUPE FLO	FR0004076891	EUR	1	|EURONEXT|	f	75943	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004076891||fr||False	f	t	t
YOC AG	DE0005932735	EUR	1	|DEUTSCHEBOERSE|	f	75913	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005932735||de||False	f	t	t
Par Technology Corp.	\N	USD	1	\N	f	81058	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PAR||us||False	f	t	t
ShangPharma Corp.	\N	USD	1	\N	f	81059	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SHP||us||False	f	t	t
China Xiniya Fashion Ltd.	\N	USD	1	\N	f	81060	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#XNY||us||False	f	t	t
Cephalon Inc.	US1567081096	USD	1	|NASDAQ100|	f	75353	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	CEPH||us||False	f	t	t
Consolidated Edison Inc.	\N	USD	1	\N	f	75339	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ED||us||False	f	t	t
Entergy Corp.	\N	USD	1	\N	f	75358	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ETR||us||False	f	t	t
Unum Group	\N	USD	1	\N	f	75363	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UNM||us||False	f	t	t
Baytex Energy Corp.	\N	USD	1	\N	f	75367	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BTE||us||False	f	t	t
Cabot Oil & Gas Corp.	\N	USD	1	\N	f	75368	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#COG||us||False	f	t	t
YPF S.A.	\N	USD	1	\N	f	75369	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#YPF||us||False	f	t	t
Wolverine World Wide Inc.	\N	USD	1	\N	f	75371	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WWW||us||False	f	t	t
Robbins & Myers Inc.	\N	USD	1	\N	f	75372	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RBN||us||False	f	t	t
Bally Technologies Inc.	\N	USD	1	\N	f	75373	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BYI||us||False	f	t	t
Barnes Group Inc.	\N	USD	1	\N	f	75374	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#B||us||False	f	t	t
Emergency Medical Services Corp. Cl A	\N	USD	1	\N	f	75375	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EMS||us||False	f	t	t
Laboratory Corp. of America Holdings	\N	USD	1	\N	f	75376	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LH||us||False	f	t	t
Clorox Co.	\N	USD	1	\N	f	75377	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CLX||us||False	f	t	t
Rockwell Collins Inc.	\N	USD	1	\N	f	75381	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#COL||us||False	f	t	t
Republic Services Inc.	\N	USD	1	\N	f	75384	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RSG||us||False	f	t	t
NetQin Mobile Inc.	\N	USD	1	\N	f	81063	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NQ||us||False	f	t	t
Feihe International Inc.	\N	USD	1	\N	f	81065	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ADY||us||False	f	t	t
Alliance HealthCare Services Inc.	\N	USD	1	\N	f	81066	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AIQ||us||False	f	t	t
Grupo Casa Saba S.A.B. de C.V.	\N	USD	1	\N	f	81067	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SAB||us||False	f	t	t
First Acceptance Corp.	\N	USD	1	\N	f	81068	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FAC||us||False	f	t	t
Qiao Xing Mobile Communication Co. Ltd.	\N	USD	1	\N	f	81069	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#QXM||us||False	f	t	t
Gushan Environmental Energy Ltd.	\N	USD	1	\N	f	81070	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GU||us||False	f	t	t
IFM Investments Ltd.	\N	USD	1	\N	f	81072	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CTC||us||False	f	t	t
Syswin Inc.	\N	USD	1	\N	f	81073	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SYSW||us||False	f	t	t
China Mass Media Corp.	\N	USD	1	\N	f	81086	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CMM||us||False	f	t	t
California Water Service Group	\N	USD	1	\N	f	81565	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CWT||us||False	f	t	t
Magnum Hunter Resources Corp.	\N	USD	1	\N	f	81566	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MHR||us||False	f	t	t
Empresas ICA S.A.B. de C.V.	\N	USD	1	\N	f	81587	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ICA||us||False	f	t	t
Sun Communities Inc.	\N	USD	1	\N	f	81588	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SUI||us||False	f	t	t
KLA-Tencor Corporation	\N	USD	1	|NASDAQ100|	f	75898	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	KLAC||us||False	f	t	t
Symantec Corporation	\N	USD	1	|NASDAQ100|	f	75928	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	SYMC||us||False	f	t	t
Frontier Oil Corp.	\N	USD	1	\N	f	75900	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FTO||us||False	f	t	t
WATSCO	US9426222009	EUR	1	|EURONEXT|	f	75955	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US9426222009||fr||False	f	t	t
DALET	FR0011026749	EUR	1	|EURONEXT|	f	75964	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011026749||fr||False	f	t	t
ELEC.STRASBOURG	FR0000031023	EUR	1	|EURONEXT|	f	75966	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000031023||fr||False	f	t	t
Graham Packaging Co. Inc.	\N	USD	1	\N	f	75602	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GRM||us||False	f	t	t
DEVOTEAM NV	FR0010987271	EUR	1	|EURONEXT|	f	75977	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010987271||fr||False	f	t	t
MediClin AG	DE0006595101	EUR	1	|DEUTSCHEBOERSE|	f	75968	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006595101||de||False	f	t	t
MeVis Medical Solutions AG	DE000A0LBFE4	EUR	1	|DEUTSCHEBOERSE|	f	75969	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0LBFE4||de||False	f	t	t
MLP AG	DE0006569908	EUR	1	|DEUTSCHEBOERSE|	f	75970	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006569908||de||False	f	t	t
Hersha Hospitality Trust Cl A	\N	USD	1	\N	f	81589	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HT||us||False	f	t	t
Unisys Corp.	\N	USD	1	\N	f	81590	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UIS||us||False	f	t	t
Hill-Rom Holdings Inc.	\N	USD	1	\N	f	81591	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HRC||us||False	f	t	t
CA Technologies	US12673P1057	USD	1	|NASDAQ100|	f	75422	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	CA||us||False	f	t	t
Microchip Technolgy, Inc	\N	USD	1	|NASDAQ100|	f	75424	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	MCHP||us||False	f	t	t
Reed Elsevier N.V.	\N	USD	1	\N	f	75385	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ENL||us||False	f	t	t
Massey Energy Co.	\N	USD	1	\N	f	75394	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MEE||us||False	f	t	t
IntercontinentalExchange Inc.	\N	USD	1	\N	f	75397	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ICE||us||False	f	t	t
Dr Pepper Snapple Group Inc.	\N	USD	1	\N	f	75402	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DPS||us||False	f	t	t
Lubrizol Corp.	\N	USD	1	\N	f	75405	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LZ||us||False	f	t	t
ONEOK Inc.	\N	USD	1	\N	f	75419	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OKE||us||False	f	t	t
National Retail Properties Inc.	\N	USD	1	\N	f	75421	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NNN||us||False	f	t	t
Edwards Lifesciences Corp.	\N	USD	1	\N	f	75427	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EW||us||False	f	t	t
SEACOR Holding Inc.	\N	USD	1	\N	f	81592	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CKH||us||False	f	t	t
Genesco Inc.	\N	USD	1	\N	f	81607	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GCO||us||False	f	t	t
Ocwen Financial Corp.	\N	USD	1	\N	f	81608	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OCN||us||False	f	t	t
Kosmos Energy Ltd.	\N	USD	1	\N	f	81609	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KOS||us||False	f	t	t
Corporate Executive Board Co.	\N	USD	1	\N	f	81610	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EXBD||us||False	f	t	t
Allete Inc.	\N	USD	1	\N	f	81612	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ALE||us||False	f	t	t
Eagle Materials Inc.	\N	USD	1	\N	f	81614	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EXP||us||False	f	t	t
Brink's Co.	\N	USD	1	\N	f	81615	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BCO||us||False	f	t	t
Simpson Manufacturing Co.	\N	USD	1	\N	f	81616	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SSD||us||False	f	t	t
Titanium Metals Corp.	\N	USD	1	\N	f	81617	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TIE||us||False	f	t	t
NorthWestern Corp.	\N	USD	1	\N	f	81618	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NWE||us||False	f	t	t
RLI Corp.	\N	USD	1	\N	f	81619	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RLI||us||False	f	t	t
Group 1 Automotive Inc.	\N	USD	1	\N	f	81620	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GPI||us||False	f	t	t
Greif Inc. Cl A	\N	USD	1	\N	f	81621	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GEF||us||False	f	t	t
EXCO Resources Inc.	\N	USD	1	\N	f	81622	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#XCO||us||False	f	t	t
Bill Barrett Corp.	\N	USD	1	\N	f	81623	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BBG||us||False	f	t	t
Buckle Inc.	\N	USD	1	\N	f	81624	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BKE||us||False	f	t	t
NeoPhotonics Corp.	\N	USD	1	\N	f	81626	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NPTN||us||False	f	t	t
Excel Maritime Carriers Ltd.	\N	USD	1	\N	f	81634	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EXM||us||False	f	t	t
Tower International Inc.	\N	USD	1	\N	f	81637	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TOWR||us||False	f	t	t
Zale Corp.	\N	USD	1	\N	f	81638	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ZLC||us||False	f	t	t
Standard Register Co.	\N	USD	1	\N	f	81639	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SR||us||False	f	t	t
Neenah Paper Inc.	\N	USD	1	\N	f	81647	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NP||us||False	f	t	t
Mistras Group Inc.	\N	USD	1	\N	f	81648	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MG||us||False	f	t	t
Noranda Aluminum Holding Corp.	\N	USD	1	\N	f	81649	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NOR||us||False	f	t	t
Penn Virginia Corp.	\N	USD	1	\N	f	81650	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PVA||us||False	f	t	t
Simcere Pharmaceutical Group	\N	USD	1	\N	f	81651	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SCR||us||False	f	t	t
United Microelectronics Corp.	\N	USD	1	\N	f	75945	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UMC||us||False	f	t	t
MeadWestvaco Corp.	\N	USD	1	\N	f	75948	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MWV||us||False	f	t	t
Rock-Tenn Co. Cl A	\N	USD	1	\N	f	75950	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RKT||us||False	f	t	t
Dr. Reddy's Laboratories Ltd.	\N	USD	1	\N	f	75953	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RDY||us||False	f	t	t
OFI PRIV EQU CAP	FR0011077270	EUR	1	|EURONEXT|	f	75978	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011077270||fr||False	f	t	t
Call IBEX 35 | 9750 € | 17/02/12 | B9705	FR0011083849	EUR	5	|SGW|	f	75981	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9705||fr||False	f	t	t
Call IBEX 35 | 7250 € | 20/01/12 | C1095	FR0011124007	EUR	5	|SGW|	f	75983	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1095||fr||False	f	t	t
Call IBEX 35 | 10250 € | 17/02/12 | B9706	FR0011083856	EUR	5	|SGW|	f	75984	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9706||fr||False	f	t	t
BOLLORE	FR0000039299	EUR	1	|EURONEXT|	f	75986	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000039299||fr||False	f	t	t
CRCAM LANGUED CCI	FR0010461053	EUR	1	|EURONEXT|	f	75987	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010461053||fr||False	f	t	t
CRCAM TOURAINE CCI	FR0000045304	EUR	1	|EURONEXT|	f	75989	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000045304||fr||False	f	t	t
JCDECAUX NV	FR0010987289	EUR	1	|EURONEXT|	f	76009	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010987289||fr||False	f	t	t
Put IBEX 35 | 8250 € | 17/02/12 | B9950	FR0011091396	EUR	5	|SGW|	f	76017	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9950||fr||False	f	t	t
ELIA	BE0003822393	EUR	1	|EURONEXT|	f	75980	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003822393||be||False	f	t	t
TIGENIX (SUBS) C1	BE0970125283	EUR	1	|EURONEXT|	f	76020	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0970125283||be||False	f	t	t
PUNCH I STVVPR (D)	BE0005635090	EUR	1	|EURONEXT|	f	76836	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005635090||be||False	f	t	t
UMS United Medical Systems International AG	DE0005493654	EUR	1	|DEUTSCHEBOERSE|	f	76010	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005493654||de||False	f	t	t
United Internet AG	DE0005089031	EUR	1	|DEUTSCHEBOERSE|	f	76018	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005089031||de||False	f	t	t
A.M. Castle & Co.	\N	USD	1	\N	f	81652	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CAS||us||False	f	t	t
\N	\N	\N	\N	\N	f	76012	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0125629008||None||False	f	t	t
CSS Industries Inc.	\N	USD	1	\N	f	81653	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CSS||us||False	f	t	t
Western Digital Corp.	\N	USD	1	\N	f	75432	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WDC||us||False	f	t	t
Nordstrom Inc.	\N	USD	1	\N	f	75442	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JWN||us||False	f	t	t
National Semiconductor Corp.	\N	USD	1	\N	f	75445	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NSM||us||False	f	t	t
Companhia Paranaense de Energia-COPEL	\N	USD	1	\N	f	75451	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ELP||us||False	f	t	t
International Coal Group Inc.	\N	USD	1	\N	f	75453	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ICO||us||False	f	t	t
EQT Corp.	\N	USD	1	\N	f	75463	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EQT||us||False	f	t	t
Southern Union Co.	\N	USD	1	\N	f	75466	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SUG||us||False	f	t	t
CorpBanca S.A.	\N	USD	1	\N	f	75470	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BCA||us||False	f	t	t
Delek US Holdings Inc.	\N	USD	1	\N	f	81654	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DK||us||False	f	t	t
China Digital TV Holding Co. Ltd.	\N	USD	1	\N	f	81655	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STV||us||False	f	t	t
Natural Gas Services Group Inc.	\N	USD	1	\N	f	81656	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NGS||us||False	f	t	t
Frontier Communications Corp.	\N	USD	1	\N	f	75493	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FTR||us||False	f	t	t
Varian Medical Systems Inc.	\N	USD	1	\N	f	75494	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VAR||us||False	f	t	t
Empresa Nacional de Electricidad S.A.	\N	USD	1	\N	f	75508	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EOC||us||False	f	t	t
Brookdale Senior Living Inc.	\N	USD	1	\N	f	75521	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BKD||us||False	f	t	t
Hanover Insurance Group Inc.	\N	USD	1	\N	f	75522	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#THG||us||False	f	t	t
AGL Resources Inc.		USD	1	|SP500|	f	75559					100	c	0	2	GAS	{1}	{3}	NYSE#GAS||us||False	f	t	t
L-3 Communications Holdings Inc.	\N	USD	1	\N	f	75549	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LLL||us||False	f	t	t
Safeway Inc.	\N	USD	1	\N	f	75550	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SWY||us||False	f	t	t
Express Inc.	\N	USD	1	\N	f	75551	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EXPR||us||False	f	t	t
Digital Realty Trust Inc.	\N	USD	1	\N	f	75553	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DLR||us||False	f	t	t
KeyCorp	\N	USD	1	\N	f	75557	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KEY||us||False	f	t	t
STMicroelectronics N.V.	\N	USD	1	\N	f	75560	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STM||us||False	f	t	t
Vail Resorts Inc.	\N	USD	1	\N	f	75566	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MTN||us||False	f	t	t
Dillard's Inc.	\N	USD	1	\N	f	75568	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DDS||us||False	f	t	t
CoreLogic Inc.	\N	USD	1	\N	f	75569	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CLGX||us||False	f	t	t
Forest Oil Corp.	\N	USD	1	\N	f	75571	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FST||us||False	f	t	t
Companhia Siderurgica Nacional	\N	USD	1	\N	f	75573	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SID||us||False	f	t	t
Church & Dwight Co.	\N	USD	1	\N	f	75576	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CHD||us||False	f	t	t
Net App, Inc.	\N	USD	1	|NASDAQ100|	f	75979	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NTAP||us||False	f	t	t
Qiagen NV	\N	USD	1	|NASDAQ100|	f	75988	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	QGEN||us||False	f	t	t
Flextronics International Ltd.	SG9999000020	USD	1	|NASDAQ100|	f	76019	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	FLEX||us||False	f	t	t
HITT	NL0000358158	EUR	1	|EURONEXT|	f	76048	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000358158||nl||False	f	t	t
Call IBEX 35 | 9250 € | 18/05/12 | C1119	FR0011124247	EUR	5	|SGW|	f	76022	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1119||fr||False	f	t	t
COFIGEO	FR0011037589	EUR	1	|EURONEXT|	f	76025	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011037589||fr||False	f	t	t
Call IBEX 35 | 10750 € | 18/05/12 | C2138	FR0011145465	EUR	5	|SGW|	f	76031	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C2138||fr||False	f	t	t
Put IBEX 35 | 7750 € | 17/02/12 | B9949	FR0011091388	EUR	5	|SGW|	f	76037	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9949||fr||False	f	t	t
Put IBEX 35 | 9000 € | 18/11/11 | B9551	FR0011080803	EUR	5	|SGW|	f	76039	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9551||fr||False	f	t	t
Put IBEX 35 | 9500 € | 18/11/11 | B7224	FR0011039742	EUR	5	|SGW|	f	76040	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7224||fr||False	f	t	t
Call IBEX 35 | 12000 € | 18/11/11 | B7223	FR0011039734	EUR	5	|SGW|	f	76041	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7223||fr||False	f	t	t
AUBAY	FR0000063737	EUR	1	|EURONEXT|	f	76045	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000063737||fr||False	f	t	t
Call IBEX 35 | 9500 € | 18/11/11 | B7218	FR0011039684	EUR	5	|SGW|	f	76063	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7218||fr||False	f	t	t
Put IBEX 35 | 7250 € | 17/02/12 | C3283	FR0011168236	EUR	5	|SGW|	f	76066	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3283||fr||False	f	t	t
Put IBEX 35 | 8500 € | 18/11/11 | B9938	FR0011091271	EUR	5	|SGW|	f	76071	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9938||fr||False	f	t	t
Transalta Corp.	\N	USD	1	\N	f	75584	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TAC||us||False	f	t	t
LSI Corp.	\N	USD	1	\N	f	75585	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LSI||us||False	f	t	t
Reliance Steel & Aluminum Co.	\N	USD	1	\N	f	75591	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RS||us||False	f	t	t
Constellation Brands Inc. Cl A	\N	USD	1	\N	f	75592	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STZ||us||False	f	t	t
China Security & Surveillance Technology Inc.	\N	USD	1	\N	f	75593	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CSR||us||False	f	t	t
Markel Corp.	\N	USD	1	\N	f	75603	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MKL||us||False	f	t	t
AerCap Holdings N.V.	\N	USD	1	\N	f	75604	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AER||us||False	f	t	t
Family Dollar Stores Inc.	\N	USD	1	\N	f	75627	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FDO||us||False	f	t	t
Amdocs Ltd.	\N	USD	1	\N	f	76296	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DOX||us||False	f	t	t
Stillwater Mining Co.	\N	USD	1	\N	f	75665	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SWC||us||False	f	t	t
Hecla Mining Co.	\N	USD	1	\N	f	75666	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HL||us||False	f	t	t
Buckeye Technologies Inc.	\N	USD	1	\N	f	75668	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BKI||us||False	f	t	t
\N	\N	\N	\N	\N	f	76910	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0115711014||None||False	f	t	t
Deluxe Corp.	\N	USD	1	\N	f	75670	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DLX||us||False	f	t	t
LinkedIn Corp. Cl A	\N	USD	1	\N	f	75671	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LNKD||us||False	f	t	t
Intrepid Potash Inc.	\N	USD	1	\N	f	75672	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IPI||us||False	f	t	t
Tupperware Brands Corp.	\N	USD	1	\N	f	75679	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TUP||us||False	f	t	t
Harris Corp.	\N	USD	1	\N	f	76333	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HRS||us||False	f	t	t
Dish Network Corporation	US25470M1099	USD	1	|NASDAQ100|	f	75734	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	DISH||us||False	f	t	t
eBay, Inc	US2786421030	USD	1	|NASDAQ100|	f	75736	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	EBAY||us||False	f	t	t
Retail Ventures Inc.	\N	USD	1	\N	f	75685	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RVI||us||False	f	t	t
RenaissanceRe Holdings Ltd.	\N	USD	1	\N	f	75691	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RNR||us||False	f	t	t
Wilmington Trust Corp.	\N	USD	1	\N	f	75701	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WL||us||False	f	t	t
L-1 Identity Solutions Inc.	\N	USD	1	\N	f	75706	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ID||us||False	f	t	t
Marshall & Ilsley Corp.	\N	USD	1	\N	f	75707	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MI||us||False	f	t	t
Gartner Inc.	\N	USD	1	\N	f	75719	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IT||us||False	f	t	t
Lennar Corp. Cl A	\N	USD	1	\N	f	75721	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LEN||us||False	f	t	t
Westar Energy Inc.	\N	USD	1	\N	f	75723	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WR||us||False	f	t	t
Renault	FR0000131906	EUR	1	|CAC|	f	76029					100	c	0	3	RNO.PA	{1}	{3}	RNO.PA||fr||False	f	t	t
Nationwide Health Properties Inc.	\N	USD	1	\N	f	75735	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NHP||us||False	f	t	t
Intuitive Surgical Inc.	US46120E6023	USD	1	|NASDAQ100|	f	75747	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	ISRG||us||False	f	t	t
News Corporation	\N	USD	1	|NASDAQ100|	f	75766	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NWSA||us||False	f	t	t
\N	\N	\N	\N	\N	f	76074	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0102562008||None||False	f	t	t
Call IBEX 35 | 7000 € | 16/12/11 | B9939	FR0011091289	EUR	5	|SGW|	f	76073	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9939||fr||False	f	t	t
Put IBEX 35 | 9500 € | 15/06/12 | B9971	FR0011091602	EUR	5	|SGW|	f	76078	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9971||fr||False	f	t	t
TERREIS NV	FR0010989871	EUR	1	|EURONEXT|	f	76079	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010989871||fr||False	f	t	t
Call IBEX 35 | 10500 € | 21/09/12 | C3293	FR0011168335	EUR	5	|SGW|	f	76080	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3293||fr||False	f	t	t
Put IBEX 35 | 10000 € | 18/11/11 | B7225	FR0011039759	EUR	5	|SGW|	f	76084	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7225||fr||False	f	t	t
Put IBEX 35 | 10500 € | 18/11/11 | B7226	FR0011039767	EUR	5	|SGW|	f	76085	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7226||fr||False	f	t	t
Call IBEX 35 | 10750 € | 17/02/12 | B9707	FR0011083864	EUR	5	|SGW|	f	76086	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9707||fr||False	f	t	t
Put IBEX 35 | 11000 € | 18/11/11 | B7227	FR0011039775	EUR	5	|SGW|	f	76090	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7227||fr||False	f	t	t
SCHAEFFER DUFOUR	FR0011067552	EUR	1	|EURONEXT|	f	76092	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011067552||fr||False	f	t	t
EURAZEO DA ANF	FR0011044387	EUR	1	|EURONEXT|	f	76100	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011044387||fr||False	f	t	t
Call IBEX 35 | 15000 € | 19/12/14 | B7871	FR0011065747	EUR	5	|SGW|	f	76114	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7871||fr||False	f	t	t
FMC Technologies Inc.	\N	USD	1	\N	f	75751	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FTI||us||False	f	t	t
Progressive Corp.	\N	USD	1	\N	f	75752	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PGR||us||False	f	t	t
Stanley Black & Decker Inc.	\N	USD	1	\N	f	75755	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SWK||us||False	f	t	t
Tim Hortons Inc.	\N	USD	1	\N	f	75757	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#THI||us||False	f	t	t
Solera Holdings Inc.	\N	USD	1	\N	f	75763	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SLH||us||False	f	t	t
VimpelCom Ltd.	\N	USD	1	\N	f	75764	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VIP||us||False	f	t	t
Advantest Corp.	\N	USD	1	\N	f	75769	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ATE||us||False	f	t	t
Avista Corp.	\N	USD	1	\N	f	75770	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AVA||us||False	f	t	t
\N	\N	\N	\N	\N	f	76109	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0147026001||None||False	f	t	t
El Paso Electric Co.	\N	USD	1	\N	f	75773	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EE||us||False	f	t	t
Dresser-Rand Group Inc.	\N	USD	1	\N	f	76461	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DRC||us||False	f	t	t
Halliburton Co.	\N	USD	1	\N	f	75783	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HAL||us||False	f	t	t
PNC Financial Services Group Inc.	\N	USD	1	\N	f	75794	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PNC||us||False	f	t	t
Dominion Resources Inc. (Virginia)	\N	USD	1	\N	f	75795	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#D||us||False	f	t	t
Prudential Financial Inc.	\N	USD	1	\N	f	75805	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PRU||us||False	f	t	t
Health Net Inc.	\N	USD	1	\N	f	75808	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HNT||us||False	f	t	t
Lazard Ltd.	\N	USD	1	\N	f	75813	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LAZ||us||False	f	t	t
World Fuel Services Corp.	\N	USD	1	\N	f	75821	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#INT||us||False	f	t	t
Black Hills Corp.	\N	USD	1	\N	f	75822	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BKH||us||False	f	t	t
McMoRan Exploration Co.	\N	USD	1	\N	f	75823	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MMR||us||False	f	t	t
Sotheby's	\N	USD	1	\N	f	76540	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BID||us||False	f	t	t
First Solar, Inc.	US3364331070	USD	1	|NASDAQ100|	f	75843	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	FSLR||us||False	f	t	t
Vulcan Materials Co.	\N	USD	1	\N	f	75831	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VMC||us||False	f	t	t
Continental Resources Inc.	\N	USD	1	\N	f	75833	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CLR||us||False	f	t	t
Banco de Chile	\N	USD	1	\N	f	75834	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BCH||us||False	f	t	t
CNA Surety Corp.	\N	USD	1	\N	f	75837	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SUR||us||False	f	t	t
PRIMEDIA Inc.	\N	USD	1	\N	f	75841	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PRM||us||False	f	t	t
Pepco Holdings Inc.	\N	USD	1	\N	f	75842	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#POM||us||False	f	t	t
Cabela's Inc.	\N	USD	1	\N	f	75850	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CAB||us||False	f	t	t
Polypore International Inc.	\N	USD	1	\N	f	76582	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PPO||us||False	f	t	t
Allied Irish Banks PLC	\N	USD	1	\N	f	75894	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AIB||us||False	f	t	t
Jackson Hewitt Tax Service Inc.	\N	USD	1	\N	f	75905	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JTX||us||False	f	t	t
Eastman Kodak Co.	\N	USD	1	\N	f	75912	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EK||us||False	f	t	t
Concho Resources Inc.	\N	USD	1	\N	f	75921	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CXO||us||False	f	t	t
Harley-Davidson Inc.	\N	USD	1	\N	f	75923	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HOG||us||False	f	t	t
Chemspec International Ltd.	\N	USD	1	\N	f	75926	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CPC||us||False	f	t	t
Penn West Petroleum Ltd.	\N	USD	1	\N	f	75932	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PWE||us||False	f	t	t
Hershey Co.	\N	USD	1	\N	f	75934	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HSY||us||False	f	t	t
FREY	FR0010588079	EUR	1	|EURONEXT|	f	76116	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010588079||fr||False	f	t	t
GFI INFORMATIQUE	FR0004038099	EUR	1	|EURONEXT|	f	76120	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004038099||fr||False	f	t	t
Put IBEX 35 | 8500 € | 21/09/12 | C3299	FR0011168392	EUR	5	|SGW|	f	76121	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3299||fr||False	f	t	t
CarMax Inc.		USD	1	|SP500|	f	75758					100	c	0	2	KMX	{1}	{3}	NYSE#KMX||us||False	f	t	t
HAULOTTE GROUP	FR0000066755	EUR	1	|EURONEXT|	f	76140	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000066755||fr||False	f	t	t
Call IBEX 35 | 8500 € | 16/12/11 | B9553	FR0011080829	EUR	5	|SGW|	f	76142	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9553||fr||False	f	t	t
ZODIAC AERO NV	FR0011108935	EUR	1	|EURONEXT|	f	76162	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011108935||fr||False	f	t	t
INNELEC MULTIMEDIA	FR0000064297	EUR	1	|EURONEXT|	f	76165	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064297||fr||False	f	t	t
PAIRI DAIZA STRIP	BE0005564357	EUR	1	|EURONEXT|	f	76125	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005564357||be||False	f	t	t
GIMV	BE0003699130	EUR	1	|EURONEXT|	f	76164	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003699130||be||False	f	t	t
DELTA LLOYD	NL0009294552	EUR	1	|EURONEXT|	f	76117	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009294552||nl||False	f	t	t
ACCELL GROUP	NL0000350106	EUR	1	|EURONEXT|	f	76126	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000350106||nl||False	f	t	t
\N	\N	\N	\N	\N	f	76157	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0147196002||None||False	f	t	t
Westag + Getalit AG Vz	DE0007775231	EUR	1	|DEUTSCHEBOERSE|	f	76163	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007775231||de||False	f	t	t
Corn Products International Inc.	\N	USD	1	\N	f	75961	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CPO||us||False	f	t	t
CGG Veritas	\N	USD	1	\N	f	75962	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CGV||us||False	f	t	t
Warner Music Group Corp.	\N	USD	1	\N	f	75963	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WMG||us||False	f	t	t
Canadian Imperial Bank of Commerce	\N	USD	1	\N	f	75965	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CM||us||False	f	t	t
Statoil ASA	\N	USD	1	\N	f	75967	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STO||us||False	f	t	t
Chubb Corp.	\N	USD	1	\N	f	75974	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CB||us||False	f	t	t
Goodrich Corp.	\N	USD	1	\N	f	75976	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GR||us||False	f	t	t
Fresenius Medical Care AG & Co. KGaA	\N	USD	1	\N	f	75982	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FMS||us||False	f	t	t
Lorillard Inc.	\N	USD	1	\N	f	75985	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LO||us||False	f	t	t
Whirlpool Corp.	\N	USD	1	\N	f	75991	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WHR||us||False	f	t	t
AVX Corp.	\N	USD	1	\N	f	76008	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AVX||us||False	f	t	t
Transocean Ltd.	\N	USD	1	\N	f	76011	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RIG||us||False	f	t	t
KB Financial Group Inc.	\N	USD	1	\N	f	76014	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KB||us||False	f	t	t
EnCana Corp.	\N	USD	1	\N	f	76015	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ECA||us||False	f	t	t
Liberty Media Corporation	\N	USD	1	|NASDAQ100|	f	76060	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	LIFE||us||False	f	t	t
Hologic, Inc.	US4364401012	USD	1	|NASDAQ100|	f	76070	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	HOLX||us||False	f	t	t
Talisman Energy Inc.	\N	USD	1	\N	f	76035	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TLM||us||False	f	t	t
China Telecom Corp. Ltd.	\N	USD	1	\N	f	76036	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CHA||us||False	f	t	t
AMB Property Corp.	\N	USD	1	\N	f	76042	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AMB||us||False	f	t	t
Watson Pharmaceuticals Inc.	\N	USD	1	\N	f	76043	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WPI||us||False	f	t	t
Timken Co.	\N	USD	1	\N	f	76044	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TKR||us||False	f	t	t
Pentair Inc.	\N	USD	1	\N	f	76046	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PNR||us||False	f	t	t
Kinder Morgan Inc.	\N	USD	1	\N	f	76047	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KMI||us||False	f	t	t
Energen Corp.	\N	USD	1	\N	f	76058	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EGN||us||False	f	t	t
Knight Capital Group Inc. Cl A	\N	USD	1	\N	f	76062	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KCG||us||False	f	t	t
Electronic Arts, Inc	US2855121099	USD	1	|NASDAQ100|	f	76087	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	ERTS||us||False	f	t	t
QUALCOMM Incorporated	\N	USD	1	|NASDAQ100|	f	76099	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	QCOM||us||False	f	t	t
Mylan, Inc.	\N	USD	1	|NASDAQ100|	f	76118	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	MYL||us||False	f	t	t
Fiserv, Inc.	US3377381088	USD	1	|NASDAQ100|	f	76132	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	FISV||us||False	f	t	t
Call IBEX 35 | 13000 € | 16/12/11 | B5147	FR0011002815	EUR	5	|SGW|	f	76175	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B5147||fr||False	f	t	t
MEMSCAP DS	FR0011176569	EUR	1	|EURONEXT|	f	76178	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011176569||fr||False	f	t	t
INTERPARFUMS	FR0004024222	EUR	1	|EURONEXT|	f	76184	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004024222||fr||False	f	t	t
METABOLIC EXPLORER	FR0004177046	EUR	1	|EURONEXT|	f	76185	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004177046||fr||False	f	t	t
MODELABS GROUP	FR0010060665	EUR	1	|EURONEXT|	f	76186	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010060665||fr||False	f	t	t
Call IBEX 35 | 12500 € | 16/12/11 | B5146	FR0011002807	EUR	5	|SGW|	f	76191	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B5146||fr||False	f	t	t
INSTALLUX	FR0000060451	EUR	1	|EURONEXT|	f	76194	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060451||fr||False	f	t	t
Put IBEX 35 | 7000 € | 16/12/11 | B9941	FR0011091305	EUR	5	|SGW|	f	76196	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9941||fr||False	f	t	t
TERREIS	FR0010407049	EUR	1	|EURONEXT|	f	76202	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010407049||fr||False	f	t	t
Put IBEX 35 | 8500 € | 16/12/11 | B5148	FR0011002823	EUR	5	|SGW|	f	76212	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B5148||fr||False	f	t	t
IPSEN	FR0010259150	EUR	1	|EURONEXT|	f	76214	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010259150||fr||False	f	t	t
TESSENDERLO	BE0003555639	EUR	1	|EURONEXT|	f	76203	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003555639||be||False	f	t	t
KEYWARE TECH. (D)	BE0003880979	EUR	1	|EURONEXT|	f	76213	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003880979||be||False	f	t	t
\N	\N	\N	\N	\N	f	76181	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0113556007||None||False	f	t	t
Süss MicroTec AG	DE0007226706	EUR	1	|DEUTSCHEBOERSE|	f	76192	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007226706||de||False	f	t	t
VeriSign Inc.	\N	USD	1	|NASDAQ100|	f	76105	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	VRSN||us||False	f	t	t
PS Business Parks Inc.	\N	USD	1	\N	f	76098	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PSB||us||False	f	t	t
RLJ Lodging Trust	\N	USD	1	\N	f	76101	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RLJ||us||False	f	t	t
Advanced Semiconductor Engineering Inc.	\N	USD	1	\N	f	76115	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ASX||us||False	f	t	t
Stericycle, Inc.	\N	USD	1	|NASDAQ100|	f	76147	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	SRCL||us||False	f	t	t
Smurfit-Stone Container Corp.	\N	USD	1	\N	f	76119	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SSCC||us||False	f	t	t
Mettler-Toledo International Inc.	\N	USD	1	\N	f	76123	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MTD||us||False	f	t	t
Donaldson Co. Inc.	\N	USD	1	\N	f	76127	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DCI||us||False	f	t	t
Xylem Inc.	\N	USD	1	\N	f	76128	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#XYL||us||False	f	t	t
SM Energy Co.	\N	USD	1	\N	f	76129	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SM||us||False	f	t	t
Alpha Natural Resources Inc.	\N	USD	1	\N	f	76135	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ANR||us||False	f	t	t
Ashland Inc.	\N	USD	1	\N	f	76144	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ASH||us||False	f	t	t
Walter Energy Inc.	\N	USD	1	\N	f	76146	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WLT||us||False	f	t	t
ResMed Inc.	\N	USD	1	\N	f	76148	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RMD||us||False	f	t	t
M&F Worldwide Corp.	\N	USD	1	\N	f	76149	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MFW||us||False	f	t	t
Kirby Corp.	\N	USD	1	\N	f	76150	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KEX||us||False	f	t	t
Coca-Cola Hellenic Bottling Co. S.A.	\N	USD	1	\N	f	76151	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CCH||us||False	f	t	t
Cisco Systems, Inc.	US17275R1023	USD	1	|NASDAQ100|	f	76169	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	CSCO||us||False	f	t	t
Syngenta AG	\N	USD	1	\N	f	76166	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SYT||us||False	f	t	t
Interpublic Group of Cos.	\N	USD	1	\N	f	76170	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IPG||us||False	f	t	t
Enersis S.A.	\N	USD	1	\N	f	76172	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ENI||us||False	f	t	t
Coventry Health Care Inc.	\N	USD	1	\N	f	76174	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CVH||us||False	f	t	t
Owens Corning	\N	USD	1	\N	f	76177	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OC||us||False	f	t	t
Sealed Air Corp.	\N	USD	1	\N	f	76179	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SEE||us||False	f	t	t
NV Energy Inc.	\N	USD	1	\N	f	76182	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NVE||us||False	f	t	t
Arthur J. Gallagher & Co.	\N	USD	1	\N	f	76183	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AJG||us||False	f	t	t
Rockwood Holdings Inc.	\N	USD	1	\N	f	76368	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ROC||us||False	f	t	t
ITT CORP NEW	US4509112011	EUR	1	|EURONEXT|	f	76219	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US4509112011||fr||False	f	t	t
JACQUES BOGART	FR0000032633	EUR	1	|EURONEXT|	f	76220	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000032633||fr||False	f	t	t
KINDY	FR0000052904	EUR	1	|EURONEXT|	f	76224	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000052904||fr||False	f	t	t
GECIMED	FR0000061566	EUR	1	|EURONEXT|	f	76228	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000061566||fr||False	f	t	t
Macerich Co.	\N	USD	1	\N	f	76282	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MAC||us||False	f	t	t
Call IBEX 35 | 9750 € | 21/10/11 | B7207	FR0011039577	EUR	5	|SGW|	f	76229	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7207||fr||False	f	t	t
Put IBEX 35 | 8750 € | 21/10/11 | B9549	FR0011080787	EUR	5	|SGW|	f	76230	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9549||fr||False	f	t	t
Put IBEX 35 | 9000 € | 16/12/11 | B5149	FR0011002831	EUR	5	|SGW|	f	76231	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B5149||fr||False	f	t	t
TURBO Call IBEX 35 | 7750 € | 16/12/11 | 55096	FR0011115674	EUR	5	|SGW|	f	76232	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#55096||fr||False	f	t	t
\N	\N	\N	\N	\N	f	77409	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0158013005||None||False	f	t	t
Put IBEX 35 | 9500 € | 16/12/11 | B5150	FR0011002849	EUR	5	|SGW|	f	76233	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B5150||fr||False	f	t	t
Put IBEX 35 | 10000 € | 16/12/11 | B5151	FR0011002856	EUR	5	|SGW|	f	76234	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B5151||fr||False	f	t	t
PAGESJAUNES	FR0010096354	EUR	1	|EURONEXT|	f	76238	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010096354||fr||False	f	t	t
PASSAT	FR0000038465	EUR	1	|EURONEXT|	f	76240	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000038465||fr||False	f	t	t
SOITEC	FR0004025062	EUR	1	|EURONEXT|	f	76242	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004025062||fr||False	f	t	t
XING AG	DE000XNG8888	EUR	1	|DEUTSCHEBOERSE|	f	76225	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000XNG8888||de||False	f	t	t
FactSet Research Systems Inc.	\N	USD	1	\N	f	76188	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FDS||us||False	f	t	t
Build-A-Bear Workshop Inc.	\N	USD	1	\N	f	76190	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BBW||us||False	f	t	t
Longtop Financial Technologies Ltd.	\N	USD	1	\N	f	76197	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LFT||us||False	f	t	t
TNS Inc.	\N	USD	1	\N	f	77085	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TNS||us||False	f	t	t
PVH Corp.	\N	USD	1	\N	f	76218	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PVH||us||False	f	t	t
TransDigm Group Inc.	\N	USD	1	\N	f	76221	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TDG||us||False	f	t	t
Camden Property Trust	\N	USD	1	\N	f	76222	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CPT||us||False	f	t	t
Quanta Services Inc.	\N	USD	1	\N	f	76223	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PWR||us||False	f	t	t
Sunoco Inc.	\N	USD	1	\N	f	76235	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SUN||us||False	f	t	t
NRG Energy Inc.	\N	USD	1	\N	f	76239	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NRG||us||False	f	t	t
Mednax Inc.	\N	USD	1	\N	f	76241	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MD||us||False	f	t	t
Camelot Information Systems Inc.	\N	USD	1	\N	f	80212	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CIS||us||False	f	t	t
STAG Industrial Inc.	\N	USD	1	\N	f	80213	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STAG||us||False	f	t	t
Arbor Realty Trust Inc.	\N	USD	1	\N	f	80214	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ABR||us||False	f	t	t
Box Ships Inc.	\N	USD	1	\N	f	80216	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TEU||us||False	f	t	t
Baltic Trading Ltd.	\N	USD	1	\N	f	80217	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BALT||us||False	f	t	t
AMR Corp.	\N	USD	1	\N	f	80433	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AMR||us||False	f	t	t
BOURSORAMA	FR0000075228	EUR	1	|EURONEXT|	f	76266	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000075228||fr||False	f	t	t
Put IBEX 35 | 11000 € | 16/12/11 | B5153	FR0011002872	EUR	5	|SGW|	f	76270	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B5153||fr||False	f	t	t
Put IBEX 35 | 9750 € | 21/10/11 | B7214	FR0011039643	EUR	5	|SGW|	f	76271	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7214||fr||False	f	t	t
Put IBEX 35 | 10250 € | 21/10/11 | B7215	FR0011039650	EUR	5	|SGW|	f	76272	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7215||fr||False	f	t	t
Call IBEX 35 | 7000 € | 18/11/11 | B9997	FR0011101781	EUR	5	|SGW|	f	76274	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9997||fr||False	f	t	t
DIAGNOSTIC MEDICAL	FR0000063224	EUR	1	|EURONEXT|	f	76276	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000063224||fr||False	f	t	t
Put IBEX 35 | 9250 € | 21/10/11 | B7213	FR0011039635	EUR	5	|SGW|	f	76279	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7213||fr||False	f	t	t
CRYO SAVE GROUP	NL0009272137	EUR	1	|EURONEXT|	f	76269	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009272137||nl||False	f	t	t
RBS CAP FUND TRVII	US74928P2074	EUR	1	|EURONEXT|	f	76277	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#US74928P2074||nl||False	f	t	t
Expeditors International of Washington Inc. 	US3021301094	USD	1	|NASDAQ100|	f	76275	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	EXPD||us||False	f	t	t
Temple-Inland Inc.	\N	USD	1	\N	f	76244	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TIN||us||False	f	t	t
Cooper Cos.	\N	USD	1	\N	f	76245	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#COO||us||False	f	t	t
Cullen/Frost Bankers Inc.	\N	USD	1	\N	f	76262	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CFR||us||False	f	t	t
BUREAU VERITAS NV	FR0010979450	EUR	1	|EURONEXT|	f	76315	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010979450||fr||False	f	t	t
FINANCIERE ODET	FR0000062234	EUR	1	|EURONEXT|	f	76326	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000062234||fr||False	f	t	t
IPSOS	FR0000073298	EUR	1	|EURONEXT|	f	76327	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000073298||fr||False	f	t	t
LACIE S.A.	FR0000054314	EUR	1	|EURONEXT|	f	76331	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000054314||fr||False	f	t	t
UNITED ANODISERS	BE0160342011	EUR	1	|EURONEXT|	f	76336	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#BE0160342011||fr||False	f	t	t
Call IBEX 35 inLine | 7500 € | 14/12/11 | I0036	FR0011081330	EUR	5	|SGW|	f	76340	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0036||fr||False	f	t	t
Call IBEX 35 inLine | 7500 € | 14/12/11 | I0037	FR0011081355	EUR	5	|SGW|	f	76341	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0037||fr||False	f	t	t
Call IBEX 35 inLine | 7000 € | 14/03/12 | I0049	FR0011117902	EUR	5	|SGW|	f	76344	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0049||fr||False	f	t	t
TETRAGON FIN GRP	GG00B1RMC548	EUR	1	|EURONEXT|	f	76283	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GG00B1RMC548||nl||False	f	t	t
CROWN VAN GELDER	NL0000345452	EUR	1	|EURONEXT|	f	76325	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000345452||nl||False	f	t	t
\N	\N	\N	\N	\N	f	76307	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0169993005||None||False	f	t	t
B.PAST.D.A11	ES0613770934	EUR	1	|MERCADOCONTINUO|	f	76337	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0613770934||es||False	f	t	t
\N	\N	\N	\N	\N	f	76338	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0110013002||None||False	f	t	t
\N	\N	\N	\N	\N	f	76346	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0165142003||None||False	f	t	t
\N	\N	\N	\N	\N	f	76351	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0175805003||None||False	f	t	t
Expedia, Inc	US30212P1057	USD	1	|NASDAQ100|	f	76281	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	EXPE||us||False	f	t	t
Henry Schein, Inc.	US8064071025	USD	1	|NASDAQ100|	f	76319	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	HSIC||us||False	f	t	t
Logitech International S.A.	\N	USD	1	|NASDAQ100|	f	76329	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	LOGI||us||False	f	t	t
Linear Technology Corporation	\N	USD	1	|NASDAQ100|	f	76339	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	LLTC||us||False	f	t	t
Teva Pharmaceutical Industries Limited	\N	USD	1	|NASDAQ100|	f	76343	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	TEVA||us||False	f	t	t
NYSE Euronext	\N	USD	1	\N	f	76285	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NYX||us||False	f	t	t
Cemex S.A.B. de C.V.	\N	USD	1	\N	f	76286	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CX||us||False	f	t	t
Constellation Energy Group Inc.	\N	USD	1	\N	f	76290	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CEG||us||False	f	t	t
Korea Electric Power Corp.	\N	USD	1	\N	f	76292	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KEP||us||False	f	t	t
Plum Creek Timber Co. Inc. REIT	\N	USD	1	\N	f	76293	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PCL||us||False	f	t	t
Southern Copper Corp.	\N	USD	1	\N	f	76294	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SCCO||us||False	f	t	t
American Water Works Co.	\N	USD	1	\N	f	76295	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AWK||us||False	f	t	t
Hospira Inc.	\N	USD	1	\N	f	76297	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HSP||us||False	f	t	t
Rayonier Inc. REIT	\N	USD	1	\N	f	76303	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RYN||us||False	f	t	t
Comerica Inc.	\N	USD	1	\N	f	76311	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CMA||us||False	f	t	t
Sociedad Quimica y Minera De Chile S.A.	\N	USD	1	\N	f	76312	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SQM||us||False	f	t	t
Iron Mountain Inc.	\N	USD	1	\N	f	76323	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IRM||us||False	f	t	t
OGE Energy Corp.	\N	USD	1	\N	f	76324	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OGE||us||False	f	t	t
AGCO Corp.	\N	USD	1	\N	f	76328	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AGCO||us||False	f	t	t
Yanzhou Coal Mining Co. Ltd.	\N	USD	1	\N	f	76334	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#YZC||us||False	f	t	t
Reddy Ice Holdings Inc.	\N	USD	1	\N	f	76335	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FRZ||us||False	f	t	t
Arrow Electronics Inc.	\N	USD	1	\N	f	76349	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ARW||us||False	f	t	t
International Flavors & Fragrances Inc.	\N	USD	1	\N	f	76350	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IFF||us||False	f	t	t
\N	\N	\N	\N	\N	f	76352	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0165268006||None||False	f	t	t
DPA GROUP	NL0009197771	EUR	1	|EURONEXT|	f	76386	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009197771||nl||False	f	t	t
BULL	FR0010266601	EUR	1	|EURONEXT|	f	76364	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010266601||fr||False	f	t	t
L'OREAL	FR0000120321	EUR	1	|CAC|EURONEXT|EUROSTOXX|	f	76330					100	c	0	3	None	\N	\N	EURONEXT#FR0000120321||fr||False	f	t	t
DOCKS LYONNAIS	FR0000060204	EUR	1	|EURONEXT|	f	76376	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060204||fr||False	f	t	t
LAGARDERE S.C.A.	FR0000130213	EUR	1	|EURONEXT|	f	76395	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000130213||fr||False	f	t	t
MEETIC	FR0011099357	EUR	1	|EURONEXT|	f	76396	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011099357||fr||False	f	t	t
ACANTHE DEV.	FR0000064602	EUR	1	|EURONEXT|	f	76409	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064602||fr||False	f	t	t
DEFICOM GROUP	BE0003624351	EUR	1	|EURONEXT|	f	76369	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003624351||be||False	f	t	t
DEFICOM STRIP	BE0005570412	EUR	1	|EURONEXT|	f	76375	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005570412||be||False	f	t	t
DOW CHEMICAL CERT	BE0004594355	EUR	1	|EURONEXT|	f	76385	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0004594355||be||False	f	t	t
GALAPAGOS	BE0003818359	EUR	1	|EURONEXT|	f	76387	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003818359||be||False	f	t	t
ACCENTIS	BE0003696102	EUR	1	|EURONEXT|	f	76410	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003696102||be||False	f	t	t
Nabors Industries Ltd.	\N	USD	1	\N	f	76360	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NBR||us||False	f	t	t
Oceaneering International Inc.	\N	USD	1	\N	f	76361	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OII||us||False	f	t	t
Waste Connections Inc.	\N	USD	1	\N	f	76363	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WCN||us||False	f	t	t
Legg Mason Inc.	\N	USD	1	\N	f	76367	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LM||us||False	f	t	t
NVR Inc.	\N	USD	1	\N	f	76379	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NVR||us||False	f	t	t
China Education Alliance Inc.	\N	USD	1	\N	f	76382	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CEU||us||False	f	t	t
URS Corp.	\N	USD	1	\N	f	76389	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#URS||us||False	f	t	t
Arch Coal Inc.	\N	USD	1	\N	f	76390	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ACI||us||False	f	t	t
Eaton Vance Corp.	\N	USD	1	\N	f	76391	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EV||us||False	f	t	t
SandRidge Energy Inc.	\N	USD	1	\N	f	76392	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SD||us||False	f	t	t
Home Depot Inc.	\N	USD	1	\N	f	76399	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HD||us||False	f	t	t
IHS Inc. Cl A	\N	USD	1	\N	f	76406	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IHS||us||False	f	t	t
Robert Half International Inc.	\N	USD	1	\N	f	76407	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RHI||us||False	f	t	t
Axis Capital Holdings Ltd.	\N	USD	1	\N	f	76408	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AXS||us||False	f	t	t
Jabil Circuit Inc.	\N	USD	1	\N	f	76411	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JBL||us||False	f	t	t
ACTIA GROUP	FR0000076655	EUR	1	|EURONEXT|	f	76412	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000076655||fr||False	f	t	t
ALTAREA	FR0000033219	EUR	1	|EURONEXT|	f	76420	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000033219||fr||False	f	t	t
ANOVO	FR0010698217	EUR	1	|EURONEXT|	f	76435	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010698217||fr||False	f	t	t
TURBO Call IBEX 35 | 9500 € | 17/06/11 | 54832	FR0011003169	EUR	5	|SGW|	f	76439	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54832||fr||False	f	t	t
INFO VISTA	FR0004031649	EUR	1	|EURONEXT|	f	76467	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004031649||fr||False	f	t	t
INGENICO	FR0000125346	EUR	1	|EURONEXT|	f	76472	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000125346||fr||False	f	t	t
AGEAS STRIP VVPR	BE0005591624	EUR	1	|EURONEXT|	f	76413	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005591624||be||False	f	t	t
AGFA STRIP VVPR(D)	BE0005638128	EUR	1	|EURONEXT|	f	76416	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005638128||be||False	f	t	t
4ENERGY STR (D)	BE0005625968	EUR	1	|EURONEXT|	f	76459	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005625968||be||False	f	t	t
AARDVARK INVEST	LU0111311071	EUR	1	|EURONEXT|	f	76460	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#LU0111311071||be||False	f	t	t
ARTHUR	FR0004166155	EUR	1	|EURONEXT|	f	76466	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#FR0004166155||be||False	f	t	t
AMSTERDAM COMMOD.	NL0000313286	EUR	1	|EURONEXT|	f	76423	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000313286||nl||False	f	t	t
J.B. Hunt Transport Services, I	\N	USD	1	|NASDAQ100|	f	76437	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	JBHT||us||False	f	t	t
NII Holdings Inc.	US62913F2011	USD	1	|NASDAQ100|	f	76468	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NIHD||us||False	f	t	t
United States Steel Corp.	\N	USD	1	\N	f	76426	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#X||us||False	f	t	t
Rowan Cos. Inc.	\N	USD	1	\N	f	76428	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RDC||us||False	f	t	t
LAN Airlines S.A.	\N	USD	1	\N	f	76431	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LFL||us||False	f	t	t
General Maritime Corp.	\N	USD	1	\N	f	76433	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GMR||us||False	f	t	t
Signet Jewelers Ltd.	\N	USD	1	\N	f	76434	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SIG||us||False	f	t	t
MFA Financial Inc.	\N	USD	1	\N	f	76436	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MFA||us||False	f	t	t
Atwood Oceanics Inc.	\N	USD	1	\N	f	76438	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ATW||us||False	f	t	t
Mindray Medical International Ltd.	\N	USD	1	\N	f	76441	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MR||us||False	f	t	t
Service Corp. International	\N	USD	1	\N	f	76442	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SCI||us||False	f	t	t
Trinity Industries Inc.	\N	USD	1	\N	f	76445	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TRN||us||False	f	t	t
Genesee & Wyoming Inc. Cl A	\N	USD	1	\N	f	76451	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GWR||us||False	f	t	t
Teleflex Inc.	\N	USD	1	\N	f	76452	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TFX||us||False	f	t	t
Sally Beauty Holdings Inc.	\N	USD	1	\N	f	76453	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SBH||us||False	f	t	t
Crane Co.	\N	USD	1	\N	f	76454	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CR||us||False	f	t	t
Everest Re Group Ltd.	\N	USD	1	\N	f	76462	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RE||us||False	f	t	t
MDU Resources Group Inc.	\N	USD	1	\N	f	76464	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MDU||us||False	f	t	t
Mack-Cali Realty Corp.	\N	USD	1	\N	f	76465	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CLI||us||False	f	t	t
Warnaco Group Inc.	\N	USD	1	\N	f	76473	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WRC||us||False	f	t	t
Coeur d'Alene Mines Corp.	\N	USD	1	\N	f	76474	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CDE||us||False	f	t	t
Highwoods Properties Inc.	\N	USD	1	\N	f	76475	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HIW||us||False	f	t	t
IRDNORDPASDECALAIS	FR0000124232	EUR	1	|EURONEXT|	f	76478	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000124232||fr||False	f	t	t
KLEMURS	FR0010404780	EUR	1	|EURONEXT|	f	76479	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010404780||fr||False	f	t	t
LACROIX SA	FR0000066607	EUR	1	|EURONEXT|	f	76481	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000066607||fr||False	f	t	t
ATMEL CORP.	US0495131049	EUR	1	|EURONEXT|	f	76498	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US0495131049||fr||False	f	t	t
Call IBEX 35 | 10500 € | 18/11/11 | B7220	FR0011039700	EUR	5	|SGW|	f	76501	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7220||fr||False	f	t	t
Put IBEX 35 | 8000 € | 18/11/11 | B9937	FR0011091263	EUR	5	|SGW|	f	76502	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9937||fr||False	f	t	t
Call IBEX 35 | 10000 € | 18/11/11 | B7219	FR0011039692	EUR	5	|SGW|	f	76503	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7219||fr||False	f	t	t
AUGROS COSMETICS	FR0000061780	EUR	1	|EURONEXT|	f	76511	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000061780||fr||False	f	t	t
FIDUCIAL REAL EST.	FR0000060535	EUR	1	|EURONEXT|	f	76513	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060535||fr||False	f	t	t
BLEECKER	FR0000062150	EUR	1	|EURONEXT|	f	76547	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000062150||fr||False	f	t	t
PFIZER CERT	BE0004536745	EUR	1	|EURONEXT|	f	76526	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0004536745||be||False	f	t	t
BEVER HOLDING	NL0000285278	EUR	1	|EURONEXT|	f	76512	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000285278||nl||False	f	t	t
Fastenal Company	US3119001044	USD	1	|NASDAQ100|	f	76499	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	FAST||us||False	f	t	t
AECOM Technology Corp.	\N	USD	1	\N	f	76480	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ACM||us||False	f	t	t
Oasis Petroleum Inc.	\N	USD	1	\N	f	76484	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OAS||us||False	f	t	t
Waddell & Reed Financial Inc.	\N	USD	1	\N	f	76495	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WDR||us||False	f	t	t
Kodiak Oil & Gas Corp.	\N	USD	1	\N	f	76496	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KOG||us||False	f	t	t
Ford Motor Co.	\N	USD	1	\N	f	76497	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#F||us||False	f	t	t
Fidelity National Financial Inc.	\N	USD	1	\N	f	76504	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FNF||us||False	f	t	t
Dick's Sporting Goods Inc.	\N	USD	1	\N	f	76516	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DKS||us||False	f	t	t
National Bank of Greece S.A.	\N	USD	1	\N	f	76518	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NBG||us||False	f	t	t
Solutia Inc.	\N	USD	1	\N	f	76519	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SOA||us||False	f	t	t
Huntsman Corp.	\N	USD	1	\N	f	76520	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HUN||us||False	f	t	t
CBL & Associates Properties Inc.	\N	USD	1	\N	f	76521	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CBL||us||False	f	t	t
Triumph Group Inc.	\N	USD	1	\N	f	76523	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TGI||us||False	f	t	t
Valmont Industries Inc.	\N	USD	1	\N	f	76530	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VMI||us||False	f	t	t
LaSalle Hotel Properties	\N	USD	1	\N	f	76539	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LHO||us||False	f	t	t
Owens-Illinois Inc.	\N	USD	1	\N	f	76542	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OI||us||False	f	t	t
Genworth Financial Inc. Cl A	\N	USD	1	\N	f	76545	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GNW||us||False	f	t	t
Raymond James Financial Inc.	\N	USD	1	\N	f	76548	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RJF||us||False	f	t	t
CATERPILLAR INC	US1491231015	EUR	1	|EURONEXT|	f	76553	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US1491231015||fr||False	f	t	t
BOUYGUES	FR0011121888	EUR	1	|EURONEXT|	f	76559	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011121888||fr||False	f	t	t
INTERCALL REDUCT.	FR0000044901	EUR	1	|EURONEXT|	f	76560	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000044901||fr||False	f	t	t
CCA INTERNATIONAL	FR0000078339	EUR	1	|EURONEXT|	f	76561	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000078339||fr||False	f	t	t
CEGEREAL	FR0010309096	EUR	1	|EURONEXT|	f	76563	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010309096||fr||False	f	t	t
\N	\N	\N	\N	\N	f	76556	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0163612007||None||False	f	t	t
CESAR BSAR	FR0010876813	EUR	1	|EURONEXT|	f	76564	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010876813||fr||False	f	t	t
HI-MEDIA	FR0000075988	EUR	1	|EURONEXT|	f	76588	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000075988||fr||False	f	t	t
DELTAPLU BSAR1211	FR0010202655	EUR	1	|EURONEXT|	f	76590	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010202655||fr||False	f	t	t
Call IBEX 35 | 9500 € | 16/12/11 | B5140	FR0011002740	EUR	5	|SGW|	f	76591	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B5140||fr||False	f	t	t
Call IBEX 35 | 10000 € | 16/12/11 | B5141	FR0011002757	EUR	5	|SGW|	f	76592	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B5141||fr||False	f	t	t
REALDO STR 1/100TP	BE0005552238	EUR	1	|EURONEXT|	f	76572	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005552238||be||False	f	t	t
BOUSSARD GAVAUD C	GG00B1XFMJ13	EUR	1	|EURONEXT|	f	76550	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GG00B1XFMJ13||nl||False	f	t	t
\N	\N	\N	\N	\N	f	76577	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0147102018||None||False	f	t	t
Infosys Technologies Limited	US4567881085	USD	1	|NASDAQ100|	f	76571	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	INFY||us||False	f	t	t
Gannett Co. Inc.	\N	USD	1	\N	f	76554	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GCI||us||False	f	t	t
Aptargroup Inc.	\N	USD	1	\N	f	76555	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ATR||us||False	f	t	t
American Financial Group Inc.	\N	USD	1	\N	f	76566	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AFG||us||False	f	t	t
Oshkosh Corp.	\N	USD	1	\N	f	76567	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OSK||us||False	f	t	t
Carters Inc.	\N	USD	1	\N	f	76568	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CRI||us||False	f	t	t
Huaneng Power International Inc.	\N	USD	1	\N	f	76569	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HNP||us||False	f	t	t
Ruddick Corp.	\N	USD	1	\N	f	76573	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RDK||us||False	f	t	t
Schweitzer-Mauduit International Inc.	\N	USD	1	\N	f	76583	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SWM||us||False	f	t	t
CYS Investments Inc.	\N	USD	1	\N	f	76584	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CYS||us||False	f	t	t
AbitibiBowater Inc.	\N	USD	1	\N	f	76585	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ABH||us||False	f	t	t
Waste Management Inc.	\N	USD	1	\N	f	76586	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WM||us||False	f	t	t
Loews Corp.	\N	USD	1	\N	f	76587	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#L||us||False	f	t	t
Yamana Gold Inc.	\N	USD	1	\N	f	76589	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AUY||us||False	f	t	t
HIGH CO	FR0000054231	EUR	1	|EURONEXT|	f	76595	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000054231||fr||False	f	t	t
KLEPIERRE	FR0000121964	EUR	1	|EURONEXT|	f	76597	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000121964||fr||False	f	t	t
LAURENT-PERRIER	FR0006864484	EUR	1	|EURONEXT|	f	76599	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0006864484||fr||False	f	t	t
RALLYE	FR0000060618	EUR	1	|EURONEXT|	f	76600	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060618||fr||False	f	t	t
S.E.B.	FR0000121709	EUR	1	|EURONEXT|	f	76604	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000121709||fr||False	f	t	t
ACCOR NV	FR0010979682	EUR	1	|EURONEXT|	f	76606	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010979682||fr||False	f	t	t
RHODIA	FR0011056027	EUR	1	|EURONEXT|	f	76607	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011056027||fr||False	f	t	t
Put IBEX 35 | 9500 € | 16/09/11 | B4749	FR0010984674	EUR	5	|SGW|	f	76608	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4749||fr||False	f	t	t
SAFRAN	FR0000073272	EUR	1	|EURONEXT|	f	76610	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000073272||fr||False	f	t	t
ROULARTA STRIP	BE0005546172	EUR	1	|EURONEXT|	f	76602	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005546172||be||False	f	t	t
Maxim Integrated Products Inc.	\N	USD	1	|NASDAQ100|	f	76593	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	MXIM||us||False	f	t	t
Oracle Corporation	\N	USD	1	|NASDAQ100|	f	76617	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	ORCL||us||False	f	t	t
PACCAR Inc.	\N	USD	1	|NASDAQ100|	f	76622	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	PCAR||us||False	f	t	t
Gold Fields Ltd.	\N	USD	1	\N	f	76594	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GFI||us||False	f	t	t
Western Union Co.	\N	USD	1	\N	f	76598	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WU||us||False	f	t	t
Quest Diagnostics Inc.	\N	USD	1	\N	f	76601	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DGX||us||False	f	t	t
Terra Nova Royalty Corp.	\N	USD	1	\N	f	76616	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TTT||us||False	f	t	t
Kansas City Southern	\N	USD	1	\N	f	76618	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KSU||us||False	f	t	t
Validus Holdings Ltd.	\N	USD	1	\N	f	76619	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VR||us||False	f	t	t
AB SCIENCE	FR0010557264	EUR	1	|EURONEXT|	f	76642	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010557264||fr||False	f	t	t
AIR FRANCE -KLM	FR0000031122	EUR	1	|EURONEXT|	f	76649	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000031122||fr||False	f	t	t
Regal-Beloit Corp.	\N	USD	1	\N	f	76624	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RBC||us||False	f	t	t
SEQUANA	FR0000063364	EUR	1	|EURONEXT|	f	76653	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000063364||fr||False	f	t	t
TELEPERFORMANCE	FR0000051807	EUR	1	|EURONEXT|	f	76658	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000051807||fr||False	f	t	t
TF1	FR0000054900	EUR	1	|EURONEXT|	f	76665	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000054900||fr||False	f	t	t
Call IBEX 35 | 10750 € | 19/08/11 | B6049	FR0011017748	EUR	5	|SGW|	f	76671	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B6049||fr||False	f	t	t
Put IBEX 35 | 9750 € | 19/08/11 | B6056	FR0011017813	EUR	5	|SGW|	f	76672	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B6056||fr||False	f	t	t
ABLYNX (D)	BE0003877942	EUR	1	|EURONEXT|	f	76644	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003877942||be||False	f	t	t
AGFA-GEVAERT	BE0003755692	EUR	1	|EURONEXT|	f	76645	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003755692||be||False	f	t	t
AAREAL BKCAP FD TR	XS0138973010	EUR	1	|EURONEXT|	f	76640	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#XS0138973010||nl||False	f	t	t
TEN CATE	NL0000375749	EUR	1	|EURONEXT|	f	76663	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000375749||nl||False	f	t	t
iShares MSCI Brazil Index	\N	USD	4	\N	f	76643	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	EWZ||br||False	f	t	t
WGL Holdings Inc.	\N	USD	1	\N	f	76625	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WGL||us||False	f	t	t
Bank of Hawaii Corp.	\N	USD	1	\N	f	76631	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BOH||us||False	f	t	t
StanCorp Financial Group Inc.	\N	USD	1	\N	f	76633	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SFG||us||False	f	t	t
Hornbeck Offshore Services Inc.	\N	USD	1	\N	f	76634	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HOS||us||False	f	t	t
New York Times Co. Cl A	\N	USD	1	\N	f	76635	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NYT||us||False	f	t	t
Laclede Group Inc.	\N	USD	1	\N	f	76636	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LG||us||False	f	t	t
Orbital Sciences Corp.	\N	USD	1	\N	f	76637	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ORB||us||False	f	t	t
Honda Motor Co. Ltd.	\N	USD	1	\N	f	76638	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HMC||us||False	f	t	t
NTT DOCOMO Inc.	\N	USD	1	\N	f	76639	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DCM||us||False	f	t	t
TJX Cos.	\N	USD	1	\N	f	76646	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TJX||us||False	f	t	t
Precision Castparts Corp.	\N	USD	1	\N	f	76647	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PCP||us||False	f	t	t
CenturyLink Inc.	\N	USD	1	\N	f	76648	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CTL||us||False	f	t	t
Nippon Telegraph & Telephone Corp.	\N	USD	1	\N	f	76652	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NTT||us||False	f	t	t
InterContinental Hotels Group PLC	\N	USD	1	\N	f	76666	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IHG||us||False	f	t	t
UDR Inc.	\N	USD	1	\N	f	76668	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UDR||us||False	f	t	t
Advance Auto Parts Inc.	\N	USD	1	\N	f	76669	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AAP||us||False	f	t	t
Alliance Data Systems Corp.	\N	USD	1	\N	f	76673	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ADS||us||False	f	t	t
Key Energy Services Inc.	\N	USD	1	\N	f	76681	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KEG||us||False	f	t	t
Protective Life Corp.	\N	USD	1	\N	f	76682	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PL||us||False	f	t	t
GenOn Energy Inc.	\N	USD	1	\N	f	76683	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GEN||us||False	f	t	t
K12 Inc.	\N	USD	1	\N	f	76684	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LRN||us||False	f	t	t
INAS (2.7777777P1)	PTINA0APS030	EUR	1	|EURONEXT|	f	76711	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTINA0APS030||pt||False	f	t	t
MUSEE GREVIN	FR0000037970	EUR	1	|EURONEXT|	f	76689	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000037970||fr||False	f	t	t
Call IBEX 35 | 7000 € | 21/09/12 | C3286	FR0011168269	EUR	5	|SGW|	f	76690	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3286||fr||False	f	t	t
Call IBEX 35 | 7500 € | 21/09/12 | C3287	FR0011168277	EUR	5	|SGW|	f	76693	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3287||fr||False	f	t	t
BIGBEN INTERACTIVE	FR0000074072	EUR	1	|EURONEXT|	f	76696	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000074072||fr||False	f	t	t
Call IBEX 35 | 8000 € | 18/11/11 | B9934	FR0011091230	EUR	5	|SGW|	f	76715	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9934||fr||False	f	t	t
ZENITEL STRIP	BE0005594651	EUR	1	|EURONEXT|	f	76705	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005594651||be||False	f	t	t
ZETES INDUST.STRIP	BE0005600714	EUR	1	|EURONEXT|	f	76706	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005600714||be||False	f	t	t
ZETES INDUSTRIES	BE0003827442	EUR	1	|EURONEXT|	f	76709	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003827442||be||False	f	t	t
HAL TRUST	BMG455841020	EUR	1	|EURONEXT|	f	76687	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#BMG455841020||nl||False	f	t	t
VIVENDA MEDIA GR	NL0009312362	EUR	1	|EURONEXT|	f	76695	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009312362||nl||False	f	t	t
Warner Chilcott plc	IE00B446CM77	USD	1	|NASDAQ100|	f	76697	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	WCRX||us||False	f	t	t
CAE Inc.	\N	USD	1	\N	f	76703	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CAE||us||False	f	t	t
Governor & Co. of the Bank of Ireland	\N	USD	1	\N	f	76717	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IRE||us||False	f	t	t
Post Properties Inc.	\N	USD	1	\N	f	76718	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PPS||us||False	f	t	t
Copa Holdings S.A. Cl A	\N	USD	1	\N	f	76719	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CPA||us||False	f	t	t
\N	\N	\N	\N	\N	f	77736	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	NYSE#HUB||None||False	f	t	t
BELVEDERE	FR0000060873	EUR	1	|EURONEXT|	f	76736	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060873||fr||False	f	t	t
BOURSE DIRECT	FR0000074254	EUR	1	|EURONEXT|	f	76737	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000074254||fr||False	f	t	t
CASINO GUICHARD	FR0000125585	EUR	1	|EURONEXT|	f	76741	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000125585||fr||False	f	t	t
GEVELOT	FR0000033888	EUR	1	|EURONEXT|	f	76744	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000033888||fr||False	f	t	t
ORCO PROPERTY GRP	LU0122624777	EUR	1	|EURONEXT|	f	76749	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#LU0122624777||fr||False	f	t	t
CISCO SYSTEM INC	US17275R1023	EUR	1	|EURONEXT|	f	76742	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#US17275R1023||nl||False	f	t	t
RANDSTAD	NL0000379121	EUR	1	|EURONEXT|	f	76750	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000379121||nl||False	f	t	t
Omega Healthcare Investors Inc.	\N	USD	1	\N	f	76721	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OHI||us||False	f	t	t
Wright Express Corp.	\N	USD	1	\N	f	76722	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WXS||us||False	f	t	t
Nielsen Holdings N.V.	\N	USD	1	\N	f	76726	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NLSN||us||False	f	t	t
Youku Inc.	\N	USD	1	\N	f	76727	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#YOKU||us||False	f	t	t
Cato Corp. Cl A	\N	USD	1	\N	f	76732	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CATO||us||False	f	t	t
Texas Industries Inc.	\N	USD	1	\N	f	76733	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TXI||us||False	f	t	t
Lions Gate Entertainment Corp.	\N	USD	1	\N	f	76734	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LGF||us||False	f	t	t
Tetra Technologies Inc.	\N	USD	1	\N	f	76735	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TTI||us||False	f	t	t
Mead Johnson Nutrition Co.	\N	USD	1	\N	f	76743	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MJN||us||False	f	t	t
Macy's Inc.	\N	USD	1	\N	f	76747	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#M||us||False	f	t	t
China Unicom (Hong Kong) Ltd.	\N	USD	1	\N	f	76748	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CHU||us||False	f	t	t
Sherwin-Williams Co.	\N	USD	1	\N	f	76753	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SHW||us||False	f	t	t
TECHNIP	FR0000131708	EUR	1	|EURONEXT|	f	76768	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000131708||fr||False	f	t	t
PRISMAFLEX INTL	FR0004044600	EUR	1	|EURONEXT|	f	76785	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004044600||fr||False	f	t	t
Put IBEX 35 | 9750 € | 20/04/12 | C2135	FR0011145432	EUR	5	|SGW|	f	76794	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C2135||fr||False	f	t	t
SOLVAY	BE0003470755	EUR	1	|EURONEXT|	f	76763	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003470755||be||False	f	t	t
NAT PORTEFEUIL (D)	BE0003845626	EUR	1	|EURONEXT|	f	76792	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003845626||be||False	f	t	t
SLIGRO FOOD GROUP	NL0000817179	EUR	1	|EURONEXT|	f	76755	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000817179||nl||False	f	t	t
INNOCONCEPTS	NL0000361145	EUR	1	|EURONEXT|	f	76761	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000361145||nl||False	f	t	t
POSTNL	NL0009739416	EUR	1	|EURONEXT|	f	76783	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009739416||nl||False	f	t	t
Wisconsin Energy Corp.	\N	USD	1	\N	f	76754	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WEC||us||False	f	t	t
Fidelity National Information Services Inc.	\N	USD	1	\N	f	76759	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FIS||us||False	f	t	t
Willis Group Holdings PLC	\N	USD	1	\N	f	76769	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WSH||us||False	f	t	t
WABCO Holdings Inc.	\N	USD	1	\N	f	76770	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WBC||us||False	f	t	t
AMERIGROUP Corp.	\N	USD	1	\N	f	76771	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AGP||us||False	f	t	t
Ritchie Bros. Auctioneers Inc.	\N	USD	1	\N	f	76773	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RBA||us||False	f	t	t
IDACORP Inc.	\N	USD	1	\N	f	76776	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IDA||us||False	f	t	t
Endurance Specialty Holdings Ltd.	\N	USD	1	\N	f	76777	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ENH||us||False	f	t	t
CNO Financial Group Inc.	\N	USD	1	\N	f	76778	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CNO||us||False	f	t	t
Janus Capital Group Inc.	\N	USD	1	\N	f	76781	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JNS||us||False	f	t	t
Navigant Consulting Inc.	\N	USD	1	\N	f	76782	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NCI||us||False	f	t	t
Total S.A.	\N	USD	1	\N	f	76788	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TOT||us||False	f	t	t
\N	\N	\N	\N	\N	f	77891	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0170644001||None||False	f	t	t
Call IBEX 35 | 8750 € | 18/05/12 | C1118	FR0011124239	EUR	5	|SGW|	f	76796	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1118||fr||False	f	t	t
Call IBEX 35 inLine | 8000 € | 17/06/11 | I0025	FR0011002377	EUR	5	|SGW|	f	76797	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0025||fr||False	f	t	t
Call IBEX 35 | 9000 € | 20/12/13 | C3305	FR0011168459	EUR	5	|SGW|	f	76798	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3305||fr||False	f	t	t
MAUREL ET PROM NV	FR0010986570	EUR	1	|EURONEXT|	f	76800	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010986570||fr||False	f	t	t
BOURBON NV	FR0010988816	EUR	1	|EURONEXT|	f	76802	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010988816||fr||False	f	t	t
Put IBEX 35 | 7500 € | 16/12/11 | B9942	FR0011091313	EUR	5	|SGW|	f	76810	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9942||fr||False	f	t	t
PROLOGUE	FR0010380626	EUR	1	|EURONEXT|	f	76811	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010380626||fr||False	f	t	t
Bed Bath & Beyond Inc	US0758961009	USD	1	|NASDAQ100|SP500|	f	76701					100	c	0	2	BBBY	{1}	{3}	BBBY||us||False	f	t	t
PROLOGIS EURO PROP	LU0467842786	EUR	1	|EURONEXT|	f	76801	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#LU0467842786||nl||False	f	t	t
PROLOGIS EURO PROP	LU0100194785	EUR	1	|EURONEXT|	f	76808	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#LU0100194785||nl||False	f	t	t
Kraft Foods Inc. Cl A	\N	USD	1	\N	f	76803	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KFT||us||False	f	t	t
Fortune Brands Inc.	\N	USD	1	\N	f	76809	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FO||us||False	f	t	t
EMC Corp.	\N	USD	1	\N	f	76813	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EMC||us||False	f	t	t
Petroleo Brasileiro S/A	\N	USD	1	\N	f	76817	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PBR||us||False	f	t	t
Put IBEX 35 | 9000 € | 21/09/12 | C3300	FR0011168400	EUR	5	|SGW|	f	76833	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3300||fr||False	f	t	t
Put IBEX 35 | 9500 € | 21/09/12 | C3301	FR0011168418	EUR	5	|SGW|	f	76834	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3301||fr||False	f	t	t
Put IBEX 35 | 10000 € | 21/09/12 | C3302	FR0011168426	EUR	5	|SGW|	f	76839	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3302||fr||False	f	t	t
Call IBEX 35 | 9000 € | 21/12/12 | C3304	FR0011168442	EUR	5	|SGW|	f	76841	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3304||fr||False	f	t	t
QUANTEL	FR0000038242	EUR	1	|EURONEXT|	f	76842	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000038242||fr||False	f	t	t
QUOTIUM TECHNO	FR0010211615	EUR	1	|EURONEXT|	f	76854	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010211615||fr||False	f	t	t
MEETIC	FR0011076488	EUR	1	|EURONEXT|	f	76855	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011076488||fr||False	f	t	t
PUBLICIS GROUPE SA	FR0000130577	EUR	1	|EURONEXT|	f	76856	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000130577||fr||False	f	t	t
Put IBEX 35 | 8000 € | 16/03/12 | B9954	FR0011091438	EUR	5	|SGW|	f	76857	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9954||fr||False	f	t	t
PUNCH INT.	BE0003748622	EUR	1	|EURONEXT|	f	76840	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003748622||be||False	f	t	t
QUESTFOR GR-PRICAF	BE0003730448	EUR	1	|EURONEXT|	f	76843	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003730448||be||False	f	t	t
Barrick Gold Corp.	\N	USD	1	\N	f	76818	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ABX||us||False	f	t	t
Canon Inc.	\N	USD	1	\N	f	76819	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CAJ||us||False	f	t	t
Goldman Sachs Group Inc.	\N	USD	1	\N	f	76820	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GS||us||False	f	t	t
Applied Industrial Technologies Inc.	\N	USD	1	\N	f	76822	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AIT||us||False	f	t	t
Brandywine Realty Trust	\N	USD	1	\N	f	76823	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BDN||us||False	f	t	t
Silvercorp Metals Inc.	\N	USD	1	\N	f	76824	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SVM||us||False	f	t	t
H.B. Fuller Co.	\N	USD	1	\N	f	76825	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FUL||us||False	f	t	t
Swift Energy Co.	\N	USD	1	\N	f	76826	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SFY||us||False	f	t	t
Stone Energy Corp.	\N	USD	1	\N	f	76827	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SGY||us||False	f	t	t
Simon Property Group Inc.	\N	USD	1	\N	f	76849	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SPG||us||False	f	t	t
Goldcorp Inc.	\N	USD	1	\N	f	76850	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GG||us||False	f	t	t
Southern Co.	\N	USD	1	\N	f	76853	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SO||us||False	f	t	t
Emerson Electric Co.	\N	USD	1	\N	f	76859	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EMR||us||False	f	t	t
STEF	FR0000064271	EUR	1	|EURONEXT|	f	76863	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064271||fr||False	f	t	t
QURIUS	NL0000368140	EUR	1	|EURONEXT|	f	76860	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000368140||nl||False	f	t	t
National Grid PLC	\N	USD	1	\N	f	76864	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NGG||us||False	f	t	t
Prudential PLC	\N	USD	1	\N	f	76865	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PUK||us||False	f	t	t
NextEra Energy Inc.	\N	USD	1	\N	f	76867	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NEE||us||False	f	t	t
Hitachi Ltd.	\N	USD	1	\N	f	76868	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HIT||us||False	f	t	t
General Mills Inc.	\N	USD	1	\N	f	76869	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GIS||us||False	f	t	t
Time Warner Cable Inc.	\N	USD	1	\N	f	76870	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TWC||us||False	f	t	t
Illinois Tool Works Inc.	\N	USD	1	\N	f	76871	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ITW||us||False	f	t	t
Lockheed Martin Corp.	\N	USD	1	\N	f	76876	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LMT||us||False	f	t	t
US Airways Group Inc.	\N	USD	1	\N	f	76877	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LCC||us||False	f	t	t
RSC Holdings Inc.	\N	USD	1	\N	f	76878	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RRR||us||False	f	t	t
Tennant Co.	\N	USD	1	\N	f	76879	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TNC||us||False	f	t	t
National Financial Partners Corp.	\N	USD	1	\N	f	76880	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NFP||us||False	f	t	t
\N	\N	\N	\N	\N	f	78023	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0147075008||None||False	f	t	t
BOIRON	FR0000061129	EUR	1	|EURONEXT|	f	76882	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000061129||fr||False	f	t	t
EDF ENERGIES NOUV.	FR0010400143	EUR	1	|EURONEXT|	f	76883	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010400143||fr||False	f	t	t
BUREAU VERITAS	FR0006174348	EUR	1	|EURONEXT|	f	76885	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0006174348||fr||False	f	t	t
CAMBODGE NOM.	FR0000079659	EUR	1	|EURONEXT|	f	76890	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000079659||fr||False	f	t	t
CAMELEON SOFTWARE	FR0000074247	EUR	1	|EURONEXT|	f	76891	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000074247||fr||False	f	t	t
CAMESO BSAR17JUL14	FR0010772921	EUR	1	|EURONEXT|	f	76901	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010772921||fr||False	f	t	t
PATRIMOINE & COMNS	FR0011048545	EUR	1	|EURONEXT|	f	76903	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011048545||fr||False	f	t	t
Put IBEX 35 | 11500 € | 16/12/11 | B5154	FR0011002880	EUR	5	|SGW|	f	76905	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B5154||fr||False	f	t	t
Put IBEX 35 | 12000 € | 16/12/11 | B5155	FR0011002898	EUR	5	|SGW|	f	76906	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B5155||fr||False	f	t	t
CAMPINE	BE0003825420	EUR	1	|EURONEXT|	f	76902	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003825420||be||False	f	t	t
Ashford Hospitality Trust Inc.	\N	USD	1	\N	f	76881	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AHT||us||False	f	t	t
H.J. Heinz Co.	\N	USD	1	\N	f	76886	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HNZ||us||False	f	t	t
Ecolab Inc.	\N	USD	1	\N	f	76887	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ECL||us||False	f	t	t
Noble Energy Inc.	\N	USD	1	\N	f	76893	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NBL||us||False	f	t	t
Chesapeake Energy Corp.	\N	USD	1	\N	f	76899	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CHK||us||False	f	t	t
Elan Corp. PLC	\N	USD	1	\N	f	76900	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ELN||us||False	f	t	t
DSW Inc. Cl A	\N	USD	1	\N	f	76904	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DSW||us||False	f	t	t
Par Pharmaceutical Cos. Inc.	\N	USD	1	\N	f	76907	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PRX||us||False	f	t	t
\N	\N	\N	\N	\N	f	76911	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0115711006||None||False	f	t	t
\N	\N	\N	\N	\N	f	76912	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0115718001||None||False	f	t	t
DANEELECBSAR13	FR0010329292	EUR	1	|EURONEXT|	f	76941	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010329292||fr||False	f	t	t
DEVERNOIS	FR0000060840	EUR	1	|EURONEXT|	f	76942	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060840||fr||False	f	t	t
DEVOTEAM	FR0000073793	EUR	1	|EURONEXT|	f	76943	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000073793||fr||False	f	t	t
Put IBEX 35 | 11000 € | 16/09/11 | B4752	FR0010984708	EUR	5	|SGW|	f	76954	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4752||fr||False	f	t	t
Put IBEX 35 | 11500 € | 16/09/11 | B4753	FR0010984716	EUR	5	|SGW|	f	76955	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4753||fr||False	f	t	t
BELRECA	BE0020575115	EUR	1	|EURONEXT|	f	76940	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0020575115||be||False	f	t	t
DOCKWISE	BMG2786A2052	EUR	1	|EURONEXT|	f	76944	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#BMG2786A2052||nl||False	f	t	t
\N	\N	\N	\N	\N	f	76913	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0115719009||None||False	f	t	t
Kemper Corp.	\N	USD	1	\N	f	76908	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KMPR||us||False	f	t	t
Platinum Underwriters Holdings Ltd.	\N	USD	1	\N	f	76909	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PTP||us||False	f	t	t
Synovus Financial Corp.	\N	USD	1	\N	f	76918	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SNV||us||False	f	t	t
Ann Inc.	\N	USD	1	\N	f	76919	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ANN||us||False	f	t	t
TERNIUM S.A.	\N	USD	1	\N	f	76921	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TX||us||False	f	t	t
Lexington Realty Trust	\N	USD	1	\N	f	76923	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LXP||us||False	f	t	t
Gaylord Entertainment Co.	\N	USD	1	\N	f	76924	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GET||us||False	f	t	t
Louisiana-Pacific Corp.	\N	USD	1	\N	f	76926	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LPX||us||False	f	t	t
Meritor Inc.	\N	USD	1	\N	f	76938	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MTOR||us||False	f	t	t
Kyocera Corp.	\N	USD	1	\N	f	76939	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KYO||us||False	f	t	t
TE Connectivity Ltd.	\N	USD	1	\N	f	76946	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TEL||us||False	f	t	t
ProLogis Inc.	\N	USD	1	\N	f	76950	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PLD||us||False	f	t	t
SeaDrill Ltd.	\N	USD	1	\N	f	76956	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SDRL||us||False	f	t	t
DOW CHEMICAL	US2605431038	EUR	1	|EURONEXT|	f	76963	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US2605431038||fr||False	f	t	t
ESSO	FR0000120669	EUR	1	|EURONEXT|	f	76964	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000120669||fr||False	f	t	t
FONCIERE 7 INVEST	FR0000065930	EUR	1	|EURONEXT|	f	76974	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000065930||fr||False	f	t	t
FORNIX BIOSCIENCES	NL0000439990	EUR	1	|EURONEXT|	f	76989	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000439990||nl||False	f	t	t
PETROTEC AG	DE000PET1111	EUR	1	|DEUTSCHEBOERSE|	f	76959	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000PET1111||de||False	f	t	t
Zimmer Holdings Inc.	\N	USD	1	\N	f	76965	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ZMH||us||False	f	t	t
ConAgra Foods Inc.	\N	USD	1	\N	f	76966	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CAG||us||False	f	t	t
Hypercom Corp.	\N	USD	1	\N	f	76973	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HYC||us||False	f	t	t
Limited Brands Inc.	\N	USD	1	\N	f	76975	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LTD||us||False	f	t	t
Ecopetrol S.A.	\N	USD	1	\N	f	76976	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EC||us||False	f	t	t
Starwood Hotels & Resorts Worldwide Inc.	\N	USD	1	\N	f	76977	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HOT||us||False	f	t	t
Tyson Foods Inc. Cl A	\N	USD	1	\N	f	76978	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TSN||us||False	f	t	t
Scotts Miracle-Gro Co.	\N	USD	1	\N	f	76983	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SMG||us||False	f	t	t
GATX Corp.	\N	USD	1	\N	f	76985	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GMT||us||False	f	t	t
Diebold Inc.	\N	USD	1	\N	f	76986	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DBD||us||False	f	t	t
Tata Motors Ltd.	\N	USD	1	\N	f	76988	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TTM||us||False	f	t	t
THALES NV	FR0010979641	EUR	1	|EURONEXT|	f	76991	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010979641||fr||False	f	t	t
Put IBEX 35 | 10250 € | 19/08/11 | B6057	FR0011017821	EUR	5	|SGW|	f	76992	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B6057||fr||False	f	t	t
LVL MEDICAL GROUPE	FR0011034651	EUR	1	|EURONEXT|	f	76994	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011034651||fr||False	f	t	t
Put IBEX 35 | 9750 € | 17/02/12 | B9712	FR0011083914	EUR	5	|SGW|	f	76999	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9712||fr||False	f	t	t
G.OPEN BSAAR1014	FR0010518654	EUR	1	|EURONEXT|	f	77006	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010518654||fr||False	f	t	t
FORESTIERE EQUAT.	CI0000053161	EUR	1	|EURONEXT|	f	77010	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#CI0000053161||fr||False	f	t	t
FOUNTAIN	BE0003752665	EUR	1	|EURONEXT|	f	76993	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003752665||be||False	f	t	t
FORD MOTOR CERT	BE0004571122	EUR	1	|EURONEXT|	f	77004	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0004571122||be||False	f	t	t
GOLDFIELDS(X.DRIEF	BE0004529674	EUR	1	|EURONEXT|	f	77011	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0004529674||be||False	f	t	t
Hartford Financial Services Group Inc.	\N	USD	1	\N	f	76995	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HIG||us||False	f	t	t
Denbury Resources Inc.	\N	USD	1	\N	f	77000	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DNR||us||False	f	t	t
Emdeon Inc. Cl A	\N	USD	1	\N	f	77002	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EM||us||False	f	t	t
Telekomunikasi Indonesia	\N	USD	1	\N	f	77005	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TLK||us||False	f	t	t
AutoNation Inc.		USD	1	|SP500|	f	76920					100	c	0	2	AN	{1}	{3}	NYSE#AN||us||False	f	t	t
Newell Rubbermaid Inc.	\N	USD	1	\N	f	77023	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NWL||us||False	f	t	t
Dollar General Corp.	\N	USD	1	\N	f	77024	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DG||us||False	f	t	t
Scana Corp.	\N	USD	1	\N	f	77025	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SCG||us||False	f	t	t
Avnet Inc.	\N	USD	1	\N	f	77030	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AVT||us||False	f	t	t
Cimarex Energy Co.	\N	USD	1	\N	f	77031	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#XEC||us||False	f	t	t
International Game Technology	\N	USD	1	\N	f	77032	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IGT||us||False	f	t	t
\N	\N	\N	\N	\N	f	77027	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0133486003||None||False	f	t	t
IMPRESA,SGPS	PTIPR0AM0000	EUR	1	|EURONEXT|	f	77041	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTIPR0AM0000||pt||False	f	t	t
HENRI MAIRE	FR0000061087	EUR	1	|EURONEXT|	f	77039	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000061087||fr||False	f	t	t
INNATE PHARMA	FR0010331421	EUR	1	|EURONEXT|	f	77064	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010331421||fr||False	f	t	t
LE TANNEUR	FR0000075673	EUR	1	|EURONEXT|	f	77065	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000075673||fr||False	f	t	t
ING GROEP CERT	BE0004523610	EUR	1	|EURONEXT|	f	77052	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0004523610||be||False	f	t	t
LEASINVEST-SICAFI	BE0003770840	EUR	1	|EURONEXT|	f	77066	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003770840||be||False	f	t	t
Ivanhoe Mines Ltd.	\N	USD	1	\N	f	77033	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IVN||us||False	f	t	t
Diana Shipping Inc.	\N	USD	1	\N	f	77037	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DSX||us||False	f	t	t
CVS Caremark Corp.	\N	USD	1	\N	f	77040	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CVS||us||False	f	t	t
United Parcel Service Inc. Cl B	\N	USD	1	\N	f	77044	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UPS||us||False	f	t	t
Freeport-McMoRan Copper & Gold Inc.	\N	USD	1	\N	f	77048	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FCX||us||False	f	t	t
Praxair Inc.	\N	USD	1	\N	f	77062	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PX||us||False	f	t	t
Royal Bank of Scotland Group PLC	\N	USD	1	\N	f	77063	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RBS||us||False	f	t	t
Compania de Minas Buenaventura S.A.	\N	USD	1	\N	f	77067	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BVN||us||False	f	t	t
Herbalife Ltd.	\N	USD	1	\N	f	77068	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HLF||us||False	f	t	t
COFIGEO	FR0000035008	EUR	1	|EURONEXT|	f	77070	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000035008||fr||False	f	t	t
STORE ELEC NV	FR0010987032	EUR	1	|EURONEXT|	f	77073	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010987032||fr||False	f	t	t
SL Green Realty Corp.	\N	USD	1	\N	f	77071	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SLG||us||False	f	t	t
Wyndham Worldwide Corp.	\N	USD	1	\N	f	77074	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WYN||us||False	f	t	t
General Growth Properties Inc.	\N	USD	1	\N	f	77076	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GGP||us||False	f	t	t
Helmerich & Payne Inc.	\N	USD	1	\N	f	77077	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HP||us||False	f	t	t
Darden Restaurants Inc.	\N	USD	1	\N	f	77078	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DRI||us||False	f	t	t
Credicorp Ltd.	\N	USD	1	\N	f	77081	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BAP||us||False	f	t	t
INM.COLONIAL	ES0139140018	EUR	1	|MERCADOCONTINUO|	f	77072	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0139140018||es||False	f	t	t
CMS Energy Corp.	\N	USD	1	\N	f	77082	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CMS||us||False	f	t	t
Bridgepoint Education Inc.	\N	USD	1	\N	f	77086	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BPI||us||False	f	t	t
Monsanto Co.	\N	USD	1	\N	f	78464	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MON||us||False	f	t	t
INTEXA	FR0000064958	EUR	1	|EURONEXT|	f	77093	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064958||fr||False	f	t	t
PHILIP MORRIS INTL	US7181721090	EUR	1	|EURONEXT|	f	77095	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US7181721090||fr||False	f	t	t
EUROSIC BS	FR0011129048	EUR	1	|EURONEXT|	f	77098	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011129048||fr||False	f	t	t
PICANOL	BE0003807246	EUR	1	|EURONEXT|	f	77101	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003807246||be||False	f	t	t
INT FLAVORS	US4595061015	EUR	1	|EURONEXT|	f	77091	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#US4595061015||nl||False	f	t	t
PHARMING GROUP	NL0000377018	EUR	1	|EURONEXT|	f	77094	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000377018||nl||False	f	t	t
Lowe's Cos.	\N	USD	1	\N	f	77092	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LOW||us||False	f	t	t
Northrop Grumman Corp.	\N	USD	1	\N	f	77097	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NOC||us||False	f	t	t
Kroger Co.	\N	USD	1	\N	f	77104	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KR||us||False	f	t	t
Chunghwa Telecom Co. Ltd.	\N	USD	1	\N	f	77109	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CHT||us||False	f	t	t
CEPSA	ES0132580319	EUR	1	|MERCADOCONTINUO|	f	77112	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0132580319||es||False	f	t	t
REN	PTREL0AM0008	EUR	1	|EURONEXT|	f	77146	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTREL0AM0008||pt||False	f	t	t
PUBLICIS BSA	FR0000312928	EUR	1	|EURONEXT|	f	77138	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000312928||fr||False	f	t	t
RBS CAP FUND TR V	US74928K2087	EUR	1	|EURONEXT|	f	77141	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#US74928K2087||nl||False	f	t	t
Essex Property Trust Inc.	\N	USD	1	\N	f	77113	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ESS||us||False	f	t	t
Realty Income Corp.	\N	USD	1	\N	f	77114	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#O||us||False	f	t	t
Torchmark Corp.	\N	USD	1	\N	f	77119	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TMK||us||False	f	t	t
Equifax Inc.	\N	USD	1	\N	f	77120	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EFX||us||False	f	t	t
ING GROEP	NL0000303600	EUR	1	|EURONEXT|EUROSTOXX|	f	77046					100	c	0	12	None	\N	\N	EURONEXT#NL0000303600||nl||False	f	t	t
PHILIPS KON	NL0000009538	EUR	1	|EURONEXT|EUROSTOXX|	f	77096					100	c	0	12	None	\N	\N	EURONEXT#NL0000009538||nl||False	f	t	t
Brookfield Office Properties Inc.	\N	USD	1	\N	f	77126	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BPO||us||False	f	t	t
SAIC Inc.	\N	USD	1	\N	f	77127	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SAI||us||False	f	t	t
Alere Inc.	\N	USD	1	\N	f	77128	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ALR||us||False	f	t	t
ITT Corp.	\N	USD	1	\N	f	77129	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ITT||us||False	f	t	t
Bio-Rad Laboratories Inc. Cl A	\N	USD	1	\N	f	77132	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BIO||us||False	f	t	t
Dean Foods Co.	\N	USD	1	\N	f	77133	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DF||us||False	f	t	t
\N	\N	\N	\N	\N	f	77144	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0136083039||None||False	f	t	t
REXEL	FR0010451203	EUR	1	|EURONEXT|	f	77149	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010451203||fr||False	f	t	t
REXEL NV	FR0011170026	EUR	1	|EURONEXT|	f	77151	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011170026||fr||False	f	t	t
RIO TINTO ORD	GB0007188757	EUR	1	|EURONEXT|	f	77154	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#GB0007188757||fr||False	f	t	t
SOLVING EFESO INTL	FR0004500106	EUR	1	|EURONEXT|	f	77184	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004500106||fr||False	f	t	t
REXEL NV	FR0010978809	EUR	1	|EURONEXT|	f	77188	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010978809||fr||False	f	t	t
RHJ INTERNATIONAL	BE0003815322	EUR	1	|EURONEXT|	f	77153	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003815322||be||False	f	t	t
BOEING CERT	BE0004608494	EUR	1	|EURONEXT|	f	77185	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0004608494||be||False	f	t	t
NAT PORTEF STR(D)	BE0005603742	EUR	1	|EURONEXT|	f	77187	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005603742||be||False	f	t	t
SACYR D11-J	ES0682870979	EUR	1	|MERCADOCONTINUO|	f	77148	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0682870979||es||False	f	t	t
schlott gruppe Aktiengesellschaft	DE0005046304	EUR	1	|DEUTSCHEBOERSE|	f	77157	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005046304||de||False	f	t	t
Pinnacle West Capital Corp.	\N	USD	1	\N	f	77152	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PNW||us||False	f	t	t
Tempur-Pedic International Inc.	\N	USD	1	\N	f	77155	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TPX||us||False	f	t	t
MGM Resorts International	\N	USD	1	\N	f	77156	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MGM||us||False	f	t	t
AU Optronics Corp.	\N	USD	1	\N	f	77159	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AUO||us||False	f	t	t
Diamond Offshore Drilling Inc.	\N	USD	1	\N	f	77160	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DO||us||False	f	t	t
Oil States International Inc.	\N	USD	1	\N	f	77161	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OIS||us||False	f	t	t
Global Payments Inc.	\N	USD	1	\N	f	77162	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GPN||us||False	f	t	t
W.R. Berkley Corp.	\N	USD	1	\N	f	77163	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WRB||us||False	f	t	t
Ultra Petroleum Corp.	\N	USD	1	\N	f	77164	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UPL||us||False	f	t	t
Stantec Inc.	\N	USD	1	\N	f	77165	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STN||us||False	f	t	t
Primerica Inc.	\N	USD	1	\N	f	77166	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PRI||us||False	f	t	t
Choice Hotels International Inc.	\N	USD	1	\N	f	77167	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CHH||us||False	f	t	t
CNH Global N.V.	\N	USD	1	\N	f	77177	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CNH||us||False	f	t	t
ABM Industries Inc.	\N	USD	1	\N	f	77178	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ABM||us||False	f	t	t
Piper Jaffray Cos.	\N	USD	1	\N	f	77179	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PJC||us||False	f	t	t
Standard Motor Products Inc.	\N	USD	1	\N	f	77180	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SMP||us||False	f	t	t
Triple-S Management Corp. Cl B	\N	USD	1	\N	f	77181	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GTS||us||False	f	t	t
Advance America Cash Advance Centers Inc.	\N	USD	1	\N	f	77182	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AEA||us||False	f	t	t
Brown Shoe Co. Inc.	\N	USD	1	\N	f	77183	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BWS||us||False	f	t	t
BONBSAAR2016	FR0010734509	EUR	1	|EURONEXT|	f	77198	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010734509||fr||False	f	t	t
FINATIS	FR0000035123	EUR	1	|EURONEXT|	f	77207	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000035123||fr||False	f	t	t
MAISONS FRANCE	FR0004159473	EUR	1	|EURONEXT|	f	77209	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004159473||fr||False	f	t	t
BOEING COMPANY	US0970231058	EUR	1	|EURONEXT|	f	77197	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#US0970231058||nl||False	f	t	t
MARATHON OIL CORP	US5658491064	EUR	1	|EURONEXT|	f	77200	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#US5658491064||nl||False	f	t	t
TNT	NL0000009066	EUR	1	|EURONEXT|	f	77201	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000009066||nl||False	f	t	t
SPYKER CARS	NL0000380830	EUR	1	|EURONEXT|	f	77205	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000380830||nl||False	f	t	t
euromicron AG	DE0005660005	EUR	1	|DEUTSCHEBOERSE|	f	77194	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005660005||de||False	f	t	t
International Business Machines Corp.	\N	USD	1	\N	f	77196	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IBM||us||False	f	t	t
Merck & Co. Inc.	\N	USD	1	\N	f	77206	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MRK||us||False	f	t	t
Verizon Communications Inc.	\N	USD	1	\N	f	77208	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VZ||us||False	f	t	t
Sanofi	\N	USD	1	\N	f	77210	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SNY||us||False	f	t	t
MSCI Inc. Cl A	\N	USD	1	\N	f	77213	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MSCI||us||False	f	t	t
Senior Housing Properties Trust	\N	USD	1	\N	f	77215	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SNH||us||False	f	t	t
KT Corp.	\N	USD	1	\N	f	77216	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KT||us||False	f	t	t
Smithfield Foods Inc.	\N	USD	1	\N	f	77219	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SFD||us||False	f	t	t
Questar Corp.	\N	USD	1	\N	f	77220	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STR||us||False	f	t	t
GameStop Corp. Cl A	\N	USD	1	\N	f	77222	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GME||us||False	f	t	t
Guess? Inc.	\N	USD	1	\N	f	77223	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GES||us||False	f	t	t
Heico Corp.	\N	USD	1	\N	f	78711	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HEI||us||False	f	t	t
VALEO NV	FR0010979484	EUR	1	|EURONEXT|	f	77235	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010979484||fr||False	f	t	t
CARREFOUR	FR0000120172	EUR	1	|EURONEXT|	f	77236	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000120172||fr||False	f	t	t
SCHLUMBERGER	AN8068571086	EUR	1	|EURONEXT|	f	77239	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#AN8068571086||fr||False	f	t	t
Call IBEX 35 | 9000 € | 16/09/11 | B4738	FR0010984567	EUR	5	|SGW|	f	77247	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4738||fr||False	f	t	t
Call IBEX 35 | 10000 € | 16/09/11 | B4740	FR0010984583	EUR	5	|SGW|	f	77248	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4740||fr||False	f	t	t
Call IBEX 35 | 10500 € | 16/09/11 | B4741	FR0010984591	EUR	5	|SGW|	f	77249	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4741||fr||False	f	t	t
Patni Computer Systems Ltd.	\N	USD	1	\N	f	77232	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PTI||us||False	f	t	t
EOG Resources Inc.	\N	USD	1	\N	f	77237	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EOG||us||False	f	t	t
Mosaic Co.	\N	USD	1	\N	f	77241	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MOS||us||False	f	t	t
TURBO Put IBEX 35 | 10250 € | 16/09/11 | 54979	FR0011057561	EUR	5	|SGW|	f	77252	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54979||fr||False	f	t	t
TURBO Put IBEX 35 | 10750 € | 16/09/11 | 54981	FR0011057587	EUR	5	|SGW|	f	77253	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54981||fr||False	f	t	t
Call IBEX 35 | 8000 € | 16/09/11 | B4736	FR0010984542	EUR	5	|SGW|	f	77256	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4736||fr||False	f	t	t
Call IBEX 35 | 8500 € | 16/09/11 | B4737	FR0010984559	EUR	5	|SGW|	f	77257	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B4737||fr||False	f	t	t
ARKEMA NV	FR0010979476	EUR	1	|EURONEXT|	f	77258	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010979476||fr||False	f	t	t
General Motors Co.	\N	USD	1	\N	f	77254	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GM||us||False	f	t	t
Jones Lang LaSalle Inc.	\N	USD	1	\N	f	77261	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JLL||us||False	f	t	t
W.R. Grace & Co.	\N	USD	1	\N	f	77263	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GRA||us||False	f	t	t
Piedmont Office Realty Trust Inc. Cl A	\N	USD	1	\N	f	77267	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PDM||us||False	f	t	t
Domtar Corp.	\N	USD	1	\N	f	77268	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UFS||us||False	f	t	t
Provident Energy Ltd.	\N	USD	1	\N	f	77269	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PVX||us||False	f	t	t
UGI Corp.	\N	USD	1	\N	f	77270	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UGI||us||False	f	t	t
Vonage Holdings Corp.	\N	USD	1	\N	f	77275	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VG||us||False	f	t	t
CTS Corp.	\N	USD	1	\N	f	77279	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CTS||us||False	f	t	t
Movado Group Inc.	\N	USD	1	\N	f	77280	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MOV||us||False	f	t	t
Venoco Inc.	\N	USD	1	\N	f	77281	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VQ||us||False	f	t	t
Suncor Energy Inc.	\N	USD	1	\N	f	77283	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SU||us||False	f	t	t
Koninklijke Philips Electronics N.V.	\N	USD	1	\N	f	77284	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PHG||us||False	f	t	t
Spectra Energy Corp.	\N	USD	1	\N	f	77288	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SE||us||False	f	t	t
ARKEMA NV	FR0011169804	EUR	1	|EURONEXT|	f	77293	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011169804||fr||False	f	t	t
ATARI BSA 31/12/12	FR0010690099	EUR	1	|EURONEXT|	f	77295	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010690099||fr||False	f	t	t
AVIAT LATECOERE BS	FR0010910562	EUR	1	|EURONEXT|	f	77296	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010910562||fr||False	f	t	t
ABC ARBITRAGE	FR0004040608	EUR	1	|EURONEXT|	f	77334	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004040608||fr||False	f	t	t
ADL PARTNER	FR0000062978	EUR	1	|EURONEXT|	f	77341	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000062978||fr||False	f	t	t
CIMENTS FRANCAIS	FR0000120982	EUR	1	|EURONEXT|	f	77342	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000120982||fr||False	f	t	t
ACKERMANS V.HAAREN	BE0003764785	EUR	1	|EURONEXT|	f	77340	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003764785||be||False	f	t	t
AALBERTS INDUSTR	NL0000852564	EUR	1	|EURONEXT|	f	77286	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000852564||nl||False	f	t	t
AMG	NL0000888691	EUR	1	|EURONEXT|	f	77292	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000888691||nl||False	f	t	t
ACCSYS	GB00B0LMC530	EUR	1	|EURONEXT|	f	77339	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GB00B0LMC530||nl||False	f	t	t
State Street Corp.	\N	USD	1	\N	f	77299	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STT||us||False	f	t	t
Under Armour Inc. Cl A	\N	USD	1	\N	f	77300	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UA||us||False	f	t	t
Clean Harbors Inc.	\N	USD	1	\N	f	77302	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CLH||us||False	f	t	t
Broadridge Financial Solutions Inc.	\N	USD	1	\N	f	77303	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BR||us||False	f	t	t
Atmos Energy Corp.	\N	USD	1	\N	f	77305	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ATO||us||False	f	t	t
Carlisle Cos.	\N	USD	1	\N	f	77306	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CSL||us||False	f	t	t
Ingram Micro Inc. Cl A	\N	USD	1	\N	f	77307	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IM||us||False	f	t	t
AMCOL International Corp.	\N	USD	1	\N	f	77327	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ACO||us||False	f	t	t
Crude Carriers Corp.	\N	USD	1	\N	f	77338	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CRU||us||False	f	t	t
BEFESA	ES0114491014	EUR	1	|MERCADOCONTINUO|	f	77343	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0114491014||es||False	f	t	t
SANT DI11(49P1)	ES0613900986	EUR	1	|EURONEXT|	f	77348	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#ES0613900986||pt||False	f	t	t
DMS BC	FR0010944876	EUR	1	|EURONEXT|	f	77373	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010944876||fr||False	f	t	t
GECI INTL	FR0000079634	EUR	1	|EURONEXT|	f	77374	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000079634||fr||False	f	t	t
GENERIX	FR0010501692	EUR	1	|EURONEXT|	f	77377	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010501692||fr||False	f	t	t
GROUPE GO SPORT	FR0000072456	EUR	1	|EURONEXT|	f	77387	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000072456||fr||False	f	t	t
GPE EUROTUN.BS 07	FR0010452441	EUR	1	|EURONEXT|	f	77391	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010452441||fr||False	f	t	t
GOODYEAR CERT	BE0004359916	EUR	1	|EURONEXT|	f	77385	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0004359916||be||False	f	t	t
SCHNEIDER ELECTRIC	FR0000121972	EUR	1	|CAC|EURONEXT|EUROSTOXX|	f	77242					100	c	0	3	None	\N	\N	EURONEXT#FR0000121972||fr||False	f	t	t
ACCOR	FR0000120404	EUR	1	|CAC|EURONEXT|	f	77335					100	c	0	3	None	\N	\N	EURONEXT#FR0000120404||fr||False	f	t	t
Nomura Holdings Inc.	\N	USD	1	\N	f	77354	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NMR||us||False	f	t	t
Silver Wheaton Corp.	\N	USD	1	\N	f	77355	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SLW||us||False	f	t	t
Home Properties Inc.	\N	USD	1	\N	f	77356	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HME||us||False	f	t	t
Packaging Corp. of America	\N	USD	1	\N	f	77368	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PKG||us||False	f	t	t
Fortune Brands Home & Security Inc.	\N	USD	1	\N	f	77369	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FBHS||us||False	f	t	t
Dover Corp.	\N	USD	1	\N	f	77375	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DOV||us||False	f	t	t
Marriott International Inc. Cl A	\N	USD	1	\N	f	77379	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MAR||us||False	f	t	t
Alberto-Culver Co.	\N	USD	1	\N	f	77381	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ACV||us||False	f	t	t
Beckman Coulter Inc.	\N	USD	1	\N	f	77382	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BEC||us||False	f	t	t
Genuine Parts Co.	\N	USD	1	\N	f	77383	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GPC||us||False	f	t	t
Ralph Lauren Corp. Cl A	\N	USD	1	\N	f	77386	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RL||us||False	f	t	t
American Eagle Outfitters Inc.	\N	USD	1	\N	f	77390	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AEO||us||False	f	t	t
BCPDI11(0.04399P1)	PTBCP0AMI015	EUR	1	|EURONEXT|	f	77398	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTBCP0AMI015||pt||False	f	t	t
Call IBEX 35 | 10750 € | 21/10/11 | B7209	FR0011039593	EUR	5	|SGW|	f	77393	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7209||fr||False	f	t	t
Call IBEX 35 | 11250 € | 21/10/11 | B7210	FR0011039601	EUR	5	|SGW|	f	77397	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7210||fr||False	f	t	t
TURBO Put IBEX 35 | 10500 € | 16/12/11 | 55020	FR0011076876	EUR	5	|SGW|	f	77428	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#55020||fr||False	f	t	t
MOTORS LIQUID CERT	BE0004593340	EUR	1	|EURONEXT|	f	77405	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0004593340||be||False	f	t	t
Patterson Companies Inc.	\N	USD	1	|NASDAQ100|	f	77396	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	PDCO||us||False	f	t	t
Liberty Media Interactive	\N	USD	1	|NASDAQ100|	f	77399	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	LINTA||us||False	f	t	t
Gilead Sciences, Inc.	US3755581036	USD	1	|NASDAQ100|	f	77426	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	GILD||us||False	f	t	t
Complete Production Services Inc.	\N	USD	1	\N	f	77392	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CPX||us||False	f	t	t
Clarcor Inc.	\N	USD	1	\N	f	77403	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CLC||us||False	f	t	t
Colonial Properties Trust	\N	USD	1	\N	f	77411	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CLP||us||False	f	t	t
Five Star Quality Care Inc.	\N	USD	1	\N	f	77419	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FVE||us||False	f	t	t
Mahanagar Telephone Nigam Ltd.	\N	USD	1	\N	f	77420	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MTE||us||False	f	t	t
SeaBright Holdings Inc.	\N	USD	1	\N	f	77421	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SBX||us||False	f	t	t
Bank of Montreal	\N	USD	1	\N	f	77422	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BMO||us||False	f	t	t
AuRico Gold Inc.	\N	USD	1	\N	f	77424	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AUQ||us||False	f	t	t
Call IBEX 35 | 10250 € | 21/10/11 | B7208	FR0011039585	EUR	5	|SGW|	f	77432	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7208||fr||False	f	t	t
AREVA CI	FR0004275832	EUR	1	|EURONEXT|	f	77433	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004275832||fr||False	f	t	t
Call IBEX 35 | 11750 € | 21/10/11 | B7211	FR0011039619	EUR	5	|SGW|	f	77451	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7211||fr||False	f	t	t
Call IBEX 35 | 12250 € | 21/10/11 | B7212	FR0011039627	EUR	5	|SGW|	f	77452	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7212||fr||False	f	t	t
AGTA RECORD	CH0008853209	EUR	1	|EURONEXT|	f	77472	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#CH0008853209||fr||False	f	t	t
IFCO Systems N.V.	NL0000268456	EUR	1	|DEUTSCHEBOERSE|	f	77454	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#NL0000268456||de||False	f	t	t
Illumina Inc.	US4523271090	USD	1	|NASDAQ100|	f	77442	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	ILMN||us||False	f	t	t
Millicom International Cellular	\N	USD	1	|NASDAQ100|	f	77455	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	MICC||us||False	f	t	t
Cerner Corporation	US1567821046	USD	1	|NASDAQ100|	f	77457	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	CERN||us||False	f	t	t
Tanger Factory Outlet Centers Inc.	\N	USD	1	\N	f	77429	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SKT||us||False	f	t	t
Compass Minerals International Inc.	\N	USD	1	\N	f	77437	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CMP||us||False	f	t	t
Valley National Bancorp	\N	USD	1	\N	f	77439	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VLY||us||False	f	t	t
Endeavour Silver Corp.	\N	USD	1	\N	f	77447	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EXK||us||False	f	t	t
First Industrial Realty Trust Inc.	\N	USD	1	\N	f	77463	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FR||us||False	f	t	t
Granite Construction Inc.	\N	USD	1	\N	f	77464	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GVA||us||False	f	t	t
Swift Transportation Co. Cl A	\N	USD	1	\N	f	77465	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SWFT||us||False	f	t	t
GAMMA HOLDING	NL0000355824	EUR	1	|EURONEXT|	f	77474	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000355824||nl||False	f	t	t
GAMMA HOLDING	NL0000355865	EUR	1	|EURONEXT|	f	77475	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000355865||nl||False	f	t	t
AJAX	NL0000018034	EUR	1	|EURONEXT|	f	77484	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000018034||nl||False	f	t	t
SanDisk Corporation	\N	USD	1	|NASDAQ100|	f	77487	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	SNDK||us||False	f	t	t
O'Reilly Automotive Inc.	\N	USD	1	|NASDAQ100|	f	77494	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	ORLY||us||False	f	t	t
Paychex Inc.	\N	USD	1	|NASDAQ100|	f	77495	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	PAYX||us||False	f	t	t
Marvell Technology Group, Ltd.	\N	USD	1	|NASDAQ100|	f	77496	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	MRVL||us||False	f	t	t
Microsoft Corporation	\N	USD	1	|NASDAQ100|	f	77497	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	MSFT||us||False	f	t	t
Staples, Inc.	\N	USD	1	|NASDAQ100|	f	77498	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	SPLS||us||False	f	t	t
Seagate Technology PLC	\N	USD	1	|NASDAQ100|	f	77499	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	STX||us||False	f	t	t
Activision Blizzard Inc.	US00507V1098	USD	1	|NASDAQ100|	f	77500	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	ATVI||us||False	f	t	t
Urban Outfitters Inc.	\N	USD	1	|NASDAQ100|	f	77501	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	URBN||us||False	f	t	t
Amgen Inc.	US0311621009	USD	1	|NASDAQ100|SP500|	f	77440					100	c	0	2	None	\N	\N	AMGN||us||False	f	t	t
HAMON STRIP	BE0005529970	EUR	1	|EURONEXT|	f	77530	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005529970||be||False	f	t	t
HARBOURVEST HVGPE	GG00B28XHD63	EUR	1	|EURONEXT|	f	77533	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GG00B28XHD63||nl||False	f	t	t
Intuit Inc.	US4612021034	USD	1	|NASDAQ100|	f	77527	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	INTU||us||False	f	t	t
Cognizant Technology Solutions	US1924461023	USD	1	|NASDAQ100|	f	77535	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	CTSH||us||False	f	t	t
Shinhan Financial Group Co. Ltd.	\N	USD	1	\N	f	77504	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SHG||us||False	f	t	t
Estee Lauder Cos. Inc.	\N	USD	1	\N	f	77505	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EL||us||False	f	t	t
Extra Space Storage Inc.	\N	USD	1	\N	f	77506	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EXR||us||False	f	t	t
Six Flags Entertainment Corp.	\N	USD	1	\N	f	77507	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SIX||us||False	f	t	t
Corrections Corp. of America	\N	USD	1	\N	f	77508	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CXW||us||False	f	t	t
Vectren Corp.	\N	USD	1	\N	f	77509	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VVC||us||False	f	t	t
First Horizon National Corp.	\N	USD	1	\N	f	77512	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FHN||us||False	f	t	t
Headwaters Inc.	\N	USD	1	\N	f	77518	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HW||us||False	f	t	t
Imperva Inc.	\N	USD	1	\N	f	77519	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IMPV||us||False	f	t	t
Wells Fargo & Co.	\N	USD	1	\N	f	77521	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WFC||us||False	f	t	t
McDonald's Corp.	\N	USD	1	\N	f	77529	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MCD||us||False	f	t	t
Royal Bank of Canada	\N	USD	1	\N	f	77534	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RY||us||False	f	t	t
GENERIX DS	FR0011120765	EUR	1	|EURONEXT|	f	77540	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011120765||fr||False	f	t	t
EBIZCUSS.COM	FR0000078859	EUR	1	|EURONEXT|	f	77543	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000078859||fr||False	f	t	t
Comcast Corporation	US20030N1019	USD	1	|NASDAQ100|	f	77544	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	CMCSK||us||False	f	t	t
Starbucks Corporation	\N	USD	1	|NASDAQ100|	f	77545	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	SBUX||us||False	f	t	t
Westpac Banking Corp.	\N	USD	1	\N	f	77536	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WBK||us||False	f	t	t
Garmin Ltd.	CH0114405324	USD	1	|NASDAQ100|	f	77554	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	GRMN||us||False	f	t	t
Banco Santander S.A.	\N	USD	1	\N	f	77537	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STD||us||False	f	t	t
Tidewater Inc.	\N	USD	1	\N	f	77560	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TDW||us||False	f	t	t
Old Republic International Corp.	\N	USD	1	\N	f	77563	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ORI||us||False	f	t	t
United Rentals Inc.	\N	USD	1	\N	f	77564	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#URI||us||False	f	t	t
Priceline.com Incorporated	\N	USD	1	|NASDAQ100|	f	77577	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	PCLN||us||False	f	t	t
Sigma-Aldrich Corporation	\N	USD	1	|NASDAQ100|	f	77581	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	SIAL||us||False	f	t	t
Directv	US25490A1016	USD	1	|NASDAQ100|	f	77583	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	DTV||us||False	f	t	t
Tenet Healthcare Corp.	\N	USD	1	\N	f	77565	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#THC||us||False	f	t	t
Superior Energy Services Inc.	\N	USD	1	\N	f	77566	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SPN||us||False	f	t	t
Brinker International Inc.	\N	USD	1	\N	f	77567	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EAT||us||False	f	t	t
Forestar Group Inc.	\N	USD	1	\N	f	77570	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FOR||us||False	f	t	t
Sara Lee Corp.	\N	USD	1	\N	f	77571	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SLE||us||False	f	t	t
NewMarket Corp.	\N	USD	1	\N	f	77574	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NEU||us||False	f	t	t
LAFARGE NV	FR0010982207	EUR	1	|EURONEXT|	f	77585	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010982207||fr||False	f	t	t
ALCATEL LUCENT NV	FR0010985861	EUR	1	|EURONEXT|	f	77598	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010985861||fr||False	f	t	t
ALANHERI	NL0000440022	EUR	1	|EURONEXT|	f	77599	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000440022||nl||False	f	t	t
Virgin Media, Inc.	\N	USD	1	|NASDAQ100|	f	77586	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	VMED||us||False	f	t	t
Genzyme Corporation	US3729171047	USD	1	|NASDAQ100|	f	77587	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	GENZ||us||False	f	t	t
Foster Wheeler AG.	CH0018666781	USD	1	|NASDAQ100|	f	77588	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	FWLT||us||False	f	t	t
Baidu Inc.	US0567521085	USD	1	|NASDAQ100|	f	77602	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	BIDU||us||False	f	t	t
New Jersey Resources Corp.	\N	USD	1	\N	f	77589	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NJR||us||False	f	t	t
Sensient Technologies Corp.	\N	USD	1	\N	f	77590	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SXT||us||False	f	t	t
Chico's Fas Inc.	\N	USD	1	\N	f	77591	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CHS||us||False	f	t	t
Toro Co.	\N	USD	1	\N	f	77593	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TTC||us||False	f	t	t
Aluminum Corp. of China Ltd.	\N	USD	1	\N	f	77594	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ACH||us||False	f	t	t
Harsco Corp.	\N	USD	1	\N	f	77595	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HSC||us||False	f	t	t
DigitalGlobe Inc.	\N	USD	1	\N	f	77597	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DGI||us||False	f	t	t
\N	\N	\N	\N	\N	f	77610	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0115114003||None||False	f	t	t
MEMSCAP REGPT	FR0010298620	EUR	1	|EURONEXT|	f	77637	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010298620||fr||False	f	t	t
Altera corporation	US0214411003	USD	1	|NASDAQ100|SP500|	f	77552					100	c	0	2	ALTR	{1}	{3}	ALTR||us||False	f	t	t
Colony Financial Inc.	\N	USD	1	\N	f	77620	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CLNY||us||False	f	t	t
DENTSPLY International Inc.	US2490301072	USD	1	|NASDAQ100|	f	77606	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	XRAY||us||False	f	t	t
Sears Holdings Corporation	\N	USD	1	|NASDAQ100|	f	77608	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	SHLD||us||False	f	t	t
Vodafone Group plc	\N	USD	1	|NASDAQ100|	f	77629	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	VOD||us||False	f	t	t
Joy Global, Inc.	\N	USD	1	|NASDAQ100|	f	77635	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	JOYG||us||False	f	t	t
Gray Television Inc.	\N	USD	1	\N	f	77621	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GTN||us||False	f	t	t
Noah Holdings Ltd.	\N	USD	1	\N	f	77622	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NOAH||us||False	f	t	t
Taomee Holdings Ltd.	\N	USD	1	\N	f	77623	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TAOM||us||False	f	t	t
Xerium Technologies Inc.	\N	USD	1	\N	f	77624	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#XRM||us||False	f	t	t
Carriage Services Inc.	\N	USD	1	\N	f	77625	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CSV||us||False	f	t	t
Enzo Biochem Inc.	\N	USD	1	\N	f	77626	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ENZ||us||False	f	t	t
Ventas Inc.	\N	USD	1	\N	f	77640	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VTR||us||False	f	t	t
BCE Inc.	\N	USD	1	\N	f	77642	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BCE||us||False	f	t	t
Wendy's Co.	\N	USD	1	\N	f	77644	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WEN||us||False	f	t	t
AKKA TECHNOLOGIES	FR0004180537	EUR	1	|EURONEXT|	f	77681	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004180537||fr||False	f	t	t
AKZO NOBEL	NL0000009132	EUR	1	|EURONEXT|	f	77682	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000009132||nl||False	f	t	t
ARCADIS	NL0006237562	EUR	1	|EURONEXT|	f	77696	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0006237562||nl||False	f	t	t
Peabody Energy Corp.	\N	USD	1	\N	f	77646	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BTU||us||False	f	t	t
Teradata Corp.	\N	USD	1	\N	f	77650	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TDC||us||False	f	t	t
First Majestic Silver Corp.	\N	USD	1	\N	f	77651	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AG||us||False	f	t	t
HudBay Minerals Inc.	\N	USD	1	\N	f	77652	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HBM||us||False	f	t	t
Life Time Fitness Inc.	\N	USD	1	\N	f	77653	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LTM||us||False	f	t	t
Washington Real Estate Investment Trust	\N	USD	1	\N	f	77654	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WRE||us||False	f	t	t
Cinemark Holdings Inc.	\N	USD	1	\N	f	77655	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CNK||us||False	f	t	t
Fairchild Semiconductor International Inc.	\N	USD	1	\N	f	77657	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FCS||us||False	f	t	t
Lennox International Inc.	\N	USD	1	\N	f	77659	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LII||us||False	f	t	t
Resolute Energy Corp.	\N	USD	1	\N	f	77672	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#REN||us||False	f	t	t
Rosetta Stone Inc.	\N	USD	1	\N	f	77673	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RST||us||False	f	t	t
China Cord Blood Corp.	\N	USD	1	\N	f	77674	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CO||us||False	f	t	t
Nautilus Inc.	\N	USD	1	\N	f	77675	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NLS||us||False	f	t	t
Furniture Brands International Inc.	\N	USD	1	\N	f	77676	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FBN||us||False	f	t	t
Medco Health Solutions Inc.	\N	USD	1	\N	f	77679	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MHS||us||False	f	t	t
Las Vegas Sands Corp.	\N	USD	1	\N	f	77680	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LVS||us||False	f	t	t
Cameco Corp.	\N	USD	1	\N	f	77687	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CCJ||us||False	f	t	t
Albemarle Corp.	\N	USD	1	\N	f	77688	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ALB||us||False	f	t	t
Philippine Long Distance Telephone Co.	\N	USD	1	\N	f	77692	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PHI||us||False	f	t	t
Leucadia National Corp.	\N	USD	1	\N	f	77694	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LUK||us||False	f	t	t
LG Display Co. Ltd.	\N	USD	1	\N	f	77697	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LPL||us||False	f	t	t
AURES TECHNOLOGIES	FR0000073827	EUR	1	|EURONEXT|	f	77699	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000073827||fr||False	f	t	t
AUSYBSA15OCT15	FR0010505941	EUR	1	|EURONEXT|	f	77703	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010505941||fr||False	f	t	t
EULER HERMES NV	FR0010978783	EUR	1	|EURONEXT|	f	77708	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010978783||fr||False	f	t	t
EUROFINS SCIENT NV	FR0010989780	EUR	1	|EURONEXT|	f	77709	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010989780||fr||False	f	t	t
IEC PROFES.MEDIA	FR0000066680	EUR	1	|EURONEXT|	f	77717	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000066680||fr||False	f	t	t
CYBERDECK	FR0004154151	EUR	1	|EURONEXT|	f	77723	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004154151||fr||False	f	t	t
TOREADOR RESOURCES	US8910501068	EUR	1	|EURONEXT|	f	77726	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US8910501068||fr||False	f	t	t
AFONE	FR0000044612	EUR	1	|EURONEXT|	f	77727	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000044612||fr||False	f	t	t
ARKEMA	FR0010313833	EUR	1	|EURONEXT|	f	77731	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010313833||fr||False	f	t	t
ARTPRICE COM	FR0000074783	EUR	1	|EURONEXT|	f	77735	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000074783||fr||False	f	t	t
I.R.I.S  GROUP	BE0003756708	EUR	1	|EURONEXT|	f	77716	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003756708||be||False	f	t	t
ATRIUM EUR REALEST	JE00B3DCF752	EUR	1	|EURONEXT|	f	77698	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#JE00B3DCF752||nl||False	f	t	t
HOLLAND COLOURS	NL0000440311	EUR	1	|EURONEXT|	f	77715	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000440311||nl||False	f	t	t
Luxottica Group S.p.A.	\N	USD	1	\N	f	77706	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LUX||us||False	f	t	t
Lear Corp.	\N	USD	1	\N	f	77710	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LEA||us||False	f	t	t
Telephone & Data Systems Inc.	\N	USD	1	\N	f	77713	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TDS||us||False	f	t	t
Higher One Holdings Inc.	\N	USD	1	\N	f	77718	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ONE||us||False	f	t	t
Morton's Restaurant Group Inc.	\N	USD	1	\N	f	77719	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MRT||us||False	f	t	t
Natuzzi S.p.A.	\N	USD	1	\N	f	77720	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NTZ||us||False	f	t	t
Sparton Corp.	\N	USD	1	\N	f	77721	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SPA||us||False	f	t	t
Orbitz Worldwide Inc.	\N	USD	1	\N	f	77722	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OWW||us||False	f	t	t
Occidental Petroleum Corp.	\N	USD	1	\N	f	77725	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OXY||us||False	f	t	t
Waters Corp.	\N	USD	1	\N	f	77732	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WAT||us||False	f	t	t
McCormick & Co. Inc.	\N	USD	1	\N	f	77733	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MKC||us||False	f	t	t
Omnicare Inc.	\N	USD	1	\N	f	77734	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OCR||us||False	f	t	t
U.S. Cellular Corp.	\N	USD	1	\N	f	79575	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#USM||us||False	f	t	t
B.COM.PORTUGUES	PTBCP0AM0007	EUR	1	|EURONEXT|	f	77767	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTBCP0AM0007||pt||False	f	t	t
BCI NAVIGATION	FR0000076192	EUR	1	|EURONEXT|	f	77768	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000076192||fr||False	f	t	t
ARSEUS TEMP.(D)	BE0380320805	EUR	1	|EURONEXT|	f	77738	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0380320805||be||False	f	t	t
BIOTECH (PRICAF)	BE0003795128	EUR	1	|EURONEXT|	f	77771	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003795128||be||False	f	t	t
BEKAERT (D)	BE0974258874	EUR	1	|EURONEXT|	f	77774	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0974258874||be||False	f	t	t
BELGACOM	BE0003810273	EUR	1	|EURONEXT|	f	77776	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003810273||be||False	f	t	t
NYRSTAR (D)	BE0003876936	EUR	1	|EURONEXT|	f	77778	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003876936||be||False	f	t	t
Dolby Laboratories Inc. Cl A	\N	USD	1	\N	f	77741	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DLB||us||False	f	t	t
Tenneco Inc.	\N	USD	1	\N	f	77742	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TEN||us||False	f	t	t
Sturm Ruger & Co.	\N	USD	1	\N	f	77743	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RGR||us||False	f	t	t
Asbury Automotive Group Inc.	\N	USD	1	\N	f	77744	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ABG||us||False	f	t	t
Sauer-Danfoss Inc.	\N	USD	1	\N	f	77745	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SHS||us||False	f	t	t
Griffon Corp.	\N	USD	1	\N	f	77746	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GFF||us||False	f	t	t
Nordion Inc.	\N	USD	1	\N	f	77747	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NDZ||us||False	f	t	t
Meadowbrook Insurance Group Inc.	\N	USD	1	\N	f	77748	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MIG||us||False	f	t	t
Emeritus Corp.	\N	USD	1	\N	f	77759	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ESC||us||False	f	t	t
Modine Manufacturing Co.	\N	USD	1	\N	f	77760	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MOD||us||False	f	t	t
OfficeMax Inc.	\N	USD	1	\N	f	77761	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OMX||us||False	f	t	t
Gerber Scientific Inc.	\N	USD	1	\N	f	77769	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GRB||us||False	f	t	t
Corporate Office Properties Trust	\N	USD	1	\N	f	77775	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OFC||us||False	f	t	t
Celestica Inc.	\N	USD	1	\N	f	77777	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CLS||us||False	f	t	t
South Jersey Industries Inc.	\N	USD	1	\N	f	77779	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SJI||us||False	f	t	t
GNC Holdings Inc. Cl A	\N	USD	1	\N	f	77780	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GNC||us||False	f	t	t
Lumber Liquidators Holdings Inc.	\N	USD	1	\N	f	77781	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LL||us||False	f	t	t
TECHNIP NV	FR0010980318	EUR	1	|EURONEXT|	f	77783	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010980318||fr||False	f	t	t
EULER HERMES	FR0004254035	EUR	1	|EURONEXT|	f	77821	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004254035||fr||False	f	t	t
ELIA STRIP	BE0005597688	EUR	1	|EURONEXT|	f	77820	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005597688||be||False	f	t	t
Getty Realty Corp.	\N	USD	1	\N	f	77782	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GTY||us||False	f	t	t
ENI S.p.A.	\N	USD	1	\N	f	77784	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#E||us||False	f	t	t
Enbridge Inc.	\N	USD	1	\N	f	77786	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ENB||us||False	f	t	t
Travelers Cos. Inc.	\N	USD	1	\N	f	77787	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TRV||us||False	f	t	t
National Presto Industries Inc.	\N	USD	1	\N	f	77788	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NPK||us||False	f	t	t
Northstar Realty Finance Corp.	\N	USD	1	\N	f	77789	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NRF||us||False	f	t	t
Thomson Reuters Corp.	\N	USD	1	\N	f	77790	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TRI||us||False	f	t	t
Orix Corp.	\N	USD	1	\N	f	77791	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IX||us||False	f	t	t
Fluor Corp.	\N	USD	1	\N	f	77792	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FLR||us||False	f	t	t
Universal Health Realty Income Trust	\N	USD	1	\N	f	77793	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UHT||us||False	f	t	t
Maidenform Brands Inc.	\N	USD	1	\N	f	77794	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MFB||us||False	f	t	t
Skechers USA Inc. Cl A	\N	USD	1	\N	f	77800	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SKX||us||False	f	t	t
Giant Interactive Group Inc.	\N	USD	1	\N	f	77801	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GA||us||False	f	t	t
John Bean Technologies Corp.	\N	USD	1	\N	f	77802	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JBT||us||False	f	t	t
Select Medical Holdings Corp.	\N	USD	1	\N	f	77803	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SEM||us||False	f	t	t
Yingli Green Energy Holding Co. Ltd.	\N	USD	1	\N	f	77804	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#YGE||us||False	f	t	t
Harte-Hanks Inc.	\N	USD	1	\N	f	77805	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HHS||us||False	f	t	t
Skyline Corp.	\N	USD	1	\N	f	77806	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SKY||us||False	f	t	t
FirstEnergy Corp.	\N	USD	1	\N	f	77810	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FE||us||False	f	t	t
Canadian Pacific Railway Ltd.	\N	USD	1	\N	f	77816	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CP||us||False	f	t	t
Cooper Industries PLC Cl A	\N	USD	1	\N	f	77818	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CBE||us||False	f	t	t
Smith & Nephew PLC	\N	USD	1	\N	f	77819	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SNN||us||False	f	t	t
Forest Laboratories Inc.	\N	USD	1	\N	f	77822	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FRX||us||False	f	t	t
SARTORIUS NV	FR0010999466	EUR	1	|EURONEXT|	f	77826	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010999466||fr||False	f	t	t
EURAZEO	FR0000121121	EUR	1	|EURONEXT|	f	77827	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000121121||fr||False	f	t	t
EURO DISNEY	FR0010540740	EUR	1	|EURONEXT|	f	77828	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010540740||fr||False	f	t	t
EUTELSAT COMMUNIC.	FR0010221234	EUR	1	|EURONEXT|	f	77830	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010221234||fr||False	f	t	t
ORAPI	FR0000075392	EUR	1	|EURONEXT|	f	77840	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000075392||fr||False	f	t	t
MICHELIN NV	FR0010981985	EUR	1	|EURONEXT|	f	77841	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010981985||fr||False	f	t	t
Call IBEX 35 | 11250 € | 17/02/12 | B9708	FR0011083872	EUR	5	|SGW|	f	77852	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9708||fr||False	f	t	t
Call IBEX 35 | 11750 € | 17/02/12 | B9709	FR0011083880	EUR	5	|SGW|	f	77854	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9709||fr||False	f	t	t
INTERVEST OFF-WARE	BE0003746600	EUR	1	|EURONEXT|	f	77837	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003746600||be||False	f	t	t
PAIRI DAIZA	BE0003771855	EUR	1	|EURONEXT|	f	77849	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003771855||be||False	f	t	t
GENERAL ELECT.CERT	BE0004609500	EUR	1	|EURONEXT|	f	77857	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0004609500||be||False	f	t	t
Dun & Bradstreet Corp.	\N	USD	1	\N	f	77823	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DNB||us||False	f	t	t
Alcatel-Lucent	\N	USD	1	\N	f	77831	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ALU||us||False	f	t	t
D.R. Horton Inc.	\N	USD	1	\N	f	77833	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DHI||us||False	f	t	t
Valassis Communications Inc.	\N	USD	1	\N	f	77834	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VCI||us||False	f	t	t
Glimcher Realty Trust	\N	USD	1	\N	f	77835	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GRT||us||False	f	t	t
KAR Auction Services Inc.	\N	USD	1	\N	f	77842	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KAR||us||False	f	t	t
Kennedy-Wilson Holdings Inc.	\N	USD	1	\N	f	77843	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KW||us||False	f	t	t
Myers Industries Inc.	\N	USD	1	\N	f	77844	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MYE||us||False	f	t	t
STR Holdings Inc.	\N	USD	1	\N	f	77845	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STRI||us||False	f	t	t
Resource Capital Corp.	\N	USD	1	\N	f	77847	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RSO||us||False	f	t	t
Superior Industries International Inc.	\N	USD	1	\N	f	77848	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SUP||us||False	f	t	t
BLYTH Inc.	\N	USD	1	\N	f	79784	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BTH||us||False	f	t	t
LE NOBLE AGE	FR0004170017	EUR	1	|EURONEXT|	f	77861	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004170017||fr||False	f	t	t
LEBON	FR0000121295	EUR	1	|EURONEXT|	f	77862	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000121295||fr||False	f	t	t
LINEDATA SERVICES	FR0004156297	EUR	1	|EURONEXT|	f	77864	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004156297||fr||False	f	t	t
PPR NV	FR0010988808	EUR	1	|EURONEXT|	f	77866	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010988808||fr||False	f	t	t
VIEL ET COMPAGNIE	FR0000050049	EUR	1	|EURONEXT|	f	77868	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000050049||fr||False	f	t	t
VILMORIN & CIE	FR0000052516	EUR	1	|EURONEXT|	f	77870	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000052516||fr||False	f	t	t
M.R.M	FR0000060196	EUR	1	|EURONEXT|	f	77876	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060196||fr||False	f	t	t
PROCTER GAMBLE	US7427181091	EUR	1	|EURONEXT|	f	77890	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US7427181091||fr||False	f	t	t
DAMARTEX	FR0000185423	EUR	1	|EURONEXT|	f	77896	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000185423||fr||False	f	t	t
Call IBEX 35 | 6500 € | 16/03/12 | C1099	FR0011124049	EUR	5	|SGW|	f	77897	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1099||fr||False	f	t	t
Sims Metal Management Ltd.	\N	USD	1	\N	f	77858	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SMS||us||False	f	t	t
Wesco International Inc.	\N	USD	1	\N	f	77859	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WCC||us||False	f	t	t
Cytec Industries Inc.	\N	USD	1	\N	f	77860	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CYT||us||False	f	t	t
Alleghany Corp.	\N	USD	1	\N	f	77874	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#Y||us||False	f	t	t
Carpenter Technology Corp.	\N	USD	1	\N	f	77875	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CRS||us||False	f	t	t
City National Corp.	\N	USD	1	\N	f	77877	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CYN||us||False	f	t	t
DeVry Inc.	\N	USD	1	\N	f	77878	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DV||us||False	f	t	t
Commercial Metals Co.	\N	USD	1	\N	f	77879	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CMC||us||False	f	t	t
Dupont Fabros Technology Inc.	\N	USD	1	\N	f	77887	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DFT||us||False	f	t	t
Insperity Inc.	\N	USD	1	\N	f	77888	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NSP||us||False	f	t	t
PHH Corp.	\N	USD	1	\N	f	77889	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PHH||us||False	f	t	t
American Assets Trust Inc.	\N	USD	1	\N	f	77893	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AAT||us||False	f	t	t
Horace Mann Educators Corp.	\N	USD	1	\N	f	77894	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HMN||us||False	f	t	t
Quicksilver Resources Inc.	\N	USD	1	\N	f	77895	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KWK||us||False	f	t	t
Winnebago Industries Inc.	\N	USD	1	\N	f	79809	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WGO||us||False	f	t	t
BANCO SANTANDER	ES0113900J37	EUR	1	|EURONEXT|	f	77900	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#ES0113900J37||pt||False	f	t	t
BANIF-SGPS	PTBNF0AM0005	EUR	1	|EURONEXT|	f	77903	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTBNF0AM0005||pt||False	f	t	t
J.MARTINS,SGPS	PTJMT0AE0001	EUR	1	|EURONEXT|	f	77908	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTJMT0AE0001||pt||False	f	t	t
REDITUS,SGPS	PTRED0AP0010	EUR	1	|EURONEXT|	f	77919	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTRED0AP0010||pt||False	f	t	t
Call IBEX 35 | 7000 € | 16/03/12 | B9951	FR0011091404	EUR	5	|SGW|	f	77898	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9951||fr||False	f	t	t
Call IBEX 35 | 7500 € | 16/03/12 | B9952	FR0011091412	EUR	5	|SGW|	f	77899	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9952||fr||False	f	t	t
GROUPE GUILLIN	FR0000051831	EUR	1	|EURONEXT|	f	77915	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000051831||fr||False	f	t	t
EUROSIC	FR0011080357	EUR	1	|EURONEXT|	f	77918	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011080357||fr||False	f	t	t
MEDASYS	FR0000052623	EUR	1	|EURONEXT|	f	77923	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000052623||fr||False	f	t	t
MONTUPET SA	FR0000037046	EUR	1	|EURONEXT|	f	77938	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000037046||fr||False	f	t	t
MOBISTAR	BE0003735496	EUR	1	|EURONEXT|	f	77928	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003735496||be||False	f	t	t
NB PRIV EQ PARTN	GG00B1ZBD492	EUR	1	|EURONEXT|	f	77914	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GG00B1ZBD492||nl||False	f	t	t
Deere & Co.	\N	USD	1	\N	f	77997	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DE||us||False	f	t	t
MACINTOSH RETAIL	NL0000367993	EUR	1	|EURONEXT|	f	77922	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000367993||nl||False	f	t	t
Cliffs Natural Resources Inc.	\N	USD	1	\N	f	77901	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CLF||us||False	f	t	t
Aegon N.V.	\N	USD	1	\N	f	77902	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AEG||us||False	f	t	t
Whiting Petroleum Corp.	\N	USD	1	\N	f	77906	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WLL||us||False	f	t	t
Calpine Corp.	\N	USD	1	\N	f	77909	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CPN||us||False	f	t	t
Thor Industries Inc.	\N	USD	1	\N	f	77910	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#THO||us||False	f	t	t
Convergys Corp.	\N	USD	1	\N	f	77911	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CVG||us||False	f	t	t
PNM Resources Inc.	\N	USD	1	\N	f	77921	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PNM||us||False	f	t	t
UniSource Energy Corp.	\N	USD	1	\N	f	77930	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UNS||us||False	f	t	t
DCT Industrial Trust Inc.	\N	USD	1	\N	f	77931	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DCT||us||False	f	t	t
Holly Corp.	\N	USD	1	\N	f	77932	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HOC||us||False	f	t	t
Compania Cervecerias Unidas S.A.	\N	USD	1	\N	f	77933	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CCU||us||False	f	t	t
Targa Resources Corp.	\N	USD	1	\N	f	77934	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TRGP||us||False	f	t	t
Regis Corp.	\N	USD	1	\N	f	77935	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RGS||us||False	f	t	t
BankUnited Inc.	\N	USD	1	\N	f	77936	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BKU||us||False	f	t	t
TEIXEIRA DUARTE	PTTD10AM0000	EUR	1	|EURONEXT|	f	77964	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTTD10AM0000||pt||False	f	t	t
BASTIDE LE CONFORT	FR0000035370	EUR	1	|EURONEXT|	f	77945	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000035370||fr||False	f	t	t
STILFONTEIN GOLD	ZAU000008930	EUR	1	|EURONEXT|	f	77951	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#ZAU000008930||fr||False	f	t	t
STORE ELECTRONICS	FR0010282822	EUR	1	|EURONEXT|	f	77952	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010282822||fr||False	f	t	t
TECHNOFAN	FR0000065450	EUR	1	|EURONEXT|	f	77954	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000065450||fr||False	f	t	t
Put IBEX 35 | 7750 € | 20/04/12 | C1111	FR0011124163	EUR	5	|SGW|	f	77955	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1111||fr||False	f	t	t
Put IBEX 35 | 8250 € | 20/04/12 | C1112	FR0011124171	EUR	5	|SGW|	f	77958	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1112||fr||False	f	t	t
Put IBEX 35 | 8750 € | 20/04/12 | C1113	FR0011124189	EUR	5	|SGW|	f	77961	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1113||fr||False	f	t	t
SIPAREX CROISSANCE	FR0000061582	EUR	1	|EURONEXT|	f	77965	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000061582||fr||False	f	t	t
SCHAEFFER DUFOUR	FR0011089473	EUR	1	|EURONEXT|	f	77966	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011089473||fr||False	f	t	t
BANIMMO A (D)	BE0003870871	EUR	1	|EURONEXT|	f	77944	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003870871||be||False	f	t	t
ROSIER	BE0003575835	EUR	1	|EURONEXT|	f	77947	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003575835||be||False	f	t	t
UNISYS	US9092143067	EUR	1	|EURONEXT|	f	77946	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#US9092143067||nl||False	f	t	t
BDI - BioEnergy International AG	AT0000A02177	EUR	1	|DEUTSCHEBOERSE|	f	77948	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#AT0000A02177||de||False	f	t	t
Noah Education Holdings Ltd.	\N	USD	1	\N	f	77939	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NED||us||False	f	t	t
China Hydroelectric Corp.	\N	USD	1	\N	f	77940	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CHC||us||False	f	t	t
Daqo New Energy Corp.	\N	USD	1	\N	f	77941	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DQ||us||False	f	t	t
Vale S.A.	\N	USD	1	\N	f	77942	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VALE||us||False	f	t	t
France Telecom	\N	USD	1	\N	f	77943	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FTE||us||False	f	t	t
Unit Corp.	\N	USD	1	\N	f	77953	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UNT||us||False	f	t	t
Compass Diversified Holdings	\N	USD	1	\N	f	77956	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CODI||us||False	f	t	t
TreeHouse Foods Inc.	\N	USD	1	\N	f	77960	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#THS||us||False	f	t	t
Sappi Ltd.	\N	USD	1	\N	f	77963	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SPP||us||False	f	t	t
Grupo Aeroportuario del Sureste S.A.B. de C.V.	\N	USD	1	\N	f	77969	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ASR||us||False	f	t	t
Cash America International Inc.	\N	USD	1	\N	f	77970	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CSH||us||False	f	t	t
Call IBEX 35 | 11000 € | 15/06/12 | B9963	FR0011091529	EUR	5	|SGW|	f	77989	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9963||fr||False	f	t	t
Put IBEX 35 | 7000 € | 15/06/12 | B9966	FR0011091552	EUR	5	|SGW|	f	77990	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9966||fr||False	f	t	t
Put IBEX 35 | 9000 € | 15/06/12 | B9970	FR0011091594	EUR	5	|SGW|	f	77994	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9970||fr||False	f	t	t
VISIODENT	FR0000065765	EUR	1	|EURONEXT|	f	77996	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000065765||fr||False	f	t	t
BONGRAIN	FR0000120107	EUR	1	|EURONEXT|	f	77999	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000120107||fr||False	f	t	t
VIVALIS	FR0004056851	EUR	1	|EURONEXT|	f	78001	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004056851||fr||False	f	t	t
BOURBON	FR0004548873	EUR	1	|EURONEXT|	f	78002	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004548873||fr||False	f	t	t
TONNA ELECTRONIQUE	FR0000064388	EUR	1	|EURONEXT|	f	78003	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064388||fr||False	f	t	t
TELENET GROUP	BE0003826436	EUR	1	|EURONEXT|	f	77973	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003826436||be||False	f	t	t
BOSKALIS WESTMIN	NL0000852580	EUR	1	|EURONEXT|	f	78000	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000852580||nl||False	f	t	t
 RIB Software AG	DE000A0Z2XN6	EUR	1	|DEUTSCHEBOERSE|	f	77992	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0Z2XN6||de||False	f	t	t
EastGroup Properties Inc.	\N	USD	1	\N	f	77974	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EGP||us||False	f	t	t
Northwest Natural Gas Co.	\N	USD	1	\N	f	77975	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NWN||us||False	f	t	t
Gulfmark Offshore Inc. (Cl A)	\N	USD	1	\N	f	77976	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GLF||us||False	f	t	t
AZZ Inc.	\N	USD	1	\N	f	77979	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AZZ||us||False	f	t	t
Wabash National Corp.	\N	USD	1	\N	f	77980	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WNC||us||False	f	t	t
Quantum Corp.	\N	USD	1	\N	f	77981	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#QTM||us||False	f	t	t
Exterran Holdings Inc.	\N	USD	1	\N	f	77986	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EXH||us||False	f	t	t
Comstock Resources Inc.	\N	USD	1	\N	f	77987	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CRK||us||False	f	t	t
China New Borun Corp.	\N	USD	1	\N	f	77988	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BORN||us||False	f	t	t
Unilever N.V.	\N	USD	1	\N	f	77991	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UN||us||False	f	t	t
E.I. DuPont de Nemours & Co.	\N	USD	1	\N	f	77993	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DD||us||False	f	t	t
Unilever PLC	\N	USD	1	\N	f	77995	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UL||us||False	f	t	t
WellCare Health Plans Inc.	\N	USD	1	\N	f	78005	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WCG||us||False	f	t	t
NeuStar Inc. Cl A	\N	USD	1	\N	f	78006	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NSR||us||False	f	t	t
Alexander's Inc.	\N	USD	1	\N	f	78013	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ALX||us||False	f	t	t
LAPERWOBR30DEC11	FR0010670406	EUR	1	|EURONEXT|	f	78019	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010670406||fr||False	f	t	t
Call IBEX 35 | 10500 € | 15/06/12 | B9962	FR0011091511	EUR	5	|SGW|	f	78021	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9962||fr||False	f	t	t
Carmignac Profil Réactif 75	FR0010148999	EUR	2	|CARMIGNAC|	f	78036	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	FR0010148999||fr||False	f	t	t
HAVBSAAR2013	FR0010355644	EUR	1	|EURONEXT|	f	78038	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010355644||fr||False	f	t	t
LVLBSAAR2015	FR0010617027	EUR	1	|EURONEXT|	f	78042	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010617027||fr||False	f	t	t
SOFIBUS PATRIMOINE	FR0000038804	EUR	1	|EURONEXT|	f	78043	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000038804||fr||False	f	t	t
Chemtura Corp.	\N	USD	1	\N	f	78028	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CHMT||us||False	f	t	t
Grupo Aeroportuario del Pacifico S.A.B. de C.V.	\N	USD	1	\N	f	78029	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PAC||us||False	f	t	t
Imax Corp.	\N	USD	1	\N	f	78030	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IMAX||us||False	f	t	t
SYNNEX Corp.	\N	USD	1	\N	f	78031	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SNX||us||False	f	t	t
Boston Beer Co. Cl A	\N	USD	1	\N	f	78032	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SAM||us||False	f	t	t
SINOPEC Shanghai Petrochemical Co. Ltd.	\N	USD	1	\N	f	78033	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SHI||us||False	f	t	t
Lentuo International Inc.	\N	USD	1	\N	f	78034	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LAS||us||False	f	t	t
Wal-Mart Stores Inc.	\N	USD	1	\N	f	78035	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WMT||us||False	f	t	t
Deutsche Bank AG	\N	USD	1	\N	f	78037	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DB||us||False	f	t	t
Mizuho Financial Group Inc.	\N	USD	1	\N	f	78039	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MFG||us||False	f	t	t
Call IBEX 35 | 11000 € | 20/12/13 | B7864	FR0011065671	EUR	5	|SGW|	f	78045	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7864||fr||False	f	t	t
Call IBEX 35 | 9000 € | 19/12/14 | C3306	FR0011168467	EUR	5	|SGW|	f	78048	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3306||fr||False	f	t	t
SOFT COMPUTING	FR0000075517	EUR	1	|EURONEXT|	f	78053	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000075517||fr||False	f	t	t
SOGECLAIR	FR0000065864	EUR	1	|EURONEXT|	f	78058	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000065864||fr||False	f	t	t
Carmignac Profil Reactif 100	FR0010149211	EUR	2	|CARMIGNAC|	f	78066	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	FR0010149211||fr||False	f	t	t
TURBO Put IBEX 35 | 12000 € | 17/06/11 | 54849	FR0011003334	EUR	5	|SGW|	f	78067	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54849||fr||False	f	t	t
Call IBEX 35 inLine | 9500 € | 17/06/11 | I0022	FR0011002344	EUR	5	|SGW|	f	78068	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0022||fr||False	f	t	t
TURBO Call IBEX 35 | 9750 € | 17/06/11 | 54833	FR0011003177	EUR	5	|SGW|	f	78070	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#54833||fr||False	f	t	t
SOFINA	BE0003717312	EUR	1	|EURONEXT|	f	78051	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003717312||be||False	f	t	t
VERTICE 360	ES0183304312	EUR	1	|MERCADOCONTINUO|	f	78063	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0183304312||es||False	f	t	t
Manulife Financial Corp.	\N	USD	1	\N	f	78046	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MFC||us||False	f	t	t
Teck Resources Ltd.	\N	USD	1	\N	f	78047	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TCK||us||False	f	t	t
Northeast Utilities	\N	USD	1	\N	f	78049	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NU||us||False	f	t	t
Jacobs Engineering Group Inc.	\N	USD	1	\N	f	78052	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JEC||us||False	f	t	t
Autoliv Inc.	\N	USD	1	\N	f	78054	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ALV||us||False	f	t	t
Masco Corp.	\N	USD	1	\N	f	78055	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MAS||us||False	f	t	t
Georgia Gulf Corp.	\N	USD	1	\N	f	78057	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GGC||us||False	f	t	t
Meredith Corp.	\N	USD	1	\N	f	78059	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MDP||us||False	f	t	t
Zuoan Fashion Ltd.	\N	USD	1	\N	f	78062	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ZA||us||False	f	t	t
Central Pacific Financial Corp.	\N	USD	1	\N	f	78064	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CPF||us||False	f	t	t
CPI Corp.	\N	USD	1	\N	f	78065	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CPY||us||False	f	t	t
BRISA	PTBRI0AM0000	EUR	1	|EURONEXT|	f	78077	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTBRI0AM0000||pt||False	f	t	t
U10	FR0000079147	EUR	1	|EURONEXT|	f	78072	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000079147||fr||False	f	t	t
WEATHERFORD	CH0038838394	EUR	1	|EURONEXT|	f	78080	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#CH0038838394||fr||False	f	t	t
AXWAY SOFTWARE DS	FR0011070135	EUR	1	|EURONEXT|	f	78101	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011070135||fr||False	f	t	t
NEOPOST NV	FR0010999474	EUR	1	|EURONEXT|	f	78103	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010999474||fr||False	f	t	t
WDP-SICAFI	BE0003763779	EUR	1	|EURONEXT|	f	78079	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003763779||be||False	f	t	t
AB INBEV STR VVPR	BE0005582532	EUR	1	|EURONEXT|	f	78104	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005582532||be||False	f	t	t
BQUE NAT. BELGIQUE	BE0003008019	EUR	1	|EURONEXT|	f	78107	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003008019||be||False	f	t	t
3W POWER	GG00B39QCR01	EUR	1	|EURONEXT|	f	78088	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GG00B39QCR01||nl||False	f	t	t
3W POWERC0712	GG00B39QCZ84	EUR	1	|EURONEXT|	f	78095	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GG00B39QCZ84||nl||False	f	t	t
MANAGEMENT SHARE	NL0000440253	EUR	1	|EURONEXT|	f	78102	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000440253||nl||False	f	t	t
Epigenomics AG	DE000A0BVT96	EUR	1	|DEUTSCHEBOERSE|	f	78100	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0BVT96||de||False	f	t	t
NAME	\N	USD	1	\N	f	78082	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TICKER||us||False	f	t	t
Target Corp.	\N	USD	1	\N	f	78084	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TGT||us||False	f	t	t
Danaher Corp.	\N	USD	1	\N	f	78085	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DHR||us||False	f	t	t
FedEx Corp.	\N	USD	1	\N	f	78086	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FDX||us||False	f	t	t
Marathon Oil Corp.	\N	USD	1	\N	f	78087	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MRO||us||False	f	t	t
China Petroleum & Chemical Corp.	\N	USD	1	\N	f	78090	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SNP||us||False	f	t	t
McKesson Corp.	\N	USD	1	\N	f	78096	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MCK||us||False	f	t	t
BRASSERIE CAMEROUN	CM0000035113	EUR	1	|EURONEXT|	f	78109	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#CM0000035113||fr||False	f	t	t
BUREAU VERITAS NV	FR0011169820	EUR	1	|EURONEXT|	f	78128	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011169820||fr||False	f	t	t
Desarrolladora Homex S.A.B. de C.V.	\N	USD	1	\N	f	78199	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HXM||us||False	f	t	t
American Express Co.		USD	1	|SP500|	f	78083					100	c	0	2	AXP	{1}	{3}	NYSE#AXP||us||False	f	t	t
MB RETAIL EUROPE	FR0000061475	EUR	1	|EURONEXT|	f	78149	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000061475||fr||False	f	t	t
BREDERODE	BE0003792091	EUR	1	|EURONEXT|	f	78111	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003792091||be||False	f	t	t
INTERV.RETAIL-SIFI	BE0003754687	EUR	1	|EURONEXT|	f	78138	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003754687||be||False	f	t	t
MEDIVISION	IL0010846314	EUR	1	|EURONEXT|	f	78150	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#IL0010846314||be||False	f	t	t
BRILL KON	NL0000442523	EUR	1	|EURONEXT|	f	78115	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000442523||nl||False	f	t	t
FleetCor Technologies Inc.	\N	USD	1	\N	f	78113	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FLT||us||False	f	t	t
Sonic Automotive Inc. Cl A	\N	USD	1	\N	f	78114	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SAH||us||False	f	t	t
Dover Motorsports Inc.	\N	USD	1	\N	f	78116	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DVD||us||False	f	t	t
Global Ship Lease Inc. Cl A	\N	USD	1	\N	f	78119	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GSL||us||False	f	t	t
WSP Holdings Ltd.	\N	USD	1	\N	f	78120	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WH||us||False	f	t	t
CAIXANOVA A AHORRO	ES0115082036	EUR	2	|BMF|0128|	f	78081	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115082036||es||False	f	t	t
Rio Tinto PLC	\N	USD	1	\N	f	78121	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RIO||us||False	f	t	t
Raytheon Co.	\N	USD	1	\N	f	78124	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RTN||us||False	f	t	t
PPL Corp.	\N	USD	1	\N	f	78125	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PPL||us||False	f	t	t
Vornado Realty Trust	\N	USD	1	\N	f	78131	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VNO||us||False	f	t	t
BRF-Brazil Foods S/A	\N	USD	1	\N	f	78132	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BRFS||us||False	f	t	t
Omnicom Group Inc.	\N	USD	1	\N	f	78134	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OMC||us||False	f	t	t
Charles Schwab Corp.	\N	USD	1	\N	f	78135	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SCHW||us||False	f	t	t
Kohl's Corp.	\N	USD	1	\N	f	78136	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KSS||us||False	f	t	t
Pebblebrook Hotel Trust	\N	USD	1	\N	f	78137	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PEB||us||False	f	t	t
AK Steel Holding Corp.	\N	USD	1	\N	f	78151	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AKS||us||False	f	t	t
Tyler Technologies Inc.	\N	USD	1	\N	f	78152	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TYL||us||False	f	t	t
Penske Automotive Group Inc.	\N	USD	1	\N	f	78155	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PAG||us||False	f	t	t
MICROPOLE	FR0000077570	EUR	1	|EURONEXT|	f	78153	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000077570||fr||False	f	t	t
ALTEN	FR0000071946	EUR	1	|EURONEXT|	f	78180	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000071946||fr||False	f	t	t
MIKO	BE0003731453	EUR	1	|EURONEXT|	f	78154	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003731453||be||False	f	t	t
ABLYNX STR VVPR(D)	BE0005620910	EUR	1	|EURONEXT|	f	78164	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005620910||be||False	f	t	t
ACCENTIS STRIP (D)	BE0005641155	EUR	1	|EURONEXT|	f	78165	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005641155||be||False	f	t	t
ACKERMANS STRIP	BE0005562336	EUR	1	|EURONEXT|	f	78168	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005562336||be||False	f	t	t
Arbitron Inc.	\N	USD	1	\N	f	78157	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ARB||us||False	f	t	t
Oriental Financial Group Inc.	\N	USD	1	\N	f	78161	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OFG||us||False	f	t	t
\N	\N	\N	\N	\N	f	78176	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0113931002||None||False	f	t	t
American Realty Investors Inc.	\N	USD	1	\N	f	78162	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ARL||us||False	f	t	t
Transcontinental Realty Investors	\N	USD	1	\N	f	78163	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TCI||us||False	f	t	t
Chevron Corp.	\N	USD	1	\N	f	78166	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CVX||us||False	f	t	t
ConocoPhillips	\N	USD	1	\N	f	78167	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#COP||us||False	f	t	t
Bank of Nova Scotia	\N	USD	1	\N	f	78169	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BNS||us||False	f	t	t
Covidien PLC	\N	USD	1	\N	f	78170	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#COV||us||False	f	t	t
Marathon Petroleum Corp.	\N	USD	1	\N	f	78171	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MPC||us||False	f	t	t
Agrium Inc.	\N	USD	1	\N	f	78174	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AGU||us||False	f	t	t
CF Industries Holdings Inc.	\N	USD	1	\N	f	78177	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CF||us||False	f	t	t
Pioneer Natural Resources Co.	\N	USD	1	\N	f	78178	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PXD||us||False	f	t	t
Sun Life Financial Inc.	\N	USD	1	\N	f	78179	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SLF||us||False	f	t	t
Celadon Group Inc.	\N	USD	1	\N	f	80291	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CGI||us||False	f	t	t
ALTRI SGPS	PTALT0AE0002	EUR	1	|EURONEXT|	f	78182	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTALT0AE0002||pt||False	f	t	t
ARGAN	FR0010481960	EUR	1	|EURONEXT|	f	78185	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010481960||fr||False	f	t	t
BURELLE	FR0000061137	EUR	1	|EURONEXT|	f	78187	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000061137||fr||False	f	t	t
BUSINESS ET DECIS.	FR0000078958	EUR	1	|EURONEXT|	f	78192	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000078958||fr||False	f	t	t
ALPHA M.O.S. DS	FR0011073907	EUR	1	|EURONEXT|	f	78194	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011073907||fr||False	f	t	t
AVANQUEST SOFTWARE	FR0004026714	EUR	1	|EURONEXT|	f	78216	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004026714||fr||False	f	t	t
BIOALLIANCE DS	FR0011073493	EUR	1	|EURONEXT|	f	78217	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011073493||fr||False	f	t	t
BERNARD LOISEAU	FR0000066961	EUR	1	|EURONEXT|	f	78218	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000066961||fr||False	f	t	t
AVENIR TELECOM	FR0000066052	EUR	1	|EURONEXT|	f	78223	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000066052||fr||False	f	t	t
AVIATION LATECOERE	FR0000032278	EUR	1	|EURONEXT|	f	78228	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000032278||fr||False	f	t	t
BAAN	NL0000336352	EUR	1	|EURONEXT|	f	78211	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000336352||nl||False	f	t	t
BAM NON CONV PREF	NL0000337327	EUR	1	|EURONEXT|	f	78213	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000337327||nl||False	f	t	t
DXESTX5C	LU0380865021	EUR	1	|MERCADOCONTINUO|	f	78209	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0380865021||es||False	f	t	t
Iberdrola Renovables	ES0147645016	EUR	1	|MERCADOCONTINUO|	f	78175					100	c	0	1	None	\N	\N		f	t	t
ALSTOM	FR0010220475	EUR	1	|CAC|EURONEXT|	f	78172					100	c	0	3	None	\N	\N	EURONEXT#FR0010220475||fr||False	f	t	t
Motorola Mobility Holdings Inc.	\N	USD	1	\N	f	78183	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MMI||us||False	f	t	t
Southwestern Energy Co.	\N	USD	1	\N	f	78193	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SWN||us||False	f	t	t
Woori Finance Holdings Co. Ltd.	\N	USD	1	\N	f	78197	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WF||us||False	f	t	t
DXEURSTX50LE	LU0411077828	EUR	1	|MERCADOCONTINUO|	f	78227	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0411077828||es||False	f	t	t
Banco Latinoamericano de Comercio Exterior S.A. Cl E	\N	USD	1	\N	f	78200	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BLX||us||False	f	t	t
Drew Industries Inc.	\N	USD	1	\N	f	78206	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DW||us||False	f	t	t
KBW Inc.	\N	USD	1	\N	f	78207	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KBW||us||False	f	t	t
Lithia Motors Inc. Cl A	\N	USD	1	\N	f	78208	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LAD||us||False	f	t	t
Walgreen Co.	\N	USD	1	\N	f	78212	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WAG||us||False	f	t	t
Public Service Enterprise Group Inc.	\N	USD	1	\N	f	78224	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PEG||us||False	f	t	t
Host Hotels & Resorts Inc.	\N	USD	1	\N	f	78225	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HST||us||False	f	t	t
Murphy Oil Corp.	\N	USD	1	\N	f	78226	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MUR||us||False	f	t	t
BENI STABILI	IT0001389631	EUR	1	|EURONEXT|	f	78233	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#IT0001389631||fr||False	f	t	t
COFIDUR	FR0000054629	EUR	1	|EURONEXT|	f	78234	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000054629||fr||False	f	t	t
BRICORAMA	FR0000054421	EUR	1	|EURONEXT|	f	78239	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000054421||fr||False	f	t	t
MONTAIGNE FASHION	FR0004048734	EUR	1	|EURONEXT|	f	78245	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004048734||fr||False	f	t	t
BARCO	BE0003790079	EUR	1	|EURONEXT|	f	78232	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003790079||be||False	f	t	t
Chipotle Mexican Grill Inc.	\N	USD	1	\N	f	78230	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CMG||us||False	f	t	t
Juniper Networks Inc.	\N	USD	1	\N	f	78240	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JNPR||us||False	f	t	t
Xerox Corp.	\N	USD	1	\N	f	78243	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#XRX||us||False	f	t	t
China Southern Airlines Co. Ltd.	\N	USD	1	\N	f	78244	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ZNH||us||False	f	t	t
Advantage Oil & Gas Ltd.	\N	USD	1	\N	f	78246	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AAV||us||False	f	t	t
Spansion Inc. Cl A	\N	USD	1	\N	f	78247	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CODE||us||False	f	t	t
DXIBX35TRN	LU0592216393	EUR	1	|MERCADOCONTINUO|	f	78236	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0592216393||es||False	f	t	t
FAES FARMA	ES0134950F36	EUR	1	|MERCADOCONTINUO|	f	78238	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0134950F36||es||False	f	t	t
Consolidated Graphics Inc.	\N	USD	1	\N	f	78248	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CGX||us||False	f	t	t
UNIPAPEL	ES0182045312	EUR	1	|MERCADOCONTINUO|	f	78251	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0182045312||es||False	f	t	t
URBAS	ES0182280018	EUR	1	|MERCADOCONTINUO|	f	78252	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0182280018||es||False	f	t	t
Comfort Systems USA Inc.	\N	USD	1	\N	f	78255	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FIX||us||False	f	t	t
Culp Inc.	\N	USD	1	\N	f	78256	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CFI||us||False	f	t	t
\N	\N	\N	\N	\N	f	78254	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0175087008||None||False	f	t	t
HSBC Holdings PLC	\N	USD	1	\N	f	78260	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HBC||us||False	f	t	t
Walt Disney Co.	\N	USD	1	\N	f	78262	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DIS||us||False	f	t	t
Norfolk Southern Corp.	\N	USD	1	\N	f	78265	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NSC||us||False	f	t	t
International Paper Co.	\N	USD	1	\N	f	78266	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IP||us||False	f	t	t
A. LATAM TOP	ES0105304002	EUR	1	|MERCADOCONTINUO|	f	78264	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0105304002||es||False	f	t	t
Ingersoll-Rand Co. Ltd.	\N	USD	1	\N	f	78267	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IR||us||False	f	t	t
Safe Bulkers Inc.	\N	USD	1	\N	f	80425	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SB||us||False	f	t	t
ACC IBEX INV	ES0105305009	EUR	1	|MERCADOCONTINUO|	f	78272	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0105305009||es||False	f	t	t
HEINEKEN HOLDING	NL0000008977	EUR	1	|EURONEXT|	f	78294	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000008977||nl||False	f	t	t
CNIM CONSTR.FRF 10	FR0000053399	EUR	1	|EURONEXT|	f	78282	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000053399||fr||False	f	t	t
DELFINGEN	FR0000054132	EUR	1	|EURONEXT|	f	78284	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000054132||fr||False	f	t	t
DELTA PLUS GROUP	FR0004152502	EUR	1	|EURONEXT|	f	78285	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004152502||fr||False	f	t	t
GECINA NOM.	FR0010040865	EUR	1	|EURONEXT|	f	78289	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010040865||fr||False	f	t	t
GEMALTO	NL0000400653	EUR	1	|EURONEXT|	f	78291	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#NL0000400653||fr||False	f	t	t
GIFIBSAAR7 JUL15	FR0010753301	EUR	1	|EURONEXT|	f	78292	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010753301||fr||False	f	t	t
GROUPE ARES	FR0000072167	EUR	1	|EURONEXT|	f	78302	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000072167||fr||False	f	t	t
ACACIA REINVERPLUS EUROPA	ES0157934003	EUR	2	|BMF|0995|	f	78210	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157934003||es||False	f	t	t
GIFI	FR0000075095	EUR	1	|EURONEXT|	f	78304	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000075095||fr||False	f	t	t
OFI PRI EQ CAP BS1	FR0010909283	EUR	1	|EURONEXT|	f	78305	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010909283||fr||False	f	t	t
Ameron International Corp.	\N	USD	1	\N	f	78275	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AMN||us||False	f	t	t
ACC IBEX TOP	ES0105337002	EUR	1	|MERCADOCONTINUO|	f	78276	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0105337002||es||False	f	t	t
Southwest Airlines Co.	\N	USD	1	\N	f	78277	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LUV||us||False	f	t	t
Sprint Nextel Corp.	\N	USD	1	\N	f	78279	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#S||us||False	f	t	t
AXA	FR0000120628	EUR	1	|CAC|EURONEXT|EUROSTOXX|	f	78231					100	c	0	3	CS.PA	{1}	{3}	EURONEXT#FR0000120628||fr||False	f	t	t
Opko Health Inc.	\N	USD	1	\N	f	78297	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OPK||us||False	f	t	t
Provident Financial Services Inc.	\N	USD	1	\N	f	78298	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PFS||us||False	f	t	t
Newpark Resources Inc.	\N	USD	1	\N	f	78301	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NR||us||False	f	t	t
United Technologies Corp.	\N	USD	1	\N	f	78303	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UTX||us||False	f	t	t
PPG Industries Inc.	\N	USD	1	\N	f	78307	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PPG||us||False	f	t	t
CODERE	ES0119256115	EUR	1	|MERCADOCONTINUO|	f	78455	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0119256115||es||False	f	t	t
PAP.FERNANDES	PTPFE0AP0001	EUR	1	|EURONEXT|	f	78349	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTPFE0AP0001||pt||False	f	t	t
MANUTAN INTL	FR0000032302	EUR	1	|EURONEXT|	f	78308	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000032302||fr||False	f	t	t
MAROC TELECOM	MA0000011488	EUR	1	|EURONEXT|	f	78311	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#MA0000011488||fr||False	f	t	t
ORCH.KAZIBAO REGRT	FR0010160564	EUR	1	|EURONEXT|	f	78312	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010160564||fr||False	f	t	t
MANITOU BF	FR0000038606	EUR	1	|EURONEXT|	f	78337	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000038606||fr||False	f	t	t
PCB	BE0003503118	EUR	1	|EURONEXT|	f	78315	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003503118||be||False	f	t	t
CBOISSAUVWE12(1P1)	BE0006462601	EUR	1	|EURONEXT|	f	78347	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0006462601||be||False	f	t	t
AISA	ES0106585013	EUR	1	|MERCADOCONTINUO|	f	78328	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0106585013||es||False	f	t	t
\N	\N	\N	\N	\N	f	78332	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0114579008||None||False	f	t	t
ALMIRALL	ES0157097017	EUR	1	|MERCADOCONTINUO|	f	78333	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0157097017||es||False	f	t	t
Pall Corp.	\N	USD	1	\N	f	78309	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PLL||us||False	f	t	t
APERAM	LU0569974404	EUR	1	|MERCADOCONTINUO|	f	78346	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0569974404||es||False	f	t	t
Federal Realty Investment Trust	\N	USD	1	\N	f	78310	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FRT||us||False	f	t	t
Core Laboratories N.V.	\N	USD	1	\N	f	78313	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CLB||us||False	f	t	t
VeriFone Systems Inc.	\N	USD	1	\N	f	78314	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PAY||us||False	f	t	t
Foot Locker Inc.	\N	USD	1	\N	f	78320	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FL||us||False	f	t	t
Computer Sciences Corp.	\N	USD	1	\N	f	78321	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CSC||us||False	f	t	t
BRE Properties Inc.	\N	USD	1	\N	f	78329	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BRE||us||False	f	t	t
Scripps Networks Interactive Inc. Cl A	\N	USD	1	\N	f	78335	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SNI||us||False	f	t	t
Portugal Telecom SGPS S/A	\N	USD	1	\N	f	78336	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PT||us||False	f	t	t
Mid-America Apartment Communities Inc.	\N	USD	1	\N	f	78338	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MAA||us||False	f	t	t
Koppers Holdings Inc.	\N	USD	1	\N	f	78339	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KOP||us||False	f	t	t
A.F.P. Provida S.A.	\N	USD	1	\N	f	78340	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PVD||us||False	f	t	t
Crexus Investment Corp.	\N	USD	1	\N	f	78341	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CXS||us||False	f	t	t
HealthSpring Inc.	\N	USD	1	\N	f	78343	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HS||us||False	f	t	t
PepsiCo Inc.	\N	USD	1	\N	f	78344	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PEP||us||False	f	t	t
Lloyds Banking Group PLC	\N	USD	1	\N	f	78345	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LYG||us||False	f	t	t
LyondellBasell Industries N.V. Cl A	\N	USD	1	\N	f	78348	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LYB||us||False	f	t	t
CEGEDIM	FR0000053506	EUR	1	|EURONEXT|	f	78352	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000053506||fr||False	f	t	t
RADIALBSARB18JUL11	FR0010485474	EUR	1	|EURONEXT|	f	78354	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010485474||fr||False	f	t	t
REMY COINTREAU NV	FR0011062249	EUR	1	|EURONEXT|	f	78356	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011062249||fr||False	f	t	t
CEGID GROUP	FR0000124703	EUR	1	|EURONEXT|	f	78359	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000124703||fr||False	f	t	t
CFAO	FR0000060501	EUR	1	|EURONEXT|	f	78366	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060501||fr||False	f	t	t
ST DUPONT NV	FR0011047539	EUR	1	|EURONEXT|	f	78374	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011047539||fr||False	f	t	t
CFCAL BANQUE	FR0000064560	EUR	1	|EURONEXT|	f	78375	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064560||fr||False	f	t	t
ITESOFT	FR0004026151	EUR	1	|EURONEXT|	f	78376	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004026151||fr||False	f	t	t
ITS GROUP	FR0000073843	EUR	1	|EURONEXT|	f	78377	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000073843||fr||False	f	t	t
118000 AG	DE0006911902	EUR	1	|DEUTSCHEBOERSE|	f	78360	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006911902||de||False	f	t	t
3U HOLDING AG	DE0005167902	EUR	1	|DEUTSCHEBOERSE|	f	78361	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005167902||de||False	f	t	t
A.S. Création Tapeten AG	DE0005079909	EUR	1	|DEUTSCHEBOERSE|	f	78363	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005079909||de||False	f	t	t
ADC African Development Corp. GmbH & Co. KGaA	DE000A1E8NW9	EUR	1	|DEUTSCHEBOERSE|	f	78364	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1E8NW9||de||False	f	t	t
Air Berlin PLC	GB00B128C026	EUR	1	|DEUTSCHEBOERSE|	f	78367	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#GB00B128C026||de||False	f	t	t
ENSCO PLC	\N	USD	1	\N	f	78358	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ESV||us||False	f	t	t
Telecom Italia S.p.A.	\N	USD	1	\N	f	78362	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TI||us||False	f	t	t
Mobile Telesystems	\N	USD	1	\N	f	78368	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MBT||us||False	f	t	t
United Continental Holdings Inc.	\N	USD	1	\N	f	78369	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UAL||us||False	f	t	t
Capital One Financial Corp.		USD	1	|SP500|	f	78220					100	c	0	2	COF	{1}	{3}	NYSE#COF||us||False	f	t	t
AMERICA M. L	MXP001691213	EUR	1	|MERCADOCONTINUO|	f	78381	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#MXP001691213||es||False	f	t	t
AMPER	ES0109260531	EUR	1	|MERCADOCONTINUO|	f	78383	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0109260531||es||False	f	t	t
PORTUCEL	PTPTI0AM0006	EUR	1	|EURONEXT|	f	78414	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTPTI0AM0006||pt||False	f	t	t
SOITEC DS	FR0011070671	EUR	1	|EURONEXT|	f	78386	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011070671||fr||False	f	t	t
FDL	FR0000030181	EUR	1	|EURONEXT|	f	78388	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000030181||fr||False	f	t	t
ORPEA	FR0000184798	EUR	1	|EURONEXT|	f	78394	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000184798||fr||False	f	t	t
OVGBSAAR2015	FR0010681569	EUR	1	|EURONEXT|	f	78396	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010681569||fr||False	f	t	t
PERNOD RICARD NV	FR0011068865	EUR	1	|EURONEXT|	f	78397	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011068865||fr||False	f	t	t
OXYMETAL	FR0000063018	EUR	1	|EURONEXT|	f	78413	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000063018||fr||False	f	t	t
OUTREMER TELECOM	FR0010425587	EUR	1	|EURONEXT|	f	78416	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010425587||fr||False	f	t	t
OUTSIDE LIVIN IND	FR0006626032	EUR	1	|EURONEXT|	f	78417	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0006626032||fr||False	f	t	t
MEDICA	FR0010372581	EUR	1	|EURONEXT|	f	80640	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010372581||fr||False	f	t	t
OPTION (D)	BE0003836534	EUR	1	|EURONEXT|	f	78389	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003836534||be||False	f	t	t
AZKOYEN	ES0112458312	EUR	1	|MERCADOCONTINUO|	f	78398	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0112458312||es||False	f	t	t
BA. BRADESCO	BRBBDCACNPR8	EUR	1	|MERCADOCONTINUO|	f	78399	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#BRBBDCACNPR8||es||False	f	t	t
BA.PASTOR	ES0113770434	EUR	1	|MERCADOCONTINUO|	f	78402	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0113770434||es||False	f	t	t
BANCO CHILE	CLP0939W1081	EUR	1	|MERCADOCONTINUO|	f	78407	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#CLP0939W1081||es||False	f	t	t
BANESTO	ES0113440038	EUR	1	|MERCADOCONTINUO|	f	78410	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0113440038||es||False	f	t	t
CAMPOFRIO	ES0121501318	EUR	1	|MERCADOCONTINUO|	f	78415	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0121501318||es||False	f	t	t
TransCanada Corp.	\N	USD	1	\N	f	78385	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TRP||us||False	f	t	t
M&T Bank Corp.	\N	USD	1	\N	f	78387	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MTB||us||False	f	t	t
TRW Automotive Holdings Corp.	\N	USD	1	\N	f	78390	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TRW||us||False	f	t	t
Valspar Corp.	\N	USD	1	\N	f	78391	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VAL||us||False	f	t	t
Embraer S/A	\N	USD	1	\N	f	78392	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ERJ||us||False	f	t	t
Universal Health Services Inc. Cl B	\N	USD	1	\N	f	78393	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UHS||us||False	f	t	t
Strategic Hotels & Resorts Inc.	\N	USD	1	\N	f	78395	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BEE||us||False	f	t	t
Western Refining Inc.	\N	USD	1	\N	f	78400	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WNR||us||False	f	t	t
Government Properties Income Trust	\N	USD	1	\N	f	78404	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GOV||us||False	f	t	t
OM Group Inc.	\N	USD	1	\N	f	78408	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OMG||us||False	f	t	t
Banco Macro S.A.	\N	USD	1	\N	f	78409	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BMA||us||False	f	t	t
Clearwater Paper Corp.	\N	USD	1	\N	f	78411	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CLW||us||False	f	t	t
EXACOMPTA CLAIREF.	FR0000064164	EUR	1	|EURONEXT|	f	78421	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064164||fr||False	f	t	t
EXPLOS.PROD.CHI.PF	FR0000037343	EUR	1	|EURONEXT|	f	78422	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000037343||fr||False	f	t	t
EXPLOSIFS PROD.CHI	FR0000039026	EUR	1	|EURONEXT|	f	78423	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000039026||fr||False	f	t	t
CFI	FR0000037475	EUR	1	|EURONEXT|	f	78431	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000037475||fr||False	f	t	t
CGG VERITAS	FR0000120164	EUR	1	|EURONEXT|	f	78434	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000120164||fr||False	f	t	t
CHARGEURS	FR0000130692	EUR	1	|EURONEXT|	f	78436	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000130692||fr||False	f	t	t
CHAUF.URB.	FR0000052896	EUR	1	|EURONEXT|	f	78438	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000052896||fr||False	f	t	t
CHAUSSERIA	FR0000060907	EUR	1	|EURONEXT|	f	78439	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060907||fr||False	f	t	t
CFE (D)	BE0003883031	EUR	1	|EURONEXT|	f	78430	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003883031||be||False	f	t	t
CHEVRON	US1667641005	EUR	1	|EURONEXT|	f	78441	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#US1667641005||nl||False	f	t	t
AIRE GmbH & Co. KGaA	DE0006344211	EUR	1	|DEUTSCHEBOERSE|	f	78424	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006344211||de||False	f	t	t
Eli Lilly & Co.	\N	USD	1	\N	f	78425	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LLY||us||False	f	t	t
Rockwell Automation Corp.	\N	USD	1	\N	f	78426	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ROK||us||False	f	t	t
Roper Industries Inc.	\N	USD	1	\N	f	78427	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ROP||us||False	f	t	t
Regency Centers Corp.	\N	USD	1	\N	f	78428	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#REG||us||False	f	t	t
Tesoro Corp.	\N	USD	1	\N	f	78429	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TSO||us||False	f	t	t
SPX Corp.	\N	USD	1	\N	f	78432	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SPW||us||False	f	t	t
SuccessFactors Inc.	\N	USD	1	\N	f	78433	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SFSF||us||False	f	t	t
Sonoco Products Co.	\N	USD	1	\N	f	78435	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SON||us||False	f	t	t
Leggett & Platt Inc.	\N	USD	1	\N	f	78437	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LEG||us||False	f	t	t
Harry Winston Diamond Corp.	\N	USD	1	\N	f	78440	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HWD||us||False	f	t	t
Kraton Performance Polymers Inc.	\N	USD	1	\N	f	78443	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KRA||us||False	f	t	t
Anworth Mortgage Asset Corp.	\N	USD	1	\N	f	78444	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ANH||us||False	f	t	t
CEM.PORT.VAL	ES0117390411	EUR	1	|MERCADOCONTINUO|	f	78446	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0117390411||es||False	f	t	t
CEMIG P.	BRCMIGACNPR3	EUR	1	|MERCADOCONTINUO|	f	78447	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#BRCMIGACNPR3||es||False	f	t	t
Acadia Realty Trust	US0042391096	USD	1		f	78401					100	c	0	2	None	\N	\N	NYSE#AKR||us||False	f	t	t
RADIALL	FR0000050320	EUR	1	|EURONEXT|	f	78469	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000050320||fr||False	f	t	t
TURBO Put IBEX 35 | 9000 € | 16/12/11 | 55091	FR0011092154	EUR	5	|SGW|	f	78478	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#55091||fr||False	f	t	t
EGIDE DS	FR0011179993	EUR	1	|EURONEXT|	f	78481	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011179993||fr||False	f	t	t
RICOH	JP3973400009	EUR	1	|EURONEXT|	f	78482	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#JP3973400009||fr||False	f	t	t
ROUGIER S.A.	FR0000037640	EUR	1	|EURONEXT|	f	78483	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000037640||fr||False	f	t	t
TURBO Call IBEX 35 | 7000 € | 16/12/11 | 55086	FR0011092105	EUR	5	|SGW|	f	78489	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#55086||fr||False	f	t	t
TURBO Call IBEX 35 | 7500 € | 16/12/11 | 55087	FR0011092113	EUR	5	|SGW|	f	78490	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#55087||fr||False	f	t	t
GIORGIO FEDON	IT0001210050	EUR	1	|EURONEXT|	f	78499	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#IT0001210050||fr||False	f	t	t
COPEL PR.B	BRCPLEACNPB9	EUR	1	|MERCADOCONTINUO|	f	78457	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#BRCPLEACNPB9||es||False	f	t	t
CORP. ALBA	ES0117160111	EUR	1	|MERCADOCONTINUO|	f	78461	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0117160111||es||False	f	t	t
CORP. DERMO.	ES0124204019	EUR	1	|MERCADOCONTINUO|	f	78471	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0124204019||es||False	f	t	t
D. FELGUERA	ES0162600417	EUR	1	|MERCADOCONTINUO|	f	78472	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0162600417||es||False	f	t	t
DEOLEO	ES0110047919	EUR	1	|MERCADOCONTINUO|	f	78473	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0110047919||es||False	f	t	t
DECEUNINCK STVV(D)	BE0005632063	EUR	1	|EURONEXT|	f	78475	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005632063||be||False	f	t	t
ROULARTA	BE0003741551	EUR	1	|EURONEXT|	f	78486	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003741551||be||False	f	t	t
GBL	BE0003797140	EUR	1	|EURONEXT|	f	78491	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003797140||be||False	f	t	t
RBS CAP FUND TR VI	US74928M2044	EUR	1	|EURONEXT|	f	78476	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#US74928M2044||nl||False	f	t	t
ROYAL DUTCH SHELLA	GB00B03MLX29	EUR	1	|EURONEXT|	f	78492	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GB00B03MLX29||nl||False	f	t	t
AIXTRON SE	DE000A0WMPJ6	EUR	1	|DEUTSCHEBOERSE|	f	78445	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0WMPJ6||de||False	f	t	t
Generac Holdings Inc.	\N	USD	1	\N	f	78448	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GNRC||us||False	f	t	t
Cellcom Israel Ltd.	\N	USD	1	\N	f	78449	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CEL||us||False	f	t	t
McClatchy Co. Cl A	\N	USD	1	\N	f	78454	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MNI||us||False	f	t	t
Telefonos de Mexico S.A.B. de C.V.	\N	USD	1	\N	f	78460	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TMX||us||False	f	t	t
Honeywell International Inc.	\N	USD	1	\N	f	78465	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HON||us||False	f	t	t
Barclays PLC	\N	USD	1	\N	f	78466	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BCS||us||False	f	t	t
Potash Corp. of Saskatchewan Inc.	\N	USD	1	\N	f	78467	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#POT||us||False	f	t	t
Dow Chemical Co.	\N	USD	1	\N	f	78468	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DOW||us||False	f	t	t
MasterCard Inc. Cl A	\N	USD	1	\N	f	78477	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MA||us||False	f	t	t
Time Warner Inc.	\N	USD	1	\N	f	78479	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TWX||us||False	f	t	t
ING Groep N.V.	\N	USD	1	\N	f	78480	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ING||us||False	f	t	t
CNOOC Ltd.	\N	USD	1	\N	f	78487	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CEO||us||False	f	t	t
Xcel Energy Inc.	\N	USD	1	\N	f	78494	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#XEL||us||False	f	t	t
Companhia de Saneamento Basico do Estado de Sao Paul	\N	USD	1	\N	f	78496	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SBS||us||False	f	t	t
Kennametal Inc.	\N	USD	1	\N	f	78500	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KMT||us||False	f	t	t
SACYR VALLEHERMOSO	ES0182870214	EUR	1	|EURONEXT|	f	78515	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#ES0182870214||pt||False	f	t	t
GPE DIFFUSION PLUS	FR0000053449	EUR	1	|EURONEXT|	f	78506	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000053449||fr||False	f	t	t
PCAS	FR0000053514	EUR	1	|EURONEXT|	f	78508	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000053514||fr||False	f	t	t
PHARMAGEST INTER.	FR0000077687	EUR	1	|EURONEXT|	f	78511	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000077687||fr||False	f	t	t
PONCIN YACHTS	FR0010193052	EUR	1	|EURONEXT|	f	78512	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010193052||fr||False	f	t	t
SCBSM	FR0006239109	EUR	1	|EURONEXT|	f	78521	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0006239109||fr||False	f	t	t
SCBSM BS	FR0010622241	EUR	1	|EURONEXT|	f	78525	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010622241||fr||False	f	t	t
CHRISTIAN DIOR	FR0000130403	EUR	1	|EURONEXT|	f	78527	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000130403||fr||False	f	t	t
GEA GRENOBL.ELECT.	FR0000053035	EUR	1	|EURONEXT|	f	78539	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000053035||fr||False	f	t	t
SAPEC STRIP	BE0005533048	EUR	1	|EURONEXT|	f	78516	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005533048||be||False	f	t	t
DOGI	ES0126962010	EUR	1	|MERCADOCONTINUO|	f	78518	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0126962010||es||False	f	t	t
DXCHINAC	LU0292109856	EUR	1	|MERCADOCONTINUO|	f	78522	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0292109856||es||False	f	t	t
DXDAXC	LU0274211480	EUR	1	|MERCADOCONTINUO|	f	78524	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0274211480||es||False	f	t	t
Duke Realty Corp.	\N	USD	1	\N	f	78502	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DRE||us||False	f	t	t
Telecom Corp. of New Zealand Ltd.	\N	USD	1	\N	f	78503	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NZT||us||False	f	t	t
ManpowerGroup	\N	USD	1	\N	f	78504	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MAN||us||False	f	t	t
Aviva PLC	\N	USD	1	\N	f	78507	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AV||us||False	f	t	t
Nidec Corp.	\N	USD	1	\N	f	78509	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NJ||us||False	f	t	t
Range Resources Corp.	\N	USD	1	\N	f	78510	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RRC||us||False	f	t	t
Noble Corp.	\N	USD	1	\N	f	78513	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NE||us||False	f	t	t
NiSource Inc.	\N	USD	1	\N	f	78514	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NI||us||False	f	t	t
Alumina Ltd.	\N	USD	1	\N	f	78517	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AWC||us||False	f	t	t
Hertz Global Holdings Inc.	\N	USD	1	\N	f	78520	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HTZ||us||False	f	t	t
New Oriental Education & Technology Group Inc.	\N	USD	1	\N	f	78523	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EDU||us||False	f	t	t
Con-way Inc.	\N	USD	1	\N	f	78526	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CNW||us||False	f	t	t
Aqua America Inc.	\N	USD	1	\N	f	78528	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WTR||us||False	f	t	t
BioMed Realty Trust Inc.	\N	USD	1	\N	f	78532	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BMR||us||False	f	t	t
McDermott International Inc.	\N	USD	1	\N	f	78533	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MDR||us||False	f	t	t
HAVAS	FR0000121881	EUR	1	|EURONEXT|	f	78542	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000121881||fr||False	f	t	t
NATIXIS	FR0000120685	EUR	1	|EURONEXT|	f	78543	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000120685||fr||False	f	t	t
NORBERT DENTRESS.	FR0000052870	EUR	1	|EURONEXT|	f	78544	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000052870||fr||False	f	t	t
CAFOM	FR0010151589	EUR	1	|EURONEXT|	f	78548	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010151589||fr||False	f	t	t
SAMSE	FR0000060071	EUR	1	|EURONEXT|	f	78550	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060071||fr||False	f	t	t
HAMON	BE0003700144	EUR	1	|EURONEXT|	f	78540	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003700144||be||False	f	t	t
HARMONY CERT	BE0004558962	EUR	1	|EURONEXT|	f	78541	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0004558962||be||False	f	t	t
SERVICEFLATS CERT	BE0003677888	EUR	1	|EURONEXT|	f	78551	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003677888||be||False	f	t	t
Sterlite Industries (India) Ltd.	\N	USD	1	\N	f	78549	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SLT||us||False	f	t	t
NCR Corp.	\N	USD	1	\N	f	78552	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NCR||us||False	f	t	t
Centrais Eletricas Brasileiras S/A	\N	USD	1	\N	f	78553	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EBR||us||False	f	t	t
Arcos Dorados Holdings Inc. Cl A	\N	USD	1	\N	f	78554	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ARCO||us||False	f	t	t
MF Global Holdings Ltd.	\N	USD	1	\N	f	78555	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MF||us||False	f	t	t
Lexmark International Inc.	\N	USD	1	\N	f	78556	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LXK||us||False	f	t	t
Call IBEX 35 | 7250 € | 21/10/11 | B9996	FR0011101773	EUR	5	|SGW|	f	78559	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9996||fr||False	f	t	t
SIIC DE PARIS NOM.	FR0000057937	EUR	1	|EURONEXT|	f	78562	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000057937||fr||False	f	t	t
TURBO Put IBEX 35 | 9500 € | 16/12/11 | 55093	FR0011092170	EUR	5	|SGW|	f	78565	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#55093||fr||False	f	t	t
TURBO Put IBEX 35 | 9750 € | 16/12/11 | 55094	FR0011092188	EUR	5	|SGW|	f	78567	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#55094||fr||False	f	t	t
TURBO Put IBEX 35 | 10000 € | 16/12/11 | 55095	FR0011092196	EUR	5	|SGW|	f	78568	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#55095||fr||False	f	t	t
TURBO Put IBEX 35 | 9250 € | 16/12/11 | 55092	FR0011092162	EUR	5	|SGW|	f	78569	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#55092||fr||False	f	t	t
SOC FRANC CASINOS	FR0010209809	EUR	1	|EURONEXT|	f	78570	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010209809||fr||False	f	t	t
SPIR COMMUNICATION	FR0000131732	EUR	1	|EURONEXT|	f	78572	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000131732||fr||False	f	t	t
SQLI	FR0004045540	EUR	1	|EURONEXT|	f	78573	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004045540||fr||False	f	t	t
SIOEN	BE0003743573	EUR	1	|EURONEXT|	f	78564	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003743573||be||False	f	t	t
SIPEF STRIP (D)	BE0005629036	EUR	1	|EURONEXT|	f	78566	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005629036||be||False	f	t	t
SOLVAC NOM(RETAIL)	BE0003545531	EUR	1	|EURONEXT|	f	78571	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003545531||be||False	f	t	t
SUCRAF A & B	BE0003463685	EUR	1	|EURONEXT|	f	78574	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003463685||be||False	f	t	t
SIMAC TECHNIEK	NL0000441616	EUR	1	|EURONEXT|	f	78563	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000441616||nl||False	f	t	t
Midas Inc.	\N	USD	1	\N	f	78557	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MDS||us||False	f	t	t
Grupo Radio Centro S.A.B. de C.V.	\N	USD	1	\N	f	78558	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RC||us||False	f	t	t
New York & Co. Inc.	\N	USD	1	\N	f	78560	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NWY||us||False	f	t	t
Sequans Communications S.A.	\N	USD	1	\N	f	78561	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SQNS||us||False	f	t	t
SUEZ ENVIRONNEMENT	FR0010613471	EUR	1	|EURONEXT|	f	78576	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010613471||fr||False	f	t	t
DXLEVDAX	LU0411075376	EUR	1	|MERCADOCONTINUO|	f	78575	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0411075376||es||False	f	t	t
DXMEXC	LU0476289466	EUR	1	|MERCADOCONTINUO|	f	78578	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0476289466||es||False	f	t	t
DXRUSIAD	LU0322252502	EUR	1	|MERCADOCONTINUO|	f	78580	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0322252502||es||False	f	t	t
CIBOX INTER A CTIV	FR0000054322	EUR	1	|EURONEXT|	f	78584	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000054322||fr||False	f	t	t
CIC	FR0005025004	EUR	1	|EURONEXT|	f	78586	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0005025004||fr||False	f	t	t
CIE MAROCAINE	FR0000030611	EUR	1	|EURONEXT|	f	78600	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000030611||fr||False	f	t	t
DXSP500C	LU0490618542	EUR	1	|MERCADOCONTINUO|	f	78581	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0490618542||es||False	f	t	t
CIE B.SAUVAG.STRIP	BE0005576476	EUR	1	|EURONEXT|	f	78588	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005576476||be||False	f	t	t
CIE BOIS SAUVAGE	BE0003592038	EUR	1	|EURONEXT|	f	78599	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003592038||be||False	f	t	t
DXSP500SH	LU0322251520	EUR	1	|MERCADOCONTINUO|	f	78582	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0322251520||es||False	f	t	t
DXSP5INV2	LU0411078636	EUR	1	|MERCADOCONTINUO|	f	78583	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0411078636||es||False	f	t	t
Analytik Jena AG	DE0005213508	EUR	1	|DEUTSCHEBOERSE|	f	78597	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005213508||de||False	f	t	t
aleo solar Aktiengesellschaft	DE000A0JM634	EUR	1	|DEUTSCHEBOERSE|	f	78601	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0JM634||de||False	f	t	t
SLM Corp.	\N	USD	1	\N	f	78585	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SLM||us||False	f	t	t
Reynolds American Inc.	\N	USD	1	\N	f	78587	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RAI||us||False	f	t	t
Eldorado Gold Corp.	\N	USD	1	\N	f	78589	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EGO||us||False	f	t	t
Ralcorp Holdings Inc.	\N	USD	1	\N	f	78590	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RAH||us||False	f	t	t
Rackspace Hosting Inc.	\N	USD	1	\N	f	78592	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RAX||us||False	f	t	t
Delphi Financial Group Inc. Cl A	\N	USD	1	\N	f	78593	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DFG||us||False	f	t	t
Emulex Corp.	\N	USD	1	\N	f	78594	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ELX||us||False	f	t	t
3D Systems Corp.	\N	USD	1	\N	f	78596	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DDD||us||False	f	t	t
American Axle & Manufacturing Holdings Inc.	\N	USD	1	\N	f	78598	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AXL||us||False	f	t	t
GASCOGNE	FR0000124414	EUR	1	|EURONEXT|	f	78605	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000124414||fr||False	f	t	t
GAUMONT	FR0000034894	EUR	1	|EURONEXT|	f	78608	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000034894||fr||False	f	t	t
SUPRA	FR0000032567	EUR	1	|EURONEXT|	f	78629	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000032567||fr||False	f	t	t
TELEVERBIER	CH0008175645	EUR	1	|EURONEXT|	f	78631	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#CH0008175645||fr||False	f	t	t
VICAT	FR0000031775	EUR	1	|EURONEXT|	f	78642	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000031775||fr||False	f	t	t
VRANKEN-POMMERY	FR0000062796	EUR	1	|EURONEXT|	f	78645	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000062796||fr||False	f	t	t
CIMESCAUT	BE0003304061	EUR	1	|EURONEXT|	f	78602	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003304061||be||False	f	t	t
UCB	BE0003739530	EUR	1	|EURONEXT|	f	78633	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003739530||be||False	f	t	t
HEIJMANS	NL0009269109	EUR	1	|EURONEXT|	f	78609	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009269109||nl||False	f	t	t
VALUE8	NL0009082486	EUR	1	|EURONEXT|	f	78640	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009082486||nl||False	f	t	t
Amadeus Fire AG	DE0005093108	EUR	1	|DEUTSCHEBOERSE|	f	78603	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005093108||de||False	f	t	t
artnet AG	DE000A1K0375	EUR	1	|DEUTSCHEBOERSE|	f	78604	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1K0375||de||False	f	t	t
Asian Bamboo AG	DE000A0M6M79	EUR	1	|DEUTSCHEBOERSE|	f	78610	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0M6M79||de||False	f	t	t
ATOSS Software AG	DE0005104400	EUR	1	|DEUTSCHEBOERSE|	f	78619	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005104400||de||False	f	t	t
Augusta Technologie AG	DE000A0D6612	EUR	1	|DEUTSCHEBOERSE|	f	78635	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0D6612||de||False	f	t	t
Aurubis AG	DE0006766504	EUR	1	|DEUTSCHEBOERSE|	f	78637	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006766504||de||False	f	t	t
Axel Springer AG	DE0005501357	EUR	1	|DEUTSCHEBOERSE|	f	78641	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005501357||de||False	f	t	t
Balda AG	DE0005215107	EUR	1	|DEUTSCHEBOERSE|	f	78648	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005215107||de||False	f	t	t
W&T Offshore Inc.	\N	USD	1	\N	f	78612	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WTI||us||False	f	t	t
DineEquity Inc.	\N	USD	1	\N	f	78613	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DIN||us||False	f	t	t
Lindsay Corp.	\N	USD	1	\N	f	78620	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LNN||us||False	f	t	t
Nordic American Tankers Ltd.	\N	USD	1	\N	f	78627	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NAT||us||False	f	t	t
EnPro Industries Inc.	\N	USD	1	\N	f	78628	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NPO||us||False	f	t	t
AstraZeneca PLC	\N	USD	1	\N	f	78630	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AZN||us||False	f	t	t
U.S. Bancorp	\N	USD	1	\N	f	78632	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#USB||us||False	f	t	t
Canadian Natural Resources Ltd.	\N	USD	1	\N	f	78634	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CNQ||us||False	f	t	t
Discover Financial Services	\N	USD	1	\N	f	78644	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DFS||us||False	f	t	t
Consol Energy Inc.	\N	USD	1	\N	f	78647	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CNX||us||False	f	t	t
COHERIS	FR0004031763	EUR	1	|EURONEXT|	f	78691	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004031763||fr||False	f	t	t
PUBLIC SYSTEME HOP	FR0000065278	EUR	1	|EURONEXT|	f	78697	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000065278||fr||False	f	t	t
\N	\N	\N	\N	\N	f	78655	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0126542002||None||False	f	t	t
SARTORIUS NV	FR0011169192	EUR	1	|EURONEXT|	f	78705	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011169192||fr||False	f	t	t
SINCLAIR PHARMA	GB0033856740	EUR	1	|EURONEXT|	f	78708	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#GB0033856740||fr||False	f	t	t
WAREHOUSES-SICAFI	BE0003734481	EUR	1	|EURONEXT|	f	78653	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003734481||be||False	f	t	t
CMB	BE0003817344	EUR	1	|EURONEXT|	f	78679	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003817344||be||False	f	t	t
COFINIMMO PRIV1	BE0003811289	EUR	1	|EURONEXT|	f	78686	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003811289||be||False	f	t	t
COFINIMMO PRIV2	BE0003813301	EUR	1	|EURONEXT|	f	78688	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003813301||be||False	f	t	t
DXSP5LEV2	LU0411078552	EUR	1	|MERCADOCONTINUO|	f	78678	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0411078552||es||False	f	t	t
Basler AG	DE0005102008	EUR	1	|DEUTSCHEBOERSE|	f	78652	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005102008||de||False	f	t	t
Aareal Bank AG	DE0005408116	EUR	1	|DEUTSCHEBOERSE|	f	78684	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005408116||de||False	f	t	t
BAUER Aktiengesellschaft	DE0005168108	EUR	1	|DEUTSCHEBOERSE|	f	78685	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005168108||de||False	f	t	t
BayWa AG Na	DE0005194005	EUR	1	|DEUTSCHEBOERSE|	f	78689	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005194005||de||False	f	t	t
J.C. Penney Co. Inc.	\N	USD	1	\N	f	78650	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JCP||us||False	f	t	t
Jefferies Group Inc.	\N	USD	1	\N	f	78658	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JEF||us||False	f	t	t
Hatteras Financial Corp.	\N	USD	1	\N	f	78662	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HTS||us||False	f	t	t
Shaw Group Inc.	\N	USD	1	\N	f	78664	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SHAW||us||False	f	t	t
Southwest Gas Corp.	\N	USD	1	\N	f	78670	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SWX||us||False	f	t	t
First Potomac Realty Trust	\N	USD	1	\N	f	78674	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FPO||us||False	f	t	t
Pfizer Inc.	\N	USD	1	\N	f	78675	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PFE||us||False	f	t	t
Principal Financial Group Inc.	\N	USD	1	\N	f	78677	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PFG||us||False	f	t	t
Turkcell Iletisim Hizmetleri A.S.	\N	USD	1	\N	f	78680	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TKC||us||False	f	t	t
Cleco Corp.	\N	USD	1	\N	f	78681	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CNL||us||False	f	t	t
Weight Watchers International Inc.	\N	USD	1	\N	f	78682	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WTW||us||False	f	t	t
Centene Corp.	\N	USD	1	\N	f	78690	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CNC||us||False	f	t	t
Evercore Partners Inc. Cl A	\N	USD	1	\N	f	78693	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EVR||us||False	f	t	t
Office Depot Inc.	\N	USD	1	\N	f	78701	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ODP||us||False	f	t	t
AutoZone Inc.		USD	1	|SP500|	f	78646					100	c	0	2	AZO	{1}	{3}	NYSE#AZO||us||False	f	t	t
Oxford Industries Inc.	\N	USD	1	\N	f	78706	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OXM||us||False	f	t	t
Nelnet Inc. Cl A	\N	USD	1	\N	f	78713	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NNI||us||False	f	t	t
Patriot Coal Corp.	\N	USD	1	\N	f	78714	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PCX||us||False	f	t	t
Indosat	\N	USD	1	\N	f	78715	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IIT||us||False	f	t	t
ZUBLIN IMMOBILIERE	FR0010298901	EUR	1	|EURONEXT|	f	78722	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010298901||fr||False	f	t	t
BayWa AG vNa	DE0005194062	EUR	1	|DEUTSCHEBOERSE|	f	78729	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005194062||de||False	f	t	t
Bilfinger Berger SE	DE0005909006	EUR	1	|DEUTSCHEBOERSE|	f	78745	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005909006||de||False	f	t	t
Trina Solar Ltd.	\N	USD	1	\N	f	78716	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TSL||us||False	f	t	t
Coca-Cola Co.	\N	USD	1	\N	f	78717	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KO||us||False	f	t	t
Schlumberger Ltd.	\N	USD	1	\N	f	78718	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SLB||us||False	f	t	t
Citigroup Inc.	\N	USD	1	\N	f	78723	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#C||us||False	f	t	t
Union Pacific Corp.	\N	USD	1	\N	f	78724	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UNP||us||False	f	t	t
CVR Energy Inc.	\N	USD	1	\N	f	78725	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CVI||us||False	f	t	t
Alexander & Baldwin Inc.	\N	USD	1	\N	f	78726	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ALEX||us||False	f	t	t
Stifel Financial Corp.	\N	USD	1	\N	f	78727	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SF||us||False	f	t	t
Owens & Minor Inc.	\N	USD	1	\N	f	78728	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OMI||us||False	f	t	t
Belden Inc.	\N	USD	1	\N	f	78730	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BDC||us||False	f	t	t
Nalco Holding Co.	\N	USD	1	\N	f	78731	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NLC||us||False	f	t	t
Esterline Technologies Corp.	\N	USD	1	\N	f	78734	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ESL||us||False	f	t	t
Starwood Property Trust Inc.	\N	USD	1	\N	f	78736	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STWD||us||False	f	t	t
FTI Consulting Inc.	\N	USD	1	\N	f	78737	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FCN||us||False	f	t	t
Federated Investors Inc.	\N	USD	1	\N	f	78738	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FII||us||False	f	t	t
UIL Holdings Corp.	\N	USD	1	\N	f	78739	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UIL||us||False	f	t	t
Supervalu Inc.	\N	USD	1	\N	f	78743	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SVU||us||False	f	t	t
\N	\N	\N	\N	\N	f	81273	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0165240005||None||False	f	t	t
COMPTA	PTCOM0AE0007	EUR	1	|EURONEXT|	f	78763	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTCOM0AE0007||pt||False	f	t	t
Put IBEX 35 | 8250 € | 20/01/12 | B9946	FR0011091354	EUR	5	|SGW|	f	78759	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9946||fr||False	f	t	t
Put IBEX 35 | 10750 € | 21/10/11 | B7216	FR0011039668	EUR	5	|SGW|	f	78764	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7216||fr||False	f	t	t
Put IBEX 35 | 11250 € | 21/10/11 | B7217	FR0011039676	EUR	5	|SGW|	f	78765	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7217||fr||False	f	t	t
Call IBEX 35 | 8250 € | 20/04/12 | C1105	FR0011124106	EUR	5	|SGW|	f	78770	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1105||fr||False	f	t	t
Put IBEX 35 | 9500 € | 16/03/12 | B7621	FR0011058528	EUR	5	|SGW|	f	78773	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7621||fr||False	f	t	t
Put IBEX 35 | 10500 € | 16/03/12 | B7617	FR0011058544	EUR	5	|SGW|	f	78782	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7617||fr||False	f	t	t
Put IBEX 35 | 11000 € | 16/03/12 | B7618	FR0011058551	EUR	5	|SGW|	f	78784	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7618||fr||False	f	t	t
Call IBEX 35 | 7250 € | 20/04/12 | C1103	FR0011124080	EUR	5	|SGW|	f	78786	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1103||fr||False	f	t	t
Carmignac Profil Réactif 50	FR0010149203	EUR	2	|CARMIGNAC|	f	78788	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	FR0010149203||fr||False	f	t	t
ADT S.I.I.C.	FR0000064594	EUR	1	|EURONEXT|	f	78791	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064594||fr||False	f	t	t
Call IBEX 35 | 7750 € | 20/04/12 | C1104	FR0011124098	EUR	5	|SGW|	f	78794	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1104||fr||False	f	t	t
ADVINI	FR0000053043	EUR	1	|EURONEXT|	f	78796	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000053043||fr||False	f	t	t
AFFIPARIS	FR0010148510	EUR	1	|EURONEXT|	f	78797	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010148510||fr||False	f	t	t
Call IBEX 35 | 6500 € | 21/09/12 | C3285	FR0011168251	EUR	5	|SGW|	f	78799	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3285||fr||False	f	t	t
DXST600C	LU0328475792	EUR	1	|MERCADOCONTINUO|	f	78748	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0328475792||es||False	f	t	t
CONNECT GROUP	BE0003786036	EUR	1	|EURONEXT|	f	78772	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003786036||be||False	f	t	t
DXWORLDC	LU0274208692	EUR	1	|MERCADOCONTINUO|	f	78753	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0274208692||es||False	f	t	t
EADS	NL0000235190	EUR	1	|MERCADOCONTINUO|	f	78755	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#NL0000235190||es||False	f	t	t
CONVERSUS CAP	GG00B1WR8K11	EUR	1	|EURONEXT|	f	78776	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GG00B1WR8K11||nl||False	f	t	t
ELECNOR	ES0129743318	EUR	1	|MERCADOCONTINUO|	f	78775	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0129743318||es||False	f	t	t
CORIO	NL0000288967	EUR	1	|EURONEXT|	f	78798	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000288967||nl||False	f	t	t
biolitec AG	DE0005213409	EUR	1	|DEUTSCHEBOERSE|	f	78746	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005213409||de||False	f	t	t
Biotest AG St	DE0005227201	EUR	1	|DEUTSCHEBOERSE|	f	78749	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005227201||de||False	f	t	t
bmp AG	DE0003304200	EUR	1	|DEUTSCHEBOERSE|	f	78750	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0003304200||de||False	f	t	t
BMW AG Vz	DE0005190037	EUR	1	|DEUTSCHEBOERSE|	f	78752	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005190037||de||False	f	t	t
Deufol AG	DE0005101505	EUR	1	|DEUTSCHEBOERSE|	f	78762	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005101505||de||False	f	t	t
Hudson Pacific Properties Inc.	\N	USD	1	\N	f	78760	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HPP||us||False	f	t	t
Monmouth Real Estate Investment Corp. Cl A	\N	USD	1	\N	f	78761	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MNR||us||False	f	t	t
Taiwan Semiconductor Manufacturing Co.	\N	USD	1	\N	f	78767	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TSM||us||False	f	t	t
UnitedHealth Group Inc.	\N	USD	1	\N	f	78768	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UNH||us||False	f	t	t
Duke Energy Corp.	\N	USD	1	\N	f	78769	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DUK||us||False	f	t	t
CSX Corp.	\N	USD	1	\N	f	78771	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CSX||us||False	f	t	t
Continucare Corp.	\N	USD	1	\N	f	78781	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CNU||us||False	f	t	t
Gildan Activewear Inc.	\N	USD	1	\N	f	78800	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GIL||us||False	f	t	t
Call IBEX 35 | 8000 € | 21/09/12 | C3288	FR0011168285	EUR	5	|SGW|	f	78801	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3288||fr||False	f	t	t
Call IBEX 35 | 11000 € | 21/09/12 | C3294	FR0011168343	EUR	5	|SGW|	f	78802	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C3294||fr||False	f	t	t
Call IBEX 35 | 15000 € | 20/12/13 | B7866	FR0011065697	EUR	5	|SGW|	f	78803	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7866||fr||False	f	t	t
CRCAM NORM.SEINE	FR0000044364	EUR	1	|EURONEXT|	f	78812	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000044364||fr||False	f	t	t
CRCAM PARIS ET IDF	FR0000045528	EUR	1	|EURONEXT|	f	78814	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000045528||fr||False	f	t	t
Call IBEX 35 | 6750 € | 18/05/12 | C1114	FR0011124197	EUR	5	|SGW|	f	78818	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1114||fr||False	f	t	t
Call IBEX 35 | 11000 € | 18/11/11 | B7221	FR0011039718	EUR	5	|SGW|	f	78820	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7221||fr||False	f	t	t
Call IBEX 35 | 11500 € | 18/11/11 | B7222	FR0011039726	EUR	5	|SGW|	f	78823	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B7222||fr||False	f	t	t
Put IBEX 35 | 7500 € | 18/11/11 | B9936	FR0011091255	EUR	5	|SGW|	f	78824	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9936||fr||False	f	t	t
CS (COMM.SYSTEMES)	FR0007317813	EUR	1	|EURONEXT|	f	78825	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0007317813||fr||False	f	t	t
Call IBEX 35 | 7250 € | 18/05/12 | C1115	FR0011124205	EUR	5	|SGW|	f	78826	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1115||fr||False	f	t	t
Call IBEX 35 | 7750 € | 18/05/12 | C1116	FR0011124213	EUR	5	|SGW|	f	78833	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1116||fr||False	f	t	t
Call IBEX 35 | 8250 € | 18/05/12 | C1117	FR0011124221	EUR	5	|SGW|	f	78835	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C1117||fr||False	f	t	t
CRCAM MORBIHAN CCI	FR0000045551	EUR	1	|EURONEXT|	f	78836	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000045551||fr||False	f	t	t
CRCAM NORD CCI	FR0000185514	EUR	1	|EURONEXT|	f	78839	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000185514||fr||False	f	t	t
Put IBEX 35 | 9250 € | 20/04/12 | C2134	FR0011145424	EUR	5	|SGW|	f	78841	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C2134||fr||False	f	t	t
\N	\N	\N	\N	\N	f	81368	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0165144009||None||False	f	t	t
Brenntag AG	DE000A1DAHH0	EUR	1	|DEUTSCHEBOERSE|	f	78817	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1DAHH0||de||False	f	t	t
Brüder Mannesmann AG	DE0005275507	EUR	1	|DEUTSCHEBOERSE|	f	78821	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005275507||de||False	f	t	t
C.A.T. OIL AG	AT0000A00Y78	EUR	1	|DEUTSCHEBOERSE|	f	78822	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#AT0000A00Y78||de||False	f	t	t
CANCOM AG	DE0005419105	EUR	1	|DEUTSCHEBOERSE|	f	78827	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005419105||de||False	f	t	t
Carl Zeiss Meditec AG	DE0005313704	EUR	1	|DEUTSCHEBOERSE|	f	78828	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005313704||de||False	f	t	t
Celesio AG	DE000CLS1001	EUR	1	|DEUTSCHEBOERSE|	f	78829	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000CLS1001||de||False	f	t	t
Dollar Thrifty Automotive Group Inc.	\N	USD	1	\N	f	78804	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DTG||us||False	f	t	t
A.O. Smith Corp.	\N	USD	1	\N	f	78805	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AOS||us||False	f	t	t
Helix Energy Solutions Group Inc.	\N	USD	1	\N	f	78806	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HLX||us||False	f	t	t
F.N.B. Corp.	\N	USD	1	\N	f	78809	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FNB||us||False	f	t	t
HCP Inc.	\N	USD	1	\N	f	78811	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HCP||us||False	f	t	t
Kellogg Co.	\N	USD	1	\N	f	78813	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#K||us||False	f	t	t
Health Care REIT Inc.	\N	USD	1	\N	f	78815	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HCN||us||False	f	t	t
Agnico-Eagle Mines Ltd.	\N	USD	1	\N	f	78819	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AEM||us||False	f	t	t
Ametek Inc.	\N	USD	1	\N	f	78837	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AME||us||False	f	t	t
Put IBEX 35 | 10250 € | 20/04/12 | C2136	FR0011145440	EUR	5	|SGW|	f	78844	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#C2136||fr||False	f	t	t
Call IBEX 35 | 9000 € | 15/06/12 | B9959	FR0011091487	EUR	5	|SGW|	f	78860	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9959||fr||False	f	t	t
Call IBEX 35 | 10000 € | 15/06/12 | B9961	FR0011091503	EUR	5	|SGW|	f	78861	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9961||fr||False	f	t	t
PAREF	FR0010263202	EUR	1	|EURONEXT|	f	78873	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010263202||fr||False	f	t	t
Call IBEX 35 inLine | 7000 € | 14/12/11 | I0044	FR0011117621	EUR	5	|SGW|	f	78875	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0044||fr||False	f	t	t
Call IBEX 35 inLine | 6500 € | 14/12/11 | I0043	FR0011117605	EUR	5	|SGW|	f	78876	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#I0043||fr||False	f	t	t
ORDINA	NL0000440584	EUR	1	|EURONEXT|	f	78870	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000440584||nl||False	f	t	t
ESP.DEL ZINC	ES0132970213	EUR	1	|MERCADOCONTINUO|	f	78862	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0132970213||es||False	f	t	t
EZENTIS	ES0172708317	EUR	1	|MERCADOCONTINUO|	f	78869	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0172708317||es||False	f	t	t
Hormel Foods Corp.	\N	USD	1	\N	f	78845	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HRL||us||False	f	t	t
HCA Holdings Inc.	\N	USD	1	\N	f	78846	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HCA||us||False	f	t	t
Grubb & Ellis Co.	\N	USD	1	\N	f	78853	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GBE||us||False	f	t	t
Integrys Energy Group Inc.	\N	USD	1	\N	f	78854	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TEG||us||False	f	t	t
Reinsurance Group of America Inc.	\N	USD	1	\N	f	78855	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RGA||us||False	f	t	t
Progress Energy Inc.	\N	USD	1	\N	f	78856	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PGN||us||False	f	t	t
Navistar International Corp.	\N	USD	1	\N	f	78858	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NAV||us||False	f	t	t
HCC Insurance Holdings Inc.	\N	USD	1	\N	f	78859	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HCC||us||False	f	t	t
Hospitality Properties Trust	\N	USD	1	\N	f	78863	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HPT||us||False	f	t	t
Weingarten Realty Investors	\N	USD	1	\N	f	78864	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WRI||us||False	f	t	t
Precision Drilling Corp.	\N	USD	1	\N	f	78865	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PDS||us||False	f	t	t
Great Plains Energy Inc.	\N	USD	1	\N	f	78866	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GXP||us||False	f	t	t
Progressive Waste Solutions Ltd.	\N	USD	1	\N	f	78868	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BIN||us||False	f	t	t
CAIXA GALICIA EUROIBOR GARANT.	ES0119483008	EUR	2	|BMF|0128|	f	78831	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0119483008||es||False	f	t	t
SCHAEFFER DUFOUR	FR0000064511	EUR	1	|EURONEXT|	f	78906	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064511||fr||False	f	t	t
ALTRAN TECHN.	FR0000034639	EUR	1	|EURONEXT|	f	78910	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000034639||fr||False	f	t	t
LECTRA	FR0000065484	EUR	1	|EURONEXT|	f	78920	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000065484||fr||False	f	t	t
REMY COINTREAU	FR0000130395	EUR	1	|EURONEXT|	f	78935	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000130395||fr||False	f	t	t
OFI PRIV EQU CAP	FR0000038945	EUR	1	|EURONEXT|	f	78939	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000038945||fr||False	f	t	t
\N	\N	\N	\N	\N	f	78911	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0112829009||None||False	f	t	t
TOUPARGEL GROUPE	FR0000039240	EUR	1	|EURONEXT|	f	78942	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000039240||fr||False	f	t	t
OFI PRI EQ CAP BS2	FR0010909309	EUR	1	|EURONEXT|	f	78953	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010909309||fr||False	f	t	t
SCHEERD.V KERCHOVE	BE0012378593	EUR	1	|EURONEXT|	f	78926	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0012378593||be||False	f	t	t
APERAM	LU0569974404	EUR	1	|EURONEXT|	f	78912	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#LU0569974404||nl||False	f	t	t
CENIT AG	DE0005407100	EUR	1	|DEUTSCHEBOERSE|	f	78896	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005407100||de||False	f	t	t
Centrosolar Group AG	DE0005148506	EUR	1	|DEUTSCHEBOERSE|	f	78897	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005148506||de||False	f	t	t
CENTROTEC Sustainable AG	DE0005407506	EUR	1	|DEUTSCHEBOERSE|	f	78898	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005407506||de||False	f	t	t
centrotherm photovoltaics AG	DE000A0JMMN2	EUR	1	|DEUTSCHEBOERSE|	f	78900	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0JMMN2||de||False	f	t	t
CeWe Color Holding AG	DE0005403901	EUR	1	|DEUTSCHEBOERSE|	f	78901	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005403901||de||False	f	t	t
China Specialty Glass AG	DE000A1EL8Y8	EUR	1	|DEUTSCHEBOERSE|	f	78902	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1EL8Y8||de||False	f	t	t
comdirect bank AG	DE0005428007	EUR	1	|DEUTSCHEBOERSE|	f	78905	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005428007||de||False	f	t	t
TNT EXPRESS	NL0009739424	EUR	1	|EURONEXT|	f	78932	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009739424||nl||False	f	t	t
FERSA	ES0136463017	EUR	1	|MERCADOCONTINUO|	f	78962	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0136463017||es||False	f	t	t
artnet AG	DE0006909500	EUR	1	|DEUTSCHEBOERSE|	f	78961	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006909500||de||False	f	t	t
Amrep Corp.	\N	USD	1	\N	f	78899	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AXR||us||False	f	t	t
Canadian National Railway Co.	\N	USD	1	\N	f	78917	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CNI||us||False	f	t	t
Graco Inc.	\N	USD	1	\N	f	78918	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GGG||us||False	f	t	t
Alaska Air Group Inc.	\N	USD	1	\N	f	78919	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ALK||us||False	f	t	t
Douglas Emmett Inc.	\N	USD	1	\N	f	78923	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DEI||us||False	f	t	t
Flowers Foods Inc.	\N	USD	1	\N	f	78925	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FLO||us||False	f	t	t
Spirit AeroSystems Hldgs Inc. Cl A	\N	USD	1	\N	f	78927	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SPR||us||False	f	t	t
Covance Inc.	\N	USD	1	\N	f	78928	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CVD||us||False	f	t	t
Coca-Cola Femsa S.A.B. de C.V.	\N	USD	1	\N	f	78929	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KOF||us||False	f	t	t
Konami Corp.	\N	USD	1	\N	f	78933	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KNM||us||False	f	t	t
Assured Guaranty Ltd.	\N	USD	1	\N	f	78934	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AGO||us||False	f	t	t
FLUIDRA	ES0137650018	EUR	1	|MERCADOCONTINUO|	f	78964	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0137650018||es||False	f	t	t
E.SANTO FINANCIAL	LU0011904405	EUR	1	|EURONEXT|	f	79004	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#LU0011904405||pt||False	f	t	t
EDP	PTEDP0AM0009	EUR	1	|EURONEXT|	f	79022	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTEDP0AM0009||pt||False	f	t	t
CompuGroup Medical AG	DE0005437305	EUR	1	|DEUTSCHEBOERSE|	f	78971	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005437305||de||False	f	t	t
Conergy AG	DE000A1KRCK4	EUR	1	|DEUTSCHEBOERSE|	f	78972	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1KRCK4||de||False	f	t	t
ESTAVIS AG	DE000A0KFKB3	EUR	1	|DEUTSCHEBOERSE|	f	78973	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0KFKB3||de||False	f	t	t
Constantin Medien AG	DE0009147207	EUR	1	|DEUTSCHEBOERSE|	f	78991	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0009147207||de||False	f	t	t
COR&FJA AG	DE0005130108	EUR	1	|DEUTSCHEBOERSE|	f	79041	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005130108||de||False	f	t	t
Corporate Equity Partners AG	CH0108753523	EUR	1	|DEUTSCHEBOERSE|	f	79047	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#CH0108753523||de||False	f	t	t
BlackRock Inc.		USD	1	|SP500|	f	78810					100	c	0	2	BLK	{1}	{3}	NYSE#BLK||us||False	f	t	t
ARCELORMITTAL	LU0323134006	EUR	1	|CAC|EURONEXT|EUROSTOXX|	f	78915					100	c	0	12	None	\N	\N	EURONEXT#LU0323134006||nl||False	f	t	t
C-QUADRAT Investment AG	AT0000613005	EUR	1	|DEUTSCHEBOERSE|	f	79048	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#AT0000613005||de||False	f	t	t
FTSE4GOODIBX	ES0139761003	EUR	1	|MERCADOCONTINUO|	f	79015	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0139761003||es||False	f	t	t
FUNESPA&Ntilde;A	ES0140441017	EUR	1	|MERCADOCONTINUO|	f	79016	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0140441017||es||False	f	t	t
Entertainment Properties Trust	\N	USD	1	\N	f	78965	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EPR||us||False	f	t	t
Anixter International Inc.	\N	USD	1	\N	f	78979	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AXE||us||False	f	t	t
Alliant Techsystems Inc.	\N	USD	1	\N	f	78981	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ATK||us||False	f	t	t
CARBO Ceramics Inc.	\N	USD	1	\N	f	78982	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CRR||us||False	f	t	t
Molycorp Inc.	\N	USD	1	\N	f	78983	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MCP||us||False	f	t	t
G.A.M.	ES0141571119	EUR	1	|MERCADOCONTINUO|	f	79036	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0141571119||es||False	f	t	t
Aspen Insurance Holdings Ltd.	\N	USD	1	\N	f	78987	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AHL||us||False	f	t	t
Brunswick Corp.	\N	USD	1	\N	f	78989	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BC||us||False	f	t	t
GlaxoSmithKline PLC	\N	USD	1	\N	f	78995	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GSK||us||False	f	t	t
MBIA Inc.	\N	USD	1	\N	f	78997	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MBI||us||False	f	t	t
Exelis Inc.	\N	USD	1	\N	f	78998	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#XLS||us||False	f	t	t
GE.INVERSION	ES0141960635	EUR	1	|MERCADOCONTINUO|	f	79051	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0141960635||es||False	f	t	t
BIOMERIEUX	FR0010096479	EUR	1	|EURONEXT|	f	78966	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010096479||fr||False	f	t	t
LISI	FR0000050353	EUR	1	|EURONEXT|	f	78988	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000050353||fr||False	f	t	t
ASCENCIO (D)	BE0003856730	EUR	1	|EURONEXT|	f	78994	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003856730||be||False	f	t	t
ECKERT-ZIEGLER BG	BE0003689032	EUR	1	|EURONEXT|	f	79013	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003689032||be||False	f	t	t
4ENERGY INV (D)	BE0003888089	EUR	1	|EURONEXT|	f	79017	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003888089||be||False	f	t	t
ECONOCOM GROUP	BE0003563716	EUR	1	|EURONEXT|	f	79018	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003563716||be||False	f	t	t
A.S.T. GROUPE	FR0000076887	EUR	1	|EURONEXT|	f	79053	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000076887||fr||False	f	t	t
CRCAM ATL.VEND.CCI	FR0000185506	EUR	1	|EURONEXT|	f	79056	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000185506||fr||False	f	t	t
CROSSWOOD	FR0000050395	EUR	1	|EURONEXT|	f	79057	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000050395||fr||False	f	t	t
ACTEOS	FR0000076861	EUR	1	|EURONEXT|	f	79060	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000076861||fr||False	f	t	t
ASSYSTEMBSAR2012	FR0010166371	EUR	1	|EURONEXT|	f	79061	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010166371||fr||False	f	t	t
CSCOM BS13B	FR0010325035	EUR	1	|EURONEXT|	f	79064	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010325035||fr||False	f	t	t
ETAM DEVELOPPEMENT	FR0000035743	EUR	1	|EURONEXT|	f	79069	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000035743||fr||False	f	t	t
COLRUYT (D)	BE0974256852	EUR	1	|EURONEXT|	f	79063	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0974256852||be||False	f	t	t
IBM CERT	BE0004607488	EUR	1	|EURONEXT|	f	79070	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0004607488||be||False	f	t	t
ACCELL GROUP	NL0009767532	EUR	1	|EURONEXT|	f	79058	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009767532||nl||False	f	t	t
Huntington Ingalls Industries Inc.	\N	USD	1	\N	f	79052	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HII||us||False	f	t	t
Bristow Group Inc.	\N	USD	1	\N	f	79055	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BRS||us||False	f	t	t
Telecom Argentina S.A.	\N	USD	1	\N	f	79067	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TEO||us||False	f	t	t
Hyatt Hotels Corp.	\N	USD	1	\N	f	79071	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#H||us||False	f	t	t
\N	\N	\N	\N	\N	f	79066	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0138367000||None||False	f	t	t
SONAE IND.SGPS	PTS3P0AM0017	EUR	1	|EURONEXT|	f	79077	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTS3P0AM0017||pt||False	f	t	t
AES CHEMUNEX	FR0010158642	EUR	1	|EURONEXT|	f	79086	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010158642||fr||False	f	t	t
ANGLOGOLD ASHANTI	ZAE000043485	EUR	1	|EURONEXT|	f	79089	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#ZAE000043485||fr||False	f	t	t
ALPHA MOS	FR0000062804	EUR	1	|EURONEXT|	f	79096	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000062804||fr||False	f	t	t
BAC MAJESTIC	FR0010973487	EUR	1	|EURONEXT|	f	79105	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010973487||fr||False	f	t	t
GEO ORD.B	MXP3142C1177	EUR	1	|MERCADOCONTINUO|	f	79088	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#MXP3142C1177||es||False	f	t	t
ANGLOGOLD ASH CERT	BE0088072930	EUR	1	|EURONEXT|	f	79093	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0088072930||be||False	f	t	t
ALFACAM GROUP	BE0003868859	EUR	1	|EURONEXT|	f	79095	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003868859||be||False	f	t	t
BAN RSWARR 10JUN15	BE0974254832	EUR	1	|EURONEXT|	f	79107	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0974254832||be||False	f	t	t
BANIMMO STRIP (D)	BE0005614855	EUR	1	|EURONEXT|	f	79113	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005614855||be||False	f	t	t
AAMIGOO	CWN001011006	EUR	1	|EURONEXT|	f	79091	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#CWN001011006||nl||False	f	t	t
Continental AG	DE0005439004	EUR	1	|DEUTSCHEBOERSE|	f	79081	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005439004||de||False	f	t	t
CropEnergies AG	DE000A0LAUP1	EUR	1	|DEUTSCHEBOERSE|	f	79082	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0LAUP1||de||False	f	t	t
CTS Eventim AG	DE0005470306	EUR	1	|DEUTSCHEBOERSE|	f	79083	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005470306||de||False	f	t	t
Curanum AG	DE0005240709	EUR	1	|DEUTSCHEBOERSE|	f	79085	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005240709||de||False	f	t	t
Mueller Industries Inc.	\N	USD	1	\N	f	79072	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MLI||us||False	f	t	t
Brady Corp. Cl A	\N	USD	1	\N	f	79079	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BRC||us||False	f	t	t
General Cable Corp.	\N	USD	1	\N	f	79080	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BGC||us||False	f	t	t
Novartis AG	\N	USD	1	\N	f	79084	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NVS||us||False	f	t	t
Novo Nordisk A/S	\N	USD	1	\N	f	79087	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NVO||us||False	f	t	t
Hess Corp.	\N	USD	1	\N	f	79090	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HES||us||False	f	t	t
W.W. Grainger Inc.	\N	USD	1	\N	f	79097	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GWW||us||False	f	t	t
Healthcare Realty Trust Inc.	\N	USD	1	\N	f	79099	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HR||us||False	f	t	t
Health Management Associates Inc. Cl A	\N	USD	1	\N	f	79100	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HMA||us||False	f	t	t
Live Nation Entertainment Inc.	\N	USD	1	\N	f	79101	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LYV||us||False	f	t	t
AOL Inc.	\N	USD	1	\N	f	79108	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AOL||us||False	f	t	t
First American Financial Corp.	\N	USD	1	\N	f	79109	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FAF||us||False	f	t	t
Webster Financial Corp.	\N	USD	1	\N	f	79110	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WBS||us||False	f	t	t
Maximus Inc.	\N	USD	1	\N	f	79111	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MMS||us||False	f	t	t
Genpact Ltd.	\N	USD	1	\N	f	79112	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#G||us||False	f	t	t
FONDMADRID	ES0138801032	EUR	2	|BMF|0085|	f	75414	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138801032||es||False	f	t	t
KUTXAINDEX2	ES0157017031	EUR	2	|BMF|0086|	f	76193	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157017031||es||False	f	t	t
BANQUE TARNEAUD	FR0000065526	EUR	1	|EURONEXT|	f	79114	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000065526||fr||False	f	t	t
TCF Financial Corp.	\N	USD	1	\N	f	79117	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TCB||us||False	f	t	t
Fibria Celulose S.A.	\N	USD	1	\N	f	79125	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FBR||us||False	f	t	t
Cott Corp.	\N	USD	1	\N	f	79126	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#COT||us||False	f	t	t
Thermo Fisher Scientific Inc.	\N	USD	1	\N	f	79127	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TMO||us||False	f	t	t
99 Cents Only Stores	\N	USD	1	\N	f	79128	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NDN||us||False	f	t	t
ABANTE VALOR	ES0190052037	EUR	2	|BMF|0194|	f	78189	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0190052037||es||False	f	t	t
SANTANDER RENTA FIJA LARGO PLAZO C	ES0105941019	EUR	2	|BMF|0012|	f	80825	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105941019||es||False	f	t	t
WELZIA SIGMA 5	ES0184694034	EUR	2	|BMF|0207|	f	80852	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184694034||es||False	f	t	t
BANCO POP.ESPANOL	ES0113790531	EUR	1	|EURONEXT|	f	79164	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#ES0113790531||pt||False	f	t	t
F.RAMA	PTFRV0AE0004	EUR	1	|EURONEXT|	f	79176	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTFRV0AE0004||pt||False	f	t	t
NOVABASE,SGPS	PTNBA0AM0006	EUR	1	|EURONEXT|	f	79179	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTNBA0AM0006||pt||False	f	t	t
BQUE DE LA REUNION	FR0000039612	EUR	1	|EURONEXT|	f	79129	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000039612||fr||False	f	t	t
BRAS.OUEST AFRIC.	SN0008626971	EUR	1	|EURONEXT|	f	79131	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#SN0008626971||fr||False	f	t	t
BRICODEAL	FR0000063919	EUR	1	|EURONEXT|	f	79134	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000063919||fr||False	f	t	t
MERCK AND CO INC	US58933Y1055	EUR	1	|EURONEXT|	f	79146	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US58933Y1055||fr||False	f	t	t
BARBARA BUI	FR0000062788	EUR	1	|EURONEXT|	f	79165	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000062788||fr||False	f	t	t
ETU.REALI.MOULES	FR0000063950	EUR	1	|EURONEXT|	f	79168	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000063950||fr||False	f	t	t
EURO RESSOURCES	FR0000054678	EUR	1	|EURONEXT|	f	79172	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000054678||fr||False	f	t	t
GERDAU PREF.	BRGGBRACNPR8	EUR	1	|MERCADOCONTINUO|	f	79135	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#BRGGBRACNPR8||es||False	f	t	t
GR.C.OCCIDEN	ES0116920333	EUR	1	|MERCADOCONTINUO|	f	79136	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0116920333||es||False	f	t	t
GR.EMP.ENCE	ES0130625512	EUR	1	|MERCADOCONTINUO|	f	79141	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0130625512||es||False	f	t	t
DAB bank AG	DE0005072300	EUR	1	|DEUTSCHEBOERSE|	f	79138	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005072300||de||False	f	t	t
\N	\N	\N	\N	\N	f	79157	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0165193006||None||False	f	t	t
IBERPAPEL	ES0147561015	EUR	1	|MERCADOCONTINUO|	f	79163	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0147561015||es||False	f	t	t
BOUSSARD GHL GBP	GG00B39VMM07	EUR	1	|EURONEXT|	f	79167	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GG00B39VMM07||nl||False	f	t	t
Edison International	\N	USD	1	\N	f	79130	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EIX||us||False	f	t	t
Royal Caribbean Cruises Ltd.	\N	USD	1	\N	f	79137	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RCL||us||False	f	t	t
Kilroy Realty Corp.	\N	USD	1	\N	f	79143	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KRC||us||False	f	t	t
Watsco Inc.	\N	USD	1	\N	f	79148	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WSO||us||False	f	t	t
St. Joe Co.	\N	USD	1	\N	f	79149	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JOE||us||False	f	t	t
Hillenbrand Inc.	\N	USD	1	\N	f	79152	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HI||us||False	f	t	t
FON FINECO AHORRO	ES0175605031	EUR	2	|BMF|0132|	f	79140	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175605031||es||False	f	t	t
INM.COLONIAL	ES0139140042	EUR	1	|MERCADOCONTINUO|	f	79200	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0139140042||es||False	f	t	t
JAZZTEL	GB00B5TMSP21	EUR	1	|MERCADOCONTINUO|	f	79201	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#GB00B5TMSP21||es||False	f	t	t
EUROFINS BSAR 13	FR0010292755	EUR	1	|EURONEXT|	f	79173	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010292755||fr||False	f	t	t
BREDERODE STRIP	BE0005585568	EUR	1	|EURONEXT|	f	79133	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005585568||be||False	f	t	t
BARCO STRIP (D)	BE0005583548	EUR	1	|EURONEXT|	f	79166	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005583548||be||False	f	t	t
EnerSys Inc.	\N	USD	1	\N	f	79153	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ENS||us||False	f	t	t
Fair Isaac Corp.	\N	USD	1	\N	f	79154	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FICO||us||False	f	t	t
Colfax Corp.	\N	USD	1	\N	f	79158	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CFX||us||False	f	t	t
UBS AG	\N	USD	1	\N	f	79169	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UBS||us||False	f	t	t
Williams Cos.	\N	USD	1	\N	f	79170	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WMB||us||False	f	t	t
Coca-Cola Enterprises Inc.	\N	USD	1	\N	f	79174	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CCE||us||False	f	t	t
Crown Holdings Inc.	\N	USD	1	\N	f	79178	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CCK||us||False	f	t	t
NetSuite Inc.	\N	USD	1	\N	f	79180	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#N||us||False	f	t	t
Chemed Corp.	\N	USD	1	\N	f	79182	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CHE||us||False	f	t	t
LA SEDA BAR.	ES0175290115	EUR	1	|MERCADOCONTINUO|	f	79202	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0175290115||es||False	f	t	t
LYXETFEURUTI	FR0010344853	EUR	1	|MERCADOCONTINUO|	f	79203	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010344853||es||False	f	t	t
LYXETFJAPANT	FR0010245514	EUR	1	|MERCADOCONTINUO|	f	79205	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010245514||es||False	f	t	t
VOLTA FINANCE	GG00B1GHHH78	EUR	1	|EURONEXT|	f	79273	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GG00B1GHHH78||nl||False	f	t	t
LYXIBEXINVER	FR0010762492	EUR	1	|MERCADOCONTINUO|	f	79230	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010762492||es||False	f	t	t
LYXNDX1ETF	FR0007063177	EUR	1	|MERCADOCONTINUO|	f	79232	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0007063177||es||False	f	t	t
DEAG Deutsche Entertainment AG	DE000A0Z23G6	EUR	1	|DEUTSCHEBOERSE|	f	79254	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0Z23G6||de||False	f	t	t
Diageo PLC	\N	USD	1	\N	f	79211	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DEO||us||False	f	t	t
\N	\N	\N	\N	\N	f	79242	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0141222002||None||False	f	t	t
Delhaize Group	\N	USD	1	\N	f	79218	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DEG||us||False	f	t	t
\N	\N	\N	\N	\N	f	79250	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0133506008||None||False	f	t	t
FON FINECO TOP RENTA FIJA A	ES0137639003	EUR	2	|BMF|0132|	f	79194	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137639003||es||False	f	t	t
Affiliated Managers Group Inc.	\N	USD	1	\N	f	79222	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AMG||us||False	f	t	t
Gafisa S/A	\N	USD	1	\N	f	79231	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GFA||us||False	f	t	t
Watts Water Technologies Inc. Cl A	\N	USD	1	\N	f	79233	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WTS||us||False	f	t	t
National Health Investors Inc.	\N	USD	1	\N	f	79234	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NHI||us||False	f	t	t
MELIA HOTELS	ES0176252718	EUR	1	|MERCADOCONTINUO|	f	79277	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0176252718||es||False	f	t	t
METROVACESA	ES0154220414	EUR	1	|MERCADOCONTINUO|	f	79278	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0154220414||es||False	f	t	t
MIQUEL COST.	ES0164180012	EUR	1	|MERCADOCONTINUO|	f	79279	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0164180012||es||False	f	t	t
MONTEBALITO	ES0116494016	EUR	1	|MERCADOCONTINUO|	f	79283	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0116494016||es||False	f	t	t
SWORD GROUP	FR0004180578	EUR	1	|EURONEXT|	f	79209	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004180578||fr||False	f	t	t
GBL STRIP	BE0005588596	EUR	1	|EURONEXT|	f	79226	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005588596||be||False	f	t	t
GDF SUEZ STRIP VV	BE0005628020	EUR	1	|EURONEXT|	f	79227	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005628020||be||False	f	t	t
SPECTOR STRIP	BE0005518866	EUR	1	|EURONEXT|	f	79243	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005518866||be||False	f	t	t
NAFTRAC	MX1BNA060006	EUR	1	|MERCADOCONTINUO|	f	79289	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#MX1BNA060006||es||False	f	t	t
PORCELEYNE FLES	NL0000378669	EUR	1	|EURONEXT|	f	79301	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000378669||nl||False	f	t	t
NYESA	ES0150480111	EUR	1	|MERCADOCONTINUO|	f	79298	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0150480111||es||False	f	t	t
PESCANOVA	ES0169350016	EUR	1	|MERCADOCONTINUO|	f	79300	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0169350016||es||False	f	t	t
NR NORDIC RUSSIA	JE00B1G3KL02	EUR	1	|EURONEXT|	f	79302	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#JE00B1G3KL02||nl||False	f	t	t
Data Modul AG	DE0005498901	EUR	1	|DEUTSCHEBOERSE|	f	79291	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005498901||de||False	f	t	t
OCCIDENTAL PETROL.	US6745991058	EUR	1	|EURONEXT|	f	79312	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#US6745991058||nl||False	f	t	t
Delticom AG	DE0005146807	EUR	1	|DEUTSCHEBOERSE|	f	79297	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005146807||de||False	f	t	t
Montpelier Re Holdings Ltd.	\N	USD	1	\N	f	79286	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MRH||us||False	f	t	t
LBI INTERNATIONAL	NL0009508720	EUR	1	|EURONEXT|	f	79358	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009508720||nl||False	f	t	t
Universal Corp.	\N	USD	1	\N	f	79288	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UVV||us||False	f	t	t
MEMC Electronic Materials Inc.	\N	USD	1	\N	f	79290	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WFR||us||False	f	t	t
MasTec Inc.	\N	USD	1	\N	f	79292	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MTZ||us||False	f	t	t
Toyota Motor Corp.	\N	USD	1	\N	f	79305	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TM||us||False	f	t	t
Toronto-Dominion Bank	\N	USD	1	\N	f	79306	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TD||us||False	f	t	t
Grupo Televisa S.A. de C.V.	\N	USD	1	\N	f	79307	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TV||us||False	f	t	t
NATRACEUTICA	ES0165359011	EUR	1	|MERCADOCONTINUO|	f	79333	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0165359011||es||False	f	t	t
NH HOTELES	ES0161560018	EUR	1	|MERCADOCONTINUO|	f	79335	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0161560018||es||False	f	t	t
NICO.CORREA	ES0166300212	EUR	1	|MERCADOCONTINUO|	f	79336	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0166300212||es||False	f	t	t
Texas Instruments Inc.	\N	USD	1	\N	f	79308	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TXN||us||False	f	t	t
PETROBRAS O.	BRPETRACNOR9	EUR	1	|MERCADOCONTINUO|	f	79343	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#BRPETRACNOR9||es||False	f	t	t
PETROBRAS P.	BRPETRACNPR6	EUR	1	|MERCADOCONTINUO|	f	79354	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#BRPETRACNPR6||es||False	f	t	t
PRISA CONV.B	ES0171743042	EUR	1	|MERCADOCONTINUO|	f	79355	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0171743042||es||False	f	t	t
American Tower REIT		USD	1	|SP500|	f	79213					100	c	0	2	None	\N	\N	NYSE#AMT||us||False	f	t	t
Ameriprise Financial Inc.		USD	1	|SP500|	f	79214					100	c	0	2	None	\N	\N	NYSE#AMP||us||False	f	t	t
Alcoa Inc.	US0138171014	USD	1	|SP500|	f	79310					100	c	0	2	AA	{1}	{3}	NYSE#AA||us||False	f	t	t
Obrascon Huarte Laín (OHL) S.A.	ES0142090317	EUR	1	|IBEX|MERCADOCONTINUO|	f	79299					100	c	0	1	OHL.MC	{1}	{3}	MC#ES0142090317||es||False	f	t	t
PINGUINLUT STRVVPR	BE0005618898	EUR	1	|EURONEXT|	f	79323	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005618898||be||False	f	t	t
PINGUINLUTOSA	BE0003765790	EUR	1	|EURONEXT|	f	79326	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003765790||be||False	f	t	t
BATENBURG TECHNIEK	NL0006292906	EUR	1	|EURONEXT|	f	79365	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0006292906||nl||False	f	t	t
UNION PAC CORP	US9078181081	EUR	1	|EURONEXT|	f	79396	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#US9078181081||nl||False	f	t	t
ROTO SMEETS	NL0009169515	EUR	1	|EURONEXT|	f	79411	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009169515||nl||False	f	t	t
USIMINAS ORD	BRUSIMACNOR3	EUR	1	|MERCADOCONTINUO|	f	79377	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#BRUSIMACNOR3||es||False	f	t	t
CAJA LABORAL RENTA FIJA A LARGO	ES0115312037	EUR	2	|BMF|0161|	f	79317	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115312037||es||False	f	t	t
VALE OR.	BRVALEACNOR0	EUR	1	|MERCADOCONTINUO|	f	79382	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#BRVALEACNOR0||es||False	f	t	t
VALE PR.	BRVALEACNPA3	EUR	1	|MERCADOCONTINUO|	f	79387	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#BRVALEACNPA3||es||False	f	t	t
VIDRALA	ES0183746314	EUR	1	|MERCADOCONTINUO|	f	79395	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0183746314||es||False	f	t	t
VISCOFAN	ES0184262212	EUR	1	|MERCADOCONTINUO|	f	79397	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0184262212||es||False	f	t	t
VOLCAN B	PEP648014202	EUR	1	|MERCADOCONTINUO|	f	79398	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#PEP648014202||es||False	f	t	t
VUELING	ES0184591032	EUR	1	|MERCADOCONTINUO|	f	79399	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0184591032||es||False	f	t	t
Demag Cranes AG	DE000DCAG010	EUR	1	|DEUTSCHEBOERSE|	f	79419	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000DCAG010||de||False	f	t	t
WellPoint Inc.	\N	USD	1	\N	f	79378	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WLP||us||False	f	t	t
USIMINAS	BRUSIMACNPA6	EUR	1	|MERCADOCONTINUO|	f	79416	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#BRUSIMACNPA6||es||False	f	t	t
ZARDOYA OTIS	ES0184933812	EUR	1	|MERCADOCONTINUO|	f	79418	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0184933812||es||False	f	t	t
DTE Energy Co.	\N	USD	1	\N	f	79380	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DTE||us||False	f	t	t
LTC Properties Inc.	\N	USD	1	\N	f	79381	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LTC||us||False	f	t	t
ZELTIA	ES0184940817	EUR	1	|MERCADOCONTINUO|	f	79425	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0184940817||es||False	f	t	t
Education Realty Trust Inc.	\N	USD	1	\N	f	79383	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EDR||us||False	f	t	t
WuXi Pharmatech (Cayman) Inc.	\N	USD	1	\N	f	79384	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WX||us||False	f	t	t
Cooper Tire & Rubber Co.	\N	USD	1	\N	f	79385	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CTB||us||False	f	t	t
Fresh Del Monte Produce Inc.	\N	USD	1	\N	f	79386	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FDP||us||False	f	t	t
Monster Worldwide Inc.	\N	USD	1	\N	f	79388	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MWW||us||False	f	t	t
ORCO BSAR 2012	LU0234878881	EUR	1	|EURONEXT|	f	79370	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#LU0234878881||fr||False	f	t	t
SOFTIMAT	BE0003773877	EUR	1	|EURONEXT|	f	79362	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003773877||be||False	f	t	t
D'IETEREN (D)	BE0974259880	EUR	1	|EURONEXT|	f	79373	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0974259880||be||False	f	t	t
TESSENDERLO STRIP	BE0005515839	EUR	1	|EURONEXT|	f	79389	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005515839||be||False	f	t	t
THINK-MEDIA	BE0003804219	EUR	1	|EURONEXT|	f	79392	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003804219||be||False	f	t	t
TRANSICS INT.	BE0003869865	EUR	1	|EURONEXT|	f	79393	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003869865||be||False	f	t	t
RTL GROUP	LU0061462528	EUR	1	|EURONEXT|	f	79414	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#LU0061462528||be||False	f	t	t
FLUXYS CAT.D	BE0003803203	EUR	1	|EURONEXT|	f	79431	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003803203||be||False	f	t	t
Calgon Carbon Corp.	\N	USD	1	\N	f	79391	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CCC||us||False	f	t	t
UniFirst Corp.	\N	USD	1	\N	f	79394	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UNF||us||False	f	t	t
BancorpSouth Inc.	\N	USD	1	\N	f	79400	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BXS||us||False	f	t	t
SWEDISH AUTOMOBILE	NL0009816248	EUR	1	|EURONEXT|	f	79492	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009816248||nl||False	f	t	t
TELEGRAAF MEDIA GR	NL0000386605	EUR	1	|EURONEXT|	f	79494	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000386605||nl||False	f	t	t
Derby Cycle AG	DE000A1H6HN1	EUR	1	|DEUTSCHEBOERSE|	f	79508	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1H6HN1||de||False	f	t	t
Deutsche Beteiligungs AG	DE0005508105	EUR	1	|DEUTSCHEBOERSE|	f	79514	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005508105||de||False	f	t	t
Deutz AG	DE0006305006	EUR	1	|DEUTSCHEBOERSE|	f	79521	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006305006||de||False	f	t	t
Renren Inc. Cl A	\N	USD	1	\N	f	79439	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RENN||us||False	f	t	t
Cohen & Steers Inc.	\N	USD	1	\N	f	79440	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CNS||us||False	f	t	t
American Equity Investment Life Holding Co.	\N	USD	1	\N	f	79441	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AEL||us||False	f	t	t
Adecoagro S.A.	\N	USD	1	\N	f	79443	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AGRO||us||False	f	t	t
Hanger Orthopedic Group Inc.	\N	USD	1	\N	f	79447	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HGR||us||False	f	t	t
Albany International Corp. Cl A	\N	USD	1	\N	f	79448	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AIN||us||False	f	t	t
Fusion-io Inc.	\N	USD	1	\N	f	79450	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FIO||us||False	f	t	t
Analog Devices Inc.		USD	1	|SP500|	f	79379					100	c	0	2	ADI	{1}	{3}	NYSE#ADI||us||False	f	t	t
ARSEUS (D)	BE0003874915	EUR	1	|EURONEXT|	f	79512	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003874915||be||False	f	t	t
GLOBAL GRAPHICS	FR0004152221	EUR	1	|EURONEXT|	f	79527	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#FR0004152221||be||False	f	t	t
Philip Morris International Inc.	\N	USD	1	\N	f	79463	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PM||us||False	f	t	t
Devon Energy Corp.	\N	USD	1	\N	f	79469	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DVN||us||False	f	t	t
ESCO Technologies Inc.	\N	USD	1	\N	f	79470	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ESE||us||False	f	t	t
Orient Express Hotels Ltd.	\N	USD	1	\N	f	79471	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#OEH||us||False	f	t	t
Ryland Group Inc.	\N	USD	1	\N	f	79472	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RYL||us||False	f	t	t
Briggs & Stratton Corp.	\N	USD	1	\N	f	79480	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BGG||us||False	f	t	t
Jones Group Inc.	\N	USD	1	\N	f	79491	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JNY||us||False	f	t	t
Pep Boys-Manny Moe & Jack	\N	USD	1	\N	f	79493	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PBY||us||False	f	t	t
LSB Industries Inc.	\N	USD	1	\N	f	79500	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LXU||us||False	f	t	t
BE SEMICONDUCTOR	NL0000339760	EUR	1	|EURONEXT|	f	79543	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000339760||nl||False	f	t	t
GRONTMIJ	NL0000853034	EUR	1	|EURONEXT|	f	79582	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000853034||nl||False	f	t	t
GROOTHANDELSGEBOUW	NL0000440824	EUR	1	|EURONEXT|	f	79584	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000440824||nl||False	f	t	t
HEINEKEN	NL0000009165	EUR	1	|EURONEXT|	f	79599	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000009165||nl||False	f	t	t
Deutsche Börse tendered shares	DE000A1KRND6	EUR	1	|DEUTSCHEBOERSE|	f	79572	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1KRND6||de||False	f	t	t
Deutsche EuroShop AG	DE0007480204	EUR	1	|DEUTSCHEBOERSE|	f	79573	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007480204||de||False	f	t	t
Deutsche Wohnen AG	DE000A0HN5C6	EUR	1	|DEUTSCHEBOERSE|	f	79625	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0HN5C6||de||False	f	t	t
Aircastle Ltd.	\N	USD	1	\N	f	79545	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AYR||us||False	f	t	t
Freescale Semiconductor Holdings I Ltd.	\N	USD	1	\N	f	79546	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FSL||us||False	f	t	t
Associated Estates Realty Corp.	\N	USD	1	\N	f	79548	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AEC||us||False	f	t	t
Vector Group Ltd.	\N	USD	1	\N	f	79549	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VGR||us||False	f	t	t
Belo Corp. Series A	\N	USD	1	\N	f	79550	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BLC||us||False	f	t	t
Cincinnati Bell Inc.	\N	USD	1	\N	f	79551	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CBB||us||False	f	t	t
CEC Entertainment Inc.	\N	USD	1	\N	f	79552	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CEC||us||False	f	t	t
Employers Holdings Inc.	\N	USD	1	\N	f	79555	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EIG||us||False	f	t	t
Glatfelter	\N	USD	1	\N	f	79556	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GLT||us||False	f	t	t
Pennsylvania Real Estate Investment Trust	\N	USD	1	\N	f	79557	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PEI||us||False	f	t	t
Tootsie Roll Industries Inc.	\N	USD	1	\N	f	79558	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TR||us||False	f	t	t
Stepan Co.	\N	USD	1	\N	f	79576	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SCL||us||False	f	t	t
Johnson Controls Inc.	\N	USD	1	\N	f	79581	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JCI||us||False	f	t	t
Prestige Brands Holdings Inc.	\N	USD	1	\N	f	79586	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PBH||us||False	f	t	t
COURTOIS	FR0000065393	EUR	1	|EURONEXT|	f	79544	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000065393||fr||False	f	t	t
ATENOR GROUP (D)	BE0003837540	EUR	1	|EURONEXT|	f	79542	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003837540||be||False	f	t	t
HOMBURG INVEST A	CA4368714040	EUR	1	|EURONEXT|	f	79669	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#CA4368714040||nl||False	f	t	t
FUGRO	NL0000352565	EUR	1	|EURONEXT|	f	79700	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000352565||nl||False	f	t	t
IBM	US4592001014	EUR	1	|EURONEXT|	f	79711	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#US4592001014||nl||False	f	t	t
ICT AUTOMATISERING	NL0000359537	EUR	1	|EURONEXT|	f	79713	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000359537||nl||False	f	t	t
Deutsche Wohnen AG Na	DE0006283302	EUR	1	|DEUTSCHEBOERSE|	f	79667	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006283302||de||False	f	t	t
DF Deutsche Forfait AG	DE0005488795	EUR	1	|DEUTSCHEBOERSE|	f	79668	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005488795||de||False	f	t	t
SAF AG	CH0024848738	EUR	1	|DEUTSCHEBOERSE|	f	79670	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#CH0024848738||de||False	f	t	t
Dialog Semiconductor plc	GB0059822006	EUR	1	|DEUTSCHEBOERSE|	f	79671	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#GB0059822006||de||False	f	t	t
\N	\N	\N	\N	\N	f	79678	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0175989039||None||False	f	t	t
Standex International Corp.	\N	USD	1	\N	f	79637	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SXI||us||False	f	t	t
Pampa Energia S.A.	\N	USD	1	\N	f	79638	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PAM||us||False	f	t	t
Boyd Gaming Corp.	\N	USD	1	\N	f	79639	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BYD||us||False	f	t	t
Clear Channel Outdoor Holdings Inc.	\N	USD	1	\N	f	79640	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CCO||us||False	f	t	t
Tutor Perini Corp.	\N	USD	1	\N	f	79641	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TPC||us||False	f	t	t
PennyMac Mortgage Investment Trust	\N	USD	1	\N	f	79642	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PMT||us||False	f	t	t
Badger Meter Inc.	\N	USD	1	\N	f	79643	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BMI||us||False	f	t	t
Biglari Holdings Inc.	\N	USD	1	\N	f	79644	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BH||us||False	f	t	t
Goodrich Petroleum Corp.	\N	USD	1	\N	f	79647	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GDP||us||False	f	t	t
Ship Finance International Ltd.	\N	USD	1	\N	f	79661	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SFL||us||False	f	t	t
IBERSOL,SGPS	PTIBS0AM0008	EUR	1	|EURONEXT|	f	79709	\N	\N	\N	\N	100	c	0	9	\N	\N	\N	EURONEXT#PTIBS0AM0008||pt||False	f	t	t
ENCRES DUBUIT	FR0004030708	EUR	1	|EURONEXT|	f	79634	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004030708||fr||False	f	t	t
IBA (D)	BE0003766806	EUR	1	|EURONEXT|	f	79708	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003766806||be||False	f	t	t
FON FINECO INTERES I	ES0164814016	EUR	2	|BMF|0132|	f	79682	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164814016||es||False	f	t	t
NEW SOURCES ENERGY	NL0009822014	EUR	1	|EURONEXT|	f	79796	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009822014||nl||False	f	t	t
KARDAN	NL0000113652	EUR	1	|EURONEXT|	f	79850	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000113652||nl||False	f	t	t
DIC Asset AG	DE0005098404	EUR	1	|DEUTSCHEBOERSE|	f	79755	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005098404||de||False	f	t	t
Fortegra Financial Corp.	\N	USD	1	\N	f	80498	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FRF||us||False	f	t	t
Douglas Holding AG	DE0006099005	EUR	1	|DEUTSCHEBOERSE|	f	79756	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006099005||de||False	f	t	t
Dr. Hönle AG	DE0005157101	EUR	1	|DEUTSCHEBOERSE|	f	79797	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005157101||de||False	f	t	t
Drägerwerk AG & Co. KGaA St 	DE0005550602	EUR	1	|DEUTSCHEBOERSE|	f	79844	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005550602||de||False	f	t	t
Drägerwerk AG & Co. KGaA Vz	DE0005550636	EUR	1	|DEUTSCHEBOERSE|	f	79849	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005550636||de||False	f	t	t
Texas Pacific Land Trust Sub Share Ctf	\N	USD	1	\N	f	79753	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TPL||us||False	f	t	t
Endeavour International Corp.	\N	USD	1	\N	f	79760	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#END||us||False	f	t	t
Hudson Valley Holding Corp.	\N	USD	1	\N	f	79763	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HVB||us||False	f	t	t
PMI Group Inc.	\N	USD	1	\N	f	79764	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PMI||us||False	f	t	t
Lee Enterprises Inc.	\N	USD	1	\N	f	79765	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LEE||us||False	f	t	t
Magnetek Inc.	\N	USD	1	\N	f	79766	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MAG||us||False	f	t	t
PetroQuest Energy Inc.	\N	USD	1	\N	f	79767	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PQ||us||False	f	t	t
Sunrise Senior Living Inc.	\N	USD	1	\N	f	79770	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SRZ||us||False	f	t	t
Excel Trust Inc.	\N	USD	1	\N	f	79771	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EXL||us||False	f	t	t
ExamWorks Group Inc.	\N	USD	1	\N	f	79774	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EXAM||us||False	f	t	t
IMMOB.DASSAULT	FR0000033243	EUR	1	|EURONEXT|	f	79749	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000033243||fr||False	f	t	t
IMMOBETELGEUSE	FR0000036725	EUR	1	|EURONEXT|	f	79750	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000036725||fr||False	f	t	t
IMERYS	FR0000120859	EUR	1	|EURONEXT|	f	79789	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000120859||fr||False	f	t	t
IMMO MOURY (D)	BE0003893139	EUR	1	|EURONEXT|	f	79747	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003893139||be||False	f	t	t
IMPERIAL OIL	BE0004602430	EUR	1	|EURONEXT|	f	79758	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0004602430||be||False	f	t	t
KAS BANK	NL0000362648	EUR	1	|EURONEXT|	f	79856	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000362648||nl||False	f	t	t
CAN PLUSMARCA ACTIVA	ES0115707038	EUR	2	|BMF|0128|	f	79813	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115707038||es||False	f	t	t
KENDRION	NL0000852531	EUR	1	|EURONEXT|	f	79865	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000852531||nl||False	f	t	t
Drillisch AG	DE0005545503	EUR	1	|DEUTSCHEBOERSE|	f	79918	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005545503||de||False	f	t	t
Dole Food Co. Inc.	\N	USD	1	\N	f	79852	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DOLE||us||False	f	t	t
RealD Inc.	\N	USD	1	\N	f	79853	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RLD||us||False	f	t	t
Assisted Living Concepts Inc. Cl A	\N	USD	1	\N	f	79855	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ALC||us||False	f	t	t
RailAmerica Inc.	\N	USD	1	\N	f	79857	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RA||us||False	f	t	t
Safeguard Scientifics Inc.	\N	USD	1	\N	f	79864	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SFE||us||False	f	t	t
SJW Corp.	\N	USD	1	\N	f	79874	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SJW||us||False	f	t	t
Quad/Graphics Inc.	\N	USD	1	\N	f	79875	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#QUAD||us||False	f	t	t
Callon Petroleum Co.	\N	USD	1	\N	f	79876	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CPE||us||False	f	t	t
Zep Inc.	\N	USD	1	\N	f	79879	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ZEP||us||False	f	t	t
China Kanghui Holdings	\N	USD	1	\N	f	79882	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KH||us||False	f	t	t
Campus Crest Communities Inc.	\N	USD	1	\N	f	79883	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CCG||us||False	f	t	t
Pros Holdings Inc.	\N	USD	1	\N	f	79884	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PRO||us||False	f	t	t
IntraLinks Holdings Inc.	\N	USD	1	\N	f	79885	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IL||us||False	f	t	t
Harvest Natural Resources Inc.	\N	USD	1	\N	f	79886	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HNR||us||False	f	t	t
American Reprographics Co.	\N	USD	1	\N	f	79889	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ARC||us||False	f	t	t
Capital Senior Living Corp.	\N	USD	1	\N	f	79892	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CSU||us||False	f	t	t
Genco Shipping & Trading Ltd.	\N	USD	1	\N	f	79893	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GNK||us||False	f	t	t
NCI Building Systems Inc.	\N	USD	1	\N	f	79894	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NCS||us||False	f	t	t
KBC	BE0003565737	EUR	1	|EURONEXT|	f	79861	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003565737||be||False	f	t	t
KBC ANCORA	BE0003867844	EUR	1	|EURONEXT|	f	79862	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003867844||be||False	f	t	t
KINEPOLIS GROUP	BE0003722361	EUR	1	|EURONEXT|	f	79887	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003722361||be||False	f	t	t
BALLAST NEDAM	NL0000336543	EUR	1	|EURONEXT|	f	79967	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000336543||nl||False	f	t	t
BAM GROEP KON	NL0000337319	EUR	1	|EURONEXT|	f	79968	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000337319||nl||False	f	t	t
BAWAG CAP  7,125PL	DE0008600966	EUR	1	|EURONEXT|	f	79975	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#DE0008600966||nl||False	f	t	t
BETER BED	NL0000339703	EUR	1	|EURONEXT|	f	80008	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000339703||nl||False	f	t	t
NIEUWE STEEN INV	NL0000292324	EUR	1	|EURONEXT|	f	80014	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000292324||nl||False	f	t	t
NUTRECO	NL0000375400	EUR	1	|EURONEXT|	f	80024	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000375400||nl||False	f	t	t
Suntech Power Holdings Co. Ltd.	\N	USD	1	\N	f	79969	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#STP||us||False	f	t	t
GFI Group Inc.	\N	USD	1	\N	f	79972	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GFIG||us||False	f	t	t
Kite Realty Group Trust	\N	USD	1	\N	f	79976	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KRG||us||False	f	t	t
Kadant Inc.	\N	USD	1	\N	f	79980	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KAI||us||False	f	t	t
Apollo Commercial Real Estate Finance Inc.	\N	USD	1	\N	f	79981	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ARI||us||False	f	t	t
Saul Centers Inc.	\N	USD	1	\N	f	79982	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BFS||us||False	f	t	t
LeapFrog Enterprises Inc. Cl A	\N	USD	1	\N	f	79984	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LF||us||False	f	t	t
CapLease Inc.	\N	USD	1	\N	f	79985	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LSE||us||False	f	t	t
Navios Maritime Holdings Inc.	\N	USD	1	\N	f	79988	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NM||us||False	f	t	t
BACCARAT	FR0000064123	EUR	1	|EURONEXT|	f	79964	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064123||fr||False	f	t	t
BAINS MER MONACO	MC0000031187	EUR	1	|EURONEXT|	f	79966	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#MC0000031187||fr||False	f	t	t
MALTERIES FCO-BEL.	FR0000030074	EUR	1	|EURONEXT|	f	79990	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000030074||fr||False	f	t	t
MEDASYS BS1	FR0011162536	EUR	1	|EURONEXT|	f	79997	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011162536||fr||False	f	t	t
BEKAERT STRIP (D)	BE0005640140	EUR	1	|EURONEXT|	f	79987	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005640140||be||False	f	t	t
Douglas Dynamics Inc.	\N	USD	1	\N	f	79992	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PLOW||us||False	f	t	t
Qihoo 360 Technology Co. Ltd.	\N	USD	1	\N	f	79995	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#QIHU||us||False	f	t	t
SunCoke Energy Inc.	\N	USD	1	\N	f	80009	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SXC||us||False	f	t	t
Steinway Musical Instruments Inc.	\N	USD	1	\N	f	80010	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LVB||us||False	f	t	t
MoneyGram International Inc.	\N	USD	1	\N	f	80011	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MGI||us||False	f	t	t
Revlon Inc. Cl A	\N	USD	1	\N	f	80012	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#REV||us||False	f	t	t
Rex American Resources Corp.	\N	USD	1	\N	f	80013	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#REX||us||False	f	t	t
Systemax Inc.	\N	USD	1	\N	f	80017	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SYX||us||False	f	t	t
Orion Marine Group Inc.	\N	USD	1	\N	f	80018	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ORN||us||False	f	t	t
ORANJEWOUD A	NL0000370419	EUR	1	|EURONEXT|	f	80071	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000370419||nl||False	f	t	t
IBERCAJA CONSERVADOR, CLASE C	ES0146792025	EUR	2	|f_es_BMF|	f	79961					100	c	0	1	None	{2}	\N	ES0146792025||None||False	f	t	t
STERN GROEP	NL0000336303	EUR	1	|EURONEXT|	f	80121	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000336303||nl||False	f	t	t
Dürr AG	DE0005565204	EUR	1	|DEUTSCHEBOERSE|	f	80082	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005565204||de||False	f	t	t
Dyckerhoff AG St	DE0005591002	EUR	1	|DEUTSCHEBOERSE|	f	80096	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005591002||de||False	f	t	t
Dyckerhoff AG Vz	DE0005591036	EUR	1	|DEUTSCHEBOERSE|	f	80097	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005591036||de||False	f	t	t
EADS N.V.	NL0000235190	EUR	1	|DEUTSCHEBOERSE|	f	80104	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#NL0000235190||de||False	f	t	t
ECKERT & ZIEGLER AG	DE0005659700	EUR	1	|DEUTSCHEBOERSE|	f	80105	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005659700||de||False	f	t	t
Einhell Germany AG	DE0005654933	EUR	1	|DEUTSCHEBOERSE|	f	80162	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005654933||de||False	f	t	t
Chatham Lodging Trust	\N	USD	1	\N	f	80063	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CLDT||us||False	f	t	t
SeaCube Container Leasing Ltd.	\N	USD	1	\N	f	80064	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BOX||us||False	f	t	t
FXCM Inc.	\N	USD	1	\N	f	80065	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FXCM||us||False	f	t	t
Primero Mining Corp.	\N	USD	1	\N	f	80068	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PPP||us||False	f	t	t
Met-Pro Corp.	\N	USD	1	\N	f	80095	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MPR||us||False	f	t	t
Ducommun Inc.	\N	USD	1	\N	f	80098	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DCO||us||False	f	t	t
MRBRICOLAGEBSAAR14	FR0010814186	EUR	1	|EURONEXT|	f	80062	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010814186||fr||False	f	t	t
NERGECO	FR0000037392	EUR	1	|EURONEXT|	f	80066	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000037392||fr||False	f	t	t
RUE DU COMMERCE	FR0011163815	EUR	1	|EURONEXT|	f	80067	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011163815||fr||False	f	t	t
SII	FR0000074122	EUR	1	|EURONEXT|	f	80091	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000074122||fr||False	f	t	t
SILIC	FR0000050916	EUR	1	|EURONEXT|	f	80092	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000050916||fr||False	f	t	t
SABCA (D)	BE0003654655	EUR	1	|EURONEXT|	f	80077	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003654655||be||False	f	t	t
TUBIZE-FIN	BE0003823409	EUR	1	|EURONEXT|	f	80129	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003823409||be||False	f	t	t
IDT Corp. Cl B	\N	USD	1	\N	f	80100	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IDT||us||False	f	t	t
International Shipholding Corp.	\N	USD	1	\N	f	80101	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ISH||us||False	f	t	t
Pike Electric Corp.	\N	USD	1	\N	f	80111	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PIKE||us||False	f	t	t
Artio Global Investors Inc. Cl A	\N	USD	1	\N	f	80119	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ART||us||False	f	t	t
Walker & Dunlop Inc.	\N	USD	1	\N	f	80122	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WD||us||False	f	t	t
Primus Telecommunications Group Inc.	\N	USD	1	\N	f	80123	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PTGI||us||False	f	t	t
TMS International Corp. Cl A	\N	USD	1	\N	f	80124	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TMS||us||False	f	t	t
Teavana Holdings Inc.	\N	USD	1	\N	f	80125	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TEA||us||False	f	t	t
Franklin Covey Co.	\N	USD	1	\N	f	80126	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FC||us||False	f	t	t
Schawk Inc.	\N	USD	1	\N	f	80142	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SGK||us||False	f	t	t
DSM KON	NL0000009827	EUR	1	|EURONEXT|	f	80190	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000009827||nl||False	f	t	t
LOGICA	GB0005227086	EUR	1	|EURONEXT|	f	80207	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GB0005227086||nl||False	f	t	t
WITTE MOLEN	NL0009767540	EUR	1	|EURONEXT|	f	80237	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009767540||nl||False	f	t	t
WOLTERS KLUWER	NL0000395903	EUR	1	|EURONEXT|	f	80238	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000395903||nl||False	f	t	t
Electronics Line 3000 Ltd.	IL0010905052	EUR	1	|DEUTSCHEBOERSE|	f	80163	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#IL0010905052||de||False	f	t	t
E.ON AG	DE000ENAG999	EUR	1	|DAX|DEUTSCHEBOERSE|EUROSTOXX|	f	80103					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE000ENAG999||de||False	f	t	t
ELMOS Semiconductor AG	DE0005677108	EUR	1	|DEUTSCHEBOERSE|	f	80174	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005677108||de||False	f	t	t
\N	\N	\N	\N	\N	f	80239	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0181397003||None||False	f	t	t
ElringKlinger AG	DE0007856023	EUR	1	|DEUTSCHEBOERSE|	f	80175	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007856023||de||False	f	t	t
AUSYBSAAR20OCT16	FR0010805366	EUR	1	|EURONEXT|	f	80166	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010805366||fr||False	f	t	t
DEXIA STRIP	BE0005587580	EUR	1	|EURONEXT|	f	80179	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005587580||be||False	f	t	t
DRDGOLD CERT.BELG.	BE0004520582	EUR	1	|EURONEXT|	f	80188	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0004520582||be||False	f	t	t
VGP	BE0003878957	EUR	1	|EURONEXT|	f	80195	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003878957||be||False	f	t	t
LOTUS BAKERIES	BE0003604155	EUR	1	|EURONEXT|	f	80227	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003604155||be||False	f	t	t
EnviTec Biogas AG	DE000A0MVLS8	EUR	1	|DEUTSCHEBOERSE|	f	80181	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0MVLS8||de||False	f	t	t
Epigenomics AG	DE000A1K0516	EUR	1	|DEUTSCHEBOERSE|	f	80200	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1K0516||de||False	f	t	t
H&R AG	DE0007757007	EUR	1	|DEUTSCHEBOERSE|	f	80203	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007757007||de||False	f	t	t
HAMBORNER REIT AG	DE0006013006	EUR	1	|DEUTSCHEBOERSE|	f	80204	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006013006||de||False	f	t	t
ESSANELLE HAIR GROUP AG	DE0006610314	EUR	1	|DEUTSCHEBOERSE|	f	80233	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006610314||de||False	f	t	t
Fresenius SE & Co. KGaA 	DE0005785604	EUR	1	|DEUTSCHEBOERSE|	f	80234	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005785604||de||False	f	t	t
Fuchs Petrolub AG St	DE0005790406	EUR	1	|DEUTSCHEBOERSE|	f	80235	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005790406||de||False	f	t	t
Fuchs Petrolub AG Vz	DE0005790430	EUR	1	|DEUTSCHEBOERSE|	f	80236	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005790430||de||False	f	t	t
Homag Group AG	DE0005297204	EUR	1	|DEUTSCHEBOERSE|	f	80247	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005297204||de||False	f	t	t
Country Style Cooking Restaurant Chain Co. Ltd.	\N	USD	1	\N	f	80167	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CCSC||us||False	f	t	t
Xueda Education Group	\N	USD	1	\N	f	80169	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#XUE||us||False	f	t	t
Red Lion Hotels Corp.	\N	USD	1	\N	f	80170	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RLH||us||False	f	t	t
MPG Office Trust Inc.	\N	USD	1	\N	f	80171	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MPG||us||False	f	t	t
Oil-Dri Corp. of America	\N	USD	1	\N	f	80172	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ODC||us||False	f	t	t
Gramercy Capital Corp.	\N	USD	1	\N	f	80176	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GKK||us||False	f	t	t
NL Industries Inc.	\N	USD	1	\N	f	80177	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NL||us||False	f	t	t
Cash Store Financial Services Inc.	\N	USD	1	\N	f	80209	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CSFS||us||False	f	t	t
NEDSENSE ENTERPR	NL0009312842	EUR	1	|EURONEXT|	f	80275	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009312842||nl||False	f	t	t
\N	\N	\N	\N	\N	f	80304	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0165269004||None||False	f	t	t
\N	\N	\N	\N	\N	f	80332	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0165241003||None||False	f	t	t
HORNBACH HOLDING AG	DE0006083439	EUR	1	|DEUTSCHEBOERSE|	f	80251	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006083439||de||False	f	t	t
HORNBACH-Baumarkt-AG	DE0006084403	EUR	1	|DEUTSCHEBOERSE|	f	80255	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006084403||de||False	f	t	t
CLIFFS	US18683K1016	EUR	1	|EURONEXT|	f	80256	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#US18683K1016||fr||False	f	t	t
CBOISSAUVWE15(1P1)	BE0006463617	EUR	1	|EURONEXT|	f	80253	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0006463617||be||False	f	t	t
REALDOLM 1/100 TMP	BE0003732469	EUR	1	|EURONEXT|	f	80310	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003732469||be||False	f	t	t
REALDOLM STRIP (D)	BE0005630042	EUR	1	|EURONEXT|	f	80311	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005630042||be||False	f	t	t
REALDOLMEN (D)	BE0003899193	EUR	1	|EURONEXT|	f	80313	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003899193||be||False	f	t	t
Hugo Boss AG Vz	DE0005245534	EUR	1	|DEUTSCHEBOERSE|	f	80264	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005245534||de||False	f	t	t
Hypoport AG	DE0005493365	EUR	1	|DEUTSCHEBOERSE|	f	80265	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005493365||de||False	f	t	t
IFM Immobilien AG	DE000A0JDU97	EUR	1	|DEUTSCHEBOERSE|	f	80267	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0JDU97||de||False	f	t	t
Indus Holding AG	DE0006200108	EUR	1	|DEUTSCHEBOERSE|	f	80270	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006200108||de||False	f	t	t
init innovation in traffic systems AG	DE0005759807	EUR	1	|DEUTSCHEBOERSE|	f	80274	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005759807||de||False	f	t	t
Hamburger Hafen und Logistik AG	DE000A0S8488	EUR	1	|DEUTSCHEBOERSE|	f	80286	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0S8488||de||False	f	t	t
Hannover Rückversicherung AG	DE0008402215	EUR	1	|DEUTSCHEBOERSE|	f	80287	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0008402215||de||False	f	t	t
Höft & Wessel AG	DE0006011000	EUR	1	|DEUTSCHEBOERSE|	f	80288	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006011000||de||False	f	t	t
itelligence AG	DE0007300402	EUR	1	|DEUTSCHEBOERSE|	f	80320	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007300402||de||False	f	t	t
BankAtlantic Bancorp Inc. Cl A	\N	USD	1	\N	f	80249	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BBX||us||False	f	t	t
Dover Downs Gaming & Entertainment Inc.	\N	USD	1	\N	f	80250	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DDE||us||False	f	t	t
Maui Land & Pineapple Co. Inc.	\N	USD	1	\N	f	80254	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MLP||us||False	f	t	t
Tata Communications Ltd.	\N	USD	1	\N	f	80294	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TCL||us||False	f	t	t
Winthrop Realty Trust	\N	USD	1	\N	f	80296	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FUR||us||False	f	t	t
Thermon Group Holdings Inc.	\N	USD	1	\N	f	80358	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#THR||us||False	f	t	t
Fabrinet	\N	USD	1	\N	f	80312	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#FN||us||False	f	t	t
Universal Technical Institute Inc.	\N	USD	1	\N	f	80317	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UTI||us||False	f	t	t
Brookfield Residential Properties Inc.	\N	USD	1	\N	f	80318	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BRP||us||False	f	t	t
EnergySolutions Inc.	\N	USD	1	\N	f	80319	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ES||us||False	f	t	t
E.W. Scripps Co. Cl A	\N	USD	1	\N	f	80325	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SSP||us||False	f	t	t
Cal Dive International Inc.	\N	USD	1	\N	f	80340	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DVR||us||False	f	t	t
CTAC	NL0000345577	EUR	1	|EURONEXT|	f	80344	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000345577||nl||False	f	t	t
BINCKBANK	NL0000335578	EUR	1	|EURONEXT|	f	80383	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000335578||nl||False	f	t	t
DICO INTERNATIONAL	NL0009733351	EUR	1	|EURONEXT|	f	80390	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009733351||nl||False	f	t	t
EGO-LIFESTYLE	NL0009127547	EUR	1	|EURONEXT|	f	80410	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009127547||nl||False	f	t	t
EUROCOMMERCIAL	NL0000288876	EUR	1	|EURONEXT|	f	80421	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000288876||nl||False	f	t	t
MOLOGEN AG	DE0006637200	EUR	1	|DEUTSCHEBOERSE|	f	80391	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006637200||de||False	f	t	t
MorphoSys AG	DE0006632003	EUR	1	|DEUTSCHEBOERSE|	f	80394	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006632003||de||False	f	t	t
MPC AG	DE0005187603	EUR	1	|DEUTSCHEBOERSE|	f	80397	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005187603||de||False	f	t	t
MTU Aero Engines Holding AG	DE000A0D9PT0	EUR	1	|DEUTSCHEBOERSE|	f	80400	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0D9PT0||de||False	f	t	t
Mühlbauer Holding AG & Co. KGaA	DE0006627201	EUR	1	|DEUTSCHEBOERSE|	f	80406	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006627201||de||False	f	t	t
DIGIGRAM	FR0000035784	EUR	1	|EURONEXT|	f	80345	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000035784||fr||False	f	t	t
COLRUYT STRIP (D)	BE0005637112	EUR	1	|EURONEXT|	f	80356	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005637112||be||False	f	t	t
COFINIMMO-SICAFI	BE0003593044	EUR	1	|EURONEXT|	f	80387	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003593044||be||False	f	t	t
ENVIPCO (D)	NL0009901610	EUR	1	|EURONEXT|	f	80416	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#NL0009901610||be||False	f	t	t
EURONAV	BE0003816338	EUR	1	|EURONEXT|	f	80435	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003816338||be||False	f	t	t
MVV Energie AG	DE000A0H52F5	EUR	1	|DEUTSCHEBOERSE|	f	80408	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0H52F5||de||False	f	t	t
Nemetschek AG	DE0006452907	EUR	1	|DEUTSCHEBOERSE|	f	80409	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006452907||de||False	f	t	t
NEXUS AG	DE0005220909	EUR	1	|DEUTSCHEBOERSE|	f	80412	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005220909||de||False	f	t	t
Nordex SE	DE000A0D6554	EUR	1	|DEUTSCHEBOERSE|	f	80424	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0D6554||de||False	f	t	t
NORMA Group AG	DE000A1H8BV3	EUR	1	|DEUTSCHEBOERSE|	f	80427	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1H8BV3||de||False	f	t	t
NOVEMBER AG	DE000A0Z24E9	EUR	1	|DEUTSCHEBOERSE|	f	80431	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0Z24E9||de||False	f	t	t
Westwood Holdings Group Inc.	\N	USD	1	\N	f	80352	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WHG||us||False	f	t	t
C&J Energy Services Inc.	\N	USD	1	\N	f	80360	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CJES||us||False	f	t	t
Teekay Tankers Ltd.	\N	USD	1	\N	f	80382	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TNK||us||False	f	t	t
BBVA Banco Frances S.A.	\N	USD	1	\N	f	80386	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BFR||us||False	f	t	t
Cenveo Inc.	\N	USD	1	\N	f	80389	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CVO||us||False	f	t	t
Tsakos Energy Navigation Ltd.	\N	USD	1	\N	f	80422	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TNP||us||False	f	t	t
Nam Tai Electronics Inc.	\N	USD	1	\N	f	80423	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NTE||us||False	f	t	t
Metals USA Holdings Corp.	\N	USD	1	\N	f	80426	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MUSA||us||False	f	t	t
Apollo Residential Mortgage Inc.	\N	USD	1	\N	f	80428	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AMTG||us||False	f	t	t
Spartech Corp.	\N	USD	1	\N	f	80430	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SEH||us||False	f	t	t
Equal Energy Ltd.	\N	USD	1	\N	f	80432	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EQU||us||False	f	t	t
REED ELSEVIER	NL0006144495	EUR	1	|EURONEXT|	f	80459	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0006144495||nl||False	f	t	t
MICROSOFT CORP SPL	US5949181045	EUR	1	|EURONEXT|	f	80529	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#US5949181045||nl||False	f	t	t
HES BEHEER	NL0000358125	EUR	1	|EURONEXT|	f	80538	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000358125||nl||False	f	t	t
OHB AG	DE0005936124	EUR	1	|DEUTSCHEBOERSE|	f	80455	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005936124||de||False	f	t	t
FAUVET GIREL	FR0000063034	EUR	1	|EURONEXT|	f	80439	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000063034||fr||False	f	t	t
RENTABILIWEB (D)	BE0946620946	EUR	1	|EURONEXT|	f	80461	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0946620946||be||False	f	t	t
RESILUX	BE0003707214	EUR	1	|EURONEXT|	f	80474	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003707214||be||False	f	t	t
RETAIL EST.-SICAFI	BE0003720340	EUR	1	|EURONEXT|	f	80476	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003720340||be||False	f	t	t
HENEX	BE0003873909	EUR	1	|EURONEXT|	f	80536	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003873909||be||False	f	t	t
HOME INV.BELG-SIFI	BE0003760742	EUR	1	|EURONEXT|	f	80549	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003760742||be||False	f	t	t
ORCO Germany S.A.	LU0251710041	EUR	1	|DEUTSCHEBOERSE|	f	80457	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#LU0251710041||de||False	f	t	t
OVB Holding AG	DE0006286560	EUR	1	|DEUTSCHEBOERSE|	f	80458	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006286560||de||False	f	t	t
3W Power S.A.	GG00B39QCR01	EUR	1	|DEUTSCHEBOERSE|	f	80470	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#GG00B39QCR01||de||False	f	t	t
4SC AG	DE0005753818	EUR	1	|DEUTSCHEBOERSE|	f	80471	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005753818||de||False	f	t	t
aap Implantate AG	DE0005066609	EUR	1	|DEUTSCHEBOERSE|	f	80472	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005066609||de||False	f	t	t
ad pepper media International N.V.	NL0000238145	EUR	1	|DEUTSCHEBOERSE|	f	80473	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#NL0000238145||de||False	f	t	t
Adler Modemärkte AG	DE000A1H8MU2	EUR	1	|DEUTSCHEBOERSE|	f	80478	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1H8MU2||de||False	f	t	t
ADVA AG Optical Networking	DE0005103006	EUR	1	|DEUTSCHEBOERSE|	f	80480	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005103006||de||False	f	t	t
AGENNIX AG	DE000A1A6XX4	EUR	1	|DEUTSCHEBOERSE|	f	80482	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1A6XX4||de||False	f	t	t
All for One Midmarket AG	DE0005110001	EUR	1	|DEUTSCHEBOERSE|	f	80514	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005110001||de||False	f	t	t
Alphaform AG	DE0005487953	EUR	1	|DEUTSCHEBOERSE|	f	80516	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005487953||de||False	f	t	t
JinkoSolar Holding Co. Ltd.	\N	USD	1	\N	f	80486	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#JKS||us||False	f	t	t
Bitauto Holdings Ltd.	\N	USD	1	\N	f	80487	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BITA||us||False	f	t	t
Pacific Drilling S.A.	\N	USD	1	\N	f	80488	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PACD||us||False	f	t	t
Urstadt Biddle Properties Inc.	\N	USD	1	\N	f	80490	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#UBP||us||False	f	t	t
Alon Holdings-Blue Square-Israel Ltd.	\N	USD	1	\N	f	80492	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BSI||us||False	f	t	t
BlueLinx Holdings Inc.	\N	USD	1	\N	f	80493	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BXC||us||False	f	t	t
China Green Agriculture Inc.	\N	USD	1	\N	f	80523	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CGA||us||False	f	t	t
DHT Holdings Inc.	\N	USD	1	\N	f	80527	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DHT||us||False	f	t	t
China Nepstar Chain Drugstore Ltd.	\N	USD	1	\N	f	80528	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#NPD||us||False	f	t	t
American Oriental Bioengineering Inc.	\N	USD	1	\N	f	80533	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AOB||us||False	f	t	t
Bluegreen Corp.	\N	USD	1	\N	f	80537	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BXG||us||False	f	t	t
Media General Inc. Cl A	\N	USD	1	\N	f	80540	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MEG||us||False	f	t	t
Kid Brands Inc.	\N	USD	1	\N	f	80547	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#KID||us||False	f	t	t
Theragenics Corp.	\N	USD	1	\N	f	80548	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TGX||us||False	f	t	t
HUNTER DOUGLAS	ANN4327C1303	EUR	1	|EURONEXT|	f	80567	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#ANN4327C1303||nl||False	f	t	t
HYDRATEC	NL0009391242	EUR	1	|EURONEXT|	f	80589	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009391242||nl||False	f	t	t
INTEL CORP	US4581401001	EUR	1	|EURONEXT|	f	80592	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#US4581401001||nl||False	f	t	t
MEDIQ	NL0009103530	EUR	1	|EURONEXT|	f	80663	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0009103530||nl||False	f	t	t
BB Biotech AG	CH0038389992	EUR	1	|DEUTSCHEBOERSE|	f	80554	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#CH0038389992||de||False	f	t	t
Beate Uhse AG	DE0007551400	EUR	1	|DEUTSCHEBOERSE|	f	80555	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007551400||de||False	f	t	t
Bechtle AG	DE0005158703	EUR	1	|DEUTSCHEBOERSE|	f	80556	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005158703||de||False	f	t	t
Bertrandt AG	DE0005232805	EUR	1	|DEUTSCHEBOERSE|	f	80558	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005232805||de||False	f	t	t
P&I Personal & Informatik AG	DE0006913403	EUR	1	|DEUTSCHEBOERSE|	f	80580	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006913403||de||False	f	t	t
PAION AG	DE000A0B65S3	EUR	1	|DEUTSCHEBOERSE|	f	80581	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0B65S3||de||False	f	t	t
PNE WIND AG	DE000A0JBPG2	EUR	1	|DEUTSCHEBOERSE|	f	80582	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0JBPG2||de||False	f	t	t
POLIS Immobilien AG	DE0006913304	EUR	1	|DEUTSCHEBOERSE|	f	80583	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006913304||de||False	f	t	t
\N	\N	\N	\N	\N	f	80658	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0170417010||None||False	f	t	t
NET SERVIÇOS	BRNETCACNPR3	EUR	1	|MERCADOCONTINUO|	f	80662	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#BRNETCACNPR3||es||False	f	t	t
HOTELS DE PARIS	FR0004165801	EUR	1	|EURONEXT|	f	80563	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004165801||fr||False	f	t	t
IBA STRIP (D)	BE0005563342	EUR	1	|EURONEXT|	f	80590	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005563342||be||False	f	t	t
JENSEN-GROUP	BE0003858751	EUR	1	|EURONEXT|	f	80597	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003858751||be||False	f	t	t
MDXHEALTH	BE0003844611	EUR	1	|EURONEXT|	f	80632	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003844611||be||False	f	t	t
MELEXIS (D)	BE0165385973	EUR	1	|EURONEXT|	f	80642	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0165385973||be||False	f	t	t
MOURY CONSTRUCT	BE0003602134	EUR	1	|EURONEXT|	f	80664	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003602134||be||False	f	t	t
Powerland AG	DE000PLD5558	EUR	1	|DEUTSCHEBOERSE|	f	80584	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000PLD5558||de||False	f	t	t
Praktiker AG	DE000A0F6MD5	EUR	1	|DEUTSCHEBOERSE|	f	80585	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0F6MD5||de||False	f	t	t
Prime Office AG	DE000PRME012	EUR	1	|DEUTSCHEBOERSE|	f	80586	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000PRME012||de||False	f	t	t
PROCON MultiMedia AG	DE0005122006	EUR	1	|DEUTSCHEBOERSE|	f	80588	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005122006||de||False	f	t	t
Kabel Deutschland Holding AG	DE000KD88880	EUR	1	|DEUTSCHEBOERSE|	f	80621	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000KD88880||de||False	f	t	t
Klöckner & Co SE	DE000KC01000	EUR	1	|DEUTSCHEBOERSE|	f	80623	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000KC01000||de||False	f	t	t
Logwin AG	LU0106198319	EUR	1	|DEUTSCHEBOERSE|	f	80624	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#LU0106198319||de||False	f	t	t
Startek Inc.	\N	USD	1	\N	f	80593	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SRT||us||False	f	t	t
Maxcom Telecomunicaciones S.A.B. de C.V.	\N	USD	1	\N	f	80595	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MXT||us||False	f	t	t
AGRIA Corp.	\N	USD	1	\N	f	80596	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GRO||us||False	f	t	t
General Steel Holdings Inc.	\N	USD	1	\N	f	80598	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#GSI||us||False	f	t	t
China Distance Education Holdings Ltd.	\N	USD	1	\N	f	80599	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DL||us||False	f	t	t
NEWAYS ELECTRONICS	NL0000440618	EUR	1	|EURONEXT|	f	80673	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000440618||nl||False	f	t	t
OCTOPLUS	NL0000345718	EUR	1	|EURONEXT|	f	80697	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000345718||nl||False	f	t	t
PEPSICO	US7134481081	EUR	1	|EURONEXT|	f	80747	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#US7134481081||nl||False	f	t	t
PUMA SE	DE0006969603	EUR	1	|DEUTSCHEBOERSE|	f	80665	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006969603||de||False	f	t	t
PVA TePla AG	DE0007461006	EUR	1	|DEUTSCHEBOERSE|	f	80666	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007461006||de||False	f	t	t
Beiersdorf Aktiengesellschaft	DE0005200000	EUR	1	|DAX|DEUTSCHEBOERSE|	f	80557					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE0005200000||de||False	f	t	t
Princess Private Equity Holding Limited	DE000A0LBRM2	EUR	1	|DEUTSCHEBOERSE|	f	80684	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0LBRM2||de||False	f	t	t
PSI Aktiengesellschaft	DE000A0Z1JH9	EUR	1	|DEUTSCHEBOERSE|	f	80686	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0Z1JH9||de||False	f	t	t
PULSION Medical Systems AG	DE0005487904	EUR	1	|DEUTSCHEBOERSE|	f	80688	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005487904||de||False	f	t	t
Q-CELLS SE	DE0005558662	EUR	1	|DEUTSCHEBOERSE|	f	80703	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005558662||de||False	f	t	t
QSC AG	DE0005137004	EUR	1	|DEUTSCHEBOERSE|	f	80704	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005137004||de||False	f	t	t
RHÖN-KLINIKUM AG	DE0007042301	EUR	1	|DEUTSCHEBOERSE|	f	80736	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007042301||de||False	f	t	t
Rofin-Sinar Technologies Inc.	US7750431022	EUR	1	|DEUTSCHEBOERSE|	f	80737	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#US7750431022||de||False	f	t	t
Roth & Rau AG	DE000A0JCZ51	EUR	1	|DEUTSCHEBOERSE|	f	80739	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0JCZ51||de||False	f	t	t
R. Stahl AG	DE0007257727	EUR	1	|DEUTSCHEBOERSE|	f	80757	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007257727||de||False	f	t	t
Rational AG	DE0007010803	EUR	1	|DEUTSCHEBOERSE|	f	80758	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007010803||de||False	f	t	t
REALTECH AG	DE0007008906	EUR	1	|DEUTSCHEBOERSE|	f	80759	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007008906||de||False	f	t	t
MP NIGERIA	FR0011120914	EUR	1	|EURONEXT|	f	80671	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011120914||fr||False	f	t	t
NEXITY	FR0010112524	EUR	1	|EURONEXT|	f	80674	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010112524||fr||False	f	t	t
NEXTRADIOTV	FR0010240994	EUR	1	|EURONEXT|	f	80675	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010240994||fr||False	f	t	t
MOURY STRIP	BE0005521894	EUR	1	|EURONEXT|	f	80667	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005521894||be||False	f	t	t
NEUFCOUR-FIN.	BE0003680916	EUR	1	|EURONEXT|	f	80672	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003680916||be||False	f	t	t
OIM	GB00B063YS85	EUR	1	|EURONEXT|	f	80707	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#GB00B063YS85||be||False	f	t	t
OMEGA PHARMA	BE0003785020	EUR	1	|EURONEXT|	f	80712	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003785020||be||False	f	t	t
ORCOBSAAR1219	XS0290764728	EUR	1	|EURONEXT|	f	80715	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#XS0290764728||be||False	f	t	t
PAYTON PLANAR	IL0010830391	EUR	1	|EURONEXT|	f	80745	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#IL0010830391||be||False	f	t	t
PICANOL ST VVPR(D)	BE0005631057	EUR	1	|EURONEXT|	f	80749	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005631057||be||False	f	t	t
WEGENER	NL0000394567	EUR	1	|EURONEXT|	f	80806	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000394567||nl||False	f	t	t
VAN LANSCHOT	NL0000302636	EUR	1	|EURONEXT|	f	80823	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000302636||nl||False	f	t	t
VASTNED RETAIL	NL0000288918	EUR	1	|EURONEXT|	f	80824	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000288918||nl||False	f	t	t
WERELDHAVE	NL0000289213	EUR	1	|EURONEXT|	f	80855	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000289213||nl||False	f	t	t
WESSANEN KON	NL0000395317	EUR	1	|EURONEXT|	f	80859	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000395317||nl||False	f	t	t
XEIKON	NL0006007247	EUR	1	|EURONEXT|	f	80860	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0006007247||nl||False	f	t	t
YATRA	JE00B1FBT077	EUR	1	|EURONEXT|	f	80862	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#JE00B1FBT077||nl||False	f	t	t
BAYER	DE000BAY0017	EUR	1	|MERCADOCONTINUO|	f	80820	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#DE000BAY0017||es||False	f	t	t
Reply Deutschland AG	DE0005501456	EUR	1	|DEUTSCHEBOERSE|	f	80760	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005501456||de||False	f	t	t
BIOSEARCH	ES0172233118	EUR	1	|MERCADOCONTINUO|	f	80839	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0172233118||es||False	f	t	t
BRADESPAR PR	BRBRAPACNPR2	EUR	1	|MERCADOCONTINUO|	f	80844	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#BRBRAPACNPR2||es||False	f	t	t
BRASKEM PR.A	BRBRKMACNPA4	EUR	1	|MERCADOCONTINUO|	f	80845	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#BRBRKMACNPA4||es||False	f	t	t
\N	\N	\N	\N	\N	f	80850	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0175088006||None||False	f	t	t
Rheinmetall AG	DE0007030009	EUR	1	|DEUTSCHEBOERSE|	f	80761	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007030009||de||False	f	t	t
VET AFFAIRES	FR0000077158	EUR	1	|EURONEXT|	f	80796	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000077158||fr||False	f	t	t
VPK PACKAGING	BE0003749638	EUR	1	|EURONEXT|	f	80802	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003749638||be||False	f	t	t
VPK STRIP	BE0005551222	EUR	1	|EURONEXT|	f	80804	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005551222||be||False	f	t	t
UMICORE STRIP (D)	BE0005623948	EUR	1	|EURONEXT|	f	80822	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005623948||be||False	f	t	t
WERELDHAV B-SICAFI	BE0003724383	EUR	1	|EURONEXT|	f	80847	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003724383||be||False	f	t	t
Rücker AG	DE0007041105	EUR	1	|DEUTSCHEBOERSE|	f	80766	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007041105||de||False	f	t	t
S.A.G. Solarstrom AG	DE0007021008	EUR	1	|DEUTSCHEBOERSE|	f	80769	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007021008||de||False	f	t	t
Biotest AG Vz	DE0005227235	EUR	1	|DEUTSCHEBOERSE|	f	80793	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005227235||de||False	f	t	t
HOCHTIEF AG	DE0006070006	EUR	1	|DEUTSCHEBOERSE|	f	80794	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006070006||de||False	f	t	t
PATRIZIA Immobilien AG	DE000PAT1AG3	EUR	1	|DEUTSCHEBOERSE|	f	80831	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000PAT1AG3||de||False	f	t	t
Pfeiffer Vacuum Technology AG	DE0006916604	EUR	1	|DEUTSCHEBOERSE|	f	80832	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006916604||de||False	f	t	t
Sedo Holding AG	DE0005490155	EUR	1	|DEUTSCHEBOERSE|	f	80873	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005490155||de||False	f	t	t
SFC Energy AG	DE0007568578	EUR	1	|DEUTSCHEBOERSE|	f	80917	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007568578||de||False	f	t	t
SGL CARBON SE	DE0007235301	EUR	1	|DEUTSCHEBOERSE|	f	80918	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007235301||de||False	f	t	t
SKW Stahl-Metallurgie Holding AG	DE000SKWM021	EUR	1	|DEUTSCHEBOERSE|	f	80925	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000SKWM021||de||False	f	t	t
Sky Deutschland AG	DE000SKYD000	EUR	1	|DEUTSCHEBOERSE|	f	80926	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000SKYD000||de||False	f	t	t
SMA Solar Technology AG	DE000A0DJ6J9	EUR	1	|DEUTSCHEBOERSE|	f	80927	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0DJ6J9||de||False	f	t	t
SMARTRAC N.V.	NL0000186633	EUR	1	|DEUTSCHEBOERSE|	f	80928	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#NL0000186633||de||False	f	t	t
SMT Scharf AG	DE0005751986	EUR	1	|DEUTSCHEBOERSE|	f	80929	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005751986||de||False	f	t	t
Softing AG	DE0005178008	EUR	1	|DEUTSCHEBOERSE|	f	80930	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005178008||de||False	f	t	t
Software AG	DE0003304002	EUR	1	|DEUTSCHEBOERSE|	f	80931	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0003304002||de||False	f	t	t
SOLAR-FABRIK AG	DE0006614712	EUR	1	|DEUTSCHEBOERSE|	f	80932	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0006614712||de||False	f	t	t
STRATEC Biomedical AG	DE0007289001	EUR	1	|DEUTSCHEBOERSE|	f	80976	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007289001||de||False	f	t	t
Ströer Out-of-Home Media AG	DE0007493991	EUR	1	|DEUTSCHEBOERSE|	f	80977	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007493991||de||False	f	t	t
Südzucker AG	DE0007297004	EUR	1	|DEUTSCHEBOERSE|	f	80978	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007297004||de||False	f	t	t
sunways AG	DE0007332207	EUR	1	|DEUTSCHEBOERSE|	f	80979	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007332207||de||False	f	t	t
SURTECO SE	DE0005176903	EUR	1	|DEUTSCHEBOERSE|	f	80980	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005176903||de||False	f	t	t
S&#220;SS MicroTec AG	DE000A1K0235	EUR	1	|DEUTSCHEBOERSE|	f	80981	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1K0235||de||False	f	t	t
SYGNIS Pharma AG	DE000A1E9B74	EUR	1	|DEUTSCHEBOERSE|	f	80982	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A1E9B74||de||False	f	t	t
Symrise AG	DE000SYM9999	EUR	1	|DEUTSCHEBOERSE|	f	80983	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000SYM9999||de||False	f	t	t
systaic AG	DE000A0JKYP6	EUR	1	|DEUTSCHEBOERSE|	f	80984	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0JKYP6||de||False	f	t	t
Syzygy AG	DE0005104806	EUR	1	|DEUTSCHEBOERSE|	f	80985	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005104806||de||False	f	t	t
TAG Immobilien AG	DE0008303504	EUR	1	|DEUTSCHEBOERSE|	f	80986	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0008303504||de||False	f	t	t
TAKKT AG	DE0007446007	EUR	1	|DEUTSCHEBOERSE|	f	80987	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007446007||de||False	f	t	t
technotrans AG	DE000A0XYGA7	EUR	1	|DEUTSCHEBOERSE|	f	80988	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0XYGA7||de||False	f	t	t
telegate AG	DE0005118806	EUR	1	|DEUTSCHEBOERSE|	f	80989	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005118806||de||False	f	t	t
Teleplan International N.V.	NL0000229458	EUR	1	|DEUTSCHEBOERSE|	f	81032	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#NL0000229458||de||False	f	t	t
TELES AG Informationstechnologien	DE0007454902	EUR	1	|DEUTSCHEBOERSE|	f	81033	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007454902||de||False	f	t	t
Tipp24 SE	DE0007847147	EUR	1	|DEUTSCHEBOERSE|	f	81035	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007847147||de||False	f	t	t
Tognum AG	DE000A0N4P43	EUR	1	|DEUTSCHEBOERSE|	f	81036	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0N4P43||de||False	f	t	t
TOM TAILOR Holding AG	DE000A0STST2	EUR	1	|DEUTSCHEBOERSE|	f	81037	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0STST2||de||False	f	t	t
TOMORROW FOCUS AG	DE0005495329	EUR	1	|DEUTSCHEBOERSE|	f	81038	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005495329||de||False	f	t	t
TUI AG	DE000TUAG000	EUR	1	|DEUTSCHEBOERSE|	f	81039	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000TUAG000||de||False	f	t	t
YOUNIQ AG	DE000A0B7EZ7	EUR	1	|DEUTSCHEBOERSE|	f	81107	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0B7EZ7||de||False	f	t	t
ZhongDe Waste Technology AG	DE000ZDWT018	EUR	1	|DEUTSCHEBOERSE|	f	81108	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000ZDWT018||de||False	f	t	t
zooplus AG	DE0005111702	EUR	1	|DEUTSCHEBOERSE|	f	81109	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005111702||de||False	f	t	t
FORTEC Elektronik AG	DE0005774103	EUR	1	|DEUTSCHEBOERSE|	f	81150	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005774103||de||False	f	t	t
Nasdaq Composite	\N	USD	3	\N	t	81088	\N	\N	\N	\N	100	c	0	2	^IXIC	{1}	{3}	^IXIC||us||False	f	t	t
Xinyuan Real Estate Co. Ltd.	\N	USD	1	\N	f	81022	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#XIN||us||False	f	t	t
Concord Medical Services Holdings Ltd.	\N	USD	1	\N	f	81023	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CCM||us||False	f	t	t
Dex One Corp.	\N	USD	1	\N	f	81024	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#DEXO||us||False	f	t	t
\N	\N	\N	\N	\N	f	81075	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0147428009||None||False	f	t	t
\N	\N	\N	\N	\N	f	81095	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0147411005||None||False	f	t	t
Siemens AG	DE0007236101	EUR	1	|DAX|DEUTSCHEBOERSE|EUROSTOXX|	f	80920					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE0007236101||de||False	f	t	t
Fraport AG	DE0005773303	EUR	1	|DEUTSCHEBOERSE|	f	81154	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005773303||de||False	f	t	t
freenet AG	DE000A0Z2ZZ5	EUR	1	|DEUTSCHEBOERSE|	f	81156	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE000A0Z2ZZ5||de||False	f	t	t
Fresenius Medical Care AG & Co. KGaA Vz	DE0005785836	EUR	1	|DEUTSCHEBOERSE|	f	81159	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005785836||de||False	f	t	t
QIAGEN N.V.	NL0000240000	EUR	1	|DEUTSCHEBOERSE|	f	81162	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#NL0000240000||de||False	f	t	t
EVOTEC AG	DE0005664809	EUR	1	|DEUTSCHEBOERSE|	f	81171	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005664809||de||False	f	t	t
SAM	FR0000044497	EUR	1	|EURONEXT|	f	81155	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000044497||fr||False	f	t	t
SELCODIS	FR0000065492	EUR	1	|EURONEXT|	f	81157	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000065492||fr||False	f	t	t
SELECTIRENTE	FR0004175842	EUR	1	|EURONEXT|	f	81160	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0004175842||fr||False	f	t	t
SIGNAUX GIROD	FR0000060790	EUR	1	|EURONEXT|	f	81161	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000060790||fr||False	f	t	t
SPADEL	BE0003798155	EUR	1	|EURONEXT|	f	81242	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003798155||be||False	f	t	t
SPECTOR	BE0003663748	EUR	1	|EURONEXT|	f	81243	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003663748||be||False	f	t	t
TEXAF	BE0003550580	EUR	1	|EURONEXT|	f	81246	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003550580||be||False	f	t	t
THENERGO (D)	BE0003895159	EUR	1	|EURONEXT|	f	81247	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003895159||be||False	f	t	t
TIGENIX (D)	BE0003864817	EUR	1	|EURONEXT|	f	81255	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003864817||be||False	f	t	t
TOTAL STRIP	BE0005554259	EUR	1	|EURONEXT|	f	81258	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0005554259||be||False	f	t	t
UNIT4	NL0000389096	EUR	1	|EURONEXT|	f	81297	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000389096||nl||False	f	t	t
USG PEOPLE	NL0000354488	EUR	1	|EURONEXT|	f	81299	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000354488||nl||False	f	t	t
Heidelberger Druckmaschinen AG	DE0007314007	EUR	1	|DEUTSCHEBOERSE|	f	81265	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0007314007||de||False	f	t	t
\N	\N	\N	\N	\N	f	81311	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0160748002||None||False	f	t	t
\N	\N	\N	\N	\N	f	81327	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0165126006||None||False	f	t	t
\N	\N	\N	\N	\N	f	81342	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0165194004||None||False	f	t	t
INDO INTERNA	ES0148224118	EUR	1	|MERCADOCONTINUO|	f	81348	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0148224118||es||False	f	t	t
MADRID EMERGENTE GLOBAL	ES0158971038	EUR	2	|BMF|0085|	f	81301	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158971038||es||False	f	t	t
INM.DEL SUR	ES0154653911	EUR	1	|MERCADOCONTINUO|	f	81350	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0154653911||es||False	f	t	t
DXESTX5SH	LU0292106753	EUR	1	|MERCADOCONTINUO|	f	81351	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0292106753||es||False	f	t	t
INYPSA	ES0152768612	EUR	1	|MERCADOCONTINUO|	f	81352	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0152768612||es||False	f	t	t
DXJAPANC	LU0274209740	EUR	1	|MERCADOCONTINUO|	f	81353	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0274209740||es||False	f	t	t
DXLATAMC	LU0292108619	EUR	1	|MERCADOCONTINUO|	f	81354	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0292108619||es||False	f	t	t
DXLPPRIVC	LU0322250712	EUR	1	|MERCADOCONTINUO|	f	81355	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0322250712||es||False	f	t	t
LINGOTES ESP	ES0158480311	EUR	1	|MERCADOCONTINUO|	f	81356	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0158480311||es||False	f	t	t
LYX IBEX ETF	FR0010251744	EUR	1	|MERCADOCONTINUO|	f	81357	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010251744||es||False	f	t	t
ELETROBRAS B	BRELETACNPB7	EUR	1	|MERCADOCONTINUO|	f	81358	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#BRELETACNPB7||es||False	f	t	t
TOUAXBSAR0316	FR0010435438	EUR	1	|EURONEXT|	f	81259	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0010435438||fr||False	f	t	t
TUBIZE (ATTR)	BE0099967573	EUR	1	|EURONEXT|	f	81264	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0099967573||be||False	f	t	t
UMICORE (D)	BE0003884047	EUR	1	|EURONEXT|	f	81275	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003884047||be||False	f	t	t
UNITRONICS	IL0010838311	EUR	1	|EURONEXT|	f	81298	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#IL0010838311||be||False	f	t	t
BANKIA	ES0113307039	EUR	1	|IBEX|MERCADOCONTINUO|	t	81111					100	c	0	1	BKIA.MC	{1}	{3}	MC#ES0113307039||es||False	f	t	t
Fresenius Medical Care AG & Co. KGaA St	DE0005785802	EUR	1	|DAX|DEUTSCHEBOERSE|	f	81158					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE0005785802||de||False	f	t	t
LYXEASTETF	FR0010204073	EUR	1	|MERCADOCONTINUO|	f	81360	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010204073||es||False	f	t	t
ELETROBRAS O	BRELETACNOR6	EUR	1	|MERCADOCONTINUO|	f	81361	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#BRELETACNOR6||es||False	f	t	t
LYXESTX5 ETF	FR0007054358	EUR	1	|MERCADOCONTINUO|	f	81362	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0007054358||es||False	f	t	t
ENDESA CHILE	CLP3710M1090	EUR	1	|MERCADOCONTINUO|	f	81363	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#CLP3710M1090||es||False	f	t	t
LYXETFAAAGB	FR0010820258	EUR	1	|MERCADOCONTINUO|	f	81364	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010820258||es||False	f	t	t
GR.ELEKTRA	MX01EL000003	EUR	1	|MERCADOCONTINUO|	f	81370	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#MX01EL000003||es||False	f	t	t
GR.MODELO C	MXP4833F1044	EUR	1	|MERCADOCONTINUO|	f	81371	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#MXP4833F1044||es||False	f	t	t
GRUPOSURA	COT13PA00011	EUR	1	|MERCADOCONTINUO|	f	81372	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#COT13PA00011||es||False	f	t	t
\N	\N	\N	\N	\N	f	81374	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0165238009||None||False	f	t	t
BBVA B.FRAN.	ARP125991090	EUR	1	|MERCADOCONTINUO|	f	81424	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ARP125991090||es||False	f	t	t
BBVAIBOXXINV	ES0142446006	EUR	1	|MERCADOCONTINUO|	f	81425	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0142446006||es||False	f	t	t
BO.RIOJANAS	ES0115002018	EUR	1	|MERCADOCONTINUO|	f	81426	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0115002018||es||False	f	t	t
BRADESPAR OR	BRBRAPACNOR5	EUR	1	|MERCADOCONTINUO|	f	81427	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#BRBRAPACNOR5||es||False	f	t	t
C.V.N.E.	ES0184140210	EUR	1	|MERCADOCONTINUO|	f	81428	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0184140210||es||False	f	t	t
CAM	ES0114400007	EUR	1	|MERCADOCONTINUO|	f	81429	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0114400007||es||False	f	t	t
DXASIAC	LU0292107991	EUR	1	|MERCADOCONTINUO|	f	81430	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0292107991||es||False	f	t	t
AFI BONS ETF	ES0106061007	EUR	1	|MERCADOCONTINUO|	f	81442	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0106061007||es||False	f	t	t
AFI MONE ETF	ES0106078001	EUR	1	|MERCADOCONTINUO|	f	81443	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0106078001||es||False	f	t	t
ALFA C/I-S/A	MXP000511016	EUR	1	|MERCADOCONTINUO|	f	81444	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#MXP000511016||es||False	f	t	t
BA.SANT.RIO	ARBRIO010194	EUR	1	|MERCADOCONTINUO|	f	81445	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ARBRIO010194||es||False	f	t	t
BANORTE	MXP370711014	EUR	1	|MERCADOCONTINUO|	f	81446	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#MXP370711014||es||False	f	t	t
BARON DE LEY	ES0114297015	EUR	1	|MERCADOCONTINUO|	f	81447	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0114297015||es||False	f	t	t
DXBANKC	LU0292103651	EUR	1	|MERCADOCONTINUO|	f	81465	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0292103651||es||False	f	t	t
DXBANKSH	LU0322249037	EUR	1	|MERCADOCONTINUO|	f	81466	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0322249037||es||False	f	t	t
DXBRAZILC	LU0292109344	EUR	1	|MERCADOCONTINUO|	f	81467	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0292109344||es||False	f	t	t
DXDAXSH	LU0292106241	EUR	1	|MERCADOCONTINUO|	f	81468	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0292106241||es||False	f	t	t
DXDAXSHX2	LU0411075020	EUR	1	|MERCADOCONTINUO|	f	81469	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0411075020||es||False	f	t	t
DXEMERGC	LU0292107645	EUR	1	|MERCADOCONTINUO|	f	81470	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0292107645||es||False	f	t	t
DXESTSELD	LU0292095535	EUR	1	|MERCADOCONTINUO|	f	81471	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0292095535||es||False	f	t	t
LYXETFBRAZIL	FR0010408799	EUR	1	|MERCADOCONTINUO|	f	81487	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010408799||es||False	f	t	t
LYXETFCHINAE	FR0010204081	EUR	1	|MERCADOCONTINUO|	f	81488	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010204081||es||False	f	t	t
LYXETFCORPBO	FR0010737544	EUR	1	|MERCADOCONTINUO|	f	81489	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010737544||es||False	f	t	t
LYXETFCRB	FR0010270033	EUR	1	|MERCADOCONTINUO|	f	81490	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010270033||es||False	f	t	t
LYXETFCRN	FR0010346205	EUR	1	|MERCADOCONTINUO|	f	81491	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010346205||es||False	f	t	t
LYXETFEURHEA	FR0010344879	EUR	1	|MERCADOCONTINUO|	f	81492	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010344879||es||False	f	t	t
LYXETFEUROCA	FR0010510800	EUR	1	|MERCADOCONTINUO|	f	81493	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010510800||es||False	f	t	t
LYXETFEUROIL	FR0010344960	EUR	1	|MERCADOCONTINUO|	f	81494	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010344960||es||False	f	t	t
LYXETFEURTEL	FR0010344812	EUR	1	|MERCADOCONTINUO|	f	81495	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010344812||es||False	f	t	t
LYXETFLATINA	FR0010410266	EUR	1	|MERCADOCONTINUO|	f	81496	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010410266||es||False	f	t	t
LYXETFMINDIA	FR0010361683	EUR	1	|MERCADOCONTINUO|	f	81498	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010361683||es||False	f	t	t
LYXETFMSCIAH	FR0010833541	EUR	1	|MERCADOCONTINUO|	f	81499	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010833541||es||False	f	t	t
LYXETFMSCIEM	FR0010429068	EUR	1	|MERCADOCONTINUO|	f	81500	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010429068||es||False	f	t	t
LYXETFMSCIEU	FR0010261198	EUR	1	|MERCADOCONTINUO|	f	81501	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010261198||es||False	f	t	t
LYXETFMSCIGR	FR0010168765	EUR	1	|MERCADOCONTINUO|	f	81502	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010168765||es||False	f	t	t
LYXETFMSCIUS	FR0010833566	EUR	1	|MERCADOCONTINUO|	f	81503	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010833566||es||False	f	t	t
LYXETFMSCIVA	FR0010168781	EUR	1	|MERCADOCONTINUO|	f	81504	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010168781||es||False	f	t	t
IAG	ES0177542018	EUR	1	|IBEX|MERCADOCONTINUO|	f	81346					100	c	0	1	IAG.MC	{1}	{3}	MC#ES0177542018||es||False	f	t	t
ACC.ESTX.ETF	ES0105321030	EUR	4	|MERCADOCONTINUO|	f	81439					100	c	0	1	None	\N	\N	MC#ES0105321030||es||False	f	t	t
LYXETFNEWENE	FR0010524777	EUR	1	|MERCADOCONTINUO|	f	81506	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010524777||es||False	f	t	t
LYXETFRUSSIA	FR0010326140	EUR	1	|MERCADOCONTINUO|	f	81507	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010326140||es||False	f	t	t
LYXETFSELECD	FR0010378604	EUR	1	|MERCADOCONTINUO|	f	81508	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010378604||es||False	f	t	t
LYXETFSHORT	FR0010589101	EUR	1	|MERCADOCONTINUO|	f	81509	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010589101||es||False	f	t	t
LYXETFSMALLC	FR0010168773	EUR	1	|MERCADOCONTINUO|	f	81510	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010168773||es||False	f	t	t
LYXETFSP500A	LU0496786574	EUR	1	|MERCADOCONTINUO|	f	81511	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#LU0496786574||es||False	f	t	t
LYXETFSTXX60	FR0010345371	EUR	1	|MERCADOCONTINUO|	f	81512	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#FR0010345371||es||False	f	t	t
GRUPO TAVEX	ES0108180219	EUR	1	|MERCADOCONTINUO|	f	81513	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0108180219||es||False	f	t	t
SNIACE	ES0165380017	EUR	1	|MERCADOCONTINUO|	f	81514	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0165380017||es||False	f	t	t
SOLARIA	ES0165386014	EUR	1	|MERCADOCONTINUO|	f	81515	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0165386014||es||False	f	t	t
SOTOGRANDE	ES0138109014	EUR	1	|MERCADOCONTINUO|	f	81516	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0138109014||es||False	f	t	t
SUZANO BAHIA	BRSUZBACNPA3	EUR	1	|MERCADOCONTINUO|	f	81517	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#BRSUZBACNPA3||es||False	f	t	t
TECNOCOM	ES0147582B12	EUR	1	|MERCADOCONTINUO|	f	81518	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0147582B12||es||False	f	t	t
TESTA INM.	ES0170885018	EUR	1	|MERCADOCONTINUO|	f	81519	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0170885018||es||False	f	t	t
TUBACEX	ES0132945017	EUR	1	|MERCADOCONTINUO|	f	81520	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0132945017||es||False	f	t	t
TUBOS REUNI.	ES0180850416	EUR	1	|MERCADOCONTINUO|	f	81521	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0180850416||es||False	f	t	t
TV AZTECA	MXP740471117	EUR	1	|MERCADOCONTINUO|	f	81522	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#MXP740471117||es||False	f	t	t
URALITA	ES0182170615	EUR	1	|MERCADOCONTINUO|	f	81523	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0182170615||es||False	f	t	t
QUABIT	ES0110944016	EUR	1	|MERCADOCONTINUO|	f	81525	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0110944016||es||False	f	t	t
TELMEX	MXP904131325	EUR	1	|MERCADOCONTINUO|	f	81526	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#MXP904131325||es||False	f	t	t
REALIA	ES0173908015	EUR	1	|MERCADOCONTINUO|	f	81527	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0173908015||es||False	f	t	t
RENO M. S/A	IT0001178299	EUR	1	|MERCADOCONTINUO|	f	81528	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#IT0001178299||es||False	f	t	t
RENO M.CONV.	IT0001178240	EUR	1	|MERCADOCONTINUO|	f	81529	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#IT0001178240||es||False	f	t	t
RENTA CORP.	ES0173365018	EUR	1	|MERCADOCONTINUO|	f	81531	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0173365018||es||False	f	t	t
REYAL URBIS	ES0122761010	EUR	1	|MERCADOCONTINUO|	f	81532	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0122761010||es||False	f	t	t
ROVI	ES0157261019	EUR	1	|MERCADOCONTINUO|	f	81533	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0157261019||es||False	f	t	t
Blount International Inc.	\N	USD	1	\N	f	81564	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#BLT||us||False	f	t	t
SAN JOSE	ES0180918015	EUR	1	|MERCADOCONTINUO|	f	81535	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0180918015||es||False	f	t	t
SARE B	MX01SA030007	EUR	1	|MERCADOCONTINUO|	f	81536	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#MX01SA030007||es||False	f	t	t
SERVICE P.S.	ES0143421G11	EUR	1	|MERCADOCONTINUO|	f	81537	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	MC#ES0143421G11||es||False	f	t	t
MGIC Investment Corp.	\N	USD	1	\N	f	81567	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MTG||us||False	f	t	t
OCE	NL0000354934	EUR	1	|EURONEXT|	f	81627	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000354934||nl||False	f	t	t
EMCOR Group Inc.	\N	USD	1	\N	f	81593	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#EME||us||False	f	t	t
CapitalSource Inc.	\N	USD	1	\N	f	81596	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CSE||us||False	f	t	t
Portland General Electric Co.	\N	USD	1	\N	f	81599	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#POR||us||False	f	t	t
Washington Post Co. Cl B	\N	USD	1	\N	f	81601	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WPO||us||False	f	t	t
Two Harbors Investment Corp.	\N	USD	1	\N	f	81602	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TWO||us||False	f	t	t
MI Developments Inc.	\N	USD	1	\N	f	81603	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MIM||us||False	f	t	t
CACI International Inc. Cl A	\N	USD	1	\N	f	81605	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CACI||us||False	f	t	t
AboveNet Inc.	\N	USD	1	\N	f	81606	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ABVT||us||False	f	t	t
ROLINCO	NL0000288736	EUR	1	|EURONEXT|	f	81631	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000288736||nl||False	f	t	t
ROODMICROTEC	NL0000440477	EUR	1	|EURONEXT|	f	81632	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#NL0000440477||nl||False	f	t	t
ROYAL DUTCH SHELLB	GB00B03MM408	EUR	1	|EURONEXT|	f	81633	\N	\N	\N	\N	100	c	0	12	\N	\N	\N	EURONEXT#GB00B03MM408||nl||False	f	t	t
MONTEA C.V.A.	BE0003853703	EUR	1	|EURONEXT|	f	81594	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003853703||be||False	f	t	t
MOPOLI	NL0000488153	EUR	1	|EURONEXT|	f	81595	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#NL0000488153||be||False	f	t	t
MOPOLI FOND	NL0000488161	EUR	1	|EURONEXT|	f	81597	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#NL0000488161||be||False	f	t	t
RECTICEL	BE0003656676	EUR	1	|EURONEXT|	f	81629	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003656676||be||False	f	t	t
SAPEC	BE0003625366	EUR	1	|EURONEXT|	f	81636	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003625366||be||False	f	t	t
SIPEF (D)	BE0003898187	EUR	1	|EURONEXT|	f	81645	\N	\N	\N	\N	100	c	0	11	\N	\N	\N	EURONEXT#BE0003898187||be||False	f	t	t
A.C. RENTA FIJA EURO	ES0107516033	EUR	2	|BMF|0128|	f	74784	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107516033||es||False	f	t	t
A.C.RENTA FIJA EURO 1	ES0126524034	EUR	2	|BMF|0128|	f	74786	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126524034||es||False	f	t	t
INDITEX	ES0148396015	EUR	1	|EUROSTOXX|IBEX|MERCADOCONTINUO|	t	79192					100	c	0	1	ITX.MC	{1}	{3}	MC#ES0148396015||es||False	f	t	t
CAJA INGENIEROS A. GARANTIZADO	ES0115531032	EUR	2	|BMF|0193|	f	74796	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115531032||es||False	f	t	t
CAJA LABORAL AHORRO 2	ES0114984034	EUR	2	|BMF|0161|	f	74797	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114984034||es||False	f	t	t
CAJA LABORAL BOLSA	ES0115467039	EUR	2	|BMF|0161|	f	74799	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115467039||es||False	f	t	t
CAJABURGOS EUROPA	ES0115452031	EUR	2	|BMF|0128|	f	74802	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115452031||es||False	f	t	t
ALLIANZ SELECCION MODERADO	ES0108276033	EUR	2	|BMF|0168|	f	74812	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108276033||es||False	f	t	t
AHORRO CORPORACION IBEX AÑO 1	ES0114815030	EUR	2	|BMF|0128|	f	74814	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114815030||es||False	f	t	t
ALPHA PLUS DIVERSIFICACION	ES0108701006	EUR	2	|BMF|0225|	f	74819	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108701006||es||False	f	t	t
ATLAS CAPITAL PATRIMONIO	ES0111167005	EUR	2	|BMF|0210|	f	74827	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111167005||es||False	f	t	t
ALLIANZ SELECCION EMPRENDEDOR	ES0108291032	EUR	2	|BMF|0168|	f	74854	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108291032||es||False	f	t	t
AVIVA CORTO PLAZO  CLASE A	ES0170156006	EUR	2	|BMF|0191|	f	74855	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170156006||es||False	f	t	t
CAI RENDIMIENTO	ES0115106033	EUR	2	|BMF|0128|	f	74866	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115106033||es||False	f	t	t
CAIXANOVA GARANTIZADO GLOBAL	ES0115109037	EUR	2	|BMF|0128|	f	74867	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115109037||es||False	f	t	t
CAJA INGENIEROS 2013 2E GARANTIZADO	ES0157327000	EUR	2	|BMF|0193|	f	74868	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157327000||es||False	f	t	t
CAJASTUR CARTERA CONSERVADORA	ES0113701033	EUR	2	|BMF|0176|	f	74869	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113701033||es||False	f	t	t
CAIXA CATALUNYA BORSA 4	ES0114403035	EUR	2	|BMF|0020|	f	74871	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114403035||es||False	f	t	t
CAJASUR HISPANIA	ES0115447031	EUR	2	|BMF|0128|	f	74889	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115447031||es||False	f	t	t
ATLAS CAP.CARTERA DINAMICA CLASE A	ES0111127009	EUR	2	|BMF|0210|	f	74908	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111127009||es||False	f	t	t
CAJA INGENIEROS RF UNIVERSAL	ES0114811039	EUR	2	|BMF|0193|	f	74921	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114811039||es||False	f	t	t
RENTA 4 BANCO	ES0173358039	EUR	1	|MERCADOCONTINUO|	f	81530					100	c	0	1	R4.MC	{1}	{3}	MC#ES0173358039||es||False	f	t	t
BANCA CIVICA  ACCIONES	ES0165537038	EUR	2	|BMF|0071|	f	74925	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165537038||es||False	f	t	t
BANCA CIVICA AHORRO 1	ES0165530033	EUR	2	|BMF|0071|	f	74929	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165530033||es||False	f	t	t
BANCA CIVICA CONSERVADOR VAR 3	ES0115651004	EUR	2	|BMF|0071|	f	74936	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115651004||es||False	f	t	t
BANCA CIVICA FLOTANTE GARANTIZADO II	ES0165546039	EUR	2	|BMF|0071|	f	74937	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165546039||es||False	f	t	t
BANCA CIVICA FLOTANTE GARANTIZADO I	ES0165528003	EUR	2	|BMF|0071|	f	74938	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165528003||es||False	f	t	t
AC ALPHA MULTIESTRATEGIA	ES0107292007	EUR	2	|BMF|0128|	f	74949	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107292007||es||False	f	t	t
ALPHA PLUS DIVERSIFICACION CLASE B, FI	ES0108701014	EUR	2	|BMF|0225|	f	74958	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108701014||es||False	f	t	t
BANCAJA EUROPA FINANCIERO	ES0112942034	EUR	2	|BMF|0083|	f	74960	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112942034||es||False	f	t	t
CAJA INGENIEROS BOLSA EURO PLUS	ES0115443030	EUR	2	|BMF|0193|	f	74961	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115443030||es||False	f	t	t
CAJA INGENIEROS EUROB.GARANTIZ	ES0115442032	EUR	2	|BMF|0193|	f	74965	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115442032||es||False	f	t	t
CAJA INGENIEROS FONDT.CORTO PLAZ	ES0114887039	EUR	2	|BMF|0193|	f	74969	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114887039||es||False	f	t	t
AYG SYZ MULTISTRATEGY	ES0184954008	EUR	2	|BMF|0195|	f	74986	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184954008||es||False	f	t	t
CAJA INGENIEROS GESTION DINAMICA	ES0119488007	EUR	2	|BMF|0193|	f	74987	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0119488007||es||False	f	t	t
CAJA INGENIEROS IBEX PLUS	ES0122708037	EUR	2	|BMF|0193|	f	74991	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122708037||es||False	f	t	t
CAJA LABORAL AHORRO	ES0115466031	EUR	2	|BMF|0161|	f	74995	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115466031||es||False	f	t	t
ALPHAVILLE	ES0108703002	EUR	2	|BMF|0220|	f	74997	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108703002||es||False	f	t	t
ABANTE RENTA	ES0162947032	EUR	2	|BMF|0194|	f	75001	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162947032||es||False	f	t	t
BANESTO GARANTIZADO OCASION 2008	ES0114044037	EUR	2	|BMF|0012|	f	75010	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114044037||es||False	f	t	t
BANCAJA GESTION DIRECCIONAL 30	ES0137501039	EUR	2	|BMF|0083|	f	75017	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137501039||es||False	f	t	t
BANCAJA INTERES I	ES0116973035	EUR	2	|BMF|0083|	f	75044	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116973035||es||False	f	t	t
BARCLAYS BOLSA ESPAÑA	ES0138847035	EUR	2	|BMF|0063|	f	75057	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138847035||es||False	f	t	t
BG DINERO	ES0114686035	EUR	2	|BMF|0110|	f	75058	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114686035||es||False	f	t	t
BANCAJA GESTION DIRECCIONAL 60	ES0138001039	EUR	2	|BMF|0083|	f	75062	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138001039||es||False	f	t	t
CAJA LABORAL BOLSA GARANT. II	ES0114888037	EUR	2	|BMF|0161|	f	75064	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114888037||es||False	f	t	t
BANCA CIVICA GARANTIZADO EUROSTOXX II	ES0115732002	EUR	2	|BMF|0071|	f	75084	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115732002||es||False	f	t	t
BANCAJA INTERES II	ES0116974033	EUR	2	|BMF|0083|	f	75091	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116974033||es||False	f	t	t
CAIXASABADELL 6 MIXT	ES0113695037	EUR	2	|BMF|0128|	f	75094	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113695037||es||False	f	t	t
CAJA INGENIEROS 2012 GARANTIZADO	ES0164375000	EUR	2	|BMF|0193|	f	75119	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164375000||es||False	f	t	t
CAJA LABORAL RF GARANTIZADO 1	ES0114948039	EUR	2	|BMF|0161|	f	75120	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114948039||es||False	f	t	t
CAJA MADRID EVOLUCION VAR 15	ES0158948036	EUR	2	|BMF|0085|	f	75121	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158948036||es||False	f	t	t
BANCA CIVICA AHORRO 31	ES0165526031	EUR	2	|BMF|0071|	f	75126	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165526031||es||False	f	t	t
BNP PARIBAS CONSERVADOR	ES0171954037	EUR	2	|BMF|0061|	f	75128	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0171954037||es||False	f	t	t
BNP PARIBAS GLOBAL III	ES0160617033	EUR	2	|BMF|0061|	f	75131	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160617033||es||False	f	t	t
BPERE FONDO IBERICO ADAGIO	ES0118503004	EUR	2	|BMF|0198|	f	75144	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0118503004||es||False	f	t	t
BARCLAYS MIXTO 25	ES0138846037	EUR	2	|BMF|0063|	f	75161	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138846037||es||False	f	t	t
ABANTE BOLSA	ES0105011037	EUR	2	|BMF|0194|	f	75162	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105011037||es||False	f	t	t
CREDIT AGRICOLE MERCAEUROPA SMALL CAP	ES0123743033	EUR	2	|BMF|0174|	f	75168	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0123743033||es||False	f	t	t
CAJASTUR MULTICESTA OPTIMA II	ES0115319032	EUR	2	|BMF|0176|	f	75170	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115319032||es||False	f	t	t
CAJASUR MIXTO	ES0114893037	EUR	2	|BMF|0128|	f	75171	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114893037||es||False	f	t	t
DWS MULTIGESTION ACTIVA GARANT.	ES0125793036	EUR	2	|BMF|0142|	f	75172	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125793036||es||False	f	t	t
DWS CAPITAL II	ES0125774036	EUR	2	|BMF|0142|	f	75173	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125774036||es||False	f	t	t
EDM AHORRO	ES0168673038	EUR	2	|BMF|0049|	f	75174	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168673038||es||False	f	t	t
AHORRO CORPORACION BONOS FINANCI	ES0107369003	EUR	2	|BMF|0128|	f	75184	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107369003||es||False	f	t	t
FOCAIXA EQUILIBRIO	ES0138188034	EUR	2	|BMF|0015|	f	75187	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138188034||es||False	f	t	t
AMISTRA PATRIMONIAL	ES0109214009	EUR	2	|BMF|0232|	f	75190	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109214009||es||False	f	t	t
CAJA LABORAL BOLSA GARANT. IX	ES0115310031	EUR	2	|BMF|0161|	f	75191	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115310031||es||False	f	t	t
BANESTO DECIDIDO ACTIVO	ES0113791034	EUR	2	|BMF|0012|	f	75192	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113791034||es||False	f	t	t
BANESTO DIVIDENDO EUROPA	ES0113109039	EUR	2	|BMF|0012|	f	75206	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113109039||es||False	f	t	t
CAJA MADRID AVANZA.	ES0115084008	EUR	2	|BMF|0085|	f	75207	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115084008||es||False	f	t	t
CCM RENTA GARANTIZADO	ES0119733006	EUR	2	|BMF|0128|	f	75208	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0119733006||es||False	f	t	t
CAIXANOVA RENTA FIJA	ES0115019004	EUR	2	|BMF|0128|	f	75218	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115019004||es||False	f	t	t
CAJA LABORAL BOLSA GARANT. V	ES0115476030	EUR	2	|BMF|0161|	f	75219	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115476030||es||False	f	t	t
CAJA LABORAL BOLSA GARANT. VI	ES0115477038	EUR	2	|BMF|0161|	f	75220	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115477038||es||False	f	t	t
CAJA LABORAL RENTA FIJA GARANTIZADO IV	ES0164731038	EUR	2	|BMF|0161|	f	75222	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164731038||es||False	f	t	t
EDM INVERSION	ES0168674036	EUR	2	|BMF|0049|	f	75223	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168674036||es||False	f	t	t
FONDIBAS MIXTO	ES0117625030	EUR	2	|BMF|0113|	f	75228	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117625030||es||False	f	t	t
BANESTO GARANTIZADO SELECCION EUROPA	ES0165202039	EUR	2	|BMF|0012|	f	75238	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165202039||es||False	f	t	t
CAIXA CATALUNYA INDEX	ES0115457030	EUR	2	|BMF|0020|	f	75243	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115457030||es||False	f	t	t
CAIXA CATALUNYA 1-A	ES0122700034	EUR	2	|BMF|0020|	f	75245	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122700034||es||False	f	t	t
BANESTO GARANTIZADO SELECCION EUROPA 2	ES0113948030	EUR	2	|BMF|0012|	f	75261	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113948030||es||False	f	t	t
BANESTO GARAN.OPORTUNIDAD EUROPA	ES0113712030	EUR	2	|BMF|0012|	f	75262	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113712030||es||False	f	t	t
BANESTO GARAN.RENTAS CONSTANTES 2015	ES0181696032	EUR	2	|BMF|0012|	f	75263	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181696032||es||False	f	t	t
BARCLAYS MULTIALFA	ES0184930032	EUR	2	|BMF|0063|	f	75265	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184930032||es||False	f	t	t
BARCLAYS MULTIFONDO ALTERNATIVO	ES0184927038	EUR	2	|BMF|0063|	f	75267	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184927038||es||False	f	t	t
ESAF GARANT. BOLSA EUROPEA 3	ES0168397034	EUR	2	|BMF|0047|	f	75268	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168397034||es||False	f	t	t
ESAF GARANT.BOLSA ESPAÑOLA 4	ES0168564039	EUR	2	|BMF|0113|	f	75269	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168564039||es||False	f	t	t
ESAF GARANTIZADO 5 ESTRELLAS	ES0168657031	EUR	2	|BMF|0047|	f	75270	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168657031||es||False	f	t	t
ESAF GARANTTIZADO ORO	ES0168669036	EUR	2	|BMF|0047|	f	75273	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168669036||es||False	f	t	t
ESPIRITO SANTO PREMIUM BOLSA	ES0114916036	EUR	2	|BMF|0113|	f	75275	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114916036||es||False	f	t	t
ALTAE EURIBOR MAS GARANTIZADO	ES0108834005	EUR	2	|BMF|0085|	f	75283	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108834005||es||False	f	t	t
ALTAE INDICE S&P 500	ES0108851033	EUR	2	|BMF|0085|	f	75288	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108851033||es||False	f	t	t
CAJA SEGOVIA GARANTIZADO 2	ES0116942030	EUR	2	|BMF|0128|	f	75304	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116942030||es||False	f	t	t
FONCAIXA BOLSA GESTION EURO	ES0137802031	EUR	2	|BMF|0015|	f	75312	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137802031||es||False	f	t	t
AHORRO CORPORACION EURO IBEX GAR	ES0107366033	EUR	2	|BMF|0128|	f	75314	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107366033||es||False	f	t	t
CAIXAGIRONA EUROMIXT 40	ES0170231031	EUR	2	|BMF|0006|	f	75316	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170231031||es||False	f	t	t
CAJA SEGOVIA GARANTIZADO 3	ES0122709035	EUR	2	|BMF|0128|	f	75317	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122709035||es||False	f	t	t
CAJA SEGOVIA RENDIMIENTO GAR. 1	ES0115374037	EUR	2	|BMF|0128|	f	75318	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115374037||es||False	f	t	t
ESPIRITO SANTO PROTECCION BOLSA	ES0112698008	EUR	2	|BMF|0113|	f	75319	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112698008||es||False	f	t	t
EUROVALOR CONSOLIDADO 5	ES0133742033	EUR	2	|BMF|0004|	f	75320	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133742033||es||False	f	t	t
EUROVALOR IBEROAMERICA	ES0133576035	EUR	2	|BMF|0004|	f	75321	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133576035||es||False	f	t	t
FONCAIXA GARANTIA RENTA FIJA 19	ES0137687002	EUR	2	|BMF|0015|	f	75327	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137687002||es||False	f	t	t
BANESTO GARANTIZADO SELECCION IBEX 2	ES0113532032	EUR	2	|BMF|0012|	f	75329	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113532032||es||False	f	t	t
BANESTO GARANT.IBEX TOP 2	ES0113526034	EUR	2	|BMF|0012|	f	75333	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113526034||es||False	f	t	t
AVILA GARANTIA UNO	ES0112297033	EUR	2	|BMF|0128|	f	75334	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112297033||es||False	f	t	t
BANESTO GARANTIZADO BOLSA TOP 2	ES0113267035	EUR	2	|BMF|0012|	f	75342	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113267035||es||False	f	t	t
BANESTO GARANTIZADO OCASION	ES0113658035	EUR	2	|BMF|0012|	f	75343	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113658035||es||False	f	t	t
BBK GARANTIZADO RENTA FIJA 2012	ES0114185038	EUR	2	|BMF|0095|	f	75344	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114185038||es||False	f	t	t
CAJABURGOS BOLSA	ES0115508030	EUR	2	|BMF|0128|	f	75351	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115508030||es||False	f	t	t
CAJACANARIAS RENTA FIJA EURO	ES0124546039	EUR	2	|BMF|0128|	f	75352	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0124546039||es||False	f	t	t
CAJAGRANADA RENTA FIJA GARANT.II	ES0115428031	EUR	2	|BMF|0128|	f	75355	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115428031||es||False	f	t	t
FONCAIXA PATRIMONIO 16	ES0138653037	EUR	2	|BMF|0015|	f	75359	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138653037||es||False	f	t	t
CAJAGRANADA RF GARANTIZADO IV	ES0141226037	EUR	2	|BMF|0128|	f	75360	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0141226037||es||False	f	t	t
CAM MUNDIAL BONOS	ES0138933033	EUR	2	|BMF|0127|	f	75361	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138933033||es||False	f	t	t
FON FINECO INTERES A	ES0164814008	EUR	2	|BMF|0132|	f	75362	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164814008||es||False	f	t	t
FONCAIXA GARANTIA RENTA FIJA 23	ES0137786002	EUR	2	|BMF|0015|	f	75364	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137786002||es||False	f	t	t
FONCONSUL	ES0138785037	EUR	2	|BMF|0160|	f	75365	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138785037||es||False	f	t	t
FONDANETO	ES0138772035	EUR	2	|BMF|0012|	f	75366	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138772035||es||False	f	t	t
BANESTO MODERADO ACTIVO	ES0113781035	EUR	2	|BMF|0012|	f	75382	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113781035||es||False	f	t	t
BANESTO PROTECCION BOLSA 2	ES0113527032	EUR	2	|BMF|0012|	f	75383	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113527032||es||False	f	t	t
MADRID IBEX PREMIUM 95	ES0158985038	EUR	2	|BMF|0085|	f	75386	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158985038||es||False	f	t	t
CAJA BURGOS RENTA	ES0115491039	EUR	2	|BMF|0128|	f	75388	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115491039||es||False	f	t	t
FONCAIXA PATRIMONIO 35	ES0115421036	EUR	2	|BMF|0015|	f	75395	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115421036||es||False	f	t	t
BANESTO MIXTO RENTA FIJA 72/25	ES0114016035	EUR	2	|BMF|0012|	f	75407	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114016035||es||False	f	t	t
FONDEMAR DE INVERSIONES	ES0138053030	EUR	2	|BMF|0105|	f	75408	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138053030||es||False	f	t	t
FONDITEL ALBATROS	ES0138184033	EUR	2	|BMF|0200|	f	75409	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138184033||es||False	f	t	t
FONDITEL DINERO	ES0138338035	EUR	2	|BMF|0200|	f	75410	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138338035||es||False	f	t	t
BANESTO MIXTO RENTA FIJA 90/10	ES0114017033	EUR	2	|BMF|0012|	f	75411	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114017033||es||False	f	t	t
BANESTO MIXTO RENTA VARIAB.50/50	ES0114038039	EUR	2	|BMF|0012|	f	75412	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114038039||es||False	f	t	t
FONDITEL RENTA FIJA MIXTA INTER.	ES0138047032	EUR	2	|BMF|0200|	f	75413	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138047032||es||False	f	t	t
FONDMAPFRE BOLSA	ES0138901030	EUR	2	|BMF|0121|	f	75415	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138901030||es||False	f	t	t
FONDMAPFRE BOLSA GARANTIZADO	ES0138708039	EUR	2	|BMF|0121|	f	75416	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138708039||es||False	f	t	t
FONDO CAJA MURCIA INTERES GAR.VI	ES0138121001	EUR	2	|BMF|0128|	f	75418	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138121001||es||False	f	t	t
ALCALA BOLSA	ES0107692032	EUR	2	|BMF|0137|	f	75431	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107692032||es||False	f	t	t
ALCALA GLOBAL	ES0107693030	EUR	2	|BMF|0137|	f	75433	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107693030||es||False	f	t	t
ARTE FINANCIERO	ES0110276039	EUR	2	|BMF|0113|	f	75437	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110276039||es||False	f	t	t
CS.GLOBAL FONDOS GESTION ACTIVA	ES0132214034	EUR	2	|BMF|0173|	f	75439	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0132214034||es||False	f	t	t
AHORROFONDO	ES0107512032	EUR	2	|BMF|0128|	f	75443	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107512032||es||False	f	t	t
AHORROFONDO 20	ES0107475032	EUR	2	|BMF|0128|	f	75449	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107475032||es||False	f	t	t
BANESTO GARANTIZADO OCASION 2	ES0113792032	EUR	2	|BMF|0012|	f	75452	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113792032||es||False	f	t	t
FONDCOYUNTURA	ES0138969037	EUR	2	|f_es_0043|f_es_BMF|	f	75370	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138969037||es||False	f	t	t
CAIXAGIRONA RENTA FIXA	ES0138825031	EUR	2	|BMF|0006|	f	75454	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138825031||es||False	f	t	t
DAEDALUS MODERADO	ES0123033005	EUR	2	|BMF|0195|	f	75459	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0123033005||es||False	f	t	t
ALCALA AHORRO	ES0107696033	EUR	2	|BMF|0137|	f	75460	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107696033||es||False	f	t	t
FONDMAPFRE DIVERSIFICACION	ES0147625034	EUR	2	|BMF|0121|	f	75464	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147625034||es||False	f	t	t
FONDO GTZDO. CONFIANZA XII CAJA MURCIA	ES0138080033	EUR	2	|BMF|0128|	f	75465	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138080033||es||False	f	t	t
FONDO SUPERSELECCION DIVIDENDO	ES0138311032	EUR	2	|BMF|0012|	f	75467	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138311032||es||False	f	t	t
FONDO URBION	ES0138560034	EUR	2	|BMF|0012|	f	75468	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138560034||es||False	f	t	t
FONDO VALENCIA BRIC NUEVOS DESAF	ES0138561032	EUR	2	|BMF|0083|	f	75469	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138561032||es||False	f	t	t
FONDO VALENCIA EUROPA	ES0138519030	EUR	2	|BMF|0083|	f	75471	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138519030||es||False	f	t	t
EDM VALORES UNO	ES0127796037	EUR	2	|BMF|0049|	f	75473	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0127796037||es||False	f	t	t
FONCAFIX	ES0138806031	EUR	2	|BMF|0100|	f	75474	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138806031||es||False	f	t	t
ESAF GAR.RENTABILIDAD SEGURA 2	ES0168568006	EUR	2	|BMF|0047|	f	75476	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168568006||es||False	f	t	t
ESAF GARAN.BOLSA EUROPEA 2	ES0168566034	EUR	2	|BMF|0047|	f	75478	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168566034||es||False	f	t	t
ESAF GARAN.BOLSA MUNDIAL 3	ES0168621037	EUR	2	|BMF|0047|	f	75480	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168621037||es||False	f	t	t
FONDMAPFRE GARANTIZADO 607	ES0165196033	EUR	2	|BMF|0121|	f	75482	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165196033||es||False	f	t	t
FONDO VALENCIA FDO.DE FDO.90 GLO	ES0138678034	EUR	2	|BMF|0083|	f	75484	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138678034||es||False	f	t	t
FONDO VALENCIA FONDO DE FONDOS30	ES0138236031	EUR	2	|BMF|0083|	f	75485	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138236031||es||False	f	t	t
FONDO VALENCIA GARANTIZADO MIX.7	ES0138402039	EUR	2	|BMF|0083|	f	75486	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138402039||es||False	f	t	t
SANTANDER PREMIER CANCELABLE 4	ES0107766000	EUR	2	|BMF|0012|	f	75495	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107766000||es||False	f	t	t
AHORRO CORP. EUROACCIONES	ES0106943030	EUR	2	|BMF|0128|	f	75496	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0106943030||es||False	f	t	t
ASTURFONDO AHORRO	ES0111037034	EUR	2	|BMF|0176|	f	75498	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111037034||es||False	f	t	t
ASTURFONDO DINERO	ES0111046035	EUR	2	|BMF|0176|	f	75499	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111046035||es||False	f	t	t
BANESDEUDA FONDTESORO LARGO PLAZ	ES0114047030	EUR	2	|BMF|0012|	f	75500	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114047030||es||False	f	t	t
EDM RENTA	ES0127795039	EUR	2	|BMF|0049|	f	75501	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0127795039||es||False	f	t	t
FONDO VALENCIA GARN.ELECCION OPTIMA 5	ES0138363033	EUR	2	|BMF|0083|	f	75502	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138363033||es||False	f	t	t
FONDO VALENCIA GARN.ELECCION OPTIMA 6	ES0112739034	EUR	2	|BMF|0083|	f	75503	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112739034||es||False	f	t	t
FONDO VALENCIA INTERES III	ES0115219034	EUR	2	|BMF|0083|	f	75504	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115219034||es||False	f	t	t
FONDO VALENCIA INTERNACIONAL	ES0138601036	EUR	2	|BMF|0083|	f	75509	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138601036||es||False	f	t	t
FONDO VALENCIA RENTA	ES0138726031	EUR	2	|BMF|0083|	f	75512	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138726031||es||False	f	t	t
FONDOCAJA DEPOSITO	ES0115846034	EUR	2	|BMF|0128|	f	75514	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115846034||es||False	f	t	t
FONDOCAJA GARANTIZADO ELECCION	ES0166022006	EUR	2	|BMF|0128|	f	75516	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0166022006||es||False	f	t	t
FONDOCAJA GARANTIZADO PREMIER	ES0138364031	EUR	2	|BMF|0128|	f	75517	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138364031||es||False	f	t	t
FONDOGAESCO	ES0138233038	EUR	2	|BMF|0029|	f	75518	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138233038||es||False	f	t	t
BANCA CIVICA GESTION 50	ES0138853033	EUR	2	|BMF|0071|	f	75523	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138853033||es||False	f	t	t
BANCA CIVICA PREMIUM RENDIMIENTO CLASE A	ES0115716005	EUR	2	|BMF|0071|	f	75525	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115716005||es||False	f	t	t
BANCAJA INTERES III	ES0113044038	EUR	2	|BMF|0083|	f	75530	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113044038||es||False	f	t	t
BANCAJA INTERES PRINCIPAL	ES0141173031	EUR	2	|BMF|0083|	f	75532	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0141173031||es||False	f	t	t
SABADELL BS GARANTIA FONDOS 2	ES0175251034	EUR	2	|BMF|0058|	f	75546	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175251034||es||False	f	t	t
ESAF GARANTIZADO BOLSA EUROPEA 4	ES0168667030	EUR	2	|BMF|0047|	f	75561	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168667030||es||False	f	t	t
FONDONORTE DIVISAS	ES0122070032	EUR	2	|BMF|0009|	f	75562	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122070032||es||False	f	t	t
FONDONORTE EURO-RENTA	ES0138818036	EUR	2	|BMF|0009|	f	75563	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138818036||es||False	f	t	t
FONDONORTE EUROBOLSA	ES0138494036	EUR	2	|BMF|0009|	f	75564	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138494036||es||False	f	t	t
FONDTURIA	ES0158323032	EUR	2	|BMF|0140|	f	75565	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158323032||es||False	f	t	t
FONDUERO ACCIONES GARANTIZADO	ES0138522034	EUR	2	|BMF|0162|	f	75567	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138522034||es||False	f	t	t
FONDUERO CAPITAL GARANTIZADO 8	ES0165091036	EUR	2	|BMF|0162|	f	75570	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165091036||es||False	f	t	t
FONDUERO CAPITAL GARANTIZADO 7	ES0138566031	EUR	2	|BMF|0162|	f	75572	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138566031||es||False	f	t	t
EUROVALOR AFRICA Y ORIENTE MEDIO	ES0133444002	EUR	2	|BMF|0004|	f	75594	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133444002||es||False	f	t	t
FONCAIXA PRIVADA BOLSAPLUS	ES0105188033	EUR	2	|BMF|0015|	f	75597	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105188033||es||False	f	t	t
BANESDEUDA FONDVALENCIA	ES0114048038	EUR	2	|BMF|0012|	f	75599	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114048038||es||False	f	t	t
ESTUBROKER GAC I	ES0133461030	EUR	2	|BMF|0037|	f	75610	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133461030||es||False	f	t	t
EUROPA INNOVACION	ES0114921036	EUR	2	|BMF|0015|	f	75612	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114921036||es||False	f	t	t
EUROVALOR EUROPA DEL ESTE	ES0133554032	EUR	2	|BMF|0004|	f	75613	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133554032||es||False	f	t	t
FONDUERO EMERGENTES	ES0138521036	EUR	2	|BMF|0162|	f	75615	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138521036||es||False	f	t	t
FONDUERO EUROBOLSA  GARANTIZADO	ES0138568037	EUR	2	|BMF|0162|	f	75617	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138568037||es||False	f	t	t
FONDUERO EUROPA	ES0147496030	EUR	2	|BMF|0162|	f	75618	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147496030||es||False	f	t	t
FONDUERO EUROPEO GARANTIZADO	ES0141225039	EUR	2	|BMF|0162|	f	75619	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0141225039||es||False	f	t	t
FONDUERO GARANTIZADO	ES0177863034	EUR	2	|BMF|0162|	f	75620	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0177863034||es||False	f	t	t
FONDUERO MIXTO	ES0138852035	EUR	2	|BMF|0162|	f	75621	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138852035||es||False	f	t	t
FONDUERO PLUS	ES0138495033	EUR	2	|BMF|0162|	f	75622	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138495033||es||False	f	t	t
FONDUERO R.V. ESPAÑOLA	ES0138628039	EUR	2	|BMF|0162|	f	75623	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138628039||es||False	f	t	t
ATLAS CAPITAL BEST MANAGERS	ES0111171031	EUR	2	|BMF|0210|	f	75624	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111171031||es||False	f	t	t
CAIXAGIRONA EUROMIXT 20	ES0142491036	EUR	2	|BMF|0006|	f	75626	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142491036||es||False	f	t	t
CAIXANOVA GESTION	ES0109220030	EUR	2	|BMF|0128|	f	75629	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109220030||es||False	f	t	t
CAIXA GALICIA RENTA FIJA 1	ES0142543034	EUR	2	|BMF|0128|	f	75631	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142543034||es||False	f	t	t
EUROVALOR FONDEPOSITO PLUS	ES0127026005	EUR	2	|BMF|0004|	f	75649	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0127026005||es||False	f	t	t
MANDATO GROWTH	ES0159446006	EUR	2	|BMF|0113|	f	75651	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159446006||es||False	f	t	t
MANRESA EVEREST	ES0133881039	EUR	2	|BMF|0076|	f	75654	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133881039||es||False	f	t	t
EUROVALOR GARANTIZADO EUROCONSOLIDACION	ES0170260030	EUR	2	|BMF|0004|	f	75655	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170260030||es||False	f	t	t
EUROVALOR GAR.PROYEC.EUROPA	ES0133562035	EUR	2	|BMF|0004|	f	75656	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133562035||es||False	f	t	t
EUROVALOR GARANTIZADO CESTA SELECCION	ES0127027003	EUR	2	|BMF|0004|	f	75659	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0127027003||es||False	f	t	t
EUROVALOR GARANTIZADO ELITE	ES0133504037	EUR	2	|BMF|0004|	f	75660	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133504037||es||False	f	t	t
FONDUERO SECTORIAL	ES0147142030	EUR	2	|BMF|0162|	f	75664	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147142030||es||False	f	t	t
FONDUXO	ES0138893039	EUR	2	|BMF|0083|	f	75667	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138893039||es||False	f	t	t
BANCA CIVICA EUROPA	ES0133572034	EUR	2	|BMF|0071|	f	75676	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133572034||es||False	f	t	t
FONCAIXA GAR.OPORT.EMERGENTE III	ES0137702009	EUR	2	|BMF|0015|	f	75687	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137702009||es||False	f	t	t
EUROVALOR RECURSOS NATURALES	ES0133623001	EUR	2	|BMF|0004|	f	75688	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133623001||es||False	f	t	t
FONEMPORIUM	ES0138907037	EUR	2	|BMF|0182|	f	75689	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138907037||es||False	f	t	t
CAIXA CATALUNYA EQUILIBRI 2	ES0115288039	EUR	2	|BMF|0020|	f	75692	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115288039||es||False	f	t	t
CAIXA CATALUNYA EQUILIBRIO	ES0101337030	EUR	2	|BMF|0020|	f	75693	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0101337030||es||False	f	t	t
FON FINECO OPTIMUM GARANTIZADO	ES0138391034	EUR	2	|BMF|0132|	f	75694	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138391034||es||False	f	t	t
EUROVALOR GARANTIZADO MUNDIAL	ES0133543001	EUR	2	|BMF|0004|	f	75695	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133543001||es||False	f	t	t
CAIXA CATALUNYA DINAMICO	ES0115323034	EUR	2	|BMF|0020|	f	75696	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115323034||es||False	f	t	t
MANDATO INCOME	ES0159449000	EUR	2	|BMF|0113|	f	75697	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159449000||es||False	f	t	t
CAIXA CATALUNYA DINAMIC 2	ES0115210033	EUR	2	|BMF|0020|	f	75698	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115210033||es||False	f	t	t
FONMANRESA	ES0138858032	EUR	2	|BMF|0076|	f	75716	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138858032||es||False	f	t	t
FONMIX LAIETANA	ES0158319030	EUR	2	|BMF|0051|	f	75717	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158319030||es||False	f	t	t
FONPENEDES	ES0138887031	EUR	2	|BMF|0163|	f	75718	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138887031||es||False	f	t	t
FONPENEDES BORSA JAPON	ES0138605037	EUR	2	|BMF|0163|	f	75720	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138605037||es||False	f	t	t
FONPENEDES GAR.INT.MES BORSA 8	ES0138608031	EUR	2	|BMF|0163|	f	75724	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138608031||es||False	f	t	t
FONPENEDES INTERES GARANTIT 2	ES0117016032	EUR	2	|BMF|0163|	f	75725	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117016032||es||False	f	t	t
BANKPYME IBERBOLSA	ES0114065032	EUR	2	|BMF|0024|	f	75729	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114065032||es||False	f	t	t
BANKPIME PARTICIPACIONES PREFERENTES	ES0113439006	EUR	2	|BMF|0024|	f	75742	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113439006||es||False	f	t	t
BANKPYME FONDOLAR	ES0113481008	EUR	2	|BMF|0024|	f	75753	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113481008||es||False	f	t	t
BANKPYME GEST.DE CART. MODERADA	ES0113801031	EUR	2	|BMF|0024|	f	75759	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113801031||es||False	f	t	t
EUROVALOR RENTA FIJA	ES0133864035	EUR	2	|BMF|0004|	f	75761	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133864035||es||False	f	t	t
EUROVALOR RENTA FIJA CORTO	ES0138986031	EUR	2	|BMF|0004|	f	75767	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138986031||es||False	f	t	t
EUROVALOR SECTOR INMOBILIARIO	ES0133612038	EUR	2	|BMF|0004|	f	75768	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133612038||es||False	f	t	t
EUROVALOR TESORERIA	ES0138985033	EUR	2	|BMF|0004|	f	75771	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138985033||es||False	f	t	t
EXTRAFONDO BANESTO	ES0134676032	EUR	2	|BMF|0012|	f	75772	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0134676032||es||False	f	t	t
FOMODI	ES0138782034	EUR	2	|BMF|0203|	f	75774	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138782034||es||False	f	t	t
FONPENEDES INTERES GARANTIT 3	ES0115231039	EUR	2	|BMF|0163|	f	75775	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115231039||es||False	f	t	t
ALTAE DEUDA SOBERANA CP	ES0108740004	EUR	2	|BMF|0085|	f	75776	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108740004||es||False	f	t	t
CAJA SEGOVIA RENDIMIENTO GARAN.2	ES0122710033	EUR	2	|BMF|0128|	f	75778	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122710033||es||False	f	t	t
MANRESA FONDIPOSIT	ES0159533001	EUR	2	|BMF|0076|	f	75792	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159533001||es||False	f	t	t
SIITNEDIF TORDESILLAS IBOP, CLASE I	ES0175977000	EUR	2	|BMF|0216|	f	75793	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175977000||es||False	f	t	t
ALTAE DINERO	ES0108901036	EUR	2	|BMF|0085|	f	75797	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108901036||es||False	f	t	t
ALTAE DOBLE GARANTIA	ES0108849037	EUR	2	|BMF|0085|	f	75800	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108849037||es||False	f	t	t
ASTURFONDO DINERO PLATINUM	ES0110929033	EUR	2	|BMF|0176|	f	75801	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110929033||es||False	f	t	t
FONCAIXA 103 FONDANDALUCIA	ES0138062031	EUR	2	|BMF|0015|	f	75802	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138062031||es||False	f	t	t
FONCAIXA 3 R.F. LARGO DOLAR	ES0138808037	EUR	2	|BMF|0015|	f	75809	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138808037||es||False	f	t	t
ABANTE PATRIMONIO GLOBAL	ES0105013033	EUR	2	|BMF|0194|	f	75812	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105013033||es||False	f	t	t
ALTAE CESTA ESPAñOLA	ES0108847031	EUR	2	|BMF|0085|	f	75814	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108847031||es||False	f	t	t
FONVALCEM	ES0138930039	EUR	2	|BMF|0083|	f	75819	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138930039||es||False	f	t	t
ARCALIA INTERES	ES0138913035	EUR	2	|BMF|0083|	f	75825	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138913035||es||False	f	t	t
ASTURFONDO EUROBOLSA GARANTIZADO	ES0111023034	EUR	2	|BMF|0176|	f	75832	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111023034||es||False	f	t	t
ATLAS CAPITAL BOLSA	ES0111151009	EUR	2	|BMF|0210|	f	75835	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111151009||es||False	f	t	t
ATLAS CAPITAL CARTERA DINAMICA, CLASE I	ES0111127017	EUR	2	|BMF|0210|	f	75844	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111127017||es||False	f	t	t
ATLAS CAPITAL CRECIMIENTO	ES0111118032	EUR	2	|BMF|0210|	f	75846	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111118032||es||False	f	t	t
ATLAS CAPITAL LIQUIDEZ ACTIVA	ES0111166031	EUR	2	|BMF|0210|	f	75853	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111166031||es||False	f	t	t
CAJABURGOS RENTA 2	ES0126537036	EUR	2	|BMF|0128|	f	75856	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126537036||es||False	f	t	t
FONCAIXA 67 RENTA FIJA LARGO EUR	ES0138384039	EUR	2	|BMF|0015|	f	75864	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138384039||es||False	f	t	t
FONCAIXA 75 GLOBAL	ES0138257037	EUR	2	|BMF|0015|	f	75865	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138257037||es||False	f	t	t
GESCOOPERATIVO DEUDA CORPORATIVA	ES0158603037	EUR	2	|BMF|0140|	f	75868	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158603037||es||False	f	t	t
AG DIP WORLD EQUITIES FUND	ES0109657009	EUR	2	|BMF|0195|	f	75878	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109657009||es||False	f	t	t
BANCA CIVICA PREMIUM RENDIMIENTO CLASE B	ES0115716013	EUR	2	|BMF|0071|	f	75881	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115716013||es||False	f	t	t
BANCA CIVICA PREMIUM RENDIMIENTO II CL.A	ES0115709000	EUR	2	|BMF|0071|	f	75883	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115709000||es||False	f	t	t
BANCA CIVICA TIPO GARANTIZADO I	ES0115710008	EUR	2	|BMF|0071|	f	75886	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115710008||es||False	f	t	t
CCM RENTA 5	ES0116979008	EUR	2	|BMF|0128|	f	75887	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116979008||es||False	f	t	t
CAM FUTURO SELECCION	ES0175116039	EUR	2	|BMF|0127|	f	75888	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175116039||es||False	f	t	t
BANCA CIVICA PREMIUM REVALORIZACION	ES0115715007	EUR	2	|BMF|0071|	f	75889	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115715007||es||False	f	t	t
BANCA CIVICA PRIMIUM RENDIMIENT.CL.B	ES0115709018	EUR	2	|BMF|0071|	f	75892	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115709018||es||False	f	t	t
BANCA CIVICA PROGRESO	ES0126530031	EUR	2	|BMF|0071|	f	75893	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126530031||es||False	f	t	t
CAJA MADRID AVANZA RENTAS I	ES0115020002	EUR	2	|BMF|0085|	f	75897	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115020002||es||False	f	t	t
CAJA MADRID AVANZA RENTAS II	ES0147599007	EUR	2	|BMF|0085|	f	75902	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147599007||es||False	f	t	t
FONCAIXA BOLSA EURO	ES0138133030	EUR	2	|BMF|0015|	f	75903	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138133030||es||False	f	t	t
FONCAIXA BOLSA EUROPA OPORTUNIDA	ES0138068038	EUR	2	|BMF|0015|	f	75904	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138068038||es||False	f	t	t
FONCAIXA CAR.GEST.INTER.	ES0137696003	EUR	2	|BMF|0015|	f	75906	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137696003||es||False	f	t	t
FONDESPAÑA USA	ES0138221033	EUR	2	|BMF|0130|	f	75907	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138221033||es||False	f	t	t
FONCAIXA CARTERA R.F.DURACION	ES0137806032	EUR	2	|BMF|0015|	f	75908	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137806032||es||False	f	t	t
FONCAIXA CARTERA R.F.EMERGENTES	ES0138012036	EUR	2	|BMF|0015|	f	75909	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138012036||es||False	f	t	t
GESCOOPERATIVO DINAMICO	ES0142163031	EUR	2	|BMF|0140|	f	75910	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142163031||es||False	f	t	t
GESCOOPERATIVO FONDEPOSITO	ES0142099003	EUR	2	|BMF|0140|	f	75911	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142099003||es||False	f	t	t
BANCAJA BRIC NUEVOS DESAFIOS	ES0112889037	EUR	2	|BMF|0083|	f	75919	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112889037||es||False	f	t	t
FONCAIXA GARANTIA EURO-DOLAR II	ES0137703007	EUR	2	|BMF|0015|	f	75920	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137703007||es||False	f	t	t
BANCAJA RENTA FIJA DOLAR	ES0138894037	EUR	2	|BMF|0083|	f	75924	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138894037||es||False	f	t	t
CAJARIOJA AHORRO GARANTIZADO 1	ES0169085000	EUR	2	|BMF|0128|	f	75925	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169085000||es||False	f	t	t
FONDO CAJA MURCIA INTERES GARANTIZADO	ES0138358033	EUR	2	|BMF|0128|	f	75937	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138358033||es||False	f	t	t
BANCAJA RENTA FIJA MIXTA	ES0112977030	EUR	2	|BMF|0083|	f	75938	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112977030||es||False	f	t	t
BANCAJA RENTA VARIABLE	ES0113002036	EUR	2	|BMF|0083|	f	75939	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113002036||es||False	f	t	t
BANCAJA SMALL&MID CAPS	ES0112979036	EUR	2	|BMF|0083|	f	75940	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112979036||es||False	f	t	t
BANCOFAR FUTURO	ES0181693039	EUR	2	|BMF|0085|	f	75941	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181693039||es||False	f	t	t
BANESTO IBEX TOTAL	ES0113946034	EUR	2	|BMF|0012|	f	75946	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113946034||es||False	f	t	t
ATLAS RENTA DE INVERSIONES	ES0111200038	EUR	2	|f_es_0043|f_es_BMF|	f	75859	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111200038||es||False	f	t	t
BANESTO LIQUIDEZ DEUDA PUBLICA A	ES0113747010	EUR	2	|BMF|0012|	f	75947	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113747010||es||False	f	t	t
CX CAT.PATRI.DINAMIC	ES0115007033	EUR	2	|BMF|0020|	f	75949	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115007033||es||False	f	t	t
FONCAIXA 90 CESTA MIXTA 75 RV	ES0138171030	EUR	2	|BMF|0015|	f	75951	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138171030||es||False	f	t	t
FONCAIXA 52 BOLSA GESTION EURO	ES0138702032	EUR	2	|BMF|0015|	f	75952	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138702032||es||False	f	t	t
BANIF ACCIONES ESPAñOLAS GARANTI	ES0169067032	EUR	2	|BMF|0012|	f	75954	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169067032||es||False	f	t	t
FONDO EXTREMADURA GARANTIZADO VII	ES0115425037	EUR	2	|BMF|0128|	f	75956	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115425037||es||False	f	t	t
FONDO GAR.CONFIANZA X C.MURCIA	ES0182044034	EUR	2	|BMF|0128|	f	75957	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182044034||es||False	f	t	t
FONDO SUPERSELECCION DIVIDENDO 2	ES0138312030	EUR	2	|BMF|0012|	f	75958	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138312030||es||False	f	t	t
IBERCAJA GESTION BP GLOBAL BONDS	ES0146822004	EUR	2	|BMF|0084|	f	76003	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146822004||es||False	f	t	t
IBERCAJA GESTION GARANTIZADO	ES0147036034	EUR	2	|BMF|0084|	f	76004	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147036034||es||False	f	t	t
IBERCAJA GESTION GARANTIZADO 5	ES0147106035	EUR	2	|BMF|0084|	f	76005	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147106035||es||False	f	t	t
IBERCAJA GESTION GARANTIZADO 8	ES0147108007	EUR	2	|BMF|0084|	f	76007	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147108007||es||False	f	t	t
FONCAIXA BOLSA SECTOR SALUD	ES0137817005	EUR	2	|BMF|0015|	f	76016	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137817005||es||False	f	t	t
CAJA INGENIEROS GLOBAL	ES0114988035	EUR	2	|BMF|0193|	f	76030	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114988035||es||False	f	t	t
FONTIBREFONDO	ES0138918034	EUR	2	|BMF|0012|	f	76032	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138918034||es||False	f	t	t
IBERCAJA HIGH YIELD	ES0147105037	EUR	2	|BMF|0084|	f	76034	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147105037||es||False	f	t	t
IBERCAJA HIGH YIELD, CLASE B	ES0147105003	EUR	2	|BMF|0084|	f	76038	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147105003||es||False	f	t	t
IBERCAJA HORIZONTE	ES0147642039	EUR	2	|BMF|0084|	f	76051	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147642039||es||False	f	t	t
IBERCAJA INDEX 4	ES0147155032	EUR	2	|BMF|0084|	f	76052	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147155032||es||False	f	t	t
IBERCAJA INTERNACIONAL, CLASE B	ES0147184008	EUR	2	|BMF|0084|	f	76054	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147184008||es||False	f	t	t
IBERCAJA JAPON, CLASE B	ES0147129003	EUR	2	|BMF|0084|	f	76055	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147129003||es||False	f	t	t
IBERCAJA LATINOAMERICA	ES0147075032	EUR	2	|BMF|0084|	f	76056	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147075032||es||False	f	t	t
IBERCAJA MIXTO FLEXIBLE 15	ES0146944006	EUR	2	|BMF|0084|	f	76057	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146944006||es||False	f	t	t
BANKPYME TOP CLASS 75 R.V.	ES0114091038	EUR	2	|BMF|0024|	f	76059	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114091038||es||False	f	t	t
BANSABADELL BS GAR.EXTRA 11	ES0111094001	EUR	2	|BMF|0058|	f	76061	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111094001||es||False	f	t	t
BBK GARANTIZADO BOLSA EUROPA	ES0114201033	EUR	2	|BMF|0095|	f	76064	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114201033||es||False	f	t	t
BANESTO ESPECIAL EMPRESAS	ES0113108031	EUR	2	|BMF|0012|	f	76069	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113108031||es||False	f	t	t
IBERCAJA OPORTUNIDAD RENTA FIJA	ES0184007005	EUR	2	|BMF|0084|	f	76075	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184007005||es||False	f	t	t
IBERCAJA PATRIMONIO DINAMICO	ES0147038030	EUR	2	|BMF|0084|	f	76076	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147038030||es||False	f	t	t
IBERCAJA PETROQUIMICO	ES0130706031	EUR	2	|BMF|0084|	f	76077	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0130706031||es||False	f	t	t
IBERCAJA PREMIER	ES0147022034	EUR	2	|BMF|0084|	f	76083	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147022034||es||False	f	t	t
CAJARIOJA GARANTIZADO 3	ES0115378038	EUR	2	|BMF|0128|	f	76088	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115378038||es||False	f	t	t
BANKPYME RF PRIVADA DICIEMBRE 2012	ES0113403002	EUR	2	|BMF|0024|	f	76089	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113403002||es||False	f	t	t
BANKPYME RF PRIVADA JUNIO 2011	ES0125623001	EUR	2	|BMF|0024|	f	76091	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125623001||es||False	f	t	t
BANKPYME SWISS	ES0177031038	EUR	2	|BMF|0024|	f	76094	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0177031038||es||False	f	t	t
BBVA BOLSA	ES0138861036	EUR	2	|f_es_0014|f_es_BMF|	f	76013	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138861036||es||False	f	t	t
IBERCAJA SELECCION RENTA FIJA	ES0147192035	EUR	2	|BMF|0084|	f	76159	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147192035||es||False	f	t	t
IBERCAJA SMALL CAPS	ES0130708037	EUR	2	|BMF|0084|	f	76160	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0130708037||es||False	f	t	t
IBERCAJA TECNOLOGICO	ES0147644035	EUR	2	|BMF|0084|	f	76161	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147644035||es||False	f	t	t
BANESTO GARANTIZADO TRIPLE RENDI	ES0113531034	EUR	2	|BMF|0012|	f	76168	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113531034||es||False	f	t	t
BANKOA RENDIMIENTO 2 GARANTIZADO, FI	ES0114084033	EUR	2	|BMF|0035|	f	76173	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114084033||es||False	f	t	t
BANKOA STOXX 50 GARANTIZADO, FI	ES0180654032	EUR	2	|BMF|0035|	f	76176	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180654032||es||False	f	t	t
ING DIR.F.NARANJ.STAN.&POOR'S500	ES0152769032	EUR	2	|BMF|0015|	f	76204	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0152769032||es||False	f	t	t
ING DIRECT F.NAR.EURO STOXX 50	ES0152771038	EUR	2	|BMF|0015|	f	76205	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0152771038||es||False	f	t	t
ING DIRECT FONDO NARANJA IBEX 35	ES0152741031	EUR	2	|BMF|0015|	f	76206	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0152741031||es||False	f	t	t
MANRESA GARANTIT VI	ES0117064008	EUR	2	|BMF|0076|	f	76207	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117064008||es||False	f	t	t
MANRESA GARANTIT VII	ES0117065005	EUR	2	|BMF|0076|	f	76208	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117065005||es||False	f	t	t
MANRESA MUNDIBORSA	ES0115413033	EUR	2	|BMF|0076|	f	76209	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115413033||es||False	f	t	t
MANRESA PATRIMONI	ES0117091035	EUR	2	|BMF|0076|	f	76210	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117091035||es||False	f	t	t
MARCH NEW EMERGING WORLD	ES0160933000	EUR	2	|BMF|0190|	f	76211	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160933000||es||False	f	t	t
ST COLECTIVO FINANCIERO	ES0110049030	EUR	2	|BMF|0061|	f	76226	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110049030||es||False	f	t	t
CREDIT AGRICOLE MERCATRADING	ES0162232005	EUR	2	|BMF|0174|	f	76227	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162232005||es||False	f	t	t
BBVA FON-PLAZO 2012 B	ES0113959003	EUR	2	|f_es_0014|f_es_BMF|	f	76112	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113959003||es||False	f	t	t
NR FONDO 1	ES0166474033	EUR	2	|BMF|0113|	f	76261	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0166474033||es||False	f	t	t
FONPENEDES INVERSIO	ES0158320038	EUR	2	|BMF|0163|	f	76273	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158320038||es||False	f	t	t
BNP PARIBAS BONOS	ES0118496035	EUR	2	|BMF|0061|	f	76278	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0118496035||es||False	f	t	t
FONPENEDES MIXT EUROEMERGENT	ES0115230031	EUR	2	|BMF|0163|	f	76287	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115230031||es||False	f	t	t
BANESTO DOLAR 95 II	ES0113581005	EUR	2	|BMF|0012|	f	76288	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113581005||es||False	f	t	t
BANKOA BOLSA	ES0113418034	EUR	2	|BMF|0035|	f	76289	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113418034||es||False	f	t	t
BANESTO ESPECIAL RENTA FIJA	ES0113796033	EUR	2	|BMF|0012|	f	76291	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113796033||es||False	f	t	t
BANESTO GARANTIZADO OCASION PLUS	ES0113475034	EUR	2	|BMF|0012|	f	76298	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113475034||es||False	f	t	t
BANESTO GARANTIZADO SELECCION IBEX	ES0113656039	EUR	2	|BMF|0012|	f	76299	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113656039||es||False	f	t	t
BANESTO IBEX TOP	ES0113947032	EUR	2	|BMF|0012|	f	76300	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113947032||es||False	f	t	t
BANESTO SELECCION CONSERVADOR	ES0181698038	EUR	2	|BMF|0012|	f	76301	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181698038||es||False	f	t	t
BARCLAYS GARANTIZADO PROTECCION	ES0184824037	EUR	2	|BMF|0063|	f	76302	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184824037||es||False	f	t	t
BARCLAYS GESTION	ES0113802039	EUR	2	|BMF|0063|	f	76304	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113802039||es||False	f	t	t
BARCLAYS GESTION 25	ES0113422036	EUR	2	|BMF|0063|	f	76305	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113422036||es||False	f	t	t
BARCLAYS GESTION DINAMICA 300	ES0184919035	EUR	2	|BMF|0063|	f	76306	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184919035||es||False	f	t	t
ING DIRECT FONDO NARANJA M.EUROP	ES0152777035	EUR	2	|BMF|0015|	f	76308	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0152777035||es||False	f	t	t
OPENBANK CORTO PLAZO	ES0178172039	EUR	2	|BMF|0012|	f	76309	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0178172039||es||False	f	t	t
OPENBANK EUROINDICE 50	ES0168651034	EUR	2	|BMF|0012|	f	76310	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168651034||es||False	f	t	t
BARCLAYS GESTION TOTAL	ES0114165030	EUR	2	|BMF|0063|	f	76314	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114165030||es||False	f	t	t
BARCLAYS INT. GARANTIZADO 1	ES0138216033	EUR	2	|BMF|0063|	f	76316	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138216033||es||False	f	t	t
BANKOA TESORERIA	ES0113692034	EUR	2	|BMF|0035|	f	76317	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113692034||es||False	f	t	t
BARCLAYS LIQUIDEZ	ES0113717005	EUR	2	|BMF|0063|	f	76318	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113717005||es||False	f	t	t
FONDUERO CAPITAL GARANTIZADO 1	ES0138562030	EUR	2	|BMF|0162|	f	76342	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138562030||es||False	f	t	t
MULTIOPORTUNIDAD II	ES0164982037	EUR	2	|BMF|0132|	f	76345	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164982037||es||False	f	t	t
MUTUAFONDO BOLSA	ES0165193030	EUR	2	|BMF|0021|	f	76347	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165193030||es||False	f	t	t
CAIXA CATALUNYA 2-B	ES0114924006	EUR	2	|BMF|0020|	f	76348	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114924006||es||False	f	t	t
P-G MATER RENTA MIXTA	ES0167778002	EUR	2	|BMF|0029|	f	76353	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0167778002||es||False	f	t	t
P-G MATER RENTA VARIABLE	ES0167782004	EUR	2	|BMF|0029|	f	76354	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0167782004||es||False	f	t	t
PLUSMADRID 50	ES0170161030	EUR	2	|BMF|0085|	f	76356	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170161030||es||False	f	t	t
PLUSMADRID 75	ES0170167037	EUR	2	|BMF|0085|	f	76357	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170167037||es||False	f	t	t
PLUSMADRID AHORRO	ES0170271037	EUR	2	|BMF|0085|	f	76358	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170271037||es||False	f	t	t
PLUSMADRID AHORRO EURO	ES0170232039	EUR	2	|BMF|0085|	f	76359	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170232039||es||False	f	t	t
FONDUERO DINERO	ES0138891033	EUR	2	|BMF|0162|	f	76393	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138891033||es||False	f	t	t
ING DIRECT FONDO NARANJA MODERAD	ES0152739001	EUR	2	|BMF|0031|	f	76394	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0152739001||es||False	f	t	t
CAIXA CATALUNYA MULTISEC.MUNDIAL	ES0101338038	EUR	2	|BMF|0020|	f	76397	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0101338038||es||False	f	t	t
MUTUAFONDO HIGH YIELD	ES0165238033	EUR	2	|BMF|0021|	f	76400	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165238033||es||False	f	t	t
RURAL CESTA DECIDIDA 80	ES0174338030	EUR	2	|BMF|0140|	f	76401	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174338030||es||False	f	t	t
RURAL CESTA PRUDENTE 40	ES0158281032	EUR	2	|BMF|0140|	f	76402	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158281032||es||False	f	t	t
GESCOOPERATIVO DIVIDENDO EURO	ES0174389033	EUR	2	|BMF|0140|	f	76403	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174389033||es||False	f	t	t
RURAL GARANTIZADO RENTA FIJA 2014	ES0174267007	EUR	2	|BMF|0140|	f	76404	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174267007||es||False	f	t	t
RURAL RENTA FONDVALENCIA	ES0174411035	EUR	2	|BMF|0140|	f	76405	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174411035||es||False	f	t	t
BARCLAYS GARANTIZADO 17	ES0184846030	EUR	2	|BMF|0063|	f	76415	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184846030||es||False	f	t	t
BARCLAYS FONDO GLOBAL SELECCION	ES0115252035	EUR	2	|BMF|0063|	f	76417	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115252035||es||False	f	t	t
BANKOA TOP 3 GARANTIZADO	ES0182793036	EUR	2	|BMF|0035|	f	76419	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182793036||es||False	f	t	t
CCM RENTA PROGRESIVO	ES0119734004	EUR	2	|BMF|0176|	f	76422	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0119734004||es||False	f	t	t
CITIFONDO AGIL	ES0113722039	EUR	2	|BMF|0012|	f	76424	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113722039||es||False	f	t	t
ING DIRECT FONDO NARANJA R.F	ES0152772036	EUR	2	|f_es_0043|f_es_BMF|	f	76398	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0152772036||es||False	f	t	t
CITIFONDO BOND	ES0113723037	EUR	2	|BMF|0012|	f	76425	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113723037||es||False	f	t	t
FONMARCH	ES0138841038	EUR	2	|BMF|0190|	f	76427	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138841038||es||False	f	t	t
FONMASTER I	ES0138909033	EUR	2	|BMF|0046|	f	76429	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138909033||es||False	f	t	t
IBERCAJA GESTION GARANTIZADO 2	ES0147193033	EUR	2	|BMF|0084|	f	76432	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147193033||es||False	f	t	t
MUTUAFONDO LP	ES0165240039	EUR	2	|BMF|0021|	f	76440	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165240039||es||False	f	t	t
MUTUAFONDO	ES0165237035	EUR	2	|BMF|0021|	f	76443	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165237035||es||False	f	t	t
FONDO MULTIMIX 2004	ES0138224037	EUR	2	|BMF|0021|	f	76444	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138224037||es||False	f	t	t
NUCLEFON	ES0166486037	EUR	2	|BMF|0098|	f	76447	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0166486037||es||False	f	t	t
OKAVANDO DELTA FI CLASE I	ES0167211004	EUR	2	|BMF|0194|	f	76448	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0167211004||es||False	f	t	t
RURAL RENTA VARIABLE ESPAÑA	ES0175734039	EUR	2	|BMF|0140|	f	76449	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175734039||es||False	f	t	t
RURAL RENTA VARIABLE INTER.	ES0175736034	EUR	2	|BMF|0140|	f	76450	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175736034||es||False	f	t	t
BANKPYME MULTIFIX 25 R.V.	ES0165099039	EUR	2	|BMF|0024|	f	76455	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165099039||es||False	f	t	t
BANKOA AHORRO FONDO	ES0113691036	EUR	2	|BMF|0035|	f	76456	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113691036||es||False	f	t	t
BANKPYME MULTISALUD	ES0110057033	EUR	2	|BMF|0024|	f	76457	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110057033||es||False	f	t	t
BARCLAYS BOLSA USA	ES0124662034	EUR	2	|BMF|0063|	f	76458	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0124662034||es||False	f	t	t
BARCLAYS BONOS CONSERVADOR	ES0138943032	EUR	2	|BMF|0063|	f	76463	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138943032||es||False	f	t	t
BARCLAYS DEUDA PUBLICA	ES0113803037	EUR	2	|BMF|0063|	f	76469	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113803037||es||False	f	t	t
BBK GARANTIZADO BOLSA 4	ES0113404000	EUR	2	|BMF|0095|	f	76470	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113404000||es||False	f	t	t
BBK GARANTIZADO BOLSA 5	ES0110059039	EUR	2	|BMF|0095|	f	76471	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110059039||es||False	f	t	t
IBERCAJA GESTION GARANTIZADO 6	ES0147107009	EUR	2	|BMF|0084|	f	76483	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147107009||es||False	f	t	t
IBERCAJA H20&ENERGIAS RENOVABLES	ES0184004002	EUR	2	|BMF|0084|	f	76485	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184004002||es||False	f	t	t
OPENBANK IBEX 35	ES0119203034	EUR	2	|BMF|0012|	f	76486	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0119203034||es||False	f	t	t
PBP BRIC DINAMICO	ES0147134037	EUR	2	|BMF|0182|	f	76487	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147134037||es||False	f	t	t
PBP CORPORATES SELECCION	ES0113321030	EUR	2	|BMF|0182|	f	76488	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113321030||es||False	f	t	t
PBP DINERO FONDTESORO CORTO PLAZO	ES0147167037	EUR	2	|BMF|0182|	f	76489	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147167037||es||False	f	t	t
PBP DIVERSIFICACION GLOBAL	ES0147041034	EUR	2	|BMF|0182|	f	76490	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147041034||es||False	f	t	t
PBP ESTRATEGIAS	ES0147033031	EUR	2	|BMF|0182|	f	76491	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147033031||es||False	f	t	t
PBP GESTION FLEXIBLE	ES0110158039	EUR	2	|BMF|0182|	f	76492	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110158039||es||False	f	t	t
RURAL TECNOLOGICO RENTA VARIABLE	ES0175738030	EUR	2	|BMF|0140|	f	76493	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175738030||es||False	f	t	t
SABADELL BS ASIA EMERGENTES BOLS	ES0175083031	EUR	2	|BMF|0058|	f	76494	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175083031||es||False	f	t	t
BBK GARANTIZADO FINANZAS	ES0113274007	EUR	2	|BMF|0095|	f	76505	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113274007||es||False	f	t	t
BBK GARANTIZADO INDICE EUROPA	ES0114238035	EUR	2	|BMF|0095|	f	76506	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114238035||es||False	f	t	t
CAIXASABADELL FONSDIPOSIT	ES0118595034	EUR	2	|BMF|0128|	f	76507	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0118595034||es||False	f	t	t
CAJA LABORAL BOLSA USA	ES0115304034	EUR	2	|BMF|0161|	f	76508	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115304034||es||False	f	t	t
CAJA LABORAL BOLSAS EUROPEAS	ES0114812037	EUR	2	|BMF|0161|	f	76509	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114812037||es||False	f	t	t
CAJA LABORAL CONFIANZA	ES0164733034	EUR	2	|BMF|0161|	f	76510	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164733034||es||False	f	t	t
IBERCAJA CASH 2	ES0147042032	EUR	2	|BMF|0084|	f	76514	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147042032||es||False	f	t	t
CAJA LABORAL CRECIMIENTO	ES0115468037	EUR	2	|BMF|0161|	f	76517	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115468037||es||False	f	t	t
IBERCAJA JAPON	ES0147129037	EUR	2	|BMF|0084|	f	76522	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147129037||es||False	f	t	t
IBERCAJA NUEVAS OPORTUNIDADES	ES0147076030	EUR	2	|BMF|0084|	f	76524	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147076030||es||False	f	t	t
MANDATO BALANCED	ES0159474008	EUR	2	|BMF|0113|	f	76528	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159474008||es||False	f	t	t
MANRESA GLOBAL FIX	ES0117067001	EUR	2	|BMF|0076|	f	76529	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117067001||es||False	f	t	t
IBERCAJA OPORTUNIDAD RENTA FIJA, CLASE B	ES0184007013	EUR	2	|BMF|0084|	f	76531	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184007013||es||False	f	t	t
IBERCAJA PATRIMONIO	ES0147187035	EUR	2	|BMF|0084|	f	76532	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147187035||es||False	f	t	t
PBP OBJETIVO CRECIENTE	ES0168851030	EUR	2	|BMF|0182|	f	76533	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168851030||es||False	f	t	t
PBP OBJETIVO RENTABILIDAD	ES0168831032	EUR	2	|BMF|0182|	f	76534	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168831032||es||False	f	t	t
PRIVAT FONSELECCION	ES0158327033	EUR	2	|BMF|0078|	f	76535	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158327033||es||False	f	t	t
RURAL BOLSA EURO GARANTIA	ES0156831036	EUR	2	|BMF|0140|	f	76536	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0156831036||es||False	f	t	t
RURAL TOLEDO 1	ES0174388035	EUR	2	|BMF|0031|	f	76537	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174388035||es||False	f	t	t
SABADELL BS BONOS EMERGENTES	ES0183338039	EUR	2	|BMF|0058|	f	76538	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0183338039||es||False	f	t	t
BBK GARANTIZADO RENTA FIJA 2012,	ES0125626004	EUR	2	|BMF|0095|	f	76543	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125626004||es||False	f	t	t
BBK GESTION ACTIVA INVERSION	ES0113192035	EUR	2	|BMF|0095|	f	76544	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113192035||es||False	f	t	t
BBK MIXTO	ES0114258033	EUR	2	|BMF|0095|	f	76546	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114258033||es||False	f	t	t
BNP PARIBAS FONDO SOLIDARIDAD	ES0145874030	EUR	2	|BMF|0061|	f	76549	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0145874030||es||False	f	t	t
CAJA MADRID BRICT	ES0115139034	EUR	2	|BMF|0085|	f	76551	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115139034||es||False	f	t	t
CAJA MADRID EVOLUCION VAR 10	ES0105578035	EUR	2	|BMF|0085|	f	76552	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105578035||es||False	f	t	t
BANESTO ESPECIAL AHORRO	ES0114013032	EUR	2	|BMF|0012|	f	76558	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114013032||es||False	f	t	t
ESAF RENTA FIJA CORTO	ES0115049035	EUR	2	|BMF|0047|	f	76565	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115049035||es||False	f	t	t
CS ESTRATEGIA GLOBAL	ES0127021030	EUR	2	|BMF|0173|	f	76570	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0127021030||es||False	f	t	t
CS GLOBAL FONDOS 0-30, FI	ES0184716035	EUR	2	|BMF|0173|	f	76574	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184716035||es||False	f	t	t
CS GLOBAL LINK	ES0142537036	EUR	2	|BMF|0173|	f	76575	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142537036||es||False	f	t	t
IBERCAJA CASH	ES0147102034	EUR	2	|BMF|0084|	f	76578	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147102034||es||False	f	t	t
BBVA BONOS CASH PLUS	ES0110081033	EUR	2	|f_es_0014|f_es_BMF|	f	76541	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110081033||es||False	f	t	t
ALTAE BOLSA ACTIVA	ES0177041037	EUR	2	|BMF|0085|	f	76609	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0177041037||es||False	f	t	t
ALTAE BRICC	ES0113308037	EUR	2	|BMF|0085|	f	76611	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113308037||es||False	f	t	t
CAIXAGIRONA EMERGENT	ES0115461032	EUR	2	|BMF|0006|	f	76620	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115461032||es||False	f	t	t
BG INDICE GARANTIZADO	ES0114625033	EUR	2	|BMF|0110|	f	76621	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114625033||es||False	f	t	t
INTERDIN PENTATHLON	ES0162858031	EUR	2	|BMF|0198|	f	76627	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162858031||es||False	f	t	t
SABADELL BS ESPAÑA BOLSA	ES0174404030	EUR	2	|BMF|0058|	f	76628	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174404030||es||False	f	t	t
SABADELL BS EUROACCION 130/30	ES0175084005	EUR	2	|BMF|0058|	f	76629	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175084005||es||False	f	t	t
SABADELL BS EUROPA  BOLSA	ES0174416034	EUR	2	|BMF|0058|	f	76630	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174416034||es||False	f	t	t
SABADELL BS EUROPA EMERGENTE BOL	ES0111099034	EUR	2	|BMF|0058|	f	76632	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111099034||es||False	f	t	t
ASTURFONDO RENTA VARIABLE ESPAÑA	ES0111038032	EUR	2	|BMF|0176|	f	76641	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111038032||es||False	f	t	t
ASTURFONDO RENTA VARIABLE EURO	ES0111011039	EUR	2	|BMF|0176|	f	76654	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111011039||es||False	f	t	t
ASTURFONDO RENTAS	ES0111049039	EUR	2	|BMF|0176|	f	76655	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111049039||es||False	f	t	t
ATLAS CAPITAL RENTA FIJA	ES0111168003	EUR	2	|BMF|0210|	f	76656	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111168003||es||False	f	t	t
AVANCE GLOBAL	ES0112340031	EUR	2	|BMF|0105|	f	76657	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112340031||es||False	f	t	t
MADRID VALORES PREMIUM III	ES0159083031	EUR	2	|BMF|0085|	f	76660	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159083031||es||False	f	t	t
MADRID VALORES PREMIUM 100	ES0159179037	EUR	2	|BMF|0085|	f	76661	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159179037||es||False	f	t	t
DWS GLOBALFLEX GARANTIZADO	ES0125803033	EUR	2	|BMF|0142|	f	76662	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125803033||es||False	f	t	t
BETA DEUDA  FONDT.LARGO PLAZO	ES0114671037	EUR	2	|BMF|0061|	f	76667	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114671037||es||False	f	t	t
BNP PARIBAS DINAMICO	ES0171956032	EUR	2	|BMF|0061|	f	76675	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0171956032||es||False	f	t	t
BNP PARIBAS GLOBAL DINVER	ES0160615037	EUR	2	|BMF|0061|	f	76676	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160615037||es||False	f	t	t
AHORRO CORPORACION PATRIMONIO IN	ES0106929039	EUR	2	|BMF|0128|	f	76677	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0106929039||es||False	f	t	t
INVERBONOS	ES0175858036	EUR	2	|BMF|0162|	f	76678	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175858036||es||False	f	t	t
INVERDEUDA FONDTESORO	ES0155849039	EUR	2	|BMF|0162|	f	76679	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155849039||es||False	f	t	t
SABADELL BS EUROPA VALOR	ES0183339037	EUR	2	|BMF|0058|	f	76680	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0183339037||es||False	f	t	t
BONA RENDA	ES0115091037	EUR	2	|BMF|0029|	f	76686	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115091037||es||False	f	t	t
BPA FONDO IBERICO ACCIONES	ES0114903000	EUR	2	|BMF|0198|	f	76688	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114903000||es||False	f	t	t
CAAM MULTIFONDO BAJO RIESGO	ES0164371033	EUR	2	|BMF|0031|	f	76692	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164371033||es||False	f	t	t
AVIVA ESPABOLSA	ES0170147039	EUR	2	|BMF|0191|	f	76704	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170147039||es||False	f	t	t
AVIVA ESPABOLSA 2	ES0112357035	EUR	2	|BMF|0191|	f	76707	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112357035||es||False	f	t	t
CAI RENDIMIENTO II	ES0157081037	EUR	2	|BMF|0128|	f	76708	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157081037||es||False	f	t	t
CAI RENTA MIXTO	ES0115336036	EUR	2	|BMF|0128|	f	76710	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115336036||es||False	f	t	t
INTERDIN TESORERIA	ES0154957031	EUR	2	|BMF|0198|	f	76712	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0154957031||es||False	f	t	t
BNP PARIBAS GLOBAL INVESTMENT	ES0118502030	EUR	2	|BMF|0061|	f	76713	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0118502030||es||False	f	t	t
BNP PARIBAS INSTITUCIONES	ES0118581034	EUR	2	|BMF|0061|	f	76714	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0118581034||es||False	f	t	t
BNP PARIBAS SELECCION	ES0160620037	EUR	2	|BMF|0061|	f	76716	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160620037||es||False	f	t	t
BOLSALIDER	ES0115068035	EUR	2	|BMF|0029|	f	76723	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115068035||es||False	f	t	t
SABADELL BS GARANTIA EXTRA 2	ES0175242033	EUR	2	|BMF|0058|	f	76724	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175242033||es||False	f	t	t
SABADELL BS GARANTIA FIJA 4	ES0176092031	EUR	2	|BMF|0058|	f	76725	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0176092031||es||False	f	t	t
SABADELL BS GARANTIA FIJA 5	ES0176093039	EUR	2	|BMF|0058|	f	76728	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0176093039||es||False	f	t	t
SABADELL BS GARANTIA SUPERIOR 9	ES0175263039	EUR	2	|BMF|0058|	f	76729	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175263039||es||False	f	t	t
AVIVA EUROBOLSA 2	ES0112351038	EUR	2	|BMF|0191|	f	76745	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112351038||es||False	f	t	t
AVIVA FONVALOR EURO  CLASE A	ES0170136008	EUR	2	|BMF|0191|	f	76746	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170136008||es||False	f	t	t
CAIXANOVA GARANTIZADO RENTAS 3	ES0105577037	EUR	2	|BMF|0128|	f	76751	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105577037||es||False	f	t	t
MADRID GESTION DINAMICA	ES0138979036	EUR	2	|BMF|0085|	f	76752	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138979036||es||False	f	t	t
CAI RENTA MIXTO 40	ES0101332031	EUR	2	|BMF|0128|	f	76756	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0101332031||es||False	f	t	t
CAIXA CATALUNYA 1	ES0122699038	EUR	2	|BMF|0020|	f	76757	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122699038||es||False	f	t	t
CAIXA CATALUNYA LIQUIDITAT	ES0122702030	EUR	2	|BMF|0020|	f	76758	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122702030||es||False	f	t	t
BETA ACTIVOS MONETARIO	ES0117010035	EUR	2	|BMF|0061|	f	76760	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117010035||es||False	f	t	t
UNNIM IBEX TOP DIVIDEND	ES0125117038	EUR	2	|BMF|0192|	f	76762	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125117038||es||False	f	t	t
CAIXA GALICIA RENTA CRECIENTE	ES0105575031	EUR	2	|BMF|0128|	f	76764	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105575031||es||False	f	t	t
CAIXA GALICIA RF 3 AÑO 2013	ES0122705033	EUR	2	|BMF|0128|	f	76766	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122705033||es||False	f	t	t
CAIXA GALICIA SELECCION GARANTIZ	ES0105576039	EUR	2	|BMF|0128|	f	76767	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105576039||es||False	f	t	t
CAIXASABADELL 2 - FIX	ES0118597030	EUR	2	|BMF|0128|	f	76772	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0118597030||es||False	f	t	t
INTERDIN VALOR DINAMICO	ES0154974036	EUR	2	|BMF|0198|	f	76774	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0154974036||es||False	f	t	t
MANRESA CREIXEMENT	ES0159504036	EUR	2	|BMF|0076|	f	76775	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159504036||es||False	f	t	t
SABADELL BS JAPON  BOLSA	ES0174402034	EUR	2	|BMF|0058|	f	76779	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174402034||es||False	f	t	t
SABADELL BS MIX 50	ES0174391039	EUR	2	|BMF|0058|	f	76780	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174391039||es||False	f	t	t
BANCA CIVICA GESTION 15	ES0165547037	EUR	2	|BMF|0071|	f	76786	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165547037||es||False	f	t	t
AVIVA GESTION GLOBAL	ES0170136032	EUR	2	|BMF|0191|	f	76787	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170136032||es||False	f	t	t
AVIVA RENTA FIJA	ES0170138038	EUR	2	|BMF|0191|	f	76789	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170138038||es||False	f	t	t
BANCA CIVICA GESTION 30	ES0165533037	EUR	2	|BMF|0071|	f	76791	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165533037||es||False	f	t	t
AVIVA RENTA FIJA  CLASE A	ES0170138004	EUR	2	|BMF|0191|	f	76793	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170138004||es||False	f	t	t
B Y P EUROPA	ES0118537002	EUR	2	|BMF|0223|	f	76795	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0118537002||es||False	f	t	t
IBERCAJA CONSERVADOR 2	ES0146922002	EUR	2	|BMF|0084|	f	76804	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146922002||es||False	f	t	t
INTERMONEY RENTA FIJA CORTO PLAZ	ES0155171038	EUR	2	|BMF|0069|	f	76805	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155171038||es||False	f	t	t
MANRESA GARANTIT EURIBOR MES 50	ES0117062002	EUR	2	|BMF|0076|	f	76807	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117062002||es||False	f	t	t
BANCA CIVICA GARANTIZADO ACCIONES I	ES0115660005	EUR	2	|BMF|0071|	f	76815	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115660005||es||False	f	t	t
INTERMONEY VARIABLE EURO	ES0155142039	EUR	2	|BMF|0069|	f	76816	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155142039||es||False	f	t	t
SABADELL BS RENDIMIENTO EMPRESA	ES0174435034	EUR	2	|BMF|0058|	f	76828	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174435034||es||False	f	t	t
SABADELL BS RENDIMIENTO EURO	ES0173829039	EUR	2	|BMF|0058|	f	76829	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173829039||es||False	f	t	t
SABADELL BS RENDIMIENTO PYME	ES0174392037	EUR	2	|BMF|0058|	f	76830	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174392037||es||False	f	t	t
SABADELL BS RENTA	ES0111113033	EUR	2	|BMF|0058|	f	76831	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111113033||es||False	f	t	t
SABADELL BS RENTAB. OBJ. 1	ES0111146009	EUR	2	|BMF|0058|	f	76832	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111146009||es||False	f	t	t
BANCAJA RENTA FIJA	ES0138844032	EUR	2	|BMF|0083|	f	76835	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138844032||es||False	f	t	t
BANCAJA RENTA FIJA CORTO PLAZO	ES0112954039	EUR	2	|BMF|0083|	f	76837	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112954039||es||False	f	t	t
FONCAIXA PRIVADA BOLSA INTERNAC.	ES0115062038	EUR	2	|BMF|0015|	f	76838	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115062038||es||False	f	t	t
BANCA CIVICA SOLIDO GARANTIZADO IV	ES0115717003	EUR	2	|BMF|0071|	f	76844	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115717003||es||False	f	t	t
BANCAJA GARANTIZADO 19	ES0112967007	EUR	2	|BMF|0083|	f	76845	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112967007||es||False	f	t	t
BANCAJA GARANTIZADO II	ES0112963030	EUR	2	|BMF|0083|	f	76846	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112963030||es||False	f	t	t
BANCAJA GARANTIZADO R.VARIABLE 8	ES0112897030	EUR	2	|BMF|0083|	f	76847	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112897030||es||False	f	t	t
BANCAJA RENTA VARIABLE EE.UU.	ES0112978038	EUR	2	|BMF|0083|	f	76848	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112978038||es||False	f	t	t
BANCAJA GESTION DIRECCIONAL 100	ES0137572030	EUR	2	|BMF|0083|	f	76858	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137572030||es||False	f	t	t
FONCAIXA GARANTIA DOBLE DIRECCIO	ES0137775005	EUR	2	|BMF|0015|	f	76862	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137775005||es||False	f	t	t
SABADELL BS SELECCION ACTIVA V2	ES0158287039	EUR	2	|BMF|0058|	f	76873	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158287039||es||False	f	t	t
SABADELL BS SELECCION ACTIVA V4	ES0158288037	EUR	2	|BMF|0058|	f	76874	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158288037||es||False	f	t	t
SAFEI AHORRO FONDTESORO	ES0138873031	EUR	2	|BMF|0085|	f	76875	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138873031||es||False	f	t	t
AHORRO CORP. AUSTRALASIA	ES0107491039	EUR	2	|BMF|0128|	f	76884	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107491039||es||False	f	t	t
AVIVA EUROBOLSA	ES0170141032	EUR	2	|BMF|0191|	f	76888	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170141032||es||False	f	t	t
DAEDALUS CONSERVADOR	ES0126048000	EUR	2	|BMF|0195|	f	76889	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126048000||es||False	f	t	t
BANKOA GESTION GLOBAL	ES0164593032	EUR	2	|BMF|0035|	f	76892	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164593032||es||False	f	t	t
BANCAJA RENTA VARIABLE EURO	ES0112961034	EUR	2	|BMF|0083|	f	76915	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112961034||es||False	f	t	t
SAFEI BOLSA EURO	ES0138661030	EUR	2	|BMF|0085|	f	76922	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138661030||es||False	f	t	t
SAFEI CRECIMIENTO	ES0126522038	EUR	2	|BMF|0085|	f	76925	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126522038||es||False	f	t	t
SANTANDER 100 X 1003	ES0174962003	EUR	2	|BMF|0012|	f	76927	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174962003||es||False	f	t	t
SANTANDER 100 X 1004	ES0174963001	EUR	2	|BMF|0012|	f	76928	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174963001||es||False	f	t	t
SANTANDER 100 X 1005	ES0174964009	EUR	2	|BMF|0012|	f	76929	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174964009||es||False	f	t	t
SANTANDER 105 EUROPA 2	ES0176934034	EUR	2	|BMF|0012|	f	76930	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0176934034||es||False	f	t	t
SANTANDER 105 EUROPA 3	ES0138308038	EUR	2	|BMF|0012|	f	76931	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138308038||es||False	f	t	t
SANTANDER ACCIONES ESPAÑOLAS A	ES0138823036	EUR	2	|BMF|0012|	f	76932	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138823036||es||False	f	t	t
SANTANDER ACCIONES ESPAÑOLAS B	ES0138823002	EUR	2	|BMF|0012|	f	76933	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138823002||es||False	f	t	t
SANTANDER AHORRO ACTIVO A	ES0145803005	EUR	2	|BMF|0012|	f	76934	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0145803005||es||False	f	t	t
SANTANDER AHORRO ACTIVO C	ES0145803039	EUR	2	|BMF|0012|	f	76935	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0145803039||es||False	f	t	t
SANTANDER AHORRO DIARIO 1	ES0155889035	EUR	2	|BMF|0012|	f	76936	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155889035||es||False	f	t	t
SANTANDER AHORRO DIARIO 2	ES0155872031	EUR	2	|BMF|0012|	f	76937	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155872031||es||False	f	t	t
BANCAJA RENTA VARIABLE MIXTA	ES0116980030	EUR	2	|BMF|0083|	f	76945	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116980030||es||False	f	t	t
BANESTO 95 BOLSA TOP	ES0113758009	EUR	2	|BMF|0012|	f	76947	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113758009||es||False	f	t	t
BANESTO 95 IBEX 60	ES0113462008	EUR	2	|BMF|0012|	f	76948	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113462008||es||False	f	t	t
FONCAIXA 61 BOLSA TECNOLOGIA	ES0138322039	EUR	2	|BMF|0015|	f	76949	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138322039||es||False	f	t	t
BANESTO 95 SELECCION MUNDIAL	ES0113602009	EUR	2	|BMF|0012|	f	76952	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113602009||es||False	f	t	t
BANESTO AHORRO	ES0138802030	EUR	2	|BMF|0012|	f	76953	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138802030||es||False	f	t	t
BANESTO BOLSA 30 2	ES0113543039	EUR	2	|BMF|0012|	f	76957	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113543039||es||False	f	t	t
BANESTO BOLSA 30 3	ES0113962031	EUR	2	|BMF|0012|	f	76958	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113962031||es||False	f	t	t
FONCAIXA CARTERA DINAMICO V3	ES0137695039	EUR	2	|BMF|0015|	f	76961	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137695039||es||False	f	t	t
BANESTO BOLSA TOP	ES0113436002	EUR	2	|BMF|0012|	f	76967	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113436002||es||False	f	t	t
SANTANDER RENTA FIJA CORPORATIVA	ES0174971038	EUR	2	|BMF|0012|	f	76968	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174971038||es||False	f	t	t
KUTXAMIXTO 85/15	ES0156892004	EUR	2	|BMF|0086|	f	76969	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0156892004||es||False	f	t	t
FONCAIXA GARANTIA ACTIVA	ES0137924033	EUR	2	|BMF|0015|	f	76970	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137924033||es||False	f	t	t
SERFIEX EUROPA	ES0175419037	EUR	2	|BMF|0191|	f	76971	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175419037||es||False	f	t	t
SERFIEX IBEX 35 INDICE	ES0175590035	EUR	2	|BMF|0191|	f	76972	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175590035||es||False	f	t	t
KUTXAMONETARIO	ES0157002033	EUR	2	|BMF|0086|	f	76979	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157002033||es||False	f	t	t
KUTXAMONETARIO2	ES0157354038	EUR	2	|BMF|0086|	f	76980	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157354038||es||False	f	t	t
SANTANDER FOREX	ES0175827007	EUR	2	|BMF|0012|	f	76982	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175827007||es||False	f	t	t
SANTANDER GAR.ACTIVA CONSERV.2	ES0174968034	EUR	2	|BMF|0012|	f	76984	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174968034||es||False	f	t	t
SANTANDER GAR.ACTIVA CONSERV.3	ES0174953036	EUR	2	|BMF|0012|	f	76987	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174953036||es||False	f	t	t
CAJA LABORAL BOLSA UNIVERSAL	ES0164734032	EUR	2	|BMF|0161|	f	76997	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164734032||es||False	f	t	t
CAJA LABORAL DINERO	ES0115489033	EUR	2	|BMF|0161|	f	76998	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115489033||es||False	f	t	t
BBVA PROPIEDAD	ES0110179035	EUR	2	|f_es_0014|f_es_BMF|	f	76951	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110179035||es||False	f	t	t
BANESTO BOLSAS EUROPEAS	ES0113657037	EUR	2	|BMF|0012|	f	77003	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113657037||es||False	f	t	t
BANESTO FONDEPOSITOS	ES0113474037	EUR	2	|BMF|0012|	f	77007	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113474037||es||False	f	t	t
CAJA LABORAL BOLSA GARANT.VII	ES0115478036	EUR	2	|BMF|0161|	f	77008	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115478036||es||False	f	t	t
CAJA LABORAL BOLSA GARANT.XIII	ES0164732036	EUR	2	|BMF|0161|	f	77009	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164732036||es||False	f	t	t
CAJA INGENIEROS EUROPA 25	ES0115451033	EUR	2	|BMF|0193|	f	77013	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115451033||es||False	f	t	t
CAJA LABORAL BOLSA JAPON	ES0115396030	EUR	2	|BMF|0161|	f	77014	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115396030||es||False	f	t	t
CAJA LABORAL MERCADOS EMERGENT	ES0114928031	EUR	2	|BMF|0161|	f	77017	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114928031||es||False	f	t	t
SABADELL BS GARANTIA EXTRA 6	ES0111201036	EUR	2	|BMF|0058|	f	77019	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111201036||es||False	f	t	t
CAJA LABORAL PATRIMONIO	ES0115469035	EUR	2	|BMF|0161|	f	77021	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115469035||es||False	f	t	t
CAJA LABORAL RENDIMIENTO	ES0115463038	EUR	2	|BMF|0161|	f	77026	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115463038||es||False	f	t	t
SANTANDER GARAN.ACTIVA MODER.2	ES0174952038	EUR	2	|BMF|0012|	f	77028	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174952038||es||False	f	t	t
SANTANDER GARAN.ACTIVA MODER.3	ES0174969032	EUR	2	|BMF|0012|	f	77029	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174969032||es||False	f	t	t
SANTANDER GARAN.ACTIVA MODERADO	ES0174967036	EUR	2	|BMF|0012|	f	77034	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174967036||es||False	f	t	t
SANTANDER GESTION GLOBAL	ES0107994008	EUR	2	|BMF|0012|	f	77035	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107994008||es||False	f	t	t
SANTANDER INDICE ESPAÑA	ES0133862039	EUR	2	|BMF|0012|	f	77036	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133862039||es||False	f	t	t
BANESTO LIQUIDEZ DEUDA PUBLICA B	ES0113747002	EUR	2	|BMF|0012|	f	77038	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113747002||es||False	f	t	t
BG GESTION INMOBILIARIA GARANT.3	ES0114624036	EUR	2	|BMF|0110|	f	77042	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114624036||es||False	f	t	t
MANRESA VALOR	ES0117142002	EUR	2	|BMF|0076|	f	77043	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117142002||es||False	f	t	t
BANIF CORTO PLAZO E	ES0115237002	EUR	2	|BMF|0012|	f	77047	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115237002||es||False	f	t	t
BANIF DIVIDENDO	ES0113544037	EUR	2	|BMF|0012|	f	77049	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113544037||es||False	f	t	t
BANIF DIVIDENDO EUROPA	ES0109360034	EUR	2	|BMF|0012|	f	77050	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109360034||es||False	f	t	t
BANIF ENERGIAS RENOV.ESTRUCTURAD	ES0113269031	EUR	2	|BMF|0012|	f	77051	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113269031||es||False	f	t	t
BANIF ESTRUCTURADO	ES0113660031	EUR	2	|BMF|0012|	f	77053	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113660031||es||False	f	t	t
BANIF EUROPA GARANTIZADO	ES0115203038	EUR	2	|BMF|0012|	f	77054	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115203038||es||False	f	t	t
BANIF FONDEPOSITOS	ES0122071030	EUR	2	|BMF|0012|	f	77055	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122071030||es||False	f	t	t
BARCLAYS GARANT.PROTECCION 2	ES0141220030	EUR	2	|BMF|0063|	f	77056	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0141220030||es||False	f	t	t
NMAS1 GESTION BOLSA EUROPEA	ES0166301038	EUR	2	|BMF|0202|	f	77057	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0166301038||es||False	f	t	t
EUROPA REESTRUCTURACION	ES0182643009	EUR	2	|BMF|0015|	f	77059	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182643009||es||False	f	t	t
BANIF GLOBAL 3-98	ES0138600038	EUR	2	|BMF|0012|	f	77060	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138600038||es||False	f	t	t
BANIF GLOBAL UNIVERSAL	ES0113545034	EUR	2	|BMF|0012|	f	77061	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113545034||es||False	f	t	t
CAJA LABORAL RENTA ASEGURADA I	ES0114891031	EUR	2	|BMF|0161|	f	77069	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114891031||es||False	f	t	t
CAJA LABORAL RENTA FIJA GARANTIZADO III	ES0114890033	EUR	2	|BMF|0161|	f	77075	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114890033||es||False	f	t	t
SANTANDER MEMORIA	ES0138359031	EUR	2	|BMF|0012|	f	77079	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138359031||es||False	f	t	t
SANTANDER MEMORIA 2	ES0112736030	EUR	2	|BMF|0012|	f	77080	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112736030||es||False	f	t	t
SANTANDER MEMORIA 3	ES0112737038	EUR	2	|BMF|0012|	f	77083	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112737038||es||False	f	t	t
SANTANDER MIXTO ACCIONES	ES0145814036	EUR	2	|BMF|0012|	f	77084	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0145814036||es||False	f	t	t
DAEDALUS VARIABLE	ES0125302002	EUR	2	|BMF|0195|	f	77087	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125302002||es||False	f	t	t
CAIXA CATALUNYA PROPIETAT	ES0113248035	EUR	2	|BMF|0020|	f	77088	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113248035||es||False	f	t	t
IBERCAJA SELECTIVO GARANTIZADO	ES0147198032	EUR	2	|BMF|0084|	f	77090	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147198032||es||False	f	t	t
ALFA OMEGA	ES0107934038	EUR	2	|BMF|0198|	f	77099	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107934038||es||False	f	t	t
ALFIL CAPITAL GLOBAL	ES0115066039	EUR	2	|BMF|0203|	f	77100	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115066039||es||False	f	t	t
BANIF RF CORTO PLAZO	ES0112793031	EUR	2	|BMF|0012|	f	77102	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112793031||es||False	f	t	t
BANIF RV ESPAÑA	ES0112795036	EUR	2	|BMF|0012|	f	77103	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112795036||es||False	f	t	t
ALFIL CAPITAL RENTABILIDAD ABSOL	ES0107954036	EUR	2	|BMF|0203|	f	77105	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107954036||es||False	f	t	t
BANIF SELECCION 1	ES0112796034	EUR	2	|BMF|0012|	f	77107	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112796034||es||False	f	t	t
FONDO TRIPLE OPCION AGRICULTURA	ES0138227030	EUR	2	|BMF|0012|	f	77110	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138227030||es||False	f	t	t
BANIF TESORERIA FONDTESORO CP	ES0112791035	EUR	2	|BMF|0012|	f	77115	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112791035||es||False	f	t	t
CAJA MADRID TITANES	ES0158964033	EUR	2	|BMF|0085|	f	77122	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158964033||es||False	f	t	t
CAJA MADRID TITANES II	ES0109222036	EUR	2	|BMF|0085|	f	77123	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109222036||es||False	f	t	t
KUTXAMONETARIO3	ES0156977037	EUR	2	|BMF|0086|	f	77124	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0156977037||es||False	f	t	t
KUTXAOPPORTUNITIES	ES0157003031	EUR	2	|BMF|0086|	f	77125	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157003031||es||False	f	t	t
KUTXAPLUS	ES0157027030	EUR	2	|BMF|0086|	f	77130	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157027030||es||False	f	t	t
MADRID GESTION ACTIVA 100	ES0159037037	EUR	2	|BMF|0085|	f	77131	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159037037||es||False	f	t	t
CAJAMAR MULTIGESTION MODERADO	ES0109226037	EUR	2	|BMF|0069|	f	77135	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109226037||es||False	f	t	t
CAM FUTURO SELECCION 7	ES0140982036	EUR	2	|BMF|0127|	f	77136	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0140982036||es||False	f	t	t
CARTESIO X	ES0116567035	EUR	2	|BMF|0221|	f	77137	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116567035||es||False	f	t	t
CARTESIO Y	ES0182527038	EUR	2	|BMF|0221|	f	77139	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182527038||es||False	f	t	t
CATALANA OCCIDENTE BOLSA ESP.	ES0116901036	EUR	2	|BMF|0037|	f	77140	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116901036||es||False	f	t	t
CATALANA OCCIDENTE BOLSA MUNDIAL	ES0116881030	EUR	2	|BMF|0037|	f	77142	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116881030||es||False	f	t	t
F.VALENCIA GAR.ELECCION OPT.2	ES0138228038	EUR	2	|BMF|0083|	f	77143	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138228038||es||False	f	t	t
FIDEFONDO	ES0137631034	EUR	2	|BMF|0058|	f	77145	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137631034||es||False	f	t	t
MADRID GESTION ACTIVA 25	ES0158976037	EUR	2	|BMF|0085|	f	77147	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158976037||es||False	f	t	t
MADRID GESTION ACTIVA 50	ES0159084039	EUR	2	|BMF|0085|	f	77150	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159084039||es||False	f	t	t
UNIFOND EUROBOLSA	ES0181034036	EUR	2	|BMF|0154|	f	77158	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181034036||es||False	f	t	t
VITAL DIVISA	ES0184249037	EUR	2	|BMF|0007|	f	77168	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184249037||es||False	f	t	t
MADRID GESTION ACTIVA 75	ES0158986036	EUR	2	|BMF|0085|	f	77169	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158986036||es||False	f	t	t
MADRID IBEX PREMIUM 100-I	ES0159081035	EUR	2	|BMF|0085|	f	77170	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159081035||es||False	f	t	t
SANTANDER RENTA FIJA A	ES0146133006	EUR	2	|BMF|0012|	f	77173	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146133006||es||False	f	t	t
SANTANDER TESORERO I	ES0112744034	EUR	2	|BMF|0012|	f	77174	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112744034||es||False	f	t	t
SEGUNDA GENERACION RENTA	ES0175426032	EUR	2	|BMF|0061|	f	77175	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175426032||es||False	f	t	t
SEGURFONDO ASIA	ES0138281037	EUR	2	|BMF|0098|	f	77176	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138281037||es||False	f	t	t
FONCAIXA GESTION ALTERNATIVA V6	ES0145456002	EUR	2	|BMF|0015|	f	77189	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0145456002||es||False	f	t	t
FONCAIXA PRIVADA ESTRATEGIA HEDG	ES0164463004	EUR	2	|BMF|0015|	f	77190	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164463004||es||False	f	t	t
CAIXA CATALUNYA CREIXEMENT	ES0115405039	EUR	2	|BMF|0020|	f	77204	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115405039||es||False	f	t	t
CATALANA OCCIDENTE PATRIMONIO	ES0116903032	EUR	2	|BMF|0037|	f	77212	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116903032||es||False	f	t	t
COMPROMISO FONDO ETICO	ES0121091039	EUR	2	|BMF|0061|	f	77214	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0121091039||es||False	f	t	t
CONSTANTFONS	ES0121776035	EUR	2	|BMF|0029|	f	77217	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0121776035||es||False	f	t	t
CONSULNOR RENTA FIJA DOS AÑOS	ES0123547004	EUR	2	|BMF|0160|	f	77218	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0123547004||es||False	f	t	t
MANRESA DINAMIC 25	ES0159505033	EUR	2	|BMF|0076|	f	77221	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159505033||es||False	f	t	t
SEGURFONDO USA	ES0175447038	EUR	2	|BMF|0098|	f	77225	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175447038||es||False	f	t	t
SELECTOR GLOBAL	ES0175450032	EUR	2	|BMF|0206|	f	77226	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175450032||es||False	f	t	t
SEQUEFONDO	ES0132467038	EUR	2	|BMF|0063|	f	77227	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0132467038||es||False	f	t	t
GESTIOHNA DINERO.	ES0152505006	EUR	2	|BMF|0194|	f	77228	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0152505006||es||False	f	t	t
UBS GLOBAL GESTION ACTIVA CLASE I	ES0122073036	EUR	2	|BMF|0185|	f	77229	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122073036||es||False	f	t	t
UBS GLOBAL GESTION ACTIVA CLASE P	ES0122073002	EUR	2	|BMF|0185|	f	77230	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122073002||es||False	f	t	t
BBK  OPVS	ES0113275004	EUR	2	|BMF|0095|	f	77243	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113275004||es||False	f	t	t
BBK 0/100 CARTERAS	ES0113053005	EUR	2	|BMF|0095|	f	77244	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113053005||es||False	f	t	t
BBK BOLSA	ES0114388038	EUR	2	|BMF|0095|	f	77245	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114388038||es||False	f	t	t
BBK BOLSA EEUU	ES0113191037	EUR	2	|BMF|0095|	f	77260	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113191037||es||False	f	t	t
CAIXA GALICIA EUROBOLSA	ES0115411037	EUR	2	|BMF|0128|	f	77262	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115411037||es||False	f	t	t
CAIXA GALICIA IBEXPLUS	ES0115289037	EUR	2	|BMF|0128|	f	77264	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115289037||es||False	f	t	t
CAIXA GALICIA INVERSIONES	ES0107470033	EUR	2	|BMF|0128|	f	77265	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107470033||es||False	f	t	t
CAIXA GALICIA MIX	ES0115418032	EUR	2	|BMF|0128|	f	77266	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115418032||es||False	f	t	t
BARCLAYS GARANTIZADO 14	ES0184844035	EUR	2	|BMF|0063|	f	77282	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184844035||es||False	f	t	t
BANKOA IBEX 106 GARANTIZADO 2	ES0180655039	EUR	2	|BMF|0035|	f	77285	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180655039||es||False	f	t	t
BARCLAYS GESTION 50	ES0110058031	EUR	2	|BMF|0063|	f	77287	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110058031||es||False	f	t	t
BARCLAYS GESTION DINAMICA 150	ES0184928036	EUR	2	|BMF|0063|	f	77289	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184928036||es||False	f	t	t
BANKOA DEUDA PUBLICA	ES0113690038	EUR	2	|BMF|0035|	f	77294	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113690038||es||False	f	t	t
BARCLAYS RENDIMIENTO EFECTIVO	ES0170456034	EUR	2	|BMF|0063|	f	77297	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170456034||es||False	f	t	t
BBK BOLSA EURO	ES0114221031	EUR	2	|BMF|0095|	f	77298	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114221031||es||False	f	t	t
ALFIL FONTOTAL	ES0107955009	EUR	2	|BMF|0203|	f	77304	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107955009||es||False	f	t	t
BBK BOLSA JAPON	ES0114232038	EUR	2	|BMF|0095|	f	77308	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114232038||es||False	f	t	t
BBK BOLSAS EMERGENTES	ES0114233036	EUR	2	|BMF|0095|	f	77309	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114233036||es||False	f	t	t
BBK BONO	ES0114276035	EUR	2	|BMF|0095|	f	77310	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114276035||es||False	f	t	t
BBK DINAMICO	ES0114202031	EUR	2	|BMF|0095|	f	77311	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114202031||es||False	f	t	t
BBK GARANTIZADO 7	ES0113452033	EUR	2	|BMF|0095|	f	77312	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113452033||es||False	f	t	t
DWS INVEST	ES0125784035	EUR	2	|BMF|0142|	f	77313	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125784035||es||False	f	t	t
MANRESA GARANTIT 10	ES0160102002	EUR	2	|BMF|0076|	f	77314	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160102002||es||False	f	t	t
MANRESA GARANTIT 11	ES0160103000	EUR	2	|BMF|0076|	f	77315	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160103000||es||False	f	t	t
MANRESA GARANTIT 12	ES0160104008	EUR	2	|BMF|0076|	f	77316	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160104008||es||False	f	t	t
MANRESA GARANTIT 13	ES0160105005	EUR	2	|BMF|0076|	f	77317	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160105005||es||False	f	t	t
SANTANDER MIXTO RENTA FIJA 90-10	ES0155818034	EUR	2	|BMF|0012|	f	77318	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155818034||es||False	f	t	t
UNIFOND  BOLSA PATRIMONIO	ES0176902007	EUR	2	|BMF|0154|	f	77319	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0176902007||es||False	f	t	t
UNIFOND 2011-VI	ES0181051030	EUR	2	|BMF|0154|	f	77320	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181051030||es||False	f	t	t
UNIFOND 2012-II	ES0180994032	EUR	2	|BMF|0154|	f	77321	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180994032||es||False	f	t	t
UNIFOND 2012-III	ES0181033038	EUR	2	|BMF|0154|	f	77322	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181033038||es||False	f	t	t
UNIFOND 2012-IV	ES0181041031	EUR	2	|BMF|0154|	f	77323	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181041031||es||False	f	t	t
UNIFOND 2012-IX	ES0181065030	EUR	2	|BMF|0154|	f	77324	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181065030||es||False	f	t	t
UNIFOND 2012-V	ES0181050032	EUR	2	|BMF|0154|	f	77325	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181050032||es||False	f	t	t
UNIFOND 2012-VI	ES0178234037	EUR	2	|BMF|0154|	f	77326	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0178234037||es||False	f	t	t
BBK BOLSA EEUU NUEVA ECONOMIA	ES0114222039	EUR	2	|BMF|0095|	f	77330	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114222039||es||False	f	t	t
BBK DIVIDENDO	ES0133759037	EUR	2	|BMF|0095|	f	77331	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133759037||es||False	f	t	t
BBK EMPRESAS DINAMICO	ES0137724003	EUR	2	|BMF|0095|	f	77332	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137724003||es||False	f	t	t
BBK FONDINERO	ES0114262035	EUR	2	|BMF|0095|	f	77333	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114262035||es||False	f	t	t
BBK FONDO INTERNACIONAL	ES0113987038	EUR	2	|BMF|0095|	f	77336	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113987038||es||False	f	t	t
BBK GARANTIZADO BOLSA	ES0114234034	EUR	2	|BMF|0095|	f	77337	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114234034||es||False	f	t	t
BBK GARANTIZADO BOLSA 2	ES0113453031	EUR	2	|BMF|0095|	f	77345	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113453031||es||False	f	t	t
BBK GARANTIZADO BOLSA 3	ES0125625006	EUR	2	|BMF|0095|	f	77346	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125625006||es||False	f	t	t
ESAF GAR.RENTABILIDAD SEGURA	ES0168624007	EUR	2	|BMF|0047|	f	77361	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168624007||es||False	f	t	t
UNIFOND 2012-VII	ES0181011034	EUR	2	|BMF|0154|	f	77365	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181011034||es||False	f	t	t
UNIFOND 2011-II	ES0178233039	EUR	2	|BMF|0154|	f	77366	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0178233039||es||False	f	t	t
UNIFOND 2013-IX	ES0181394000	EUR	2	|BMF|0154|	f	77367	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181394000||es||False	f	t	t
ALLIANZ BOLSA	ES0108372030	EUR	2	|BMF|0168|	f	77371	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108372030||es||False	f	t	t
ALLIANZ MIXTO	ES0108280035	EUR	2	|BMF|0168|	f	77372	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108280035||es||False	f	t	t
ALLIANZ RENTA FIJA AHORRO	ES0108371032	EUR	2	|BMF|0168|	f	77378	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108371032||es||False	f	t	t
FONCAIXA BOLSA 54	ES0182824039	EUR	2	|BMF|0015|	f	77380	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182824039||es||False	f	t	t
ALLIANZ RF CORTO EUROLAND	ES0108251036	EUR	2	|BMF|0168|	f	77388	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108251036||es||False	f	t	t
A & G MULTISELECTION FUND	ES0105012035	EUR	2	|BMF|0195|	f	77389	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105012035||es||False	f	t	t
BANESTO 100%CAPITAL MEJOR OPCION	ES0113916037	EUR	2	|BMF|0012|	f	77394	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113916037||es||False	f	t	t
BARCLAYS GARANTIZADO 10	ES0133801037	EUR	2	|BMF|0063|	f	77395	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133801037||es||False	f	t	t
IBERCAJA BP DIGITAL 2	ES0146921004	EUR	2	|BMF|0084|	f	77400	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146921004||es||False	f	t	t
JP MORGAN GLOBAL ALTERNATIVE FUN	ES0156581003	EUR	2	|BMF|0059|	f	77401	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0156581003||es||False	f	t	t
ALLIANZ SELECCION CONSERVADOR	ES0108341035	EUR	2	|BMF|0168|	f	77402	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108341035||es||False	f	t	t
BBK GARANTIZADO BOLSA EUROPA 2	ES0114235031	EUR	2	|BMF|0095|	f	77404	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114235031||es||False	f	t	t
BBK GESTION ACTIVA PATRIMONIO	ES0114836036	EUR	2	|BMF|0095|	f	77406	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114836036||es||False	f	t	t
ESPINOSA PARTNERS INVERSIONES	ES0133091035	EUR	2	|BMF|0210|	f	77407	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133091035||es||False	f	t	t
ESPIRITO SANTO CAPITAL PLUS	ES0125240038	EUR	2	|BMF|0113|	f	77408	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125240038||es||False	f	t	t
MANRESA GARANTIT 9	ES0159506007	EUR	2	|BMF|0076|	f	77410	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159506007||es||False	f	t	t
UNIFOND 2013-X	ES0181067036	EUR	2	|BMF|0154|	f	77412	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181067036||es||False	f	t	t
UNIFOND INTERES ANUAL	ES0180984033	EUR	2	|BMF|0154|	f	77413	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180984033||es||False	f	t	t
UNIFOND 2010-XII	ES0181064033	EUR	2	|BMF|0154|	f	77414	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181064033||es||False	f	t	t
VALORICA GLOBAL	ES0182798001	EUR	2	|BMF|0223|	f	77415	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182798001||es||False	f	t	t
VALORICA MACRO	ES0182856007	EUR	2	|BMF|0223|	f	77416	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182856007||es||False	f	t	t
VENTURE BOLSA AMERICANA	ES0183221037	EUR	2	|BMF|0197|	f	77417	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0183221037||es||False	f	t	t
VENTURE BOLSA EUROPEA	ES0183283037	EUR	2	|BMF|0197|	f	77418	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0183283037||es||False	f	t	t
ALTAE PLUS	ES0177042035	EUR	2	|BMF|0085|	f	77425	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0177042035||es||False	f	t	t
AMISTRA GLOBAL, FI	ES0109213001	EUR	2	|BMF|0232|	f	77427	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109213001||es||False	f	t	t
EUROFONDO	ES0133812034	EUR	2	|BMF|0029|	f	77431	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133812034||es||False	f	t	t
BARCLAYS MULTIMANAGER PLUS	ES0184825034	EUR	2	|BMF|0063|	f	77434	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184825034||es||False	f	t	t
FONCAIXA GARAN.EUROPA PROT.IX	ES0137697001	EUR	2	|BMF|0015|	f	77435	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137697001||es||False	f	t	t
EUROVALOR BANCA SEGUROS	ES0133484008	EUR	2	|BMF|0004|	f	77436	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133484008||es||False	f	t	t
BBK GESTION ACTIVA RENDIMIENTO	ES0114390034	EUR	2	|BMF|0095|	f	77441	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114390034||es||False	f	t	t
BBK R.F. OPORTUNIDAD CARTERAS	ES0125627002	EUR	2	|BMF|0095|	f	77443	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125627002||es||False	f	t	t
FONCAIXA PRIVADA MULTIG.ACT.VARI	ES0106194030	EUR	2	|BMF|0015|	f	77444	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0106194030||es||False	f	t	t
BBK REAL ESTATE MUNDIAL	ES0114236039	EUR	2	|BMF|0095|	f	77445	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114236039||es||False	f	t	t
BBK RENTA FIJA 2014	ES0113423034	EUR	2	|BMF|0095|	f	77446	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113423034||es||False	f	t	t
BBK RENTA FIJA 3 MESES	ES0114256037	EUR	2	|BMF|0095|	f	77458	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114256037||es||False	f	t	t
BBK RENTA GLOBAL	ES0114387030	EUR	2	|BMF|0095|	f	77459	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114387030||es||False	f	t	t
BBK CAPITAL PARTNERS	ES0114237037	EUR	2	|BMF|0095|	f	77460	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114237037||es||False	f	t	t
BESTINVER MIXTO INTERNACIONAL	ES0114618038	EUR	2	|BMF|0103|	f	77461	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114618038||es||False	f	t	t
EUROVALOR GARANT.REC.NATURALES	ES0133542037	EUR	2	|BMF|0004|	f	77462	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133542037||es||False	f	t	t
IBERCAJA ACTIVO GARANTIZADO	ES0147103032	EUR	2	|BMF|0084|	f	77490	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147103032||es||False	f	t	t
FONDESPAÑA CONSOLIDA 4	ES0182036030	EUR	2	|BMF|0130|	f	77491	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182036030||es||False	f	t	t
BETA ACCIONES	ES0114677034	EUR	2	|BMF|0061|	f	77492	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114677034||es||False	f	t	t
AHORRO CORP. DEUDA FONDT. L.P.	ES0107521033	EUR	2	|BMF|0128|	f	77493	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107521033||es||False	f	t	t
EUROVALOR PARTICULARES VOLUMEN FI CL. I	ES0133877003	EUR	2	|BMF|0004|	f	77510	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133877003||es||False	f	t	t
EUROVALOR RENTA FIJA INTERNAC.	ES0138966033	EUR	2	|BMF|0004|	f	77511	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138966033||es||False	f	t	t
EUROVALOR RV EMERGENTES GLOBAL	ES0133561037	EUR	2	|BMF|0004|	f	77513	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133561037||es||False	f	t	t
VENTURE CORTO PLAZO	ES0183302035	EUR	2	|BMF|0197|	f	77514	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0183302035||es||False	f	t	t
VENTURE GESTION GLOBAL	ES0183261033	EUR	2	|BMF|0197|	f	77515	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0183261033||es||False	f	t	t
VENTURE GLOBAL	ES0183342031	EUR	2	|BMF|0197|	f	77516	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0183342031||es||False	f	t	t
VENTURE MIXTO R.FIJA	ES0183216037	EUR	2	|BMF|0197|	f	77517	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0183216037||es||False	f	t	t
FON FINECO EXCEL	ES0137651008	EUR	2	|BMF|0132|	f	77524	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137651008||es||False	f	t	t
MADRID RENTA BASE 5	ES0159090036	EUR	2	|BMF|0085|	f	77525	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159090036||es||False	f	t	t
FONCAIXA PRIVADA EURO ACCIONES	ES0105008033	EUR	2	|BMF|0015|	f	77528	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105008033||es||False	f	t	t
CAIXA CATALUNYA CONVERTIBLES	ES0115337034	EUR	2	|BMF|0020|	f	77531	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115337034||es||False	f	t	t
CAAM EURO REPO	ES0126541038	EUR	2	|BMF|0031|	f	77538	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126541038||es||False	f	t	t
CAIXA CATALUNYA BORSA EUROPEA	ES0115334031	EUR	2	|BMF|0020|	f	77541	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115334031||es||False	f	t	t
FONDESPAÑA II	ES0138881034	EUR	2	|BMF|0128|	f	77547	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138881034||es||False	f	t	t
FONCAIXA BANCA PERS.BOLSA GLOBAL	ES0137652006	EUR	2	|BMF|0015|	f	77550	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137652006||es||False	f	t	t
SANTANDER AHORRO CORTO PLAZO	ES0175831033	EUR	2	|BMF|0012|	f	77551	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175831033||es||False	f	t	t
BNP PARIBAS EQUILIBRADO	ES0171955034	EUR	2	|BMF|0061|	f	77556	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0171955034||es||False	f	t	t
BNP PARIBAS EURO	ES0125472037	EUR	2	|BMF|0061|	f	77557	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125472037||es||False	f	t	t
BNP PARIBAS GLOBAL CONSERVATIVE	ES0118552035	EUR	2	|BMF|0061|	f	77558	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0118552035||es||False	f	t	t
FON FINECO GESTION	ES0138382033	EUR	2	|BMF|0132|	f	77559	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138382033||es||False	f	t	t
FON FINECO I	ES0138783032	EUR	2	|BMF|0132|	f	77561	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138783032||es||False	f	t	t
SANTANDER SOLIDARIO DIVIDENDO EUROPA	ES0114350038	EUR	2	|BMF|0012|	f	77562	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114350038||es||False	f	t	t
VITAL BOLSA INDICE	ES0184201038	EUR	2	|BMF|0007|	f	77568	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184201038||es||False	f	t	t
VITAL DEUDA 1	ES0184240036	EUR	2	|BMF|0007|	f	77569	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184240036||es||False	f	t	t
VITALDINERO	ES0184275032	EUR	2	|BMF|0007|	f	77666	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184275032||es||False	f	t	t
WELZIA BANKS	ES0184592030	EUR	2	|BMF|0207|	f	77667	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184592030||es||False	f	t	t
WELZIA ROCKLEDGE MULTISECTORIAL	ES0184593004	EUR	2	|BMF|0207|	f	77668	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184593004||es||False	f	t	t
WELZIA SIGMA 10	ES0184684035	EUR	2	|BMF|0207|	f	77669	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184684035||es||False	f	t	t
WELZIA SIGMA 15	ES0184676031	EUR	2	|BMF|0207|	f	77670	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184676031||es||False	f	t	t
WELZIA SIGMA 2	ES0184683037	EUR	2	|BMF|0207|	f	77671	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184683037||es||False	f	t	t
SANTANDER PREMIER CANCELABLE 3	ES0114314034	EUR	2	|BMF|0012|	f	77689	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114314034||es||False	f	t	t
SANTANDER PREMIER CANDELABLE AGUA	ES0112745007	EUR	2	|BMF|0012|	f	77690	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112745007||es||False	f	t	t
FONGAUDI	ES0147608030	EUR	2	|BMF|0061|	f	77695	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147608030||es||False	f	t	t
MARCH VALORES	ES0161033032	EUR	2	|BMF|0190|	f	77757	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0161033032||es||False	f	t	t
GLOBAL MANAGERS FUND	ES0131304034	EUR	2	|BMF|0195|	f	77758	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0131304034||es||False	f	t	t
MARCHFONDO	ES0148198031	EUR	2	|BMF|0190|	f	77762	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0148198031||es||False	f	t	t
MULTIFONDO EFICIENTE	ES0138614039	EUR	2	|BMF|0132|	f	77763	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138614039||es||False	f	t	t
MULTIFONDO JAPON	ES0164813034	EUR	2	|BMF|0132|	f	77764	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164813034||es||False	f	t	t
MULTIFONDOS VITAL	ES0165096035	EUR	2	|BMF|0007|	f	77765	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165096035||es||False	f	t	t
IBERCAJA EUROPA GARANTIZADO	ES0147154035	EUR	2	|BMF|0084|	f	77766	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147154035||es||False	f	t	t
SANTANDER PREMIER CANCELABLE 2	ES0107995005	EUR	2	|BMF|0012|	f	77795	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107995005||es||False	f	t	t
BANCAJA FONDO DE FONDOS EMERGENT	ES0130352034	EUR	2	|BMF|0083|	f	77807	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0130352034||es||False	f	t	t
BANCAJA GARANT.10	ES0112972031	EUR	2	|BMF|0083|	f	77808	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112972031||es||False	f	t	t
MANRESA GARANTIT 1	ES0115415038	EUR	2	|BMF|0076|	f	77809	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115415038||es||False	f	t	t
BANCAJA GARANT.RENTA VARIABLE 7	ES0112896032	EUR	2	|BMF|0083|	f	77811	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112896032||es||False	f	t	t
BANCAJA GARANTIZADO 12	ES0112964038	EUR	2	|BMF|0083|	f	77812	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112964038||es||False	f	t	t
SANTANDER PREMIER CANCELABLE.	ES0107894000	EUR	2	|BMF|0012|	f	77825	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107894000||es||False	f	t	t
PLATINUM RENTA FIJA 2011	ES0182553034	EUR	2	|BMF|0085|	f	77829	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182553034||es||False	f	t	t
PRIVARY F1 DISCRECIONAL	ES0170900031	EUR	2	|BMF|0083|	f	77832	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170900031||es||False	f	t	t
FONDO ANTICIPACION CONSERVADOR	ES0137940039	EUR	2	|BMF|0012|	f	77836	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137940039||es||False	f	t	t
OKAVANGODELTA	ES0167211038	EUR	2	|BMF|0194|	f	77838	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0167211038||es||False	f	t	t
RURAL CESTA ASIATICA GARANTIZADO	ES0174224032	EUR	2	|BMF|0140|	f	77929	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174224032||es||False	f	t	t
RURAL CESTA CONSERVADORA 20	ES0174349037	EUR	2	|BMF|0140|	f	77937	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174349037||es||False	f	t	t
BG EUROMARKET BOLSA	ES0144098037	EUR	2	|BMF|0110|	f	77950	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0144098037||es||False	f	t	t
RURAL EMERGENTES RENTA VARIABLE	ES0174365033	EUR	2	|BMF|0140|	f	77982	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174365033||es||False	f	t	t
RURAL EURO DOLAR GARANTIZADO	ES0174372039	EUR	2	|BMF|0140|	f	77983	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174372039||es||False	f	t	t
RURAL EURO RENTA VARIABLE	ES0174367039	EUR	2	|BMF|0140|	f	77984	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174367039||es||False	f	t	t
RURAL EUROPA 2012 GARANTIA	ES0174371031	EUR	2	|BMF|0140|	f	77985	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174371031||es||False	f	t	t
BG EURO YIELD	ES0184976035	EUR	2	|BMF|0110|	f	78004	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184976035||es||False	f	t	t
CAIXA CATALUNYA DOBLE	ES0115456032	EUR	2	|BMF|0020|	f	78007	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115456032||es||False	f	t	t
BG FOND EMPRESA	ES0134609033	EUR	2	|BMF|0110|	f	78008	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0134609033||es||False	f	t	t
CAIXA CATALUNYA EUROBORSA GARANTIT	ES0105574034	EUR	2	|BMF|0020|	f	78009	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105574034||es||False	f	t	t
BG GESTION INMOBILIARIA GARANTIZADA	ES0125933038	EUR	2	|BMF|0110|	f	78010	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125933038||es||False	f	t	t
CAIXA CATALUNYA FONDTESORO	ES0114990031	EUR	2	|BMF|0020|	f	78011	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114990031||es||False	f	t	t
CAIXA CATALUNYA FONS INTERNAC.	ES0115417034	EUR	2	|BMF|0020|	f	78012	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115417034||es||False	f	t	t
BG EUSKOVALOR	ES0184977033	EUR	2	|BMF|0110|	f	78014	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184977033||es||False	f	t	t
CAIXA CATALUNYA BORSA 13	ES0105573036	EUR	2	|BMF|0020|	f	78015	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105573036||es||False	f	t	t
CAIXAGIRONA PATRIMONI	ES0115347033	EUR	2	|BMF|0006|	f	78118	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115347033||es||False	f	t	t
CAIXANOVA GARANTIZADO GLOBAL III	ES0115081038	EUR	2	|BMF|0128|	f	78122	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115081038||es||False	f	t	t
CAIXANOVA GARANTIZADO PRIVILEGE	ES0115329031	EUR	2	|BMF|0128|	f	78126	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115329031||es||False	f	t	t
CAIXANOVA GARANTIZADO RENTA FIJA	ES0115018006	EUR	2	|BMF|0128|	f	78129	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115018006||es||False	f	t	t
CAIXANOVA GARANTIZADO RENTAS	ES0115212039	EUR	2	|BMF|0128|	f	78130	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115212039||es||False	f	t	t
SABADELL BS ESPAÑA DIVIDENDO	ES0111092039	EUR	2	|BMF|0058|	f	78133	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111092039||es||False	f	t	t
ABANTE BOLSA ABSOLUTA CLASE I	ES0109655003	EUR	2	|BMF|0194|	f	78139	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109655003||es||False	f	t	t
ABANTE PATRIMONIO GLOBAL CLASE I	ES0105013009	EUR	2	|BMF|0194|	f	78141	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105013009||es||False	f	t	t
ABANTE RENTAB.ABSOLUTA CLASE I	ES0184837005	EUR	2	|BMF|0194|	f	78143	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184837005||es||False	f	t	t
ABANTE RENTABILIDAD ABSOLUTA	ES0184837039	EUR	2	|BMF|0194|	f	78144	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184837039||es||False	f	t	t
CAIXANOVA GARANTIZADO GLOBAL II	ES0115080030	EUR	2	|BMF|0128|	f	78148	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115080030||es||False	f	t	t
SABADELL BS ESTADOS UNIDOS BOLSA	ES0138983038	EUR	2	|BMF|0058|	f	78156	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138983038||es||False	f	t	t
SABADELL BS EUROACCION	ES0111098036	EUR	2	|BMF|0058|	f	78158	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111098036||es||False	f	t	t
ABANTE ASESORES GLOBAL	ES0109652034	EUR	2	|BMF|0194|	f	78173	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109652034||es||False	f	t	t
ABANTE BOLSA ABSOLUTA	ES0109655037	EUR	2	|BMF|0194|	f	78181	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109655037||es||False	f	t	t
ABANTE SELECCION	ES0162946034	EUR	2	|BMF|0194|	f	78184	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162946034||es||False	f	t	t
ABANTE TESORERIA	ES0190051039	EUR	2	|BMF|0194|	f	78188	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0190051039||es||False	f	t	t
AC EUROSTOXX GARANTIZADO 100	ES0107396006	EUR	2	|BMF|0128|	f	78190	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107396006||es||False	f	t	t
ACACIA BONOMIX	ES0105243002	EUR	2	|BMF|0995|	f	78191	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105243002||es||False	f	t	t
ACACIA PREMIUM	ES0105263000	EUR	2	|BMF|0995|	f	78195	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105263000||es||False	f	t	t
ARCALIA GARANTIZADO RENTA FIJA	ES0156732002	EUR	2	|BMF|0083|	f	78196	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0156732002||es||False	f	t	t
BESTINFOND	ES0114673033	EUR	2	|BMF|0103|	f	78323	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114673033||es||False	f	t	t
BESTINVER BOLSA	ES0147622031	EUR	2	|BMF|0103|	f	78324	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147622031||es||False	f	t	t
BESTINVER INTERNACIONAL	ES0114638036	EUR	2	|BMF|0103|	f	78330	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114638036||es||False	f	t	t
BESTINVER RENTA	ES0114675038	EUR	2	|BMF|0103|	f	78331	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114675038||es||False	f	t	t
BIZKAIRENT FONDTESORO	ES0114870035	EUR	2	|BMF|0095|	f	78342	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114870035||es||False	f	t	t
SABADELL BS GARANTIA EUROBOLSA	ES0182179038	EUR	2	|BMF|0058|	f	78350	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182179038||es||False	f	t	t
AHORRO CORP. CAPITAL 1	ES0106941034	EUR	2	|BMF|0128|	f	78351	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0106941034||es||False	f	t	t
BG CAPITAL ASEGURADO	ES0144096031	EUR	2	|BMF|0110|	f	78353	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0144096031||es||False	f	t	t
BG ENERGIA GARANTIZADA	ES0114613005	EUR	2	|BMF|0110|	f	78355	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114613005||es||False	f	t	t
BG FONCARTERA 1	ES0114682034	EUR	2	|BMF|0110|	f	78357	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114682034||es||False	f	t	t
BG GESTION INMOB.GARANTIZADA 2	ES0114623038	EUR	2	|BMF|0110|	f	78365	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114623038||es||False	f	t	t
BG IZARBE	ES0156332035	EUR	2	|BMF|0110|	f	78371	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0156332035||es||False	f	t	t
BG MIXTO 25	ES0144099035	EUR	2	|BMF|0110|	f	78378	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0144099035||es||False	f	t	t
BG MIXTO 50	ES0144100031	EUR	2	|BMF|0110|	f	78379	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0144100031||es||False	f	t	t
AHORRO CORP. CAPITAL 6	ES0107432033	EUR	2	|BMF|0128|	f	78403	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107432033||es||False	f	t	t
AHORRO CORP. CUENTA FONDT.C.P.	ES0107519037	EUR	2	|BMF|0128|	f	78405	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107519037||es||False	f	t	t
AHORRO CORP. EUROMIX	ES0106925037	EUR	2	|BMF|0128|	f	78406	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0106925037||es||False	f	t	t
AHORRO CORP. EUROPA	ES0107492037	EUR	2	|BMF|0128|	f	78418	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107492037||es||False	f	t	t
AHORRO CORP. EUROSTOXX 50 INDICE	ES0107365035	EUR	2	|BMF|0128|	f	78419	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107365035||es||False	f	t	t
BIZKAIFONDO	ES0114865035	EUR	2	|BMF|0095|	f	78420	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114865035||es||False	f	t	t
AHORRO CORP. FONDANDALUCIA MIXTO	ES0107384036	EUR	2	|BMF|0128|	f	78442	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107384036||es||False	f	t	t
AHORRO CORP. FONDT.LARGO PLAZO	ES0107531032	EUR	2	|BMF|0128|	f	78450	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107531032||es||False	f	t	t
AHORRO CORP. IBEROAMERICA	ES0107474035	EUR	2	|BMF|0128|	f	78452	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107474035||es||False	f	t	t
AHORRO CORP. IBEX-35 INDICE	ES0107262034	EUR	2	|BMF|0128|	f	78453	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107262034||es||False	f	t	t
AHORRO CORP. RESPONSABLE 30	ES0107387039	EUR	2	|BMF|0128|	f	78456	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107387039||es||False	f	t	t
AHORRO CORP.EURIBOR MAS 50 GAR.2	ES0107534036	EUR	2	|BMF|0128|	f	78458	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107534036||es||False	f	t	t
AHORRO CORPORACION DOLAR	ES0107436034	EUR	2	|BMF|0128|	f	78462	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107436034||es||False	f	t	t
AHORRO CORPORACION CONSERV.VAR 3	ES0106951033	EUR	2	|BMF|0128|	f	78463	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0106951033||es||False	f	t	t
BANCAJA GARANTIZA. GLOBAL TITANS	ES0130353032	EUR	2	|BMF|0083|	f	78470	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0130353032||es||False	f	t	t
AHORRO CORP.INVERSION SELEC.MODE	ES0106928031	EUR	2	|BMF|0128|	f	78484	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0106928031||es||False	f	t	t
AHORRO CORP.INVERSION SELECTIVA	ES0106949037	EUR	2	|BMF|0128|	f	78485	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0106949037||es||False	f	t	t
BANCAJA GARANTIZADO 13	ES0112965001	EUR	2	|BMF|0083|	f	78488	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112965001||es||False	f	t	t
AHORRO CORP.PLAZO GARANTIZADO	ES0107397004	EUR	2	|BMF|0128|	f	78497	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107397004||es||False	f	t	t
AHORRO CORP.STAND.&POOR'S 500 IN	ES0106927033	EUR	2	|BMF|0128|	f	78501	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0106927033||es||False	f	t	t
BANIF 2011	ES0115216030	EUR	2	|BMF|0012|	f	78505	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115216030||es||False	f	t	t
AHORRO CORPORACION MODER.VAR 7	ES0107393037	EUR	2	|BMF|0128|	f	78519	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107393037||es||False	f	t	t
AHORRO CORPORACION EURIBOR+50 G	ES0107368005	EUR	2	|BMF|0128|	f	78529	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107368005||es||False	f	t	t
AHORRO CORPORACION FONDEPOSITO	ES0106933031	EUR	2	|BMF|0128|	f	78530	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0106933031||es||False	f	t	t
AHORRO CORPORACION MONETARIO	ES0107437008	EUR	2	|BMF|0128|	f	78534	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107437008||es||False	f	t	t
AHORRO CORPORACION PLAZO RENT. 3	ES0106931035	EUR	2	|BMF|0128|	f	78535	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0106931035||es||False	f	t	t
AHORRO CORPORACION RF EURO 2	ES0155841036	EUR	2	|BMF|0128|	f	78536	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155841036||es||False	f	t	t
BANESTO RENTA FIJA BONOS	ES0138877032	EUR	2	|BMF|0012|	f	78537	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138877032||es||False	f	t	t
BANESTO RENTA VARIABLE ESPAÑOLA	ES0114039037	EUR	2	|BMF|0012|	f	78538	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114039037||es||False	f	t	t
BNP PARIBAS MANAGEMENT FUND	ES0118553033	EUR	2	|BMF|0061|	f	78546	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0118553033||es||False	f	t	t
CAAM MULTIFONDO GLOBAL	ES0126545039	EUR	2	|BMF|0031|	f	78547	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126545039||es||False	f	t	t
CAHISPA MULTIFONDO	ES0112799038	EUR	2	|BMF|0029|	f	78591	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112799038||es||False	f	t	t
ALCALA-UNO	ES0107703037	EUR	2	|BMF|0137|	f	78595	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107703037||es||False	f	t	t
ALPHA PLUS RENTA FIJA EURO CORTO PLAZO B	ES0108686017	EUR	2	|BMF|0225|	f	78611	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108686017||es||False	f	t	t
ALPHA PLUS RENTABILIDAD ABSO. CLASE B	ES0108702012	EUR	2	|BMF|0225|	f	78615	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108702012||es||False	f	t	t
ALPHA PLUS RENTABILIDAD ABSOLUTA	ES0108702004	EUR	2	|BMF|0225|	f	78616	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108702004||es||False	f	t	t
CAHISPA EMERGENTES MULTIFONDO	ES0115272033	EUR	2	|BMF|0029|	f	78617	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115272033||es||False	f	t	t
CAHISPA EUROVARIABLE	ES0124541030	EUR	2	|BMF|0029|	f	78618	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0124541030||es||False	f	t	t
CAHISPA RENTA	ES0115399034	EUR	2	|BMF|0029|	f	78621	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115399034||es||False	f	t	t
CAHISPA SMALL CAPS	ES0115281034	EUR	2	|BMF|0029|	f	78622	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115281034||es||False	f	t	t
CAI 100 GARANTIZADO II	ES0115104038	EUR	2	|BMF|0128|	f	78623	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115104038||es||False	f	t	t
CAI AHORRO RENTA FIJA	ES0114844030	EUR	2	|BMF|0128|	f	78624	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114844030||es||False	f	t	t
CAIXANOVA GARANTIZADO RENTAS 2	ES0115349039	EUR	2	|BMF|0128|	f	78625	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115349039||es||False	f	t	t
DWS COMPAEURO	ES0121051033	EUR	2	|BMF|0142|	f	78626	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0121051033||es||False	f	t	t
AMUNDI CORTO PLAZO, CLASE I	ES0126542036	EUR	2	|BMF|0031|	f	78654	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126542036||es||False	f	t	t
ANNUALCYCLES STRATEGIES	ES0109298002	EUR	2	|BMF|0037|	f	78656	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109298002||es||False	f	t	t
ARCALIA BOLSA	ES0142552035	EUR	2	|BMF|0083|	f	78657	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142552035||es||False	f	t	t
ARCALIA COYUNTURA	ES0110085034	EUR	2	|BMF|0083|	f	78659	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110085034||es||False	f	t	t
ARCALIA GLOBAL	ES0110086032	EUR	2	|BMF|0083|	f	78660	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110086032||es||False	f	t	t
ARCALIA SELECCION	ES0142343039	EUR	2	|BMF|0083|	f	78661	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142343039||es||False	f	t	t
CAI BOLSA 10	ES0115351035	EUR	2	|BMF|0128|	f	78663	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115351035||es||False	f	t	t
CAI DEPOSITO	ES0114996038	EUR	2	|BMF|0128|	f	78665	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114996038||es||False	f	t	t
CAJA LABORAL BOLSA GARANT. X	ES0115311039	EUR	2	|BMF|0161|	f	78666	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115311039||es||False	f	t	t
CAJA LABORAL RENTA FIJA EURO	ES0164735039	EUR	2	|BMF|0161|	f	78667	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164735039||es||False	f	t	t
CAJABURGOS F.DE F.DINAMICO VAR 9	ES0169082031	EUR	2	|BMF|0128|	f	78673	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169082031||es||False	f	t	t
BBK GARANTIZADO 3 ACCIONES	ES0113551032	EUR	2	|BMF|0095|	f	78676	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113551032||es||False	f	t	t
BBK GARANTIZADO RENTA FIJA 10/14	ES0114585005	EUR	2	|BMF|0095|	f	78683	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114585005||es||False	f	t	t
ASTURFONDO GLOBAL	ES0110952035	EUR	2	|BMF|0176|	f	78692	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110952035||es||False	f	t	t
ASTURFONDO MIX-RENTA FIJA	ES0111028033	EUR	2	|BMF|0176|	f	78694	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111028033||es||False	f	t	t
ASTURFONDO MIX-RENTA VARIABLE	ES0111029031	EUR	2	|BMF|0176|	f	78695	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111029031||es||False	f	t	t
ASTURFONDO PLAZO II	ES0111013035	EUR	2	|BMF|0176|	f	78696	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111013035||es||False	f	t	t
BBK GARANTIZADO RENTA FIJA 2012 (2)	ES0113534004	EUR	2	|BMF|0095|	f	78698	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113534004||es||False	f	t	t
BANCA CIVICA CONFIANZA	ES0173438039	EUR	2	|BMF|0071|	f	78699	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173438039||es||False	f	t	t
BANCAJA CONSTRUCCION	ES0127794032	EUR	2	|BMF|0083|	f	78704	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0127794032||es||False	f	t	t
CAJACANARIAS GARANTIZADO	ES0142548033	EUR	2	|BMF|0128|	f	78709	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142548033||es||False	f	t	t
CAJAMAR MULTIGESTION PATRIMONIO	ES0114547039	EUR	2	|BMF|0069|	f	78710	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114547039||es||False	f	t	t
BESTINVER MIXTO	ES0114664032	EUR	2	|BMF|0103|	f	78719	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114664032||es||False	f	t	t
BIENVENIDOS A POPULAR	ES0125935009	EUR	2	|BMF|0004|	f	78720	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125935009||es||False	f	t	t
BANCAJA DIVIDENDOS	ES0112952033	EUR	2	|BMF|0083|	f	78732	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112952033||es||False	f	t	t
BARCLAYS BOLSA EUROPA	ES0138596038	EUR	2	|BMF|0063|	f	78733	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138596038||es||False	f	t	t
BEST CARMIGNAC	ES0114572003	EUR	2	|BMF|0105|	f	78740	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114572003||es||False	f	t	t
BEST JPMORGAN AM	ES0114524004	EUR	2	|BMF|0105|	f	78741	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114524004||es||False	f	t	t
CAJASUR RENTA FIJA EURO	ES0115445035	EUR	2	|BMF|0128|	f	78756	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115445035||es||False	f	t	t
CAñADA BLANCH	ES0115941033	EUR	2	|BMF|0203|	f	78757	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115941033||es||False	f	t	t
CCM CRECIMIENTO	ES0116967037	EUR	2	|BMF|0128|	f	78758	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116967037||es||False	f	t	t
CAI RENTA MIXTO 20	ES0101331033	EUR	2	|BMF|0128|	f	78766	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0101331033||es||False	f	t	t
BANCAJA GESTION ACTIVA 30	ES0112902038	EUR	2	|BMF|0083|	f	78774	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112902038||es||False	f	t	t
BANCAJA ENERGIA Y COMUNICACIONES	ES0130026034	EUR	2	|BMF|0083|	f	78778	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0130026034||es||False	f	t	t
BANCAJA GESTION ACTIVA 60	ES0112962032	EUR	2	|BMF|0083|	f	78780	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112962032||es||False	f	t	t
BANCAJA GESTION ACTIVA 90	ES0112893039	EUR	2	|BMF|0083|	f	78783	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112893039||es||False	f	t	t
BANCAJA GARANTIZADO 14	ES0112894037	EUR	2	|BMF|0083|	f	78785	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112894037||es||False	f	t	t
BANCAJA GARANTIZADO 15	ES0112966009	EUR	2	|BMF|0083|	f	78787	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112966009||es||False	f	t	t
BANCAJA GARANTIZADO 16	ES0140999030	EUR	2	|BMF|0083|	f	78789	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0140999030||es||False	f	t	t
BANCAJA GARANTIZADO 18	ES0112895034	EUR	2	|BMF|0083|	f	78790	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112895034||es||False	f	t	t
CAIXA CATALUNYA 1-B	ES0122701032	EUR	2	|BMF|0020|	f	78792	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122701032||es||False	f	t	t
CAIXA CATALUNYA GARANTIT 3 B	ES0118505009	EUR	2	|BMF|0020|	f	78793	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0118505009||es||False	f	t	t
CAIXA CATALUNYA PREVISIO	ES0138842036	EUR	2	|BMF|0020|	f	78795	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138842036||es||False	f	t	t
CAIXA CATALUNYA SPREAD	ES0115285035	EUR	2	|BMF|0020|	f	78807	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115285035||es||False	f	t	t
CAIXA GALICIA 5 MAS	ES0117182032	EUR	2	|BMF|0128|	f	78808	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117182032||es||False	f	t	t
BANESTO AHORRO ACTIVO	ES0113476032	EUR	2	|BMF|0012|	f	78816	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113476032||es||False	f	t	t
CAIXA GALICIA GARANT.5 ESTRELLAS	ES0115136030	EUR	2	|BMF|0128|	f	78832	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115136030||es||False	f	t	t
CAIXA GALICIA GARANTIA	ES0115137038	EUR	2	|BMF|0128|	f	78838	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115137038||es||False	f	t	t
CAIXA GALICIA GARANTIA 2	ES0157082035	EUR	2	|BMF|0128|	f	78840	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157082035||es||False	f	t	t
CAIXA GALICIA GARANTIA 3	ES0117183030	EUR	2	|BMF|0128|	f	78842	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117183030||es||False	f	t	t
CAIXA GALICIA GARANTIA CINCO	ES0115008031	EUR	2	|BMF|0128|	f	78847	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115008031||es||False	f	t	t
CAIXA GALICIA GARANTIA CUATRO	ES0113250031	EUR	2	|BMF|0128|	f	78848	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113250031||es||False	f	t	t
CCM FONDEPOSITO	ES0115942031	EUR	2	|BMF|0128|	f	78849	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115942031||es||False	f	t	t
CCM RENTA FIJA	ES0147611034	EUR	2	|BMF|0128|	f	78850	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147611034||es||False	f	t	t
CS RENTA VARIABLE INTERNACIONAL	ES0142538034	EUR	2	|BMF|0173|	f	78851	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142538034||es||False	f	t	t
DWS CAPITAL I	ES0114086038	EUR	2	|BMF|0142|	f	78852	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114086038||es||False	f	t	t
BANCA CIVICA IMPULSO	ES0165541030	EUR	2	|BMF|0071|	f	78857	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165541030||es||False	f	t	t
BANCA CIVICA INDEX	ES0148213038	EUR	2	|BMF|0071|	f	78872	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0148213038||es||False	f	t	t
BANCA CIVICA MONETARIO	ES0165549009	EUR	2	|BMF|0071|	f	78877	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165549009||es||False	f	t	t
BANIF CARTERA DINAMICA	ES0166333031	EUR	2	|BMF|0012|	f	78878	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0166333031||es||False	f	t	t
BANIF CARTERA EMERGENTES	ES0114081039	EUR	2	|BMF|0012|	f	78879	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114081039||es||False	f	t	t
BANIF CARTERA MODERADA	ES0115242036	EUR	2	|BMF|0012|	f	78884	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115242036||es||False	f	t	t
BANIF CORTO PLAZO B	ES0115237036	EUR	2	|BMF|0012|	f	78887	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115237036||es||False	f	t	t
CAJA INGENIEROS BOLSA USA	ES0115359038	EUR	2	|BMF|0193|	f	78889	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115359038||es||False	f	t	t
CAJA INGENIEROS EMERGENTES	ES0109221038	EUR	2	|BMF|0193|	f	78890	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109221038||es||False	f	t	t
CAJA INGENIEROS GESTION ALTERNAT	ES0142547035	EUR	2	|BMF|0193|	f	78892	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142547035||es||False	f	t	t
CAJA INGENIEROS MULTIFONDO	ES0115444038	EUR	2	|BMF|0193|	f	78893	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115444038||es||False	f	t	t
CAJA INGENIEROS PREMIER	ES0115532030	EUR	2	|BMF|0193|	f	78894	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115532030||es||False	f	t	t
CAJA INGENIEROS RENTA	ES0114986039	EUR	2	|BMF|0193|	f	78895	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114986039||es||False	f	t	t
BANIF ESTRUTURADO BANCA EUROPEA	ES0113603007	EUR	2	|BMF|0012|	f	78904	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113603007||es||False	f	t	t
BANCA CIVICA PREMIUM	ES0115690036	EUR	2	|BMF|0071|	f	78913	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115690036||es||False	f	t	t
CITIFONDO PREMIUM	ES0118912031	EUR	2	|BMF|0012|	f	78914	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0118912031||es||False	f	t	t
BANIF MONETARIO	ES0113749008	EUR	2	|BMF|0012|	f	78916	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113749008||es||False	f	t	t
CAJAGRANADA FONDPLAZO GARANT.III	ES0114544036	EUR	2	|BMF|0128|	f	78921	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114544036||es||False	f	t	t
CAJAMAR FONDEPOSITO	ES0105582003	EUR	2	|BMF|0069|	f	78931	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105582003||es||False	f	t	t
CITIFONDO RENTA VARIABLE	ES0118927039	EUR	2	|BMF|0012|	f	78937	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0118927039||es||False	f	t	t
CAJAMAR MONETARIO	ES0114546031	EUR	2	|BMF|0069|	f	78938	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114546031||es||False	f	t	t
CATALANA OCCIDENTE RENTA FIJA CP	ES0116889033	EUR	2	|BMF|0037|	f	78941	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116889033||es||False	f	t	t
CONSULNOR CONSERVADOR	ES0123546006	EUR	2	|BMF|0160|	f	78943	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0123546006||es||False	f	t	t
CONSULNOR CRECIMIENTO	ES0123549000	EUR	2	|BMF|0160|	f	78944	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0123549000||es||False	f	t	t
ESPIRITO SANTO RENTA DINAMICA	ES0150036038	EUR	2	|BMF|0113|	f	78945	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0150036038||es||False	f	t	t
ESPIRITO SANTO EUROBONOS	ES0158791030	EUR	2	|BMF|0113|	f	78946	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158791030||es||False	f	t	t
CX CAT. FONDIPOSIT	ES0118558008	EUR	2	|BMF|0020|	f	78954	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0118558008||es||False	f	t	t
DAEDALUS CRECIMIENTO	ES0125422008	EUR	2	|BMF|0195|	f	78955	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125422008||es||False	f	t	t
DAEDALUS OPORTUNIDAD	ES0125321002	EUR	2	|BMF|0195|	f	78956	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125321002||es||False	f	t	t
DALMATIAN	ES0125651036	EUR	2	|BMF|0185|	f	78957	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125651036||es||False	f	t	t
BANKPYME BROKERFOND	ES0115201032	EUR	2	|BMF|0024|	f	78959	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115201032||es||False	f	t	t
CREDIT AGRICOLE MERCADINERO	ES0124575038	EUR	2	|BMF|0174|	f	78960	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0124575038||es||False	f	t	t
BANKPYME COMUNICACIONES	ES0113693032	EUR	2	|BMF|0024|	f	78969	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113693032||es||False	f	t	t
BANKPYME EUROPE INVEST	ES0113750006	EUR	2	|BMF|0024|	f	78970	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113750006||es||False	f	t	t
BANKPYME EUROVALOR	ES0170451035	EUR	2	|BMF|0024|	f	78974	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170451035||es||False	f	t	t
CS DURACION FLEXIBLE	ES0126547035	EUR	2	|BMF|0173|	f	78976	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126547035||es||False	f	t	t
CX CAT. EURIBOR + 0,50	ES0164373005	EUR	2	|BMF|0020|	f	78977	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164373005||es||False	f	t	t
DINERKOA	ES0126499039	EUR	2	|BMF|0035|	f	78978	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126499039||es||False	f	t	t
DINERCAM	ES0126551037	EUR	2	|BMF|0126|	f	78980	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126551037||es||False	f	t	t
DINERMADRID FONDTESORO	ES0126525031	EUR	2	|BMF|0085|	f	78984	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126525031||es||False	f	t	t
ESPIRITO SANTO CARTERA ACTIVA, FI	ES0137942001	EUR	2	|BMF|0113|	f	79049	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137942001||es||False	f	t	t
ESAF GESTION FLEXIBLE	ES0138366002	EUR	2	|BMF|0047|	f	79054	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138366002||es||False	f	t	t
ESAF RENTA FIJA LARGO	ES0168662031	EUR	2	|BMF|0047|	f	79059	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168662031||es||False	f	t	t
CAIXA CATALUNYA 1-E	ES0115209035	EUR	2	|BMF|0020|	f	79062	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115209035||es||False	f	t	t
ESAF RENTA VARIABLE	ES0168668038	EUR	2	|BMF|0047|	f	79065	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168668038||es||False	f	t	t
ESPIRITO SANTO VALOR EUROPA, FI	ES0114917034	EUR	2	|BMF|0113|	f	79068	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114917034||es||False	f	t	t
CAIXA CATALUNYA 2-A	ES0119482000	EUR	2	|BMF|0020|	f	79073	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0119482000||es||False	f	t	t
ESPIRITO SANTO FONDTESORO	ES0114911037	EUR	2	|BMF|0113|	f	79074	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114911037||es||False	f	t	t
ESPIRITO SANTO PATRIMONIO, FI	ES0137765030	EUR	2	|BMF|0113|	f	79075	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137765030||es||False	f	t	t
EUROVALOR DEU.PUBLICA EUROPA AAA	ES0133528002	EUR	2	|BMF|0004|	f	79076	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133528002||es||False	f	t	t
EUROVALOR GARANTIZADO ELECCION USA	ES0133557035	EUR	2	|BMF|0004|	f	79092	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133557035||es||False	f	t	t
EUROVALOR GARANTIZADO EMERGENTES, FI	ES0133517005	EUR	2	|BMF|0004|	f	79094	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133517005||es||False	f	t	t
CAIXA CATALUNYA BORSA 14	ES0115107031	EUR	2	|BMF|0020|	f	79098	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115107031||es||False	f	t	t
EUROVALOR GARAN.MAS PROTECCION	ES0133502031	EUR	2	|BMF|0004|	f	79103	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133502031||es||False	f	t	t
EUROVALOR GARAN.RENTA FIJA	ES0133544009	EUR	2	|BMF|0004|	f	79106	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133544009||es||False	f	t	t
EUROVALOR DIVIDENDO EUROPA	ES0127025031	EUR	2	|BMF|0004|	f	79115	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0127025031||es||False	f	t	t
EUROVALOR EMPRESAS VOLUMEN	ES0169533033	EUR	2	|BMF|0004|	f	79116	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169533033||es||False	f	t	t
EUROVALOR ESTADOS UNIDOS	ES0133525032	EUR	2	|BMF|0004|	f	79118	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133525032||es||False	f	t	t
EUROVALOR EUROPA	ES0133555039	EUR	2	|BMF|0004|	f	79119	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133555039||es||False	f	t	t
EUROVALOR GARANT.EXTRASELECCION	ES0133662033	EUR	2	|BMF|0004|	f	79120	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133662033||es||False	f	t	t
EUROVALOR GARANTIZADO CRECIMIENTO	ES0133527038	EUR	2	|BMF|0004|	f	79121	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133527038||es||False	f	t	t
EUROVALOR GARANTIZADO DOLAR	ES0127024034	EUR	2	|BMF|0004|	f	79122	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0127024034||es||False	f	t	t
EUROVALOR GARANTIZADO ORO II	ES0133516007	EUR	2	|BMF|0004|	f	79123	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133516007||es||False	f	t	t
EUROVALOR GLOBAL CONVERTIBLES	ES0133579005	EUR	2	|BMF|0004|	f	79124	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133579005||es||False	f	t	t
CAJAMAR BOLSA	ES0115429039	EUR	2	|BMF|0069|	f	79144	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115429039||es||False	f	t	t
EUROVALOR JAPON	ES0133663031	EUR	2	|BMF|0004|	f	79147	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133663031||es||False	f	t	t
EUROVALOR MIXTO-30	ES0133745036	EUR	2	|BMF|0004|	f	79150	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133745036||es||False	f	t	t
EUROVALOR MIXTO-50	ES0133875031	EUR	2	|BMF|0004|	f	79151	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133875031||es||False	f	t	t
EUROVALOR MIXTO-70	ES0133865032	EUR	2	|BMF|0004|	f	79155	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133865032||es||False	f	t	t
EUROVALOR PARTIC.VOLUMEN FI CLASE A	ES0133877037	EUR	2	|BMF|0004|	f	79156	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133877037||es||False	f	t	t
EUROVALOR RENTABILIDAD GLOBAL	ES0133560039	EUR	2	|BMF|0004|	f	79159	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133560039||es||False	f	t	t
F.GAR.CONFIANZA XI CAJA MURCIA	ES0138082005	EUR	2	|BMF|0128|	f	79160	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138082005||es||False	f	t	t
F.GARAN.CONFIANZA VI CAJA MURCIA	ES0139776035	EUR	2	|BMF|0128|	f	79161	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0139776035||es||False	f	t	t
CAJA BADAJOZ INVERSION	ES0142546037	EUR	2	|BMF|0128|	f	79181	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142546037||es||False	f	t	t
FONCAIXA DINERO 6	ES0138793031	EUR	2	|BMF|0015|	f	79183	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138793031||es||False	f	t	t
FON FINECO BEST	ES0137881035	EUR	2	|BMF|0132|	f	79188	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137881035||es||False	f	t	t
FON FINECO DINERO	ES0107499032	EUR	2	|BMF|0132|	f	79191	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107499032||es||False	f	t	t
FON FINECO EURO LIDER	ES0138584034	EUR	2	|BMF|0132|	f	79193	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138584034||es||False	f	t	t
FON FINECO TOP RENTA FIJA I	ES0137639011	EUR	2	|BMF|0132|	f	79195	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137639011||es||False	f	t	t
FON FINECO VALOR	ES0176236034	EUR	2	|BMF|0132|	f	79196	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0176236034||es||False	f	t	t
FONCAIXA 1 R.F. CORTO DOLAR	ES0138807039	EUR	2	|BMF|0015|	f	79198	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138807039||es||False	f	t	t
FONDESPAÑA INTERNACIONAL III	ES0138539038	EUR	2	|BMF|0130|	f	79207	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138539038||es||False	f	t	t
FONDESPAÑA INTERNACIONAL V	ES0138297033	EUR	2	|BMF|0130|	f	79208	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138297033||es||False	f	t	t
FONDESPAñA GARANTIZ. RENTA FIJA	ES0182038036	EUR	2	|BMF|0130|	f	79212	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182038036||es||False	f	t	t
FONDESPAñA SECTORIAL CRECIMIENTO	ES0138351038	EUR	2	|BMF|0130|	f	79216	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138351038||es||False	f	t	t
FONDESPAÑA VALORES	ES0138492030	EUR	2	|BMF|0130|	f	79220	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138492030||es||False	f	t	t
CX CAT. GARANTIT 3	ES0114933007	EUR	2	|BMF|0020|	f	79229	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114933007||es||False	f	t	t
CAM MIXTO 50	ES0175114034	EUR	2	|BMF|0127|	f	79235	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175114034||es||False	f	t	t
FONCAIXA 113 CARTERA BOLSA EURO	ES0137973030	EUR	2	|BMF|0015|	f	79238	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137973030||es||False	f	t	t
FONDESPAñA EMERGENTES	ES0138443033	EUR	2	|BMF|0130|	f	79245	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138443033||es||False	f	t	t
FONDESPAñA GARANT.RENTA FIJA 2	ES0182039034	EUR	2	|BMF|0130|	f	79249	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182039034||es||False	f	t	t
FONCAIXA 114 CARTERA BOLSA USA	ES0137967032	EUR	2	|BMF|0015|	f	79251	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137967032||es||False	f	t	t
FONCAIXA 117 CARTERA BOLSA ESP.	ES0137974038	EUR	2	|BMF|0015|	f	79252	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137974038||es||False	f	t	t
FONCAIXA 72 BOLSA PAISES EMERGEN	ES0138328036	EUR	2	|BMF|0015|	f	79255	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138328036||es||False	f	t	t
FONCAIXA 86 GARANT.RENTA FIJA	ES0138219037	EUR	2	|BMF|0015|	f	79257	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138219037||es||False	f	t	t
FONCAIXA 92 GARANT. INDICES MUND	ES0138176039	EUR	2	|BMF|0015|	f	79260	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138176039||es||False	f	t	t
FONCAIXA 93 FON.BOLSAS MUNDIALES	ES0138172038	EUR	2	|BMF|0015|	f	79266	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138172038||es||False	f	t	t
FONCAIXA ESTABILIDAD	ES0137655009	EUR	2	|BMF|0015|	f	79267	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137655009||es||False	f	t	t
FONCAIXA ESTABILIDAD PLUS	ES0137641009	EUR	2	|BMF|0015|	f	79272	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137641009||es||False	f	t	t
ESAF DEUDA PUBLICA	ES0168658039	EUR	2	|BMF|0047|	f	79275	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168658039||es||False	f	t	t
ESAF 25	ES0138604030	EUR	2	|BMF|0047|	f	79280	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138604030||es||False	f	t	t
ESAF 50	ES0115047039	EUR	2	|BMF|0047|	f	79281	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115047039||es||False	f	t	t
ESAF ACCIONES EUROPEAS	ES0115048037	EUR	2	|BMF|0047|	f	79282	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115048037||es||False	f	t	t
FONDGESKOA	ES0138869039	EUR	2	|BMF|0035|	f	79293	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138869039||es||False	f	t	t
CAJA LABORAL RENTA	ES0115487037	EUR	2	|BMF|0161|	f	79304	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115487037||es||False	f	t	t
FONCAIXA 137 GAR.CESTA 12 ACCS.	ES0184924035	EUR	2	|BMF|0015|	f	79330	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184924035||es||False	f	t	t
CAJA MADRID RENTA CREC.2009	ES0105579033	EUR	2	|BMF|0085|	f	79337	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105579033||es||False	f	t	t
FONPENEDES MULTIFONS 100	ES0168663039	EUR	2	|BMF|0163|	f	79351	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168663039||es||False	f	t	t
CAJA MADRID EVOLUCION VAR 20	ES0117184038	EUR	2	|BMF|0085|	f	79363	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117184038||es||False	f	t	t
FONPENEDES MULTIFONS FIX	ES0115232037	EUR	2	|BMF|0163|	f	79364	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115232037||es||False	f	t	t
CAJA MADRID HORIZONTE	ES0169080035	EUR	2	|BMF|0085|	f	79366	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169080035||es||False	f	t	t
FINANCIALFOND	ES0169009034	EUR	2	|BMF|0173|	f	79367	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169009034||es||False	f	t	t
CAJA MADRID PYMES	ES0115140032	EUR	2	|BMF|0085|	f	79369	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115140032||es||False	f	t	t
BELGRAVIA EPSILON	ES0114353032	EUR	2	|BMF|0196|	f	79406	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114353032||es||False	f	t	t
BNP PARIBAS BOLSA ESPAñOLA	ES0125471039	EUR	2	|BMF|0061|	f	79408	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125471039||es||False	f	t	t
CAJA MURCIA GARANTIZADO	ES0115486039	EUR	2	|BMF|0128|	f	79410	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115486039||es||False	f	t	t
CAJA MURCIA SELECCION DINAMICA	ES0159180001	EUR	2	|BMF|0128|	f	79412	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159180001||es||False	f	t	t
CAJA SEGOVIA BOLSA GARANTI.2	ES0117185035	EUR	2	|BMF|0128|	f	79413	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117185035||es||False	f	t	t
BNP PARIBAS GLOBAL ASSET ALLOCAT	ES0118531039	EUR	2	|BMF|0061|	f	79420	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0118531039||es||False	f	t	t
FONCAIXA BOLSA SUDESTE ASIATICO	ES0138137031	EUR	2	|BMF|0015|	f	79423	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138137031||es||False	f	t	t
FONCAIXA BOLSA USA	ES0138113032	EUR	2	|BMF|0015|	f	79424	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138113032||es||False	f	t	t
FONDGUISSONA	ES0147607032	EUR	2	|BMF|0029|	f	79426	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147607032||es||False	f	t	t
FONDMAPFRE DINERO	ES0138902038	EUR	2	|BMF|0121|	f	79427	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138902038||es||False	f	t	t
FONDMAPFRE GARANTIZADO 611	ES0138599032	EUR	2	|BMF|0121|	f	79428	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138599032||es||False	f	t	t
FONDMAPFRE INTER. GARANTIZADO	ES0138725033	EUR	2	|BMF|0121|	f	79435	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138725033||es||False	f	t	t
FONDMUSINI III	ES0165198039	EUR	2	|BMF|0121|	f	79436	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165198039||es||False	f	t	t
BNP PARIBAS CASH	ES0150037036	EUR	2	|BMF|0061|	f	79444	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0150037036||es||False	f	t	t
FONDO ANTICIPACION CONSERVADOR 2	ES0137899037	EUR	2	|BMF|0012|	f	79445	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137899037||es||False	f	t	t
FONDO ANTICIPACION MODERADO	ES0138399037	EUR	2	|BMF|0012|	f	79446	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138399037||es||False	f	t	t
BNP PARIBAS GESTION ACTIVA	ES0118532037	EUR	2	|BMF|0061|	f	79449	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0118532037||es||False	f	t	t
FONDO ANTICIPACION MODERADO 2	ES0137941037	EUR	2	|BMF|0012|	f	79451	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137941037||es||False	f	t	t
FONDO ARTAC	ES0138354032	EUR	2	|BMF|0012|	f	79452	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138354032||es||False	f	t	t
CAJABURGOS GARANTIZADO CAP 20	ES0115482038	EUR	2	|BMF|0128|	f	79461	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115482038||es||False	f	t	t
CAJABURGOS GARANTIZADO IBEX	ES0115479034	EUR	2	|BMF|0128|	f	79473	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115479034||es||False	f	t	t
PREV.SANIT.NAC.-PLAN DE AHORRO	ES0170755039	EUR	2	|BMF|0050|	f	79474	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170755039||es||False	f	t	t
PSN PLAN DE INVERSION	ES0167791039	EUR	2	|BMF|0050|	f	79475	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0167791039||es||False	f	t	t
PSN RENTA FIJA	ES0170737037	EUR	2	|BMF|0050|	f	79476	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170737037||es||False	f	t	t
CAJABURGOS SOLUCION	ES0169083005	EUR	2	|BMF|0128|	f	79477	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169083005||es||False	f	t	t
CAJABURGOS SOLUCION 3	ES0158951006	EUR	2	|BMF|0128|	f	79478	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158951006||es||False	f	t	t
CAJACANARIAS AHORRO A PLAZO I	ES0116943038	EUR	2	|BMF|0128|	f	79479	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116943038||es||False	f	t	t
CAJACANARIAS EURIBOR MAS 70 GARN	ES0109224032	EUR	2	|BMF|0128|	f	79481	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109224032||es||False	f	t	t
CAJACANARIAS EUROPA GARANTIZADO	ES0114602032	EUR	2	|BMF|0128|	f	79482	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114602032||es||False	f	t	t
FONCAIXA FONSTRESOR CATALUNYA 59	ES0122057039	EUR	2	|BMF|0015|	f	79483	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122057039||es||False	f	t	t
FONCAIXA GAR.EUROPA PROT. VI	ES0137706034	EUR	2	|BMF|0015|	f	79485	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137706034||es||False	f	t	t
FONDUERO INDICE	ES0147577037	EUR	2	|BMF|0162|	f	79496	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147577037||es||False	f	t	t
FONDESPAÑA AUDAZ	ES0138173036	EUR	2	|BMF|0130|	f	79511	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138173036||es||False	f	t	t
FONCAIXA 125 R.F.HIGH YIELD	ES0184922039	EUR	2	|BMF|0015|	f	79522	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184922039||es||False	f	t	t
FONCAIXA 126 RENTA FIJA EMERGENT	ES0137916039	EUR	2	|BMF|0015|	f	79523	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137916039||es||False	f	t	t
FONCAIXA 127 RENTA FIJA DOS AÑOS	ES0137979037	EUR	2	|BMF|0015|	f	79524	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137979037||es||False	f	t	t
FONCAIXA 129 DIVID.BOLSA EUROPA	ES0184923037	EUR	2	|BMF|0015|	f	79525	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184923037||es||False	f	t	t
FONCAIXA 134 GESTION DINAMICA V3	ES0138066032	EUR	2	|BMF|0015|	f	79528	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138066032||es||False	f	t	t
FONCAIXA GAR.EUROPA PROTECCION 7	ES0145455004	EUR	2	|BMF|0015|	f	79529	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0145455004||es||False	f	t	t
FONCAIXA GAR.EUROPA PROTECCION 8	ES0137686004	EUR	2	|BMF|0015|	f	79530	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137686004||es||False	f	t	t
FONDO JALON	ES0138223039	EUR	2	|BMF|0012|	f	79531	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138223039||es||False	f	t	t
FONDO RENTA FIJA CORPORATIVA	ES0140831035	EUR	2	|BMF|0012|	f	79535	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0140831035||es||False	f	t	t
FONDUERO CAPITAL GARANTIZADO 2	ES0138679032	EUR	2	|BMF|0162|	f	79536	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138679032||es||False	f	t	t
FONDUERO CAPITAL GARANTIZADO 4	ES0138563038	EUR	2	|BMF|0162|	f	79537	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138563038||es||False	f	t	t
FONDUERO CAPITAL GARANTIZADO 6	ES0138565033	EUR	2	|BMF|0162|	f	79538	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138565033||es||False	f	t	t
FONCAIXA 94 FONDOS BOLSA EURO	ES0138181039	EUR	2	|BMF|0015|	f	79541	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138181039||es||False	f	t	t
FONCAIXA 95 TESOR.EURO	ES0138086030	EUR	2	|BMF|0015|	f	79547	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138086030||es||False	f	t	t
FONCAIXA 96 FONDOS BOLSA USA	ES0138189032	EUR	2	|BMF|0015|	f	79559	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138189032||es||False	f	t	t
FONCAIXA ALBUS	ES0107678007	EUR	2	|BMF|0015|	f	79560	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107678007||es||False	f	t	t
FONCAIXA ASEGURADO	ES0137640001	EUR	2	|BMF|0015|	f	79561	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137640001||es||False	f	t	t
FONCAIXA BIENVENIDA	ES0137653004	EUR	2	|BMF|0015|	f	79562	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137653004||es||False	f	t	t
FONCAIXA BOLSA ESPANA 150	ES0137878031	EUR	2	|BMF|0015|	f	79563	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137878031||es||False	f	t	t
FONDMAPFRE BOLSA AMERICA	ES0138658036	EUR	2	|BMF|0121|	f	79564	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138658036||es||False	f	t	t
FONDMAPFRE BOLSA ASIA	ES0138298031	EUR	2	|BMF|0121|	f	79565	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138298031||es||False	f	t	t
FONDO RENTA FIJA CORPORATIVA 2	ES0140823032	EUR	2	|BMF|0012|	f	79566	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0140823032||es||False	f	t	t
FONDO SANTADER GARANTIZADO ESPAÑA	ES0180960033	EUR	2	|BMF|0012|	f	79567	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180960033||es||False	f	t	t
FONDO SOLIDARIO PRO-UNICEF	ES0138518032	EUR	2	|BMF|0085|	f	79568	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138518032||es||False	f	t	t
FONDO SUPERSELECCION	ES0107774038	EUR	2	|BMF|0012|	f	79569	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107774038||es||False	f	t	t
FONDO SUPERSELECCION ACCIONES	ES0138362035	EUR	2	|BMF|0012|	f	79570	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138362035||es||False	f	t	t
FONDO SUPERSELECCION ACCIONES 2	ES0112738036	EUR	2	|BMF|0012|	f	79571	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112738036||es||False	f	t	t
FONCAIXA GARAN.RENTA FIJA PLUS 7	ES0137785004	EUR	2	|BMF|0015|	f	79577	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137785004||es||False	f	t	t
FONCAIXA GARANT.GESTIONADO 119	ES0137804037	EUR	2	|BMF|0015|	f	79583	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137804037||es||False	f	t	t
CAJAGRANADA RENTAS GARANTIZADO	ES0114543038	EUR	2	|BMF|0128|	f	79601	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114543038||es||False	f	t	t
CAJARIOJA AHORRO GARANTIZADO 2	ES0169086008	EUR	2	|BMF|0128|	f	79604	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169086008||es||False	f	t	t
CAJASOL AHORRO 11-2011	ES0140943038	EUR	2	|BMF|0128|	f	79607	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0140943038||es||False	f	t	t
FONCAIXA GAR.EUROPA PROTECCION V	ES0137727030	EUR	2	|BMF|0015|	f	79608	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137727030||es||False	f	t	t
FONCAIXA GAR.OPORT.EMERGENTE II	ES0137701001	EUR	2	|BMF|0015|	f	79609	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137701001||es||False	f	t	t
FONCAIXA GAR.OPORTUNIDAD EMERGEN	ES0137783009	EUR	2	|BMF|0015|	f	79610	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137783009||es||False	f	t	t
FONCAIXA GARANTIA EMERGENTES	ES0138069036	EUR	2	|BMF|0015|	f	79611	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138069036||es||False	f	t	t
FONCAIXA GARANTIA EMPRENDEDORES	ES0137685030	EUR	2	|BMF|0015|	f	79612	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137685030||es||False	f	t	t
FONCAIXA GARANTIA EURO DOLAR	ES0137784007	EUR	2	|BMF|0015|	f	79613	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137784007||es||False	f	t	t
FONCAIXA GARANTIA IBEX PROTECCIO	ES0106192034	EUR	2	|BMF|0015|	f	79614	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0106192034||es||False	f	t	t
FONDO VALENCIA ENERGIAS RENOVABL	ES0180961007	EUR	2	|BMF|0083|	f	79615	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180961007||es||False	f	t	t
CAJASTUR INDICES II	ES0114604038	EUR	2	|BMF|0176|	f	79618	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114604038||es||False	f	t	t
CAJASOL BOLSA I	ES0177860030	EUR	2	|BMF|0128|	f	79645	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0177860030||es||False	f	t	t
CAJASTUR MULTICESTA OPTIMA	ES0110961036	EUR	2	|BMF|0176|	f	79646	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110961036||es||False	f	t	t
CAJASOL FONDEPOSITO	ES0128452036	EUR	2	|BMF|0128|	f	79648	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0128452036||es||False	f	t	t
CAJASOL IBEX CLIQUET III	ES0128468032	EUR	2	|BMF|0128|	f	79649	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0128468032||es||False	f	t	t
CAJASTUR BOLSA MUNDIAL	ES0110951037	EUR	2	|BMF|0176|	f	79650	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110951037||es||False	f	t	t
CAJASTUR CARTERA AGRESIVA	ES0109227035	EUR	2	|BMF|0176|	f	79651	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109227035||es||False	f	t	t
CAJASTUR CARTERA MODERADA	ES0115431035	EUR	2	|BMF|0176|	f	79652	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115431035||es||False	f	t	t
CAJASTUR DOBLE OPTIMO	ES0114819032	EUR	2	|BMF|0176|	f	79653	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114819032||es||False	f	t	t
FONCAIXA MONETARIO EURO DEUDA II	ES0105167037	EUR	2	|BMF|0015|	f	79654	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105167037||es||False	f	t	t
CAJASTUR ESTRATEGIAS GARANTIZADO	ES0115432009	EUR	2	|BMF|0176|	f	79655	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115432009||es||False	f	t	t
FONCAIXA GARANTIA R.F. PLUS 2	ES0137689008	EUR	2	|BMF|0015|	f	79656	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137689008||es||False	f	t	t
FONCAIXA GARANTIA R.F. PLUS 3	ES0137698009	EUR	2	|BMF|0015|	f	79657	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137698009||es||False	f	t	t
FONCAIXA GARANTIA RENTA FIJA 11	ES0137677003	EUR	2	|BMF|0015|	f	79658	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137677003||es||False	f	t	t
FONCAIXA GARANTIA RENTA FIJA 15	ES0137787000	EUR	2	|BMF|0015|	f	79659	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137787000||es||False	f	t	t
FONCAIXA GRANDES EMPRESAS	ES0145457000	EUR	2	|BMF|0015|	f	79660	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0145457000||es||False	f	t	t
FONCAIXA OBJETIVO JUNIO 2012	ES0137681005	EUR	2	|BMF|0015|	f	79662	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137681005||es||False	f	t	t
CAJASTUR RENTA FIJA	ES0111026037	EUR	2	|BMF|0176|	f	79665	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111026037||es||False	f	t	t
CAJASTUR RENTA FIJA II, FI	ES0115380000	EUR	2	|BMF|0176|	f	79666	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115380000||es||False	f	t	t
CAJASTUR VALOR GARANTIZADO	ES0164737035	EUR	2	|BMF|0176|	f	79672	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164737035||es||False	f	t	t
FONCAIXA PRIVADA AHORRO	ES0105181038	EUR	2	|BMF|0015|	f	79677	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105181038||es||False	f	t	t
CAJASUR BOLSA EURO	ES0115512032	EUR	2	|BMF|0128|	f	79679	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115512032||es||False	f	t	t
CAJASUR SELECION MUNDIAL GARANTIZADO FI	ES0115381008	EUR	2	|BMF|0176|	f	79680	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115381008||es||False	f	t	t
FONCAIXA OPORTUNIDAD CLASE ESTANDAR	ES0164948004	EUR	2	|BMF|0015|	f	79683	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164948004||es||False	f	t	t
FONCAIXA OPORTUNIDAD CLASE PLUS	ES0164948038	EUR	2	|BMF|0015|	f	79687	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164948038||es||False	f	t	t
FONDO VALENCIA INTERES I	ES0139003034	EUR	2	|BMF|0083|	f	79691	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0139003034||es||False	f	t	t
FONDO VALENCIA INTERES II	ES0177862036	EUR	2	|BMF|0083|	f	79695	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0177862036||es||False	f	t	t
CAM BOLSA INDICE	ES0139013033	EUR	2	|BMF|0127|	f	79714	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0139013033||es||False	f	t	t
CAM DINERO PLUS	ES0170273033	EUR	2	|BMF|0127|	f	79715	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170273033||es||False	f	t	t
SECURITY FUND	ES0138822038	EUR	2	|BMF|0061|	f	79718	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138822038||es||False	f	t	t
FONALAVA	ES0138591039	EUR	2	|BMF|0007|	f	79719	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138591039||es||False	f	t	t
FONCAIXA PRIVADA OPTIMO	ES0164524037	EUR	2	|BMF|0015|	f	79723	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164524037||es||False	f	t	t
FONALCALA	ES0138932035	EUR	2	|BMF|0137|	f	79731	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138932035||es||False	f	t	t
FONCAIXA PRIVADA RENTA INTERNACI	ES0173407034	EUR	2	|BMF|0015|	f	79732	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173407034||es||False	f	t	t
FONCAIXA PRIVADA BOLSA	ES0105182036	EUR	2	|BMF|0015|	f	79733	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105182036||es||False	f	t	t
FONCAIXA PRIVADA IDEAS	ES0164492003	EUR	2	|BMF|0015|	f	79735	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164492003||es||False	f	t	t
FONCAIXA PRIVADA MULTIG.ACT.EQUI	ES0164540033	EUR	2	|BMF|0015|	f	79739	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164540033||es||False	f	t	t
FONCAIXA PRIVADA MULTIG.ACT.ESTA	ES0164539035	EUR	2	|BMF|0015|	f	79740	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164539035||es||False	f	t	t
FONCAIXA PRIVADA MULTIG.ACT.OPOR	ES0164583033	EUR	2	|BMF|0015|	f	79741	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164583033||es||False	f	t	t
FONCAIXA R.F. CORTO COLAR	ES0137993038	EUR	2	|BMF|0015|	f	79742	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137993038||es||False	f	t	t
FONCAIXA RENTA FIJA LARGO DOLAR	ES0138089034	EUR	2	|BMF|0015|	f	79744	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138089034||es||False	f	t	t
FONCAIXA TESORERIA EURO	ES0138045036	EUR	2	|BMF|0015|	f	79745	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138045036||es||False	f	t	t
MARCH CARTERA ACTIVA	ES0160811008	EUR	2	|BMF|0190|	f	79748	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160811008||es||False	f	t	t
CAM GLOBAL	ES0115582035	EUR	2	|BMF|0127|	f	79752	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115582035||es||False	f	t	t
CAM MIXTO 25	ES0115070031	EUR	2	|BMF|0127|	f	79754	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115070031||es||False	f	t	t
CAMINOS BOLSA EURO	ES0138168036	EUR	2	|BMF|0126|	f	79757	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138168036||es||False	f	t	t
FONBILBAO ACCIONES	ES0126906033	EUR	2	|BMF|0045|	f	79759	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126906033||es||False	f	t	t
CAM FONDEMPRESAS	ES0105143038	EUR	2	|BMF|0127|	f	79768	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105143038||es||False	f	t	t
CAM FONDO EMPRESA PLUS	ES0115448039	EUR	2	|BMF|0127|	f	79769	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115448039||es||False	f	t	t
CAM FONMEDIC	ES0138910031	EUR	2	|BMF|0127|	f	79772	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138910031||es||False	f	t	t
CAM FUTURO 10 GARANTIZADO	ES0140848039	EUR	2	|BMF|0127|	f	79773	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0140848039||es||False	f	t	t
FONCAM	ES0138712031	EUR	2	|BMF|0126|	f	79775	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138712031||es||False	f	t	t
FONCAIXA TESORERIA EURO PLUS	ES0137897031	EUR	2	|BMF|0015|	f	79776	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137897031||es||False	f	t	t
FONCANARIAS INTERNACIONAL	ES0138204039	EUR	2	|BMF|0012|	f	79781	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138204039||es||False	f	t	t
FONCESS FLEXIBLE	ES0164949002	EUR	2	|BMF|0105|	f	79783	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164949002||es||False	f	t	t
FONCESS PATRIMONIO	ES0164493001	EUR	2	|BMF|0105|	f	79786	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164493001||es||False	f	t	t
FONCUENTA	ES0138799038	EUR	2	|BMF|0029|	f	79787	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138799038||es||False	f	t	t
FONDACOFAR	ES0138944030	EUR	2	|BMF|0085|	f	79790	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138944030||es||False	f	t	t
CAMINOS BOLSA OPORTUNIDADES	ES0138253036	EUR	2	|BMF|0126|	f	79791	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138253036||es||False	f	t	t
PRISMAFONDO	ES0117011033	EUR	2	|BMF|0061|	f	79799	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117011033||es||False	f	t	t
FONCAIXA 46 TESORERIA EURO	ES0138664034	EUR	2	|BMF|0015|	f	79800	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138664034||es||False	f	t	t
CAN EURIBOR GARANTIA	ES0115730030	EUR	2	|BMF|0128|	f	79804	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115730030||es||False	f	t	t
CAN EURIBOR GARANTIA II	ES0165548035	EUR	2	|BMF|0128|	f	79805	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165548035||es||False	f	t	t
CANTABRIA ACCIONES	ES0115869036	EUR	2	|BMF|0062|	f	79817	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115869036||es||False	f	t	t
CANTABRIA BOLSA EURO	ES0115904031	EUR	2	|BMF|0062|	f	79818	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115904031||es||False	f	t	t
CANTABRIA GESTION DINAMICA	ES0115872030	EUR	2	|BMF|0062|	f	79819	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115872030||es||False	f	t	t
FONCAIXA 5 BOLSA EURO	ES0138792033	EUR	2	|BMF|0015|	f	79820	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138792033||es||False	f	t	t
FONCAIXA 53 BOLSA USA	ES0138615036	EUR	2	|BMF|0015|	f	79821	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138615036||es||False	f	t	t
FONDO CONFIANZA GARANTIZADO	ES0138299039	EUR	2	|BMF|0128|	f	79822	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138299039||es||False	f	t	t
FONDO DEPOSITOS PLUS	ES0118939034	EUR	2	|BMF|0012|	f	79823	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0118939034||es||False	f	t	t
FONDO EXTREMADURA GARANTIZADO I	ES0138357035	EUR	2	|BMF|0128|	f	79824	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138357035||es||False	f	t	t
FONDO EXTREMADURA GARANTIZADO II	ES0138301033	EUR	2	|BMF|0128|	f	79825	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138301033||es||False	f	t	t
FONDO EXTREMADURA GARANTIZADO VI	ES0139775037	EUR	2	|BMF|0128|	f	79826	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0139775037||es||False	f	t	t
FONGENERAL RENTA FIJA	ES0158317034	EUR	2	|BMF|0128|	f	79827	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158317034||es||False	f	t	t
FONGRUM	ES0138876034	EUR	2	|BMF|0105|	f	79828	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138876034||es||False	f	t	t
FONLAIETANA	ES0138908035	EUR	2	|BMF|0051|	f	79829	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138908035||es||False	f	t	t
CARTERA GESTION AUDAZ	ES0133664039	EUR	2	|BMF|0004|	f	79840	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133664039||es||False	f	t	t
CARTERA GESTION DEFENSIVA	ES0133578031	EUR	2	|BMF|0004|	f	79841	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133578031||es||False	f	t	t
CARTERA GESTION EQUILIBRADA	ES0133620031	EUR	2	|BMF|0004|	f	79858	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133620031||es||False	f	t	t
CARTERA GESTION MODERADA	ES0133878035	EUR	2	|BMF|0004|	f	79860	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133878035||es||False	f	t	t
CARTERA SELECCION FLEXIBLE	ES0133613036	EUR	2	|BMF|0004|	f	79863	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133613036||es||False	f	t	t
CANTABRIA RENTA 20	ES0115868038	EUR	2	|BMF|0062|	f	79866	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115868038||es||False	f	t	t
CANTABRIA RENTA FIJA EURO	ES0147161030	EUR	2	|BMF|0062|	f	79867	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147161030||es||False	f	t	t
CANTABRIA RF CORTO PLAZO	ES0182833030	EUR	2	|BMF|0062|	f	79868	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182833030||es||False	f	t	t
CAPITRADE SYSTEMATIC GLOBAL FUTURES	ES0115957005	EUR	2	|BMF|0203|	f	79869	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115957005||es||False	f	t	t
CARTERA UNIVERSAL	ES0112733037	EUR	2	|BMF|0113|	f	79870	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112733037||es||False	f	t	t
CARTERA VARIABLE	ES0116565039	EUR	2	|BMF|0126|	f	79871	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116565039||es||False	f	t	t
CATALUNYA FONS	ES0116945033	EUR	2	|BMF|0029|	f	79872	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116945033||es||False	f	t	t
FONDITEL VELOCIRAPTOR	ES0138145034	EUR	2	|BMF|0200|	f	79873	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138145034||es||False	f	t	t
CCM TRIPLE 10	ES0115835003	EUR	2	|BMF|0128|	f	79877	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115835003||es||False	f	t	t
CLASS CAJA MADRID 30 EURO	ES0113727004	EUR	2	|BMF|0085|	f	79878	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113727004||es||False	f	t	t
CLASS CAJA MADRID BONOS	ES0118914003	EUR	2	|BMF|0085|	f	79880	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0118914003||es||False	f	t	t
CLASS CAJA MADRID PLATINIUM	ES0118841008	EUR	2	|BMF|0085|	f	79881	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0118841008||es||False	f	t	t
CMB CARTERA EURO	ES0119172007	EUR	2	|BMF|0085|	f	79903	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0119172007||es||False	f	t	t
COMPOSITUM GESTION	ES0121082038	EUR	2	|BMF|0029|	f	79904	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0121082038||es||False	f	t	t
CONSULNOR RENTA VARIABLE	ES0123562003	EUR	2	|BMF|0160|	f	79905	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0123562003||es||False	f	t	t
CONSULNOR TESORERIA	ES0123615033	EUR	2	|BMF|0160|	f	79906	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0123615033||es||False	f	t	t
CREACION DE CULTURA EN ESPAÑOL	ES0124512031	EUR	2	|BMF|0198|	f	79907	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0124512031||es||False	f	t	t
FONCAIXA GARANTIA RENTA FIJA 24	ES0137776003	EUR	2	|BMF|0015|	f	79908	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137776003||es||False	f	t	t
FONCAIXA GESTION ESTRELLA E2	ES0137981033	EUR	2	|BMF|0015|	f	79909	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137981033||es||False	f	t	t
FONDO GARAN.CONFIANZA V C.MURCIA	ES0138307030	EUR	2	|BMF|0128|	f	79910	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138307030||es||False	f	t	t
FONDO GARANT.CONFIANZA III C.MUR	ES0138305034	EUR	2	|BMF|0128|	f	79911	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138305034||es||False	f	t	t
FONDO GARANT.CONFIANZA IX C.MURC	ES0138148038	EUR	2	|BMF|0128|	f	79912	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138148038||es||False	f	t	t
GAESCO EMERGENTFOND	ES0140628035	EUR	2	|BMF|0029|	f	79914	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0140628035||es||False	f	t	t
GESCOOPERATIVO DEU.SOBERANA EURO	ES0174344038	EUR	2	|BMF|0140|	f	79915	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174344038||es||False	f	t	t
SEGURFONDO INVERSION	ES0175444035	EUR	2	|BMF|0098|	f	79916	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175444035||es||False	f	t	t
FONCAIXA PRIVADA GRA.CIAS 2010 G	ES0109648032	EUR	2	|BMF|0015|	f	79917	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109648032||es||False	f	t	t
CREDIT AGRICOLE MERCAPATRIMONI	ES0162230033	EUR	2	|BMF|0174|	f	79924	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162230033||es||False	f	t	t
FONDO SENIORS	ES0138623030	EUR	2	|BMF|0126|	f	79926	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138623030||es||False	f	t	t
CREDIT AGRICOLE MERCASELECCION	ES0162231031	EUR	2	|BMF|0174|	f	79930	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162231031||es||False	f	t	t
FONCAIXA PRIVADA EURO DEUDA	ES0105003034	EUR	2	|BMF|0015|	f	79935	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105003034||es||False	f	t	t
CREDIT AGRICOLE MERCASELECCION PLUS	ES0115254031	EUR	2	|BMF|0174|	f	79938	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115254031||es||False	f	t	t
CREDIT SUISSE BOLSA	ES0113286035	EUR	2	|BMF|0173|	f	79942	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113286035||es||False	f	t	t
FONCAIXA PRIVADA EURO SELECCION	ES0106193032	EUR	2	|BMF|0015|	f	79946	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0106193032||es||False	f	t	t
FONCAIXA PRIVADA FONDO	ES0105002036	EUR	2	|BMF|0015|	f	79949	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105002036||es||False	f	t	t
FONDESPAÑA ACT.MONETARIOS FONDTE	ES0138054038	EUR	2	|BMF|0130|	f	79950	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138054038||es||False	f	t	t
FONCAIXA PRIVADA FONDO ACT.ETICO	ES0138516036	EUR	2	|BMF|0015|	f	79951	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138516036||es||False	f	t	t
FONCAIXA PRIVADA FONT.LAR.PLAZO	ES0105185039	EUR	2	|BMF|0015|	f	79952	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105185039||es||False	f	t	t
GESCOOPERATIVO FONDEPOSITO PLUS	ES0142044009	EUR	2	|BMF|0140|	f	79953	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142044009||es||False	f	t	t
FONDESPAÑA ACUMULATIVO	ES0138656030	EUR	2	|BMF|0130|	f	79955	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138656030||es||False	f	t	t
FONDESPAÑA BOLSA	ES0138587037	EUR	2	|BMF|0130|	f	79957	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138587037||es||False	f	t	t
GESCOOPERATIVO SMALL CAPS, FI	ES0141986002	EUR	2	|BMF|0140|	f	79958	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0141986002||es||False	f	t	t
IBERCAJA CONSERVADOR 1	ES0146792009	EUR	2	|BMF|0084|	f	79959	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146792009||es||False	f	t	t
CREDIT SUISSE GOVER.EURO LIQUIDI	ES0124573033	EUR	2	|BMF|0173|	f	79965	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0124573033||es||False	f	t	t
CREDIT SUISSE EQUITY YIELD	ES0113288031	EUR	2	|BMF|0173|	f	79973	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113288031||es||False	f	t	t
CREDIT SUISSE INFRAESTRUCTURAS	ES0175449034	EUR	2	|BMF|0173|	f	79974	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175449034||es||False	f	t	t
CREDIT SUISSE MONETARIO	ES0155598032	EUR	2	|BMF|0173|	f	79977	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155598032||es||False	f	t	t
CREDIT SUISSE RENTA FIJA 0-5	ES0124880032	EUR	2	|BMF|0173|	f	79978	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0124880032||es||False	f	t	t
CRV FONDBOLSA	ES0125162034	EUR	2	|BMF|0156|	f	79979	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125162034||es||False	f	t	t
CRV FONRENTA	ES0125161036	EUR	2	|BMF|0156|	f	79983	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125161036||es||False	f	t	t
CS DIRECTOR BALANCED	ES0125102030	EUR	2	|BMF|0173|	f	79986	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125102030||es||False	f	t	t
CS DIRECTOR GROWTH	ES0143673038	EUR	2	|BMF|0173|	f	79993	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0143673038||es||False	f	t	t
CS DIRECTOR INCOME	ES0125126039	EUR	2	|BMF|0173|	f	79994	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125126039||es||False	f	t	t
IBERCAJA CRECIMIENTO DINAMICO, CLASE B	ES0146843000	EUR	2	|BMF|0084|	f	79999	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146843000||es||False	f	t	t
IBERCAJA CRECIMIENTO DINAMICO	ES0146843034	EUR	2	|BMF|0084|	f	80000	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146843034||es||False	f	t	t
IBERCAJA DIVIDENDO	ES0146824000	EUR	2	|BMF|0084|	f	80002	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146824000||es||False	f	t	t
IBERCAJA DIVIDENDO, CLASE B	ES0146824018	EUR	2	|BMF|0084|	f	80003	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146824018||es||False	f	t	t
IBERCAJA DOLAR	ES0146942034	EUR	2	|BMF|0084|	f	80004	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146942034||es||False	f	t	t
FONDGUISSONA BOLSA	ES0115223036	EUR	2	|BMF|0029|	f	80023	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115223036||es||False	f	t	t
DINERO ACTIVO I	ES0126516030	EUR	2	|BMF|0007|	f	80027	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126516030||es||False	f	t	t
DINERO ACTIVO II	ES0126548033	EUR	2	|BMF|0007|	f	80028	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126548033||es||False	f	t	t
DINERO ACTIVO III	ES0126506031	EUR	2	|BMF|0007|	f	80029	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126506031||es||False	f	t	t
DINERO ACTIVO IV	ES0126494030	EUR	2	|BMF|0007|	f	80030	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126494030||es||False	f	t	t
DINFONDO	ES0126536038	EUR	2	|BMF|0126|	f	80031	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126536038||es||False	f	t	t
DINVALOR GLOBAL	ES0126553033	EUR	2	|BMF|0126|	f	80032	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126553033||es||False	f	t	t
DREAM TEAM FONDO	ES0127073031	EUR	2	|BMF|0162|	f	80033	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0127073031||es||False	f	t	t
DUX INTERNATIONAL STRATEGY	ES0127062000	EUR	2	|BMF|0206|	f	80034	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0127062000||es||False	f	t	t
DUX MIXTO VARIABLE	ES0128067008	EUR	2	|BMF|0206|	f	80036	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0128067008||es||False	f	t	t
DUX RENTA VARIABLE EUROPEA	ES0127107037	EUR	2	|BMF|0206|	f	80037	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0127107037||es||False	f	t	t
FONDIBAS	ES0138936036	EUR	2	|BMF|0113|	f	80038	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138936036||es||False	f	t	t
ESPIRITO SANTO FONDIBAS MIXTO	ES0170270039	EUR	2	|BMF|0113|	f	80039	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170270039||es||False	f	t	t
FONDICAJA	ES0138819034	EUR	2	|BMF|0128|	f	80043	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138819034||es||False	f	t	t
FONDINAMICO	ES0164526008	EUR	2	|BMF|0105|	f	80044	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164526008||es||False	f	t	t
FONDO AGE	ES0138339033	EUR	2	|BMF|0012|	f	80048	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138339033||es||False	f	t	t
IBERCAJA DOLAR, CLASE B	ES0146942000	EUR	2	|BMF|0084|	f	80049	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146942000||es||False	f	t	t
FONDO VALENCIA GAR.ELEC.OPTIMA 4	ES0138401031	EUR	2	|BMF|0083|	f	80054	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138401031||es||False	f	t	t
DUX RENTINVER RENTA FIJA	ES0127097030	EUR	2	|BMF|0206|	f	80061	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0127097030||es||False	f	t	t
DWS ACCIONES	ES0114085030	EUR	2	|BMF|0142|	f	80069	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114085030||es||False	f	t	t
DWS AGRIX GARANTIZADO	ES0138686037	EUR	2	|BMF|0142|	f	80070	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138686037||es||False	f	t	t
DWS DINER	ES0125783037	EUR	2	|BMF|0142|	f	80072	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125783037||es||False	f	t	t
DWS DINERPLUS	ES0125789034	EUR	2	|BMF|0142|	f	80073	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125789034||es||False	f	t	t
DWS CRECIMIENTO	ES0125776031	EUR	2	|BMF|0142|	f	80076	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125776031||es||False	f	t	t
DWS EUROPA BOLSA	ES0114087036	EUR	2	|BMF|0142|	f	80078	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114087036||es||False	f	t	t
DWS FONCREATIVO	ES0138535036	EUR	2	|BMF|0142|	f	80079	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138535036||es||False	f	t	t
DWS FONPROCURADOR	ES0136787035	EUR	2	|BMF|0142|	f	80080	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0136787035||es||False	f	t	t
DWS MIXTA	ES0125785032	EUR	2	|BMF|0142|	f	80081	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125785032||es||False	f	t	t
FONDO VALENCIA FONDO DE FONDOS60	ES0141223034	EUR	2	|BMF|0083|	f	80083	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0141223034||es||False	f	t	t
FONDO VALENCIA GARAN.EL.OPTIMA 8	ES0138626033	EUR	2	|BMF|0083|	f	80084	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138626033||es||False	f	t	t
FONDO VALENCIA GARAN.ELECCION OPTIMA 7	ES0138149036	EUR	2	|BMF|0083|	f	80085	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138149036||es||False	f	t	t
FONDO VALENCIA GARANTIZADO MIX.6	ES0138400033	EUR	2	|BMF|0083|	f	80086	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138400033||es||False	f	t	t
IBERCAJA EMERGENTES	ES0102562032	EUR	2	|BMF|0084|	f	80087	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0102562032||es||False	f	t	t
IBERCAJA FINANCIERO	ES0147104030	EUR	2	|BMF|0084|	f	80088	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147104030||es||False	f	t	t
DWS CANTABRIA CRECIMIENTO GAR.II	ES0115853030	EUR	2	|BMF|0142|	f	80089	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115853030||es||False	f	t	t
ESPIRITO SANTO BOLSA EUROPA SELECCION	ES0158761033	EUR	2	|BMF|0113|	f	80090	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158761033||es||False	f	t	t
ESPIRITO SANTO BOLSA SELECCION	ES0138517034	EUR	2	|BMF|0113|	f	80107	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138517034||es||False	f	t	t
ESPIRITO SANTO BOLSA USA	ES0133338030	EUR	2	|BMF|0113|	f	80108	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133338030||es||False	f	t	t
ESPIRITO SANTO DOBLE INDICE	ES0133092033	EUR	2	|BMF|0113|	f	80109	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133092033||es||False	f	t	t
ESPIRITO SANTO EUROFONDO II	ES0133591034	EUR	2	|BMF|0113|	f	80114	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133591034||es||False	f	t	t
ESPIRITO SANTO FONDEPOSITO II	ES0158792004	EUR	2	|BMF|0113|	f	80115	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158792004||es||False	f	t	t
ESPIRITO SANTO GARANTIA BOLSA	ES0158773038	EUR	2	|BMF|0113|	f	80117	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158773038||es||False	f	t	t
ESPIRITO SANTO GLOBAL SOLIDARIO	ES0131422000	EUR	2	|BMF|0113|	f	80118	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0131422000||es||False	f	t	t
ESPIRITO SANTO PHARMAFUND	ES0169778034	EUR	2	|BMF|0113|	f	80120	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169778034||es||False	f	t	t
ETCHEVERRIA MIXTO	ES0133509036	EUR	2	|BMF|0225|	f	80130	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133509036||es||False	f	t	t
EUROAGENTES BOLSA	ES0133797037	EUR	2	|BMF|0115|	f	80131	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133797037||es||False	f	t	t
EUROAGENTES PLUS	ES0133531030	EUR	2	|BMF|0115|	f	80132	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133531030||es||False	f	t	t
EUROAGENTES PREVISION	ES0133532038	EUR	2	|BMF|0115|	f	80133	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133532038||es||False	f	t	t
EUROAGENTES RENTA	ES0133798035	EUR	2	|BMF|0115|	f	80134	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133798035||es||False	f	t	t
EUROAGENTES UNIVERSAL	ES0133569030	EUR	2	|BMF|0115|	f	80135	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133569030||es||False	f	t	t
EUROVALENCIA	ES0133836033	EUR	2	|BMF|0173|	f	80136	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133836033||es||False	f	t	t
EUROVALOR AHORRO ACTIVO	ES0133462004	EUR	2	|BMF|0004|	f	80137	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133462004||es||False	f	t	t
EUROVALOR AHORRO DOLAR	ES0133501033	EUR	2	|BMF|0004|	f	80138	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133501033||es||False	f	t	t
EUROVALOR AHORRO EURO	ES0133867038	EUR	2	|BMF|0004|	f	80139	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133867038||es||False	f	t	t
FONDMAPFRE MULTISELECCION	ES0138445038	EUR	2	|BMF|0121|	f	80140	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138445038||es||False	f	t	t
FONDMAPFRE RENTA	ES0138903036	EUR	2	|BMF|0121|	f	80141	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138903036||es||False	f	t	t
FONDMAPFRE RENTA LARGO	ES0138820032	EUR	2	|BMF|0121|	f	80151	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138820032||es||False	f	t	t
FONDMAPFRE RENTA MIXTO	ES0138709037	EUR	2	|BMF|0121|	f	80159	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138709037||es||False	f	t	t
FONDMAPFRE RENTADOLAR	ES0137814002	EUR	2	|BMF|0121|	f	80161	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137814002||es||False	f	t	t
FONDMAPFRE TECNOLOGIA	ES0138396033	EUR	2	|BMF|0121|	f	80164	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138396033||es||False	f	t	t
FONDMUSINI II	ES0165197031	EUR	2	|BMF|0121|	f	80165	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165197031||es||False	f	t	t
EUROVALOR GARAN. GLOBAL	ES0133563033	EUR	2	|BMF|0004|	f	80180	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133563033||es||False	f	t	t
EUROVALOR ASIA	ES0133539033	EUR	2	|BMF|0004|	f	80183	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133539033||es||False	f	t	t
EUROVALOR BOLSA	ES0133871030	EUR	2	|BMF|0004|	f	80184	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133871030||es||False	f	t	t
EUROVALOR BOLSA ESPAñOLA	ES0133524035	EUR	2	|BMF|0004|	f	80185	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133524035||es||False	f	t	t
EUROVALOR BOLSA EUROPEA	ES0133661035	EUR	2	|BMF|0004|	f	80186	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133661035||es||False	f	t	t
EUROVALOR BONOS ALTO RENDIMIENTO	ES0133478034	EUR	2	|BMF|0004|	f	80189	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133478034||es||False	f	t	t
EUROVALOR BONOS CORPORATIVOS	ES0133485005	EUR	2	|BMF|0004|	f	80197	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133485005||es||False	f	t	t
EUROVALOR BONOS EURO LARGO PLAZO	ES0133479032	EUR	2	|BMF|0004|	f	80198	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133479032||es||False	f	t	t
EUROVALOR CONSERVACION DINAMICO	ES0133614034	EUR	2	|BMF|0004|	f	80199	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133614034||es||False	f	t	t
EUROVALOR CONSERVADOR DIN.PLUS	ES0133743031	EUR	2	|BMF|0004|	f	80201	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133743031||es||False	f	t	t
FONBILBAO DINERO	ES0138812039	EUR	2	|BMF|0045|	f	80220	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138812039||es||False	f	t	t
FONBILBAO EUROBOLSA	ES0138437035	EUR	2	|BMF|0045|	f	80221	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138437035||es||False	f	t	t
FONBILBAO GLOBAL 50	ES0138321031	EUR	2	|BMF|0045|	f	80222	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138321031||es||False	f	t	t
FONBILBAO INTERNACIONAL	ES0138701034	EUR	2	|BMF|0045|	f	80223	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138701034||es||False	f	t	t
FONBILBAO MIXTO	ES0138478039	EUR	2	|BMF|0045|	f	80224	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138478039||es||False	f	t	t
FONBILBAO RENTA FIJA	ES0138333036	EUR	2	|BMF|0045|	f	80225	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138333036||es||False	f	t	t
FONBUSA FONDOS	ES0138438033	EUR	2	|BMF|0133|	f	80226	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138438033||es||False	f	t	t
FONBUSA	ES0138784030	EUR	2	|BMF|0133|	f	80240	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138784030||es||False	f	t	t
INTERVALOR ACCS. INTERNACIONAL	ES0155715032	EUR	2	|BMF|0152|	f	80241	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155715032||es||False	f	t	t
INTERVALOR BOLSA	ES0155853031	EUR	2	|BMF|0152|	f	80242	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155853031||es||False	f	t	t
INTERVALOR FONDOS	ES0155817036	EUR	2	|BMF|0152|	f	80243	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155817036||es||False	f	t	t
INVERACTIVO CONFIANZA	ES0147131033	EUR	2	|BMF|0012|	f	80244	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147131033||es||False	f	t	t
INVERSABADELL 50 PREMIE	ES0144213032	EUR	2	|BMF|0058|	f	80245	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0144213032||es||False	f	t	t
INVERSABADELL 70	ES0138957032	EUR	2	|BMF|0058|	f	80246	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138957032||es||False	f	t	t
FONDESPAÑA CONSERVADOR	ES0138046034	EUR	2	|BMF|0130|	f	80257	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138046034||es||False	f	t	t
FONDESPAÑA CONSOLIDA 1	ES0182037038	EUR	2	|BMF|0130|	f	80258	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182037038||es||False	f	t	t
FONDESPAÑA CONSOLIDA 2	ES0138386034	EUR	2	|BMF|0130|	f	80259	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138386034||es||False	f	t	t
FONDESPAÑA DINAMICO	ES0138666039	EUR	2	|BMF|0130|	f	80260	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138666039||es||False	f	t	t
FONDESPAÑA DOLAR GARANTIZADO	ES0137813004	EUR	2	|BMF|0130|	f	80262	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137813004||es||False	f	t	t
FONDESPAÑA EMPRENDEDOR	ES0138337037	EUR	2	|BMF|0130|	f	80266	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138337037||es||False	f	t	t
FONDESPAÑA EVOLUCION EUROPA GRAN	ES0137876001	EUR	2	|BMF|0130|	f	80268	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137876001||es||False	f	t	t
FONDESPAÑA CONSOLIDA 3	ES0122066030	EUR	2	|BMF|0130|	f	80269	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122066030||es||False	f	t	t
FONDESPAÑA FONDTESORO	ES0138588035	EUR	2	|BMF|0130|	f	80273	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138588035||es||False	f	t	t
FONBUSA MIXTO	ES0138592037	EUR	2	|BMF|0133|	f	80277	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138592037||es||False	f	t	t
FONDAVILA GARANTIA 3	ES0138713039	EUR	2	|BMF|0128|	f	80278	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138713039||es||False	f	t	t
FONDCIRCULO RENTA FIJA	ES0138961034	EUR	2	|BMF|0128|	f	80280	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138961034||es||False	f	t	t
KUTXAINVER	ES0157030034	EUR	2	|BMF|0086|	f	80281	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157030034||es||False	f	t	t
KUTXAINVER2	ES0157023039	EUR	2	|BMF|0086|	f	80282	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157023039||es||False	f	t	t
MANRESA EUROPA BORSA, FI	ES0133802035	EUR	2	|BMF|0076|	f	80283	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133802035||es||False	f	t	t
MARCH MONETARIO DINAMICO	ES0160921039	EUR	2	|BMF|0190|	f	80284	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160921039||es||False	f	t	t
FONDESPAÑA EMPRENDEDOR PLUS	ES0138657038	EUR	2	|BMF|0130|	f	80289	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138657038||es||False	f	t	t
MARCH MULTIFONDO GARANTIZADO	ES0160932036	EUR	2	|BMF|0190|	f	80290	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160932036||es||False	f	t	t
FONDESPAÑA GARANTIZADO RENT.FIJA	ES0164584007	EUR	2	|BMF|0130|	f	80292	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164584007||es||False	f	t	t
FONDESPAÑA GESTION ACT.GARANT 3	ES0138598034	EUR	2	|BMF|0130|	f	80293	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138598034||es||False	f	t	t
FONDESPAÑA GESTION ACT.GARANT 5	ES0138724036	EUR	2	|BMF|0130|	f	80295	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138724036||es||False	f	t	t
FONDESPAÑA GESTION ACTIVA GAR.2	ES0138039039	EUR	2	|BMF|0130|	f	80297	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138039039||es||False	f	t	t
FONDESPAÑA GESTION ACTIVA GAR.4	ES0137939031	EUR	2	|BMF|0130|	f	80299	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137939031||es||False	f	t	t
FONDESPAÑA GESTION ACTIVA GARANT	ES0138078037	EUR	2	|BMF|0130|	f	80301	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138078037||es||False	f	t	t
FONDESPAÑA GESTION INTERNAC.	ES0138481033	EUR	2	|BMF|0130|	f	80302	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138481033||es||False	f	t	t
FONDESPAÑA GLOBAL	ES0138714037	EUR	2	|BMF|0130|	f	80303	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138714037||es||False	f	t	t
FONDESPAÑA I	ES0138787033	EUR	2	|BMF|0128|	f	80306	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138787033||es||False	f	t	t
MUTUAFONDO GESTION BONOS	ES0131366033	EUR	2	|BMF|0021|	f	80307	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0131366033||es||False	f	t	t
MUTUAFONDO TECNOLOGICO	ES0141222036	EUR	2	|BMF|0021|	f	80308	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0141222036||es||False	f	t	t
MUTUAFONDO VALORES	ES0165241037	EUR	2	|BMF|0021|	f	80309	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165241037||es||False	f	t	t
FONDESPAÑA INTERNACIONAL 8	ES0138055035	EUR	2	|BMF|0130|	f	80314	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138055035||es||False	f	t	t
FONDESPAÑA INTERNACIONAL II	ES0138514031	EUR	2	|BMF|0130|	f	80315	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138514031||es||False	f	t	t
MUTUAL PLUS	ES0108686009	EUR	2	|BMF|0225|	f	80333	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108686009||es||False	f	t	t
MUTUALFASA 2	ES0184892034	EUR	2	|BMF|0063|	f	80334	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184892034||es||False	f	t	t
SANTANDER ACCIONES EURO	ES0114063037	EUR	2	|BMF|0012|	f	80335	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114063037||es||False	f	t	t
SANTANDER ACCIONES LATINOAMERICANAS	ES0105930038	EUR	2	|BMF|0012|	f	80336	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105930038||es||False	f	t	t
SANTANDER AGGRESSIVE EUROPE	ES0113473039	EUR	2	|BMF|0012|	f	80337	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113473039||es||False	f	t	t
FONMIX LAIETANA 4	ES0141227035	EUR	2	|BMF|0051|	f	80346	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0141227035||es||False	f	t	t
FONMIX LAIETANA 5	ES0141228033	EUR	2	|BMF|0051|	f	80349	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0141228033||es||False	f	t	t
FONMIX LAIETANA DOS	ES0138524030	EUR	2	|BMF|0051|	f	80350	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138524030||es||False	f	t	t
FONMIX LAIETANA TRES	ES0138525037	EUR	2	|BMF|0051|	f	80351	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138525037||es||False	f	t	t
FONPE.GARANT.INT.MES BORSA III	ES0115233035	EUR	2	|BMF|0163|	f	80363	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115233035||es||False	f	t	t
FONPENECES ETIC I SOLIDARI	ES0138631009	EUR	2	|BMF|0163|	f	80365	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138631009||es||False	f	t	t
FONPENEDES BORSA	ES0158324030	EUR	2	|BMF|0163|	f	80367	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158324030||es||False	f	t	t
FONPENEDES BORSA EMERGENT	ES0168664037	EUR	2	|BMF|0163|	f	80369	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168664037||es||False	f	t	t
INVERBAN DINERO	ES0155823034	EUR	2	|BMF|0085|	f	80370	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155823034||es||False	f	t	t
INVERBANSER	ES0155844030	EUR	2	|BMF|0012|	f	80371	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155844030||es||False	f	t	t
NMAS1 TESORERIA	ES0169592039	EUR	2	|BMF|0190|	f	80373	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169592039||es||False	f	t	t
NOVAFONDISA	ES0166453037	EUR	2	|BMF|0037|	f	80374	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0166453037||es||False	f	t	t
FONDESPAÑA JAPON	ES0138183035	EUR	2	|BMF|0130|	f	80375	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138183035||es||False	f	t	t
NOVOCAJAS	ES0166472037	EUR	2	|BMF|0007|	f	80376	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0166472037||es||False	f	t	t
INVERKOA	ES0155848031	EUR	2	|BMF|0035|	f	80377	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155848031||es||False	f	t	t
FONDESPAÑA MODERADO	ES0182035032	EUR	2	|BMF|0130|	f	80378	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182035032||es||False	f	t	t
FONDESPAÑA MODERADO PLUS	ES0137994036	EUR	2	|BMF|0130|	f	80380	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137994036||es||False	f	t	t
FONDESPAÑA MONETARIO DINAMICO	ES0138079035	EUR	2	|BMF|0130|	f	80381	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138079035||es||False	f	t	t
FONDESPAÑA PREMIER	ES0164525000	EUR	2	|BMF|0130|	f	80384	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0164525000||es||False	f	t	t
FONDESPAÑA RENTA ACTIVA	ES0138715034	EUR	2	|BMF|0130|	f	80385	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138715034||es||False	f	t	t
INVERSABADELL 70 PREMIER	ES0155043039	EUR	2	|BMF|0058|	f	80392	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155043039||es||False	f	t	t
INVERTRES FONDO 1	ES0156038038	EUR	2	|BMF|0063|	f	80393	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0156038038||es||False	f	t	t
KUTXAGARANTIZADO MARZO 2015	ES0157016033	EUR	2	|BMF|0086|	f	80395	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157016033||es||False	f	t	t
KUTXAINDEX	ES0157026032	EUR	2	|BMF|0086|	f	80398	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157026032||es||False	f	t	t
OPORTUNIDADES GLOBALES	ES0173951031	EUR	2	|BMF|0105|	f	80399	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173951031||es||False	f	t	t
P & G MASTER RENTA FIJA	ES0167816034	EUR	2	|BMF|0029|	f	80401	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0167816034||es||False	f	t	t
P Y G CRECIMIENTO	ES0169764034	EUR	2	|BMF|0029|	f	80404	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169764034||es||False	f	t	t
FONDESPAÑA SEMESTRAL GARANT.	ES0138716032	EUR	2	|BMF|0130|	f	80414	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138716032||es||False	f	t	t
FONDESPAÑA TESORERIA	ES0138723038	EUR	2	|BMF|0130|	f	80415	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138723038||es||False	f	t	t
FONPENEDES BORSA USA	ES0138499035	EUR	2	|BMF|0163|	f	80417	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138499035||es||False	f	t	t
FONDMAPFRE BOLSA G IV	ES0138394038	EUR	2	|BMF|0121|	f	80436	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138394038||es||False	f	t	t
FONDMAPFRE BOLSA GARANTIZADO II	ES0122067038	EUR	2	|BMF|0121|	f	80437	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122067038||es||False	f	t	t
FONDMAPFRE BOLSA GIX   L	ES0138956034	EUR	2	|BMF|0121|	f	80441	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138956034||es||False	f	t	t
FONDMAPFRE BOLSA GV	ES0138395035	EUR	2	|BMF|0121|	f	80442	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138395035||es||False	f	t	t
FONDMAPFRE BOLSA GVI	ES0138352036	EUR	2	|BMF|0121|	f	80443	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138352036||es||False	f	t	t
FONDMAPFRE BOLSA GVII	ES0138353034	EUR	2	|BMF|0121|	f	80444	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138353034||es||False	f	t	t
FONDMAPFRE BOLSA GVIII	ES0138444031	EUR	2	|BMF|0121|	f	80445	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138444031||es||False	f	t	t
FONDMAPFRE BOLSA GX	ES0138777034	EUR	2	|BMF|0121|	f	80446	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138777034||es||False	f	t	t
FONPENEDES DINAMIC VAR2	ES0141229031	EUR	2	|BMF|0163|	f	80447	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0141229031||es||False	f	t	t
FONPENEDES DINAMIC VAR4	ES0138527033	EUR	2	|BMF|0163|	f	80448	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138527033||es||False	f	t	t
FONPENEDES DIPOSIT	ES0138630001	EUR	2	|BMF|0163|	f	80450	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138630001||es||False	f	t	t
FONPENEDES DOLAR	ES0117014037	EUR	2	|BMF|0163|	f	80451	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117014037||es||False	f	t	t
FONPENEDES EUROBORSA 100	ES0138727039	EUR	2	|BMF|0163|	f	80452	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138727039||es||False	f	t	t
FONPENEDES G. INTERES MES BORSAI	ES0122074034	EUR	2	|BMF|0163|	f	80453	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122074034||es||False	f	t	t
FONPENEDES GAR.INT.MES BORSA II	ES0122075031	EUR	2	|BMF|0163|	f	80456	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122075031||es||False	f	t	t
FONPENEDES GAR.INT.MES BORSA IV	ES0115234033	EUR	2	|BMF|0163|	f	80460	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115234033||es||False	f	t	t
FONPENEDES GAR.INT.MES BORSA V	ES0138501038	EUR	2	|BMF|0163|	f	80462	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138501038||es||False	f	t	t
FONQUIVIR	ES0138912037	EUR	2	|BMF|0125|	f	80463	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138912037||es||False	f	t	t
FONSVILA-REAL	ES0165206006	EUR	2	|BMF|0029|	f	80464	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165206006||es||False	f	t	t
FONTALENTO	ES0139958039	EUR	2	|BMF|0034|	f	80465	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0139958039||es||False	f	t	t
MADRID INDICE IBEX 35	ES0158967036	EUR	2	|BMF|0085|	f	80466	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158967036||es||False	f	t	t
MANRESA BORSA	ES0159529033	EUR	2	|BMF|0076|	f	80467	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159529033||es||False	f	t	t
SABADELL BS GARANTIA FIJA 6	ES0144185032	EUR	2	|BMF|0058|	f	80469	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0144185032||es||False	f	t	t
FONSNOSTRO TRIPLE A	ES0165204035	EUR	2	|BMF|0128|	f	80479	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165204035||es||False	f	t	t
SABADELL BS GARANTIA FIJA 8	ES0175086000	EUR	2	|BMF|0058|	f	80484	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175086000||es||False	f	t	t
MARCH EUROBOLSA GARANTIZADO	ES0160986032	EUR	2	|BMF|0190|	f	80495	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160986032||es||False	f	t	t
MARCH EUROPA BOLSA	ES0160746030	EUR	2	|BMF|0190|	f	80496	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160746030||es||False	f	t	t
MARCH EUROTOP GARANTIZADO	ES0160987030	EUR	2	|BMF|0190|	f	80497	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160987030||es||False	f	t	t
MARCH FUTURO GARANTIZADO	ES0160872000	EUR	2	|BMF|0190|	f	80499	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160872000||es||False	f	t	t
MARCH GESTION ALTERNATIVA	ES0160747004	EUR	2	|BMF|0190|	f	80500	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160747004||es||False	f	t	t
MARCH GLOBAL	ES0160982031	EUR	2	|BMF|0190|	f	80501	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160982031||es||False	f	t	t
SABADELL BS MIX 70	ES0174434037	EUR	2	|BMF|0058|	f	80502	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174434037||es||False	f	t	t
SABADELL BS PROGRESION	ES0111096030	EUR	2	|BMF|0058|	f	80504	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111096030||es||False	f	t	t
SABADELL BS PROGRESION EURO	ES0174376030	EUR	2	|BMF|0058|	f	80505	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174376030||es||False	f	t	t
SABADELL BS PROGRESION INSTITUC.	ES0174419038	EUR	2	|BMF|0058|	f	80506	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174419038||es||False	f	t	t
SABADELL BS R.F. MIXTA ESPAÑA	ES0111145035	EUR	2	|BMF|0058|	f	80507	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111145035||es||False	f	t	t
SABADELL BS R.V. MIXTA ESPAÑA	ES0111124030	EUR	2	|BMF|0058|	f	80509	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111124030||es||False	f	t	t
SABADELL BS RENDIM.INSTITUCIONAL	ES0174418030	EUR	2	|BMF|0058|	f	80510	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174418030||es||False	f	t	t
SABADELL BS RENDIMIENTO	ES0126544032	EUR	2	|BMF|0058|	f	80511	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126544032||es||False	f	t	t
MARCH DIVIDENDO SELECCION	ES0160871036	EUR	2	|BMF|0190|	f	80513	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160871036||es||False	f	t	t
SAFEI EFECTIVO FONDTESORO	ES0138874039	EUR	2	|BMF|0085|	f	80518	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138874039||es||False	f	t	t
SAFEI FONBOLSA	ES0138800034	EUR	2	|BMF|0085|	f	80519	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138800034||es||False	f	t	t
SANTANDER 100 POR 100	ES0114377031	EUR	2	|BMF|0012|	f	80520	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114377031||es||False	f	t	t
SANTANDER 100 X 1002	ES0174961005	EUR	2	|BMF|0012|	f	80521	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174961005||es||False	f	t	t
GAESCO T.F.T.	ES0138984036	EUR	2	|BMF|0029|	f	80522	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138984036||es||False	f	t	t
GAESCOQUANT	ES0140643034	EUR	2	|BMF|0029|	f	80525	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0140643034||es||False	f	t	t
FONTELECO 5	ES0138059037	EUR	2	|BMF|0113|	f	80530	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138059037||es||False	f	t	t
FONTESORERIA	ES0139011037	EUR	2	|BMF|0085|	f	80531	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0139011037||es||False	f	t	t
GAESCO FONDO DE FONDOS	ES0140633035	EUR	2	|BMF|0029|	f	80534	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0140633035||es||False	f	t	t
MARCH PREMIER BOLSA	ES0115540033	EUR	2	|BMF|0190|	f	80541	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115540033||es||False	f	t	t
GAESCO FONDO FONDTESORO	ES0140642036	EUR	2	|BMF|0029|	f	80542	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0140642036||es||False	f	t	t
GAESCO JAPON	ES0141113037	EUR	2	|BMF|0029|	f	80543	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0141113037||es||False	f	t	t
GAESCO MULTINACIONAL	ES0140634033	EUR	2	|BMF|0029|	f	80545	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0140634033||es||False	f	t	t
MARCH IBEX GARANTIZADO	ES0161031036	EUR	2	|BMF|0190|	f	80546	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0161031036||es||False	f	t	t
GAESCO PATRIMONIALISTA	ES0141114001	EUR	2	|BMF|0029|	f	80551	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0141114001||es||False	f	t	t
GAESCO SMALL CAPS	ES0113319034	EUR	2	|BMF|0029|	f	80552	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113319034||es||False	f	t	t
MARCH PREMIER RF	ES0160952034	EUR	2	|BMF|0190|	f	80553	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160952034||es||False	f	t	t
MARCH PREMIER TESORERIA	ES0161032034	EUR	2	|BMF|0190|	f	80559	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0161032034||es||False	f	t	t
SANTANDER 100 X 1006	ES0174941007	EUR	2	|BMF|0012|	f	80560	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174941007||es||False	f	t	t
SANTANDER 104 USA	ES0112734035	EUR	2	|BMF|0012|	f	80561	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112734035||es||False	f	t	t
SANTANDER 104 USA 2	ES0138360039	EUR	2	|BMF|0012|	f	80562	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138360039||es||False	f	t	t
SANTANDER 105 EUROPA	ES0172209035	EUR	2	|BMF|0012|	f	80564	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0172209035||es||False	f	t	t
GESCAFONDO	ES0124506033	EUR	2	|BMF|0113|	f	80568	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0124506033||es||False	f	t	t
GESCONSULT INTERNACIONAL	ES0142097031	EUR	2	|BMF|0057|	f	80569	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142097031||es||False	f	t	t
GESCONSULT TESORERIA	ES0138922036	EUR	2	|BMF|0057|	f	80570	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138922036||es||False	f	t	t
GESCONSULT CRECIMIENTO	ES0138911039	EUR	2	|BMF|0057|	f	80571	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138911039||es||False	f	t	t
GESCONSULT RENTA FIJA FLEXIBLE	ES0138217031	EUR	2	|BMF|0057|	f	80572	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138217031||es||False	f	t	t
GESCONSULT RENTA VARIABLE	ES0137381036	EUR	2	|BMF|0057|	f	80573	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137381036||es||False	f	t	t
GESCONSULT RENTA VARIABLE FLEXI.	ES0175604034	EUR	2	|BMF|0057|	f	80574	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175604034||es||False	f	t	t
GESDIVISA	ES0142437039	EUR	2	|BMF|0113|	f	80601	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142437039||es||False	f	t	t
GESIURIS CAPITAL 1	ES0116845035	EUR	2	|BMF|0037|	f	80602	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116845035||es||False	f	t	t
GESIURIS CAPITAL 2	ES0116829039	EUR	2	|BMF|0037|	f	80605	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116829039||es||False	f	t	t
GESIURIS CAPITAL 3	ES0109695033	EUR	2	|BMF|0037|	f	80606	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109695033||es||False	f	t	t
GESMADRID BOLSA EUROPEA 8	ES0109696007	EUR	2	|BMF|0085|	f	80608	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109696007||es||False	f	t	t
GESRIOJA	ES0142440033	EUR	2	|BMF|0113|	f	80609	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142440033||es||False	f	t	t
GESTIOHNA BOLSA DINAMICA	ES0116830003	EUR	2	|BMF|0194|	f	80610	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116830003||es||False	f	t	t
PATRIBOND	ES0168745034	EUR	2	|BMF|0173|	f	80611	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168745034||es||False	f	t	t
PATRISA	ES0168812032	EUR	2	|BMF|0063|	f	80612	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168812032||es||False	f	t	t
PATRIVAL	ES0142404039	EUR	2	|BMF|0173|	f	80613	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142404039||es||False	f	t	t
PBP BIOGEN	ES0147032033	EUR	2	|BMF|0182|	f	80614	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147032033||es||False	f	t	t
PBP BOLSA ESPAÑA	ES0115063036	EUR	2	|BMF|0182|	f	80615	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115063036||es||False	f	t	t
SANTANDER R.F. EMERGENTES PLUS	ES0121772034	EUR	2	|BMF|0012|	f	80616	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0121772034||es||False	f	t	t
FONSNOSTRO	ES0138859030	EUR	2	|BMF|0128|	f	80719	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138859030||es||False	f	t	t
SANTANDER RENDIMIENTO B	ES0138534005	EUR	2	|BMF|0012|	f	80617	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138534005||es||False	f	t	t
SANTANDER RF CONVERTIBLES	ES0113661039	EUR	2	|BMF|0012|	f	80618	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113661039||es||False	f	t	t
SANTANDER TESORERO B	ES0112744018	EUR	2	|BMF|0012|	f	80620	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112744018||es||False	f	t	t
SANTANDER TESORERO C	ES0112744026	EUR	2	|BMF|0012|	f	80622	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112744026||es||False	f	t	t
FONDMUSINI UNIVERSAL	ES0178520039	EUR	2	|BMF|0121|	f	80633	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0178520039||es||False	f	t	t
PBP SUMMUM	ES0168845032	EUR	2	|BMF|0182|	f	80643	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168845032||es||False	f	t	t
PBP SUMMUM II	ES0168844035	EUR	2	|BMF|0182|	f	80645	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168844035||es||False	f	t	t
PBP TESORERIA	ES0147074035	EUR	2	|BMF|0182|	f	80646	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147074035||es||False	f	t	t
PLUSMADRID	ES0170272035	EUR	2	|BMF|0085|	f	80647	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170272035||es||False	f	t	t
FONDO 111	ES0138927035	EUR	2	|BMF|0130|	f	80648	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138927035||es||False	f	t	t
PLUSMADRID 2	ES0170275038	EUR	2	|BMF|0085|	f	80649	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170275038||es||False	f	t	t
PLUSMADRID GLOBAL	ES0158177032	EUR	2	|BMF|0085|	f	80653	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158177032||es||False	f	t	t
PLUSMADRID INTER.15 ELECCION	ES0170168035	EUR	2	|BMF|0085|	f	80654	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170168035||es||False	f	t	t
PLUSMADRID VALOR	ES0138834033	EUR	2	|BMF|0085|	f	80655	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138834033||es||False	f	t	t
POPULAR PREMIUM DIVERSIFICACION	ES0169535038	EUR	2	|BMF|0004|	f	80656	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169535038||es||False	f	t	t
POPULAR SELECCION	ES0170417002	EUR	2	|BMF|0004|	f	80657	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170417002||es||False	f	t	t
PREMIUM GESTION 2	ES0170642039	EUR	2	|BMF|0159|	f	80659	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170642039||es||False	f	t	t
PREMIUM GESTION 3	ES0170613030	EUR	2	|BMF|0159|	f	80660	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170613030||es||False	f	t	t
PREMIUM GLOBAL 3	ES0170646030	EUR	2	|BMF|0159|	f	80661	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170646030||es||False	f	t	t
GESTIOHNA MODERADO	ES0116846009	EUR	2	|BMF|0194|	f	80668	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116846009||es||False	f	t	t
GLOBAL BEST SELECTION	ES0142233032	EUR	2	|BMF|0113|	f	80669	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142233032||es||False	f	t	t
GOACO MIXTO	ES0142551037	EUR	2	|BMF|0012|	f	80670	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142551037||es||False	f	t	t
PRIVAT PLUSFONDO	ES0158600033	EUR	2	|BMF|0078|	f	80676	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158600033||es||False	f	t	t
PRIVAT RENTA	ES0142167032	EUR	2	|BMF|0078|	f	80679	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142167032||es||False	f	t	t
PROFIT BOLSA	ES0171571039	EUR	2	|BMF|0139|	f	80681	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0171571039||es||False	f	t	t
PROFIT DINERO	ES0171629035	EUR	2	|BMF|0139|	f	80682	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0171629035||es||False	f	t	t
SANTANDER RENDIMIENTO I	ES0138534039	EUR	2	|BMF|0012|	f	80692	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138534039||es||False	f	t	t
SANTANDER RENTA FIJA 2016	ES0175180035	EUR	2	|BMF|0012|	f	80693	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175180035||es||False	f	t	t
GLOBAL ASSETS FUND	ES0142536038	EUR	2	|BMF|0061|	f	80694	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142536038||es||False	f	t	t
FONPENEDES MONETARI	ES0138610037	EUR	2	|BMF|0163|	f	80700	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138610037||es||False	f	t	t
FONPENEDES MULTIFONS 25	ES0168670034	EUR	2	|BMF|0163|	f	80701	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168670034||es||False	f	t	t
FONPENEDES MULTIFONS 50	ES0138606035	EUR	2	|BMF|0163|	f	80702	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138606035||es||False	f	t	t
FONPENEDES MULTIFONS 75	ES0138500030	EUR	2	|BMF|0163|	f	80706	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138500030||es||False	f	t	t
FONPENEDES RENDES	ES0158321036	EUR	2	|BMF|0163|	f	80708	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158321036||es||False	f	t	t
FONPENEDES RF CURT TERMINI	ES0138980034	EUR	2	|BMF|0163|	f	80709	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138980034||es||False	f	t	t
FONPREMIUM RF	ES0158326035	EUR	2	|BMF|0132|	f	80710	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158326035||es||False	f	t	t
FONPROFIT	ES0138929031	EUR	2	|BMF|0139|	f	80711	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138929031||es||False	f	t	t
FONRADAR INTERNACIONAL	ES0139957031	EUR	2	|BMF|0029|	f	80713	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0139957031||es||False	f	t	t
FONSGLOBAL RENTA	ES0136788033	EUR	2	|BMF|0029|	f	80714	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0136788033||es||False	f	t	t
FONSMANLLEU BORSA	ES0139002036	EUR	2	|BMF|0029|	f	80717	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0139002036||es||False	f	t	t
FONSNOSTRO II	ES0139010039	EUR	2	|BMF|0128|	f	80720	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0139010039||es||False	f	t	t
RURAL VALOR IV	ES0174433039	EUR	2	|BMF|0140|	f	80723	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174433039||es||False	f	t	t
RURAL AHORRO PLUS	ES0174305039	EUR	2	|BMF|0140|	f	80726	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174305039||es||False	f	t	t
RURAL GARAN.DOBLE OPCION 2010	ES0174343030	EUR	2	|BMF|0140|	f	80731	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174343030||es||False	f	t	t
GRANDES CUENTAS BANESTO	ES0143068031	EUR	2	|BMF|0012|	f	80738	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0143068031||es||False	f	t	t
HIGH RATE	ES0144886035	EUR	2	|BMF|0131|	f	80741	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0144886035||es||False	f	t	t
IBERCAJA 3	ES0106948039	EUR	2	|BMF|0128|	f	80742	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0106948039||es||False	f	t	t
IBERCAJA AHORRO	ES0147173035	EUR	2	|BMF|0084|	f	80743	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147173035||es||False	f	t	t
IBERCAJA BOLSA GARANTIZADO	ES0146842036	EUR	2	|BMF|0084|	f	80754	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146842036||es||False	f	t	t
RURAL CESTA DEFENSIVA 10	ES0174264038	EUR	2	|BMF|0140|	f	80755	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174264038||es||False	f	t	t
RURAL CESTA MODERADA 60	ES0174304032	EUR	2	|BMF|0140|	f	80756	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174304032||es||False	f	t	t
RURAL GARANT.RENTA FIJA 2012	ES0174266009	EUR	2	|BMF|0140|	f	80762	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174266009||es||False	f	t	t
RURAL GARANT.RENTA VARIABLE IV	ES0174350035	EUR	2	|BMF|0140|	f	80763	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174350035||es||False	f	t	t
RURAL GARANTIA EUROBOLSA	ES0174265001	EUR	2	|BMF|0140|	f	80764	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174265001||es||False	f	t	t
RURAL GARANTIZADO BRIC	ES0174364036	EUR	2	|BMF|0140|	f	80765	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174364036||es||False	f	t	t
IBERCAJA BOLSA INTERNACIONAL	ES0147641031	EUR	2	|BMF|0084|	f	80770	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147641031||es||False	f	t	t
IBERCAJA BOLSA USA	ES0147034039	EUR	2	|BMF|0084|	f	80771	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147034039||es||False	f	t	t
IBERCAJA BOLSA USA, CLASE B	ES0147034005	EUR	2	|BMF|0084|	f	80772	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147034005||es||False	f	t	t
IBERCAJA BOLSA, CLASE B	ES0147186003	EUR	2	|BMF|0084|	f	80773	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147186003||es||False	f	t	t
IBERCAJA BP ACCIONES EUROPA, FI	ES0146757002	EUR	2	|BMF|0084|	f	80774	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146757002||es||False	f	t	t
IBERCAJA BP GLOBAL BONDS, CLASE B	ES0146822012	EUR	2	|BMF|0084|	f	80775	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146822012||es||False	f	t	t
RURAL GARANTIZADO RENTA FIJA II	ES0138553039	EUR	2	|BMF|0140|	f	80776	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138553039||es||False	f	t	t
RURAL EXTRA IBEX GARANTIZADO	ES0174339038	EUR	2	|BMF|0140|	f	80777	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174339038||es||False	f	t	t
RURAL IBEX GARANTIA 2012	ES0175737032	EUR	2	|BMF|0140|	f	80778	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175737032||es||False	f	t	t
RURAL EUROPA GARANTIA 2010	ES0174383036	EUR	2	|BMF|0140|	f	80779	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174383036||es||False	f	t	t
RURAL MIXTO 25	ES0174431033	EUR	2	|BMF|0140|	f	80780	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174431033||es||False	f	t	t
RURAL MIXTO 50	ES0174398034	EUR	2	|BMF|0140|	f	80781	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174398034||es||False	f	t	t
RURAL MIXTO 75	ES0174387037	EUR	2	|BMF|0140|	f	80782	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174387037||es||False	f	t	t
RURAL MIXTO INTERNACIONAL 25	ES0174406035	EUR	2	|BMF|0140|	f	80783	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174406035||es||False	f	t	t
QUALITY CARTERA MODERADA BP	ES0172242002	EUR	2	|f_es_0014|f_es_BMF|	f	80687	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0172242002||es||False	f	t	t
RURAL MULTIFONDO 75	ES0174432031	EUR	2	|BMF|0140|	f	80785	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174432031||es||False	f	t	t
RURAL ORO GARANTIZADO	ES0174399032	EUR	2	|BMF|0140|	f	80786	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174399032||es||False	f	t	t
RURAL RENDIMIENTO	ES0174394033	EUR	2	|BMF|0140|	f	80787	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174394033||es||False	f	t	t
RURAL RENTA FIJA 3	ES0123971030	EUR	2	|BMF|0140|	f	80788	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0123971030||es||False	f	t	t
RURAL RENTA FIJA 3 PLUS	ES0123973036	EUR	2	|BMF|0140|	f	80789	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0123973036||es||False	f	t	t
RURAL RENTA FIJA 5	ES0175735036	EUR	2	|BMF|0140|	f	80790	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175735036||es||False	f	t	t
RURAL RENTA FIJA 5 PLUS	ES0123972038	EUR	2	|BMF|0140|	f	80791	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0123972038||es||False	f	t	t
RURAL RENTA FIJA INTERNACIONAL	ES0174368037	EUR	2	|BMF|0140|	f	80792	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174368037||es||False	f	t	t
SABADELL BS CORTO PLAZO EURO	ES0174403032	EUR	2	|BMF|0058|	f	80795	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174403032||es||False	f	t	t
SABADELL BS DOLAR FIJO	ES0138950037	EUR	2	|BMF|0058|	f	80799	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138950037||es||False	f	t	t
SABADELL BS FINANCIAL CAPITAL	ES0111093003	EUR	2	|BMF|0058|	f	80801	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111093003||es||False	f	t	t
SABADELL BS GAR. EXTRA 10	ES0175169004	EUR	2	|BMF|0058|	f	80805	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175169004||es||False	f	t	t
IBERCAJA BP RENTA FIJA	ES0146791001	EUR	2	|BMF|0084|	f	80807	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146791001||es||False	f	t	t
SABADELL BS BONOS EURO.	ES0173828031	EUR	2	|BMF|0058|	f	80808	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173828031||es||False	f	t	t
SABADELL BS BONOS INTERNACIONAL	ES0144212034	EUR	2	|BMF|0058|	f	80809	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0144212034||es||False	f	t	t
SABADELL BS COMMODITIES	ES0179606001	EUR	2	|BMF|0058|	f	80810	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0179606001||es||False	f	t	t
SABADELL BS GARANTIA 125 ANIVERS	ES0175215039	EUR	2	|BMF|0058|	f	80811	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175215039||es||False	f	t	t
SABADELL BS GARANTIA EXTRA 1	ES0175221037	EUR	2	|BMF|0058|	f	80812	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175221037||es||False	f	t	t
SABADELL BS GARANTIA EXTRA 13, FI	ES0158286031	EUR	2	|BMF|0058|	f	80813	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158286031||es||False	f	t	t
SANTANDER RENTA FIJA B	ES0146133030	EUR	2	|BMF|0012|	f	80814	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146133030||es||False	f	t	t
SABADELL BS FONDTESORO LARGO PL.	ES0173830037	EUR	2	|BMF|0058|	f	80815	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173830037||es||False	f	t	t
SANTANDER RENTA FIJA LARGO PLAZO A	ES0105941001	EUR	2	|BMF|0012|	f	80821	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105941001||es||False	f	t	t
SANTANDER RENTA FIJA PRIVADA	ES0175164039	EUR	2	|BMF|0012|	f	80826	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175164039||es||False	f	t	t
SANTANDER RESPONSAV.CONSERVADOR	ES0145821031	EUR	2	|BMF|0012|	f	80827	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0145821031||es||False	f	t	t
SANTANDER REVALORIZACION ACTIVA	ES0114271036	EUR	2	|BMF|0012|	f	80828	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114271036||es||False	f	t	t
WELZIA SIGMA 20	ES0184677039	EUR	2	|BMF|0207|	f	80829	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184677039||es||False	f	t	t
IBERCAJA BP SELECCION GLOBAL	ES0146758000	EUR	2	|BMF|0084|	f	80836	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146758000||es||False	f	t	t
IBERCAJA CAPITAL EUROPA	ES0102563030	EUR	2	|BMF|0084|	f	80838	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0102563030||es||False	f	t	t
SABADELL BS GARANTIA EXTRA 3	ES0175168030	EUR	2	|BMF|0058|	f	80841	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175168030||es||False	f	t	t
SABADELL BS GARANTIA EXTRA 4	ES0111141034	EUR	2	|BMF|0058|	f	80842	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0111141034||es||False	f	t	t
SABADELL BS GARANTIA EXTRA 5	ES0175082033	EUR	2	|BMF|0058|	f	80843	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175082033||es||False	f	t	t
SABADELL BS GARANTIA EXTRA 7	ES0174232035	EUR	2	|BMF|0058|	f	80848	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174232035||es||False	f	t	t
SABADELL BS GARANTIA EXTRA 8	ES0174377038	EUR	2	|BMF|0058|	f	80849	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174377038||es||False	f	t	t
SABADELL BS GARANTIA FIJA 3	ES0178521037	EUR	2	|BMF|0058|	f	80851	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0178521037||es||False	f	t	t
WM MERCADOS GLOBALES	ES0106097035	EUR	2	|BMF|0182|	f	80857	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0106097035||es||False	f	t	t
IBERCAJA BP RENTA FIJA, CLASE B	ES0146791019	EUR	2	|BMF|0084|	f	80863	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146791019||es||False	f	t	t
FONDO CAJA MURCIA INT.GARANT. II	ES0138091030	EUR	2	|BMF|0128|	f	80882	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138091030||es||False	f	t	t
FONDO VALENCIA RENTA FIJA	ES0139004032	EUR	2	|BMF|0083|	f	80933	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0139004032||es||False	f	t	t
FONDO VALENCIA RENTA FIJA MIXTA	ES0139005039	EUR	2	|BMF|0083|	f	80934	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0139005039||es||False	f	t	t
FONDO VALENCIA RENTA VARIABLE	ES0138578036	EUR	2	|BMF|0083|	f	80935	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138578036||es||False	f	t	t
FONPENEDES GAR.INT.MES BORSA VI	ES0138607033	EUR	2	|BMF|0163|	f	80990	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138607033||es||False	f	t	t
FONPENEDES GAR.INT.MES BORSA X	ES0138609039	EUR	2	|BMF|0163|	f	80991	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138609039||es||False	f	t	t
FONPENEDES GARANTI	ES0136786037	EUR	2	|BMF|0163|	f	80992	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0136786037||es||False	f	t	t
FONPENEDES GARANTIT IX PETROLI	ES0122076039	EUR	2	|BMF|0163|	f	80993	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122076039||es||False	f	t	t
FONPENEDES GARANTIT VII OR	ES0168671032	EUR	2	|BMF|0163|	f	80994	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0168671032||es||False	f	t	t
IBERCAJA AHORRO DINAMICO, CLASE B	ES0184002006	EUR	2	|BMF|0084|	f	81040	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184002006||es||False	f	t	t
IBERCAJA ALPHA	ES0146756004	EUR	2	|BMF|0084|	f	81041	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146756004||es||False	f	t	t
IBERCAJA ALPHA, CLASE B	ES0146756012	EUR	2	|BMF|0084|	f	81042	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0146756012||es||False	f	t	t
IBERCAJA BOLSA EUROPA	ES0130705033	EUR	2	|BMF|0084|	f	81044	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0130705033||es||False	f	t	t
IBERCAJA BOLSA EUROPA, CLASE B	ES0130705009	EUR	2	|BMF|0084|	f	81045	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0130705009||es||False	f	t	t
IBERCAJA SELECCION BOLSA	ES0147077038	EUR	2	|BMF|0084|	f	81047	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147077038||es||False	f	t	t
IBERCAJA SELECCION CAPITAL	ES0147197034	EUR	2	|BMF|0084|	f	81048	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147197034||es||False	f	t	t
IBERCAJA SELECCION RENTA INTERNA	ES0147149035	EUR	2	|BMF|0084|	f	81049	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147149035||es||False	f	t	t
SANTANDER RV ESPAÑA REPARTO A	ES0175174038	EUR	2	|BMF|0012|	f	81050	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175174038||es||False	f	t	t
SANTANDER RV ESPAÑA REPARTO C	ES0175174004	EUR	2	|BMF|0012|	f	81051	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175174004||es||False	f	t	t
SANTANDER SEGURIDAD	ES0145822005	EUR	2	|BMF|0012|	f	81052	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0145822005||es||False	f	t	t
SANTANDER SELEC.RV NORTEAMERICA	ES0121761037	EUR	2	|BMF|0012|	f	81054	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0121761037||es||False	f	t	t
SANTANDER SELECCION ASIA	ES0107764039	EUR	2	|BMF|0012|	f	81055	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107764039||es||False	f	t	t
SANTANDER SELECCION RV JAPON	ES0112757036	EUR	2	|BMF|0012|	f	81056	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112757036||es||False	f	t	t
SANTANDER SMALL CAPS ESPAÑA	ES0175224031	EUR	2	|BMF|0012|	f	81057	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175224031||es||False	f	t	t
SANTANDER SMALL CAPS EUROPA	ES0107987036	EUR	2	|BMF|0012|	f	81061	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107987036||es||False	f	t	t
IK PREMIUM GESTION ACTIVA	ES0147457008	EUR	2	|BMF|0156|	f	81074	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147457008||es||False	f	t	t
IK TRIPLE 5 PLUS GARANTIZADO	ES0125166035	EUR	2	|BMF|0156|	f	81076	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125166035||es||False	f	t	t
IM 93 RENTA	ES0130588033	EUR	2	|BMF|0029|	f	81077	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0130588033||es||False	f	t	t
INDOSUEZ BOLSA	ES0126527037	EUR	2	|BMF|0031|	f	81078	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126527037||es||False	f	t	t
INDOSUEZ FONDTESORO	ES0126531039	EUR	2	|BMF|0031|	f	81079	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126531039||es||False	f	t	t
ING DIRECT FONDO NARANJA CONSERV	ES0152747004	EUR	2	|BMF|0031|	f	81080	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0152747004||es||False	f	t	t
ING DIRECT FONDO NARANJA DINAMIC	ES0152743003	EUR	2	|BMF|0031|	f	81081	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0152743003||es||False	f	t	t
SABADELL BS INMOBILIARIO	ES0174234031	EUR	2	|BMF|0058|	f	81084	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174234031||es||False	f	t	t
IBERCAJA UTILITIES	ES0147189031	EUR	2	|BMF|0084|	f	81094	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147189031||es||False	f	t	t
IK AHORRO	ES0125163032	EUR	2	|BMF|0156|	f	81096	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125163032||es||False	f	t	t
IK FONDO MULTIPLE	ES0125168031	EUR	2	|BMF|0156|	f	81097	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125168031||es||False	f	t	t
IK MULTIPROTECCION 5 GARANTIZADO	ES0125112039	EUR	2	|BMF|0156|	f	81098	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125112039||es||False	f	t	t
IK MULTIVALOR 3 PLUS GARANTIZADO	ES0125164030	EUR	2	|BMF|0156|	f	81099	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125164030||es||False	f	t	t
IK MULTIVALOR 9 GARANTIZADO	ES0149043038	EUR	2	|BMF|0156|	f	81100	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0149043038||es||False	f	t	t
IBERCAJA RENTA FIJA 1 AÑO 4	ES0184005009	EUR	2	|BMF|0084|	f	81116	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184005009||es||False	f	t	t
IBERCAJA RENTA FIJA 1 AÑO 5	ES0184006007	EUR	2	|BMF|0084|	f	81118	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184006007||es||False	f	t	t
IBERCAJA RENTA FIJA 2012	ES0147023008	EUR	2	|BMF|0084|	f	81119	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147023008||es||False	f	t	t
IBERCAJA RENTA FIJA 2013	ES0147024006	EUR	2	|BMF|0084|	f	81120	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147024006||es||False	f	t	t
INVERCLASIC	ES0155028030	EUR	2	|BMF|0083|	f	81122	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155028030||es||False	f	t	t
INVERMANRESA	ES0155827035	EUR	2	|BMF|0076|	f	81123	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155827035||es||False	f	t	t
INVERMANRESA 2	ES0173447030	EUR	2	|BMF|0076|	f	81124	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173447030||es||False	f	t	t
INVERSABADELL 10	ES0184984039	EUR	2	|BMF|0058|	f	81125	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184984039||es||False	f	t	t
INVERSABADELL 10 PREMIER	ES0155008032	EUR	2	|BMF|0058|	f	81126	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155008032||es||False	f	t	t
INVERSABADELL 25	ES0174417032	EUR	2	|BMF|0058|	f	81127	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174417032||es||False	f	t	t
INVERSABADELL 25 PREMIER	ES0177124031	EUR	2	|BMF|0058|	f	81128	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0177124031||es||False	f	t	t
INVERSABADELL 50	ES0155571039	EUR	2	|BMF|0058|	f	81129	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0155571039||es||False	f	t	t
INVERSIO ACTIVA	ES0152176006	EUR	2	|BMF|0020|	f	81130	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0152176006||es||False	f	t	t
IPARFONDO	ES0184921031	EUR	2	|BMF|0132|	f	81131	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184921031||es||False	f	t	t
IURISFOND	ES0156322036	EUR	2	|BMF|0037|	f	81132	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0156322036||es||False	f	t	t
KALAHARI ALPHA	ES0160623007	EUR	2	|BMF|0194|	f	81133	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0160623007||es||False	f	t	t
KUTXACRECIMIENTO	ES0156999031	EUR	2	|BMF|0086|	f	81135	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0156999031||es||False	f	t	t
KUTXAEMERGENTE	ES0156923031	EUR	2	|BMF|0086|	f	81136	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0156923031||es||False	f	t	t
KUTXAESTRUCTURADO 2	ES0157011034	EUR	2	|BMF|0086|	f	81137	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157011034||es||False	f	t	t
KUTXAESTRUCTURADO 3	ES0156891006	EUR	2	|BMF|0086|	f	81138	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0156891006||es||False	f	t	t
KUTXAFOND	ES0142520032	EUR	2	|BMF|0086|	f	81139	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142520032||es||False	f	t	t
KUTXAGARANTIZADO JUNIO 2014	ES0156645006	EUR	2	|BMF|0086|	f	81140	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0156645006||es||False	f	t	t
KUTXAESTABILIDAD	ES0157019037	EUR	2	|BMF|0086|	f	81141	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157019037||es||False	f	t	t
KUTXAINDEX 12	ES0156729032	EUR	2	|BMF|0086|	f	81142	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0156729032||es||False	f	t	t
KUTXAINDEX 15	ES0156730006	EUR	2	|BMF|0086|	f	81143	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0156730006||es||False	f	t	t
KUTXAINDEX10	ES0156727036	EUR	2	|BMF|0086|	f	81144	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0156727036||es||False	f	t	t
KUTXAINDEX16	ES0142523002	EUR	2	|BMF|0086|	f	81145	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142523002||es||False	f	t	t
KUTXAINDEX3	ES0157018039	EUR	2	|BMF|0086|	f	81146	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157018039||es||False	f	t	t
KUTXAINDEX6	ES0157012032	EUR	2	|BMF|0086|	f	81147	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157012032||es||False	f	t	t
KUTXAINDEX8	ES0157000037	EUR	2	|BMF|0086|	f	81148	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157000037||es||False	f	t	t
KUTXAVALORJAPON	ES0157034036	EUR	2	|BMF|0086|	f	81149	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157034036||es||False	f	t	t
KUTXARENDIMIENTO	ES0157013030	EUR	2	|BMF|0086|	f	81163	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157013030||es||False	f	t	t
KUTXARENT	ES0142521030	EUR	2	|BMF|0086|	f	81164	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142521030||es||False	f	t	t
KUTXAVALOR	ES0157029036	EUR	2	|BMF|0086|	f	81165	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157029036||es||False	f	t	t
KUTXAVALOR EUROPA	ES0157032030	EUR	2	|BMF|0086|	f	81166	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157032030||es||False	f	t	t
KUTXAVALOREEUU	ES0157014038	EUR	2	|BMF|0086|	f	81167	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157014038||es||False	f	t	t
KUTXAVALORINTER	ES0157033038	EUR	2	|BMF|0086|	f	81168	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157033038||es||False	f	t	t
MADRID EUROACCION G	ES0159078031	EUR	2	|BMF|0085|	f	81306	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159078031||es||False	f	t	t
SEGURFONDO GESTION DINAMICA, FI	ES0175437039	EUR	2	|BMF|0098|	f	81179	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175437039||es||False	f	t	t
TEBAS INVESTMENT	ES0178016038	EUR	2	|BMF|0185|	f	81180	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0178016038||es||False	f	t	t
UBS CAPITAL PLUS	ES0180931034	EUR	2	|BMF|0185|	f	81181	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180931034||es||False	f	t	t
UBS CORPORATE PLUS	ES0180914006	EUR	2	|BMF|0185|	f	81182	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180914006||es||False	f	t	t
UBS DINERO	ES0180942031	EUR	2	|BMF|0185|	f	81183	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180942031||es||False	f	t	t
LAIDINER	ES0157657034	EUR	2	|BMF|0051|	f	81200	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157657034||es||False	f	t	t
LAREDOFONDO	ES0157940034	EUR	2	|BMF|0012|	f	81201	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157940034||es||False	f	t	t
LEALTAD MUNDIAL	ES0158012031	EUR	2	|BMF|0200|	f	81202	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158012031||es||False	f	t	t
LEASETEN III	ES0158021032	EUR	2	|BMF|0012|	f	81203	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158021032||es||False	f	t	t
LIBERTY EURO RENTA	ES0179171030	EUR	2	|BMF|0015|	f	81205	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0179171030||es||False	f	t	t
LIBERTY EUROPEAN STOCK MARKET	ES0179172038	EUR	2	|BMF|0015|	f	81206	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0179172038||es||False	f	t	t
LIBERTY SPANISH STOCK MARKET IND	ES0137999035	EUR	2	|BMF|0015|	f	81207	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137999035||es||False	f	t	t
LLOYDS BOLSA	ES0158865032	EUR	2	|BMF|0093|	f	81208	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158865032||es||False	f	t	t
LAIETANA GESTIO ACTIVA	ES0157656036	EUR	2	|BMF|0051|	f	81209	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157656036||es||False	f	t	t
SEGURFONDO GLOBAL MACRO	ES0175403007	EUR	2	|BMF|0098|	f	81210	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175403007||es||False	f	t	t
SEGURFONDO RENA FIJA FLEXIBLE	ES0175414004	EUR	2	|BMF|0098|	f	81211	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175414004||es||False	f	t	t
SEGURFONDO RENTA VARIABLE	ES0175445032	EUR	2	|BMF|0098|	f	81212	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175445032||es||False	f	t	t
LLOYDS FONDO 1	ES0158862039	EUR	2	|BMF|0093|	f	81215	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158862039||es||False	f	t	t
LLOYDS PREMIUM C.P.	ES0158866030	EUR	2	|BMF|0093|	f	81216	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158866030||es||False	f	t	t
LLOYDS RENTA FIJA C.P.	ES0158864035	EUR	2	|BMF|0093|	f	81221	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158864035||es||False	f	t	t
MADRID BOL.OPORTUNIDAD ELECCION	ES0158957037	EUR	2	|BMF|0085|	f	81222	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158957037||es||False	f	t	t
MADRID BOLSA	ES0158174039	EUR	2	|BMF|0085|	f	81223	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158174039||es||False	f	t	t
MADRID BOLSA EUROPEA	ES0159031030	EUR	2	|BMF|0085|	f	81224	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159031030||es||False	f	t	t
MADRID BOLSA JAPONESA	ES0158983033	EUR	2	|BMF|0085|	f	81225	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158983033||es||False	f	t	t
MADRID BOLSA LATINOAMERICANA	ES0158963035	EUR	2	|BMF|0085|	f	81226	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158963035||es||False	f	t	t
MADRID BOLSA NEW YORK	ES0161937034	EUR	2	|BMF|0085|	f	81227	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0161937034||es||False	f	t	t
MADRID BOLSA OPORTUNIDAD	ES0159076035	EUR	2	|BMF|0085|	f	81228	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159076035||es||False	f	t	t
MADRID BOLSA VALOR	ES0138840030	EUR	2	|BMF|0085|	f	81229	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138840030||es||False	f	t	t
MADRID MULTIGESTION DINAMICA	ES0163611033	EUR	2	|BMF|0085|	f	81230	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0163611033||es||False	f	t	t
MADRID PREMIERE	ES0158178030	EUR	2	|BMF|0085|	f	81231	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158178030||es||False	f	t	t
MADRID RENTABILIDAD ANUAL	ES0158211039	EUR	2	|BMF|0085|	f	81232	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158211039||es||False	f	t	t
MADRID RENTABILIDAD TRIENAL	ES0158984031	EUR	2	|BMF|0085|	f	81233	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158984031||es||False	f	t	t
MADRID TESORERIA	ES0147507034	EUR	2	|BMF|0085|	f	81234	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147507034||es||False	f	t	t
MADRID TRIPLE B	ES0159178039	EUR	2	|BMF|0085|	f	81235	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159178039||es||False	f	t	t
MANRENSA GARANTIT VIII	ES0159535006	EUR	2	|BMF|0076|	f	81236	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159535006||es||False	f	t	t
MEDIOLANUM FONDCUENTA	ES0138816030	EUR	2	|BMF|0002|	f	81237	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138816030||es||False	f	t	t
MEDIOLANUM MERCADOS EMERGENTES	ES0136467000	EUR	2	|BMF|0002|	f	81238	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0136467000||es||False	f	t	t
MEDIOLANUM MERCADOS EMERGENTES	ES0136467034	EUR	2	|BMF|0002|	f	81239	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0136467034||es||False	f	t	t
MEDIOLANUM PREMIER	ES0148219035	EUR	2	|BMF|0002|	f	81240	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0148219035||es||False	f	t	t
MADRID CESTA EUROPEA	ES0159077033	EUR	2	|BMF|0085|	f	81248	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159077033||es||False	f	t	t
MADRID CESTA OPTIMA	ES0159128034	EUR	2	|BMF|0085|	f	81250	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159128034||es||False	f	t	t
MADRID CRECIMIENTO DINAMICO	ES0158965030	EUR	2	|BMF|0085|	f	81251	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158965030||es||False	f	t	t
MADRID DEUDA ELECCION	ES0158966038	EUR	2	|BMF|0085|	f	81252	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158966038||es||False	f	t	t
MADRID DEUDA FONDTESORO	ES0158176034	EUR	2	|BMF|0085|	f	81254	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158176034||es||False	f	t	t
MADRID DEUDA PUBLICA EURO	ES0147508032	EUR	2	|BMF|0085|	f	81260	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147508032||es||False	f	t	t
MADRID DIMENSION OPTIMA 1	ES0158972036	EUR	2	|BMF|0085|	f	81261	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158972036||es||False	f	t	t
MADRID DINERO	ES0159082033	EUR	2	|BMF|0085|	f	81262	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159082033||es||False	f	t	t
MADRID DOLAR	ES0159033036	EUR	2	|BMF|0085|	f	81268	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159033036||es||False	f	t	t
MADRID EMPRESAS CASH	ES0147499034	EUR	2	|BMF|0085|	f	81304	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147499034||es||False	f	t	t
MADRID EUROBOLSA 100	ES0159088030	EUR	2	|BMF|0085|	f	81307	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0159088030||es||False	f	t	t
MADRID FOND ORO	ES0138707031	EUR	2	|BMF|0085|	f	81308	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138707031||es||False	f	t	t
MADRID FONDLIBRETA 2010	ES0158958035	EUR	2	|BMF|0085|	f	81309	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158958035||es||False	f	t	t
MADRID FONDLIBRETA 2011	ES0158959033	EUR	2	|BMF|0085|	f	81310	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158959033||es||False	f	t	t
MEDIFOND	ES0161998036	EUR	2	|BMF|0002|	f	81312	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0161998036||es||False	f	t	t
MEDIOLANUM ALPHA PLUS	ES0139008009	EUR	2	|BMF|0002|	f	81313	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0139008009||es||False	f	t	t
MEDIOLANUM ALPHA PLUS	ES0139008033	EUR	2	|BMF|0002|	f	81314	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0139008033||es||False	f	t	t
UBS ESPAñA GESTION ACTIVA	ES0180943039	EUR	2	|BMF|0185|	f	81315	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180943039||es||False	f	t	t
UBS EUROGOBIERNOS CORTO PLAZO	ES0180913008	EUR	2	|BMF|0185|	f	81316	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180913008||es||False	f	t	t
MEDCORRENT	ES0161999034	EUR	2	|BMF|0002|	f	81317	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0161999034||es||False	f	t	t
MEDIOLANUM ACTIVO	ES0165127004	EUR	2	|BMF|0002|	f	81318	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165127004||es||False	f	t	t
MEDIOLANUM ACTIVO	ES0165127038	EUR	2	|BMF|0002|	f	81319	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165127038||es||False	f	t	t
MEDIOLANUM CRECIMIENTO	ES0137389005	EUR	2	|BMF|0002|	f	81320	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137389005||es||False	f	t	t
MEDIOLANUM CRECIMIENTO	ES0137389039	EUR	2	|BMF|0002|	f	81321	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137389039||es||False	f	t	t
MEDIOLANUM ESPAÑA R.V.	ES0136466002	EUR	2	|BMF|0002|	f	81322	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0136466002||es||False	f	t	t
MEDIOLANUM ESPAÑA R.V.	ES0136466036	EUR	2	|BMF|0002|	f	81323	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0136466036||es||False	f	t	t
MEDIOLANUM EUROPA R.V.	ES0165128002	EUR	2	|BMF|0002|	f	81324	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165128002||es||False	f	t	t
MEDIOLANUM EUROPA R.V.	ES0165128036	EUR	2	|BMF|0002|	f	81325	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165128036||es||False	f	t	t
MEDIOLANUM EXCELLENT	ES0136452036	EUR	2	|BMF|0002|	f	81326	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0136452036||es||False	f	t	t
MEDIOLANUM RENTA	ES0165126030	EUR	2	|BMF|0002|	f	81328	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165126030||es||False	f	t	t
MEDIVALOR EUROPEO	ES0162022034	EUR	2	|BMF|0002|	f	81329	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162022034||es||False	f	t	t
MEDIVALOR GLOBAL	ES0162031035	EUR	2	|BMF|0002|	f	81330	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162031035||es||False	f	t	t
MERCH FONTEMAR	ES0138914033	EUR	2	|BMF|0034|	f	81331	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138914033||es||False	f	t	t
MERCH UNIVERSAL	ES0182105033	EUR	2	|BMF|0034|	f	81332	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182105033||es||False	f	t	t
MERCH-EUROUNION	ES0162211033	EUR	2	|BMF|0034|	f	81333	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162211033||es||False	f	t	t
MERCH-OPORTUNIDADES	ES0162305033	EUR	2	|BMF|0034|	f	81334	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162305033||es||False	f	t	t
METAVALOR EUROPA	ES0162757035	EUR	2	|BMF|0040|	f	81339	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162757035||es||False	f	t	t
METAVALOR GLOBAL	ES0162741005	EUR	2	|BMF|0040|	f	81340	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162741005||es||False	f	t	t
MUTUAFONDO FONDOS	ES0165194038	EUR	2	|BMF|0021|	f	81341	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165194038||es||False	f	t	t
MUTUAFONDO GESTION ACCIONES	ES0165181035	EUR	2	|BMF|0021|	f	81343	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165181035||es||False	f	t	t
UNIFOND 2012-XII	ES0181069032	EUR	2	|BMF|0154|	f	81344	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181069032||es||False	f	t	t
UNIFOND 2013-IV	ES0181083033	EUR	2	|BMF|0154|	f	81345	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181083033||es||False	f	t	t
MUTUAFONDO EURO CONVERGENCIA	ES0175805037	EUR	2	|BMF|0021|	f	81365	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175805037||es||False	f	t	t
MUTUAFONDO CORTO PLAZO	ES0165142037	EUR	2	|BMF|0021|	f	81366	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165142037||es||False	f	t	t
MUTUAFONDO GESTION MIXTO	ES0165268030	EUR	2	|BMF|0021|	f	81373	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0165268030||es||False	f	t	t
UNIFOND 2014-IV CRECIENTE	ES0181001035	EUR	2	|BMF|0154|	f	81377	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181001035||es||False	f	t	t
UNIFOND 2014-V	ES0181062037	EUR	2	|BMF|0154|	f	81378	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181062037||es||False	f	t	t
UNIFOND 2011	ES0181068034	EUR	2	|BMF|0154|	f	81379	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181068034||es||False	f	t	t
UNIFOND BOLSA 2012	ES0181009038	EUR	2	|BMF|0154|	f	81381	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181009038||es||False	f	t	t
UNIFOND BOLSA 60	ES0178235000	EUR	2	|BMF|0154|	f	81382	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0178235000||es||False	f	t	t
UNIFOND BOLSA GLOBAL	ES0180983035	EUR	2	|BMF|0154|	f	81383	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180983035||es||False	f	t	t
UNIFOND BOLSA PATRIMONIO II	ES0178237006	EUR	2	|BMF|0154|	f	81384	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0178237006||es||False	f	t	t
UNIFOND BOLSA X	ES0181003007	EUR	2	|BMF|0154|	f	81385	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181003007||es||False	f	t	t
UNIFOND DINERO	ES0181074032	EUR	2	|BMF|0154|	f	81386	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181074032||es||False	f	t	t
UNIFOND ESTRELLA	ES0181063035	EUR	2	|BMF|0154|	f	81387	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181063035||es||False	f	t	t
UNIFOND EURIBOR MAS 50 GARANTIZA	ES0178236008	EUR	2	|BMF|0154|	f	81388	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0178236008||es||False	f	t	t
UNIFOND FONDANDALUCIA	ES0181073034	EUR	2	|BMF|0154|	f	81389	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181073034||es||False	f	t	t
UNIFOND GARANTIZADO MAS 3	ES0181004005	EUR	2	|BMF|0154|	f	81390	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181004005||es||False	f	t	t
SABADELL BS SELECC.HEDGE TOP	ES0158289001	EUR	2	|BMF|0058|	f	81392	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158289001||es||False	f	t	t
PREMIUM GLOBAL 4	ES0171002035	EUR	2	|BMF|0159|	f	81397	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0171002035||es||False	f	t	t
PREMIUM GLOBAL EXITO	ES0170639035	EUR	2	|BMF|0159|	f	81398	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170639035||es||False	f	t	t
PREMIUM JB BOLSA EURO	ES0170643037	EUR	2	|BMF|0159|	f	81399	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170643037||es||False	f	t	t
PREMIUM JB BOLSA INTERNACIONAL	ES0170616033	EUR	2	|BMF|0159|	f	81400	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170616033||es||False	f	t	t
PREMIUM JB CONSERVADOR	ES0115217038	EUR	2	|BMF|0159|	f	81401	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115217038||es||False	f	t	t
PREMIUM MIXTO OPORTUNIDADES	ES0170650032	EUR	2	|BMF|0159|	f	81402	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170650032||es||False	f	t	t
PREMIUM RENTA FIJA	ES0170602033	EUR	2	|BMF|0159|	f	81403	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170602033||es||False	f	t	t
PREVIBOLSA	ES0170738035	EUR	2	|BMF|0015|	f	81404	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170738035||es||False	f	t	t
PRIVADO LIQUIDEZ DINAMICA	ES0170893038	EUR	2	|BMF|0198|	f	81405	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170893038||es||False	f	t	t
PRIVARY V GLOBAL	ES0170863031	EUR	2	|BMF|0037|	f	81406	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170863031||es||False	f	t	t
PRIVAT BCN MIXTO	ES0114907035	EUR	2	|BMF|0078|	f	81407	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114907035||es||False	f	t	t
PRIVAT BOLSA	ES0114913033	EUR	2	|BMF|0078|	f	81408	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114913033||es||False	f	t	t
R.V. 30 FOND	ES0173856032	EUR	2	|BMF|0126|	f	81414	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173856032||es||False	f	t	t
RADAR INVERSION	ES0172603005	EUR	2	|BMF|0049|	f	81416	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0172603005||es||False	f	t	t
RIVA Y GARCIA SELECCION CONSERV.	ES0156905004	EUR	2	|BMF|0131|	f	81422	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0156905004||es||False	f	t	t
RENTA FIJA 21	ES0126517038	EUR	2	|BMF|0128|	f	81449	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0126517038||es||False	f	t	t
RENTACASER	ES0173393036	EUR	2	|BMF|0128|	f	81450	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173393036||es||False	f	t	t
RENTMADRID	ES0173426034	EUR	2	|BMF|0085|	f	81451	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173426034||es||False	f	t	t
RENTMADRID 2	ES0173441033	EUR	2	|BMF|0085|	f	81455	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0173441033||es||False	f	t	t
RFMI MULTIGESTION FI	ES0122762000	EUR	2	|BMF|0185|	f	81456	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0122762000||es||False	f	t	t
RIVA Y GARCIA ACCIONES I	ES0178220036	EUR	2	|BMF|0131|	f	81457	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0178220036||es||False	f	t	t
RIVA Y GARCIA AHORRO	ES0174039034	EUR	2	|BMF|0131|	f	81462	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174039034||es||False	f	t	t
RIVA Y GARCIA DISCRECIONAL	ES0137763035	EUR	2	|BMF|0131|	f	81481	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137763035||es||False	f	t	t
RIVA Y GARCIA GLOBAL	ES0112781036	EUR	2	|BMF|0131|	f	81482	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0112781036||es||False	f	t	t
RIVA Y GARCIA R.F. INSTITUCIONAL	ES0174013005	EUR	2	|BMF|0131|	f	81483	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174013005||es||False	f	t	t
RURAL 10,60 GARANTIZADO RENTA FIJA	ES0174414039	EUR	2	|BMF|0140|	f	81484	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174414039||es||False	f	t	t
RURAL 12,60 GARANTIZADO RF, FI	ES0174227035	EUR	2	|BMF|0140|	f	81485	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0174227035||es||False	f	t	t
RURAL 13 GARANTIZADO RF FI	ES0156832000	EUR	2	|BMF|0140|	f	81486	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0156832000||es||False	f	t	t
SANTANDER BENEFICIO EUROPA	ES0138325032	EUR	2	|BMF|0012|	f	81538	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138325032||es||False	f	t	t
SANTANDER BEST	ES0137898039	EUR	2	|BMF|0012|	f	81539	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0137898039||es||False	f	t	t
SANTANDER BEST 2.	ES0175161035	EUR	2	|BMF|0012|	f	81540	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175161035||es||False	f	t	t
SANTANDER BOLSAS GANADORAS	ES0175200031	EUR	2	|BMF|0012|	f	81541	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175200031||es||False	f	t	t
SANTANDER BOLSAS MUNDIALES	ES0175173030	EUR	2	|BMF|0012|	f	81542	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175173030||es||False	f	t	t
SANTANDER BONOS FONDVALECIA	ES0117618035	EUR	2	|BMF|0012|	f	81543	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0117618035||es||False	f	t	t
SANTANDER BRICT	ES0176095034	EUR	2	|BMF|0012|	f	81544	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0176095034||es||False	f	t	t
SANTANDER CLASS DOLAR	ES0166492001	EUR	2	|BMF|0012|	f	81545	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0166492001||es||False	f	t	t
SANTANDER CLIQUET EUROPA	ES0157787039	EUR	2	|BMF|0012|	f	81546	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0157787039||es||False	f	t	t
SANTANDER CORTO EURO 1	ES0105931036	EUR	2	|BMF|0012|	f	81547	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0105931036||es||False	f	t	t
SANTANDER CORTO EURO 2	ES0172205033	EUR	2	|BMF|0012|	f	81548	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0172205033||es||False	f	t	t
SANTANDER CORTO PLAZO DOLAR	ES0121748034	EUR	2	|BMF|0012|	f	81549	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0121748034||es||False	f	t	t
SANTANDER CORTO PLAZO PLUS	ES0175075037	EUR	2	|BMF|0012|	f	81550	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175075037||es||False	f	t	t
SANTANDER DECISION CONSERVADOR	ES0176097030	EUR	2	|BMF|0012|	f	81551	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0176097030||es||False	f	t	t
SANTANDER DECISION MODERADO	ES0107777031	EUR	2	|BMF|0012|	f	81552	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107777031||es||False	f	t	t
SANTANDER DEPOSITOS PLUS	ES0107762033	EUR	2	|BMF|0012|	f	81553	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107762033||es||False	f	t	t
SANTANDER DEPOSITOS PLUS A	ES0107762009	EUR	2	|BMF|0012|	f	81554	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107762009||es||False	f	t	t
SANTANDER DEPOSITOS PLUS B	ES0107762017	EUR	2	|BMF|0012|	f	81555	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107762017||es||False	f	t	t
SANTANDER DOBLE OPORTUNIDAD	ES0128502038	EUR	2	|BMF|0012|	f	81556	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0128502038||es||False	f	t	t
SANTANDER DOBLE OPORTUNIDAD 2	ES0107991038	EUR	2	|BMF|0012|	f	81557	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107991038||es||False	f	t	t
Verso Paper Corp.	\N	USD	1	\N	f	81071	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#VRS||us||False	f	t	t
SANTANDER EMERGENTES EUROPA	ES0107772032	EUR	2	|BMF|0012|	f	81558	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107772032||es||False	f	t	t
SANTANDER EQUILIBRIO ACTIVO	ES0175078031	EUR	2	|BMF|0012|	f	81559	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175078031||es||False	f	t	t
SANTANDER EUROINDICE	ES0175147034	EUR	2	|BMF|0012|	f	81560	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175147034||es||False	f	t	t
SANTANDER FINANCIAL OPPORTUNITIE	ES0113604005	EUR	2	|BMF|0012|	f	81561	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113604005||es||False	f	t	t
SANTANDER FONDTESORO CORTO PLAZO	ES0175203035	EUR	2	|BMF|0012|	f	81562	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0175203035||es||False	f	t	t
UNIFOND RENTA FIJA GLOBAL	ES0181054034	EUR	2	|BMF|0154|	f	81568	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181054034||es||False	f	t	t
UNIFOND RENTA VARIABLE I	ES0181010036	EUR	2	|BMF|0154|	f	81569	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181010036||es||False	f	t	t
UNIFOND TESORERIA	ES0181036031	EUR	2	|BMF|0154|	f	81570	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181036031||es||False	f	t	t
UNIFOND TRANQUILIDAD	ES0181031032	EUR	2	|BMF|0154|	f	81571	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0181031032||es||False	f	t	t
UNNIM  EUROFONS BORSA	ES0125128035	EUR	2	|BMF|0192|	f	81572	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125128035||es||False	f	t	t
UNNIM DINER	ES0125153033	EUR	2	|BMF|0192|	f	81573	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125153033||es||False	f	t	t
UNNIM FONDIPOSIT	ES0125118036	EUR	2	|BMF|0192|	f	81574	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125118036||es||False	f	t	t
UNNIM GARANTI 4	ES0125129009	EUR	2	|BMF|0192|	f	81575	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125129009||es||False	f	t	t
UNNIM GARANTIT 5	ES0125130007	EUR	2	|BMF|0192|	f	81576	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125130007||es||False	f	t	t
UNNIM GARANTIT 6	ES0125131005	EUR	2	|BMF|0192|	f	81577	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125131005||es||False	f	t	t
UNNIM PLATINUM 10	ES0125122038	EUR	2	|BMF|0192|	f	81579	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125122038||es||False	f	t	t
UNNIM SELECCIO	ES0125154031	EUR	2	|BMF|0192|	f	81580	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125154031||es||False	f	t	t
URQUIJO INVERS.ETICA SOLIDARIA	ES0182543035	EUR	2	|BMF|0058|	f	81581	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182543035||es||False	f	t	t
Integralis AG	DE0005155030	EUR	1	|DEUTSCHEBOERSE|	f	74758	\N	\N	\N	\N	100	c	0	5	\N	\N	\N	DEUTSCHEBOERSE#DE0005155030||de||False	f	t	t
Medtronic Inc.	\N	USD	1	\N	f	74739	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MDT||us||False	f	t	t
Wimm-Bill-Dann Foods OJSC	\N	USD	1	\N	f	74740	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WBD||us||False	f	t	t
Colgate-Palmolive Co.	\N	USD	1	\N	f	74757	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CL||us||False	f	t	t
PetroChina Co. Ltd.	\N	USD	1	\N	f	74760	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PTR||us||False	f	t	t
ArcelorMittal	\N	USD	1	\N	f	74767	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#MT||us||False	f	t	t
EURO / USA$	\N	/	6	\N	f	74747	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	EUR2USD||eu||True	f	t	t
ABANDO EQUITIES	ES0109656001	EUR	2	|BMF|0206|	f	74751	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109656001||es||False	f	t	t
BG BRIC GARANTIZADO	ES0114612031	EUR	2	|BMF|0110|	f	74752	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114612031||es||False	f	t	t
RehabCare Group Inc.	\N	USD	1	\N	f	74971	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#RHB||us||False	f	t	t
Call IBEX 35 | 8750 € | 21/10/11 | B9548	FR0011080779	EUR	5	|SGW|	f	75040	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#B9548||fr||False	f	t	t
SAP AG	\N	USD	1	\N	f	75103	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#SAP||us||False	f	t	t
Harmony Gold Mining Co. Ltd.	\N	USD	1	\N	f	75165	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HMY||us||False	f	t	t
Pitney Bowes Inc.	\N	USD	1	\N	f	75166	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#PBI||us||False	f	t	t
\N	\N	\N	\N	\N	f	75227	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0131423008||None||False	f	t	t
CAJA SEGOVIA RENDIMIENTO GARANTIZADO 3	ES0169081033	EUR	2	|BMF|0128|	f	75346	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169081033||es||False	f	t	t
Humana Inc.	\N	USD	1	\N	f	75357	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HUM||us||False	f	t	t
AirTran Holdings Inc.	\N	USD	1	\N	f	75526	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#AAI||us||False	f	t	t
TURBO Call IBEX 35 | 8000 € | 16/12/11 | 55088	FR0011092121	EUR	5	|SGW|	f	75587	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	SGW#55088||fr||False	f	t	t
Wabtec	\N	USD	1	\N	f	75722	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WAB||us||False	f	t	t
\N	\N	\N	\N	\N	f	75915	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0116848005||None||False	f	t	t
Taubman Centers Inc.	\N	USD	1	\N	f	76006	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#TCO||us||False	f	t	t
LAREDO INVERSION LIBRE	ES0158644007	EUR	2	|BMF|0220|	f	76246	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0158644007||es||False	f	t	t
IDEX Corp.	\N	USD	1	\N	f	76257	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#IEX||us||False	f	t	t
\N	\N	\N	\N	\N	f	76626	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0114023007||None||False	f	t	t
LaBranche & Co. Inc.	\N	USD	1	\N	f	77058	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#LAB||us||False	f	t	t
EUROSIC	FR0011110915	EUR	1	|EURONEXT|	f	77108	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0011110915||fr||False	f	t	t
SANTANDER MIXTO R.F. 75-25	ES0138899036	EUR	2	|BMF|0012|	f	77171	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138899036||es||False	f	t	t
SANTANDER PREMIER DOLAR	ES0107895007	EUR	2	|BMF|0012|	f	77172	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0107895007||es||False	f	t	t
CoreSite Realty Corp.	\N	USD	1	\N	f	77233	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#COR||us||False	f	t	t
CARPINIENNE PART.	FR0000064156	EUR	1	|EURONEXT|	f	77234	\N	\N	\N	\N	100	c	0	3	\N	\N	\N	EURONEXT#FR0000064156||fr||False	f	t	t
BBVA EUROPA MULTIPLE 6	ES0113858007	EUR	2	|f_es_0014|f_es_BMF|	f	76065	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113858007||es||False	f	t	t
Beta Renta Variable Global FI	ES0114668033	EUR	2	|f_es_BMF|	f	74840					100	c	0	1	None	{2}	\N	ES0114668033||None||False	f	t	t
BBVA BONOS VALOR RELATIVO	ES0113857033	EUR	2	|f_es_0014|f_es_BMF|	f	76614	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113857033||es||False	f	t	t
Williams-Sonoma Inc.	\N	USD	1	\N	f	79139	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#WSM||us||False	f	t	t
\N	\N	\N	\N	\N	f	80202	\N	\N	\N	\N	100	c	0	1	\N	\N	\N	ES0180962005||None||False	f	t	t
Cambrex Corp.	\N	USD	1	\N	f	80359	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#CBM||us||False	f	t	t
ITC Holdings Corp.	\N	USD	1	\N	f	80884	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#ITC||us||False	f	t	t
Harbinger Group Inc.	\N	USD	1	\N	f	81064	\N	\N	\N	\N	100	c	0	2	\N	\N	\N	NYSE#HRG||us||False	f	t	t
BBVA FON-PLAZO 2011 C	ES0113856035	EUR	2	|f_es_0014|f_es_BMF|	f	75399	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113856035||es||False	f	t	t
BBVA FON-PLAZO 2012	ES0113459038	EUR	2	|f_es_0014|f_es_BMF|	f	75401	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113459038||es||False	f	t	t
BBVA EXTRA 5 ACCIONES II	ES0113456034	EUR	2	|f_es_0014|f_es_BMF|	f	75554	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113456034||es||False	f	t	t
BBVA INDICES 120	ES0114098009	EUR	2	|f_es_0014|f_es_BMF|	f	75633	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114098009||es||False	f	t	t
BBVA DINERO	ES0113202032	EUR	2	|f_es_0014|f_es_BMF|	f	75737	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113202032||es||False	f	t	t
BBVA DJ EUROSTOXX 50 4 PLUS D	ES0110186030	EUR	2	|f_es_0014|f_es_BMF|	f	75743	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110186030||es||False	f	t	t
BBVA DOBLE GARANTIA	ES0113753000	EUR	2	|f_es_0014|f_es_BMF|	f	75760	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113753000||es||False	f	t	t
BBVA ELITE PROTEGIDO	ES0114788005	EUR	2	|f_es_0014|f_es_BMF|	f	75790	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114788005||es||False	f	t	t
BBVA BOLSA IBEX QUANT	ES0114206032	EUR	2	|f_es_0014|f_es_BMF|	f	75839	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114206032||es||False	f	t	t
BBVA BOLSA EURO QUANT	ES0114225032	EUR	2	|f_es_0014|f_es_BMF|	f	75840	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114225032||es||False	f	t	t
BBVA TOP 5 GARANTIZADO	ES0114152004	EUR	2	|f_es_0014|f_es_BMF|	f	75879	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114152004||es||False	f	t	t
BBVA TOP 5 GARANTIZADO II	ES0114321039	EUR	2	|f_es_0014|f_es_BMF|	f	75885	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114321039||es||False	f	t	t
BBVA TOP 5 GARANTIZADO III	ES0113457032	EUR	2	|f_es_0014|f_es_BMF|	f	75896	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113457032||es||False	f	t	t
BBVA BOLSA ASIA MF	ES0108929037	EUR	2	|f_es_0014|f_es_BMF|	f	76021	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108929037||es||False	f	t	t
BBVA BOLSA CHINA	ES0113818001	EUR	2	|f_es_0014|f_es_BMF|	f	76023	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113818001||es||False	f	t	t
BBVA BOLSA JAPON CUBIERTO	ES0110088038	EUR	2	|f_es_0014|f_es_BMF|	f	76026	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110088038||es||False	f	t	t
BBVA ELECCION OPTIMA GARANTIZADO	ES0114175039	EUR	2	|f_es_0014|f_es_BMF|	f	76027	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114175039||es||False	f	t	t
BBVA ELECCION OPTIMA GARANTIZADO II	ES0109995037	EUR	2	|f_es_0014|f_es_BMF|	f	76028	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109995037||es||False	f	t	t
BBVA AHORRO EMPRESAS	ES0114129036	EUR	2	|f_es_0014|f_es_BMF|	f	76050	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114129036||es||False	f	t	t
BBVA EUROPA OBJETIVO 125	ES0115162002	EUR	2	|f_es_0014|f_es_BMF|	f	76067	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115162002||es||False	f	t	t
BBVA EXTRA 5 GARANTIZADO	ES0145927036	EUR	2	|f_es_0014|f_es_BMF|	f	76068	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0145927036||es||False	f	t	t
BBVA EXTRA TESORERIA	ES0110091032	EUR	2	|f_es_0014|f_es_BMF|	f	76072	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110091032||es||False	f	t	t
BBVA FON-PLAZO 2012 D	ES0180664007	EUR	2	|f_es_0014|f_es_BMF|	f	76122	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180664007||es||False	f	t	t
BBVA FON-PLAZO 2012 F	ES0113098034	EUR	2	|f_es_0014|f_es_BMF|	f	76124	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113098034||es||False	f	t	t
BBVA FON-PLAZO 2012 G	ES0142444001	EUR	2	|f_es_0014|f_es_BMF|	f	76136	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142444001||es||False	f	t	t
BBVA FON-PLAZO 2013 B	ES0115161004	EUR	2	|f_es_0014|f_es_BMF|	f	76137	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115161004||es||False	f	t	t
BBVA FON-PLAZO 2013 D	ES0115163000	EUR	2	|f_es_0014|f_es_BMF|	f	76145	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115163000||es||False	f	t	t
BBVA FON-PLAZO 2014 B	ES0114099007	EUR	2	|f_es_0014|f_es_BMF|	f	76171	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114099007||es||False	f	t	t
BBVA GARANTIZADO 5 X 5 II	ES0114189006	EUR	2	|f_es_0014|f_es_BMF|	f	76187	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114189006||es||False	f	t	t
BBVA GESTION MODERADA	ES0113993036	EUR	2	|f_es_0014|f_es_BMF|	f	76189	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113993036||es||False	f	t	t
BBVA GLOBAL AUTOCANCELABLE BP	ES0113825006	EUR	2	|f_es_0014|f_es_BMF|	f	76195	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113825006||es||False	f	t	t
BBVA INDICE USA PLUS	ES0134599036	EUR	2	|f_es_0014|f_es_BMF|	f	76198	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0134599036||es||False	f	t	t
BBVA OPORTUNIDAD GEOGRAFICA GARANTIZADO	ES0114142039	EUR	2	|f_es_0014|f_es_BMF|	f	76199	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114142039||es||False	f	t	t
BBVA PLAN RENTA	ES0113204038	EUR	2	|f_es_0014|f_es_BMF|	f	76200	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113204038||es||False	f	t	t
BBVA PLAN RENTAS 10 B	ES0142334038	EUR	2	|f_es_0014|f_es_BMF|	f	76201	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142334038||es||False	f	t	t
BBVA PLAN RENTAS 2012 C	ES0169990035	EUR	2	|f_es_0014|f_es_BMF|	f	76216	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169990035||es||False	f	t	t
BBVA PLAN RENTAS 2012 G	ES0113429007	EUR	2	|f_es_0014|f_es_BMF|	f	76237	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113429007||es||False	f	t	t
BBVA PLAN RENTAS 2011 F	ES0113425039	EUR	2	|f_es_0014|f_es_BMF|	f	76251	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113425039||es||False	f	t	t
BBVA PLAN RENTAS 2011 G	ES0113426037	EUR	2	|f_es_0014|f_es_BMF|	f	76252	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113426037||es||False	f	t	t
BBVA PLAN RENTAS 2012	ES0114455035	EUR	2	|f_es_0014|f_es_BMF|	f	76253	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114455035||es||False	f	t	t
BBVA PLAN RENTAS 2012 B	ES0169989037	EUR	2	|f_es_0014|f_es_BMF|	f	76254	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169989037||es||False	f	t	t
UNO-E IBEX 35	ES0182154031	EUR	2	|f_es_0014|f_es_BMF|	f	76265	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0182154031||es||False	f	t	t
BBVA SOLIDEZ III BP	ES0110008002	EUR	2	|f_es_0014|f_es_BMF|	f	76320	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110008002||es||False	f	t	t
BBVA SOLIDEZ IX BP	ES0116861008	EUR	2	|f_es_0014|f_es_BMF|	f	76321	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116861008||es||False	f	t	t
BBVA SOLIDEZ VI	ES0110009000	EUR	2	|f_es_0014|f_es_BMF|	f	76322	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110009000||es||False	f	t	t
BBVA SOLIDEZ VII	ES0110010008	EUR	2	|f_es_0014|f_es_BMF|	f	76332	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110010008||es||False	f	t	t
BBVA BOLSA GARANTIZADO	ES0114128038	EUR	2	|f_es_0014|f_es_BMF|	f	76370	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114128038||es||False	f	t	t
BBVA BOLSA EUROPA FINANZAS	ES0180661003	EUR	2	|f_es_0014|f_es_BMF|	f	76373	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180661003||es||False	f	t	t
BBVA BOLSA INDICE	ES0110182039	EUR	2	|f_es_0014|f_es_BMF|	f	76374	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110182039||es||False	f	t	t
BBVA BOLSA LATAM	ES0142332032	EUR	2	|f_es_0014|f_es_BMF|	f	76377	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142332032||es||False	f	t	t
BBVA BONOS L.P.FLEXIBLES	ES0108926033	EUR	2	|f_es_0014|f_es_BMF|	f	76378	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108926033||es||False	f	t	t
BBVA FON-PLAZO 2009 D	ES0180662001	EUR	2	|f_es_0014|f_es_BMF|	f	76380	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0180662001||es||False	f	t	t
BBVA PLAN RENTAS 2008 B	ES0177865039	EUR	2	|f_es_0014|f_es_BMF|	f	76418	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0177865039||es||False	f	t	t
BBVA BONOS INTERES FLOTANTE	ES0113196036	EUR	2	|f_es_0014|f_es_BMF|	f	76562	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113196036||es||False	f	t	t
BBVA BONOS LARGO PLAZO GOBIER.II	ES0162081030	EUR	2	|f_es_0014|f_es_BMF|	f	76612	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0162081030||es||False	f	t	t
BBVA BONOS LARGO PLAZO GOBIERNOS	ES0110001031	EUR	2	|f_es_0014|f_es_BMF|	f	76613	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110001031||es||False	f	t	t
BBVA DOBLE GARANTIA II	ES0113754008	EUR	2	|f_es_0014|f_es_BMF|	f	76615	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113754008||es||False	f	t	t
BBVA EVOLUCION V, 10	ES0113988036	EUR	2	|f_es_0014|f_es_BMF|	f	76664	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113988036||es||False	f	t	t
BBVA TOP 5 GARANTIZADO IV	ES0125468001	EUR	2	|f_es_0014|f_es_BMF|	f	76765	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125468001||es||False	f	t	t
BBVA TOP GARANTIZADO 4	ES0114226030	EUR	2	|f_es_0014|f_es_BMF|	f	76799	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114226030||es||False	f	t	t
BBVA EUROPA OBJETIVO 125 II	ES0113859005	EUR	2	|f_es_0014|f_es_BMF|	f	76960	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113859005||es||False	f	t	t
BBVA AHORRO II	ES0125628000	EUR	2	|f_es_0014|f_es_BMF|	f	77045	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125628000||es||False	f	t	t
BBVA CODESPA MICROFINANZAS	ES0113955035	EUR	2	|f_es_0014|f_es_BMF|	f	77259	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113955035||es||False	f	t	t
BBVA FON-PLAZO 2014 C	ES0113823001	EUR	2	|f_es_0014|f_es_BMF|	f	77350	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113823001||es||False	f	t	t
BBVA GESTION CORTO PLAZO	ES0114207030	EUR	2	|f_es_0014|f_es_BMF|	f	77351	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114207030||es||False	f	t	t
BBVA GESTION PROTECCION	ES0114097035	EUR	2	|f_es_0014|f_es_BMF|	f	77357	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114097035||es||False	f	t	t
BBVA INFLACION II	ES0113553004	EUR	2	|f_es_0014|f_es_BMF|	f	77358	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113553004||es||False	f	t	t
BBVA INVERSION EUROPA	ES0113554002	EUR	2	|f_es_0014|f_es_BMF|	f	77359	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113554002||es||False	f	t	t
BBVA OPORTUNIDAD GEOGRAFICA GARAN.II	ES0184826032	EUR	2	|f_es_0014|f_es_BMF|	f	77360	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0184826032||es||False	f	t	t
BBVA FON-PLAZO 2011	ES0114383039	EUR	2	|f_es_0014|f_es_BMF|	f	77448	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114383039||es||False	f	t	t
BBVA 100 IBEX POSITIVO III	ES0133760035	EUR	2	|f_es_0014|f_es_BMF|	f	77449	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133760035||es||False	f	t	t
BBVA PLAN RENTAS 2011	ES0114417035	EUR	2	|f_es_0014|f_es_BMF|	f	77450	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114417035||es||False	f	t	t
BBVA 110 IBEX	ES0113953030	EUR	2	|f_es_0014|f_es_BMF|	f	77471	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113953030||es||False	f	t	t
BBVA 110 IBEX II	ES0113855037	EUR	2	|f_es_0014|f_es_BMF|	f	77473	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113855037||es||False	f	t	t
BBVA & PARTNERS RETORNO ABSOLUTO	ES0115159032	EUR	2	|f_es_0014|f_es_BMF|	f	77480	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0115159032||es||False	f	t	t
BBVA 4 X 3	ES0113535001	EUR	2	|f_es_0014|f_es_BMF|	f	77523	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113535001||es||False	f	t	t
BBVA 4 X 3 II	ES0113455036	EUR	2	|f_es_0014|f_es_BMF|	f	77526	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113455036||es||False	f	t	t
BBVA 5X5 INDICES	ES0113817003	EUR	2	|f_es_0014|f_es_BMF|	f	77539	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113817003||es||False	f	t	t
BBVA ACCION EUROPA II, FI	ES0110187038	EUR	2	|f_es_0014|f_es_BMF|	f	77542	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110187038||es||False	f	t	t
BBVA FON-PLAZO 2011 B	ES0113954038	EUR	2	|f_es_0014|f_es_BMF|	f	77549	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113954038||es||False	f	t	t
BBVA ACCION EUROPA, FI	ES0114168034	EUR	2	|f_es_0014|f_es_BMF|	f	77573	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114168034||es||False	f	t	t
BBVA ACTIVOS FONDTESORO	ES0113200036	EUR	2	|f_es_0014|f_es_BMF|	f	77575	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113200036||es||False	f	t	t
BBVA AHORRO	ES0110108034	EUR	2	|f_es_0014|f_es_BMF|	f	77576	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110108034||es||False	f	t	t
BBVA AHORRO CORTO PLAZO II	ES0110131036	EUR	2	|f_es_0014|f_es_BMF|	f	77592	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110131036||es||False	f	t	t
BBVA CONSOLIDA GARANTIZADO II	ES0133762031	EUR	2	|f_es_0014|f_es_BMF|	f	77600	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133762031||es||False	f	t	t
BBVA AHORRO CORTO PLAZO III	ES0145926038	EUR	2	|f_es_0014|f_es_BMF|	f	77601	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0145926038||es||False	f	t	t
BBVA BOLSA DESARROLLO SOSTENIGLE	ES0125459034	EUR	2	|f_es_0014|f_es_BMF|	f	77630	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125459034||es||False	f	t	t
BBVA BOLSA EMERGENTES	ES0110116037	EUR	2	|f_es_0014|f_es_BMF|	f	77631	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110116037||es||False	f	t	t
BBVA BOLSA EURO	ES0110101039	EUR	2	|f_es_0014|f_es_BMF|	f	77632	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110101039||es||False	f	t	t
BBVA BOLSA EUROPA	ES0114371034	EUR	2	|f_es_0014|f_es_BMF|	f	77633	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114371034||es||False	f	t	t
BBVA BOLSA EUROPA FINANZAS I	ES0114277033	EUR	2	|f_es_0014|f_es_BMF|	f	77649	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114277033||es||False	f	t	t
BBVA BOLSA INDICE EURO	ES0110098037	EUR	2	|f_es_0014|f_es_BMF|	f	77656	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110098037||es||False	f	t	t
BBVA BOLSA INDICE USA (CUBIERTO)	ES0113925038	EUR	2	|f_es_0014|f_es_BMF|	f	77658	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113925038||es||False	f	t	t
BBVA BOLSA INTERNACIONAL MF CUBI	ES0141754038	EUR	2	|f_es_0014|f_es_BMF|	f	77663	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0141754038||es||False	f	t	t
BBVA BOLSA JAPON	ES0147634036	EUR	2	|f_es_0014|f_es_BMF|	f	77664	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147634036||es||False	f	t	t
BBVA BOLSA PLAN DIVIDENDO	ES0113536009	EUR	2	|f_es_0014|f_es_BMF|	f	77677	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113536009||es||False	f	t	t
BBVA BOLSA PLUS	ES0142451030	EUR	2	|f_es_0014|f_es_BMF|	f	77678	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142451030||es||False	f	t	t
BBVA BOLSA TECNOLOG.Y TELECOM.	ES0147711032	EUR	2	|f_es_0014|f_es_BMF|	f	77683	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147711032||es||False	f	t	t
BBVA BOLSA USA	ES0110122035	EUR	2	|f_es_0014|f_es_BMF|	f	77684	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110122035||es||False	f	t	t
BBVA BONO 2008 F	ES0113819009	EUR	2	|f_es_0014|f_es_BMF|	f	77686	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113819009||es||False	f	t	t
BBVA BONO 2010	ES0114389036	EUR	2	|f_es_0014|f_es_BMF|	f	77691	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114389036||es||False	f	t	t
BBVA BONO 2011	ES0114364039	EUR	2	|f_es_0014|f_es_BMF|	f	77693	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114364039||es||False	f	t	t
BBVA BONO FON-PLAZO 2009 C	ES0113927000	EUR	2	|f_es_0014|f_es_BMF|	f	77701	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113927000||es||False	f	t	t
BBVA BONOS 2014	ES0113277000	EUR	2	|f_es_0014|f_es_BMF|	f	77711	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113277000||es||False	f	t	t
BBVA BONOS AHORRO PLUS II	ES0114452032	EUR	2	|f_es_0014|f_es_BMF|	f	77724	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114452032||es||False	f	t	t
BBVA BONOS CASH	ES0113276002	EUR	2	|f_es_0014|f_es_BMF|	f	77740	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113276002||es||False	f	t	t
BBVA BONOS CORE BP	ES0114239033	EUR	2	|f_es_0014|f_es_BMF|	f	77770	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114239033||es||False	f	t	t
BBVA BONOS CORP. LARGO PLAZO	ES0114205034	EUR	2	|f_es_0014|f_es_BMF|	f	77772	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114205034||es||False	f	t	t
BBVA BONOS CORPORATIVOS 2011	ES0113522009	EUR	2	|f_es_0014|f_es_BMF|	f	77773	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113522009||es||False	f	t	t
BBVA BONOS CORPORATIVOS FLOTANTES	ES0113278008	EUR	2	|f_es_0014|f_es_BMF|	f	77785	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113278008||es||False	f	t	t
BBVA ESTRUCTURADO FINANZAS BP	ES0113821005	EUR	2	|f_es_0014|f_es_BMF|	f	77796	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113821005||es||False	f	t	t
BBVA ESTRUCTURADO TELECOM. II BP	ES0113822003	EUR	2	|f_es_0014|f_es_BMF|	f	77797	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113822003||es||False	f	t	t
BBVA EUROPA GARANIZADO II	ES0114094032	EUR	2	|f_es_0014|f_es_BMF|	f	77798	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114094032||es||False	f	t	t
BBVA EUROPA GARANTIZADO	ES0142443037	EUR	2	|f_es_0014|f_es_BMF|	f	77799	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142443037||es||False	f	t	t
BBVA BONOS CORTO PLAZO	ES0113101036	EUR	2	|f_es_0014|f_es_BMF|	f	77813	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113101036||es||False	f	t	t
BBVA BONOS CORTO PLAZO GOBIERNO	ES0113752002	EUR	2	|f_es_0014|f_es_BMF|	f	77814	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113752002||es||False	f	t	t
BBVA BONOS DURACION	ES0114487038	EUR	2	|f_es_0014|f_es_BMF|	f	77815	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114487038||es||False	f	t	t
BBVA FON-PLAZO 2014 D	ES0138704038	EUR	2	|f_es_0014|f_es_BMF|	f	77863	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138704038||es||False	f	t	t
BBVA FONDPLAZO DOBLE-BEX	ES0110167030	EUR	2	|f_es_0014|f_es_BMF|	f	77869	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110167030||es||False	f	t	t
BBVA GARAN.TOP DIVIDENDO 100	ES0145924033	EUR	2	|f_es_0014|f_es_BMF|	f	77871	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0145924033||es||False	f	t	t
BBVA GESTION CONSERVADORA	ES0110178037	EUR	2	|f_es_0014|f_es_BMF|	f	77872	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110178037||es||False	f	t	t
BBVA GARANTIZADO DOBLE 10	ES0114096037	EUR	2	|f_es_0014|f_es_BMF|	f	77873	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114096037||es||False	f	t	t
BBVA BONOS DURACION FLEXIBLE	ES0113203030	EUR	2	|f_es_0014|f_es_BMF|	f	77905	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113203030||es||False	f	t	t
BBVA PLAN RENTAS 2008 D	ES0147709036	EUR	2	|f_es_0014|f_es_BMF|	f	77907	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147709036||es||False	f	t	t
BBVA PLAN RENTAS 2009	ES0125465031	EUR	2	|f_es_0014|f_es_BMF|	f	77912	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0125465031||es||False	f	t	t
BBVA BONOS INTERNACIONAL FLEXIBLE	ES0110174036	EUR	2	|f_es_0014|f_es_BMF|	f	77957	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110174036||es||False	f	t	t
BBVA CESTA GLOBAL	ES0114300033	EUR	2	|f_es_0014|f_es_BMF|	f	77959	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114300033||es||False	f	t	t
BBVA CESTA GLOBAL II	ES0114372032	EUR	2	|f_es_0014|f_es_BMF|	f	77962	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114372032||es||False	f	t	t
BBVA PLAN RENTAS 2009 C	ES0109998031	EUR	2	|f_es_0014|f_es_BMF|	f	77967	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109998031||es||False	f	t	t
BBVA PLAN RENTAS 2010	ES0110000033	EUR	2	|f_es_0014|f_es_BMF|	f	77968	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110000033||es||False	f	t	t
BBVA PLAN RENTAS 2010 B	ES0116856032	EUR	2	|f_es_0014|f_es_BMF|	f	77971	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116856032||es||False	f	t	t
BBVA PLAN RENTAS 2010 C	ES0108930035	EUR	2	|f_es_0014|f_es_BMF|	f	77972	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108930035||es||False	f	t	t
BBVA PLAN RENTAS 2010 D	ES0108931033	EUR	2	|f_es_0014|f_es_BMF|	f	77977	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108931033||es||False	f	t	t
BBVA DJ EUROSTOXX 50 4 PLUS C	ES0138513033	EUR	2	|f_es_0014|f_es_BMF|	f	78056	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138513033||es||False	f	t	t
BBVA CONSOLIDADO GARANTIZADO	ES0110123033	EUR	2	|f_es_0014|f_es_BMF|	f	78060	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110123033||es||False	f	t	t
BBVA DINERO PLUS	ES0170925038	EUR	2	|f_es_0014|f_es_BMF|	f	78071	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0170925038||es||False	f	t	t
BBVA DJ EUROSTOXX 50 4 PLUS	ES0113957031	EUR	2	|f_es_0014|f_es_BMF|	f	78073	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113957031||es||False	f	t	t
BBVA DJ EUROSTOXX 50 4 PLUS A	ES0110079037	EUR	2	|f_es_0014|f_es_BMF|	f	78074	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110079037||es||False	f	t	t
BBVA DJ EUROSTOXX 50 4 PLUS B	ES0109997033	EUR	2	|f_es_0014|f_es_BMF|	f	78076	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0109997033||es||False	f	t	t
A.S.C. GLOBAL	ES0114223037	EUR	2	|f_es_0014|f_es_BMF|	f	78093	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114223037||es||False	f	t	t
BBVA EUROPA GARANTIZADO III	ES0114188032	EUR	2	|f_es_0014|f_es_BMF|	f	78097	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114188032||es||False	f	t	t
BBVA EUROPA OPTIMO	ES0113458030	EUR	2	|f_es_0014|f_es_BMF|	f	78099	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113458030||es||False	f	t	t
BBVA EVOLUCION V, 5	ES0113555009	EUR	2	|f_es_0014|f_es_BMF|	f	78105	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113555009||es||False	f	t	t
BBVA EXTRA 5 II GARANTIZADO	ES0145928034	EUR	2	|f_es_0014|f_es_BMF|	f	78106	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0145928034||es||False	f	t	t
BBVA GESTION DECIDIDA	ES0113996039	EUR	2	|f_es_0014|f_es_BMF|	f	78145	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113996039||es||False	f	t	t
BBVA PLAN RENTAS 2010 E	ES0108932031	EUR	2	|f_es_0014|f_es_BMF|	f	78146	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0108932031||es||False	f	t	t
BBVA PLAN RENTAS 2010 F	ES0169986033	EUR	2	|f_es_0014|f_es_BMF|	f	78147	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169986033||es||False	f	t	t
BBVA PLAN RENTAS 2007 G	ES0114132030	EUR	2	|f_es_0014|f_es_BMF|	f	78198	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114132030||es||False	f	t	t
BBVA PLAN RENTAS 2010 G	ES0169987031	EUR	2	|f_es_0014|f_es_BMF|	f	78201	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169987031||es||False	f	t	t
BBVA PLAN RENTAS 2011 B	ES0138490034	EUR	2	|f_es_0014|f_es_BMF|	f	78202	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138490034||es||False	f	t	t
BBVA PLAN RENTAS 2011 C	ES0169988039	EUR	2	|f_es_0014|f_es_BMF|	f	78203	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169988039||es||False	f	t	t
BBVA PLAN RENTAS 2011 D	ES0147629036	EUR	2	|f_es_0014|f_es_BMF|	f	78204	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0147629036||es||False	f	t	t
BBVA RENTA FIJA LARGO 6	ES0138889037	EUR	2	|f_es_0014|f_es_BMF|	f	78242	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0138889037||es||False	f	t	t
BBVA RENTABILIDAD 2012	ES0169992007	EUR	2	|f_es_0014|f_es_BMF|	f	78249	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0169992007||es||False	f	t	t
BBVA RENTAS 2009 B	ES0114146030	EUR	2	|f_es_0014|f_es_BMF|	f	78250	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114146030||es||False	f	t	t
BBVA SELECCION CONSUMO BP	ES0116860000	EUR	2	|f_es_0014|f_es_BMF|	f	78286	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116860000||es||False	f	t	t
BBVA SELECCION EMPRESAS BP	ES0116859002	EUR	2	|f_es_0014|f_es_BMF|	f	78287	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116859002||es||False	f	t	t
BBVA SOLIDARIDAD	ES0114279039	EUR	2	|f_es_0014|f_es_BMF|	f	78288	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114279039||es||False	f	t	t
BBVA SOLIDEZ BP	ES0110006006	EUR	2	|f_es_0014|f_es_BMF|	f	78293	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110006006||es||False	f	t	t
BBVA SOLIDEZ II BP	ES0110007004	EUR	2	|f_es_0014|f_es_BMF|	f	78296	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110007004||es||False	f	t	t
BBVA TOP 14 GARANTIZADO	ES0114151006	EUR	2	|f_es_0014|f_es_BMF|	f	78300	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114151006||es||False	f	t	t
BBVA FON-PLAZO 2014	ES0142445008	EUR	2	|f_es_0014|f_es_BMF|	f	78700	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0142445008||es||False	f	t	t
BBVA PLAN RENTAS 2011 E	ES0133764037	EUR	2	|f_es_0014|f_es_BMF|	f	78702	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0133764037||es||False	f	t	t
BBVA RENTA FIJA CORTO PLUS	ES0176232033	EUR	2	|f_es_0014|f_es_BMF|	f	78707	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0176232033||es||False	f	t	t
BBVA SOLIDEZ VIII BP	ES0110011006	EUR	2	|f_es_0014|f_es_BMF|	f	78735	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0110011006||es||False	f	t	t
BBVA BONOS DOLAR CORTO PLAZO	ES0114341037	EUR	2	|f_es_0014|f_es_BMF|	f	78888	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114341037||es||False	f	t	t
BBVA OPCION 10X3 BP	ES0114229000	EUR	2	|f_es_0014|f_es_BMF|	f	78992	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114229000||es||False	f	t	t
BBVA OPORTUNIDAD EUROPA BP	ES0114210000	EUR	2	|f_es_0014|f_es_BMF|	f	78996	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114210000||es||False	f	t	t
BBVA PLAN RENTAS 2012 D	ES0113427035	EUR	2	|f_es_0014|f_es_BMF|	f	79001	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0113427035||es||False	f	t	t
BBVA PLAN RENTAS 2012 E	ES0116855034	EUR	2	|f_es_0014|f_es_BMF|	f	79002	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0116855034||es||False	f	t	t
QUALITY VALOR	ES0114122031	EUR	2	|f_es_0014|f_es_BMF|	f	81413	\N	\N	\N	\N	100	c	0	1	\N	{2}	\N	ES0114122031||es||False	f	t	t
BNP Paribas Alternativo Dvr IICIICIL Acc	ES0150039008	EUR	2	|f_es_BMF|	f	74842					100	c	0	1	None	{2}	\N	ES0150039008||None||False	f	t	t
BNP Paribas Selección Hedge IICIICIL	ES0125474009	EUR	2	|f_es_BMF|	f	74857					100	c	0	1	None	{2}	\N	ES0125474009||None||False	f	t	t
ENDESA S.A.	ES0130670112	EUR	1	|IBEX|MERCADOCONTINUO|	f	78880					100	c	0	1	ELE.MC	{1}	{3}	MC#ES0130670112||es||False	f	t	t
Biogen Idec Inc.	US09062X1037	USD	1	|NASDAQ100|SP500|	f	77580					100	c	0	2	BIIB	{1}	{3}	BIIB||us||False	f	t	t
H&R Block Inc.		USD	1	|SP500|	f	75420					100	c	0	2	HRB	{1}	{3}	NYSE#HRB||us||False	f	t	t
BMC Software Inc.	US0559211000	USD	1	|NASDAQ100|SP500|	f	75741					100	c	0	2	BMC	{1}	{3}	BMC||us||False	f	t	t
Boeing Company	US0970231058	USD	1	|SP500|	f	79465					100	c	0	2	BA	{1}	{3}	NYSE#BA||us||False	f	t	t
BorgWarner Inc.		USD	1	|SP500|	f	78270					100	c	0	2	BWA	{1}	{3}	NYSE#BWA||us||False	f	t	t
Becton Dickinson & Co.		USD	1	|SP500|	f	77949					100	c	0	2	BDX	{1}	{3}	NYSE#BDX||us||False	f	t	t
Bristol-Myers Squibb Co.		USD	1	|SP500|	f	78903					100	c	0	2	BMY	{1}	{3}	NYSE#BMY||us||False	f	t	t
Broadcom Corporation	US1113201073	USD	1	|NASDAQ100|SP500|	f	76527					100	c	0	2	BRCM	{1}	{3}	BRCM||us||False	f	t	t
Caja Madrid Europa Plus FI	ES0157086036	EUR	2	|f_es_BMF|	f	74913					100	c	0	1	None	\N	\N	ES0157086036||None||False	f	t	t
Caja Madrid Garantía 1 Año FI	ES0113254009	EUR	2	|f_es_BMF|	f	74915					100	c	0	1	None	\N	\N	ES0113254009||None||False	f	t	t
Cajaburgos Garantizado Int. FI	ES0122711031	EUR	2	|f_es_BMF|	f	74916					100	c	0	1	None	\N	\N	ES0122711031||None||False	f	t	t
Cajarioja Garantizado 1 FI	ES0114548037	EUR	2	|f_es_BMF|	f	74917					100	c	0	1	None	\N	\N	ES0114548037||None||False	f	t	t
C.H. Robinson Worldwide, Inc.	US12541W2098	USD	1	|NASDAQ100|SP500|	f	77546					100	c	0	2	CHRW	{1}	{3}	CHRW||us||False	f	t	t
Cablevision Systems Corp.		USD	1	|SP500|	f	76258					100	c	0	2	CVC	{1}	{3}	NYSE#CVC||us||False	f	t	t
Cameron International Corp.		USD	1	|SP500|	f	74872					100	c	0	2	CAM	{1}	{3}	NYSE#CAM||us||False	f	t	t
Campbell Soup Co.		USD	1	|SP500|	f	78372					100	c	0	2	CPB	{1}	{3}	NYSE#CPB||us||False	f	t	t
Iberia	ES0147200036	EUR	1		f	76914					100	c	0	1	None	\N	\N	IBLA.MC||es||False	t	t	t
Cardinal Health Inc.		USD	1	|SP500|	f	75322					100	c	0	2	CAH	{1}	{3}	NYSE#CAH||us||False	f	t	t
CareFusion Corporation		USD	1	|SP500|	f	76691					100	c	0	2	CFN	{1}	{3}	NYSE#CFN||us||False	f	t	t
Carnival Corp.		USD	1	|SP500|	f	79171					100	c	0	2	CCL	{1}	{3}	NYSE#CCL||us||False	f	t	t
Caterpillar Inc.	US1491231015	USD	1	|SP500|	f	75278					100	c	0	2	CAT	{1}	{3}	NYSE#CAT||us||False	f	t	t
CBRE Group Inc. Cl A		USD	1	|SP500|	f	76167					100	c	0	2	CBG	{1}	{3}	NYSE#CBG||us||False	f	t	t
CBS Corp. Cl B		USD	1	|SP500|	f	74843					100	c	0	2	CBS	{1}	{3}	NYSE#CBS||us||False	f	t	t
Celgene Corporation	US1510201049	USD	1	|NASDAQ100|SP500|	f	77456					100	c	0	2	CELG	{1}	{3}	CELG||us||False	f	t	t
CenterPoint Energy Inc.		USD	1	|SP500|	f	76280					100	c	0	2	CNP	{1}	{3}	NYSE#CNP||us||False	f	t	t
EUROPAC	ES0168561019	EUR	1	|MERCADOCONTINUO|	f	78867					100	c	0	1	None	\N	\N	MC#ES0168561019||es||False	f	t	t
Compañía Levantina. Edificación de obras públicas. CLEOP	ES0158300410	EUR	1	|MERCADOCONTINUO|	f	80846					100	c	0	1	None	\N	\N	MC#ES0158300410||es||False	f	t	t
CIE AUTOMOTIVE S.A.	ES0105630315	EUR	1	|MERCADOCONTINUO|	f	78451					100	c	0	1	None	\N	\N	MC#ES0105630315||es||False	f	t	t
Alcatel Lucent	FR0000130007	EUR	1	|CAC|	f	74895					100	c	0	3	ALU.PA	{1}	{3}	ALU.PA||fr||False	f	t	t
AC Capital 9 FI	ES0152281038	EUR	2	|f_es_BMF|	f	74743					100	c	0	1	None	\N	\N	ES0152281038||None||False	f	t	t
Caixatarragona Bolsa 35 FI	ES0115067037	EUR	2	|f_es_BMF|	f	74902					100	c	0	1	None	{2}	\N	ES0115067037||None||False	f	t	t
Unifond 2014-IV FI	ES0180908008	EUR	2	|f_es_BMF|	f	81375					100	c	0	1	None	{2}	\N	ES0180908008||None||False	f	t	t
BBVA 100 Ibex Positivo FI	ES0114169032	EUR	2	|f_es_BMF|	f	74776					100	c	0	1	None	{2}	\N	ES0114169032||None||False	f	t	t
Unnim Garantit 7 FI	ES0125132003	EUR	2	|f_es_BMF|	f	81578					100	c	0	1	None	{2}	\N	ES0125132003||None||False	f	t	t
AC INVERSION FI	ES0107367007	EUR	2	|f_es_BMF|	f	74762					100	c	0	1	None	{2}	\N	ES0107367007||None||False	f	t	t
ARCANO EUROPEAN INCOME F. FIL A1 	ES0109924003	EUR	2	|f_es_BMF|	f	74810					100	c	0	1	None	{2}	\N	ES0109924003||None||False	f	t	t
BBVA Gestión Proyecto 2012 FI	ES0114144035	EUR	2	|f_es_BMF|	f	74813					100	c	0	1	None	{2}	\N	ES0114144035||None||False	f	t	t
BBVA 100 Ibex Positivo II FI	ES0114282033	EUR	2	|f_es_BMF|	f	74777					100	c	0	1	None	{2}	\N	ES0114282033||None||False	f	t	t
BBVA Plan Rentas 2010 I FI	ES0110082031	EUR	2	|f_es_BMF|	f	74835					100	c	0	1	None	{2}	\N	ES0110082031||None||False	f	t	t
BBVA Plan Rentas 2010 J FI	ES0147632030	EUR	2	|f_es_BMF|	f	74830					100	c	0	1	None	{2}	\N	ES0147632030||None||False	f	t	t
BBVA Plan Rentas 2010 L FI	ES0114136031	EUR	2	|f_es_BMF|	f	74831					100	c	0	1	None	{2}	\N	ES0114136031||None||False	f	t	t
AHOLD KON	NL0006033250	EUR	1		f	74791					100	c	0	12	AH.AS	{1}	{3}	AH.AS||None||False	f	t	t
SACYR VALLEHERMOSO	ES0182870214	EUR	1	|IBEX|MERCADOCONTINUO|	f	81534					100	c	0	1	SYV.MC	{1}	{3}	MC#ES0182870214||es||False	f	t	t
ARCANO EUROPEAN INC.CL D1	ES0109924029	EUR	2	|f_es_BMF|	f	74811					100	c	0	1	None	{2}	\N	ES0109924029||None||False	f	t	t
BBVA Multifondo Dinámico FI	ES0114373030	EUR	2	|f_es_BMF|	f	74829					100	c	0	1	None	{2}	\N	ES0114373030||None||False	f	t	t
Unicredit		EUR	1	|EUROSTOXX|	f	81087					100	c	0	6	UCG.MI	{1}	{3}	UCG.MI||it||False	f	t	t
BBVA Gestión Proyecto 2010 FI	ES0114208038	EUR	2	|f_es_0014|f_es_BMF|	f	74836					100	c	0	1	None	{2}	\N	ES0114208038||None||False	f	t	t
BBVA Plan Rentas 2009 D FI	ES0109999039	EUR	2	|f_es_BMF|	f	74834					100	c	0	1	None	{2}	\N	ES0109999039||None||False	f	t	t
BNP Paribas Inversión FI	ES0125473035	EUR	2	|f_es_BMF|	f	74861					100	c	0	1	None	{2}	\N	ES0125473035||None||False	f	t	t
Bono Alemán a 10 años		None	7		t	74801					100	c	0	5	None	{3}	\N	BUND_ALEMAN||de||False	f	t	t
AMUNDI MULTIESTRATEGIA ALT.	ES0118556002	EUR	2	|f_es_BMF|	f	74863					100	c	0	1	None	{2}	\N	ES0118556002||None||False	f	t	t
Bono Español a 10 años		None	7		t	74803					100	c	0	1	None	{3}	\N	BUND_ESPAÑOL||es||False	f	t	t
Diferencial Bono Alemán-Español a 10 años		None	7		t	74804					100	c	0	1	None	{3}	\N	BUND_DIFERENCIALESPAÑOL||es||False	f	t	t
BNP Paribas Protected Plus FI	ES0118551037	EUR	2	|f_es_BMF|	f	74862					100	c	0	1	None	{2}	\N	ES0118551037||None||False	f	t	t
BBVA Bonos Corto Plus Empresas FI	ES0113193033	EUR	2	|f_es_BMF|	f	74783					100	c	0	1	None	{2}	\N	ES0113193033||None||False	f	t	t
Yelsen EEUU Valor FI	ES0184763037	EUR	2	|f_es_BMF|	f	74772					100	c	0	1	None	{2}	\N	ES0184763037||None||False	f	t	t
STMICROELECTRONICS	NL0000226223	EUR	1	|CAC|EURONEXT|	f	74853					100	c	0	3	None	\N	\N	EURONEXT#NL0000226223||fr||False	f	t	t
BBVA 4-100 Ibex FI	ES0114203039	EUR	2	|f_es_BMF|	f	74779					100	c	0	1	None	{2}	\N	ES0114203039||None||False	f	t	t
BBVA Gestion Corto Plazo II FI	ES0114228036	EUR	2	|f_es_BMF|	f	74828					100	c	0	1	None	{2}	\N	ES0114228036||None||False	f	t	t
BBVA Bolsa Biofarma FI	ES0145923035	EUR	2	|f_es_BMF|	f	74781					100	c	0	1	None	{2}	\N	ES0145923035||None||False	f	t	t
PSI 20		EUR	3		t	78127					100	c	0	9	^PSI20	{1}	\N	PSI20.NX||pt||False	f	t	t
EADS	NL0000235190	EUR	1	|CAC|EURONEXT|	f	79008					100	c	0	3	None	\N	\N	EURONEXT#NL0000235190||fr||False	f	t	t
K+S Aktiengesellschaft	DE000KSAG888	EUR	1	|DAX|DEUTSCHEBOERSE|	f	74844					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE000KSAG888||de||False	f	t	t
ESSILOR INTERNATIONAL	FR0000121667	EUR	1	|CAC|EURONEXT|	f	79699					100	c	0	3	None	\N	\N	EURONEXT#FR0000121667||fr||False	f	t	t
CAI 100 Garantizado IV FI	ES0115105035	EUR	2	|f_es_BMF|	f	74877					100	c	0	1	None	{2}	\N	ES0115105035||None||False	f	t	t
CCM Consolidación Máxima FI	ES0116983034	EUR	2	|f_es_BMF|	f	74865					100	c	0	1	None	{2}	\N	ES0116983034||None||False	f	t	t
CAI Garantizado Súper 7 II FI	ES0115079032	EUR	2	|f_es_BMF|	f	74880					100	c	0	1	None	{2}	\N	ES0115079032||None||False	f	t	t
Caixa Catalunya Borsa 2 FI	ES0101334037	EUR	2	|f_es_BMF|	f	74883					100	c	0	1	None	{2}	\N	ES0101334037||None||False	f	t	t
Caixasabadell Protecció III FI	ES0169077031	EUR	2	|f_es_BMF|	f	74885					100	c	0	1	None	{2}	\N	ES0169077031||None||False	f	t	t
CAI Garantizado Eurostoxx FI	ES0119481036	EUR	2	|f_es_BMF|	f	74879					100	c	0	1	None	{2}	\N	ES0119481036||None||False	f	t	t
Caixasabadell Protecció IV FI	ES0169078039	EUR	2	|f_es_BMF|	f	74897					100	c	0	1	None	{2}	\N	ES0169078039||None||False	f	t	t
LVMH	FR0000121014	EUR	1	|CAC|EURONEXT|EUROSTOXX|	f	80229					100	c	0	3	None	\N	\N	EURONEXT#FR0000121014||fr||False	f	t	t
Caixatarragona Inversió Curt Termini FI	ES0177951037	EUR	2	|f_es_BMF|	f	74903					100	c	0	1	None	{2}	\N	ES0177951037||None||False	f	t	t
SOCIETE GENERALE	FR0000130809	EUR	1	|CAC|EURONEXT|EUROSTOXX|	t	80093					100	c	0	3	GLE.PA	{1}	{3}	EURONEXT#FR0000130809||fr||False	f	t	t
CAIXATARRAGONA MIXT IPC	ES0178002038	EUR	2	|f_es_BMF|	f	74912					100	c	0	1	None	\N	\N	ES0178002038||None||False	f	t	t
Caja Madrid Excellence Gar. FI	ES0113253001	EUR	2	|f_es_BMF|	f	74914					100	c	0	1	None	\N	\N	ES0113253001||None||False	f	t	t
Cantabria Crecimiento Gar. FI	ES0115905038	EUR	2	|f_es_BMF|	f	74970					100	c	0	1	None	{2}	\N	ES0115905038||None||False	f	t	t
Peugeot	FR0000121501	EUR	1	|CAC|	t	75037					100	c	0	3	UG.PA	{1}	{3}	UG.PA||fr||False	f	t	t
Volkswagen AG St	DE0007664005	EUR	1	|DAX|DEUTSCHEBOERSE|EUROSTOXX|	f	74993					100	c	0	5	VOW.DE	{1}	{3}	DEUTSCHEBOERSE#DE0007664005||de||False	f	t	t
MAN SE St	DE0005937007	EUR	1	|DAX|DEUTSCHEBOERSE|	f	81294					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE0005937007||de||False	f	t	t
Avalonbay Communities Inc.		USD	1	|SP500|	f	74873					100	c	0	2	AVB	{1}	{3}	NYSE#AVB||us||False	f	t	t
Accenture PLC Cl A	BMG1150G1116	USD	1	|SP500|	t	79256					100	c	0	2	ACN	{1}	{3}	NYSE#ACN||us||False	f	t	t
American Electric Power Co. Inc.		USD	1	|SP500|	f	75973					100	c	0	2	AEP	{1}	{3}	NYSE#AEP||us||False	f	t	t
Cabot Corp.		USD	1	|SP500|	f	76720					100	c	0	2	CBT	{1}	{3}	NYSE#CBT||us||False	f	t	t
Autodesk, Inc.	US0527691069	USD	1	|NASDAQ100|SP500|	f	76082					100	c	0	2	ADSK	{1}	{3}	ADSK||us||False	f	t	t
CREDIT AGRICOLE	FR0000045072	EUR	1	|CAC|EURONEXT|	f	76268					100	c	0	3	None	\N	\N	EURONEXT#FR0000045072||fr||False	f	t	t
Apollo Group Inc.	US0376041051	USD	1	|NASDAQ100|SP500|	f	76217					100	c	0	2	APOL	{1}	{3}	APOL||us||False	f	t	t
Suez Environnement Company		EUR	1		f	76384					100	c	0	3	None	\N	\N	SEV.PA||fr||False	f	t	t
Anadarko Petroleum Corp.		USD	1	|SP500|	f	76738					100	c	0	2	APC	{1}	{3}	NYSE#APC||us||False	f	t	t
Abbott Laboratories	US0028241000	USD	1	|SP500|	f	76790					100	c	0	2	ABT	{1}	{3}	NYSE#ABT||us||False	f	t	t
Anheuser-Busch InBev N.V.		USD	1		f	76821					100	c	0	2	None	\N	\N	NYSE#BUD||us||False	f	t	t
Air Products & Chemicals Inc.		USD	1	|SP500|	f	76897					100	c	0	2	APD	{1}	{3}	NYSE#APD||us||False	f	t	t
Allegheny Technologies Inc.		USD	1	|SP500|	f	76981					100	c	0	2	ATI	{1}	{3}	NYSE#ATI||us||False	f	t	t
Best Buy Co. Inc.		USD	1	|SP500|	f	78278					100	c	0	2	BBY	{1}	{3}	NYSE#BBY||us||False	f	t	t
Airgas Inc.	US0093631028	USD	1	|SP500|	f	77134					100	c	0	2	ARG	{1}	{3}	NYSE#ARG||us||False	f	t	t
American International Group Inc.		USD	1	|SP500|	f	77376					100	c	0	2	None	\N	\N	NYSE#AIG||us||False	f	t	t
Apartment Investment & Management Co.		USD	1	|SP500|	f	77301					100	c	0	2	AIV	{1}	{3}	NYSE#AIV||us||False	f	t	t
Automatic Data Processing, Inc.	US0530151036	USD	1	|NASDAQ100|SP500|	f	77430					100	c	0	2	ADP	{1}	{3}	ADP||us||False	f	t	t
Xilinx Inc.	US9839191015	USD	1	|NASDAQ100|SP500|	f	77605					100	c	0	2	XLNX	{1}	{3}	XLNX||us||False	f	t	t
TOTAL	FR0000120271	EUR	1	|CAC|EURONEXT|EUROSTOXX|	f	78017					100	c	0	3	FP.PA	{1}	{3}	EURONEXT#FR0000120271||fr||False	f	t	t
VIVENDI	FR0000127771	EUR	1	|CAC|EURONEXT|EUROSTOXX|	t	78020					100	c	0	3	VIV.PA	{1}	{3}	EURONEXT#FR0000127771||fr||False	f	t	t
AMADEUS	ES0109067019	EUR	1	|IBEX|MERCADOCONTINUO|	t	78334					100	c	0	1	AMS.MC	{1}	{3}	MC#ES0109067019||es||False	f	t	t
LEGRAND	FR0010307819	EUR	1	|CAC|EURONEXT|	f	78924					100	c	0	3	None	\N	\N	EURONEXT#FR0010307819||fr||False	f	t	t
FCC	ES0122060314	EUR	1	|IBEX|MERCADOCONTINUO|	f	78907					100	c	0	1	FCC.MC	{1}	{3}	MC#ES0122060314||es||False	f	t	t
BNP PARIBAS ACT.A	FR0000131104	EUR	1	|CAC|EURONEXT|EUROSTOXX|	t	78967					100	c	0	3	BNP.PA	{1}	{3}	EURONEXT#FR0000131104||fr||False	f	t	t
Deutsche Post AG	DE0005552004	EUR	1	|DAX|DEUTSCHEBOERSE|	f	79588					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE0005552004||de||False	f	t	t
Deutsche Lufthansa AG	DE0008232125	EUR	1	|DAX|DEUTSCHEBOERSE|	f	79574					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE0008232125||de||False	f	t	t
Infineon Technologies AG	DE0006231004	EUR	1	|DAX|DEUTSCHEBOERSE|	f	80271					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE0006231004||de||False	f	t	t
Münchener Rück AG	DE0008430026	EUR	1	|DAX|DEUTSCHEBOERSE|EUROSTOXX|	f	80407					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE0008430026||de||False	f	t	t
RWE AG St	DE0007037129	EUR	1	|DAX|DEUTSCHEBOERSE|EUROSTOXX|	f	80767					100	c	0	5	RWE.DE	{1}	{3}	DEUTSCHEBOERSE#DE0007037129||de||False	f	t	t
ThyssenKrupp AG	DE0007500001	EUR	1	|DAX|DEUTSCHEBOERSE|	f	81034					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE0007500001||de||False	f	t	t
RWE AG Vz	DE0007037145	EUR	1	|DEUTSCHEBOERSE|	f	80768					100	c	0	5	RWE3.DE	{1}	{3}	DEUTSCHEBOERSE#DE0007037145||de||False	f	t	t
ARCELORMITTAL	LU0323134006	EUR	1	|IBEX|MERCADOCONTINUO|	f	81101					100	c	0	1	MTS.MC	{1}	{3}	MC#LU0323134006||es||False	f	t	t
Henkel AG & Co. KGaA St	DE0006048408	EUR	1	|DAX|DEUTSCHEBOERSE|	f	81267					100	c	0	5	None	\N	\N	DEUTSCHEBOERSE#DE0006048408||de||False	f	t	t
AIR LIQUIDE	FR0000120073	EUR	1	|CAC|EURONEXT|EUROSTOXX|	f	76651					100	c	0	3	AI.PA	{1}	{3}	EURONEXT#FR0000120073||fr||False	f	t	t
UNILEVER	NL0000009355	EUR	1	|EURONEXT|EUROSTOXX|	f	81286					100	c	0	12	UNA.AS	{1}	{3}	EURONEXT#NL0000009355||nl||False	f	t	t
DIA	ES0126775032	EUR	1	|IBEX|MERCADOCONTINUO|	f	81114					100	c	0	1	DIA.MC	{1}	{3}	MC#ES0126775032||es||False	f	t	t
BANCO DE SABADELL	ES0113860A34	EUR	1	|IBEX|MERCADOCONTINUO|	f	81104					100	c	0	1	SAB.MC	{1}	{3}	MC#ES0113860A34||es||False	f	t	t
ACC LBRA ETF	ES0105322004	EUR	4	|MERCADOCONTINUO|	f	81438					100	c	0	1	None	\N	\N	MC#ES0105322004||es||False	f	t	t
Altae Cesta Asiática FI	ES0108848039	EUR	2	|f_es_BMF|	f	74768					100	c	0	1	None	{2}	\N	ES0108848039||None||False	f	t	t
Cantel Medical Corp	US1380981084	USD	1		f	74746					100	c	0	2	CMN	{1}	{3}	CMN||None||False	f	t	t
ORCHESTRA-KAZIBAO	FR0011144302	EUR	1		f	74756					100	c	0	3	None	\N	\N	EURONEXT#FR0011144302||None||False	f	t	t
Beta Alpha Dinámico FI	ES0114641030	EUR	2	|f_es_BMF|	f	74838					100	c	0	1	None	{2}	\N	ES0114641030||None||False	f	t	t
BBVA Ranking Plus FI	ES0116857030	EUR	2	|f_es_0014|f_es_BMF|	f	74837					100	c	0	1	None	{2}	\N	ES0116857030||None||False	f	t	t
Beta Renta FI	ES0114666037	EUR	2	|f_es_BMF|	f	74839					100	c	0	1	None	{2}	\N	ES0114666037||None||False	f	t	t
Beta Valor FI	ES0125931032	EUR	2	|f_es_BMF|	f	74841					100	c	0	1	None	{2}	\N	ES0125931032||None||False	f	t	t
BBVA Bono 2010 B FI	ES0113097036	EUR	2	|f_es_BMF|	f	74782					100	c	0	1	None	{2}	\N	ES0113097036||None||False	f	t	t
BBVA Estructurado Alimentación FI	ES0161364007	EUR	2	|f_es_BMF|	f	74798					100	c	0	1	None	{2}	\N	ES0161364007||None||False	f	t	t
Dow Jones Industrial Average	US2605661048	USD	3		t	78259					100	c	0	2	^DJI	{1}	{3}	^DJI||us||False	f	t	t
Allergan Inc.		USD	1	|SP500|	f	75971					100	c	0	2	AGN	{1}	{3}	NYSE#AGN||us||False	f	t	t
Amazon.com Inc.	US0231351067	USD	1	|NASDAQ100|SP500|	f	76081					100	c	0	2	AMZN	{1}	{3}	AMZN||us||False	f	t	t
ACE Ltd.		USD	1	|SP500|	f	79262					100	c	0	2	ACE	{1}	{3}	NYSE#ACE||us||False	f	t	t
Allstate Corp.		USD	1	|SP500|	f	76264					100	c	0	2	ALL	{1}	{3}	NYSE#ALL||us||False	f	t	t
Amphenol Corp. Cl A		USD	1	|SP500|	f	76603					100	c	0	2	APH	{1}	{3}	NYSE#APH||us||False	f	t	t
Aetna Inc.	US00817Y1082	USD	1	|SP500|	f	76739					100	c	0	2	AET	{1}	{3}	NYSE#AET||us||False	f	t	t
VINCI NV	FR0010994095	EUR	1	|CAC|EURONEXT|EUROSTOXX|	f	77020					100	c	0	3	DG.PA	{1}	{3}	EURONEXT#FR0010994095||fr||False	f	t	t
Apache Corporation		USD	1	|SP500|	f	77211					100	c	0	2	APA	{1}	{3}	NYSE#APA||us||False	f	t	t
AES Corp.		USD	1	|SP500|	f	77384					100	c	0	2	AES	{1}	{3}	NYSE#AES||us||False	f	t	t
Altria Group Inc.		USD	1	|SP500|	f	77344					100	c	0	2	MO	{1}	{3}	NYSE#MO||us||False	f	t	t
Apple Inc.	US0378331005	USD	1	|NASDAQ100|SP500|	f	77578					100	c	0	2	AAPL	{1}	{3}	AAPL||us||False	f	t	t
Adobe Systems Incorporated	US00724F1012	USD	1	|NASDAQ100|SP500|	f	77582					100	c	0	2	ADBE	{1}	{3}	ADBE||us||False	f	t	t
Anheus.-Busch Inbev	BE0003793107	EUR	1	|EUROSTOXX|	f	77627					100	c	0	11	ABI.BR	{1}	{3}	ABI.BR||be||False	f	t	t
Advanced Micro Devices Inc.	US0079031078	USD	1	|SP500|	f	75709					100	c	0	2	AMD	{1}	{3}	NYSE#AMD||us||False	f	t	t
Acorn International Inc.	US0048541058	USD	1		f	80158					100	c	0	2	ATV	{1}	{3}	NYSE#ATV||us||False	f	t	t
Cajasol Rentas Crecientes	ES0174808032	EUR	2	|f_es_BMF|	f	74919					100	c	0	1	None	{2}	\N	ES0174808032||None||False	f	t	t
Caixa Galicia Renta Fija FI	ES0114985031	EUR	2	|f_es_BMF|	f	74884					100	c	0	1	None	{2}	\N	ES0114985031||None||False	f	t	t
Caixasabadell Protecció II FI	ES0169076033	EUR	2	|f_es_BMF|	f	74901					100	c	0	1	None	{2}	\N	ES0169076033||None||False	f	t	t
CAIXA TARRAGONA RF CORTO PLAZO FI	ES0178001030	EUR	2	|f_es_BMF|	f	74909					100	c	0	1	None	{2}	\N	ES0178001030||None||False	f	t	t
Caixatarragona Mixt Europa FI	ES0177996032	GBP	2	|f_es_BMF|	f	74911					100	c	0	1	None	{2}	\N	ES0177996032||None||False	f	t	t
IBEX 35	ES0SI0000005	EUR	3		t	79329					100	c	0	1	^IBEX	{4,1}	{3}	^IBEX||es||False	f	t	t
Commerz Bank	DE0008032004	EUR	1	|DAX|DEUTSCHEBOERSE|	f	75041					100	c	0	5	CBK.DE	{1}	{3}	CBK.DE||None||False	f	f	t
ALTADIS		EUR	1		f	74945					100	c	0	1	None	\N	\N	ALTADIS||es||True	t	f	t
REPSOL YPF	ES0173516115	EUR	1	|EUROSTOXX|IBEX|MERCADOCONTINUO|	t	79360					100	c	0	1	REP.MC	{1}	{3}	MC#ES0173516115||es||False	f	f	t
\.


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

--
-- Data for Name: bolsas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY bolsas (id_bolsas, country, starts, ends, name, close, zone) FROM stdin;
11	be	07:00:00	19:35:00	Bolsa de Bélgica	17:38:00	Europe/Madrid
12	nl	07:00:00	19:35:00	Bolsa de Amsterdam	17:38:00	Europe/Madrid
13	ie	07:00:00	19:35:00	Bolsa de Dublín	17:38:00	Europe/Madrid
14	fi	07:00:00	19:35:00	Bolsa de Helsinki	17:38:00	Europe/Madrid
6	it	07:00:00	19:35:00	Bolsa de Milán	17:38:00	Europe/Rome
7	jp	09:00:00	15:00:00	Bolsa de Tokio	20:00:00	Asia/Tokyo
2	us	09:30:00	16:00:00	Bolsa de New York	17:38:00	America/New_York
3	fr	09:00:00	17:30:00	Bosa de París	17:38:00	Europe/Paris
5	de	09:00:00	20:00:00	Bosa de Frankfurt	17:38:00	Europe/Berlin
15	es	09:00:00	17:30:00	España. No cotiza en mercados oficiales	17:38:00	Europe/Madrid
1	es	09:00:00	18:10:00	Bolsa de Madrid	17:38:00	Europe/Madrid
10	eu	07:00:00	19:35:00	Bolsa Europea	17:38:00	Europe/Madrid
9	pt	07:00:00	19:35:00	Bolsa de Lisboa	17:38:00	Europe/Lisbon
4	en	07:00:00	19:35:00	Bolsa de Londres	17:38:00	Europe/London
8	cn	00:00:00	10:00:00	Bolsa de Hong Kong	20:00:00	Asia/Hong_Kong
\.


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

--
-- Name: dividendospagos_id_dividendospagos_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('dividendospagos_id_dividendospagos_seq', 1, false);


--
-- Data for Name: dividendospagos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY dividendospagos (id_dividendospagos, code, fecha, bruto) FROM stdin;
\.


--
-- PostgreSQL database dump complete
--

update investments set deletable=true;
