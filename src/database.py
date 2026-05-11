import mysql.connector
from mysql.connector import pooling
import streamlit as st

class DatabaseManager:
    def __init__(self):
        conf = st.secrets["mysql"]
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="med_pool",
                pool_size=5,
                host=conf["host"],
                port=int(conf["port"]),
                database=conf["database"],
                user=conf["user"],
                password=conf["password"]
            )
            self._create_tables()
        except Exception as e:
            st.error(f"Database Connection Error: {e}")

    def _create_tables(self):
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fullname VARCHAR(255),
            email VARCHAR(255) UNIQUE,
            password_hash VARCHAR(255),
            is_doctor BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.execute_query(query)

    def execute_query(self, query, params=None, fetch=False):
        conn = self.pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            if fetch:
                result = cursor.fetchall()
                return result
            conn.commit()
        except Exception as e:
            st.error(f"SQL Error: {e}")
        finally:
            cursor.close()
            conn.close()