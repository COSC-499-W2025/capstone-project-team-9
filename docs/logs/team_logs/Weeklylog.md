# Sprint Report week 5 (2025/09/29 to 2025/10/05)

## Overview
This sprint focused on the planning and design phase of the project. The team worked on creating the system's data flow representations and finalizing early design documents.

## Completed Work
- **Data Flow Diagram (DFD) Level 0** completed  
- **Data Flow Diagram (DFD) Level 1** completed
- <img width="463" height="134" alt="image" src="https://github.com/user-attachments/assets/94b2c8a1-6155-4a68-85c2-989878f6f9b9" />


## Current Status
- No code implementation at this stage  
- The project is still in the **planning and design phase**
- Receive feed back and communicate with serval teams:
      team 16, 6, 3, 10, 5, 18

## Testing
- No testing required since there is **no code yet**

## Burnup Chart
<img width="990" height="489" alt="image" src="https://github.com/user-attachments/assets/6dca39fb-e478-41ee-b1f8-9854912ff845" />

# Sprint Report – Week 6 (2025/10/06 to 2025/10/12)

## Overview
This sprint marked the transition from planning and design into **initial implementation**.  
The team began developing core system modules, connecting the database, and writing the first round of automated tests.

## Completed Work
- **Requirement #1 (issue #6) – User Consent Management** implemented by **Kevin**
  - Includes consent scope definition, status checking before data access, and withdrawal handling  
  - Related sub-issues: #11, #14, #18  
- **Database connection and configuration** verified; test scripts executed successfully  
- **File format validation** feature completed by **Eric** (#23)  
- **File-listing functionality** (nested folder display) expanded by **Jinxi** (#35)  
- **Initial test cases** added for consent and database modules  
- **Team collaboration setup** refined: branch naming, pull-request workflow, and environment consistency  
- **Sami** focused on reviewing pull requests and assisting with environment setup  
- **Evan** focused on reviewing code and assigning issues and creating issues for features and tasks
- Waiting on updates from **Ryan** (Please update, and delete this sentences)

## Current Status
- Core backend structure and modules created under `src/consent/`  
- Database container (PostgreSQL) successfully built and running via Docker  
- Unit tests passing locally  
- PR for Requirement #1 (issue #6) under review  
- Preparing for next sprint: integrating file operations with consent logic

## Testing
- **Pytest** configured and executed  
- Verified database connection tests (`test_db_connection.py`)  
- Verified consent management tests (`test_consent.py`)  
- All current tests pass locally, CI integration planned for next sprint

## Next Steps
- Merge approved PRs into `main`  
- Begin work on next project
- Expand unit tests for error handling and invalid consent scenarios  
- Ensure documentation and weekly logs remain up to date

## Burnup Chart
<img width="1084" height="554" alt="image" src="https://github.com/user-attachments/assets/76e1fbc8-3bbb-4a26-89ef-47b3a82c0de5" />
<img width="1040" height="514" alt="image" src="https://github.com/user-attachments/assets/89ca42dd-fe09-4293-a87d-7388ec1898f8" />

# Sprint Report – Week 7 (2025/10/13 to 2025/10/19)

## **Overview**
This sprint focused on implementing the conditional logic system for **external service routing** and continuing to build out core backend functionality.  
The team made significant progress on handling **user permissions for external services (like LLMs)** and establishing the foundation for the **analysis pipeline**.  
(please add your completed issues here)

## Completed Work

### **Kevin**
- **Issue #10 (Sub-issue #38)** – Conditional Logic for External Service Routing implemented  
  - Created `AnalysisRouter` class to route analysis based on user permissions  
  - Implemented `ExternalServicePermission` manager for checking user preferences  
  - Added `ServiceConfig` for storing external service permissions in PostgreSQL  
  - Created `external_service_permissions` database table with proper indexing  
  - Added **8 comprehensive unit tests** covering all routing scenarios  
  - All tests passing 
  - Pull request submitted and ready for review  

**Requirements addressed:**
- Sub-issue #38 – Implement conditional logic to check user preference  

---

### **Eric**
This week, I continued working on backend feature development and focused on improving data management and user preference handling. 
The main goal was to make the system more dynamic, user-centric, and capable of handling real-time updates.
 - Implemented the backend functionality that allows users to upload .zip project files directly into the database.
 - Added logic to process and prepare uploaded files for future analysis, ensuring the data pipeline can start right after consent is granted.

**Requirements addressed:**
- Issue #54 - Allow the user to upload files into a database so that these can be parsed
- Issue #40 - Ensure database is continually updated with the user’s preferences

---

### **Sami**
Please fill out here.

**Requirements addressed:**

---

### **Evan**
This week I worked on a new feature (issue 42) to allow users to consent to whether or not they want collaborative work to be included. I did this by creating an interactive UI in the terminal and creating all the background necessities in order to store this user preference. I also wrote unit tests as well as manually testing this feature. In addition I reviewed code for ryan, sami and kevin this week

**Requirements addressed:**

---

### **JinXi**
This week, I still working on backend development, focused on the file reading and tempdata management.
The main goal is make the system read file faster and get a tool that can effectively save, read or delete temporary data.

**Requirements addressed:**
- Issue #34 - Skip all folders then end with "/": Allow system use str to define a path is file or folder
- Issue #33 - Store Extracted Data: Allow system to store temp data in memory or tempfile, and provide functions to read, write, and delete them.

---

### **Ryan**
This week I started working on a new feature. This was a feature that allowed the user to list all projects that had been uploaded to the uploaded_files table in our database. This was done by calling the database and filtering the files that are stored using JSON to only fetch the files inside folders. Along with this i refactored the main.py page so that it becomes more simple to interact with in the CLI. 

**Requirements addressed:**
- Issue #70 - Produce a list of all projects
---

## Current Status
- Backend architecture expanding: New `analysis/` and `external_services/` modules added  
- Database schema growing: `external_service_permissions` table now in production  
- Total Test coverage improving: **35 tests passing** (up from previous week)
- A lot of code Refactoring has occured to ensure that it stays reasable throughout our process.
- Features are being built, and we will need to make sure that we are not rebuilduing these features in seperate pull requeusts 

---

## Testing
- **All tests passing:** 35/35 successful  
- **New test coverage added:**
  - `test_analysis_router.py` (8 tests)
    - Routing logic with/without permissions  
    - Database operations for service permissions  
    - Strategy selection (local vs enhanced)  
- **Test infrastructure stable:** pytest configuration consistent across team environments  
- If there is new test coming in, please add in here.

---


## Team Collaboration & Peer Evaluation

### Collaboration Highlights
- All members participated in at least one **peer review** through GitHub Pull Requests 
- Improved coordination using shared GitHub Projects board and Discord communication channel

### Peer Evaluations
| Reviewer | Reviewee | Focus Area |
|-----------|-----------|-------------|
| **Kevin** | **Eric** | Code review (file validation module) |
| **Kevin** | **Jinxi** | Code review (mplement conditional logic for external service routing) |
| **Jinxi** | **Evan** | Bug fix: File_lister incorect ordering |
| **Ryan** | **Sami** | Bug fix #65:Reiviewed Samis PR. This is a small commit and addresses issues in our main.py, and upload_file.py files.|
| **Ryan** | **Evan** | Bug fix: test suites wree not running properly on MAC, therefore he fixed the list order |
| **Ryan** | **Evan** | Issue#42: allows the user to choose whether or not collaborative work is included in the summary |
Please add more here.

## Next Steps
### Immediate
- Merge approved PRs for **Issue #38**

### Future Work
- Complete full analysis workflow integration (Issue #10)  
- Continue expanding test coverage for edge cases  
- Update documentation to reflect new modules  
---

## Burnup Chart
<img width="1058" height="572" alt="image" src="https://github.com/user-attachments/assets/13d608b5-0d30-4c11-a2d1-504f97a493e2" />
<img width="1072" height="565" alt="image" src="https://github.com/user-attachments/assets/85847931-1aea-491f-9002-fe416c83fced" />

# Sprint Report – Week 8 (2025/10/20 to 2025/10/26)

## **Overview**
This sprint focused on extending the analysis workflow to support **LOCAL-only operations** (no external APIs), ensuring the system works in offline and privacy-sensitive environments. We emphasized file categorization, skill extraction, and user-respecting behavior when external services are declined.

## Completed Work

### **Kevin**
This PR implements the **LOCAL analysis methods** that work entirely without external APIs:
- All analysis happens on the **local machine**
- **No data** is sent to external services
- Provides **meaningful feedback** even when users decline external service usage
- Categorizes files into: **code, documents, design, config, other**
- Extracts skills from: **languages, frameworks, testing, documentation, version control**

**Requirements addressed:**
- Issue #81 – Implement Local-Only Analysis
- Issue #85 – Improve Skill Extraction and Categorization

---

### **Eric**
*(Please fill out your Week 8 items.)*  
Suggested points:
- Features or improvements delivered  
- Any database / analysis enhancements  
- Issue references and testing notes

**Requirements addressed:**

---

### **Sami**
*(Please fill out your Week 8 items.)*  
Suggested points:
- PRs, bug fixes, reviews  
- Testing or infra contributions  
- Issue references

**Requirements addressed:**

---

### **Evan**
*(Please fill out your Week 8 items.)*  
Suggested points:
- New features or UX/CLI updates  
- Unit/integration tests added  
- Reviews / collaboration work

**Requirements addressed:**

---

### **JinXi**
*(Please fill out your Week 8 items.)*  
Suggested points:
- Backend/file-handling/refactors  
- Performance/robustness improvements  
- Issue references and tests

**Requirements addressed:**

---

### **Ryan**
*(Please fill out your Week 8 items.)*  
Suggested points:
- New feature(s) completed  
- Refactors and CLI polish  
- Issue references and tests

**Requirements addressed:**

---

## Current Status
- Local-only analysis integrated alongside external-service path (clean separation of strategies)
- Basic analysis **does not require API keys**
- Existing tests pass; additional local-analysis tests queued for review
- Ongoing refactors to keep modules readable and maintainable

---

## Testing
- Verified local classification and skill extraction across varied file sets
- Confirmed that declining external services cleanly routes to the local path
- Planned additions: edge cases for large repositories, binary/unsupported files, and partial data sets

---

## Team Collaboration & Peer Evaluation

### Collaboration Highlights
- Peer reviews completed via GitHub PRs across team members
- Active coordination using the shared Projects board and Discord

### Peer Evaluations
| Reviewer | Reviewee | Focus Area |
|-----------|-----------|-------------|
| **Kevin** | **Eric** | Review of analysis data flow / DB interactions |
| **Kevin** | **Jinxi** | Review of file handling & temp-data utilities |
| **Ryan** | **Evan** | Review of consent/UI interactions |
| *(Add more rows here)* |  |  |

---

## Next Steps

### Immediate
- Merge the **Local-Only Analysis** PR and incorporate feedback
- Land additional unit tests for categorization and skill extraction

### Future Work
- Integrate local analysis outputs into user-visible reports
- Expand error handling and user messaging for partial analyses
- Continue test coverage growth and docs updates

---

## Burnup Chart
*(Update with latest images for Week 8)*
<img width="1058" height="572" alt="image" src="<!-- paste week8 chart link 1 here -->" />
<img width="1072" height="565" alt="image" src="<!-- paste week8 chart link 2 here -->" />
