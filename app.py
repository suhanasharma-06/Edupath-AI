from flask import Flask, render_template, request, jsonify
import mysql.connector
import re

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="college_chatbot"
)

cursor = db.cursor(dictionary=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json

    step = data.get("step")
    value = data.get("value", "")
    name = data.get("name", "")

    v = value.lower()

    # ================= START =================
    if step == "start":
        return jsonify({"reply": "Hi 😊 What's your name?", "next": "get_name"})

    if step == "get_name":
        return jsonify({
            "reply": f"Nice to meet you, {value} 🎓\n\nHow would you like to proceed?",
            "options": ["Guided 🎯", "Manual ✍️"],
            "next": "mode",
            "name": value
        })

    if step == "mode":
        if "guided" in v:
            return jsonify({
                "reply": "Choose state:",
                "options": ["Punjab", "Haryana", "Chandigarh", "All"],
                "next": "state",
                "name": name
            })
        else:
            return jsonify({
                "reply": "Try:\n👉 NIT Jalandhar scholarship\n👉 hostel NIT\n👉 CSE colleges in Punjab\n👉 jee 90 percentage 80",
                "next": "manual",
                "name": name
            })

    # ================= GUIDED =================
    if step == "state":
        return jsonify({
            "reply": "Choose type:",
            "options": ["Government", "Private", "Both"],
            "next": "type",
            "state": value,
            "name": name
        })

    if step == "type":
        return jsonify({
            "reply": "Select branch:",
            "options": ["CSE", "AI/ML", "ECE", "Mechanical"],
            "next": "branch",
            "name": name
        })

    if step == "branch":
        return jsonify({"reply": "Enter JEE score:", "next": "jee", "name": name})

    if step == "jee":
        return jsonify({"reply": "Enter 12th %:", "next": "percentage", "jee": value, "name": name})

    if step == "percentage":
        return jsonify({"reply": "Enter budget:", "next": "budget", "percentage": value, "name": name})

    # ================= FETCH =================
    if step == "budget":
        try:
            budget = int(value)
        except:
            return jsonify({"reply": "Enter valid budget ⚠️"})

        cursor.execute("""
        SELECT college_name FROM colleges
        WHERE avg_fee <= %s + 70000
        LIMIT 8
        """, (budget,))

        res = cursor.fetchall()
        options = [r["college_name"] for r in res]

        if not options:
            cursor.execute("SELECT college_name FROM colleges LIMIT 8")
            options = [r["college_name"] for r in cursor.fetchall()]

        return jsonify({
            "reply": "Best colleges 👇",
            "options": options,
            "next": "details",
            "college_list": options,
            "jee": data.get("jee"),
            "percentage": data.get("percentage"),
            "name": name
        })

    # ================= DETAILS =================
    if step == "details":

        cursor.execute("""
        SELECT c.*,h.ac_fee,h.non_ac_fee
        FROM colleges c
        LEFT JOIN hostel h ON c.id=h.college_id
        WHERE LOWER(c.college_name)=LOWER(%s)
        """, (value,))

        c = cursor.fetchone()

        reply = f"""
<div class="card">
<h2>🎓 {c['college_name']}</h2>

📍 {c['city']}, {c['state']}<br>
💰 ₹{c['avg_fee']}<br>
📊 ₹{c['avg_placement_salary']}<br>
🏠 AC: ₹{c.get('ac_fee')} | Non-AC: ₹{c.get('non_ac_fee')}<br>

<a href="{c['map_link']}" target="_blank">📍 View Map</a><br><br>

<iframe width="100%" height="200" src="{c['campus_tour']}"></iframe><br>

<img src="{c['image_link']}" width="100%">
</div>
"""

        return jsonify({
            "reply": reply,
            "options": ["Faculty", "Scholarship", "Placement", "Contact", "Back"],
            "next": "details_options",
            "college": c["college_name"],
            "college_list": data.get("college_list", []),
            "jee": data.get("jee"),
            "percentage": data.get("percentage"),
            "name": name
        })

    # ================= DETAILS OPTIONS =================
    if step == "details_options":

        college = data.get("college")

        # -------- FACULTY --------
        if "faculty" in v:
            cursor.execute("""
            SELECT f.faculty_name,f.designation,b.branch_name
            FROM faculty f
            JOIN branches b ON f.branch_id=b.id
            JOIN colleges c ON b.college_id=c.id
            WHERE LOWER(c.college_name)=LOWER(%s)
            """, (college,))
            res = cursor.fetchall()

            reply = "<div class='card'>"
            for r in res:
                reply += f"{r['faculty_name']} ({r['designation']}) - {r['branch_name']}<br>"
            reply += "</div>"

        # -------- SCHOLARSHIP --------
        elif "scholarship" in v:
            percentage = int(data.get("percentage") or 0)
            jee = int(data.get("jee") or 0)

            cursor.execute("""
            SELECT b.branch_name, b.min_percentage, b.min_jee
            FROM branches b
            JOIN colleges c ON b.college_id = c.id
            WHERE LOWER(c.college_name)=LOWER(%s)
            """, (college,))
            res = cursor.fetchall()

            reply = "<div class='card'><b>🎓 Scholarship</b><br><br>"

            for r in res:
                score_gap = (percentage - r['min_percentage']) + (jee - r['min_jee'])

                if score_gap >= 20:
                    percent = "80%"
                elif score_gap >= 10:
                    percent = "60%"
                elif score_gap >= 5:
                    percent = "40%"
                else:
                    percent = "20%"

                reply += f"""
                <b>{r['branch_name']}</b><br>
                Required: {r['min_percentage']}% | JEE {r['min_jee']}<br>
                Your Score: {percentage}% | JEE {jee}<br>
                👉 You get: <span style='color:#22c55e'>{percent}</span><br><br>
                """

            reply += """
            <hr>
            <b>📊 Rules:</b><br>
            90+ → 80%<br>
            80+ → 60%<br>
            70+ → 40%<br>
            below 70 → 20%
            </div>
            """

        # -------- PLACEMENT --------
        elif "placement" in v:
            cursor.execute("""
            SELECT b.branch_name, p.min_package, p.avg_package, p.highest_package
            FROM placements p
            JOIN branches b ON p.branch_id = b.id
            JOIN colleges c ON p.college_id = c.id
            WHERE LOWER(c.college_name)=LOWER(%s)
            """, (college,))
            res = cursor.fetchall()

            reply = "<div class='card'><b>📊 Placement</b><br><br>"

            for r in res:
                reply += f"{r['branch_name']} → Min ₹{r['min_package']} | Avg ₹{r['avg_package']} | Highest ₹{r['highest_package']}<br>"

            reply += "</div>"

        # -------- CONTACT --------
        elif "contact" in v:
            cursor.execute("""
            SELECT phone,email,website FROM contact ct
            JOIN colleges c ON ct.college_id=c.id
            WHERE LOWER(c.college_name)=LOWER(%s)
            """, (college,))
            c = cursor.fetchone()

            reply = f"<div class='card'>{c['phone']}<br>{c['email']}<br>{c['website']}</div>"

        # -------- BACK --------
        elif "back" in v:
            return jsonify({
                "reply": "Choose another college 👇",
                "options": data.get("college_list", []),
                "next": "details",
                "name": name
            })

        return jsonify({
            "reply": reply,
            "options": ["Faculty", "Scholarship", "Placement", "Contact", "Back"],
            "next": "details_options",
            "college": college,
            "jee": data.get("jee"),
            "percentage": data.get("percentage"),
            "name": name
        })

    # ================= MANUAL =================
    if step == "manual":

        cursor.execute("SELECT college_name FROM colleges")
        all_colleges = [c["college_name"] for c in cursor.fetchall()]

        matched = None
        for col in all_colleges:
            if col.lower() in v:
                matched = col
                break

        if matched:
            return jsonify({
                "reply": f"{matched} selected 👇",
                "options": ["Faculty", "Scholarship", "Placement", "Contact"],
                "next": "details_options",
                "college": matched,
                "name": name
            })

        nums = list(map(int, re.findall(r'\d+', v)))

        if len(nums) >= 2:
            cursor.execute("SELECT college_name FROM colleges LIMIT 8")
            options = [r["college_name"] for r in cursor.fetchall()]

            return jsonify({
                "reply": "Best colleges 👇",
                "options": options,
                "next": "details",
                "name": name
            })

        return jsonify({"reply": "Try proper query 😊"})

    return jsonify({"reply": "Try again 🙂"})


if __name__ == "__main__":
    app.run(debug=True)