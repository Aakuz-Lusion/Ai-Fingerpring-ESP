from flask import Flask, request, jsonify, send_from_directory, render_template
import pymysql
import secrets

app = Flask(__name__)

# -----------------------------------------
# DATABASE CONNECTION
# -----------------------------------------
def get_test_conn():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="attendance_test",
        cursorclass=pymysql.cursors.DictCursor,
    )

# -----------------------------------------
# ADMIN LOGIN (POST)
# -----------------------------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "12345"   # change this

@app.route("/admin_login", methods=["POST"])
def admin_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        token = secrets.token_hex(16)
        return jsonify({"status": "ok", "token": token})

    return jsonify({"status": "error"})

# -----------------------------------------
# LOGIN PAGE (GET)
# -----------------------------------------
@app.route("/login")
def login_page():
    return render_template("login.html")

# -----------------------------------------
# MAIN PAGES
# -----------------------------------------
@app.route("/")
def home():
    return render_template("panel.html")

@app.route("/home")
def home_dashboard():
    return render_template("home.html")

@app.route("/logs_page")
def logs_page():
    return render_template("logs.html")

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(".", "favicon.ico")

# -----------------------------------------
# ADD USER
# -----------------------------------------
@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.get_json()
    name = data.get("name")
    finger_id = data.get("finger_id")

    if not name or not finger_id:
        return jsonify({"error": "name and finger_id required"}), 400

    conn = get_test_conn()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO users (name, finger_id, enrolled, delete_flag) VALUES (%s, %s, 0, 0)",
            (name, finger_id),
        )
        conn.commit()
    conn.close()

    return jsonify({"status": "ok"})
@app.route("/edit_name", methods=["POST"])
def edit_name():
    data = request.get_json()
    user_id = data.get("id")
    new_name = data.get("name")

    if not user_id or not new_name:
        return jsonify({"status": "error", "message": "Missing fields"})

    conn = get_test_conn()
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE users SET name = %s WHERE id = %s",
            (new_name, user_id)
        )
        conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

# -----------------------------------------
# PING (ESP8266 connectivity test)
# -----------------------------------------
@app.route("/ping")
def ping():
    return "OK"

# -----------------------------------------
# GET USERS
# -----------------------------------------
@app.route("/users", methods=["GET"])
def get_users():
    conn = get_test_conn()
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT id, name, finger_id, enrolled, delete_flag FROM users ORDER BY id ASC"
        )
        rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

# -----------------------------------------
# SET ENROLL FLAG
# -----------------------------------------
@app.route("/set_enroll", methods=["POST"])
def set_enroll():
    data = request.get_json()
    finger_id = data.get("finger_id")
    enrolled = data.get("enrolled")

    if finger_id is None or enrolled is None:
        return jsonify({"error": "finger_id and enrolled required"}), 400

    conn = get_test_conn()
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE users SET enrolled = %s WHERE finger_id = %s",
            (enrolled, finger_id),
        )
        conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

# -----------------------------------------
# SET DELETE FLAG
# -----------------------------------------
@app.route("/set_delete", methods=["POST"])
def set_delete():
    data = request.get_json()
    finger_id = data.get("finger_id")
    delete_flag = data.get("delete_flag")

    if finger_id is None or delete_flag is None:
        return jsonify({"error": "finger_id and delete_flag required"}), 400

    conn = get_test_conn()
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE users SET delete_flag = %s WHERE finger_id = %s",
            (delete_flag, finger_id),
        )
        conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

# -----------------------------------------
# ESP8266: GET ENROLL QUEUE
# -----------------------------------------
@app.route("/enroll", methods=["GET"])
def enroll_queue():
    conn = get_test_conn()
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT finger_id FROM users WHERE enrolled = 1 AND delete_flag = 0"
        )
        rows = cursor.fetchall()
    conn.close()

    ids = ",".join(str(r["finger_id"]) for r in rows)
    return ids

# -----------------------------------------
# ESP8266: ENROLL DONE
# -----------------------------------------
@app.route("/enroll_done", methods=["POST"])
def enroll_done():
    data = request.get_json()
    finger_id = data.get("finger_id")

    if not finger_id:
        return jsonify({"error": "finger_id required"}), 400

    conn = get_test_conn()
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE users SET enrolled = 2 WHERE finger_id = %s",
            (finger_id,),
        )
        conn.commit()
    conn.close()

    return jsonify({"status": "enrollment_completed"})

# -----------------------------------------
# ESP8266: GET DELETE QUEUE
# -----------------------------------------
@app.route("/delete", methods=["GET"])
def delete_queue():
    conn = get_test_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT finger_id FROM users WHERE delete_flag = 1")
        rows = cursor.fetchall()
    conn.close()

    ids = ",".join(str(r["finger_id"]) for r in rows)
    return ids

# -----------------------------------------
# ESP8266: DELETE DONE
# -----------------------------------------
@app.route("/delete_done", methods=["POST"])
def delete_done():
    data = request.get_json()
    finger_id = data.get("finger_id")

    if not finger_id:
        return jsonify({"error": "finger_id required"}), 400

    conn = get_test_conn()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM users WHERE finger_id = %s", (finger_id,))
        conn.commit()
    conn.close()

    return jsonify({"status": "deletion_completed"})

# -----------------------------------------
# ESP8266 LOG ENDPOINT
# -----------------------------------------
@app.route("/log", methods=["POST"])
def log_attendance():
    data = request.get_json()
    finger_id = data.get("finger_id")
    timestamp = data.get("timestamp")

    if not finger_id or not timestamp:
        return jsonify({"error": "finger_id and timestamp required"}), 400

    date_only = timestamp.split(" ")[0]

    conn = get_test_conn()
    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT id FROM logs
            WHERE finger_id = %s AND DATE(timestamp) = %s
            """,
            (finger_id, date_only)
        )
        exists = cursor.fetchone()

        if exists:
            conn.close()
            return jsonify({"status": "ignored", "reason": "already_logged_today"})

        cursor.execute(
            "INSERT INTO logs (finger_id, timestamp) VALUES (%s, %s)",
            (finger_id, timestamp)
        )
        conn.commit()

    conn.close()
    return jsonify({"status": "logged"})


# -----------------------------------------
# LIVE LOGS VIEWER
# -----------------------------------------
@app.route("/logs", methods=["GET"])
def logs():
    conn = get_test_conn()
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT l.id, l.finger_id, l.timestamp, u.name
            FROM logs l
            LEFT JOIN users u ON l.finger_id = u.finger_id
            ORDER BY l.timestamp DESC
            LIMIT 50
            """
        )
        rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

# -----------------------------------------
# ANALYTICS ROUTES
# -----------------------------------------
@app.route("/stats/total_users")
def total_users():
    conn = get_test_conn()
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM users WHERE delete_flag = 0")
        row = cursor.fetchone()
    conn.close()
    return jsonify(row)

@app.route("/stats/today_pie")
def today_pie():
    conn = get_test_conn()
    with conn.cursor() as cursor:

        cursor.execute("SELECT COUNT(*) AS total FROM users WHERE delete_flag = 0")
        total = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(DISTINCT finger_id) AS present
            FROM logs
            WHERE DATE(timestamp) = CURDATE()
        """)
        present = cursor.fetchone()["present"]

    conn.close()

    absent = total - present

    return jsonify({
        "present": present,
        "absent": absent,
        "total": total
    })

@app.route("/stats/days_present")
def days_present():
    conn = get_test_conn()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT u.name, COUNT(DISTINCT DATE(l.timestamp)) AS days_present
            FROM users u
            LEFT JOIN logs l ON u.finger_id = l.finger_id
            WHERE u.delete_flag = 0
            GROUP BY u.id
            ORDER BY days_present DESC
        """)
        rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

@app.route("/stats/forecast")
def forecast():
    conn = get_test_conn()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT 
                u.name,
                u.finger_id,
                COUNT(DISTINCT DATE(l.timestamp)) AS present_last_7
            FROM users u
            LEFT JOIN logs l 
                ON u.finger_id = l.finger_id
                AND DATE(l.timestamp) >= CURDATE() - INTERVAL 7 DAY
            WHERE u.delete_flag = 0
            GROUP BY u.id
        """)
        rows = cursor.fetchall()
    conn.close()

    for r in rows:
        r["forecast"] = round((r["present_last_7"] / 7) * 100, 2)

    return jsonify(rows)

# .............................................................
@app.route("/stats/ai_insights")
def ai_insights():
    conn = get_test_conn()
    with conn.cursor() as cursor:

        # Total users
        cursor.execute("SELECT COUNT(*) AS total FROM users WHERE delete_flag = 0")
        total_users = cursor.fetchone()["total"]

        # Present today
        cursor.execute("""
            SELECT COUNT(DISTINCT finger_id) AS present
            FROM logs
            WHERE DATE(timestamp) = CURDATE()
        """)
        present_today = cursor.fetchone()["present"]


        # Last 7 days attendance (ordered)
        cursor.execute("""
            SELECT DATE(timestamp) AS day, COUNT(DISTINCT finger_id) AS count
            FROM logs
            WHERE DATE(timestamp) >= CURDATE() - INTERVAL 7 DAY
            GROUP BY DATE(timestamp)
            ORDER BY day ASC
        """)
        rows = cursor.fetchall()

        # Extract labels + values
        last7_days = [str(r["day"]) for r in rows]
        last7_counts = [r["count"] for r in rows]

        # Average for prediction
        avg7 = sum(last7_counts) / len(last7_counts) if last7_counts else 0

        # Predict tomorrow = weighted average
        predicted = round(avg7 * 1.05, 2)

        # Trend detection
        if len(last7_counts) >= 2:
            trend = "Increasing" if last7_counts[-1] > last7_counts[0] else "Decreasing"
        else:
            trend = "Stable"

        # At-risk users (absent 3+ days)
        cursor.execute("""
            SELECT u.name
            FROM users u
            LEFT JOIN logs l ON u.finger_id = l.finger_id
            WHERE u.delete_flag = 0
            GROUP BY u.id
            HAVING COUNT(DISTINCT DATE(l.timestamp)) < 3
        """)
        risk_users = [r["name"] for r in cursor.fetchall()]

        # Peak time today
        cursor.execute("""
            SELECT HOUR(timestamp) AS hour, COUNT(*) AS c
            FROM logs
            WHERE DATE(timestamp) = CURDATE()
            GROUP BY HOUR(timestamp)
            ORDER BY c DESC
            LIMIT 1
        """)
        peak = cursor.fetchone()
        peak_time = f"{peak['hour']}:00" if peak else "No data"

    conn.close()

    # AI summary
    summary = (
        f"AI predicts {predicted}% attendance tomorrow. "
        f"Trend appears {trend.lower()}. "
        f"{len(risk_users)} users show low attendance patterns. "
        f"Peak activity today was around {peak_time}."
    )

    return jsonify({
        "predicted_attendance": predicted,
        "trend": trend,
        "risk_users": risk_users,
        "peak_time": peak_time,
        "summary": summary,
        "last7_days": last7_days,
        "last7_counts": last7_counts,
        "predicted_point": predicted  # optional for graph
    })



# -----------------------------------------
# RUN SERVER
# -----------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

# from flask import Flask, request, jsonify, send_from_directory, render_template, session, redirect, url_for
# import pymysql
# import secrets
# import hashlib
# import time
# from functools import wraps

# app = Flask(__name__)
# app.secret_key = "CHANGE_THIS_TO_A_RANDOM_SECRET_KEY"  # 🔐 required for session

# # -----------------------------------------
# # DATABASE CONNECTION
# # -----------------------------------------
# def get_test_conn():
#     return pymysql.connect(
#         host="localhost",
#         user="root",
#         password="",
#         database="attendance_test",
#         cursorclass=pymysql.cursors.DictCursor,
#     )

# # -----------------------------------------
# # ADMIN AUTH CONFIG (hashed password)
# # -----------------------------------------
# ADMIN_USERNAME = "admin"
# # 🔐 store SHA256 hash instead of plain password "12345"
# ADMIN_PASSWORD_HASH = hashlib.sha256("12345".encode()).hexdigest()
# SESSION_LIFETIME_SECONDS = 3600  # 1 hour

# # -----------------------------------------
# # HELPER: check login & expiration
# # -----------------------------------------
# def is_logged_in():
#     logged = session.get("admin_logged_in", False)
#     expires_at = session.get("expires_at", 0)
#     return logged and time.time() < expires_at

# # -----------------------------------------
# # DECORATOR: protect routes
# # -----------------------------------------
# def login_required(f):
#     @wraps(f)
#     def wrapper(*args, **kwargs):
#         if not is_logged_in():
#             # optional: for API calls you might return 401 instead
#             return redirect(url_for("login_page"))
#         return f(*args, **kwargs)
#     return wrapper

# # -----------------------------------------
# # ADMIN LOGIN (POST, JSON)
# # -----------------------------------------
# @app.route("/admin_login", methods=["POST"])
# def admin_login():
#     data = request.get_json()
#     username = data.get("username")
#     password = data.get("password")

#     if not username or not password:
#         return jsonify({"status": "error", "message": "Missing credentials"})

#     # hash incoming password and compare
#     incoming_hash = hashlib.sha256(password.encode()).hexdigest()

#     if username == ADMIN_USERNAME and incoming_hash == ADMIN_PASSWORD_HASH:
#         # 🔐 set session
#         session["admin_logged_in"] = True
#         session["username"] = username
#         session["expires_at"] = time.time() + SESSION_LIFETIME_SECONDS

#         token = secrets.token_hex(16)  # still return token if you want to keep it in frontend

#         return jsonify({"status": "ok", "token": token})

#     return jsonify({"status": "error", "message": "Invalid credentials"})

# # -----------------------------------------
# # ADMIN LOGOUT (optional)
# # -----------------------------------------
# @app.route("/admin_logout", methods=["POST"])
# def admin_logout():
#     session.clear()
#     return jsonify({"status": "ok"})

# # -----------------------------------------
# # LOGIN PAGE (GET)
# # -----------------------------------------
# @app.route("/login")
# def login_page():
#     # If already logged in and not expired, go to dashboard
#     if is_logged_in():
#         return redirect(url_for("home"))
#     return render_template("login.html")

# # -----------------------------------------
# # MAIN PAGES (protect panel, home, logs)
# # -----------------------------------------
# @app.route("/")
# @login_required
# def home():
#     return render_template("panel.html")

# @app.route("/home")
# @login_required
# def home_dashboard():
#     return render_template("home.html")

# @app.route("/logs_page")
# @login_required
# def logs_page():
#     return render_template("logs.html")

# @app.route("/favicon.ico")
# def favicon():
#     return send_from_directory(".", "favicon.ico")

# # -----------------------------------------
# # ADD USER (admin-only)
# # -----------------------------------------
# @app.route("/add_user", methods=["POST"])
# @login_required
# def add_user():
#     data = request.get_json()
#     name = data.get("name")
#     finger_id = data.get("finger_id")

#     if not name or not finger_id:
#         return jsonify({"error": "name and finger_id required"}), 400

#     conn = get_test_conn()
#     with conn.cursor() as cursor:
#         cursor.execute(
#             "INSERT INTO users (name, finger_id, enrolled, delete_flag) VALUES (%s, %s, 0, 0)",
#             (name, finger_id),
#         )
#         conn.commit()
#     conn.close()

#     return jsonify({"status": "ok"})

# # -----------------------------------------
# # PING (ESP8266 connectivity test) - no auth
# # -----------------------------------------
# @app.route("/ping")
# def ping():
#     return "OK"

# # -----------------------------------------
# # GET USERS (admin-only)
# # -----------------------------------------
# @app.route("/users", methods=["GET"])
# @login_required
# def get_users():
#     conn = get_test_conn()
#     with conn.cursor() as cursor:
#         cursor.execute(
#             "SELECT id, name, finger_id, enrolled, delete_flag FROM users ORDER BY id ASC"
#         )
#         rows = cursor.fetchall()
#     conn.close()
#     return jsonify(rows)

# # -----------------------------------------
# # SET ENROLL FLAG (admin-only)
# # -----------------------------------------
# @app.route("/set_enroll", methods=["POST"])
# @login_required
# def set_enroll():
#     data = request.get_json()
#     finger_id = data.get("finger_id")
#     enrolled = data.get("enrolled")

#     if finger_id is None or enrolled is None:
#         return jsonify({"error": "finger_id and enrolled required"}), 400

#     conn = get_test_conn()
#     with conn.cursor() as cursor:
#         cursor.execute(
#             "UPDATE users SET enrolled = %s WHERE finger_id = %s",
#             (enrolled, finger_id),
#         )
#         conn.commit()
#     conn.close()

#     return jsonify({"status": "ok"})

# # -----------------------------------------
# # SET DELETE FLAG (admin-only)
# # -----------------------------------------
# @app.route("/set_delete", methods=["POST"])
# @login_required
# def set_delete():
#     data = request.get_json()
#     finger_id = data.get("finger_id")
#     delete_flag = data.get("delete_flag")

#     if finger_id is None or delete_flag is None:
#         return jsonify({"error": "finger_id and delete_flag required"}), 400

#     conn = get_test_conn()
#     with conn.cursor() as cursor:
#         cursor.execute(
#             "UPDATE users SET delete_flag = %s WHERE finger_id = %s",
#             (delete_flag, finger_id),
#         )
#         conn.commit()
#     conn.close()

#     return jsonify({"status": "ok"})

# # -----------------------------------------
# # ESP8266: GET ENROLL QUEUE (no auth - device)
# # -----------------------------------------
# @app.route("/enroll", methods=["GET"])
# def enroll_queue():
#     conn = get_test_conn()
#     with conn.cursor() as cursor:
#         cursor.execute(
#             "SELECT finger_id FROM users WHERE enrolled = 1 AND delete_flag = 0"
#         )
#         rows = cursor.fetchall()
#     conn.close()

#     ids = ",".join(str(r["finger_id"]) for r in rows)
#     return ids

# # -----------------------------------------
# # ESP8266: ENROLL DONE (no auth - device)
# # -----------------------------------------
# @app.route("/enroll_done", methods=["POST"])
# def enroll_done():
#     data = request.get_json()
#     finger_id = data.get("finger_id")

#     if not finger_id:
#         return jsonify({"error": "finger_id required"}), 400

#     conn = get_test_conn()
#     with conn.cursor() as cursor:
#         cursor.execute(
#             "UPDATE users SET enrolled = 2 WHERE finger_id = %s",
#             (finger_id,),
#         )
#         conn.commit()
#     conn.close()

#     return jsonify({"status": "enrollment_completed"})

# # -----------------------------------------
# # ESP8266: GET DELETE QUEUE (no auth - device)
# # -----------------------------------------
# @app.route("/delete", methods=["GET"])
# def delete_queue():
#     conn = get_test_conn()
#     with conn.cursor() as cursor:
#         cursor.execute("SELECT finger_id FROM users WHERE delete_flag = 1")
#         rows = cursor.fetchall()
#     conn.close()

#     ids = ",".join(str(r["finger_id"]) for r in rows)
#     return ids

# # -----------------------------------------
# # ESP8266: DELETE DONE (no auth - device)
# # -----------------------------------------
# @app.route("/delete_done", methods=["POST"])
# def delete_done():
#     data = request.get_json()
#     finger_id = data.get("finger_id")

#     if not finger_id:
#         return jsonify({"error": "finger_id required"}), 400

#     conn = get_test_conn()
#     with conn.cursor() as cursor:
#         cursor.execute("DELETE FROM users WHERE finger_id = %s", (finger_id,))
#         conn.commit()
#     conn.close()

#     return jsonify({"status": "deletion_completed"})

# # -----------------------------------------
# # ESP8266: LOG ATTENDANCE (no auth - device)
# # -----------------------------------------
# @app.route("/log", methods=["POST"])
# def log_attendance():
#     data = request.get_json()
#     finger_id = data.get("finger_id")
#     timestamp = data.get("timestamp")

#     if not finger_id or not timestamp:
#         return jsonify({"error": "finger_id and timestamp required"}), 400

#     date_only = timestamp.split(" ")[0]

#     conn = get_test_conn()
#     with conn.cursor() as cursor:

#         cursor.execute(
#             """
#             SELECT id FROM logs
#             WHERE finger_id = %s AND DATE(timestamp) = %s
#             """,
#             (finger_id, date_only)
#         )
#         exists = cursor.fetchone()

#         if exists:
#             conn.close()
#             return jsonify({"status": "ignored", "reason": "already_logged_today"})

#         cursor.execute(
#             "INSERT INTO logs (finger_id, timestamp) VALUES (%s, %s)",
#             (finger_id, timestamp)
#         )
#         conn.commit()

#     conn.close()
#     return jsonify({"status": "logged"})

# # -----------------------------------------
# # LIVE LOGS VIEWER (admin-only)
# # -----------------------------------------
# @app.route("/logs", methods=["GET"])
# @login_required
# def logs():
#     conn = get_test_conn()
#     with conn.cursor() as cursor:
#         cursor.execute(
#             """
#             SELECT l.id, l.finger_id, l.timestamp, u.name
#             FROM logs l
#             LEFT JOIN users u ON l.finger_id = u.finger_id
#             ORDER BY l.timestamp DESC
#             LIMIT 50
#             """
#         )
#         rows = cursor.fetchall()
#     conn.close()
#     return jsonify(rows)

# # -----------------------------------------
# # ANALYTICS ROUTES (admin-only)
# # -----------------------------------------
# @app.route("/stats/total_users")
# @login_required
# def total_users():
#     conn = get_test_conn()
#     with conn.cursor() as cursor:
#         cursor.execute("SELECT COUNT(*) AS total FROM users WHERE delete_flag = 0")
#         row = cursor.fetchone()
#     conn.close()
#     return jsonify(row)

# @app.route("/stats/today_pie")
# @login_required
# def today_pie():
#     conn = get_test_conn()
#     with conn.cursor() as cursor:

#         cursor.execute("SELECT COUNT(*) AS total FROM users WHERE delete_flag = 0")
#         total = cursor.fetchone()["total"]

#         cursor.execute("""
#             SELECT COUNT(DISTINCT finger_id) AS present
#             FROM logs
#             WHERE DATE(timestamp) = CURDATE()
#         """)
#         present = cursor.fetchone()["present"]

#     conn.close()

#     absent = total - present

#     return jsonify({
#         "present": present,
#         "absent": absent,
#         "total": total
#     })

# @app.route("/stats/days_present")
# @login_required
# def days_present():
#     conn = get_test_conn()
#     with conn.cursor() as cursor:
#         cursor.execute("""
#             SELECT u.name, COUNT(DISTINCT DATE(l.timestamp)) AS days_present
#             FROM users u
#             LEFT JOIN logs l ON u.finger_id = l.finger_id
#             WHERE u.delete_flag = 0
#             GROUP BY u.id
#             ORDER BY days_present DESC
#         """)
#         rows = cursor.fetchall()
#     conn.close()
#     return jsonify(rows)

# @app.route("/stats/forecast")
# @login_required
# def forecast():
#     conn = get_test_conn()
#     with conn.cursor() as cursor:
#         cursor.execute("""
#             SELECT 
#                 u.name,
#                 u.finger_id,
#                 COUNT(DISTINCT DATE(l.timestamp)) AS present_last_7
#             FROM users u
#             LEFT JOIN logs l 
#                 ON u.finger_id = l.finger_id
#                 AND DATE(l.timestamp) >= CURDATE() - INTERVAL 7 DAY
#             WHERE u.delete_flag = 0
#             GROUP BY u.id
#         """)
#         rows = cursor.fetchall()
#     conn.close()

#     for r in rows:
#         r["forecast"] = round((r["present_last_7"] / 7) * 100, 2)

#     return jsonify(rows)

# # -----------------------------------------
# # RUN SERVER
# # -----------------------------------------
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)
