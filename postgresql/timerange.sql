create or replace function timerange (start timestamp, stop timestamp, step text)
RETURNS setof timestamp
AS
$$
declare
	time timestamp;
BEGIN
time := start::timestamp;
while time < stop::timestamp LOOP
        return next time;
        EXECUTE 'SELECT $1::timestamp + interval $a$' || step::text || '$a$' INTO time USING time::timestamp;
    END LOOP;
END;
$$
language 'plpgsql';

/* EXAMPLE */
SELECT COALESCE(temp,0), timerange.timerange
FROM timerange(to_timestamp(1322405902)::timestamp, to_timestamp(1352605902)::timestamp, '5 minutes'::text)
AS timerange
LEFT JOIN temp_data
ON (round(extract('epoch' FROM hometemp_data.date) / 300) = round(extract('epoch' FROM timerange.timerange) / 300));