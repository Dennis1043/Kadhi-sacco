
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)  # allows frontend JS to call backend APIs

# Database config (update with your MySQL login info)
db_config = {
    "host": "localhost",
    "user": "root",       # change to your username
    "password": "@Dennis1043",       # change to your password
    "database": "kadhi"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# ========================
# FRONTEND ROUTES
# ========================
@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")


# ========================
# BACKEND ROUTES (APIs)
# ========================

@app.route("/register", methods=["POST"])
def register_user():
    data = request.json
    required_fields = ["firebase_uid", "name", "phone", "email", "role"]
    
    # Check if all required fields are present
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400

    firebase_uid = data["firebase_uid"]
    name = data["name"]
    phone = data["phone"]
    email = data["email"]
    role = data["role"]

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Use INSERT ... ON DUPLICATE KEY UPDATE
        sql = """
        INSERT INTO users (firebase_uid, name, phone, email, role)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            name=%s,
            phone=%s,
            email=%s,
            role=%s
        """
        values = (firebase_uid, name, phone, email, role, name, phone, email, role)
        cursor.execute(sql, values)
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "User registered/updated successfully"}), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



@app.route("/save_fcm", methods=["POST"])
def save_fcm():
    data = request.json
    if "firebase_uid" not in data or "token" not in data:
        return jsonify({"error": "Missing fields"}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Find user ID by firebase_uid
        cursor.execute("SELECT id FROM users WHERE firebase_uid=%s", (data["firebase_uid"],))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404

        sql = "INSERT IGNORE INTO fcm_tokens (user_id, token) VALUES (%s, %s)"
        cursor.execute(sql, (user["id"], data["token"]))
        conn.commit()

        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Token saved"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/user", methods=["GET"])
def get_user():
    uid = request.args.get("uid")
    if not uid:
        return jsonify({"error": "uid required"}), 400
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, role FROM users WHERE firebase_uid=%s", (uid,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            return jsonify({"error": "User not found"}), 404
        return jsonify(row)
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route("/notifications", methods=["GET"])
def get_notifications():
    uid = request.args.get("uid")
    if not uid:
        return jsonify({"error": "uid required"}), 400
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, message, read_flag
            FROM notifications
            WHERE firebase_uid=%s AND read_flag=0
        """, (uid,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"rows": rows})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
from flask import request



@app.route("/contributions/add", methods=["POST"])
def add_contribution():
    try:
        user_uid = request.form.get("user_id")
        amount = request.form.get("amount")
        purpose = request.form.get("purpose")
        mpesa_code = request.form.get("mpesaCode")
        screenshot = request.files.get("screenshot")  # optional

        if not user_uid or not amount:
            return jsonify({"error": "user_id and amount are required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Find MySQL user_id using Firebase UID
        cursor.execute("SELECT id FROM users WHERE firebase_uid=%s", (user_uid,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_id = user["id"]

        # Save contribution
        cursor.execute("""
            INSERT INTO contributions (user_id, amount, contribution_date, purpose, mpesa_code, status)
            VALUES (%s, %s, CURDATE(), %s, %s, 'pending')
        """, (user_id, amount, purpose, mpesa_code))

        conn.commit()

        # (Optional) Handle screenshot later: e.g., save to uploads folder
        # if screenshot:
        #     screenshot.save(f"uploads/{user_id}_{screenshot.filename}")

        cursor.close()
        conn.close()

        return jsonify({"message": "Contribution submitted successfully"}), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



# === My Contributions (per member) ===
@app.route("/contributions/my")
def my_contributions():
    uid = request.args.get("uid")
    if not uid:
        return jsonify({"error": "Missing uid"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.id, c.amount, c.purpose, c.mpesa_code, c.status, c.timestamp, 
               u.name AS member_name
        FROM contributions c
        JOIN users u ON c.user_id = u.id
        WHERE u.firebase_uid = %s
        ORDER BY c.timestamp DESC
    """, (uid,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"rows": rows})


# === All Contributions (admin view or totals) ===
@app.route("/contributions/all")
def all_contributions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.id, c.amount, c.purpose, c.mpesa_code, c.status, c.timestamp, 
               u.name AS member_name
        FROM contributions c
        JOIN users u ON c.user_id = u.id
        ORDER BY c.timestamp DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"rows": rows})


@app.route("/admin/notifications")
def admin_notifications():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM contributions WHERE status='pending'")
    contributions = cursor.fetchall()

    cursor.execute("SELECT * FROM loan_requests WHERE status='pending'")
    loans = cursor.fetchall()

    cursor.execute("SELECT * FROM loan_repayments WHERE status='pending'")
    repayments = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify({
        "contributions": contributions,
        "loans": loans,
        "repayments": repayments
    })

@app.route("/admin/totals")
def admin_totals():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT SUM(amount) as total FROM contributions WHERE status='approved'")
    contrib_total = cursor.fetchone()["total"] or 0

    cursor.execute("SELECT SUM(amount) as total FROM loan_requests WHERE status='approved'")
    loan_total = cursor.fetchone()["total"] or 0

    cursor.close()
    conn.close()
    return jsonify({
        "contributions": contrib_total,
        "loans": loan_total
    })


@app.route("/loans/all")
def all_loans():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM loan_requests ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"rows": rows})

@app.route("/loans/update", methods=["POST"])
def update_loan_status():
    data = request.json
    loan_id = data.get("id")
    status = data.get("status")
    if status not in ["approved", "rejected"]:
        return jsonify({"error": "Invalid status"}), 400

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("UPDATE loan_requests SET status=%s WHERE id=%s", (status, loan_id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True, "message": f"Loan {status}"})

@app.route("/summary/members")
def summary_members():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users")
    users = {row["id"]: row | {"totalContribution": 0, "totalLoan": 0, "totalFines": 0} for row in cursor.fetchall()}

    cursor.execute("SELECT user_id, SUM(amount) as total FROM contributions WHERE status='approved' GROUP BY user_id")
    for row in cursor.fetchall():
        if row["user_id"] in users:
            users[row["user_id"]]["totalContribution"] = float(row["total"])

    cursor.execute("SELECT user_id, SUM(amount) as total FROM loan_requests WHERE status='approved' GROUP BY user_id")
    for row in cursor.fetchall():
        if row["user_id"] in users:
            users[row["user_id"]]["totalLoan"] = float(row["total"])

    cursor.execute("SELECT user_id, SUM(amount) as total FROM fines GROUP BY user_id")
    for row in cursor.fetchall():
        if row["user_id"] in users:
            users[row["user_id"]]["totalFines"] = float(row["total"])

    cursor.close(); conn.close()
    return jsonify({"members": list(users.values())})


@app.route("/summary/loans")
def summary_loans():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM loan_requests ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return jsonify({"loans": rows})


@app.route("/summary/fines")
def summary_fines():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM fines ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return jsonify({"fines": rows})

@app.route("/repayments")
def get_repayments():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.*, u.name 
        FROM loan_repayments r 
        LEFT JOIN users u ON r.user_id = u.id
        ORDER BY r.timestamp DESC
    """)
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return jsonify({"repayments": rows})


@app.route("/repayments/<int:repayment_id>/status", methods=["POST"])
def update_repayment_status(repayment_id):
    data = request.json
    status = data.get("status")
    if status not in ["approved", "rejected"]:
        return jsonify({"error": "Invalid status"}), 400

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("UPDATE loan_repayments SET status=%s WHERE id=%s", (status, repayment_id))
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({"message": f"Repayment {status}"})

@app.route("/contributions")
def get_contributions():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.*, u.name 
        FROM contributions c 
        LEFT JOIN users u ON c.user_id = u.id
        ORDER BY c.timestamp DESC
    """)
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return jsonify({"contributions": rows})


@app.route("/contributions/<int:contrib_id>/status", methods=["POST"])
def update_contribution_status(contrib_id):
    data = request.json
    status = data.get("status")
    if status not in ["approved", "rejected"]:
        return jsonify({"error": "Invalid status"}), 400

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("UPDATE contributions SET status=%s WHERE id=%s", (status, contrib_id))
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({"message": f"Contribution {status}"})


@app.route("/settings", methods=["GET"])
def get_settings():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM settings WHERE id=1")
    row = cursor.fetchone()
    cursor.close(); conn.close()
    return jsonify(row if row else {})

@app.route("/settings", methods=["POST"])
def save_settings():
    data = request.json
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO settings 
        (id, monthly_contribution, loan_interest, default_fine, grace_period, contribution_duration, next_contribution_date)
        VALUES (1, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        monthly_contribution=VALUES(monthly_contribution),
        loan_interest=VALUES(loan_interest),
        default_fine=VALUES(default_fine),
        grace_period=VALUES(grace_period),
        contribution_duration=VALUES(contribution_duration),
        next_contribution_date=VALUES(next_contribution_date)
    """, (
        data.get("monthlyContribution"),
        data.get("loanInterest"),
        data.get("defaultFine"),
        data.get("gracePeriod"),
        data.get("contributionDuration"),
        data.get("nextContributionDate")
    ))
    conn.commit()
    cursor.close(); conn.close()
    return jsonify({"message": "Settings saved successfully"})

@app.route("/api/balance/<user_id>", methods=["GET"])
def get_balance(user_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Contributions
        cursor.execute("SELECT IFNULL(SUM(amount), 0) as total FROM contributions WHERE userId = %s", (user_id,))
        contrib_total = cursor.fetchone()["total"]

        # Loans
        cursor.execute("SELECT IFNULL(SUM(amount), 0) as total FROM loans WHERE userId = %s", (user_id,))
        loan_total = cursor.fetchone()["total"]

        # Repayments
        cursor.execute("SELECT IFNULL(SUM(amount), 0) as total FROM repayments WHERE userId = %s", (user_id,))
        repay_total = cursor.fetchone()["total"]

        cursor.close()
        conn.close()

        return jsonify({
            "contributions": contrib_total,
            "loans": loan_total,
            "repayments": repay_total
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---- Loan Request ----
@app.route("/api/loans/request", methods=["POST"])
def request_loan():
    data = request.json
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO loans (userId, name, phone, amount, purpose, months, status, timestamp)
            VALUES (%s,%s,%s,%s,%s,%s,'pending', NOW())
        """, (data["userId"], data["name"], data["phone"], data["amount"], data["purpose"], data["months"]))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Loan requested successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---- Loan Repayment ----
@app.route("/api/loans/repay", methods=["POST"])
def repay_loan():
    data = request.json
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO repayments (userId, phone, amount, mpesaCode, note, status, timestamp)
            VALUES (%s,%s,%s,%s,%s,'pending', NOW())
        """, (data["userId"], data["phone"], data["amount"], data["mpesaCode"], data.get("note","")))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Repayment submitted, awaiting admin approval"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ---- Loan & Repayment History ----
@app.route("/api/loans/history/<user_id>", methods=["GET"])
def loan_history(user_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM loans WHERE userId=%s", (user_id,))
        loans = cursor.fetchall()

        cursor.execute("SELECT * FROM repayments WHERE userId=%s", (user_id,))
        repayments = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({"loans": loans, "repayments": repayments})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/user-fines/<user_id>", methods=["GET"])
def user_fines(user_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM fines WHERE user_id = %s ORDER BY timestamp DESC", (user_id,))
    fines = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert datetime to string for JSON
    for f in fines:
        if "timestamp" in f and f["timestamp"]:
            f["timestamp"] = f["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

    return jsonify(fines)


# --- FALLBACK STATIC ROUTE LAST ---
@app.route("/<path:filename>")
def serve_static_files(filename):
    return send_from_directory(".", filename)


# ========================
# START SERVER
# ========================
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
