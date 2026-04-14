"""
CUBAL - Main Entry Point
Connects Unity for Blood and Life

Runs a full end-to-end prototype demo:
  1. Init DB
  2. Register donors and recipients
  3. Recipient raises SOS
  4. Donors get notified
  5. Donor accepts / declines
  6. Analytics report

Usage:
    python main.py          # full demo
    python main.py --report # analytics only (if DB already populated)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from models.database import init_db
from services.registration import register_donor, register_recipient
from services.sos_service import raise_sos, handle_response, get_request_summary
from services.analytics import full_report
from data.seed_data import DEMO_DONORS, DEMO_RECIPIENTS


BANNER = """
╔══════════════════════════════════════════════════════════╗
║          CUBAL — Connecting Unity for Blood & Life       ║
║          Blood & Plasma Donation Platform Prototype      ║
╚══════════════════════════════════════════════════════════╝
"""


def section(title: str):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


def run_demo():
    print(BANNER)

    # ── 1. Database setup ─────────────────────────────────────
    section("STEP 1 — Initialising database")
    init_db()

    # ── 2. Register donors ────────────────────────────────────
    section("STEP 2 — Registering donors")
    donors = []
    for d in DEMO_DONORS:
        donor = register_donor(
            name=d["name"], age=d["age"], blood_type=d["blood_type"],
            city=d["city"], latitude=d["latitude"], longitude=d["longitude"],
            phone=d["phone"],
        )
        donors.append(donor)

    # ── 3. Register recipients ────────────────────────────────
    section("STEP 3 — Registering recipients (patients)")
    recipients = []
    for r in DEMO_RECIPIENTS:
        recipient = register_recipient(
            name=r["name"], age=r["age"], blood_type=r["blood_type"],
            city=r["city"], latitude=r["latitude"], longitude=r["longitude"],
            phone=r["phone"],
        )
        recipients.append(recipient)

    # ── 4. SOS Scenario A — O+ needed in Bengaluru ────────────
    section("STEP 4A — SOS: Vikram Rao needs O+ blood (Bengaluru)")
    result_a = raise_sos(
        recipient_id=recipients[0].recipient_id,
        blood_type="O+",
        units_needed=DEMO_RECIPIENTS[0]["units"],
        urgency=DEMO_RECIPIENTS[0]["urgency"],
        message=DEMO_RECIPIENTS[0]["message"],
    )

    # Simulate: first matched donor declines, second accepts
    if result_a["matched"]:
        request_id_a = result_a["request"]["request_id"]
        matched      = result_a["matched"]

        if len(matched) >= 1:
            donor_1, dist_1 = matched[0]
            print(f"\n  Simulating: {donor_1['name']} declines (unavailable today)...")
            handle_response(
                request_id=request_id_a,
                donor_id=donor_1["donor_id"],
                response="decline",
                reason="Travelling out of city today",
            )

        if len(matched) >= 2:
            donor_2, dist_2 = matched[1]
            print(f"\n  Simulating: {donor_2['name']} accepts...")
            handle_response(
                request_id=request_id_a,
                donor_id=donor_2["donor_id"],
                response="accept",
            )

    # ── 5. SOS Scenario B — A- needed (rare type, may expand radius) ──
    section("STEP 4B — SOS: Lakshmi Devi needs A- blood (Bengaluru)")
    result_b = raise_sos(
        recipient_id=recipients[1].recipient_id,
        blood_type="A-",
        units_needed=DEMO_RECIPIENTS[1]["units"],
        urgency=DEMO_RECIPIENTS[1]["urgency"],
        message=DEMO_RECIPIENTS[1]["message"],
    )

    # ── 6. SOS Scenario C — B- for child (very rare) ──────────
    section("STEP 4C — SOS: Mohammed Farhan (12 yrs) needs B- blood")
    result_c = raise_sos(
        recipient_id=recipients[2].recipient_id,
        blood_type="B-",
        units_needed=DEMO_RECIPIENTS[2]["units"],
        urgency=DEMO_RECIPIENTS[2]["urgency"],
        message=DEMO_RECIPIENTS[2]["message"],
    )

    # ── 7. Show request summary with full audit trail ─────────
    section("STEP 5 — Request summary & audit trail")
    if result_a["matched"]:
        summary = get_request_summary(result_a["request"]["request_id"])
        print(f"\n  Request ID : {summary['request']['request_id']}")
        print(f"  Status     : {summary['request']['status'].upper()}")
        print(f"  Fulfilled  : {summary['request']['fulfilled_at'] or 'N/A'}")
        print(f"\n  Responses recorded: {len(summary['responses'])}")
        for r in summary["responses"]:
            print(f"    - Donor {r['donor_id']} → {r['response'].upper()}"
                  + (f" | {r['reason']}" if r['reason'] else ""))
        print(f"\n  Audit entries: {len(summary['audit'])}")
        for a in summary["audit"]:
            print(f"    [{a['logged_at'][11:19]}] {a['event_type']:25} {a['description']}")

    # ── 8. Analytics ──────────────────────────────────────────
    section("STEP 6 — Analytics report")
    full_report()

    print(f"\n{'='*60}")
    print("  CUBAL demo complete.")
    print(f"{'='*60}\n")


def run_report_only():
    """Just print analytics on an existing database."""
    print(BANNER)
    section("CUBAL Analytics Report")
    full_report()


if __name__ == "__main__":
    if "--report" in sys.argv:
        run_report_only()
    else:
        run_demo()
