import psycopg2
from psycopg2 import sql

DBNAME = 'SwiftSender'
USER = 'postgres'
PASSWORD = '123'
HOST = 'localhost'
PORT = 5432
connect = psycopg2.connect(
    dbname=DBNAME,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT)
cursor = connect.cursor()
connect.autocommit = True


def list_table():
    cursor.execute("""
    SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';""")
    a = [i[0] for i in cursor.fetchall()]
    return a


def create_table():
    cursor.execute("""
    CREATE TABLE Sender(
	    senderId SERIAL PRIMARY KEY,
	    email varchar(40) NOT NULL UNIQUE
    );

    CREATE TABLE Receivers (
	    senderId SERIAL NOT NULL,
	    email varchar(255) NOT NULL,
	    FOREIGN KEY(senderId) REFERENCES Sender(senderId),
	    CONSTRAINT unique_combination_constraint UNIQUE (senderId, email)
    )""")
    