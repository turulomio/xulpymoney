
CREATE SEQUENCE public.productspairs_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


CREATE TABLE public.productspairs (
    id integer DEFAULT nextval(('"productspairs_seq"'::text)::regclass) NOT NULL,
    name varchar(200) NOT NULL,
    a_id integer NOT NULL,
    b_id integer NOT NULL
);


ALTER TABLE ONLY public.productspairs ADD CONSTRAINT productspairs_pk PRIMARY KEY (id);
ALTER TABLE public.productspairs ADD CONSTRAINT productspairs_fk_a FOREIGN KEY (a) REFERENCES public.products(id) ON DELETE RESTRICT;
ALTER TABLE public.productspairs ADD CONSTRAINT productspairs_fk_b FOREIGN KEY (b) REFERENCES public.products(id) ON DELETE RESTRICT;
