from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os

app = Flask(__name__)

# Secret key
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "student_management_secret_key"
)

# -----------------------------
# MySQL Database Connection
# -----------------------------
db = mysql.connector.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    user=os.environ.get("DB_USER", "root"),
    password=os.environ.get("DB_PASSWORD", "root"),
    database=os.environ.get("DB_NAME", "student_management"),
    port=int(os.environ.get("DB_PORT", "3306"))
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

    if "student_id" not in session:
        return redirect(url_for("login"))

    student_id = session["student_id"]

    cursor = db.cursor()

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
# Forgot Password
# -----------------------------
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]
        phone = request.form["phone"]
        new_password = request.form["new_password"]

        cursor = db.cursor()

        # Check email and phone
        query = """
        SELECT id FROM students
        WHERE email = %s AND phone = %s
        """

        cursor.execute(query, (email, phone))
        student = cursor.fetchone()

        if student:

            # Update password
            update_query = """
            UPDATE students
            SET password = %s
            WHERE id = %s
            """

            cursor.execute(
                update_query,
                (new_password, student[0])
            )

            db.commit()
            cursor.close()

            return redirect(url_for("login"))

        else:
            cursor.close()
            return "Email and Phone Number do not match!"

    return render_template("forgot_password.html")
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
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )