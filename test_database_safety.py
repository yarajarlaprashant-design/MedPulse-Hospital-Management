"""
Comprehensive Database Safety Test Suite for MedPulse Hospital System.

Validates all 9 production database safety requirements:
1. In STORAGE_MODE=mongo, if MongoDB connection fails, raise RuntimeError and prevent application startup.
2. In ENVIRONMENT=production, never allow JSON fallback, including when STORAGE_MODE=auto.
3. In STORAGE_MODE=json, permit JSON storage only in development.
4. In STORAGE_MODE=auto, permit JSON fallback only in development.
5. Update get_collection() so production cannot return JSONCollection.
6. Update get_health() to return minimal health information without database names, endpoints, connection pool details, or internal errors.
7. Preserve existing MongoDB and JSON collection behaviour where permitted.
8. Verify ENVIRONMENT is correctly loaded from backend/app/config.py.
9. Verify all storage modes and production MongoDB connection failure handling.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.config import settings, Settings
from backend.app.database import DatabaseManager, JSONCollection
from backend.app.auth.security import create_access_token, decode_token


def test_1_storage_mode_mongo_connection_failure_raises_runtime_error():
    """Requirement 1: In STORAGE_MODE=mongo, if MongoDB connection fails, raise RuntimeError."""
    with patch.dict(os.environ, {"STORAGE_MODE": "mongo", "ENVIRONMENT": "development"}):
        with patch("backend.app.database.mongo_client_manager.connect", return_value=False):
            raised = False
            try:
                DatabaseManager()
            except RuntimeError as e:
                raised = True
                assert "STORAGE_MODE='mongo'" in str(e)
                assert "Application startup aborted" in str(e)
            assert raised, "Expected RuntimeError when STORAGE_MODE='mongo' and MongoDB connection fails."
    print("[PASS] Test 1: STORAGE_MODE=mongo failure raises RuntimeError and prevents startup.")


def test_2_production_auto_mode_no_json_fallback_raises_runtime_error():
    """Requirement 2: In ENVIRONMENT=production, never allow JSON fallback when STORAGE_MODE=auto."""
    with patch.dict(os.environ, {"STORAGE_MODE": "auto", "ENVIRONMENT": "production"}):
        with patch("backend.app.database.mongo_client_manager.connect", return_value=False):
            raised = False
            try:
                DatabaseManager()
            except RuntimeError as e:
                raised = True
                assert "JSON fallback is strictly disabled in production" in str(e)
            assert raised, "Expected RuntimeError in production when STORAGE_MODE='auto' and MongoDB connection fails."
    print("[PASS] Test 2: Production with STORAGE_MODE=auto disallows JSON fallback and raises RuntimeError.")


def test_3_production_json_mode_forbidden_raises_runtime_error():
    """Requirement 3: In STORAGE_MODE=json, permit JSON storage only in development. Production must raise RuntimeError."""
    with patch.dict(os.environ, {"STORAGE_MODE": "json", "ENVIRONMENT": "production"}):
        raised = False
        try:
            DatabaseManager()
        except RuntimeError as e:
            raised = True
            assert "STORAGE_MODE='json' is strictly forbidden in production" in str(e)
        assert raised, "Expected RuntimeError in production when STORAGE_MODE='json'."
    print("[PASS] Test 3: Production with STORAGE_MODE=json is forbidden and raises RuntimeError.")


def test_4_development_json_mode_permitted():
    """Requirement 3: In STORAGE_MODE=json, permit JSON storage in development."""
    with patch.dict(os.environ, {"STORAGE_MODE": "json", "ENVIRONMENT": "development"}):
        db = DatabaseManager()
        assert db.use_mongo is False
        assert db.mongo_client is None
        assert db.mongo_db is None
        coll = db.get_collection("patients")
        assert isinstance(coll, JSONCollection)
    print("[PASS] Test 4: Development with STORAGE_MODE=json permits JSON storage.")


def test_5_development_auto_mode_fallback_permitted():
    """Requirement 4: In STORAGE_MODE=auto, permit JSON fallback only in development."""
    with patch.dict(os.environ, {"STORAGE_MODE": "auto", "ENVIRONMENT": "development"}):
        with patch("backend.app.database.mongo_client_manager.connect", return_value=False):
            db = DatabaseManager()
            assert db.use_mongo is False
            assert db.mongo_client is None
            assert db.mongo_db is None
            coll = db.get_collection("patients")
            assert isinstance(coll, JSONCollection)
    print("[PASS] Test 5: Development with STORAGE_MODE=auto permits JSON fallback when MongoDB fails.")


def test_6_get_collection_production_guard():
    """Requirement 5: Update get_collection() so production cannot return JSONCollection."""
    with patch.dict(os.environ, {"STORAGE_MODE": "auto", "ENVIRONMENT": "development"}):
        with patch("backend.app.database.mongo_client_manager.connect", return_value=False):
            db = DatabaseManager()
            # Simulate setting environment to production after initialization
            with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
                raised = False
                try:
                    db.get_collection("patients")
                except RuntimeError as e:
                    raised = True
                    assert "Cannot return JSONCollection for 'patients' in production environment" in str(e)
                assert raised, "Expected RuntimeError when get_collection() is called in production without MongoDB."
    print("[PASS] Test 6: get_collection() in production strictly blocks JSONCollection.")


def test_7_get_health_minimal_information_no_leaks():
    """Requirement 6: get_health() returns minimal health info without database names, endpoints, pool details, or internal errors."""
    with patch.dict(os.environ, {"STORAGE_MODE": "auto", "ENVIRONMENT": "development"}):
        with patch("backend.app.database.mongo_client_manager.connect", return_value=False):
            db = DatabaseManager()
            health = db.get_health()

            # Verify safe fields present
            assert "status" in health
            assert "database" in health
            assert "connected" in health
            assert "engine" in health

            # Verify forbidden sensitive keys are NOT present
            forbidden_keys = [
                "database_name",
                "endpoint",
                "connection_pool",
                "last_error",
                "error",
                "fallback_storage",
                "data_directory",
                "uri"
            ]
            for key in forbidden_keys:
                assert key not in health, f"Security leak detected: '{key}' found in get_health() response: {health}"

    print("[PASS] Test 7: get_health() returns minimal information without sensitive system leaks.")


def test_8_environment_loading_from_config():
    """Requirement 8: Verify ENVIRONMENT is correctly loaded from backend/app/config.py."""
    # Check default environment configuration
    assert hasattr(settings, "ENVIRONMENT")
    assert isinstance(settings.ENVIRONMENT, str)

    # Check is_production property behavior
    with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
        assert settings.is_production is True

    with patch.dict(os.environ, {"ENVIRONMENT": "prod"}):
        assert settings.is_production is True

    with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
        assert settings.is_production is False

    with patch.dict(os.environ, {"ENVIRONMENT": "testing"}):
        assert settings.is_production is False

    print("[PASS] Test 8: ENVIRONMENT loading and is_production property verified.")


def test_9_preserve_json_collection_behavior():
    """Requirement 7: Preserve existing JSON collection behaviour where permitted."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test_collection.json")
        coll = JSONCollection("test_collection", test_file)

        # Test insert_one
        doc_id = coll.insert_one({"name": "Test Patient", "status": "Admitted", "age": 45})
        assert doc_id is not None

        # Test find_one
        doc = coll.find_one({"_id": doc_id})
        assert doc is not None
        assert doc["name"] == "Test Patient"
        assert doc["age"] == 45

        # Test count_documents
        assert coll.count_documents({}) == 1

        # Test update_one
        updated = coll.update_one({"_id": doc_id}, {"$set": {"status": "Discharged"}})
        assert updated is True
        doc_updated = coll.find_one({"_id": doc_id})
        assert doc_updated["status"] == "Discharged"

        # Test delete_one
        deleted = coll.delete_one({"_id": doc_id})
        assert deleted is True
        assert coll.count_documents({}) == 0

    print("[PASS] Test 9: Existing JSONCollection read/write/update operations preserved.")


def test_10_production_with_successful_mongodb_connection():
    """Requirement 7: Preserve MongoDB collection behavior when connected."""
    mock_mongo_client = MagicMock()
    mock_mongo_db = MagicMock()
    mock_collection = MagicMock()
    mock_mongo_db.__getitem__.return_value = mock_collection

    with patch.dict(os.environ, {"STORAGE_MODE": "mongo", "ENVIRONMENT": "production"}):
        with patch("backend.app.database.mongo_client_manager.connect", return_value=True), \
             patch("backend.app.database.mongo_client_manager.client", mock_mongo_client), \
             patch("backend.app.database.mongo_client_manager.db", mock_mongo_db):
            db = DatabaseManager()
            assert db.use_mongo is True
            coll = db.get_collection("patients")
            assert coll == mock_collection
            health = db.get_health()
            assert health["status"] == "healthy"
            assert health["database"] == "active"
            assert health["connected"] is True
            assert health["engine"] == "mongodb"

    print("[PASS] Test 10: Production with valid MongoDB connection operates successfully.")


def test_11_production_secret_key_missing_raises_runtime_error():
    """Verify that in production, missing SECRET_KEY raises RuntimeError during startup."""
    with patch.dict(os.environ, {"ENVIRONMENT": "production", "SECRET_KEY": ""}):
        raised = False
        try:
            Settings()
        except RuntimeError as e:
            raised = True
            assert "SECRET_KEY environment variable is missing or empty in production" in str(e)
        assert raised, "Expected RuntimeError when SECRET_KEY is missing in production."
    print("[PASS] Test 11: Missing SECRET_KEY in production raises RuntimeError.")


def test_12_production_secret_key_placeholder_raises_runtime_error():
    """Verify that in production, placeholder SECRET_KEY raises RuntimeError during startup."""
    placeholders = [
        "replace-with-your-strong-production-random-secret-key",
        "super-secret-hospital-jwt-key-btech-2026-mbu",
        "your-secret-key",
        "changeme"
    ]
    for ph in placeholders:
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "SECRET_KEY": ph}):
            raised = False
            err_msg = ""
            try:
                Settings()
            except RuntimeError as e:
                raised = True
                err_msg = str(e)
                assert "Insecure or placeholder SECRET_KEY detected in production" in err_msg
                # Ensure secret is not printed or logged in the error message
                assert ph not in err_msg, f"Security leak: Placeholder value was echoed in error: {err_msg}"
            assert raised, f"Expected RuntimeError for placeholder '{ph}' in production."
    print("[PASS] Test 12: Insecure placeholder SECRET_KEY in production raises RuntimeError without echoing secret.")


def test_13_production_secret_key_valid_accepted():
    """Verify that in production, a strong random secret key is accepted."""
    import secrets
    strong_key = secrets.token_hex(32)
    with patch.dict(os.environ, {"ENVIRONMENT": "production", "SECRET_KEY": strong_key}):
        s = Settings()
        assert s.SECRET_KEY == strong_key
        assert s.is_production is True
    print("[PASS] Test 13: Strong random SECRET_KEY in production is accepted.")


def test_14_development_secret_key_works_without_secrets():
    """Verify that local development works without requiring users to expose secrets."""
    with patch.dict(os.environ, {"ENVIRONMENT": "development", "SECRET_KEY": ""}):
        s = Settings()
        assert s.is_production is False
        assert len(s.SECRET_KEY) >= 32
        
        # Test JWT token creation and verification
        token = create_access_token({"sub": "EMP-001", "role": "Doctor"})
        payload = decode_token(token)
        assert payload is not None
        assert payload.get("sub") == "EMP-001"
        assert payload.get("role") == "Doctor"
    print("[PASS] Test 14: Development operates smoothly with ephemeral secret; JWT works.")


def test_15_production_cors_origins_restricted_to_deployed_domains():
    """Verify that in production, CORS only allows configured frontend domain and excludes localhost."""
    prod_env = {
        "ENVIRONMENT": "production",
        "FRONTEND_URL": "https://medpulse-hospital.vercel.app",
        "CORS_ORIGINS": "https://medpulse-hospital.vercel.app,https://admin.medpulse.org",
        "SECRET_KEY": "a" * 64
    }
    with patch.dict(os.environ, prod_env):
        s = Settings()
        origins = s.cors_origins
        assert "http://localhost:3000" not in origins
        assert "http://127.0.0.1:3000" not in origins
        assert "https://medpulse-hospital.vercel.app" in origins
        assert "https://admin.medpulse.org" in origins

    # In development, localhost is included
    dev_env = {
        "ENVIRONMENT": "development",
        "SECRET_KEY": "a" * 64
    }
    with patch.dict(os.environ, dev_env):
        s = Settings()
        assert "http://localhost:3000" in s.cors_origins
    print("[PASS] Test 15: CORS in production is strictly limited to deployed frontend domains.")


def test_16_production_seeder_disabled():
    """Verify that in production, automatic seeding is disabled to protect existing patient records."""
    from backend.seed_data import seed_database
    prod_env = {
        "ENVIRONMENT": "production",
        "SECRET_KEY": "a" * 64
    }
    with patch.dict(os.environ, prod_env):
        with patch("backend.seed_data.get_db") as mock_get_db:
            seed_database()
            # In production, seed_database should return early without accessing collections
            mock_get_db.assert_not_called()
    print("[PASS] Test 16: Automatic seeding is disabled in production to protect patient data.")


def run_all():
    print("==================================================")
    print("STARTING PRODUCTION DATABASE & JWT SAFETY TEST SUITE")
    print("==================================================")
    test_1_storage_mode_mongo_connection_failure_raises_runtime_error()
    test_2_production_auto_mode_no_json_fallback_raises_runtime_error()
    test_3_production_json_mode_forbidden_raises_runtime_error()
    test_4_development_json_mode_permitted()
    test_5_development_auto_mode_fallback_permitted()
    test_6_get_collection_production_guard()
    test_7_get_health_minimal_information_no_leaks()
    test_8_environment_loading_from_config()
    test_9_preserve_json_collection_behavior()
    test_10_production_with_successful_mongodb_connection()
    test_11_production_secret_key_missing_raises_runtime_error()
    test_12_production_secret_key_placeholder_raises_runtime_error()
    test_13_production_secret_key_valid_accepted()
    test_14_development_secret_key_works_without_secrets()
    test_15_production_cors_origins_restricted_to_deployed_domains()
    test_16_production_seeder_disabled()
    print("==================================================")
    print("ALL 16 PRODUCTION SECURITY & SAFETY TESTS PASSED WITH 100% SUCCESS!")
    print("==================================================")


if __name__ == "__main__":
    run_all()
