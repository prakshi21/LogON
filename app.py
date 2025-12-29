from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
current_mode = "mess"  # Default mode

# Database connection config
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "mysql@pass",
    "database": "CSE24"
}

@app.route("/")
def home():
    return render_template("website.html")

@app.route('/student-login.html')
def student_login():
    return render_template('student-login.html')

@app.route('/teacher-login.html')
def teacher_login():
    return render_template('teacher-login.html')

@app.route('/mode_selector.html')
def mode_selector():
    return render_template('mode_selector.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

@app.route("/set_mode", methods=["POST"])
def set_mode():
    global current_mode
    mode = request.form.get("mode")

    if mode in ["attendance", "mess"]:
        current_mode = mode
        if mode == "attendance":
            return redirect(url_for('teacher_login'))
        elif mode == "mess":
            return redirect(url_for('home'))
    return jsonify({"error": "Invalid mode"}), 400

@app.route('/student-dashboard', methods=['POST'])
def student_dashboard():
    student_id = request.form['student_id']

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT name FROM Students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        if not student:
            return jsonify({"error": "Student not found"}), 404
        student_name = student["name"]

        cursor.execute("SELECT subject_id, name FROM Subjects")
        subjects = cursor.fetchall()

        attendance_report = []

        for subject in subjects:
            subject_id = subject["subject_id"]
            subject_name = subject["name"]

            cursor.execute("""
                SELECT COUNT(*) AS total_sessions 
                FROM Active_Sessions 
                WHERE subject_id = %s
            """, (subject_id,))
            total_sessions = cursor.fetchone()["total_sessions"]

            cursor.execute("""
                SELECT COUNT(DISTINCT r.session_id) AS attended 
                FROM RFID_Log r
                JOIN Active_Sessions s ON r.session_id = s.session_id
                WHERE r.student_id = %s AND s.subject_id = %s
            """, (student_id, subject_id))
            attended = cursor.fetchone()["attended"]

            percentage = (attended / total_sessions * 100) if total_sessions > 0 else 0
            status = "Above 75%" if percentage >= 75 else "Below 75%"

            attendance_report.append({
                "subject": subject_name,
                "attended": attended,
                "total_classes": total_sessions,
                "percentage": round(percentage, 2),
                "status": status
            })

        cursor.execute("""
            SELECT mt.meal_type, COUNT(*) AS count, mt.price
            FROM Meal_Logs ml
            JOIN Meal_Timings mt ON ml.meal_type = mt.meal_type
            WHERE ml.student_id = %s
            GROUP BY mt.meal_type, mt.price
        """, (student_id,))
        meal_rows = cursor.fetchall()

        meals = []
        total_expense = 0

        for row in meal_rows:
            meal_type = row["meal_type"]
            count = row["count"]
            price = row["price"]
            subtotal = count * price
            total_expense += subtotal

            meals.append({
                "meal_type": meal_type,
                "count": count,
                "price": price,
                "subtotal": subtotal
            })

        return render_template(
            'dashboard.html',
            student_id=student_id,
            student_name=student_name,
            attendance=attendance_report,
            meals=meals,
            total_expense=total_expense
        )

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/teacher-dashboard', methods=['POST'])
def teacher_dashboard():
    teacher_id = request.form['teacher_id']

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Teachers WHERE teacher_id = %s", (teacher_id,))
        teacher = cursor.fetchone()

        if not teacher:
            return render_template("teacher-login.html", error="Invalid Teacher ID")

        cursor.execute("""
            SELECT subject_id, name FROM Subjects WHERE teacher_id = %s
        """, (teacher_id,))
        subjects = cursor.fetchall()

        if not subjects:
            return render_template("subject-login.html", teacher_id=teacher_id, subjects=[], message="No subjects assigned.")

        return render_template("subject-login.html", teacher_id=teacher_id, subjects=subjects)

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/start_session", methods=["POST"])
def start_session():
    teacher_id = request.form.get("teacher_id")
    subject_id = request.form.get("subject_id")

    if not teacher_id or not subject_id:
        return "teacher_id and subject_id are required", 400

    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=5)

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = """
            INSERT INTO Active_Sessions (subject_id, teacher_id, start_time, end_time)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (subject_id, teacher_id, start_time, end_time))
        conn.commit()

        return redirect(url_for('session_active_page', subject_id=subject_id))

    except mysql.connector.Error as err:
        return f"Database error: {err}", 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route("/session_active")
def session_active_page():
    subject_id = request.args.get("subject_id")
    return render_template("session_active.html", subject_id=subject_id)

@app.route("/scan_rfid", methods=["POST"])
def scan_rfid():
    global current_mode
    data = request.get_json()

    rfid_tag = data.get("rfid_tag")
    if not rfid_tag:
        return jsonify({"error": "rfid_tag is required"}), 400

    print(f"[INFO] Received RFID tag: {rfid_tag} | Mode: {current_mode}")

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Students WHERE student_id = %s", (rfid_tag,))
        if not cursor.fetchone():
            print(f"[WARN] Student {rfid_tag} not found in database.")
            return jsonify({"error": "Student not found"}), 404

        if current_mode == "attendance":
            cursor.execute("""
                SELECT session_id, subject_id FROM Active_Sessions
                WHERE NOW() BETWEEN start_time AND end_time
                ORDER BY start_time DESC LIMIT 1
            """)
            session = cursor.fetchone()
            if not session:
                print("[WARN] No active session found.")
                return jsonify({"error": "No active session found"}), 404

            session_id, subject_id = session

            cursor.execute("""
                SELECT * FROM RFID_Log 
                WHERE student_id = %s AND session_id = %s
            """, (rfid_tag, session_id))
            if cursor.fetchone():
                return jsonify({"message": "Attendance already recorded"})

            cursor.execute("""
                INSERT INTO RFID_Log (student_id, session_id, subject_id, rfid_tag)
                VALUES (%s, %s, %s, %s)
            """, (rfid_tag, session_id, subject_id, rfid_tag))
            conn.commit()

            print(f"[SUCCESS] Attendance recorded for student {rfid_tag}")
            return jsonify({
                "message": "Attendance recorded",
                "mode": current_mode
            })

        elif current_mode == "mess":
            now = datetime.now()
            current_time = now.time()

            cursor.execute("""
                SELECT meal_type FROM Meal_Timings
                WHERE %s BETWEEN start_time AND end_time
                LIMIT 1
            """, (current_time,))
            meal = cursor.fetchone()

            if not meal:
                return jsonify({"error": "No meal timing matched"}), 400

            meal_type = meal[0]

            cursor.execute("""
                INSERT INTO Meal_Logs (student_id, meal_type, scanned_at)
                VALUES (%s, %s, NOW())
            """, (rfid_tag, meal_type))
            conn.commit()

            print(f"[SUCCESS] Meal logged for student {rfid_tag}, meal: {meal_type}")
            return jsonify({
                "message": "Meal logged",
                "mode": current_mode,
                "meal_type": meal_type
            })

        else:
            return jsonify({"error": "Invalid mode selected"}), 400

    except mysql.connector.Error as err:
        print(f"[ERROR] MySQL Error: {err}")
        return jsonify({"error": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
 
if __name__ == '__main__':
      app.run(debug=True)