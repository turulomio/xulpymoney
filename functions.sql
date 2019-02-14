

CREATE OR REPLACE FUNCTION public.investment_operations_current
    (
        IN p_investment_id integer, 
        IN p_at_datetime timestamp with time zone
    ) RETURNS TABLE (investment_id int, datetime timestamp with time zone, shares numeric, operationtype_id int, taxes numeric, commissions numeric, currency_conversion numeric)
    LANGUAGE plpgsql
    AS $$
DECLARE 
    o record;
BEGIN
    FOR o IN(SELECT * from operinversiones where id_inversiones= p_investment_id order by datetime)  
    LOOP
        investment_id:= o.id_inversiones;
        datetime:=o.datetime;
        shares:=o.acciones;
        operationtype_id:=o.id_tiposoperaciones;
        taxes:=o.impuestos;
        commissions:=o.comision;
        currency_conversion:=o.currency_conversion;
        RETURN NEXT;
    END LOOP;
END;
$$;
    
##    SELECT quotes.quote, quotes.datetime  INTO last_penultimate_lastyear.last, last_penultimate_lastyear.last_datetime FROM quote(id, at_datetime) quotes;
##    SELECT quotes.quote, quotes.datetime  INTO last_penultimate_lastyear.penultimate, last_penultimate_lastyear.penultimate_datetime FROM penultimate(id, at_datetime::date) quotes;
##    ly:=make_timestamptz((EXTRACT(YEAR FROM  at_datetime)-1)::integer, 12, 31, 23, 59, 59.999999::double precision) ;
##    SELECT quotes.quote, quotes.datetime  INTO last_penultimate_lastyear.lastyear, last_penultimate_lastyear.lastyear_datetime FROM quote(id,ly) quotes;
