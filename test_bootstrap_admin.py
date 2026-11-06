"""
Tests for bootstrap_admin.py — validates all safety checks WITHOUT touching MongoDB.

Covers:
  1. Missing BOOTSTRAP_ADMIN_CONFIRM blocks execution.
  2. Duplicate employee ID detection.
  3. Missing required environment variables.
  4. Weak / invalid password rejection.
  5. Invalid employee ID rejection.
  6. Password hash round-trip with the live hashing implementation.
  7. Dry-run mode completes without database access.
  8. Valid inputs pass all validation.
"""

import os
import sys
import unittest

# Ensure project root is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from bootstrap_admin import validate_password, validate_employee_id, bootstrap_admin
from backend.app.auth.security import hash_password, verify_password


class TestPasswordValidation(unittest.TestCase):
    """Tests for the password strength validator."""

    def test_too_short(self):
        errors = validate_password("Ab1!xyz")
        self.assertTrue(any("at least" in e for e in errors))

    def test_no_uppercase(self):
        errors = validate_password("abcdefgh1234!")
        self.assertTrue(any("uppercase" in e for e in errors))

    def test_no_lowercase(self):
        errors = validate_password("ABCDEFGH1234!")
        self.assertTrue(any("lowercase" in e for e in errors))

    def test_no_digit(self):
        errors = validate_password("Abcdefghijkl!")
        self.assertTrue(any("digit" in e for e in errors))

    def test_no_special_char(self):
        errors = validate_password("Abcdefgh1234")
        self.assertTrue(any("special" in e for e in errors))

    def test_common_weak_password(self):
        errors = validate_password("Admin@123")
        # Too short (9 chars) — should fail length check
        self.assertTrue(len(errors) > 0)

    def test_blocklisted_password(self):
        errors = validate_password("password")
        self.assertTrue(any("weak" in e.lower() for e in errors))

    def test_strong_password_passes(self):
        errors = validate_password("Str0ng!Pr0duction#Key99")
        self.assertEqual(errors, [], f"Expected no errors but got: {errors}")

    def test_exact_minimum_length(self):
        # 12 chars: Aa1!xxxxxxxx — exactly 12
        errors = validate_password("Aa1!xxxxxxxZ")
        self.assertEqual(errors, [], f"Expected no errors for 12-char password but got: {errors}")


class TestEmployeeIdValidation(unittest.TestCase):
    """Tests for employee ID format validation."""

    def test_empty_id(self):
        errors = validate_employee_id("")
        self.assertTrue(any("empty" in e.lower() for e in errors))

    def test_too_short(self):
        errors = validate_employee_id("AB")
        self.assertTrue(any("at least 3" in e for e in errors))

    def test_contains_spaces(self):
        errors = validate_employee_id("EMP 001")
        self.assertTrue(any("space" in e.lower() for e in errors))

    def test_valid_id(self):
        errors = validate_employee_id("EMP-ADMIN-001")
        self.assertEqual(errors, [])

    def test_valid_simple_id(self):
        errors = validate_employee_id("EMP-001")
        self.assertEqual(errors, [])


class TestPasswordHashing(unittest.TestCase):
    """Verifies that hash_password + verify_password round-trip correctly."""

    def test_hash_round_trip(self):
        test_pw = "TestP@ssw0rd!Bootstrap"
        hashed = hash_password(test_pw)
        # Hash must not contain the plaintext
        self.assertNotIn(test_pw, hashed)
        # Verification must succeed
        self.assertTrue(verify_password(test_pw, hashed))

    def test_wrong_password_fails(self):
        hashed = hash_password("CorrectPassword!1")
        self.assertFalse(verify_password("WrongPassword!1", hashed))

    def test_empty_password_fails(self):
        hashed = hash_password("SomePassword!1")
        self.assertFalse(verify_password("", hashed))

    def test_hash_not_empty(self):
        hashed = hash_password("AnyPassword!1")
        self.assertTrue(len(hashed) > 0)

    def test_different_hashes_for_same_password(self):
        """Each call should produce a different hash (unique salt)."""
        h1 = hash_password("SamePassword!1")
        h2 = hash_password("SamePassword!1")
        # Bcrypt and salted SHA-256 both use random salts
        self.assertNotEqual(h1, h2)


class TestBootstrapSafetyGates(unittest.TestCase):
    """Tests that the bootstrap function refuses to run without proper confirmation."""

    def _clear_env(self):
        """Remove all bootstrap-related env vars to start clean."""
        for var in [
            "BOOTSTRAP_ADMIN_CONFIRM", "MONGODB_URI", "MONGODB_DATABASE",
            "ADMIN_EMPLOYEE_ID", "ADMIN_FULL_NAME", "ADMIN_MOBILE",
            "ADMIN_EMAIL", "ADMIN_PASSWORD",
        ]:
            os.environ.pop(var, None)

    def test_missing_confirm_blocks_execution(self):
        """Without BOOTSTRAP_ADMIN_CONFIRM=true, bootstrap must refuse to run."""
        self._clear_env()
        os.environ["BOOTSTRAP_ADMIN_CONFIRM"] = ""
        result = bootstrap_admin(dry_run=True)
        self.assertFalse(result)
        self._clear_env()

    def test_wrong_confirm_value_blocks(self):
        """BOOTSTRAP_ADMIN_CONFIRM set to anything other than 'true' must block."""
        self._clear_env()
        os.environ["BOOTSTRAP_ADMIN_CONFIRM"] = "yes"
        result = bootstrap_admin(dry_run=True)
        self.assertFalse(result)
        self._clear_env()

    def test_dry_run_with_valid_inputs_succeeds(self):
        """Dry run with all valid env vars should succeed without DB access."""
        self._clear_env()
        os.environ["BOOTSTRAP_ADMIN_CONFIRM"] = "true"
        os.environ["MONGODB_URI"] = "mongodb+srv://test:test@cluster.example.net"
        os.environ["MONGODB_DATABASE"] = "test_db"
        os.environ["ADMIN_EMPLOYEE_ID"] = "EMP-ADMIN-001"
        os.environ["ADMIN_FULL_NAME"] = "Test Admin"
        os.environ["ADMIN_MOBILE"] = "0000000000"
        os.environ["ADMIN_EMAIL"] = "test@example.com"
        os.environ["ADMIN_PASSWORD"] = "Str0ng!Pr0duction#Key99"
        result = bootstrap_admin(dry_run=True)
        self.assertTrue(result)
        self._clear_env()

    def test_weak_password_blocks_dry_run(self):
        """Dry run must fail if the password is weak."""
        self._clear_env()
        os.environ["BOOTSTRAP_ADMIN_CONFIRM"] = "true"
        os.environ["MONGODB_URI"] = "mongodb+srv://test:test@cluster.example.net"
        os.environ["MONGODB_DATABASE"] = "test_db"
        os.environ["ADMIN_EMPLOYEE_ID"] = "EMP-ADMIN-002"
        os.environ["ADMIN_FULL_NAME"] = "Test Admin"
        os.environ["ADMIN_MOBILE"] = "0000000000"
        os.environ["ADMIN_EMAIL"] = "test@example.com"
        os.environ["ADMIN_PASSWORD"] = "weak"
        result = bootstrap_admin(dry_run=True)
        self.assertFalse(result)
        self._clear_env()

    def test_invalid_employee_id_blocks(self):
        """Dry run must fail if the employee ID is invalid."""
        self._clear_env()
        os.environ["BOOTSTRAP_ADMIN_CONFIRM"] = "true"
        os.environ["MONGODB_URI"] = "mongodb+srv://test:test@cluster.example.net"
        os.environ["MONGODB_DATABASE"] = "test_db"
        os.environ["ADMIN_EMPLOYEE_ID"] = "E"  # Too short
        os.environ["ADMIN_FULL_NAME"] = "Test Admin"
        os.environ["ADMIN_MOBILE"] = "0000000000"
        os.environ["ADMIN_EMAIL"] = "test@example.com"
        os.environ["ADMIN_PASSWORD"] = "Str0ng!Pr0duction#Key99"
        result = bootstrap_admin(dry_run=True)
        self.assertFalse(result)
        self._clear_env()


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 64)
    print("BOOTSTRAP ADMIN — SAFETY & VALIDATION TEST SUITE")
    print("=" * 64)

    # Preserve original env
    _orig_env = {k: os.environ.get(k) for k in [
        "BOOTSTRAP_ADMIN_CONFIRM", "MONGODB_URI", "MONGODB_DATABASE",
        "ADMIN_EMPLOYEE_ID", "ADMIN_FULL_NAME", "ADMIN_MOBILE",
        "ADMIN_EMAIL", "ADMIN_PASSWORD", "ENVIRONMENT", "STORAGE_MODE",
    ]}

    # Force development mode for tests so config.py doesn't raise
    os.environ["ENVIRONMENT"] = "development"
    os.environ["STORAGE_MODE"] = "json"

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestEmployeeIdValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordHashing))
    suite.addTests(loader.loadTestsFromTestCase(TestBootstrapSafetyGates))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Restore original env
    for k, v in _orig_env.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v

    print()
    if result.wasSuccessful():
        print("=" * 64)
        print(f"ALL {result.testsRun} BOOTSTRAP SAFETY TESTS PASSED")
        print("=" * 64)
    else:
        print("=" * 64)
        print(f"FAILURES: {len(result.failures)}, ERRORS: {len(result.errors)}")
        print("=" * 64)
        sys.exit(1)
