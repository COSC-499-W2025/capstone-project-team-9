
# Features Proposal for Project Option Mining Digital Work Artifacts

**Team Number:** 9  
**Team Members:**  
- Sami Jaffri (44165611)  
- Kevin Zhang (10811057)  
- Ryan Eveson (99775389)  
- TianXing (Eric) Chen (47368527)  
- Evan Pasenau (36403509)  
- Jinxi Hu (48528608)  

---

## 1. Project Scope and Usage Scenario
The basic usage scenario involves graduating students and early-career professionals as the primary user group who regularly create digital work artifacts on their computers and need to systematically catalog and analyze their professional output for career advancement purposes. A secondary user group consists of career counselors and academic advisors who may guide students in using these insights to better articulate their professional growth and identify areas for skill development.  

---

## 2. Proposed Solution
Our project provides value to students, employees, and their managers by quantifying the volume of work they have completed and providing insightful metrics to summarize their contributions concisely and discreetly.  

We will use **Python Flask APIs** and connect to a **Docker SQL database**, allowing us to collect more data and derive deeper insights than local-only processing. This enables customized graphs and metrics tailored to each user, unlike generic dashboards from other teams.  

Additionally, our **cloud-based deployment** will gather files from multiple sources simultaneously, making it easier for users to upload all their data while increasing the confidence and accuracy of analysis.  

---

## 3. Use Cases

### Use Case 1: Scan & Ingest Artifacts
- **Primary Actor:** Student/Early Professional  
- **Description:** User connects to GitHub, Google Drive, or local files, initiates a scan, and ingests digital work artifacts. Metadata is standardized and stored for searching, analytics, and portfolio generation.  
- **Preconditions:**
  1. User logged in and authenticated.  
  2. At least one data source connected.  
  3. Permissions granted.  
- **Postconditions:**
  1. Artifacts and metadata stored in DB.  
  2. Job status updated (Completed/Failed).  
  3. Search index generated.  
- **Main Scenario:** User starts scan → selects sources → system fetches and processes → data stored → summary displayed.  
- **Extensions:**  
  - Data source unavailable → marked Failed.  
  - User cancels scan → job marked Canceled.  
  - Parsing error → skipped, flagged.  
  - Duplicate detection → metadata updated.  

---

### Use Case 2: Summarize and Analyze Project Experience
- **Primary Actor:** Student  
- **Supporting Actors:** Programming staff (integration/setup).  
- **Description:** Analyze a project folder/repo and produce analytical reports (size, file counts, LOC, language distribution).  
- **Preconditions:**  
  1. User logged in.  
  2. Source folder/repo specified.  
  3. Permissions granted.  
- **Postconditions:**  
  1. Visualization generated, saved, and displayed.  
  2. Metadata logged.  
- **Main Scenario:** User selects repo → system retrieves, analyzes, generates metrics → results displayed & downloadable.  
- **Extensions:** Invalid source, permission issues, no files, job fail, or user cancellation.  

---

### Use Case 3: Build and Edit Resume / Portfolio
- **Primary Actor:** Student/Early Professional  
- **Description:** Create and edit resume/portfolio using stored artifacts and analytics. Export as PDF, Markdown, or Web page.  
- **Preconditions:**  
  - User logged in.  
  - At least one completed scan available.  
  - Permissions granted.  
- **Postconditions:**  
  - Resume/portfolio generated, saved, and linked to user profile.  
  - File available for download/share.  
- **Main Scenario:** User selects artifacts → system generates preview → user edits and exports.  
- **Extensions:** Missing artifacts, export failure, unsupported formats, unsaved changes, version control.  

---

### Use Case 4: Search & Filter Artifacts
- **Primary Actor:** Student/Early Professional  
- **Description:** Search and filter imported artifacts by keyword, type, tags, date range, or source.  
- **Preconditions:**  
  - User logged in.  
  - Artifacts already scanned and stored.  
- **Postconditions:**  
  - Matching results displayed with metadata.  
  - Results can be used for analysis/portfolio.  
- **Main Scenario:** User searches → system queries DB → results displayed → user interacts.  
- **Extensions:** No results, network delay, invalid filter combo.  

---

### Use Case 5: View Portfolio
- **Primary Actor:** HR Representative  
- **Supporting Actor:** Student/Early Professional (portfolio owner)  
- **Description:** HR views portfolio via secure link or login. Portfolio includes projects, analytics, resume data.  
- **Preconditions:**  
  - At least one portfolio generated.  
  - HR given access.  
  - Permissions configured.  
- **Postconditions:**  
  - HR views portfolio successfully.  
  - System logs access details.  
- **Main Scenario:** HR opens link → system verifies → portfolio displayed → HR navigates/downloads.  
- **Extensions:** Expired link, permission denied, download disabled.  

---

## 4. Requirements, Testing, Requirement Verification

### Technology Stack & Test Frameworks
- **Backend:** Python Flask (REST APIs)  
- **Frontend:** React + TypeScript  
- **Database:** Dockerized PostgreSQL  
- **CI/CD:** GitHub Actions + Cloud deployment  
- **Test Frameworks:**  
  - Pytest (backend)  
  - Jest + React Testing Library (frontend)  
  - Postman/Newman (API)  
  - GitHub Actions (automation)  

---

### Requirements Table

| Requirement | Description | Test Cases | Who | Difficulty |
|-------------|-------------|------------|-----|------------|
| File Collection | Collect files; allow search/filter; request permission. | Positive: verify collection & search; Negative: handle unsupported formats, duplicates, denied perms. | Jinxi | Med |
| Organizing Data & Metrics | Organize files, detect similarities/trends, visualize. | Positive: correct categorization & graphs; Negative: handle mislabeled/missing data. | Tiangxi | Hard |
| Front-End Dashboard | Register/login, filter, graphs, admin control. | Positive: login works; Negative: invalid credentials rejected. | Sami | Med |
| Summarization & Analysis | Summarize files into reports. | Positive: all files summarized; Negative: corrupted files handled. | Ryan | Easy |
| User Authentication | Secure access to analysis. | Positive: authenticated users access dashboard; Negative: unauthorized attempts blocked. | Evan | Med |
| Visualization Dashboard | Display graphs dynamically. | Positive: real-time updates; Negative: missing data doesn’t break. | Kevin | Easy |
| Performance (NFR) | Fast response times. | Positive: load <3s; Negative: handle load. | Jinxi | Med |
| Scalability (NFR) | Handle multiple devices/users. | Positive: support 3 devices; Negative: excess queued. | Sami | Med |
| Reliability (NFR) | Stable, error handling. | Positive: >99% uptime; Negative: no system-wide crash. | Evan | Hard |
| Usability (NFR) | Accessible to new users. | Manual: 80% new users succeed unaided. | Ryan | Easy |

---

### Functional & Non-Functional Requirements

- **FR-01:** Connect to external data sources securely (UC2).  
- **FR-02:** Upload files from multiple folders/devices (UC2).  
- **FR-03:** Scan sources and collect artifacts/metadata (UC2).  
- **FR-04:** Standardize, categorize, index files (UC2, UC3).  
- **FR-05:** Provide search & filter functions (UC3).  
- **FR-06:** Generate analytics visualizations (UC3).  
- **FR-07:** Export portfolio in multiple formats (UC1).  
- **NFR-01:** Process ≤500 files in <10s (UC2).  
- **NFR-02:** Encrypt all data in transit (TLS 1.2+) (UC2, UC3).  
- **NFR-03:** Maintain 99% uptime (UC2, UC3).  
- **NFR-04:** UI loads in <3s on broadband (UC1, UC2, UC3).  

---

### Testing Plan

- **FR-01:**  
  - Positive: Connect GitHub via OAuth2 → success.  
  - Negative: Expired token → rejected.  
- **FR-02:**  
  - Positive: Upload from multiple folders → success.  
  - Negative: Upload none → error.  
- **FR-03:**  
  - Positive: Scan GitHub + Google Drive → both scanned.  
  - Negative: Unreachable source → marked Failed.  
- **FR-04:**  
  - Positive: Mixed file types categorized correctly.  
- **FR-05:**  
  - Positive: Keyword search returns correct artifacts.  
  - Negative: Invalid/empty query → handled.  
- **FR-06:**  
  - Positive: Generate analytics → accurate.  
- **FR-07:**  
  - Positive: Export portfolio PDF → correct artifacts.  
- **NFR-01:** Upload/scan 500 files ≤10s.  
- **NFR-02:** All requests encrypted.  
- **NFR-04:** Dashboard loads ≤3s, responsive.  

---

### Requirement Verification

| ID | Linked Use Case | Verification Method | Automation |
|----|-----------------|----------------------|------------|
| FR-01 | UC2 | API Test (OAuth2) | Automated |
| FR-02 | UC2 | Functional Test (upload multiple folders/devices) | Automated |
| FR-03 | UC2 | Integration Test (multi-source scanning) | Automated |
| FR-04 | UC2, UC3 | Functional Test (categorization/indexing) | Automated |
| FR-05 | UC3 | Functional Test (search/filter) | Automated |
| FR-06 | UC3 | Integration Test (analytics) | Automated |
| FR-07 | UC1 | End-to-End Test (portfolio generation) | Automated |
| NFR-01 | UC2 | Performance Test (large dataset) | Semi-automated |
| NFR-02 | UC2, UC3 | Security review + automated API tests | Hybrid |
| NFR-03 | UC1–UC3 | Usability testing (devices) | Manual |

---

## 5. Workload Distribution

| ID | Assigned Member | Difficulty |
|----|-----------------|------------|
| FR-01, FR-02 | Sami | Medium |
| FR-03 | Kevin | Hard |
| FR-04 | Ryan | Hard |
| FR-05, FR-06 | Evan | Medium |
| FR-07 | Eric | Medium |
| NFR-01 | Jinxi | Hard |
| NFR-02 | Kevin | Medium |
| NFR-03 | Eric | Easy |

---

## UML Diagrams
Please refer to the end of the PDF file in this folder. 

