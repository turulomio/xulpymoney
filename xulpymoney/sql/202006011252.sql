CREATE TABLE public.strategies (
    id integer DEFAULT nextval(('"strategies_seq"'::text)::regclass) NOT NULL,
    name text NOT NULL,
    investments text,
    dt_from timestamp  with time zone,
    dt_to timestamp  with time zone
);


ALTER TABLE public.strategies OWNER TO postgres;

CREATE SEQUENCE public.strategies_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE public.strategies_seq OWNER TO postgres;

