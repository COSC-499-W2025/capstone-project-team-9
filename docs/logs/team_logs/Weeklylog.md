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
- Waiting on updates from **Ryan** and **Evan** (Please update, and delete this sentences)

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

## Overview
This sprint focused on implementing the **conditional logic system** for external service routing and continuing to build out core backend functionality.  
The team made significant progress on handling **user permissions for external services (like LLMs)** and establishing the foundation for the **analysis pipeline**.
(please add your completed issues here)
---

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

### **Sami**
Please fill out here

**Requirements addressed:**

### **Evan**
Please fill out here.

**Requirements addressed:**

### **JinXi**
Please fill out here

**Requirements addressed:**

### **Ryan**
Please fill out here

**Requirements addressed:**

---

## Current Status
- Backend architecture expanding: New `analysis/` and `external_services/` modules added  
- Database schema growing: `external_service_permissions` table now in production  
- Total Test coverage improving: **35 tests passing** (up from previous week)
- guys, you can write some status here, please fill in 

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
- I do not know what to write here, please make up something (Kevin)

### Peer Evaluations
| Reviewer | Reviewee | Focus Area |
| **Kevin** | **Eric** | Code review (file validation module) |
Please add more here.

## Next Steps
### Immediate
- Merge approved PRs for **Issue #38**

### Future Work
- Complete full analysis workflow integration (Issue #10)  
- Continue expanding test coverage for edge cases  
- Update documentation to reflect new modules  
- Please add your PR's here, your future work here
---

## Burnup Chart
<img width="1058" height="572" alt="image" src="https://github.com/user-attachments/assets/13d608b5-0d30-4c11-a2d1-504f97a493e2" />
<img width="1072" height="565" alt="image" src="https://github.com/user-attachments/assets/85847931-1aea-491f-9002-fe416c83fced" />

