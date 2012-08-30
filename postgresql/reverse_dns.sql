CREATE OR REPLACE FUNCTION public.reverse_address(addr inet)
RETURNS text 
AS
$t$
DECLARE
    mask integer;
    parts text[];
    part text;
    newpart text;
    retval text;
    rounds integer;
    host text;
    m integer;
BEGIN
    retval := '';
    rounds := 0;
    mask := masklen(addr);
    host := host(addr);
    IF (family(addr) = 4) THEN
        IF (mask < 8) THEN
            rounds := 4;
        ELSIF (mask < 16) THEN
            rounds := 3;
        ELSIF (mask < 24) THEN
            rounds := 2;
        ELSIF (mask < 32) THEN
            rounds := 1;
        END IF;
        FOREACH part in ARRAY regexp_split_to_array(host, '\.') LOOP
            rounds := rounds + 1;
            IF (rounds <= 4) THEN
                retval := part || '.' || retval;
            END IF;
        END LOOP;
        RETURN retval || 'in-addr.arpa.';
    ELSE
        IF (host ~ '^:') THEN
            host := '0' || host;
        END IF;
        parts := ARRAY[]::text[];
        FOREACH part in ARRAY regexp_split_to_array(host, ':') LOOP
            IF (part != '') THEN
                parts := array_append(parts, part);
            ELSE
                m := 9 - COUNT(*) FROM unnest(regexp_split_to_array(host, ':'));
                FOREACH m IN ARRAY array((SELECT generate_series(1, m))) LOOP
                    parts := array_append(parts, '0');
                END LOOP;
            END IF;
        END LOOP;
        m := mask / 16;
        FOREACH m IN ARRAY array((SELECT generate_series(1, m))) LOOP
            part := parts[m];
            m := 0;
            newpart := '';
            FOREACH part IN ARRAY regexp_matches(part, '(.)(.)?(.)?(.)?') LOOP
                m := m + 1;
                IF (newpart = '') THEN
                    newpart := part;
                ELSIF (part IS NULL) THEN
                    newpart := newpart || '.' || '0';
                ELSE
                    newpart := part || '.' || newpart;
                END IF;
            END LOOP;
            retval := newpart || '.' || retval;
        END LOOP;
        RETURN retval || 'ip6.arpa.';
    END IF;
END;
$t$
LANGUAGE 'plpgsql'
IMMUTABLE;