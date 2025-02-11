from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

# from werkzeug.security import generate_password_hash
# import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For flash messages


# Database connection setup
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',  # Replace with your MySQL server's host
        user='root',  # Replace with your MySQL username
        password='Root',  # Replace with your MySQL password
        database='student_management'  # Replace with your MySQL database name
    )
    return connection


# Home route (index page)
# @app.route('/')
# def home():
#     # Connect to the MySQL database
#     connection = get_db_connection()
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute('SELECT * FROM students')  # Query the students table
#     students = cursor.fetchall()  # Fetch all results from the query
#
#     cursor.close()
#     connection.close()
#
#     return render_template('index.html', students=students)  # Pass data to the template

# Home route (index page)
@app.route('/')
def home():
    return render_template('index.html')  # Render the home page


# Route to the student page
@app.route('/student', methods=['GET', 'POST'])
def student():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            # Flash a success message
            flash('Login successful!', 'success')
            return redirect(url_for('student'))  # This part is already correct

        else:
            # Flash an error message
            flash('Invalid username or password', 'error')
            return redirect(url_for('student'))

    # Render the student page on GET request
    return render_template('student.html')


# Route to the registration page
@app.route('/Register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Collect form data
            student_data = {
                'student_name': request.form['student_name'],
                'roll_number': request.form['roll_number'],
                'username': request.form['username'],
                'password': request.form['password'],
                'fathername': request.form['fathername'],
                'mothername': request.form['mothername'],
                'id': request.form['id'],
                'gender': request.form['gender'],
                'phone_number': request.form['phone_number'],
                'state': request.form['state'],
                'district': request.form['district'],
                'email': request.form['email'],
                'city': request.form['city'],
                'address': request.form['address']
            }

            # Establish database connection
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if username already exists
            cursor.execute("SELECT * FROM students WHERE username = %s", (student_data['username'],))
            if cursor.fetchone():
                flash('Username already exists', 'danger')
                return render_template('Register.html')  # Stay on the same page with the error message

            # Insert student data into the database
            cursor.execute("""
                INSERT INTO students (student_name, roll_number, username, password, 
                                      fathername, mothername, id, gender, phone_number, 
                                      email, state, district, city, address)
                VALUES (%(student_name)s, %(roll_number)s, %(username)s, %(password)s, 
                        %(fathername)s, %(mothername)s, %(id)s, %(gender)s, 
                        %(phone_number)s, %(email)s, %(state)s, %(district)s, %(city)s, %(address)s)
            """, student_data)

            conn.commit()  # Save changes
            cursor.close()
            conn.close()

            flash('Registration successful!', 'success')  # Success message
            return render_template('Register.html')

        except mysql.connector.Error as err:
            flash(f'Registration failed: {err}', 'danger')  # Error message

    # Render the page with any flashed messages
    return render_template('Register.html')


@app.route('/update_details', methods=['GET', 'POST'])
def update_details():
    if request.method == 'GET':
        # Render the HTML template for GET request (external template file should be used)
        return render_template('update_details.html', message=None)

    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_phone_number = request.form.get('phone_number', None)
        new_email = request.form.get('email', None)
        new_state = request.form.get('state', None)
        new_district = request.form.get('district', None)
        new_city = request.form.get('city', None)
        new_address = request.form.get('address', None)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify user credentials
        cursor.execute("SELECT * FROM students WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        if not user:
            cursor.close()
            conn.close()
            return render_template('update_details.html', message="Invalid credentials. Please try again.")

        # Update the details
        try:
            if new_phone_number:
                cursor.execute("UPDATE students SET phone_number = %s WHERE username = %s", (new_phone_number, username))
            if new_email:
                cursor.execute("UPDATE students SET email = %s WHERE username = %s", (new_email, username))
            if new_state:
                cursor.execute("UPDATE students SET state = %s WHERE username = %s", (new_state, username))
            if new_district:
                cursor.execute("UPDATE students SET district = %s WHERE username = %s", (new_district, username))
            if new_city:
                cursor.execute("UPDATE students SET city = %s WHERE username = %s", (new_city, username))
            if new_address:
                cursor.execute("UPDATE students SET address = %s WHERE username = %s", (new_address, username))

            conn.commit()
            cursor.close()
            conn.close()

            return render_template('update_details.html', message="Your details have been updated successfully!")
        except mysql.connector.Error as err:
            cursor.close()
            conn.close()
            return render_template('update_details.html', message=f"Error updating details: {err}")



# ute to the forgot password page
# Forgot Password page
@app.route('/Forgot_Password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']
        email = request.form.get('email')  # Get the email from the form

        # Check if the password and confirmPassword match
        if password != confirmPassword:
            flash('Passwords do not match. Please try again.', 'danger')
            return render_template('Forgot_Password.html')  # Return to the form page with the flash message

        # Proceed to update the password in the database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if the email exists in the database
            cursor.execute("SELECT * FROM students WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user:
                flash('Email not found. Please try again.', 'danger')
                cursor.close()
                conn.close()
                return render_template('Forgot_Password.html')

            # If the email exists, update the password
            cursor.execute("UPDATE students SET password = %s WHERE email = %s", (password, email))

            # Commit the changes and close the connection
            conn.commit()
            cursor.close()
            conn.close()

            # Flash success message and redirect to login page
            flash('Password updated successfully!', 'success')
            return redirect(url_for('forgot_password'))  # Assuming you have a 'login' route

        except mysql.connector.Error as err:
            flash(f"Error updating password: {err}", 'danger')
            return render_template('Forgot_Password.html')  # Return to the form page with the error message

    # If GET request, just render the form
    return render_template('Forgot_Password.html')



# Database configuration (replace these with actual values)
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Root',
    'database': 'student_management'
}

# Your database connection method here (if not already defined)
def get_db_connection():
    """Create and return a connection to the database."""
    return mysql.connector.connect(**db_config)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Admin login page."""
    error_message = None
    success_message = None

    if request.method == 'POST':
        # Safely get username and password from form
        username = request.form.get('username')
        password = request.form.get('password')

        # Add your own logic here to authenticate the admin (e.g., checking against a known admin password or a database)
        if username == "Irfan" and password == "Irfan123":  # Example logic
            session['logged_in'] = True  # Set session to indicate that the admin is logged in
            success_message = "Login successful! Redirecting to the registered page..."
            return render_template('admin.html', success_message=success_message)  # Render with success message
        else:
            error_message = "Invalid credentials, please try again."

    return render_template('admin.html', error_message=error_message)



@app.route('/Registered', methods=['GET'])
def registered():
    """Display registered student details for admin only."""
    if not session.get('logged_in'):  # Check if admin is logged in
        return redirect(url_for('admin'))  # Redirect to login page if not logged in

    connection = None
    cursor = None
    students = []  # To hold student data fetched from the DB
    error_message = None  # Variable to hold any error messages

    try:
        # Fetch the search query from the request if available
        search_id = request.args.get('search_id')  # Get the search_id parameter from the query string

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # If search_id is provided, filter students by ID
        if search_id:
            cursor.execute('SELECT id, student_name, roll_number, username, email FROM students WHERE id = %s', (search_id,))
        else:
            # If no search, fetch all students
            cursor.execute('SELECT id, student_name, roll_number, username, email FROM students')

        students = cursor.fetchall()  # Fetch the student records

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        error_message = "Error fetching data from the database."
    finally:
        # Ensure the cursor and connection are closed properly
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    # Render the template with the fetched students
    return render_template('Registered.html', students=students, error_message=error_message)


@app.route('/logout')
def logout():
    """Log the admin out."""
    session.pop('logged_in', None)  # Remove logged-in session
    return redirect(url_for('admin'))  # Redirect to login page after logging out

@app.route('/update_student/<int:student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    """Handle updating student details for the admin."""
    if not session.get('logged_in'):  # Check if admin is logged in
        return redirect(url_for('admin'))  # Redirect to login page if not logged in

    connection = None
    cursor = None
    error_message = None
    success_message = None
    student = None

    if request.method == 'GET':
        # Fetch current student details
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT * FROM students WHERE id = %s', (student_id,))
            student = cursor.fetchone()

            if not student:
                error_message = "Student not found."
                return render_template('update_student.html', error_message=error_message)

            return render_template('update_student.html', student=student)

        except mysql.connector.Error as e:
            error_message = f"Error: {e}"
            return render_template('update_student.html', error_message=error_message)

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    elif request.method == 'POST':
        # Get updated details from the form (only editable fields)
        student_name = request.form['student_name']
        roll_number = request.form['roll_number']
        username = request.form['username']
        gender = request.form['gender']
        fathername = request.form['fathername']
        mothername = request.form['mothername']
        email = request.form['email']
        phone_number = request.form['phone_number']
        state = request.form['state']
        district = request.form['district']
        city = request.form['city']
        address = request.form['address']

        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Update only the fields that can be modified (excluding Student ID and Password)
            cursor.execute("""
                UPDATE students
                SET student_name = %s, roll_number = %s, username = %s, gender = %s,
                    fathername = %s, mothername = %s, email = %s, phone_number = %s,
                    state = %s, district = %s, city = %s, address = %s
                WHERE id = %s
            """, (student_name, roll_number, username, gender, fathername, mothername, email,
                  phone_number, state, district, city, address, student_id))

            connection.commit()

            # Set success message and fetch the updated student
            success_message = "Student details updated successfully!"

            # Fetch the updated student information
            cursor.execute('SELECT * FROM students WHERE id = %s', (student_id,))
            student = cursor.fetchone()

            return render_template('update_student.html', success_message=success_message, student=student)

        except mysql.connector.Error as e:
            error_message = f"Error: {e}"
            return render_template('update_student.html', error_message=error_message)

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()




# @app.route('/update_student/<int:student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    # logic to retrieve student details and update them
    return render_template('update_student.html', student_id=student_id)

# Function to fetch student details by ID
def get_student_by_id(student_id):
    connection = None
    cursor = None
    student = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Execute the SQL query to fetch student details
        cursor.execute('SELECT * FROM students WHERE id = %s', (student_id,))
        student = cursor.fetchone()  # Fetch the first result (since ID is unique)

    except mysql.connector.Error as e:
        print(f"Error fetching student details: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return student


# Route to display student details (GET method)
@app.route('/student_details/<int:student_id>', methods=['GET'])
def student_details(student_id):
    """Show student details."""
    if not session.get('logged_in'):  # Check if admin is logged in
        return redirect(url_for('admin'))  # Redirect to login page if not logged in

    # Fetch the student details
    student = get_student_by_id(student_id)
    if student:
        return render_template('student_details.html', student=student)
    else:
        # Handle case when student is not found (optional)
        return jsonify({'error': 'Student not found'}), 404


# Route to delete student (POST method)
@app.route('/student_details/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    """Delete a student from the database."""
    if not session.get('logged_in'):  # Check if admin is logged in
        return redirect(url_for('admin'))  # Redirect to login page if not logged in

    connection = None
    cursor = None
    try:
        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Delete the student from the database
        cursor.execute('DELETE FROM students WHERE id = %s', (student_id,))
        connection.commit()

        # After successful deletion, return a success message
        success_message = "Student deleted successfully!"  # Success message
        return render_template('student_details.html', success_message=success_message)  # Render with success message

    # return '', 200  # Respond with HTTP status 200 (OK)

    # except mysql.connector.Error as e:
    #     # Return error response if deletion failed
    #     return jsonify({'error': f'Error deleting student: {e}'}), 500

    except mysql.connector.Error as e:
        # Return error response if deletion failed
        error_message = f"Error deleting student: {e}"
        return render_template('student_details.html', error_message=error_message)  # Render with error message
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()



# Form submission
@app.route('/submit', methods=['POST'])
def submit():
    # Example submission handling
    data = request.form.get('data')
    if data:
        flash('Form submitted successfully!', 'success')
    else:
        flash('Error: Form submission failed.', 'danger')
    return render_template('form.html')  # Replace with the actual template for the form



if __name__ == '__main__':
    app.run(debug=True)




