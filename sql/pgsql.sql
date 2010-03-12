

SET client_encoding = 'SQL_ASCII';
SET check_function_bodies = false;

SET SESSION AUTHORIZATION 'postgres';

CREATE TABLE actuinversiones (
    id_actuinversiones integer DEFAULT nextval('"seq_actuinversiones"'::text) NOT NULL,
    fecha date NOT NULL,
    ma_inversiones integer NOT NULL,
    actualizacion double precision NOT NULL
);

CREATE TABLE comentarios (
    id_comentarios integer NOT NULL,
    comentario text,
    lu_tiposoperaciones integer,
    lu_conceptos integer
);

CREATE TABLE conceptos (
    id_conceptos integer NOT NULL,
    concepto text,
    lu_tipooperacion integer,
    inmodificables boolean
);


CREATE TABLE cuentas (
    id_cuentas integer DEFAULT nextval('"seq_cuentas"'::text) NOT NULL,
    cuenta text,
    ma_entidadesbancarias integer,
    cu_activa boolean,
    numero_cuenta character varying(20)
);

CREATE TABLE entidadesbancarias (
    id_entidadesbancarias integer DEFAULT nextval('"seq_entidadesbancarias"'::text) NOT NULL,
    entidadesbancaria text NOT NULL,
    eb_activa boolean NOT NULL
);



CREATE TABLE inversiones (
    id_inversiones integer DEFAULT nextval('"seq_inversiones"'::text) NOT NULL,
    inversione text NOT NULL,
    in_activa boolean DEFAULT true NOT NULL,
    tpcvariable integer NOT NULL,
    lu_cuentas integer NOT NULL,
    cotizamercado boolean DEFAULT true NOT NULL
);


CREATE TABLE tiposoperaciones (
    id_tiposoperaciones integer NOT NULL,
    tipo_operacion text,
    modificable boolean,
    operinversion boolean,
    opercuentas boolean
);


CREATE TABLE opercuentas (
    id_opercuentas integer DEFAULT nextval('"seq_opercuentas"'::text) NOT NULL,
    fecha date NOT NULL,
    lu_conceptos integer NOT NULL,
    lu_tiposoperaciones integer NOT NULL,
    importe double precision NOT NULL,
    comentario text,
    ma_cuentas integer NOT NULL
);




CREATE TABLE operinversiones (
    id_operinversiones integer DEFAULT nextval('"seq_operinversiones"'::text) NOT NULL,
    fecha date,
    lu_tiposoperaciones integer,
    ma_inversiones integer,
    acciones double precision,
    importe double precision,
    impuestos double precision,
    comision double precision,
    valor_accion double precision,
    comentario text
);


CREATE TABLE opertarjetas (
    id_opertarjetas integer DEFAULT nextval('"seq_opertarjetas"'::text) NOT NULL,
    fecha date,
    lu_conceptos integer NOT NULL,
    lu_tiposoperaciones integer NOT NULL,
    importe double precision NOT NULL,
    comentario text,
    ma_tarjetas integer NOT NULL,
    pagado boolean NOT NULL,
    fechapago date,
    lu_opercuentas bigint
);


CREATE TABLE tarjetas (
    id_tarjetas integer DEFAULT nextval('"seq_tarjetas"'::text) NOT NULL,
    tarjeta text,
    lu_cuentas integer,
    numero text,
    pago_diferido boolean,
    saldomaximo double precision,
    tj_activa boolean
);


CREATE SEQUENCE depositos_id_depositos_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


CREATE TABLE depositos (
    id_depositos integer DEFAULT nextval('"depositos_id_depositos_seq"'::text) NOT NULL,
    lu_cuentas integer,
    fecha_inicio date,
    cantidad double precision,
    fecha_fin date,
    intereses double precision,
    comision double precision,
    finalizado boolean,
    comentario text,
    retencion double precision
);


CREATE TABLE tmpdepositosheredada (
)
INHERITS (opercuentas);


CREATE TABLE tmpinversionesheredada (
    id_operinversiones integer NOT NULL,
    id_inversiones integer NOT NULL
)
INHERITS (opercuentas);


CREATE SEQUENCE dividendos_id_dividendos_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 51 (OID 19559)
-- Name: dividendos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE dividendos (
    id_dividendos integer DEFAULT nextval('"dividendos_id_dividendos_seq"'::text) NOT NULL,
    lu_inversiones integer NOT NULL,
    bruto double precision NOT NULL,
    retencion double precision NOT NULL,
    liquido double precision,
    valorxaccion double precision,
    fecha date,
    id_opercuentas integer
);


--
-- TOC entry 52 (OID 19562)
-- Name: tmpdividendosheredada; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE tmpdividendosheredada (
    id_dividendos integer NOT NULL
)
INHERITS (opercuentas);



CREATE SEQUENCE seq_actuinversiones
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 11 (OID 19590)
-- Name: seq_opercuentas; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_opercuentas
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 61 (OID 19594)
-- Name: tmpoperinversiones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE tmpoperinversiones (
    id_tmpoperinversiones serial NOT NULL,
    ma_operinversiones integer NOT NULL,
    ma_inversiones integer NOT NULL,
    fecha date NOT NULL,
    acciones double precision NOT NULL,
    lu_tiposoperaciones integer,
    importe double precision,
    impuestos double precision,
    comision double precision
);


--
-- TOC entry 13 (OID 19597)
-- Name: seq_tarjetas; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_tarjetas
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 15 (OID 19599)
-- Name: seq_opertarjetas; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_opertarjetas
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 17 (OID 19601)
-- Name: seq_inversiones; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_inversiones
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 19 (OID 19603)
-- Name: seq_operinversiones; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_operinversiones
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 62 (OID 19605)
-- Name: tmpoperinversioneshistoricas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE tmpoperinversioneshistoricas (
    id_tmpoperinversioneshistoricas integer DEFAULT nextval('public.seq_tmpoperinversioneshistoricas'::text),
    ma_operinversiones integer,
    ma_inversiones integer,
    fecha_inicio date,
    importe double precision,
    lu_tiposoperaciones bigint,
    acciones double precision,
    comision double precision,
    impuestos double precision,
    fecha_venta date,
    valor_accion_compra double precision,
    valor_accion_venta double precision
);


--
-- TOC entry 21 (OID 19608)
-- Name: seq_tmpoperinversioneshistoricas; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_tmpoperinversioneshistoricas
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- TOC entry 23 (OID 198173)
-- Name: seq_entidadesbancarias; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_entidadesbancarias
    INCREMENT BY 1
    MAXVALUE 100000000
    MINVALUE 0
    CACHE 1;


--
-- TOC entry 25 (OID 198363)
-- Name: seq_cuentas; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE seq_cuentas
    INCREMENT BY 1
    MAXVALUE 1000000
    MINVALUE 0
    CACHE 1;


SET SESSION AUTHORIZATION 'postgres';

--
-- TOC entry 63 (OID 253541)
-- Name: todocuentas; Type: VIEW; Schema: public; Owner: postgres
--
CREATE VIEW todo_cuentas AS
 SELECT cuentas.id_cuentas, cuentas.cuenta, cuentas.cu_activa, cuentas.numero_cuenta, entidadesbancarias.id_entidadesbancarias, entidadesbancarias.entidadesbancaria, entidadesbancarias.eb_activa
   FROM cuentas, entidadesbancarias
  WHERE cuentas.ma_entidadesbancarias = entidadesbancarias.id_entidadesbancarias;



create view todo_tarjetas as  SELECT tarjetas.id_tarjetas, tarjetas.numero, tarjetas.tarjeta, tarjetas.lu_cuentas, tarjetas.pago_diferido, tarjetas.saldomaximo, tarjetas.tj_activa, cuentas.id_cuentas, cuentas.cuenta, cuentas.ma_entidadesbancarias, cuentas.cu_activa, cuentas.numero_cuenta, entidadesbancarias.id_entidadesbancarias, entidadesbancarias.entidadesbancaria, entidadesbancarias.eb_activa
FROM tarjetas, cuentas, entidadesbancarias WHERE tarjetas.lu_cuentas = cuentas.id_cuentas AND cuentas.ma_entidadesbancarias = entidadesbancarias.id_entidadesbancarias;

--
-- TOC entry 64 (OID 253577)
-- Name: dm_saldocuentas_fechas; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW dm_saldocuentas_fechas AS
    SELECT date_part('year'::text, opercuentas.fecha) AS date_part, sum(opercuentas.importe) AS sum, opercuentas.lu_tiposoperaciones FROM opercuentas GROUP BY date_part('year'::text, opercuentas.fecha), opercuentas.lu_tiposoperaciones HAVING ((opercuentas.lu_tiposoperaciones = 1) OR (opercuentas.lu_tiposoperaciones = 2)) ORDER BY date_part('year'::text, opercuentas.fecha);


--
-- TOC entry 91 (OID 253586)
-- Name: inversion_actualizacion(integer, integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION inversion_actualizacion(integer, integer, integer) RETURNS double precision
    AS 'select actualizacion from actuinversiones where ma_inversiones=$1 and date_part(''year'',fecha)=$2  and date_part(''month'',fecha)=$3 order by fecha desc limit 1'
    LANGUAGE sql;


--
-- TOC entry 92 (OID 253595)
-- Name: inversion_actualizacion(integer, date); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION inversion_actualizacion(integer, date) RETURNS double precision
    AS 'select actualizacion from actuinversiones where ma_inversiones=$1 and fecha<=$2 order by fecha desc limit 1'
    LANGUAGE sql;


--
-- TOC entry 65 (OID 253598)
-- Name: todoinversiones; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW todoinversiones AS
    SELECT operinversiones.importe, operinversiones.fecha, inversion_actualizacion(operinversiones.ma_inversiones, operinversiones.fecha) AS inversion_actualizacion FROM operinversiones;


--
-- TOC entry 66 (OID 253710)
-- Name: dm_totales; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE dm_totales (
    fecha date,
    clave character varying(2),
    valor double precision
);



COPY  actuinversiones (id_actuinversiones, fecha, ma_inversiones, actualizacion) FROM stdin;
1	2005-11-04	1	10
2	2005-11-05	1	10.1
3	2005-11-06	1	10.15
\.




COPY comentarios (id_comentarios, comentario, lu_tiposoperaciones, lu_conceptos) FROM stdin;
1	Inicio de Aplicación	2	1
2	Supermercado	1	2
3	Restaurante	1	3
4	Recibido de Ibercaja Libreta Ahorro	3	4
\.


--
-- Data for TOC entry 94 (OID 19457)
-- Name: conceptos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY conceptos (id_conceptos, concepto, lu_tipooperacion) FROM stdin;
2	Supermercado	1	\N
3	Restaurante	1	\N
4	Traspaso Realizado	1	\N
7	Gasolina	1	\N
8	Ocio	1	\N
9	Teléfono	1	\N
0	Desconocido	1	\N
13	Alquiler & Comunidad	1	\N
14	Universidad & Estudios	1	\N
15	Viajes & Taxi & Autopista	1	\N
16	Hoteles	1	\N
18	Regalos	1	\N
19	Electricidad	1	\N
20	Gas	1	\N
21	Intereses Negativos	1	\N
22	Ropa	1	\N
17	Loterías	1	\N
26	Informática	1	\N
27	Coche	1	\N
31	Invitaciones	1	\N
12	Televisión & Video & Cine	1	\N
23	Médicos & Farmacias & Higiene Personal	1	\N
34	Compra Casa	1	\N
36	Infraestructura Casa	1	\N
37	Pago Impuestos	1	\N
38	Comisiones bancarias	1	\N
1	Inicio de Cuenta	2	\N
5	Traspaso Recibido	3	\N
6	Devolución Impuestos	2	\N
10	Nomina	2	\N
24	Intereses Positivos	2	\N
25	Loterías Premios	2	\N
28	Herencia	2	\N
29	Compra Fondos Inversion	4	\N
30	Pagas	2	\N
32	Liquidar Inversion	5	\N
33	Otros Ingresos	2	\N
35	Venta Fondos Inversion	5	\N
39	Dividendos	2	t
40	Facturacion Tarjeta	7	t
43	Anadido Fondos Inversion	6	\N
44	Ajustes Negativos	1	\N
41	Creación Deposito	8	\N
42	Vencimiento Depósito	9	\N
45	Compra Casa (Laura)	2	\N
46	Prestamo	2	\N
47	Seguro	1	\N
\.

COPY cuentas (id_cuentas, cuenta, ma_entidadesbancarias, cu_activa, numero_cuenta) FROM stdin;
0	Efectivo	0	t	\N
1	Ejemplo Cuenta	1	t	\N
\.

COPY opercuentas(id_opercuentas,fecha,lu_conceptos,lu_tiposoperaciones,importe,comentario,ma_cuentas) FROM stdin;
1	2005-11-03	1	2	1500	Modificame con el importe de inicio de cuenta que quieras	1
2	2005-11-03	1	2	1500	Modificame con el importe de inicio de cuenta que quieras	0
3	2005-11-04	29	4	-1000	Compra de Fondo de Inversión	1
4	2005-11-04	38	1	-5	Comisión	1
5	2005-10-04	47	1	-5	\N	1
\.

COPY inversiones (id_inversiones, inversione, in_activa, tpcvariable, lu_cuentas, cotizamercado) FROM stdin;
1	Ejemplo Inversion	t	100	1	t
\.

COPY tiposoperaciones (id_tiposoperaciones, tipo_operacion, modificable, operinversion, opercuentas) FROM stdin;
5	Venta Acciones	\N	t	\N
3	Trasferencia	\N	\N	\N
0	Deconocido	\N	\N	\N
7	Facturacion Tarjeta	\N	\N	\N
8	Creación Depósito	\N	\N	\N
9	Vencimiento Depósito	\N	\N	\N
4	Compra Acciones	\N	t	\N
6	Añadido de Acciones	\N	t	\N
10	Traspaso fondo inversión	\N	t	\N
2	Ingreso	\N	\N	t
1	Gasto	f	\N	t
\.

COPY entidadesbancarias (id_entidadesbancarias, entidadesbancaria, eb_activa) FROM stdin;
0	No Bancos	t
1	Ejemplo Entidad Bancaria	t
\.



COPY operinversiones (id_operinversiones, fecha, lu_tiposoperaciones, ma_inversiones, acciones, importe, impuestos, comision, valor_accion, comentario) FROM stdin;
1	2005-11-04	4	1	100	1000	4	5	10	Operación de inversión de prueba
\.

COPY tmpoperinversiones (id_tmpoperinversiones, ma_operinversiones, ma_inversiones, fecha, acciones, lu_tiposoperaciones, importe, impuestos, comision) FROM stdin;
1	1	1	2005-11-04	100	4	1000	-4	-5
\.


COPY tarjetas (id_tarjetas, tarjeta, lu_cuentas, pago_diferido, saldomaximo, tj_activa) FROM stdin;
1	Ejemplo tarjeta diferido	1	t	600	t
2	Ejemplo tarjeta debito	1	f	600	t
\.

COPY opertarjetas (id_opertarjetas, fecha, lu_conceptos, lu_tiposoperaciones, importe, comentario, ma_tarjetas, pagado, fechapago, lu_opercuentas) FROM stdin;
\.

COPY depositos (id_depositos, lu_cuentas, fecha_inicio, cantidad, fecha_fin, intereses, comision, finalizado, comentario, retencion) FROM stdin;
\.

CREATE UNIQUE INDEX comentarios_id_comentarios ON comentarios USING btree (id_comentarios);

CREATE UNIQUE INDEX conceptos_id_conceptos ON conceptos USING btree (id_conceptos);

CREATE UNIQUE INDEX cuentas_id_cuentas ON cuentas USING btree (id_cuentas);

CREATE UNIQUE INDEX inversiones_id_inversiones ON inversiones USING btree (id_inversiones);

CREATE INDEX tiposoperaciones_id_tiposoperac ON tiposoperaciones USING btree (id_tiposoperaciones);

CREATE UNIQUE INDEX entidadesbancarias_id_entidades ON entidadesbancarias USING btree (id_entidadesbancarias);

CREATE INDEX opercuentas_ma_cuentas ON opercuentas USING btree (ma_cuentas);

CREATE INDEX actuinversiones_fecha ON actuinversiones USING btree (fecha);

CREATE UNIQUE INDEX id_tiposoperaciones_tiposoperaciones_ukey ON tiposoperaciones USING btree (id_tiposoperaciones);

CREATE UNIQUE INDEX id_operinversiones_operinversiones_ukey ON operinversiones USING btree (id_operinversiones);

CREATE INDEX id_operinversiones_operinversiones_key ON operinversiones USING btree (id_operinversiones);

CREATE UNIQUE INDEX id_opercuentas_opercuentas_ukey ON opercuentas USING btree (id_opercuentas);

CREATE INDEX tmpoperinversiones_id_tmpoperinversiones_key ON tmpoperinversiones USING btree (id_tmpoperinversiones);

CREATE INDEX index_actuinversiones_fecha ON actuinversiones USING btree (fecha);

ALTER TABLE ONLY tarjetas
    ADD CONSTRAINT tarjetas_pkey PRIMARY KEY (id_tarjetas);

ALTER TABLE ONLY opertarjetas
    ADD CONSTRAINT opertarjetas_pkey PRIMARY KEY (id_opertarjetas);

ALTER TABLE ONLY depositos
    ADD CONSTRAINT depositos_pkey PRIMARY KEY (id_depositos);

ALTER TABLE ONLY dividendos
    ADD CONSTRAINT dividendos_pkey PRIMARY KEY (id_dividendos);

ALTER TABLE ONLY tmpoperinversiones
    ADD CONSTRAINT tmpoperinversiones_pkey PRIMARY KEY (id_tmpoperinversiones);

ALTER TABLE ONLY actuinversiones
    ADD CONSTRAINT unik_actuinversiones UNIQUE (id_actuinversiones);

SELECT pg_catalog.setval('depositos_id_depositos_seq', 1, true);

SELECT pg_catalog.setval('dividendos_id_dividendos_seq', 1, true);

SELECT pg_catalog.setval('seq_actuinversiones', 1, true);

SELECT pg_catalog.setval('seq_opercuentas', 1, true);

SELECT pg_catalog.setval('tmpoperinversiones_id_tmpoperinversiones_seq', 1, true);

SELECT pg_catalog.setval('seq_tarjetas', 3, true);

SELECT pg_catalog.setval('seq_opertarjetas', 1, true);

SELECT pg_catalog.setval('seq_inversiones', 2, true);

SELECT pg_catalog.setval('seq_operinversiones', 1, true);

SELECT pg_catalog.setval('seq_tmpoperinversioneshistoricas', 1, true);

SELECT pg_catalog.setval('seq_entidadesbancarias', 2, true);

SELECT pg_catalog.setval('seq_cuentas', 2, true);


SET SESSION AUTHORIZATION 'postgres';


COMMENT ON SCHEMA public IS 'Standard public schema';


