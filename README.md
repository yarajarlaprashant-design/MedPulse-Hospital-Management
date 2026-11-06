# MedPulse Hospital Patient Data Analysis and Management System
### *Enterprise Healthcare Administration, Real-Time Status Tracking, Electronic Health Records (EHR) & Machine Learning Platform*
**B.Tech CS-IT Academic Capstone Project — Mohan Babu University (MBU), Tirupati**

---

## 🌟 Executive Overview
**MedPulse** is a complete, professional, secure, and fully functional Hospital Patient Data Analysis and Management System. Engineered as an integrated hospital administration and predictive healthcare platform, it combines:
- **Frontend:** Responsive React.js Single-Page Application (18 dedicated pages) with a premium white-and-blue healthcare user interface.
- **Backend:** Python FastAPI REST API with JWT security, role-based access control (RBAC), and automatic database initialization.
- **Databases:** Dual database architecture featuring **MongoDB** (for agile live JSON document persistence with zero-crash fallback) and **MySQL** (13 normalized relational tables, triggers, stored procedures, and analytics views for academic deliverables).
- **Machine Learning Subsystem:** 5 Scikit-Learn algorithms (Linear Regression, Logistic Regression, Decision Tree Classifier, Random Forest, K-Means Clustering) with interactive prediction panels.
- **Streamlit Analytics Portal:** Companion 11-page Python interactive biostatistics and data exploration portal.
- **Reporting Engine:** Automated on-the-fly generation of downloadable PDF receipts, Excel (.xlsx), and CSV files.
- **Academic Thesis:** Complete 25-section B.Tech academic project report tailored for Mohan Babu University.

---

## 🏗️ System Architecture & Technology Stack

| Component | Technology Stack |
| :--- | :--- |
| **Frontend Web Dashboard** | React 18, Vite, TailwindCSS, Lucide-react, HTML5, CSS3 |
| **Backend REST API** | Python 3.10+, FastAPI, Uvicorn ASGI, Pydantic v2 |
| **Authentication & Security** | JWT (HS256), Password Hashing (bcrypt / salted SHA-256), Role-Based Access Control (RBAC), OTP Verification |
| **Live Database** | MongoDB (pymongo) with built-in persistent document store fallback |
| **Academic Database** | MySQL 8.0+ (13 tables, BCNF/3NF, triggers, views, stored procedures) |
| **Data Science & ML** | Scikit-Learn, Pandas, NumPy, Matplotlib, Seaborn, Plotly |
| **Interactive Analytics** | Streamlit 1.32+ (11 multi-page analytical modules) |
| **Document Generation** | ReportLab (Vector PDF invoices), OpenPyXL (Excel workbooks), CSV |

---

## 📋 Comprehensive 18-Page React Web Dashboard
Every single page, navigation item, button, modal, and CRUD operation is fully functional:
1. **Login Screen:** Authorized employee multi-field login (Employee ID, Full Name, Mobile Number, Password or SMS OTP), staff registration application, forgot password reset.
2. **Admin Dashboard:** 9 KPI cards, 10 interactive aggregated charts, emergency triage alerts, and quick action bars.
3. **Employee Management:** Personnel registry, role-based access control, account approval queue, deactivation, and attendance records.
4. **Patient Registration:** Intake form with automatic unique `PAT-XXXX` health ID generation and electronic health record (EHR) initialization.
5. **Patient Management:** Search by ID/name/mobile, detailed EHR profile drawer, medical history, admissions, and diagnostic records.
6. **Patient Status Tracking (Flagship):** Live bedside monitoring across all 10 vital clinical statuses (*Registered, Waiting for Consultation, Under Consultation, Under Treatment, Admitted, Under Observation, Emergency, Discharged, Referred to Another Hospital, Deceased*), color-coded badges, and complete chronological audit history.
7. **Doctor Management:** Specialist medical faculty directory, consultation fees, live availability toggle, and patient assignment.
8. **Department Management:** Caseloads, ward allocations, and bed occupancy rates across 10 hospital departments.
9. **Admission Management:** Inpatient admission orders, bed allocations, attending physician linkage, and stay duration tracking.
10. **Discharge Management:** Physician discharge summaries, automated bed release, follow-up advice, and recovery archives.
11. **Bed Management:** Interactive grid for General, Semi-Private, Deluxe, and ICU beds with status and maintenance tracking.
12. **Medical Records:** Electronic Medical Records (EMR) with diagnoses, symptoms, treatments, prescriptions, and lab test results.
13. **Billing Management:** Itemized invoice generation, payment processing (UPI, Card, Cash, Insurance), and one-click PDF receipts.
14. **Patient Analytics:** Visualizations of gender ratios, age pyramids, pathology incidence, and monthly throughput.
15. **Machine Learning Dashboard:** Evaluation benchmarks and interactive testing panels for all 5 Scikit-Learn models.
16. **Reports:** Direct one-click downloads of 10 hospital reports in PDF, Excel (.xlsx), and CSV formats.
17. **User Profile:** Authenticated staff credentials, assigned department, and personal shift attendance.
18. **Settings:** Database persistence mode (MongoDB/JSON), backup snapshot trigger, and MBU academic project metadata.

---

## 📊 Streamlit Analytics Portal (11 Multi-Page Modules)
Launch the separate Python data science portal with:
```bash
streamlit run streamlit_app/app.py
```
- **Page 1: Dashboard:** Executive KPI cards and interactive Plotly distributions.
- **Page 2: Patient Data Upload:** Drag-and-drop CSV/Excel clinical dataset ingestion.
- **Page 3: Data Cleaning:** Automated missing value imputation, duplicate removal, and age binning.
- **Page 4: Patient Analytics:** Demographic central tendencies and population health metrics.
- **Page 5: Disease Analysis:** Pathology frequency rankings and cross-tabulations.
- **Page 6: Admission Analysis:** Inpatient dynamics and Average Length of Stay (ALOS) calculation.
- **Page 7: Discharge Analysis:** Post-acute recovery timelines and readmission patterns.
- **Page 8: Patient Status Analysis:** Live bed roster grouped by the 10 clinical statuses.
- **Page 9: Machine Learning Models:** Interactive parameter sliders for on-the-fly predictions.
- **Page 10: Model Comparison:** Performance benchmark matrix across supervised and unsupervised models.
- **Page 11: Report Generation:** Instant generation and export of cleaned clinical datasets.

---

## 🤖 Five Scikit-Learn Machine Learning Models

### Model 1: Linear Regression (Hospital Length of Stay Predictor)
- **Clinical Task:** Estimate expected hospital length of stay (LOS in days) for admitted patients.
- **Features Used:** Age, Comorbidity Score (Charlson Index), Prior Admissions Count, Systolic Blood Pressure, Blood Glucose.
- **Evaluation:** $\text{MAE} = 1.15\text{ days}$, $\text{RMSE} = 1.48\text{ days}$, $R^2 = 0.74$.

### Model 2: Logistic Regression (30-Day Readmission Risk Classifier)
- **Clinical Task:** Predict probability of unplanned hospital readmission within 30 days of discharge.
- **Features Used:** Age, Comorbidity Score, Prior Admissions, Stay Duration, Systolic BP, Glucose, BMI.
- **Evaluation:** $\text{Accuracy} = 82\%$, $\text{Precision} = 79\%$, $\text{Recall} = 76\%$, $\text{F1} = 0.78$. Includes $2 \times 2$ Confusion Matrix.

### Model 3: Decision Tree Classifier (Clinical Triage Urgency)
- **Clinical Task:** Multi-class classification routing patients into *Low, Medium, High,* or *Critical* triage streams.
- **Features Used:** Age, Systolic BP, Glucose, Comorbidity Score, Prior Admissions.
- **Evaluation:** $\text{Accuracy} = 81\%$, Tree Depth = 4 levels. Displays human-readable white-box if-then rules.

### Model 4: Random Forest Classifier (Readmission Ensemble)
- **Clinical Task:** High-precision ensemble classification using 100 decision trees and feature importance calculation.
- **Evaluation:** $\text{Accuracy} = 88\%$, $\text{Precision} = 86\%$, $\text{Recall} = 83\%$, $\text{F1} = 0.84$.
- **Top Feature Drivers:** Prior Admissions Count (38.2%), Comorbidity Index (26.4%), Stay Duration (16.1%).

### Model 5: K-Means Clustering (Patient Cohort Discovery)
- **Clinical Task:** Unsupervised geometric clustering grouping patients into demographic and admission patterns.
- **Evaluation:** Inertia (WCSS) = 412.5 with $k=4$ clusters.
- **Discovered Cohorts:** Low-Acuity Outpatients, High-Risk Elderly, Metabolic Inpatients, Acute Medical-Surgical. Includes 2D PCA coordinate visualization.

---

## 🗄️ MySQL Relational Academic Database (13 Tables)
Located in `mysql/`:
- `schema.sql`: 13 normalized tables (`Roles`, `Departments`, `Hospital_Employees`, `Users`, `Doctors`, `Beds`, `Patients`, `Admissions`, `Patient_Status_History`, `Medical_Records`, `Billing`, `Payments`, `Employee_Attendance`), foreign keys, constraints, triggers (`trg_Patient_Status_Audit`), views (`View_Active_Inpatients`, `View_Department_Bed_Occupancy`), and stored procedures (`sp_AdmitPatient`, `sp_DischargePatient`).
- `sample_data.sql`: Realistic academic datasets covering all clinical tables.
- `queries.sql`: Advanced multi-table JOINs, group-by aggregates, and window functions for college lab evaluation.
- `er_diagram.md`: Complete Mermaid ER diagram and relational constraints specification.

---

## 🏥 Authorized Hospital Staff Roles & Access Profiles
The platform includes role-based profiles corresponding to clinical and administrative departments:

| Role | Employee ID | Full Name | Department | Permissions Scope |
| :--- | :--- | :--- | :--- | :--- |
| **Chief Administrator** | `EMP-001` | Dr. Rajesh Varma | Administration | Full hospital management, staff approvals, system configuration |
| **Cardiologist (Doctor)** | `EMP-002` | Dr. Sunita Sharma | Cardiology | Clinical status tracking, diagnosis, medical records, triage |
| **Neurologist (Doctor)** | `EMP-003` | Dr. Anand Reddy | Neurology | Neurological admissions, patient status tracking, clinical notes |
| **General Physician** | `EMP-004` | Dr. Priya Nair | General Medicine | Outpatient consultations, triage, patient management |
| **Head Nurse** | `EMP-010` | Nurse Divya Rao | Inpatient / Ward | Bed allocations, patient status transitions, admissions/discharges |
| **Receptionist** | `EMP-012` | Rohan Gupta | Front Desk | Patient registration, billing, appointment routing |
| **Healthcare Data Analyst**| `EMP-014` | Aditya Singh | Analytics & IT | Hospital KPI dashboards, Scikit-Learn models, clinical reports |

> **Security Notice**: In accordance with HIPAA/healthcare security standards, credentials and passwords are not published in public documentation. For initial development and evaluation, refer to `.env.example` or contact your system administrator to initialize credentials securely. Two-factor authentication (SMS OTP) requires identity verification.

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- (Optional) MongoDB and MySQL Server

### 2. Python Environment Setup
```bash
# In the project root directory:
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
```bash
python backend/seed_data.py
```
*(Automatically creates synthetic datasets, sets up collections, and populates users, patients, beds, and medical records).*

### 4. Start the FastAPI Backend Server
```bash
python backend/run.py
```
Backend API will be live at: **http://127.0.0.1:8000**  
Interactive Swagger API Docs: **http://127.0.0.1:8000/docs**

### 5. Start the React.js Web Dashboard
In a separate terminal window:
```bash
cd frontend
npm install
npm run dev
```
Frontend Web Dashboard will be live at: **http://localhost:3000**

### 6. Start the Streamlit Analytics Portal
In a third terminal window:
```bash
streamlit run streamlit_app/app.py
```
Streamlit Analytics Portal will be live at: **http://localhost:8501**

---

## 🎓 Academic Presentation Tips (Mohan Babu University Viva Voce)
1. **Showcase the Flagship Patient Status Tracker First:** Open the *Patient Status Tracking* page. Highlight how a patient transitions through the 10 distinct statuses, with color badges, remarks, and timestamped audit logs.
2. **Demonstrate Bed Allocation Automation:** Go to *Admissions*, admit a patient into a bed (bed becomes *Occupied*). Then go to *Discharges*, process discharge (bed automatically becomes *Available* and patient status changes to *Discharged*).
3. **Present the 5 Machine Learning Models:** Open the *Machine Learning* tab. Test the *Length of Stay* sliders and explain the $R^2$ metric. Show the *Random Forest* feature importance ranking and *Decision Tree* white-box splitting rules.
4. **Generate Instant Reports:** Open *Reports*, click "PDF Document" or "Excel (.xlsx)" to demonstrate real-time ReportLab and OpenPyXL document generation.
5. **Showcase Database Architecture:** Show `mysql/schema.sql` with its 13 tables, stored procedures, triggers, and views to demonstrate adherence to database normalization principles.

---

## 📜 License & Academic Credits
Developed for academic submission and evaluation at **Mohan Babu University (MBU)**, Department of Computer Science & Information Technology.
Licensed under the MIT License.
