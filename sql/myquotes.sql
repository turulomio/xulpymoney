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
    name text,
    closes time without time zone,
    zone text
);


ALTER TABLE public.bolsas OWNER TO postgres;

--
-- Name: COLUMN bolsas.starts; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN bolsas.starts IS 'Hora de inicio de descargas en UTC';


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
-- Name: dps_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE dps_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dps_seq OWNER TO postgres;

--
-- Name: dps; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE dps (
    id_dps integer DEFAULT nextval('dps_seq'::regclass) NOT NULL,
    date date,
    gross numeric(18,6),
    id bigint
);


ALTER TABLE public.dps OWNER TO postgres;

--
-- Name: TABLE dps; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE dps IS 'Dividends per share paid';


--
-- Name: COLUMN dps.gross; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN dps.gross IS 'Bruto';


--
-- Name: COLUMN dps.id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN dps.id IS 'id of investment';


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

ALTER SEQUENCE dividendospagos_id_dividendospagos_seq OWNED BY dps.id_dps;


--
-- Name: estimations_dps; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE estimations_dps (
    year integer NOT NULL,
    estimation numeric(18,6) NOT NULL,
    date_estimation date,
    source text,
    manual boolean,
    id integer NOT NULL
);


ALTER TABLE public.estimations_dps OWNER TO postgres;

--
-- Name: TABLE estimations_dps; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE estimations_dps IS 'Dividends per share';


--
-- Name: estimations_eps; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE estimations_eps (
    year integer NOT NULL,
    estimation numeric(18,6) NOT NULL,
    date_estimation date,
    source text,
    manual boolean,
    id integer NOT NULL
);


ALTER TABLE public.estimations_eps OWNER TO postgres;

--
-- Name: TABLE estimations_eps; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE estimations_eps IS 'Earnings per share';


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
    ticker text,
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
-- Name: tmpohlcdaily; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW tmpohlcdaily AS
 SELECT quotes.id,
    (quotes.datetime)::date AS date,
    max(quotes.quote) AS high,
    min(quotes.quote) AS low,
    min(quotes.datetime) AS first,
    max(quotes.datetime) AS last
   FROM quotes
  GROUP BY quotes.id, (quotes.datetime)::date
  ORDER BY (quotes.datetime)::date DESC;


ALTER TABLE public.tmpohlcdaily OWNER TO postgres;

--
-- Name: ohlcdaily; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW ohlcdaily AS
 SELECT tmpohlcdaily.id,
    tmpohlcdaily.date,
    ( SELECT quote.quote
           FROM quote(tmpohlcdaily.id, tmpohlcdaily.first) quote(id, datetime, quote)) AS first,
    tmpohlcdaily.low,
    tmpohlcdaily.high,
    ( SELECT quote.quote
           FROM quote(tmpohlcdaily.id, tmpohlcdaily.last) quote(id, datetime, quote)) AS last
   FROM tmpohlcdaily;


ALTER TABLE public.ohlcdaily OWNER TO postgres;

--
-- Name: tmpohlcmonthly; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW tmpohlcmonthly AS
 SELECT quotes.id,
    date_part('year'::text, quotes.datetime) AS year,
    date_part('month'::text, quotes.datetime) AS month,
    max(quotes.quote) AS high,
    min(quotes.quote) AS low,
    min(quotes.datetime) AS first,
    max(quotes.datetime) AS last
   FROM quotes
  GROUP BY quotes.id, date_part('year'::text, quotes.datetime), date_part('month'::text, quotes.datetime);


ALTER TABLE public.tmpohlcmonthly OWNER TO postgres;

--
-- Name: ohlcmonthly; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW ohlcmonthly AS
 SELECT tmpohlcmonthly.id,
    tmpohlcmonthly.year,
    tmpohlcmonthly.month,
    ( SELECT quote.quote
           FROM quote(tmpohlcmonthly.id, tmpohlcmonthly.first) quote(id, datetime, quote)) AS first,
    tmpohlcmonthly.low,
    tmpohlcmonthly.high,
    ( SELECT quote.quote
           FROM quote(tmpohlcmonthly.id, tmpohlcmonthly.last) quote(id, datetime, quote)) AS last
   FROM tmpohlcmonthly;


ALTER TABLE public.ohlcmonthly OWNER TO postgres;

--
-- Name: tmpohlcweekly; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW tmpohlcweekly AS
 SELECT quotes.id,
    date_part('year'::text, quotes.datetime) AS year,
    date_part('week'::text, quotes.datetime) AS week,
    max(quotes.quote) AS high,
    min(quotes.quote) AS low,
    min(quotes.datetime) AS first,
    max(quotes.datetime) AS last
   FROM quotes
  GROUP BY quotes.id, date_part('year'::text, quotes.datetime), date_part('week'::text, quotes.datetime);


ALTER TABLE public.tmpohlcweekly OWNER TO postgres;

--
-- Name: ohlcweekly; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW ohlcweekly AS
 SELECT tmpohlcweekly.id,
    tmpohlcweekly.year,
    tmpohlcweekly.week,
    ( SELECT quote.quote
           FROM quote(tmpohlcweekly.id, tmpohlcweekly.first) quote(id, datetime, quote)) AS first,
    tmpohlcweekly.low,
    tmpohlcweekly.high,
    ( SELECT quote.quote
           FROM quote(tmpohlcweekly.id, tmpohlcweekly.last) quote(id, datetime, quote)) AS last
   FROM tmpohlcweekly;


ALTER TABLE public.ohlcweekly OWNER TO postgres;

--
-- Name: tmpohlcyearly; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW tmpohlcyearly AS
 SELECT quotes.id,
    date_part('year'::text, quotes.datetime) AS year,
    max(quotes.quote) AS high,
    min(quotes.quote) AS low,
    min(quotes.datetime) AS first,
    max(quotes.datetime) AS last
   FROM quotes
  GROUP BY quotes.id, date_part('year'::text, quotes.datetime);


ALTER TABLE public.tmpohlcyearly OWNER TO postgres;

--
-- Name: ohlcyearly; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW ohlcyearly AS
 SELECT tmpohlcyearly.id,
    tmpohlcyearly.year,
    ( SELECT quote.quote
           FROM quote(tmpohlcyearly.id, tmpohlcyearly.first) quote(id, datetime, quote)) AS first,
    tmpohlcyearly.low,
    tmpohlcyearly.high,
    ( SELECT quote.quote
           FROM quote(tmpohlcyearly.id, tmpohlcyearly.last) quote(id, datetime, quote)) AS last
   FROM tmpohlcyearly;


ALTER TABLE public.ohlcyearly OWNER TO postgres;

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
-- Name: bolsas_pk; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY bolsas
    ADD CONSTRAINT bolsas_pk PRIMARY KEY (id_bolsas);


--
-- Name: dividendosestimaciones_pk; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY estimations_dps
    ADD CONSTRAINT dividendosestimaciones_pk PRIMARY KEY (year, id);


--
-- Name: dps_pk; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY dps
    ADD CONSTRAINT dps_pk PRIMARY KEY (id_dps);


--
-- Name: estimacion_eps_pk; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY estimations_eps
    ADD CONSTRAINT estimacion_eps_pk PRIMARY KEY (year, id);


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

CREATE INDEX dividendosestimaciones_id ON estimations_dps USING btree (id);


--
-- Name: estimaciones_eps; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX estimaciones_eps ON estimations_eps USING btree (id);


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

