from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)

# Secret key for login session
app.secret_key = "student_management_secret_key"


# -----------------------------
# MySQL Database Connection
# -----------------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="student_management"
)

print("MySQL Database Connected Successfully!")


# -----------------------------
# Home Page
# -----------------------------
@app.route("/")
def home():
    return render_template("home.html")


# -----------------------------
# Student Registration
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]
        course = request.form["course"]

        cursor = db.cursor()

        query = """
        INSERT INTO students
        (name, email, password, phone, course)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (name, email, password, phone, course)
        )

        db.commit()
        cursor.close()

        return "Student Registered Successfully!"

    return render_template("register.html")


# -----------------------------
# Student Login
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cursor = db.cursor()

        query = """
        SELECT * FROM students
        WHERE email = %s AND password = %s
        """

        cursor.execute(query, (email, password))

        student = cursor.fetchone()

        cursor.close()

        if student:

            # Store student ID in session
            session["student_id"] = student[0]

            return redirect(url_for("dashboard"))

        else:
            return "Invalid Email or Password!"

    return render_template("login.html")


# -----------------------------
# Student Dashboard
# -----------------------------
@app.route("/dashboard")
def dashboard():

    # Check whether student is logged in
    if "student_id" not in session:
        return redirect(url_for("login"))

    student_id = session["student_id"]

    cursor = db.cursor()

    query = """
    SELECT id, name, email, phone, course
    FROM students
    WHERE id = %s
    """

    cursor.execute(query, (student_id,))

    student = cursor.fetchone()

    cursor.close()

    if student:
        return render_template(
            "dashboard.html",
            student=student
        )

    return "Student not found!"
# -----------------------------
# Edit Student Profile
# -----------------------------
@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():

    # Check if student is logged in
    if "student_id" not in session:
        return redirect(url_for("login"))

    student_id = session["student_id"]

    cursor = db.cursor()

    # Get current student information
    if request.method == "GET":

        query = """
        SELECT id, name, email, phone, course
        FROM students
        WHERE id = %s
        """

        cursor.execute(query, (student_id,))
        student = cursor.fetchone()

        cursor.close()

        return render_template(
            "edit_profile.html",
            student=student
        )

    # Update student information
    name = request.form["name"]
    phone = request.form["phone"]
    course = request.form["course"]

    query = """
    UPDATE students
    SET name = %s, phone = %s, course = %s
    WHERE id = %s
    """

    cursor.execute(
        query,
        (name, phone, course, student_id)
    )

    db.commit()
    cursor.close()

    return redirect(url_for("dashboard"))

# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

# -----------------------------
# Teacher Login
# -----------------------------
@app.route("/teacher_login", methods=["GET", "POST"])
def teacher_login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        cursor = db.cursor()

        query = """
        SELECT * FROM teachers
        WHERE email = %s AND password = %s
        """

        cursor.execute(query, (email, password))

        teacher = cursor.fetchone()

        cursor.close()

        if teacher:

            session["teacher_id"] = teacher[0]

            return "Teacher Login Successful!"

        else:

            return "Invalid Teacher Email or Password!"

    return render_template("teacher_login.html")
# -----------------------------
# Run Application
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)