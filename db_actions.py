import cx_Oracle
import config


def connect():
    con = cx_Oracle.connect(config.username, config.password, config.dsn, encoding=config.encoding)
    return con


def execute(query):
    colnames = []
    out = []
    try:
        with connect() as connection:
            # itt kellenek a db-műveletek
            with connection.cursor() as cursor:
                cursor.execute(query)
                colnames = [desc[0] for desc in cursor.description]
                for result in cursor:
                    out.append(result)
    except cx_Oracle.Error as error:
        print(error)
    return colnames, out
