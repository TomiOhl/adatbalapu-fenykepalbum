import cx_Oracle
import config


def connect():
    con = cx_Oracle.connect(config.username, config.password, config.dsn, encoding=config.encoding)
    return con


def exec_return(query, params=None):  # ahol visszater valamivel, pl SELECT
    if params is None:
        params = []
    colnames = []
    out = []
    try:
        with connect() as connection:
            # itt kellenek a db-műveletek
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                colnames = [desc[0] for desc in cursor.description]
                for result in cursor:
                    out.append(result)
    except cx_Oracle.Error as error:
        print(error)
    return colnames, out


def exec_noreturn(query, params=None):   # ahol nem ter vissza (pl INSERT)
    if params is None:
        params = []
    try:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                connection.commit()
    except cx_Oracle.Error as error:
        print(error)
