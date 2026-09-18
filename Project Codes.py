"""
Blood Donation Matching System
--------------------------------
Console-driven, in-memory Python application for matching blood donors to
blood requests based on blood-type compatibility, urgency, and a 90-day
donation cooldown period.

Run this file directly to launch the interactive console menu:
    python blood_donation_system.py
"""

import uuid
from datetime import datetime, timedelta

# Blood type compatibility table: donor_type -> list of recipient types they can give to
COMPATIBILITY = {
    "O-":  ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],  # universal donor
    "O+":  ["O+", "A+", "B+", "AB+"],
    "A-":  ["A-", "A+", "AB-", "AB+"],
    "A+":  ["A+", "AB+"],
    "B-":  ["B-", "B+", "AB-", "AB+"],
    "B+":  ["B+", "AB+"],
    "AB-": ["AB-", "AB+"],
    "AB+": ["AB+"],                    # universal recipient (as donor, can only give to AB+)
}

COOLDOWN_DAYS = 90  # minimum days required between donations


class BloodDonationSystem:
    """Handles donor registration, request intake, matching, fulfillment,
    and cancellation — all via in-memory dictionaries."""

    def __init__(self):
        self.donors = {}        # donor_id -> donor record
        self.requests = {}      # request_id -> request record
        self.transactions = {}  # txn_id -> transaction record (for reversal)

    # ---------- Admin: Donor Registration ----------
    def register_donor(self, name, blood_type, location, last_donation_date=None):
        blood_type = blood_type.strip().upper()
        if blood_type not in COMPATIBILITY:
            raise ValueError(f"Invalid blood type: {blood_type}")
        donor_id = "D" + str(len(self.donors) + 1).zfill(3)
        self.donors[donor_id] = {
            "name": name,
            "blood_type": blood_type,
            "location": location,
            "last_donation_date": last_donation_date,
        }
        return donor_id

    # ---------- Eligibility Engine ----------
    def is_eligible(self, donor_id):
        donor = self.donors[donor_id]
        if donor["last_donation_date"] is None:
            return True
        days_since = (datetime.now() - donor["last_donation_date"]).days
        return days_since >= COOLDOWN_DAYS

    def days_until_eligible(self, donor_id):
        donor = self.donors[donor_id]
        if donor["last_donation_date"] is None:
            return 0
        days_since = (datetime.now() - donor["last_donation_date"]).days
        return max(0, COOLDOWN_DAYS - days_since)

    # ---------- Admin: Request Intake ----------
    def add_request(self, blood_type_needed, urgency, hospital):
        blood_type_needed = blood_type_needed.strip().upper()
        if blood_type_needed not in COMPATIBILITY:
            raise ValueError(f"Invalid blood type: {blood_type_needed}")
        urgency = urgency.strip().lower()
        if urgency not in ("critical", "routine"):
            raise ValueError("Urgency must be 'critical' or 'routine'")
        request_id = "R" + str(len(self.requests) + 1).zfill(3)
        self.requests[request_id] = {
            "blood_type_needed": blood_type_needed,
            "urgency": urgency,
            "hospital": hospital,
            "status": "open",
        }
        return request_id

    # ---------- Matching Engine ----------
    def find_matches(self, request_id):
        if request_id not in self.requests:
            raise KeyError(f"No such request: {request_id}")
        req = self.requests[request_id]
        if req["status"] != "open":
            return []
        needed_type = req["blood_type_needed"]
        matches = [
            donor_id for donor_id, donor in self.donors.items()
            if needed_type in COMPATIBILITY[donor["blood_type"]] and self.is_eligible(donor_id)
        ]
        # Rank: donors who have never donated first, then by longest time since last donation
        matches.sort(key=lambda d: (
            self.donors[d]["last_donation_date"] is not None,
            self.donors[d]["last_donation_date"] or datetime.min,
        ))
        return matches

    # ---------- Fulfillment (Transaction Creation) ----------
    def fulfill_request(self, request_id, donor_id):
        if request_id not in self.requests:
            raise KeyError(f"No such request: {request_id}")
        if donor_id not in self.donors:
            raise KeyError(f"No such donor: {donor_id}")
        req = self.requests[request_id]
        if req["status"] != "open":
            raise ValueError("Request is not open")
        if not self.is_eligible(donor_id):
            raise ValueError(f"Donor {donor_id} is not eligible yet "
                              f"({self.days_until_eligible(donor_id)} days remaining)")
        if req["blood_type_needed"] not in COMPATIBILITY[self.donors[donor_id]["blood_type"]]:
            raise ValueError("Blood type incompatible for this request")

        txn_id = uuid.uuid4().hex[:8].upper()
        self.transactions[txn_id] = {
            "request_id": request_id,
            "donor_id": donor_id,
            "previous_last_donation": self.donors[donor_id]["last_donation_date"],
        }
        req["status"] = "fulfilled"
        self.donors[donor_id]["last_donation_date"] = datetime.now()
        return txn_id

    # ---------- Cancellation (Reversible Restoration) ----------
    def cancel_transaction(self, txn_id):
        if txn_id not in self.transactions:
            raise KeyError(f"No such transaction: {txn_id}")
        txn = self.transactions[txn_id]
        self.requests[txn["request_id"]]["status"] = "open"
        self.donors[txn["donor_id"]]["last_donation_date"] = txn["previous_last_donation"]
        del self.transactions[txn_id]
        return txn["request_id"], txn["donor_id"]


def load_seed_data(system):
    """Pre-loads sample donors and requests so the system can be demoed immediately."""
    system.register_donor("Ravi Sharma", "O-", "Bhopal")
    system.register_donor("Priya Nair", "A+", "Bhopal",
                           last_donation_date=datetime.now() - timedelta(days=10))
    system.register_donor("Aman Verma", "B+", "Indore",
                           last_donation_date=datetime.now() - timedelta(days=120))
    system.register_donor("Sneha Iyer", "AB+", "Bhopal")
    system.register_donor("Karan Singh", "O+", "Bhopal",
                           last_donation_date=datetime.now() - timedelta(days=45))

    system.add_request("A+", "critical", "AIIMS Bhopal")
    system.add_request("B+", "routine", "Hamidia Hospital")
    print("[Seed data loaded: 5 donors, 2 open requests]")


def print_donor_table(donor_ids, system):
    print(f"{'Donor ID':<10} | {'Name':<12} | {'Blood Type':<10} | Status")
    print("-" * 50)
    for donor_id in donor_ids:
        donor = system.donors[donor_id]
        status = "Eligible" if system.is_eligible(donor_id) else f"Wait {system.days_until_eligible(donor_id)}d"
        print(f"{donor_id:<10} | {donor['name']:<12} | {donor['blood_type']:<10} | {status}")


def run_smoke_test():
    """Quick sanity check of the core logic — run with: python blood_donation_system.py --test"""
    system = BloodDonationSystem()

    d1 = system.register_donor("Ravi", "O-", "Bhopal")
    system.register_donor("Priya", "A+", "Bhopal", last_donation_date=datetime.now() - timedelta(days=10))

    r1 = system.add_request("A+", "critical", "AIIMS Bhopal")

    print("Matches for", r1, ":", system.find_matches(r1))

    txn = system.fulfill_request(r1, d1)
    print("Fulfilled with transaction:", txn, "-> request status:", system.requests[r1]["status"])
    print("Donor", d1, "eligible now?", system.is_eligible(d1), "| days remaining:", system.days_until_eligible(d1))

    system.cancel_transaction(txn)
    print("After cancellation, request status:", system.requests[r1]["status"])
    print("Donor", d1, "eligible again?", system.is_eligible(d1))


def main():
    system = BloodDonationSystem()
    load_seed_data(system)
    print("=" * 50)
    print(" WELCOME TO THE BLOOD DONATION MATCHING SYSTEM")
    print("=" * 50)

    while True:
        print("\n--- GLOBAL OPTIONS ---")
        print("1. Admin Module: Register New Donor")
        print("2. Admin Module: Log New Blood Request")
        print("3. Matching Module: Find Compatible Donors for a Request")
        print("4. Fulfillment Module: Confirm a Donation Match")
        print("5. Cancellation Module: Reverse a Donation Transaction")
        print("6. Exit System Application")
        choice = input("Select an option (1-6): ").strip()

        try:
            if choice == "1":
                name = input("Donor name: ").strip()
                blood_type = input("Blood type (e.g. O-, A+, AB+): ").strip()
                location = input("Location: ").strip()
                donor_id = system.register_donor(name, blood_type, location)
                print(f"Donor registered successfully with ID: {donor_id}")

            elif choice == "2":
                blood_type = input("Blood type needed: ").strip()
                urgency = input("Urgency (critical/routine): ").strip()
                hospital = input("Hospital / location: ").strip()
                request_id = system.add_request(blood_type, urgency, hospital)
                print(f"Request logged successfully with ID: {request_id}")

            elif choice == "3":
                request_id = input("Request ID: ").strip()
                matches = system.find_matches(request_id)
                if not matches:
                    print("No eligible compatible donors found.")
                else:
                    print(f"\n[MATCHES FOR REQUEST {request_id}]")
                    print_donor_table(matches, system)

            elif choice == "4":
                request_id = input("Request ID: ").strip()
                donor_id = input("Donor ID to fulfill with: ").strip()
                txn_id = system.fulfill_request(request_id, donor_id)
                print(f"Match confirmed. Transaction ID: {txn_id}")

            elif choice == "5":
                txn_id = input("Transaction ID to cancel: ").strip()
                request_id, donor_id = system.cancel_transaction(txn_id)
                print(f"Transaction reversed. Request {request_id} reopened, donor {donor_id} restored.")

            elif choice == "6":
                print("Exiting system. Goodbye!")
                break

            else:
                print("Invalid option. Please choose between 1 and 6.")

        except (ValueError, KeyError) as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        run_smoke_test()
    else:
        main()
