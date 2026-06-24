from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector

app = Flask(__name__)
app.secret_key = "sakthi_secret"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="hospitaldb"
)

def login_required(role=None):
    if "user" not in session:
        return False
    if role and session.get("role") != role:
        return False
    return True

@app.route("/")
def home():
    return render_template("hospital_dashboard.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    role = request.form["role"]

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s AND role=%s", (email, password, role))
    user = cursor.fetchone()
    cursor.close()

    if user:
        session["user"] = user
        session["role"] = role
        return redirect(url_for("dashboard"))
    return "❌ Invalid credentials"

@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("home"))

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()
    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()
    cursor.close()

    return render_template("hospital_dashboard.html",
                           patients=patients,
                           doctors=doctors,
                           patient_count=len(patients),
                           doctor_count=len(doctors))

# ---------------- Patients CRUD ----------------
@app.route("/add_patient", methods=["POST"])
def add_patient():
    if not login_required("Doctor"):
        return redirect(url_for("home"))
    cursor = db.cursor()
    cursor.execute("INSERT INTO patients (name, age, gender, contact, address, disease) VALUES (%s,%s,%s,%s,%s,%s)",
                   (request.form["pname"], request.form["page"], request.form["pgender"],
                    request.form["pcontact"], request.form["paddress"], request.form["disease"]))
    db.commit()
    cursor.close()
    return redirect(url_for("dashboard"))

@app.route("/update_patient/<int:id>", methods=["POST"])
def update_patient(id):
    if not login_required("Doctor"):
        return redirect(url_for("home"))
    cursor = db.cursor()
    cursor.execute("UPDATE patients SET name=%s, age=%s, gender=%s, contact=%s, address=%s, disease=%s WHERE id=%s",
                   (request.form["pname"], request.form["page"], request.form["pgender"],
                    request.form["pcontact"], request.form["paddress"], request.form["disease"], id))
    db.commit()
    cursor.close()
    return redirect(url_for("dashboard"))

@app.route("/delete_patient/<int:id>")
def delete_patient(id):
    if not login_required("Doctor"):
        return redirect(url_for("home"))
    cursor = db.cursor()
    cursor.execute("DELETE FROM patients WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    return redirect(url_for("dashboard"))

# ---------------- Doctors CRUD ----------------
@app.route("/add_doctor", methods=["POST"])
def add_doctor():
    if not login_required("Patient"):
        return redirect(url_for("home"))
    cursor = db.cursor()
    cursor.execute("INSERT INTO doctors (name, speciality, contact, email) VALUES (%s,%s,%s,%s)",
                   (request.form["dname"], request.form["dspeciality"], request.form["dcontact"], request.form["demail"]))
    db.commit()
    cursor.close()
    return redirect(url_for("dashboard"))

@app.route("/update_doctor/<int:id>", methods=["POST"])
def update_doctor(id):
    if not login_required("Patient"):
        return redirect(url_for("home"))
    cursor = db.cursor()
    cursor.execute("UPDATE doctors SET name=%s, speciality=%s, contact=%s, email=%s WHERE id=%s",
                   (request.form["dname"], request.form["dspeciality"], request.form["dcontact"], request.form["demail"], id))
    db.commit()
    cursor.close()
    return redirect(url_for("dashboard"))

@app.route("/delete_doctor/<int:id>")
def delete_doctor(id):
    if not login_required("Patient"):
        return redirect(url_for("home"))
    cursor = db.cursor()
    cursor.execute("DELETE FROM doctors WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)




