from flask import Flask, redirect, url_for, session, render_template, request, flash
from fetch_data import fetch_data_from_database
from filter import filter_data, get_persons
from auth import authenticate_user, change_password
import secrets
import logging

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/login', methods=['GET', 'POST'])
def login():
    change_password = False  # Initialize change_password variable
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        logging.debug(f"Login attempt for username: {username}")
        
        auth_result = authenticate_user(username, password)
        logging.debug(f"Authentication result: {auth_result}")

        if auth_result == "authenticated":
            session['username'] = username
            flash("Welcome, you are successfully logged in!", "success")
            return redirect(url_for('main_page'))
        elif auth_result == "change_password":
            change_password = True
            flash("You are required to change your password.", "info")
            return render_template('login.html', change_password=change_password, username=username)
        elif auth_result == "invalid_credentials":
            flash("Invalid username or password. Please try again.", "danger")
        else:
            flash("An error occurred during authentication. Please try again later.", "danger")

    # Pass change_password to the template
    return render_template('login.html', change_password=change_password)

@app.route('/change_password', methods=['POST'])
def change_password_route():
    username = request.form.get('username')
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')
    
    logging.debug(f"Change password attempt for username: {username}")

    if new_password != confirm_new_password:
        flash("Passwords do not match. Please try again.", "danger")
        return render_template('login.html', change_password=True, username=username)

    if change_password(username, new_password):
        flash("Your password has been changed successfully. Please log in again.", "success")
        return redirect(url_for('login'))
    else:
        flash("There was an error changing your password. Please try again.", "danger")
        return render_template('login.html', change_password=True, username=username)

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
    app.run(host='0.0.0.0', port=5000, debug=True)
