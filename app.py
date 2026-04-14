"""
CUBAL - Flask Web Application
Run with: python app.py
Then open: http://localhost:5000
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from models.database import init_db
from models.repository import (
    DonorRepository, RecipientRepository, SOSRepository,
    ResponseRepository, AuditRepository
)
from services.registration import register_donor, register_recipient
from services.sos_service import raise_sos, handle_response
from models.entities import VALID_BLOOD_TYPES

app = Flask(__name__)
app.secret_key = "cubal_secret_2024"

init_db()


# ── Home ──────────────────────────────────────────────────────
@app.route("/")
def index():
    donors     = DonorRepository.get_all()
    requests   = SOSRepository.get_all()
    open_reqs  = SOSRepository.get_open()
    audit      = AuditRepository.get_all()[:8]
    stats = {
        "total_donors":     len(donors),
        "available_donors": sum(1 for d in donors if d["is_available"]),
        "open_requests":    len(open_reqs),
        "total_fulfilled":  sum(1 for r in requests if r["status"] == "fulfilled"),
    }
    return render_template("index.html", stats=stats, open_requests=open_reqs, audit=audit)


# ── Donor registration ────────────────────────────────────────
@app.route("/register/donor", methods=["GET", "POST"])
def register_donor_view():
    if request.method == "POST":
        try:
            donor = register_donor(
                name       = request.form["name"],
                age        = int(request.form["age"]),
                blood_type = request.form["blood_type"],
                city       = request.form["city"],
                latitude   = float(request.form["latitude"]),
                longitude  = float(request.form["longitude"]),
                phone      = request.form["phone"],
            )
            flash(f"Welcome, {donor.name}! You are now registered as a donor.", "success")
            return redirect(url_for("donors"))
        except Exception as e:
            flash(str(e), "error")
    return render_template("register_donor.html", blood_types=sorted(VALID_BLOOD_TYPES))


# ── Recipient registration ────────────────────────────────────
@app.route("/register/recipient", methods=["GET", "POST"])
def register_recipient_view():
    if request.method == "POST":
        try:
            recipient = register_recipient(
                name       = request.form["name"],
                age        = int(request.form["age"]),
                blood_type = request.form["blood_type"],
                city       = request.form["city"],
                latitude   = float(request.form["latitude"]),
                longitude  = float(request.form["longitude"]),
                phone      = request.form["phone"],
            )
            flash(f"Registered successfully, {recipient.name}.", "success")
            return redirect(url_for("raise_sos_view", recipient_id=recipient.recipient_id))
        except Exception as e:
            flash(str(e), "error")
    return render_template("register_recipient.html", blood_types=sorted(VALID_BLOOD_TYPES))


# ── Raise SOS ─────────────────────────────────────────────────
@app.route("/sos/raise", methods=["GET", "POST"])
@app.route("/sos/raise/<recipient_id>", methods=["GET", "POST"])
def raise_sos_view(recipient_id=None):
    recipients = RecipientRepository.get_all() if hasattr(RecipientRepository, "get_all") else []
    if request.method == "POST":
        try:
            rid = request.form.get("recipient_id") or recipient_id
            result = raise_sos(
                recipient_id = rid,
                blood_type   = request.form["blood_type"],
                units_needed = int(request.form.get("units_needed", 1)),
                urgency      = request.form.get("urgency", "high"),
                message      = request.form.get("message", ""),
            )
            flash(f"SOS raised! {len(result.get('matched', []))} donor(s) notified.", "success")
            return redirect(url_for("request_detail", request_id=result["request"]["request_id"]))
        except Exception as e:
            flash(str(e), "error")

    all_recipients = _get_all_recipients()
    return render_template(
        "raise_sos.html",
        blood_types=sorted(VALID_BLOOD_TYPES),
        recipients=all_recipients,
        selected_id=recipient_id,
    )


def _get_all_recipients():
    conn = __import__("models.database", fromlist=["get_connection"]).get_connection()
    rows = conn.execute("SELECT * FROM recipients").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Donors list ───────────────────────────────────────────────
@app.route("/donors")
def donors():
    all_donors = DonorRepository.get_all()
    return render_template("donors.html", donors=all_donors)


# ── SOS Requests list ─────────────────────────────────────────
@app.route("/requests")
def requests_list():
    all_requests = SOSRepository.get_all()
    return render_template("requests.html", requests=all_requests)


# ── Request detail ────────────────────────────────────────────
@app.route("/requests/<request_id>")
def request_detail(request_id):
    req       = SOSRepository.get_by_id(request_id)
    responses = ResponseRepository.get_for_request(request_id)
    audit     = AuditRepository.get_for_entity(request_id)
    donors    = DonorRepository.get_all()
    return render_template(
        "request_detail.html",
        req=req, responses=responses, audit=audit, donors=donors
    )


# ── Donor respond (accept/decline) ───────────────────────────
@app.route("/respond", methods=["POST"])
def respond():
    try:
        result = handle_response(
            request_id = request.form["request_id"],
            donor_id   = request.form["donor_id"],
            response   = request.form["response"],
            reason     = request.form.get("reason", ""),
        )
        if result["status"] == "fulfilled":
            flash(f"Donation confirmed! Thank you for saving a life.", "success")
        else:
            flash("Response recorded. The request remains open.", "info")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("request_detail", request_id=request.form["request_id"]))


# ── Audit log ─────────────────────────────────────────────────
@app.route("/audit")
def audit_log():
    entries = AuditRepository.get_all()
    return render_template("audit.html", entries=entries)


# ── API: live stats (for dashboard refresh) ──────────────────
@app.route("/api/stats")
def api_stats():
    donors   = DonorRepository.get_all()
    requests = SOSRepository.get_all()
    return jsonify({
        "total_donors":     len(donors),
        "available_donors": sum(1 for d in donors if d["is_available"]),
        "open_requests":    sum(1 for r in requests if r["status"] in ("open","in_progress")),
        "total_fulfilled":  sum(1 for r in requests if r["status"] == "fulfilled"),
    })


if __name__ == "__main__":
    print("\n  CUBAL is running → http://localhost:5000\n")
    app.run(debug=True, port=5000)
