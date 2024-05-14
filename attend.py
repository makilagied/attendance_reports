import os
import psycopg2
from openpyxl import load_workbook, Workbook
from datetime import datetime
from excel_handler import ExcelHandler
import pandas as pd

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

        # Execute a SQL query to fetch all data
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
    ad.access_date ASC, s.staff_id ASC;



        """
        cursor.execute(sql_query)

        # Fetch all the rows
        rows = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        if not rows:
            print("No data found in the database.")
        else:
            print("Data successfully fetched from the database.")
            return rows
    except psycopg2.Error as e:
        print(f"Error fetching data from the database: {e}")
        return None
    
    
# def update_excel_with_data(data):
#     try:
#         # Create an instance of ExcelHandler
#         excel_handler = ExcelHandler()

#         # Specify the file path for the Excel file
#         file_path = "data12.xlsx"

#         # Convert the data to a DataFrame
#         data_frame = pd.DataFrame(data, columns=["Staff ID", "Staff Name", "Access Date", "First Entry Time", "Last Exit Time", "Entry Status", "Exit Status", "Absentee Status"])
#         # Convert 'Access Date' column to datetime format
#         data_frame['Access Date'] = pd.to_datetime(data_frame['Access Date'])

#         # Format 'Access Date' column as "dd:mm:yyyy"
#         data_frame['Access Date'] = data_frame['Access Date'].dt.strftime('%d/%m/%Y')


#         # Save the DataFrame to the Excel file using ExcelHandler
#         excel_handler.save_to_excel(data_frame, file_path)

#         # Print status
#         print("Data successfully updated in Excel.")
#     except Exception as e:
#         print(f"Error updating data in Excel: {e}")


def update_excel_with_data(data):
    try:
        # Create an instance of ExcelHandler
        excel_handler = ExcelHandler()

        # Specify the file path for the Excel file
        file_path = "attendance_data.xlsx"

        # Convert the data to a DataFrame
        data_frame = pd.DataFrame(data, columns=["Staff ID", "Staff Name", "Access Date", "First Entry Time", "Last Exit Time", "Entry Status", "Exit Status", "Absentee Status"])

        # Convert 'Access Date' column to datetime format
        data_frame['Access Date'] = pd.to_datetime(data_frame['Access Date'])

        # Group data by month
        grouped_data = data_frame.groupby(data_frame['Access Date'].dt.month)

        # Save data to separate sheets for each month
        for month, group in grouped_data:
            # Convert month number to month name
            month_name = group['Access Date'].iloc[0].strftime('%B')

            # Save the DataFrame to the Excel file using ExcelHandler
            excel_handler.save_to_excel(group, file_path, sheet_name=month_name)

        # Print status
        print("Data successfully updated in Excel.")
    except Exception as e:
        print(f"Error updating data in Excel: {e}")


def main():
    data = fetch_data_from_database()
    if data:
        update_excel_with_data(data)

if __name__ == "__main__":
    main()


