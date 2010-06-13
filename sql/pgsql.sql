--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- Name: plpgsql; Type: PROCEDURAL LANGUAGE; Schema: -; Owner: postgres
--

CREATE PROCEDURAL LANGUAGE plpgsql;


ALTER PROCEDURAL LANGUAGE plpgsql OWNER TO postgres;

SET search_path = public, pg_catalog;

--
-- Name: cuentas_saldo(integer, date); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION cuentas_saldo(p_id_cuentas integer, p_fechaparametro date) RETURNS double precision
    LANGUAGE plpgsql
    AS $$
DECLARE
    recCuentas RECORD;
    resultado FLOAT;
BEGIN
    resultado := 0;
    FOR recCuentas IN SELECT * FROM opercuentas where id_cuentas=p_id_cuentas and fecha <= p_fechaparametro LOOP
resultado := resultado + recCuentas.importe;
    END LOOP;
    RETURN resultado;
END;
$$;


ALTER FUNCTION public.cuentas_saldo(p_id_cuentas integer, p_fechaparametro date) OWNER TO postgres;

--
-- Name: eb_saldo(integer, date); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION eb_saldo(p_id_bancos integer, fechaparametro date) RETURNS double precision
    LANGUAGE plpgsql
    AS $$
DECLARE
    recCuentas RECORD;
    recInversiones RECORD;
    resultado FLOAT;
BEGIN
    resultado := 0;
    FOR recCuentas IN SELECT id_cuentas FROM cuentas where id_entidadesbancarias=p_id_bancos LOOP
        resultado := resultado + cuentas_saldo(recCuentas.id_cuentas, fechaparametro);        
        FOR recInversiones IN SELECT * FROM inversiones, cuentas where inversiones.id_cuentas=cuentas.id_cuentas and cuentas.id_cuentas=recCuentas.id_cuentas LOOP
    resultado := resultado + inversiones_saldo(recInversiones.id_inversiones, fechaparametro);
        END LOOP;    
    END LOOP;
    RETURN resultado;
END;
$$;


ALTER FUNCTION public.eb_saldo(p_id_bancos integer, fechaparametro date) OWNER TO postgres;

--
-- Name: inversion_actualizacion(integer, integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION inversion_actualizacion(integer, integer, integer) RETURNS double precision
    LANGUAGE sql
    AS $_$select actualizacion from actuinversiones where id_inversiones=$1 and date_part('year',fecha)=$2  and date_part('month',fecha)=$3 order by fecha desc limit 1$_$;


ALTER FUNCTION public.inversion_actualizacion(integer, integer, integer) OWNER TO postgres;

--
-- Name: inversion_actualizacion(integer, date); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION inversion_actualizacion(p_id_inversiones integer, fechaparametro date) RETURNS double precision
    LANGUAGE plpgsql
    AS $$
DECLARE
    rec RECORD;
    resultado FLOAT;
BEGIN
    resultado := 0;
    FOR rec IN SELECT actualizacion from actuinversiones where id_inversiones=p_id_inversiones and fecha  <= fechaparametro order by fecha desc limit 1 LOOP
	resultado:= rec.actualizacion;
    END LOOP;
    RETURN resultado;
END;
$$;


ALTER FUNCTION public.inversion_actualizacion(p_id_inversiones integer, fechaparametro date) OWNER TO postgres;

--
-- Name: inversion_invertido(integer, date); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION inversion_invertido(p_id_inversiones integer, p_fecha date) RETURNS double precision
    LANGUAGE plpgsql
    AS $$DECLARE
rec RECORD;
invertido FLOAT;
BEGIN
    invertido := 0;
    FOR rec IN SELECT fecha, acciones, valor_accion from tmpoperinversiones where id_inversiones=p_id_inversiones and Fecha <= p_fecha LOOP
	invertido := invertido + (rec.acciones * rec.valor_accion);
    END LOOP;
    RETURN invertido;
END;$$;


ALTER FUNCTION public.inversion_invertido(p_id_inversiones integer, p_fecha date) OWNER TO postgres;

--
-- Name: inversion_pendiente(integer, date); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION inversion_pendiente(p_id_inversiones integer, fechaparametro date) RETURNS double precision
    LANGUAGE plpgsql
    AS $$DECLARE
    rec RECORD;
    inicio FLOAT;
    final FLOAT;
BEGIN
    final := 0;
    inicio := 0;
    FOR rec IN SELECT fecha, acciones, valor_accion from tmpoperinversiones where id_inversiones=p_id_inversiones and Fecha <= fechaparametro LOOP
	inicio := inicio + (rec.acciones * rec.valor_accion);
	final := final + (rec.acciones * inversion_actualizacion(p_id_inversiones, fechaparametro));
    END LOOP;
    RETURN final - inicio;
END;$$;


ALTER FUNCTION public.inversion_pendiente(p_id_inversiones integer, fechaparametro date) OWNER TO postgres;

--
-- Name: inversion_saldo_medio(date, boolean, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION inversion_saldo_medio(fechaparametro date, pactiva boolean, pcotiza_mercados boolean) RETURNS double precision
    LANGUAGE plpgsql
    AS $$
DECLARE
    rec RECORD;
    recDias RECORD;
    resultado FLOAT;
BEGIN
    resultado := 0;
    FOR rec IN SELECT * FROM inversiones where in_activa=pactiva  and cotizamercado=pcotiza_mercados LOOP
       resultado := resultado + inversiones_saldo(rec.id_inversiones,fechaparametro);
    END LOOP;

    FOR recDias IN SELECT date(now())-fechaparametro as dias LOOP
       IF int2(recDias.dias)<>0
          THEN resultado:= resultado/recDias.dias;
          ELSE resultado := 0;
       END IF;
    END LOOP;
    RETURN resultado;
END;
$$;


ALTER FUNCTION public.inversion_saldo_medio(fechaparametro date, pactiva boolean, pcotiza_mercados boolean) OWNER TO postgres;

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
-- Name: inversiones_acciones(integer, date); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION inversiones_acciones(p_id_inversiones integer, fechaparametro date) RETURNS double precision
    LANGUAGE plpgsql
    AS $$
DECLARE
    recOperInversiones RECORD;
    resultado FLOAT;
BEGIN
    resultado := 0;
    FOR recOperInversiones IN SELECT acciones FROM operinversiones where id_inversiones=p_id_inversiones and fecha <= fechaparametro LOOP
	resultado := resultado + recOperInversiones.acciones;
    END LOOP;
    RETURN resultado;
END;
$$;


ALTER FUNCTION public.inversiones_acciones(p_id_inversiones integer, fechaparametro date) OWNER TO postgres;

--
-- Name: inversiones_saldo(integer, date); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION inversiones_saldo(id_inversiones integer, fechaparametro date) RETURNS double precision
    LANGUAGE plpgsql
    AS $$
DECLARE
BEGIN
    RETURN inversiones_acciones(id_inversiones,fechaparametro)* inversion_actualizacion(id_inversiones,fechaparametro);
END;
$$;


ALTER FUNCTION public.inversiones_saldo(id_inversiones integer, fechaparametro date) OWNER TO postgres;

--
-- Name: plpgsql_call_handler(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION plpgsql_call_handler() RETURNS language_handler
    LANGUAGE c
    AS '$libdir/plpgsql', 'plpgsql_call_handler';


ALTER FUNCTION public.plpgsql_call_handler() OWNER TO postgres;

--
-- Name: plpgsql_validator(oid); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION plpgsql_validator(oid) RETURNS void
    LANGUAGE c
    AS '$libdir/plpgsql', 'plpgsql_validator';


ALTER FUNCTION public.plpgsql_validator(oid) OWNER TO postgres;

--
-- Name: rendimiento_personal_total(integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION rendimiento_personal_total(id_inversiones integer, ano integer) RETURNS double precision
    LANGUAGE plpgsql
    AS $$
DECLARE
    rec RECORD;
    resultado FLOAT;
BEGIN
    resultado := 0;
    FOR rec IN SELECT actualizacion from actuinversiones where ma_inversiones=id_inversiones and fecha  <= fechaparametro order by fecha desc limit 1 LOOP
	resultado:= rec.actualizacion;
    END LOOP;
    RETURN resultado;
END;
$$;


ALTER FUNCTION public.rendimiento_personal_total(id_inversiones integer, ano integer) OWNER TO postgres;

--
-- Name: saldo_total(date); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION saldo_total(fechaparametro date) RETURNS double precision
    LANGUAGE plpgsql
    AS $$
DECLARE
    recCuentas RECORD;
    recInversiones RECORD;
    resultado FLOAT;
BEGIN
    resultado := 0;
    FOR recCuentas IN SELECT id_cuentas FROM cuentas LOOP
        resultado := resultado + cuentas_saldo(recCuentas.id_cuentas, fechaparametro);        
        FOR recInversiones IN SELECT * FROM inversiones, cuentas where inversiones.id_cuentas=cuentas.id_cuentas and cuentas.id_cuentas=recCuentas.id_cuentas LOOP
    resultado := resultado + inversiones_saldo(recInversiones.id_inversiones, fechaparametro);
        END LOOP;    
    END LOOP;
    RETURN resultado;
END;
$$;


ALTER FUNCTION public.saldo_total(fechaparametro date) OWNER TO postgres;

--
-- Name: saldototalcuentasactivas(date); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION saldototalcuentasactivas(fechaparametro date) RETURNS double precision
    LANGUAGE plpgsql
    AS $$
DECLARE
    recCuentas RECORD;
    resultado FLOAT;
BEGIN
    resultado := 0;
    FOR recCuentas IN SELECT * FROM cuentas where cu_activa=true LOOP
	PERFORM 'Refreshing materialized view ' ;
	resultado := resultado + cuentas_saldo(recCuentas.id_cuentas, fechaparametro);
    END LOOP;
    RETURN resultado;
END;
$$;


ALTER FUNCTION public.saldototalcuentasactivas(fechaparametro date) OWNER TO postgres;

--
-- Name: saldototalinversionesactivas(date); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION saldototalinversionesactivas(fechaparametro date) RETURNS double precision
    LANGUAGE plpgsql
    AS $$
DECLARE
    rec RECORD;
    resultado FLOAT;
BEGIN
    resultado := 0;
    FOR rec IN SELECT * FROM inversiones LOOP
	resultado := resultado + inversiones_saldo(rec.id_inversiones, fechaparametro);
    END LOOP;
    RETURN resultado;
END;
$$;


ALTER FUNCTION public.saldototalinversionesactivas(fechaparametro date) OWNER TO postgres;

--
-- Name: transferencia(date, integer, integer, double precision, double precision); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION transferencia(p_fecha date, p_cuentaorigen integer, p_cuentadestino integer, p_importe double precision, p_comision double precision) RETURNS void
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


ALTER FUNCTION public.transferencia(p_fecha date, p_cuentaorigen integer, p_cuentadestino integer, p_importe double precision, p_comision double precision) OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = true;

--
-- Name: actuinversiones; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE actuinversiones (
    id_actuinversiones integer DEFAULT nextval(('"seq_actuinversiones"'::text)::regclass) NOT NULL,
    fecha date NOT NULL,
    id_inversiones integer NOT NULL,
    actualizacion double precision NOT NULL
);


ALTER TABLE public.actuinversiones OWNER TO postgres;

--
-- Name: conceptos; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE conceptos (
    id_conceptos integer DEFAULT nextval(('"seq_conceptos"'::text)::regclass) NOT NULL,
    concepto text,
    id_tiposoperaciones integer,
    inmodificables boolean
);


ALTER TABLE public.conceptos OWNER TO postgres;

--
-- Name: cuentas; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE cuentas (
    id_cuentas integer DEFAULT nextval(('"seq_cuentas"'::text)::regclass) NOT NULL,
    cuenta text,
    id_entidadesbancarias integer,
    cu_activa boolean,
    numero_cuenta character varying(20)
);


ALTER TABLE public.cuentas OWNER TO postgres;

--
-- Name: depositos; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE depositos (
    id_depositos integer DEFAULT nextval(('"depositos_id_depositos_seq"'::text)::regclass) NOT NULL,
    id_cuentas integer,
    fecha_inicio date,
    cantidad double precision,
    fecha_fin date,
    intereses double precision,
    comision double precision,
    finalizado boolean,
    comentario text,
    retencion double precision
);


ALTER TABLE public.depositos OWNER TO postgres;

--
-- Name: depositos_id_depositos_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE depositos_id_depositos_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.depositos_id_depositos_seq OWNER TO postgres;

--
-- Name: dividendos; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE dividendos (
    id_dividendos integer DEFAULT nextval(('"dividendos_id_dividendos_seq"'::text)::regclass) NOT NULL,
    id_inversiones integer NOT NULL,
    bruto double precision NOT NULL,
    retencion double precision NOT NULL,
    liquido double precision,
    valorxaccion double precision,
    fecha date,
    id_opercuentas integer
);


ALTER TABLE public.dividendos OWNER TO postgres;

--
-- Name: dividendos_id_dividendos_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE dividendos_id_dividendos_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.dividendos_id_dividendos_seq OWNER TO postgres;

--
-- Name: opercuentas; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE opercuentas (
    id_opercuentas integer DEFAULT nextval(('"seq_opercuentas"'::text)::regclass) NOT NULL,
    fecha date NOT NULL,
    id_conceptos integer NOT NULL,
    id_tiposoperaciones integer NOT NULL,
    importe double precision NOT NULL,
    comentario text,
    id_cuentas integer NOT NULL
);


ALTER TABLE public.opercuentas OWNER TO postgres;

--
-- Name: dm_saldocuentas_fechas; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW dm_saldocuentas_fechas AS
    SELECT date_part('year'::text, opercuentas.fecha) AS date_part, sum(opercuentas.importe) AS sum, opercuentas.id_tiposoperaciones AS lu_tiposoperaciones FROM opercuentas GROUP BY date_part('year'::text, opercuentas.fecha), opercuentas.id_tiposoperaciones HAVING ((opercuentas.id_tiposoperaciones = 1) OR (opercuentas.id_tiposoperaciones = 2)) ORDER BY date_part('year'::text, opercuentas.fecha);


ALTER TABLE public.dm_saldocuentas_fechas OWNER TO postgres;

--
-- Name: dm_totales; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE dm_totales (
    fecha date,
    clave character varying(2),
    valor double precision
);


ALTER TABLE public.dm_totales OWNER TO postgres;

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
-- Name: ibex35; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE ibex35 (
    fecha date NOT NULL,
    cierre double precision NOT NULL,
    diff double precision
);


ALTER TABLE public.ibex35 OWNER TO postgres;

SET default_with_oids = true;

--
-- Name: inversiones; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE inversiones (
    id_inversiones integer DEFAULT nextval(('"seq_inversiones"'::text)::regclass) NOT NULL,
    inversion text NOT NULL,
    in_activa boolean DEFAULT true NOT NULL,
    tpcvariable integer NOT NULL,
    id_cuentas integer NOT NULL,
    compra double precision DEFAULT 0 NOT NULL,
    venta double precision DEFAULT 0 NOT NULL,
    internet text
);


ALTER TABLE public.inversiones OWNER TO postgres;

--
-- Name: opertarjetas; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE opertarjetas (
    id_opertarjetas integer DEFAULT nextval(('"seq_opertarjetas"'::text)::regclass) NOT NULL,
    fecha date,
    id_conceptos integer NOT NULL,
    id_tiposoperaciones integer NOT NULL,
    importe double precision NOT NULL,
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
    SELECT 'c', opercuentas.fecha, opercuentas.id_conceptos, opercuentas.id_tiposoperaciones, opercuentas.importe, opercuentas.comentario FROM opercuentas WHERE (opercuentas.id_tiposoperaciones <> 7) UNION SELECT 't', opertarjetas.fechapago AS fecha, opertarjetas.id_conceptos, opertarjetas.id_tiposoperaciones, opertarjetas.importe, opertarjetas.comentario FROM opertarjetas WHERE (opertarjetas.pagado = true) ORDER BY 2;


ALTER TABLE public.opercuentastarjetas OWNER TO postgres;

--
-- Name: operinversiones; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE operinversiones (
    id_operinversiones integer DEFAULT nextval(('"seq_operinversiones"'::text)::regclass) NOT NULL,
    fecha date,
    id_tiposoperaciones integer,
    id_inversiones integer,
    acciones double precision,
    importe double precision,
    impuestos double precision,
    comision double precision,
    valor_accion double precision
);


ALTER TABLE public.operinversiones OWNER TO postgres;

--
-- Name: pga_diagrams; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_diagrams (
    diagramname character varying(64) NOT NULL,
    diagramtables text,
    diagramlinks text
);


ALTER TABLE public.pga_diagrams OWNER TO postgres;

--
-- Name: pga_forms; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_forms (
    formname character varying(64),
    formsource text
);


ALTER TABLE public.pga_forms OWNER TO postgres;

--
-- Name: pga_graphs; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_graphs (
    graphname character varying(64) NOT NULL,
    graphsource text,
    graphcode text
);


ALTER TABLE public.pga_graphs OWNER TO postgres;

--
-- Name: pga_images; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_images (
    imagename character varying(64) NOT NULL,
    imagesource text
);


ALTER TABLE public.pga_images OWNER TO postgres;

--
-- Name: pga_layout; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_layout (
    tablename character varying(64),
    nrcols smallint,
    colnames text,
    colwidth text
);


ALTER TABLE public.pga_layout OWNER TO postgres;

--
-- Name: pga_queries; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_queries (
    queryname character varying(64),
    querytype character(1),
    querycommand text,
    querytables text,
    querylinks text,
    queryresults text,
    querycomments text
);


ALTER TABLE public.pga_queries OWNER TO postgres;

--
-- Name: pga_reports; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_reports (
    reportname character varying(64),
    reportsource text,
    reportbody text,
    reportprocs text,
    reportoptions text
);


ALTER TABLE public.pga_reports OWNER TO postgres;

--
-- Name: pga_schema; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_schema (
    schemaname character varying(64),
    schematables text,
    schemalinks text
);


ALTER TABLE public.pga_schema OWNER TO postgres;

--
-- Name: pga_scripts; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE pga_scripts (
    scriptname character varying(64),
    scriptsource text
);


ALTER TABLE public.pga_scripts OWNER TO postgres;

--
-- Name: seq_actuinversiones; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_actuinversiones
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.seq_actuinversiones OWNER TO postgres;

--
-- Name: seq_conceptos; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_conceptos
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.seq_conceptos OWNER TO postgres;

--
-- Name: seq_cuentas; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_cuentas
    START WITH 0
    INCREMENT BY 1
    MAXVALUE 1000000
    MINVALUE 0
    CACHE 1;


ALTER TABLE public.seq_cuentas OWNER TO postgres;

--
-- Name: seq_entidadesbancarias; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_entidadesbancarias
    START WITH 0
    INCREMENT BY 1
    MAXVALUE 100000000
    MINVALUE 0
    CACHE 1;


ALTER TABLE public.seq_entidadesbancarias OWNER TO postgres;

--
-- Name: seq_inversiones; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_inversiones
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.seq_inversiones OWNER TO postgres;

--
-- Name: seq_opercuentas; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_opercuentas
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.seq_opercuentas OWNER TO postgres;

--
-- Name: seq_operinversiones; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_operinversiones
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.seq_operinversiones OWNER TO postgres;

--
-- Name: seq_opertarjetas; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_opertarjetas
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.seq_opertarjetas OWNER TO postgres;

--
-- Name: seq_tarjetas; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_tarjetas
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.seq_tarjetas OWNER TO postgres;

--
-- Name: seq_tmpoperinversioneshistoricas; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_tmpoperinversioneshistoricas
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.seq_tmpoperinversioneshistoricas OWNER TO postgres;

--
-- Name: tarjetas; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE tarjetas (
    id_tarjetas integer DEFAULT nextval(('"seq_tarjetas"'::text)::regclass) NOT NULL,
    tarjeta text,
    id_cuentas integer,
    pago_diferido boolean,
    saldomaximo double precision,
    tj_activa boolean,
    numero text
);


ALTER TABLE public.tarjetas OWNER TO postgres;

--
-- Name: tiposoperaciones; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE tiposoperaciones (
    id_tiposoperaciones integer NOT NULL,
    tipooperacion text,
    modificable boolean,
    operinversion boolean,
    opercuentas boolean
);


ALTER TABLE public.tiposoperaciones OWNER TO postgres;

--
-- Name: tmpdepositosheredada; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE tmpdepositosheredada (
)
INHERITS (opercuentas);


ALTER TABLE public.tmpdepositosheredada OWNER TO postgres;

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
-- Name: tmpoperinversiones; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE tmpoperinversiones (
    id_tmpoperinversiones integer NOT NULL,
    id_operinversiones integer NOT NULL,
    id_inversiones integer NOT NULL,
    fecha date NOT NULL,
    acciones double precision NOT NULL,
    id_tiposoperaciones integer,
    importe double precision,
    impuestos double precision,
    comision double precision,
    valor_accion double precision
);


ALTER TABLE public.tmpoperinversiones OWNER TO postgres;

--
-- Name: tmpoperinversiones_id_tmpoperinversiones_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE tmpoperinversiones_id_tmpoperinversiones_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


ALTER TABLE public.tmpoperinversiones_id_tmpoperinversiones_seq OWNER TO postgres;

--
-- Name: tmpoperinversiones_id_tmpoperinversiones_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE tmpoperinversiones_id_tmpoperinversiones_seq OWNED BY tmpoperinversiones.id_tmpoperinversiones;


--
-- Name: tmpoperinversioneshistoricas; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE tmpoperinversioneshistoricas (
    id_tmpoperinversioneshistoricas integer DEFAULT nextval(('public.seq_tmpoperinversioneshistoricas'::text)::regclass),
    id_operinversiones integer,
    id_inversiones integer,
    fecha_inicio date,
    importe double precision,
    id_tiposoperaciones bigint,
    acciones double precision,
    comision double precision,
    impuestos double precision,
    fecha_venta date,
    valor_accion_compra double precision,
    valor_accion_venta double precision
);


ALTER TABLE public.tmpoperinversioneshistoricas OWNER TO postgres;

--
-- Name: id_tmpoperinversiones; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE tmpoperinversiones ALTER COLUMN id_tmpoperinversiones SET DEFAULT nextval('tmpoperinversiones_id_tmpoperinversiones_seq'::regclass);


--
-- Name: clave_primaria; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY ibex35
    ADD CONSTRAINT clave_primaria PRIMARY KEY (fecha);


--
-- Name: depositos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY depositos
    ADD CONSTRAINT depositos_pkey PRIMARY KEY (id_depositos);


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
-- Name: pga_diagrams_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pga_diagrams
    ADD CONSTRAINT pga_diagrams_pkey PRIMARY KEY (diagramname);


--
-- Name: pga_graphs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pga_graphs
    ADD CONSTRAINT pga_graphs_pkey PRIMARY KEY (graphname);


--
-- Name: pga_images_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY pga_images
    ADD CONSTRAINT pga_images_pkey PRIMARY KEY (imagename);


--
-- Name: tarjetas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY tarjetas
    ADD CONSTRAINT tarjetas_pkey PRIMARY KEY (id_tarjetas);


--
-- Name: tmpoperinversiones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY tmpoperinversiones
    ADD CONSTRAINT tmpoperinversiones_pkey PRIMARY KEY (id_tmpoperinversiones);


--
-- Name: unik_actuinversiones; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY actuinversiones
    ADD CONSTRAINT unik_actuinversiones UNIQUE (id_actuinversiones);


--
-- Name: actuinversiones_fecha; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX actuinversiones_fecha ON actuinversiones USING btree (fecha);


--
-- Name: conceptos_id_conceptos; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX conceptos_id_conceptos ON conceptos USING btree (id_conceptos);


--
-- Name: cuentas_id_cuentas; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX cuentas_id_cuentas ON cuentas USING btree (id_cuentas);


--
-- Name: entidadesbancarias_id_entidades; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX entidadesbancarias_id_entidades ON entidadesbancarias USING btree (id_entidadesbancarias);


--
-- Name: id_opercuentas_opercuentas_ukey; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX id_opercuentas_opercuentas_ukey ON opercuentas USING btree (id_opercuentas);


--
-- Name: id_operinversiones_operinversiones_key; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX id_operinversiones_operinversiones_key ON operinversiones USING btree (id_operinversiones);


--
-- Name: id_operinversiones_operinversiones_ukey; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX id_operinversiones_operinversiones_ukey ON operinversiones USING btree (id_operinversiones);


--
-- Name: id_tiposoperaciones_tiposoperaciones_ukey; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX id_tiposoperaciones_tiposoperaciones_ukey ON tiposoperaciones USING btree (id_tiposoperaciones);


--
-- Name: index_actuinversiones_fecha; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX index_actuinversiones_fecha ON actuinversiones USING btree (fecha);


--
-- Name: inversiones_id_inversiones; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX inversiones_id_inversiones ON inversiones USING btree (id_inversiones);


--
-- Name: opercuentas_ma_cuentas; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX opercuentas_ma_cuentas ON opercuentas USING btree (id_cuentas);


--
-- Name: tiposoperaciones_id_tiposoperac; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX tiposoperaciones_id_tiposoperac ON tiposoperaciones USING btree (id_tiposoperaciones);


--
-- Name: tmpoperinversiones_id_tmpoperinversiones_key; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX tmpoperinversiones_id_tmpoperinversiones_key ON tmpoperinversiones USING btree (id_tmpoperinversiones);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: pga_diagrams; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE pga_diagrams FROM PUBLIC;
REVOKE ALL ON TABLE pga_diagrams FROM postgres;
GRANT ALL ON TABLE pga_diagrams TO postgres;
GRANT ALL ON TABLE pga_diagrams TO PUBLIC;


--
-- Name: pga_forms; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE pga_forms FROM PUBLIC;
REVOKE ALL ON TABLE pga_forms FROM postgres;
GRANT ALL ON TABLE pga_forms TO postgres;
GRANT ALL ON TABLE pga_forms TO PUBLIC;


--
-- Name: pga_graphs; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE pga_graphs FROM PUBLIC;
REVOKE ALL ON TABLE pga_graphs FROM postgres;
GRANT ALL ON TABLE pga_graphs TO postgres;
GRANT ALL ON TABLE pga_graphs TO PUBLIC;


--
-- Name: pga_images; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE pga_images FROM PUBLIC;
REVOKE ALL ON TABLE pga_images FROM postgres;
GRANT ALL ON TABLE pga_images TO postgres;
GRANT ALL ON TABLE pga_images TO PUBLIC;


--
-- Name: pga_layout; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE pga_layout FROM PUBLIC;
REVOKE ALL ON TABLE pga_layout FROM postgres;
GRANT ALL ON TABLE pga_layout TO postgres;
GRANT ALL ON TABLE pga_layout TO PUBLIC;


--
-- Name: pga_queries; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE pga_queries FROM PUBLIC;
REVOKE ALL ON TABLE pga_queries FROM postgres;
GRANT ALL ON TABLE pga_queries TO postgres;
GRANT ALL ON TABLE pga_queries TO PUBLIC;


--
-- Name: pga_reports; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE pga_reports FROM PUBLIC;
REVOKE ALL ON TABLE pga_reports FROM postgres;
GRANT ALL ON TABLE pga_reports TO postgres;
GRANT ALL ON TABLE pga_reports TO PUBLIC;


--
-- Name: pga_schema; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE pga_schema FROM PUBLIC;
REVOKE ALL ON TABLE pga_schema FROM postgres;
GRANT ALL ON TABLE pga_schema TO postgres;
GRANT ALL ON TABLE pga_schema TO PUBLIC;


--
-- Name: pga_scripts; Type: ACL; Schema: public; Owner: postgres
--

REVOKE ALL ON TABLE pga_scripts FROM PUBLIC;
REVOKE ALL ON TABLE pga_scripts FROM postgres;
GRANT ALL ON TABLE pga_scripts TO postgres;
GRANT ALL ON TABLE pga_scripts TO PUBLIC;


--
-- PostgreSQL database dump complete
--

