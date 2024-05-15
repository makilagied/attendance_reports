from flask import redirect, url_for, session, render_template, request
from fetch_data import fetch_data_from_database
from filter import filter_data, get_persons
from flask import Flask
from auth import authenticate_user


app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])  # Allow both GET and POST requests
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if authenticate_user(username, password):
            session['username'] = username
            return redirect(url_for('index'))  # Redirect to the main page after successful login
        else:
            return render_template('login.html', error_message='Invalid username or password')

    return render_template('login.html')


@app.route('/')
def main_page():
    # Check if the user is logged in
    if 'username' in session:
        data = fetch_data_from_database()
        filtered_data = filter_data(data, request.args)
        persons = get_persons(data)  # Function to get unique persons from data
        # Render the main page after successful login
        return render_template('index.html', filtered_data=filtered_data, persons=persons)
    else:
        # If the user is not logged in, redirect to the login page
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
