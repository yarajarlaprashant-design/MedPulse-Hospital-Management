"""
MedPulse Hospital Management System — One-Time Production Admin Bootstrap Script.

PURPOSE:
    Creates exactly one initial Admin user in the production MongoDB Atlas
    `hospital_management_db` so that the admin-approval workflow can begin.

SECURITY:
    - Reads ALL credentials from environment variables or secure interactive input.
    - Never hardcodes passwords, URIs, or personal information.
    - Never prints passwords, hashes, URIs, or PII.
    - Refuses to run without explicit BOOTSTRAP_ADMIN_CONFIRM=true.
    - Refuses to overwrite an existing employee_id.
    - Uses the EXACT same hashing function as the live authentication system.

USAGE:
    See the instructions at the bottom of this file or run:
        python bootstrap_admin.py --help

AFTER RUNNING:
    Delete this script and remove the environment variables.
    Do NOT commit this script with credentials to Git.
"""

import os
import sys
import getpass
import argparse
from datetime import datetime

# ---------------------------------------------------------------------------
# 1. Resolve project root so existing app modules can be imported
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = SCRIPT_DIR  # bootstrap_admin.py lives at the project root
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------------------------
# 2. Import the EXACT hashing function used by the live login endpoint
# ---------------------------------------------------------------------------
from backend.app.auth.security import hash_password, verify_password


# ---------------------------------------------------------------------------
# 3. Constants
# ---------------------------------------------------------------------------
MIN_PASSWORD_LENGTH = 12
DATABASE_NAME_DEFAULT = "hospital_management_db"
USERS_COLLECTION = "users"
EMPLOYEES_COLLECTION = "employees"


# ---------------------------------------------------------------------------
# 4. Input collection — environment variables with interactive fallback
# ---------------------------------------------------------------------------
def get_input(env_var: str, prompt: str, *, secret: bool = False, required: bool = True) -> str:
    """
    Reads a value from the named environment variable.
    Falls back to interactive input if the variable is not set.
    Uses getpass for secret fields to avoid terminal echo.
    """
    value = os.getenv(env_var, "").strip()
    if value:
        if secret:
            print(f"  {env_var}: (loaded from environment)")
        else:
            print(f"  {env_var}: {value}")
        return value

    # Interactive fallback
    if secret:
        value = getpass.getpass(f"  {prompt}: ").strip()
    else:
        value = input(f"  {prompt}: ").strip()

    if required and not value:
        print(f"\n[ABORT] {env_var} is required but was not provided.")
        sys.exit(1)

    return value


# ---------------------------------------------------------------------------
# 5. Validation helpers
# ---------------------------------------------------------------------------
def validate_password(password: str) -> list:
    """
    Returns a list of validation error strings.  Empty list means the password is acceptable.
    """
    errors = []
    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters (got {len(password)}).")
    if password.lower() in {
        "password", "admin", "admin123", "admin@123", "staff@123",
        "changeme", "secret", "12345678", "123456789012",
    }:
        errors.append("Password is a commonly-known weak value. Choose a stronger one.")
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter.")
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter.")
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit.")
    if password.isalnum():
        errors.append("Password must contain at least one special character.")
    return errors


def validate_employee_id(emp_id: str) -> list:
    """Returns a list of validation error strings for the employee ID."""
    errors = []
    if not emp_id:
        errors.append("Employee ID cannot be empty.")
    if len(emp_id) < 3:
        errors.append("Employee ID must be at least 3 characters.")
    if " " in emp_id:
        errors.append("Employee ID must not contain spaces.")
    return errors


# ---------------------------------------------------------------------------
# 6. Main bootstrap logic
# ---------------------------------------------------------------------------
def bootstrap_admin(*, dry_run: bool = False) -> bool:
    """
    Creates the initial Admin user in MongoDB.
    Returns True on success, False on failure.
    """
    print("=" * 64)
    print("MedPulse Hospital — Production Admin Bootstrap")
    print("=" * 64)

    # ---- Safety gate ----
    confirm = os.getenv("BOOTSTRAP_ADMIN_CONFIRM", "").strip().lower()
    if confirm != "true":
        print(
            "\n[ABORT] Safety confirmation missing.\n"
            "Set the environment variable BOOTSTRAP_ADMIN_CONFIRM=true to proceed.\n"
            "This guard prevents accidental execution."
        )
        return False

    # ---- Collect inputs ----
    print("\nCollecting configuration (from environment or interactive input):\n")

    mongodb_uri = get_input(
        "MONGODB_URI",
        "MongoDB Atlas connection URI (mongodb+srv://...)",
        secret=True, required=True,
    )
    db_name = get_input(
        "MONGODB_DATABASE",
        f"Database name [{DATABASE_NAME_DEFAULT}]",
        required=False,
    ) or DATABASE_NAME_DEFAULT

    employee_id = get_input("ADMIN_EMPLOYEE_ID", "Admin Employee ID (e.g. EMP-ADMIN-001)")
    full_name = get_input("ADMIN_FULL_NAME", "Admin Full Name")
    mobile_number = get_input("ADMIN_MOBILE", "Admin Mobile Number")
    email = get_input("ADMIN_EMAIL", "Admin Email Address", required=False) or ""
    password = get_input("ADMIN_PASSWORD", "Admin Password (min 12 chars, mixed case + digit + special)", secret=True)

    # ---- Validate employee ID ----
    eid_errors = validate_employee_id(employee_id)
    if eid_errors:
        print("\n[ABORT] Invalid Employee ID:")
        for e in eid_errors:
            print(f"  - {e}")
        return False

    # ---- Validate password ----
    pw_errors = validate_password(password)
    if pw_errors:
        print("\n[ABORT] Password does not meet security requirements:")
        for e in pw_errors:
            print(f"  - {e}")
        return False

    # ---- Dry-run mode ----
    if dry_run:
        print("\n[DRY RUN] Validation passed. No database changes will be made.")
        print(f"  Employee ID : {employee_id}")
        print(f"  Full Name   : {full_name}")
        print(f"  Role        : Admin")
        print(f"  Database    : {db_name}")
        print("  Password    : (validated, not shown)")
        print("  Hash method : hash_password() from backend.app.auth.security")
        return True

    # ---- Connect to MongoDB ----
    print("\nConnecting to MongoDB...")
    try:
        import pymongo
        try:
            import certifi
            ca_file = certifi.where()
        except ImportError:
            ca_file = None

        client_opts = {
            "serverSelectionTimeoutMS": 10000,
            "connectTimeoutMS": 10000,
            "socketTimeoutMS": 10000,
            "appName": "MedPulseBootstrapAdmin",
        }
        if ca_file and ("mongodb+srv://" in mongodb_uri or "mongodb.net" in mongodb_uri):
            client_opts["tlsCAFile"] = ca_file

        client = pymongo.MongoClient(mongodb_uri, **client_opts)
        client.admin.command("ping")
        print("  MongoDB connection verified.")
    except Exception as exc:
        # Sanitize error to avoid leaking URI
        safe_err = str(exc)
        if "@" in safe_err:
            safe_err = safe_err.split("@")[-1]  # keep only post-@ portion
        print(f"\n[ABORT] Failed to connect to MongoDB: ...@{safe_err}")
        return False

    db = client[db_name]
    users_coll = db[USERS_COLLECTION]
    emp_coll = db[EMPLOYEES_COLLECTION]

    # ---- Check for duplicate ----
    existing = users_coll.find_one({"employee_id": employee_id})
    if existing:
        print(f"\n[ABORT] Employee ID '{employee_id}' already exists in the users collection.")
        print("  This script will NOT overwrite existing accounts.")
        print("  Choose a different employee ID or manually verify the existing account.")
        client.close()
        return False

    existing_emp = emp_coll.find_one({"employee_id": employee_id})
    if existing_emp:
        print(f"\n[ABORT] Employee ID '{employee_id}' already exists in the employees collection.")
        print("  This script will NOT overwrite existing accounts.")
        client.close()
        return False

    # ---- Hash password using the exact live implementation ----
    print("  Hashing password with production algorithm...")
    password_hash = hash_password(password)

    # ---- Verify the hash works with the live verify_password function ----
    if not verify_password(password, password_hash):
        print("\n[ABORT] CRITICAL — hash verification round-trip failed. Aborting to prevent lockout.")
        client.close()
        return False
    print("  Hash round-trip verification passed.")

    # ---- Build documents matching the exact schema used by auth.py ----
    now_iso = datetime.now().isoformat()
    now_date = datetime.now().strftime("%Y-%m-%d")

    user_doc = {
        "employee_id": employee_id,
        "full_name": full_name,
        "mobile_number": mobile_number,
        "email": email,
        "role": "Admin",
        "department": "Administration",
        "password_hash": password_hash,
        "is_approved": True,
        "is_active": True,
        "registered_at": now_iso,
        "created_at": now_iso,
        "created_by": "bootstrap_admin.py (one-time setup)",
    }

    emp_doc = {
        "employee_id": employee_id,
        "full_name": full_name,
        "mobile_number": mobile_number,
        "email": email,
        "gender": "Not Specified",
        "age": 0,
        "qualification": "Not Specified",
        "department": "Administration",
        "designation": "System Administrator",
        "role": "Admin",
        "joining_date": now_date,
        "status": "Active",
    }

    # ---- Insert ----
    print("  Inserting admin user document...")
    users_coll.insert_one(user_doc)

    print("  Inserting admin employee document...")
    emp_coll.insert_one(emp_doc)

    # ---- Final verification ----
    verify_user = users_coll.find_one({"employee_id": employee_id})
    if verify_user and verify_user.get("is_approved") is True and verify_user.get("role") == "Admin":
        print("\n" + "=" * 64)
        print("SUCCESS — Admin account created and verified.")
        print("=" * 64)
        print(f"  Employee ID : {employee_id}")
        print(f"  Role        : Admin")
        print(f"  Approved    : True")
        print(f"  Active      : True")
        print(f"  Database    : {db_name}")
        print(f"  Collections : {USERS_COLLECTION}, {EMPLOYEES_COLLECTION}")
        print()
        print("NEXT STEPS:")
        print("  1. Log in to the MedPulse frontend with this Admin account.")
        print("  2. Approve any pending staff registration requests.")
        print("  3. DELETE this script from the server and your local machine.")
        print("  4. REMOVE the ADMIN_PASSWORD and MONGODB_URI environment variables.")
        print("  5. Do NOT commit this script with credentials to Git.")
    else:
        print("\n[WARNING] Insert completed but verification read-back failed.")
        print("  Check the MongoDB Atlas console manually.")

    client.close()
    return True


# ---------------------------------------------------------------------------
# 7. CLI entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="MedPulse Hospital — One-Time Production Admin Bootstrap",
        epilog=(
            "Environment variables:\n"
            "  BOOTSTRAP_ADMIN_CONFIRM  Must be 'true' to proceed (safety gate)\n"
            "  MONGODB_URI              MongoDB Atlas connection string\n"
            "  MONGODB_DATABASE         Database name (default: hospital_management_db)\n"
            "  ADMIN_EMPLOYEE_ID        Employee ID for the admin account\n"
            "  ADMIN_FULL_NAME          Full name of the admin\n"
            "  ADMIN_MOBILE             Mobile number of the admin\n"
            "  ADMIN_EMAIL              Email address (optional)\n"
            "  ADMIN_PASSWORD           Strong password (min 12 chars)\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate all inputs without connecting to MongoDB or creating any records.",
    )
    args = parser.parse_args()

    success = bootstrap_admin(dry_run=args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
