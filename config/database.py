import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager

class Database:
    @staticmethod
    def get_connection():
        """Crée une connexion à la base de données"""
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="trait8",
                charset='utf8mb4',
                use_unicode=True
            )
            return connection
        except Error as e:
            print(f"Erreur de connexion à la base de données: {e}")
            raise

    @staticmethod
    @contextmanager
    def get_cursor(dictionary=True):
        """Context manager pour gérer automatiquement la connexion et le curseur"""
        connection = None
        cursor = None
        try:
            connection = Database.get_connection()
            cursor = connection.cursor(dictionary=dictionary)
            yield cursor
            connection.commit()
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Erreur base de données: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

def execute_query(query, params=None, fetch=False, fetchone=False):
    """Exécute une requête SQL"""
    with Database.get_cursor() as cursor:
        cursor.execute(query, params or ())
        
        if fetchone:
            return cursor.fetchone()
        elif fetch:
            return cursor.fetchall()
        else:
            return cursor.lastrowid

def execute_many(query, data):
    """Exécute plusieurs insertions"""
    with Database.get_cursor() as cursor:
        cursor.executemany(query, data)
        return cursor.rowcount