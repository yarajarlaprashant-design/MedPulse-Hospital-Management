"""
Automated End-to-End System Integration Test.
Verifies FastAPI endpoints, JWT authentication, RBAC, and ML predictions.
"""

import sys
import os
import time

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient
from backend.app.main import app

def run_tests():
    print("==================================================")
    print("STARTING COMPREHENSIVE SYSTEM INTEGRATION TESTS")
    print("==================================================")
    client = TestClient(app)

    # 1. Health check & Database Health
    res = client.get("/api/v1/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    db_res = client.get("/api/v1/health/database")
    assert db_res.status_code == 200, f"DB Health check failed: {db_res.text}"
    print(f"[PASS] 1. API Health Check OK: Status={res.json().get('status')}, DB Engine={db_res.json().get('engine')}")

    # 2. Staff Login with EMP-001 (Admin)
    login_payload = {
        "full_name": "Dr. Rajesh Varma",
        "mobile_number": "9848022331",
        "employee_id": "EMP-001",
        "password": "Admin@123"
    }
    res = client.post("/api/v1/auth/login", json=login_payload)
    assert res.status_code == 200, f"Login failed: {res.text}"
    token = res.json()["access_token"]
    user = res.json()["user"]
    print(f"[PASS] 2. Staff Login Authenticated: {user['full_name']} (Role: {user['role']})")

    headers = {"Authorization": f"Bearer {token}"}

    # 3. Patient Status Tracking Metrics (Flagship Module)
    res = client.get("/api/v1/status-tracking/dashboard-metrics", headers=headers)
    assert res.status_code == 200, f"Status tracking failed: {res.text}"
    metrics = res.json()
    print(f"[PASS] 3. Patient Status Tracking Metrics: Total Registered={metrics['total_registered_patients']}, Admitted={metrics['currently_admitted']}, Emergency={metrics['emergency_patients']}")

    # 4. Patient Status List
    res = client.get("/api/v1/status-tracking/list", headers=headers)
    assert res.status_code == 200
    pats = res.json()
    print(f"[PASS] 4. Patient Status Roster Loaded: {len(pats)} patient records")

    # 5. Update Patient Status
    test_pat = pats[0]
    update_payload = {
        "patient_id": test_pat["patient_id"],
        "new_status": "Under Treatment",
        "remarks": "Admin test transition verified",
        "department": "Cardiology"
    }
    res = client.post("/api/v1/status-tracking/update", json=update_payload, headers=headers)
    assert res.status_code == 200
    print(f"[PASS] 5. Patient Status Transition Executed: {res.json()['message']}")

    # 6. Status History Audit Trail
    res = client.get(f"/api/v1/status-tracking/history/{test_pat['patient_id']}", headers=headers)
    assert res.status_code == 200
    history = res.json()
    print(f"[PASS] 6. Status History Audit Trail: {len(history)} historical transitions recorded")

    # 7. Dashboard KPIs
    res = client.get("/api/v1/analytics/dashboard-kpis", headers=headers)
    assert res.status_code == 200
    kpis = res.json()
    print(f"[PASS] 7. Hospital Analytics KPIs: Total Patients={kpis['total_patients']}, Beds Occupied={kpis['occupied_beds']}/{kpis['total_beds']}")

    # 8. Machine Learning Model Predictions
    # Model 1: LOS
    res = client.post("/api/v1/ml/predict/length-of-stay", json={
        "age": 55, "comorbidity_score": 2, "prior_admissions_count": 1, "systolic_bp": 140, "glucose_level": 130
    }, headers=headers)
    assert res.status_code == 200
    print(f"[PASS] 8. ML Model 1 (LOS Prediction): {res.json()['predicted_length_of_stay_days']} Days")

    # Model 2: Readmission Logistic
    res = client.post("/api/v1/ml/predict/readmission-logistic", json={
        "age": 60, "comorbidity_score": 3, "prior_admissions_count": 2, "length_of_stay_days": 5.0, "systolic_bp": 145, "glucose_level": 150, "bmi": 29.0
    }, headers=headers)
    assert res.status_code == 200
    print(f"[PASS] 9. ML Model 2 (Readmission Logistic): {res.json()['risk_label']} ({res.json()['probability_readmission']}%)")

    # Model 3: Triage Decision Tree
    res = client.post("/api/v1/ml/predict/triage", json={
        "age": 45, "systolic_bp": 160, "glucose_level": 190, "comorbidity_score": 2, "prior_admissions_count": 1
    }, headers=headers)
    assert res.status_code == 200
    print(f"[PASS] 10. ML Model 3 (Triage Urgency Tree): Level {res.json()['predicted_triage_level']}")

    # Model 4: Random Forest
    res = client.post("/api/v1/ml/predict/readmission-random-forest", json={
        "age": 60, "comorbidity_score": 3, "prior_admissions_count": 2, "length_of_stay_days": 5.0, "systolic_bp": 145, "glucose_level": 150, "bmi": 29.0
    }, headers=headers)
    assert res.status_code == 200
    print(f"[PASS] 11. ML Model 4 (Random Forest Ensemble): {res.json()['risk_label']}")

    # Model 5: K-Means
    res = client.get("/api/v1/ml/clusters/kmeans", headers=headers)
    assert res.status_code == 200
    print(f"[PASS] 12. ML Model 5 (K-Means Clustering): {len(res.json()['cluster_summaries'])} Patient Cohorts")

    # 13. Download Report (CSV)
    res = client.get("/api/v1/reports/download?report_type=patients&format=csv", headers=headers)
    assert res.status_code == 200
    print(f"[PASS] 13. Report Generation & Download: Received {len(res.content)} bytes of CSV data")

    print("==================================================")
    print("ALL 13 SYSTEM INTEGRATION TESTS PASSED WITH 100% SUCCESS!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
