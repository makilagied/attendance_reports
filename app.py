from flask import Flask, render_template, request, jsonify 
import psycopg2
from datetime import datetime, timedelta

app = Flask(__name__)


 # Add this import if not already present






# Define get_persons function
def get_persons(data):
    persons = set()
    for row in data:
        persons.add(row[1])  # Assuming the person's name is in the second column
    return list(persons)

def fetch_data_from_database():
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

@app.route('/', methods=['GET'])
def index():
    data = fetch_data_from_database()
    filtered_data = filter_data(data, request.args)
    persons = get_persons(data)  # Function to get unique persons from data
    return render_template('index.html', filtered_data=filtered_data, persons=persons)

def filter_by_date(data, date):
    if date:
        return [row for row in data if row[2] == date]
    return data

def filter_by_person(data, person):
    if person:
        return [row for row in data if row[1] == person]
    return data

def filter_by_status(data, status):
    if status:
        return [row for row in data if row[5] == status or row[6] == status or row[7] == status]
    return data

# def filter_data(data, filters):
#     filtered_data = data
#     if 'date' in filters:
#         filtered_data = filter_by_date(filtered_data, filters['date'])
#     if 'person' in filters:
#         filtered_data = filter_by_person(filtered_data, filters['person'])
#     if 'status' in filters:
#         filtered_data = filter_by_status(filtered_data, filters['status'])
#     return filtered_data

from datetime import datetime

def filter_by_date_range(data, start_date, end_date):
    if not start_date and not end_date:
        return data

    filtered_data = []
    for row in data:
        row_date = datetime.strptime(row[2], '%Y-%m-%d')
        if start_date and end_date:  # Filter by both start and end date
            if start_date <= row_date <= end_date:
                filtered_data.append(row)
        elif start_date:  # Filter by start date only
            if row_date >= start_date:
                filtered_data.append(row)
        elif end_date:  # Filter by end date only
            if row_date <= end_date:
                filtered_data.append(row)

    return filtered_data

def filter_data(data, filters):
    filtered_data = data
    start_date_str = filters.get('start_date', '')
    end_date_str = filters.get('end_date', '')

    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    elif start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = None
    elif end_date_str:
        start_date = None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    else:
        start_date = None
        end_date = None

    if 'date' in filters:
        filtered_data = filter_by_date(filtered_data, filters['date'])
    if 'person' in filters:
        filtered_data = filter_by_person(filtered_data, filters['person'])
    if 'status' in filters:
        filtered_data = filter_by_status(filtered_data, filters['status'])
    if start_date or end_date:
        filtered_data = filter_by_date_range(filtered_data, start_date, end_date)
    
    return filtered_data








if __name__ == '__main__':
    app.run(debug=True)
