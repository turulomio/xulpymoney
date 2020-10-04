drop function public.ohcldailybeforesplits;
drop function public.ohclmonthlybeforesplits;

--
-- Name: ohcldailybeforesplits(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.ohcldailybeforesplits(product_id integer) RETURNS TABLE(products_id integer, date date, open numeric, high numeric, low numeric, close numeric)
    LANGUAGE plpgsql
    AS $$
DECLARE 
    o record;
BEGIN
    FOR o IN (select 
                quotes.products_id, 
                datetime::date as date, 
                (array_agg(quote order by datetime))[1] as open, 
                min(quote) as low, 
                max(quote) as high, 
                (array_agg(quote order by datetime desc))[1] as close 
            from quotes 
            where quotes.products_id=product_id
            group by quotes.products_id, datetime::date 
            order by datetime::date )  
    LOOP
	    products_id=o.products_id;
        date:= o.date;
        open:=o.open;
        high:=o.high;
        low:=o.low;
        close:=o.close;
        RETURN NEXT;
    END LOOP;
END;
$$;


ALTER FUNCTION public.ohcldailybeforesplits(product_id integer) OWNER TO postgres;

--
-- Name: ohclmonthlybeforesplits(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.ohclmonthlybeforesplits(product_id integer) RETURNS TABLE(products_id integer, year integer, month integer, open numeric, high numeric, low numeric, close numeric)
    LANGUAGE plpgsql
    AS $$
DECLARE 
    o record;
BEGIN
    FOR o IN (                   select 
			    t.products_id,
                date_part('year',date) as year, 
                date_part('month', date) as month, 
                (array_agg(t.open order by date))[1] as open, 
                min(t.low) as low, 
                max(t.high) as high, 
                (array_agg(t.close order by date desc))[1] as close 
            from ohclDailyBeforeSplits(product_id) as t
            group by t.products_id,  year, month 
            order by year, month)
    LOOP
	    products_id=product_id;
        year:= o.year;
			  month:= o.month;
        open:=o.open;
        high:=o.high;
        low:=o.low;
        close:=o.close;
        RETURN NEXT;
    END LOOP;
END;
$$;


ALTER FUNCTION public.ohclmonthlybeforesplits(product_id integer) OWNER TO postgres;
