# Blood Donation Matching System

## Overview

The Blood Donation Matching System is a console-based matching application designed to connect blood requests with eligible, compatible donors in real time. Developed using clean Object-Oriented Programming (OOP) paradigms in Python, the system uses dynamic in-memory dictionary structures to guarantee fast lookups without an external database. It applies real blood-type compatibility rules and a rolling eligibility cooldown, and includes defensive error-handling to gracefully reject invalid blood types, duplicate actions, and unsafe transactions.

## Features

- **Donor Registration Module** — Registers donors with a unique ID, blood type, location, and (optional) last donation date.
- **Request Intake Module** — Logs incoming blood requests with required blood type, urgency level, and hospital/location.
- **Compatibility Matching Engine** — Filters registered donors against a request using the full 8-type donor-to-recipient compatibility table, returning only donors who are both compatible and currently eligible.
- **Eligibility Engine** — Calculates real-time donor eligibility using a 90-day cooldown since the last donation, and reports days remaining for donors who are not yet eligible.
- **Unique Transaction Reference Generator** — Creates an 8-character uppercase transaction ID (via `uuid`) for every completed donation match.
- **Cancellation Module** — Reverses a completed transaction, reopening the request and restoring the donor's previous eligibility state, using the transaction ID.
- **Defensive Exception Trapping** — Unified try-except handling for invalid blood types, unknown IDs, incompatible matches, and requests/donors already in a terminal state.

## Technologies / Tools Used

- **Programming Language:** Python 3.x
- **Core Standard Modules:** `uuid` (transaction reference generation), `datetime` (eligibility cooldown tracking)
- **Development Environment:** VS Code / any standard IDE
- **Version Control:** Git & GitHub

## Steps to Install & Run the Project

### Prerequisites

Make sure you have Python 3.x installed on your system. Verify with:

```bash
python --version
```

### Installation

1. Clone this repository to your local machine:

```bash
git clone https://github.com/<avanimvaishnav>/Blood-Donation-Matching-System.git
```

2. Navigate into the project folder:

```bash
cd Blood-Donation-Matching-System
```

### Running the Application

```bash
python3 blood_donation_system.py
```

## Instructions for Testing

Run the application and use the following test inputs inside the interactive console menu to verify system integrity:

1. **Test Case 1 (Donor Registration):** Go to option `1`. Register a donor with blood type `O-` and no prior donation date. Confirm the donor is created and marked eligible immediately (O- has no donation history yet).
2. **Test Case 2 (Request Intake):** Select option `2`. Create a request for blood type `A+`, urgency `critical`, hospital `AIIMS Bhopal`. Confirm the request is logged with status `open`.
3. **Test Case 3 (Matching):** Select option `3`. Enter the request ID from Test Case 2. Verify the system returns only donors whose blood type is compatible with A+ (e.g., an O- or A+ donor) and who are currently eligible.
4. **Test Case 4 (Fulfillment & Ineligibility Check):** Select option `4`. Fulfill the request with a matched donor. Confirm an 8-character transaction ID is generated and that the donor becomes ineligible with 90 days remaining. Try fulfilling another request with the same donor immediately — verify the system blocks it.
5. **Test Case 5 (Cancellation & Restoration):** Select option `5`. Input the transaction ID from Test Case 4. Verify the request reopens and the donor's eligibility is restored to its exact prior state.

## Screenshots

**Main Interactive Menu**

```
==================================================
 WELCOME TO THE BLOOD DONATION MATCHING SYSTEM
==================================================
--- GLOBAL OPTIONS ---
1. Admin Module: Register New Donor
2. Admin Module: Log New Blood Request
3. Matching Module: Find Compatible Donors for a Request
4. Fulfillment Module: Confirm a Donation Match
5. Cancellation Module: Reverse a Donation Transaction
6. Exit System Application
Select an option (1-6): 3

[MATCHES FOR REQUEST R001 — Blood Type Needed: A+]
Donor ID   | Name         | Blood Type | Status
--------------------------------------------------
D001       | Ravi         | O-         | Eligible
D003       | Priya        | A+         | Eligible
```
