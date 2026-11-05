import os
from datetime import datetime
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""),
        database="sports_club",
    )

def query(sql, args=(), commit=False):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(sql, args)
    rows = [] if commit else cur.fetchall()
    if commit:
        db.commit()
    cur.close()
    db.close()
    return rows

# Each section: table, primary key, and its form fields (column, label, type).
# type "fk:table:pk:display" makes a dropdown filled from another table.
ENTITIES = {
    "members": {"title": "Members", "pk": "member_id", "fields": [
        ("name", "Name", "text"), ("age", "Age", "number"),
        ("gender", "Gender", "select:Male,Female,Other"),
        ("phone", "Phone", "text"), ("join_date", "Join Date", "date")]},
    "coaches": {"title": "Coaches", "pk": "coach_id", "fields": [
        ("name", "Name", "text"), ("phone", "Phone", "text"),
        ("speciality", "Speciality", "text")]},
    "sports": {"title": "Sports", "pk": "sport_id", "fields": [
        ("name", "Sport", "text"), ("monthly_fee", "Monthly Fee", "number"),
        ("coach_id", "Coach", "fk:coaches:coach_id:name")]},
    "enrollments": {"title": "Enrollments", "pk": "enroll_id", "fields": [
        ("member_id", "Member", "fk:members:member_id:name"),
        ("sport_id", "Sport", "fk:sports:sport_id:name")]},
    "payments": {"title": "Payments", "pk": "payment_id", "fields": [
        ("member_id", "Member", "fk:members:member_id:name"),
        ("amount", "Amount", "number"), ("pay_date", "Date", "date"),
        ("for_month", "For Month", "select:" + ",".join(MONTHS))]},
}

def list_sql(table, e):
    cols, joins = [f"t.{e['pk']} AS id"], []
    for i, (col, _, typ) in enumerate(e["fields"]):
        if typ.startswith("fk:"):
            _, tbl, pk, disp = typ.split(":")
            cols.append(f"j{i}.{disp} AS `{col}`")
            joins.append(f"LEFT JOIN {tbl} j{i} ON t.{col} = j{i}.{pk}")
        else:
            cols.append(f"t.{col} AS `{col}`")
    return f"SELECT {', '.join(cols)} FROM {table} t {' '.join(joins)} ORDER BY t.{e['pk']}"

def dropdown_options(e):
    opts = {}
    for col, _, typ in e["fields"]:
        if typ.startswith("fk:"):
            _, tbl, pk, disp = typ.split(":")
            opts[col] = query(f"SELECT {pk} AS id, {disp} AS label FROM {tbl}")
    return opts

@app.route("/")
def dashboard():
    stats = {
        "Members": query("SELECT COUNT(*) c FROM members")[0]["c"],
        "Coaches": query("SELECT COUNT(*) c FROM coaches")[0]["c"],
        "Sports": query("SELECT COUNT(*) c FROM sports")[0]["c"],
        "Fees Collected (₹)": query("SELECT COALESCE(SUM(amount),0) c FROM payments")[0]["c"],
    }
    per_sport = query("""SELECT s.name, COUNT(en.enroll_id) AS total
                         FROM sports s LEFT JOIN enrollments en ON s.sport_id = en.sport_id
                         GROUP BY s.sport_id, s.name""")
    return render_template("index.html", stats=stats, per_sport=per_sport, entities=ENTITIES)

@app.route("/pending")
def pending():
    month = request.args.get("month", datetime.now().strftime("%B"))
    rows = query("""
        SELECT m.name, m.phone,
               COALESCE(SUM(s.monthly_fee), 0) AS due,
               (SELECT COALESCE(SUM(p.amount), 0) FROM payments p
                WHERE p.member_id = m.member_id AND p.for_month = %s) AS paid
        FROM members m
        LEFT JOIN enrollments en ON m.member_id = en.member_id
        LEFT JOIN sports s ON en.sport_id = s.sport_id
        GROUP BY m.member_id, m.name, m.phone
        ORDER BY m.name""", (month,))
    for r in rows:
        r["pending"] = r["due"] - r["paid"]
    pending_rows = [r for r in rows if r["pending"] > 0]
    total_pending = sum(r["pending"] for r in pending_rows)
    return render_template("pending.html", rows=pending_rows, month=month, months=MONTHS,
                           total=total_pending, entities=ENTITIES)

@app.route("/<table>")
def show(table):
    e = ENTITIES.get(table)
    if not e:
        return "Not found", 404
    q = request.args.get("q", "").strip()
    rows = query(list_sql(table, e))
    if q:
        rows = [r for r in rows if q.lower() in " ".join(str(v) for v in r.values()).lower()]
    return render_template("list.html", table=table, e=e, rows=rows, q=q, entities=ENTITIES)

@app.route("/<table>/add", methods=["GET", "POST"])
@app.route("/<table>/edit/<int:rid>", methods=["GET", "POST"])
def form(table, rid=None):
    e = ENTITIES.get(table)
    if not e:
        return "Not found", 404
    cols = [f[0] for f in e["fields"]]
    if request.method == "POST":
        vals = [request.form.get(c) or None for c in cols]
        if rid:
            sets = ", ".join(f"{c}=%s" for c in cols)
            query(f"UPDATE {table} SET {sets} WHERE {e['pk']}=%s", vals + [rid], commit=True)
        else:
            marks = ", ".join(["%s"] * len(cols))
            query(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({marks})", vals, commit=True)
        return redirect(url_for("show", table=table))
    row = query(f"SELECT * FROM {table} WHERE {e['pk']}=%s", (rid,))[0] if rid else {}
    return render_template("form.html", table=table, e=e, row=row,
                           opts=dropdown_options(e), entities=ENTITIES)

@app.route("/<table>/delete/<int:rid>", methods=["POST"])
def delete(table, rid):
    e = ENTITIES.get(table)
    if e:
        query(f"DELETE FROM {table} WHERE {e['pk']}=%s", (rid,), commit=True)
    return redirect(url_for("show", table=table))

if __name__ == "__main__":
    app.run(debug=True)
