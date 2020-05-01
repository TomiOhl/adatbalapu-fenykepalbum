-- szkript, ami kigyűjti, hogy kicsoda milyen várost látogatott meg
-- ez SQL Developerbe bemásolva és lefuttatva működik, de amikor függvényt akartam csinálni belőle, problémákba ütköztem. A nem működő verzió a szkript alatt
DECLARE
    TYPE uticelok_record IS RECORD(author Pictures.Author%TYPE, title Pictures.Title%TYPE, location Settlements.Name%TYPE);
    TYPE uticelok_table IS TABLE OF uticelok_record INDEX BY PLS_INTEGER;
    uticelok uticelok_table;

BEGIN
    SELECT Author, Pictures.Title, Settlements.Name BULK COLLECT INTO uticelok FROM Pictures, Users, Settlements WHERE author = users.nick and pictures.location != users.location and pictures.location = settlements.id;
    FOR i IN uticelok.FIRST..uticelok.LAST 
        LOOP
            DBMS_OUTPUT.PUT_LINE(uticelok(i).author || ' - ' || uticelok(i).title || ' - ' || uticelok(i).location);
        END LOOP;
END;

-- a függvény:

CREATE TYPE uticelok_record AS OBJECT (
	author VARCHAR2(20), title VARCHAR2(30), location VARCHAR2(50)
);
CREATE TYPE uticelok_table AS TABLE OF uticelok_record;

create or replace FUNCTION "travelers_places"
RETURN uticelok_table AS
        uticelok uticelok_table;
    BEGIN
        -- kigyujti azokat a helyeket, ahova kirandultak a juzerek
        SELECT Author, Pictures.Title, Settlements.Name
        BULK COLLECT INTO uticelok(author, title, location)
        FROM Pictures, Users, Settlements
        WHERE Author = Users.Nick AND Pictures.Location != Users.Location AND Pictures.Location = Settlements.Id;
    END;​