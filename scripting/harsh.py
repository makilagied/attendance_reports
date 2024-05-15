import psycopg2
import hashlib

def hash_password(password):
    # Hash the password using SHA-256
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

def insert_user(username, password):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname="hikdb",
            user="hik",
            password="hik@123",
            host="10.10.102.2",
            port="5432"
        )

        # Create a cursor object using the cursor() method
        cursor = conn.cursor()

        # Hash the password
        hashed_password = hash_password(password)

        # Execute the SQL query to insert user details
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))

        # Commit the transaction
        conn.commit()
        print("User inserted successfully")
    except psycopg2.Error as e:
        print(f"Error inserting user: {e}")
    finally:
        if conn:
            conn.close()

# Example usage
insert_user('user', 'password')
