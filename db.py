import psycopg2


def get_connection():

    conn = psycopg2.connect(
        database="expense_db",
        user="postgres",
        password="Raviteja13323#",
        host="localhost",
        port="5432"
    )

    return conn