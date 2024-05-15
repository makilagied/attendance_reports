from db_conn import create_db_connection  # Import the create_db_connection function

def fetch_data_from_database():
    try:
        # Create a database connection
        conn = create_db_connection()
        if conn is None:
            return None

        # Create a cursor object using the cursor() method
        cursor = conn.cursor()

        # Execute the SQL query
        sql_query = """
SELECT 
    s.staff_id,
    s.staff_name,
    TO_CHAR(ad.access_date, 'YYYY-MM-DD') AS access_date,
    TO_CHAR(MIN(CASE WHEN a.access_time <= TIME '11:00:00' THEN a.access_time END), 'HH24:MI') AS first_entry_time,
    TO_CHAR(MAX(CASE WHEN a.access_time >= TIME '12:00:00' THEN a.access_time END), 'HH24:MI') AS last_exit_time,
    CASE
        WHEN MIN(CASE WHEN a.access_time <= TIME '09:00:59' THEN a.access_time END) IS NOT NULL AND MIN(CASE WHEN a.access_time <= TIME '09:00:59' THEN a.access_time END) <= TIME '09:00:59' THEN 'In Time'
        WHEN MIN(CASE WHEN a.access_time <= TIME '11:00:00' THEN a.access_time END) IS NOT NULL AND MIN(CASE WHEN a.access_time <= TIME '11:00:00' THEN a.access_time END) > TIME '09:01:00' THEN 'Late Comer'
        ELSE NULL
    END AS entry_status,
    CASE
        WHEN MAX(CASE WHEN a.access_time >= CASE WHEN EXTRACT('dow' FROM ad.access_date) = 6 THEN TIME '12:30:00' ELSE TIME '17:00:00' END THEN a.access_time END) IS NOT NULL AND MAX(CASE WHEN a.access_time >= CASE WHEN EXTRACT('dow' FROM ad.access_date) = 6 THEN TIME '12:30:00' ELSE TIME '17:00:00' END THEN a.access_time END) >= CASE WHEN EXTRACT('dow' FROM ad.access_date) = 6 THEN TIME '12:30:00' ELSE TIME '17:00:00' END THEN 'In Time'
        WHEN MAX(CASE WHEN a.access_time >= CASE WHEN EXTRACT('dow' FROM ad.access_date) = 6 THEN TIME '11:00:00' ELSE TIME '14:00:00' END THEN a.access_time END) IS NOT NULL AND MAX(CASE WHEN a.access_time >= CASE WHEN EXTRACT('dow' FROM ad.access_date) = 6 THEN TIME '11:00:00' ELSE TIME '14:00:00' END THEN a.access_time END) < CASE WHEN EXTRACT('dow' FROM ad.access_date) = 6 THEN TIME '11:00:00' ELSE TIME '16:59:59' END THEN 'Early Leaver'
        ELSE NULL
    END AS exit_status,

    CASE
        WHEN MIN(a.access_time) IS NULL AND MAX(a.access_time) IS NULL THEN 'Absentee'
        ELSE NULL
    END AS absentee_status
FROM 
    staff s
CROSS JOIN
    (SELECT DISTINCT access_date FROM attendance) ad
LEFT JOIN 
    attendance a ON s.staff_name = a.personal_name AND ad.access_date = a.access_date
GROUP BY 
    s.staff_id, s.staff_name, ad.access_date
ORDER BY 
    ad.access_date ASC, s.staff_id DESC;

        """
        cursor.execute(sql_query)

        # Fetch all the rows
        rows = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return rows
    except psycopg2.Error as e:
        print(f"Error fetching data from the database: {e}")
        return None
