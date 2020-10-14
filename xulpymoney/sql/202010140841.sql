
--
-- Name: percentage(numeric, numeric, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE OR REPLACE FUNCTION public.percentage(from_ numeric, to_ numeric, by_100 boolean DEFAULT true) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
BEGIN
	if from_ = 0::numeric then 
		return Null;
	end if;
	if by_100 = true then
		return(to_-from_)/from_*100;
	else
		return(to_-from_)/from_;
	end if;
END;
$$;


ALTER FUNCTION public.percentage(from_ numeric, to_ numeric, by_100 boolean) OWNER TO postgres;
