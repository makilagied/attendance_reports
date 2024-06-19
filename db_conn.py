import psycopg2

def create_db_connection():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname="hikdb",
            user="hik",
            password="hik@123",
            host="10.10.102.2",
            port="5432"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None


