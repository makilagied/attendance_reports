import psycopg2
import hashlib
from db_conn import create_db_connection

def authenticate_user(username, password):
    try:
        # Create a database connection
        conn = create_db_connection()
        if conn is None:
            return None

        # Create a cursor object using the cursor() method
        cursor = conn.cursor()

        # Execute the SQL query to fetch user details
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result:
            hashed_password = result[0]
            input_hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if hashed_password == input_hashed_password:
                return True
        return False
    except psycopg2.Error as e:
        print(f"Error authenticating user: {e}")
        return False
    finally:
        if conn:
            conn.close()
