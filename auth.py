import psycopg2
import hashlib
from db_conn import create_db_connection

def authenticate_user(username, password):
    try:
        conn = create_db_connection()
        if conn is None:
            return None

        cursor = conn.cursor()
        cursor.execute("SELECT password, must_change_password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result:
            hashed_password = result[0]
            must_change_password = result[1]
            input_hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if hashed_password == input_hashed_password:
                if must_change_password:
                    return "change_password"
                return "authenticated"
        return "invalid_credentials"
    except psycopg2.Error as e:
        print(f"Error authenticating user: {e}")
        return "error"
    finally:
        if conn:
            conn.close()

def change_password(username, new_password):
    try:
        conn = create_db_connection()
        if conn is None:
            return False

        cursor = conn.cursor()
        new_hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        cursor.execute("UPDATE users SET password = %s, must_change_password = FALSE WHERE username = %s", 
                       (new_hashed_password, username))
        conn.commit()
        return True
    except psycopg2.Error as e:
        print(f"Error changing password: {e}")
        return False
    finally:
        if conn:
            conn.close()