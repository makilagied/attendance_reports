from datetime import datetime

def get_persons(data):
    persons = set()
    for row in data:
        persons.add(row[1])  # Assuming the person's name is in the second column
    return list(persons)

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
