from flask import Flask
from flask import redirect, url_for, session, render_template, request
from fetch_data import fetch_data_from_database
from filter import filter_data, get_persons
from auth import authenticate_user
import secrets


app = Flask(__name__)

app.secret_key =secrets.token_hex(16)

@app.route('/login', methods=['GET', 'POST'])  # Allow both GET and POST requests
def login():
    if request.method == 'POST':  # Check if the request method is POST
        username = request.form['username']
        password = request.form['password']

        if authenticate_user(username, password):
            session['username'] = username
            return redirect(url_for('main_page'))  # Redirect to the main page after successful login
        else:
            error_message = 'Invalid username or password'
            return render_template('login.html', error_message=error_message)
    return render_template('login.html', error_message=None)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('main_page'))


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
