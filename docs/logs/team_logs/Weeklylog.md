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
- Issue #39 - internal analysis
  
---

### **Eric**
This week, I continued contributing to the backend feature development phase, focusing on data processing and contribution tracking.
Specifically, I completed two issues that are part of the project analytics module:

🥇 Issue #49 — “Identify activity type and amount of contribution made by the user”

Implemented logic to classify user actions (e.g., commits, merges, file uploads) and quantify their contribution.
Integrated backend processing to automatically recognize and record different types of user activities within the database.
This lays the groundwork for generating contribution analytics in future sprints.
🥈 Issue #50 — “[Rank Projects] Store the amount of work a user has contributed to a project”

Developed a feature to calculate and persist each user’s contribution score to individual projects.
This allows the system to rank projects and users based on activity and contribution level, providing the foundation for future visualization and reporting.
This week involved both coding and testing, ensuring the new contribution-tracking mechanisms worked as expected.
Our team continued to collaborate effectively through regular discussions and reviews, keeping progress smooth and well-coordinated.

---

### **Sami**
- Worked on implementing a new project summary feature
- The feature incorporated 4 sub issues which were also pushed this week
- Refactored code, and imports for better generalization (i.e. some files would only work on specific computers)
- Reviewed 5 PR's and helped with code changes
- Created a new document for keeping track of features in our project
**Requirements addressed:**
- Issue #21, #60, #61, #62, #63

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
Update and part overwrite the file upload function to implement better feedback when user upload files.
- Use a new class called **UploadResult** to store the upload results
- Modify the codes in **upload_file.py** so that all functions can use a object of **UploadResult** to store status of uploading process and return it back to main.py when upload success or failure.
- Modify the codes in **main.py**, so thant it can show print the **UploadResult** out.
- Add test functions for bothe modify in **upload_file.py** and **main.py**.
  
**Requirements addressed:**
- issue 29 - Display error message on the UI, Inform the user of the error type
---

### **Ryan**
This is my PR Description: This pr is a extension of the upload files functionality. It encompasses the sub task of storing all the file contents in a new database. This database is called file_contents and contains all the needed information about the file that is being Stored. It stores information about the extension type, the lines of code, the folder its from etc. this function runs in unison with the upload files function that Sami completed last week. When you store the data.
- This completed issue #76
- Along with this I Updated the Issues board and build a document that is shared with everyone so that we are able to more easily track what we are going to work on over the next 2 weeks. This is done by adding your name to features and writing down a description so that there is less overlap of code. it is very similar to our project table that we hae in github but it allows for us to explain our processes in more detail

**Requirements addressed:**
Store project information into a database
---

### **Evan**
*(Please fill out your Week 8 items.)*  
Suggested points:
- New feature(s) completed: identifying what each contributor did in a collaborative project and creating multiple metrics. 
- Refactors and CLI polish: refactoring the methods for outputing the metrics so that the code is not redundant
- Issue references and tests: issue 43
**Requirements addressed:**
Extrapolate individual contributions for a given collaboration project
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
- We met up 3 times this week and discussed areas that we were struggling in and needed help

### Things to work on / Reflection
We need to ensure that we are understanding the code that others are writing and leaving more in depth reviews of code. We dont want to just review code by running the tests and not actually understanding what each other are doing. Additoinally, we need to work on reducing code repitition. There are a lot of features that overlap and we are rewriting a lot of code. this will need ot be refactored later on to ensure no code overlap occurs. Aside from that, there were a few PR's that needed to get pushed before new features could be added. We created a new document this week that helped keep track of hierarchical devlopment which lets us push features that need to be completed before hand, instead of creating random features and joining them later. 

### Peer Evaluations
| Reviewer | Reviewee | Focus Area |
|-----------|-----------|-------------|
| **Kevin** | **Eric** | Review of analysis data flow / DB interactions |
| **Kevin** | **Jinxi** | Review of file handling & temp-data utilities |
| **Ryan** | **Evan** | Review of consent/UI interactions |
| **Sami** | **Eric**  | Identifying Activity Type and Amount of Contribution |
| **Sami** | **Jinxi**  | Storing Extracted Data |
| **Jinxi** | **Eric** | Review of analysis data flow / DB interactions |
| **Jinxi** | **Kevin** | Review of analysis data flow / DB interactions |
| **Ryan** | **Eric** | Ryan reviewed: Identify the activity type and the amount of contribution made by the user. |
| **Ryan** | **Sami** | Ryan Reviewed: Summarize a Project Feature + Subissues |
| **Ryan** | **Kevin** | Ryan Reviewed: internal analysis #39 |


---

## Next Steps

### Immediate
- Merge the **Local-Only Analysis** PR and incorporate feedback
- Land additional unit tests for categorization and skill extraction

### Future Work
- Integrate local analysis outputs into user-visible reports
- Expand error handling and user messaging for partial analyses
- Continue test coverage growth and docs updates
- Kevin will working on the Feature: Retrieve Portfolio Information #24
- Evan will working on putting collaborative contributions into the database, creating percentages of the work each collaborator has done, sorting projects between individual and collaborative.
- Eric will work on deleting previously generated insights and displaying more key metrics of a project
- Ryan Will be working on Ranking and summarize ranking over the next 2 weeks. I am going to work on this by using Kevin And Erics PRs that they made this week and the metrics that they created to deteremine the best project and output the top ranked projects.
- Jinxi will work on update user information in db function, and code reviewing.
1. plan for rank importance: There is a ranking score that is given by Eric’s code. With Kevin’s metrics that he pulled, and the score that Eric gets, i will create a weighted avg of all projects and rank them.
2. Plan for summarize top projects:I will just summarize the summary of the top 3 projects using samis Summarizing logic. This should be a small PR and i will be able to help anyone who needs help
3. This will just be added to the main.py and will allow the user to get a summary of the top 3 projects. It will not show any information about any other projects.
---

## Burnup Chart
<img width="1052" height="619" alt="image" src="https://github.com/user-attachments/assets/91ae903f-5a34-4592-8a1d-cf0678530db2" />
<img width="1109" height="689" alt="image" src="https://github.com/user-attachments/assets/884639c3-e3a5-45f4-8cba-3ec0f6028c90" />

# Sprint Report – Week 9 (2025/10/27 to 2025/11/02)

## **Overview**
This sprint focused on **refactoring repetitive code**, **improving database maintainability**, and **enhancing the collaborative analysis features**.  
We introduced new utility modules to reduce redundancy, added metrics for more detailed contribution tracking, expanded local analysis capabilities, and implemented a database cleanup tool to simplify re-analysis workflows.  
The overall goal this week was to **optimize code structure**, **increase maintainability**, and **strengthen analysis accuracy** across both individual and collaborative workflows.

## **Completed Work**
#### **PR #101 – Refactoring (Part 1 & 2)**
- Introduced a **`common/constants.py`** file to centralize shared constants across the codebase, eliminating repeated literals.  
- Refactored **database connection logic** by creating a unified **`db_config.py`** module used across 15+ files.  
- Greatly improved **code readability** and **maintenance consistency**.  
- No feature changes or dependency updates, purely structural optimization.  
**Impact:** Reduced code duplication, standardized configuration management, and prepared the backend for faster iteration.

#### **PR #92 – Collaboration: Expanded Metrics**
- Enhanced the **collaborative analytics module** to provide more in-depth contribution insights.  
- Added functions to measure:  
  - **Lines contributed per collaborator**  
  - **Files modified**  
  - **Summary of contributions**  
- Ensures fairer, more transparent evaluation of teamwork.
**Impact:** Strengthens the collaborative component by offering richer data on contributor activity.

#### **PR #102 – Analysis if User Declines Outside Sources**
- Implemented full **privacy-aware analysis fallback** when users opt out of external services.  
- Added **permission prompts**, **privacy information**, and the **ProjectAnalyzer** class for local workflows.  
- Built new menu options:  
  - *Analyze Project*  
  - *Manage External Service Settings*  
- Added a **comprehensive 19-test suite (95%+ coverage)**.  
- Introduced new **database tables** for storing permissions and results.
**Impact:** Fully supports **offline/local analysis** while ensuring privacy and transparency, completing a key part of the user consent system.

### **Kevin**
This week, I completed **PR #102 – Analysis if User Declines Outside Sources**, which delivers the full **local analysis system** with privacy-aware behavior.  
This feature ensures that users can still analyze their projects even if they choose not to use external APIs. The focus was on making the backend both **privacy-compliant** and **fully functional offline**.

#### **Key Work Completed**
- Implemented **ProjectAnalyzer** class to coordinate local and external analysis workflows.  
- Added **external service permission prompts** that explain privacy implications clearly to the user.  
- Integrated **local-only analysis** for language detection, framework recognition, testing patterns, documentation, and version-control metrics.  
- Extended the **main CLI menu** to include:  
  - `Analyze Project (with Local Fallback)`  
  - `Manage External Service Settings`  
- Added a new **database table** for tracking service permissions and analysis results.  
- Wrote **19 comprehensive unit tests** (covering 95 %+ of new functionality).  
- Verified that all user-declined external service scenarios now fall back to secure, offline analysis.

**Requirements addressed:**  
- Issue #102 – Analysis if User Declines Outside Sources  
- (Supports Feature #10 – Conditional Analysis Routing)

---

### **Eric**
This week, I focused on completing Issue #87 — “Cleanup Old Insights”, an important maintenance feature for the project’s data-management module.
Issue #87 — “Cleanup Old Insights”
Implemented a cleanup function to safely remove previously generated insight data from the database.
--The feature now deletes both file_contents and the corresponding records in uploaded_files, ensuring that outdated or unused project data is fully cleared to free storage and prevent redundant analysis.
--Added unit tests (test_cleanup_insights.py) using mock database connections to verify the deletion logic and row count behavior without touching real data.
--Integrated the cleanup option into the main menu, allowing users to manually trigger data cleanup through the CLI interface with confirmation prompts.
This feature enhances the system’s maintainability and data consistency by ensuring that obsolete projects and their artifacts can be removed cleanly.

---

### **Sami**
This week I focused on backend refactoring to reduce repetitive code and improve maintainability across the project.
- **PR #100 & #101 – Refactoring:**  
  - Consolidated repeated database connection logic into a shared module (`db_config.py`), now used across multiple files.  
  - Created a new `common/constants.py` file to centralize frequently used constants and configuration values.  
  - Updated imports and removed redundant code throughout the backend to ensure consistency.  
  - Verified that all refactored modules work seamlessly with existing features and tests.
**Requirements addressed:**  
- Issue #101 – Codebase Refactoring and Optimization  
**Impact:**  
Improved code organization, reduced duplication, and increased backend maintainability.  
These refactors set the foundation for future scalability and easier feature development.

---

### **Evan**
- I wrote the code for pull requests 106 and 103 which closed issues 93, 94, and 105
- Both pull request included multiple tests or updating of tests to cover the new content
- I reviewed others code for pull requests 104, 100, 102
**Requirements addressed:** 
Issues: #93, #94, #105
**Impact**
Added features for identifying collaborative projects from individual projects and collecting the users name so that we can identify which contributor they are. I also added the ability to change preferences which adds flexibility.
---

### **JinXi**
Fixed a bug in my code from last week that prevented the system from uploading files and saving files to the database. Check others' PR to make sure no problems in them. PR:
[Fixed a spelling error and optimized the closing of sursor and conn. #97](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/97)

This bug cause prevented the system from uploading files and saving files to the database. 
The issue was resolved by accidentally deleting the original code that saved files while modifying the upload_file.py file and then adding it back.
This means that future code modifications will require running the main program for testing.

Moreover reviewed PR #95, #96, #98, #100, #101, #102

---

### **Ryan**
This week I completed two tasks focused on improving system reliability and analytical output.
- **PR #99 – Resolve Testing Problems:** Reviewed and fixed failing or redundant tests, removed invalid characters (including emojis) that caused encoding issues, and ensured all tests are meaningful, consistent, and aligned with recent refactoring.  
- **PR #98 – Ranking Projects:** Implemented a ranking feature using Eric’s Key Metrics data to calculate project scores and display them through the CLI. This lays the groundwork for future LLM-based ranking and project summary integration.
**Requirements addressed:**  
- Issue #99 – Resolve Testing Problems  
- Issue #98 – Implement Project Ranking Feature
**Impact:**  
Improved test stability across modules and introduced a foundational ranking system that enables users to compare projects quantitatively while preparing for advanced LLM-based evaluation in upcoming sprints.
---

## **Current Status**
The project backend has reached a **stable and maintainable stage**, with most core modules now refactored and modularized.  
Major technical debt from earlier sprints was addressed through centralized configuration and reusable components, improving both readability and consistency across the system.

- **Refactoring complete:** repetitive database and constant definitions consolidated into shared modules (`db_config.py`, `common/constants.py`).  
- **Local and external analysis fully integrated:** the system now supports both **online (enhanced)** and **offline (local-only)** workflows through the new `ProjectAnalyzer`.  
- **Collaborative analytics expanded:** additional contribution metrics (lines, files, summaries) provide a richer understanding of multi-user projects.  
- **Database maintenance tools added:** developers can now remove obsolete insights safely using `cleanup_insights.py`, ensuring data consistency during re-analysis.  
- **Menu and permission management refined:** users can manage analysis settings and external-service permissions directly from the CLI.  
- **Testing coverage improved:** multiple new test suites introduced across refactored and new modules, maintaining > 90 % coverage in critical paths.

Overall, the system is now **functionally complete for core analysis and collaboration**, structurally optimized for scalability, and ready for upcoming **ranking, reporting, and visualization** features planned for the next sprint.

---

## **Testing**
This sprint achieved a major improvement in test coverage and reliability across newly refactored and analysis-related modules.  
All new PRs included corresponding unit tests, ensuring that core features remain stable after extensive refactoring and feature expansion.
- **Overall coverage:** > **90%** on core backend modules  
- **PR #102 (Local/External Analysis):**  
  - Added **21 unit tests** validating analysis routing, permission handling, and local analysis logic.  
  - Confirmed that offline fallback works correctly when users decline external service usage.  
- **PR #104 (Cleanup Insights Tool):**  
  - Added **`test_cleanup_insights.py`** to validate safe deletion of project metrics and file content data.  
  - Confirmed rollback behavior and data consistency across tables after cleanup.  
- **Refactoring PRs (#100, #101):**  
  - Verified that centralized modules (`db_config.py`, `constants.py`) do not break existing imports or dependencies.  
  - All previous test suites passed after refactor with zero regressions.  
- **Collaboration Metrics (PR #92, #103):**  
  - Tested new contribution metric functions (lines contributed, files touched, summary generation).  
  - Verified compatibility with existing database schemas and analytics pipeline.  
All current tests are **passing successfully**, and no new bugs or regressions were reported during this sprint.  
Focus will shift next sprint toward expanding integration tests and automated validation for ranking and reporting modules.

---

### **Collaboration Highlights**
- The team collaborated closely across multiple interconnected PRs, ensuring smooth merges between **refactoring**, **analysis**, and **collaborative metrics** features.  
- Frequent Discord discussions and GitHub PR reviews helped coordinate large-scale refactoring (#100, #101) without breaking dependencies.  
- Cross-review between members improved quality control—especially for database changes, constants migration, and new analysis workflows.  
- Joint debugging sessions were held to verify database consistency after refactoring and to confirm new tests for cleanup and local analysis passed.  
- Documentation for shared modules (like `db_config.py` and `constants.py`) was reviewed collectively to ensure all team members understood the updated architecture.  

### **Things to Work On / Reflection**
- **Refactoring awareness:** As more code becomes centralized, team members should review the new shared utilities (`common/constants.py`, `db_config.py`) before adding similar logic elsewhere.  
- **PR coordination:** Some PRs depended on others (e.g., #100 before #101). Better scheduling or labeling (e.g., *“merge after”* notes) will help maintain clarity in future sprints.  
- **Testing standardization:** Although coverage is strong, writing test cases with consistent naming and structure will make future maintenance easier.  
- **Documentation depth:** Continue improving inline docstrings and README notes for new tools like `cleanup_insights.py` to help onboard new contributors. 
- The refactoring broke a lot of code especially the database stuff. 
- Overall, collaboration this sprint was highly effective—communication was proactive, and merge conflicts were resolved quickly.

### **Peer Evaluations**
| Reviewer | Reviewee | Focus Area |
|-----------|-----------|-------------|
| **Kevin** | **Eric** | Verified collaborative metrics integration and cleanup tool testing |
| **Kevin** | **Sami** | Reviewed refactoring PR dependencies and main workflow updates |
| **Evan** | **Ryan** | Reviewed project ranking PR |
| **Evan** | **Eric** | Reviewed outside analysis consent PR |
| **Sami** | **Kevin** | Analysis with Local Feedback PR |
| **Sami** | **Evan** | Reviewed collaboration more metrics PR |
| **Sami** | **Eric** | Reviewed Clean Up Old Insights by Project PR |
| **Sami** | **Jinxi** | Reviewed Optimizing, and Fixing spelling errors  PR |
| **Sami** | **Ryan** | Reviewed test fix PR |
|Please Modify in this row| And delete this after everyone finished their weekly log| |

---

## **Next Steps**

### **Immediate**
- Ryan will contiune working on Ranking projects, since this has some merge conflict.
- Kevin will keep working on the Feature: Retrieve resume and Retrieve Portfolio Information. 
- Sami will work on organizing, and planning our next steps for November's milestone. This includes verifying feature completion, refactoring, and bug fixes. 
- Eric plan to extend the existing analysis module to include project duration, active days, and activity frequency percentages. 
- Evan will give a percentage or skills available from a collaborative project. 
- JinXi will xxxxx

### **Future Work (long term)**
- **Ranking & Portfolio Features:**  
  - Implement project ranking based on combined metrics (activity, skill diversity, collaboration level, and recency).  
  - Develop visual or textual summaries highlighting top projects and individual strengths.  
- **Reporting & Visualization:**  
  - Generate human-readable or exportable reports (PDF/HTML) summarizing project metrics, skills, and contributions.  
  - Integrate CLI output with a dashboard or future web interface for richer analytics.  
- **Enhanced Collaboration Insights:**  
  - Use stored GitHub usernames to pull additional metadata (commits, authorship) for deeper contribution analysis.  
  - Provide percentage breakdowns and role identification per collaborator.  
- **Automated Maintenance:**  
  - Schedule background cleanup or data-validation routines to prevent database bloat over time.  
  - Add monitoring for duplicated or orphaned records after repeated uploads.  
- **Scalability & Deployment:**  
  - Containerize the finalized backend and test deployment stability with Docker Compose.  
  - Prepare for CI/CD integration and automated test runs before merges.  
- **User Experience Enhancements:**  
  - Refine CLI interface with clearer feedback, color coding, and progress indicators.  
  - Add help commands and inline documentation for new menu options.
---

## **Burnup Chart**
<img width="1069" height="608" alt="image" src="https://github.com/user-attachments/assets/fb2f97cb-3291-4c63-9321-818d42328a84" />
<img width="1086" height="671" alt="image" src="https://github.com/user-attachments/assets/68843e6b-89bd-4afa-b06b-c6746cd53580" />

# Sprint Report – Week 10 (2025/11/03 to 2025/11/09)

## **Overview**
This sprint focused on strengthening the system’s functionality by integrating new modules, improving test coverage, and refining collaborative and resume-related features.  
The team merged several PRs addressing both feature enhancements and code reliability, ensuring the backend remains stable as new capabilities are introduced.

---

## **Completed Work**
This week the team focused on integrating new features, enhancing existing modules, and improving testing consistency.  
A total of eight pull requests were completed and merged into the main branch:

- **#123 – CLI Integration w/ Minor Code Refactoring**  

- **#122 – Resume Generation and Formatting**  

- **#121 – Fixing test_upload_file.py**  

- **#120 – Resume Manager Module and Initialization File**  

- **#117 – Update test_file_contents.py**  

- **#116 – Enhance Collaborative Identification**  

- **#115 – Listing Projects Update**  

### **Kevin**
This week I worked on the implementation of the resume generation and management system, completing two pull requests that together deliver the foundation for the **Retrieve Resume (Feature #26)** functionality.

#### **Key Work Completed**
- **PR #122 – Resume Generation and Formatting**  
  Implemented the second sub-issue of Feature #26 by adding resume formatting capabilities.  
  The system now supports multiple output formats for generated resumes, including **JSON**, **Markdown**, and **plain text**.  
  This ensures flexibility for both programmatic access and user-friendly viewing.

- **PR #120 – Resume Manager Module and Initialization File**  
  Developed the **Resume Manager** module, which handles the creation, storage, and retrieval of résumé data generated from analyzed project artifacts.  
  Defined the `ResumeManager` class responsible for managing all resume-related processes and integrating them into the existing analysis pipeline.

**Requirements addressed:**  
- Feature #26 – Retrieve Resume  
- Sub-Issues #120 and #122  

**Requirements addressed:**
PR #120 – Resume Manager Module and Initialization File and 
PR #122 – Resume Generation and Formatting

---

### **Sami**
This week I completed **PR #123 – CLI Integration with Minor Code Refactoring** and **PR #123 - Fixing test_upload_file.py**.
This was primarily a refactoring task, involving a large number of line changes due to project reorganization.

#### **Key Work Completed**
- **Refactored `main.py`** to simplify its role as the project entry point, delegating core logic to modularized components.  
- Created a new **`src/cli/`** directory containing:  
  - `display.py` – Handles success and error messages.  
  - `menus.py` – Manages menu navigation and user selections.  
  - `main_menu.py` – Contains the main CLI loop.  
- Added a new **`src/app.py`** file for centralized app initialization (database setup, managers, and permission handling).  
- Removed redundant functions and cleaned up outdated imports in `main.py`.  
- Fixed minor bugs, including handling `None` values in `get_user_git_username()` and an indentation issue in `ask_user_preferences`.  
- Updated tests to reflect new module structure and import paths.
  
**Requirements addressed:**
PR #123 – CLI Integration & Refactoring (Structural Improvement) and 
PR #121 - Fixing test_upload_file.py

---

### **Eric**
This week, I focused on implementing Feature #10 — Extract Key Contribution Metrics, which is an important step toward providing meaningful project analytics for our backend system.

The main goal of this feature is to analyze and summarize contribution activities within a project by:

Extracting key metrics such as project duration, activity frequency, and type distribution (e.g., code vs test vs design vs documentation).
Displaying the relative proportion of each contribution type to help visualize how team members engage across different aspects of development.
Laying the groundwork for generating analytical insights in the frontend dashboard.
To achieve this, I worked on:

Implementing functions to parse contribution logs and categorize actions by activity type.
Calculating time-based statistics (e.g., number of commits per week, total duration of active contributions).
Integrating the data with our database schema so future visualization modules can query the metrics easily.
I also tested the implementation with several sample datasets to ensure that both data accuracy and consistency across users were preserved.
Through team meetings and reviews, we refined the metric definitions to ensure alignment with our analytics design from previous milestones.



---

### **Evan**
- I wrote code for finding users name in file titles with in projects for a way of finding collaborators as well as finding the authors of git hub commits
- I reviewed pull requests for sami, ryan, kevin and eric
- I wrote a workflow for ensuring all the tests pass on pr to the main branch.

### My Plan for next week
- I plan to implement the collaborative extrapolation

### Reflection
It went pretty well this week for future could I would like to do a better job in avoiding the time complexity complications I ran into when finding the names.

**Requirements addressed:**
Identify users by their name in title
---

### **JinXi**
- Set up issues for the account system development
- Develop the basic account information data table and this data table's CRUD functions.
#### **Key Work Completed**
-**PR 133: Basic user information table and CRUDs**:
      
      - Write coodes for creat table **user_informations**, this table store all use account informations: user_name, password, creat_time, last_loggin, is_login.
      
      - Write **CRUD** functions for *Query User*，*Update password and user name*, and *Delete user*
      
      - This PR would be the base of all following account system development.
      
#### **PR reviewed**:

- PR 122, PR 123, PR 129, PR 131.

#### next week plane:

- implement the basic login and logout function.

- Consider to correlate current data table with user_informations data table.

#### reflection:
Went well this week, and more caution is needed in the upcoming development.

---

### **Ryan**

I refacotred the ranking system to account for better summaries, and connected mine and samis summarizer to the ranking system. THere is now 2 things that the ranking system cna do. 1 is rank the projects (all of them by just showing proj name and score) and 2 is summarize the top 3 projects useing the summarizer fucntion
The continuation of working on the ranking system is going very well. I still have some more things to add on to this, but i did not have time this week. This will be compelted during reading break
Along with this I fixed the upload files testing. THis is because it was adding in "many files" in to our DB instead of just mocking the upload. This happened every single time the tests were run which began to clog our DB.

I refactored, and bug fixed A LOT this week. this was done by myself and with the help of Sami and Evan

**Requirements addressed:**
closed issue #106: https://github.com/COSC-499-W2025/capstone-project-team-9/issues/130
This is my pr link: https://github.com/COSC-499-W2025/capstone-project-team-9/pull/131

---

## **Current Status**
Compared to last week, where the focus was on **backend stabilization, refactoring, and test reliability**, this sprint marked a shift toward **user-oriented functionality and structural refinement**.  
The system now includes a more modular CLI, a working résumé generation pipeline, and enhanced collaborative analysis tools.

- **Project structure finalized:** The new `src/cli/` module cleanly separates interface logic from backend operations, making the codebase easier to extend and maintain.  
- **Resume features implemented:** The newly introduced **Resume Manager** and formatting capabilities allow users to generate résumé data directly from analyzed project metrics in multiple formats (JSON, Markdown, text).  
- **Collaboration detection improved:** Updates to the collaborative identification system enhance contributor tracking within multi-user projects.  
- **Testing reliability restored:** Test suites for upload and file-content modules were repaired and aligned with recent refactoring changes, ensuring stable builds.  
- **CLI and project listing refined:** User navigation and data display in the CLI have been simplified and standardized.  

---

## **Testing**

This week, I added and updated tests related to the newly implemented résumé features to ensure correctness and integration with the main workflow.

- **`tests/test_resume_formatter.py`** – Verified that résumé data is properly formatted and exported across all supported formats (JSON, Markdown, and plain text).  
- **`tests/test_resume_manager.py`** – Tested the creation, retrieval, and storage of résumé data handled by the `ResumeManager` class.  
- **`tests/test_main_integration.py`** – Confirmed that the résumé generation process integrates correctly with the CLI and overall application flow.  
- **`tests/test_upload_file.py`** – Updated existing tests to maintain compatibility with the refactored upload logic and ensure smooth data handling.

All tests passed successfully, confirming that the résumé modules integrate cleanly with existing components and maintain overall system stability.

---

### **Collaboration Highlights**
- The team collaborated effectively to manage several interconnected PRs that introduced significant structural changes, including the new CLI module and résumé management system.  
- Frequent GitHub reviews and Discord discussions ensured smooth coordination while reorganizing the project structure and updating test paths.  
- Members worked closely to verify that résumé-related modules and the new CLI framework integrated properly with existing database and analysis components.  
- Collaborative debugging sessions were held to address test failures resulting from refactoring and to ensure the application ran correctly after module separation.  
- Team communication remained consistent and supportive throughout the sprint, helping maintain stability during large-scale project restructuring.

### **Things to Work On / Reflection**
- **Cross-module testing:** Continue validating dependencies between CLI, résumé, and analysis modules to prevent regression errors after future changes.  
- **Refactor awareness:** As the project now uses a more modular directory structure (`src/cli`, `src/app.py`, `src/analysis`, etc.), team members should double-check imports and paths before merging.  
- **Documentation consistency:** Update module-level docstrings and README sections to reflect the new structure, ensuring clear developer onboarding.  
- **Merge coordination:** Maintain clear PR sequencing (e.g., “merge after” notes) for dependent changes to avoid version conflicts.  
- Overall, collaboration this sprint was **productive and well-coordinated**, especially given the complexity of structural updates and integration work.

### **Peer Evaluations**
| Reviewer | Reviewee | Focus Area |
|-----------|-----------|-------------|
|     Kevin      |     Sami      |     Reviewed PR #123 – verified CLI refactoring structure and test updates      |
|    Kevin       |    Evan       |   Reviewed PR #116 – checked collaborator detection accuracy and performance impact          |
|     Sami      |      Evan      |    Reviewed PR #116 – checked collaborator detection accuracy and performance impact         |
|       Sami    |     Kevin      |  Reviewed PR #120 - Resume Manager module and initialization file                            |
|       Evan   |     sami        |  Reviewed PR #115 - updating listed projects                            |
|       Evan    |     Kevin      |  Reviewed PR #120 - Resume Manager module and initialization file                            |
|       Eric        |       Jinxi        |   Reviewed PR #133 - Basic user information table and CRUDs         |
|       Eric        |       Sami        |   Reviewed PR #123 – verified CLI refactoring structure and test updates         |
|    Jinxi     |   Eric   |   Reviewed PR #129 - Feature #10: Extract key contribution metrics in a project, displaying information about the duration of the project and activity type contribution frequency        |
|Jinxi|Rany|Revied PR #131 - Summarize ranked projects|
|Jinxi|Sami|Reviewed PR #123 – verified CLI refactoring structure and test updates|
|Ryan|Kevin|Reviewed PR #120 – Resume Manager module and initialization file|
|Ryan|Eric|Reviewed PR #129 – Extract key contribution metrics in a project, displaying information about the duration of the project and activity type contribution frequency|
|Ryan|Sami|Reviewed PR #123 – CLI Integration w/ minor code refactoring|
|Ryan|Evan|Reviewed PR #116 – Enhance colaborative identification|
|Ryan|Sami|Reviewed PR #115 – Listing projects update|
|Ryan|Sami|Reviewed PR #121 – Fixing test_upload_file.py|
|Ryan|Jinxi|Reviewed PR #122 – Basic user information table and CRUDs|



---

## **Next Steps**
### **Immediate**
- **Integrate résumé and analysis workflows:**  
  Connect the résumé generation feature with project analysis results to automatically include project summaries, metrics, and collaboration data.
- **Finalize ranking feature integration:**  
  Use the metrics and résumé data to refine project ranking outputs and display results through the CLI.
- **Refine CLI usability:**  
  Improve menu organization, add help prompts, and ensure consistent error handling throughout the new CLI structure.
- **Expand unit and integration testing:**  
  Add tests for the newly integrated résumé and ranking modules to ensure data consistency and end-to-end functionality.
- **Documentation updates:**  
  Update README and module-level docstrings to reflect the new project structure under `src/cli/` and `src/app.py`.
- **List Key metrics:**
  Extracting key metrics such as project duration, activity frequency, and type distribution (e.g., code vs test vs design vs documentation).
- **Account system:**
  Develop account system to implement login/logout and user data isolated.


### **Future Work (Long Term)**
- **Automated résumé export:**  
  Allow users to download résumé outputs in PDF or HTML format for easy portfolio sharing.
- **Enhanced collaboration analytics:**  
  Integrate stored GitHub usernames to extract contribution history and quantify collaboration more accurately.
- **Continuous integration setup:**  
  Implement CI/CD pipelines to automate testing and deployment, ensuring consistency across environments.
- **User experience and API expansion:**  
  Prepare for future Milestone 2 by exposing CLI functionality through REST or web-based interfaces for easier interaction.

---

## **Burnup Chart**
<img width="1279" height="651" alt="image" src="https://github.com/user-attachments/assets/b0afcbdf-0ab6-44b3-aa67-a3c747c6addd" />
<img width="1280" height="576" alt="image" src="https://github.com/user-attachments/assets/347c7a4b-6ab4-40b6-beee-972263d568e9" />

# Sprint Report – Week 11 (2025/11/10 to 2025/11/16)
## **Overview**
This week is reading break, for any personal works, please refer to personal logs.

# Sprint Report – Week 12 (2025/11/17 to 2025/11/23)
## **Overview**
After the break, the team resumed development with strong progress across authentication, timeline accuracy, ZIP validation, deeper project ranking, collaborative analysis improvements, and portfolio generation.
The focus this week was on expanding user-facing features, strengthening backend robustness, and integrating deep analysis into higher-level workflows such as project ranking and portfolio construction.

---

## **Completed Work**
- **#138** Basic login, logout, and registration. https://github.com/COSC-499-W2025/capstone-project-team-9/pull/138
- **#139** Fix timeline using internal ZIP timestamps. https://github.com/COSC-499-W2025/capstone-project-team-9/pull/139
- **#140** Improve ZIP upload validation + add test coverage. https://github.com/COSC-499-W2025/capstone-project-team-9/pull/140  
- **#141** Integrate deep analysis into ranking. https://github.com/COSC-499-W2025/capstone-project-team-9/pull/141 
- **#144** Extrapolate collaborative project files. https://github.com/COSC-499-W2025/capstone-project-team-9/pull/144
- **#145** Portfolio logic + skill mapper. https://github.com/COSC-499-W2025/capstone-project-team-9/pull/145
- **#147** Improved collaborative extrapolation (common names, auto-select GitHub username). https://github.com/COSC-499-W2025/capstone-project-team-9/pull/147
- **#151** Enforcing the collaborative permission https://github.com/COSC-499-W2025/capstone-project-team-9/pull/151
---

### **Sami**

This week I focused on expanding the portfolio generation functionality by integrating the new PortfolioManager module into the system. Instead of introducing new analysis logic, I structured the module so it reuses all existing utilities—summarization, ranking, collaboration detection, file statistics, skill extraction, and timeline analysis—to generate complete portfolio reports from uploaded projects.

I also worked with the new SkillMapper module, which transforms low-level technical signals detected during deep code analysis (such as OOP principles, data structures, algorithms, and optimization patterns) into professional, resume-ready skill categories. These are then included in the final portfolio output.

In addition to development work, I reviewed several PRs from Evan and created a full suite of tests to validate the PortfolioManager and SkillMapper integrations.

---

### **Evan**
- I wrote the code for pull requests 151, 144 and 147 which closed issues 150, 124, and 146
- This includes enforcing the collaborative permission and extrapolating the collaborative portion of projects. This means using their name or GitHub username to find out what in the project they worked on, and then only using that in our analysis.

- all 3 pull request included multiple tests or updates of tests to cover the new content
- I reviewed others code for pull requests 149, and 145

---

### **Kevin**
- Implemented **CLI integration for résumé operations** (#143). https://github.com/COSC-499-W2025/capstone-project-team-9/pull/143
- Added `handle_generate_resume()` to support generating and regenerating résumés from project analysis results.
- Implemented `handle_view_resume()` allowing users to view résumés in multiple formats (JSON, Markdown, and plain text).
- Added `handle_delete_resume()` with confirmation prompts to safely remove stored résumé data.
- Updated the main menu to include new résumé options (Items 12–14).
---

### **JinXi**

Problem fixing: [issue#132: develop basic login and logout feature](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/138)
- A Linux-compatible version has been added to the feature that displays the user's password input as '*', making the feature cross-platform.
- Remove all emojis / unusual characters from the code to make sure the account system still works on different platform.
- Change the all imports of AuthManager and user_account_menu into absolute imports, this is for CI compatibility。
  
PR developed: [issue#142 make sure the system can be used only when the user already login](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/149)
- Add a new login_menu functions to show the login menu.
- Modify the main_menu.py and main.py to make sure use can only go to the main menu when they already login.
- Add new test in test_user_menu.py to test the new codes.

Reviewed PR#139, PR#140, PR#141, PR#143

---

### **Eric**
Fix #1 — Use ZIP Internal Timestamps for Accurate Project Timeline
Previously, the project start and end dates incorrectly used the upload time of the ZIP file.
This caused misleading analytics, especially for older projects or repositories worked on over multiple months.

This week, I implemented a full timestamp extraction pipeline:

Extracted source timestamps from ZipInfo.date_time for each file.
Stored two new fields in file_contents:
source_created_at
source_modified_at
Updated the key_metrics timeline logic to compute:
Project Start Date = MIN(source_created_at)
Project End Date = MAX(source_modified_at)
Added a safety fallback: if no internal timestamps exist (rare), it defaults to the timestamps in uploaded_files.
This fix ensures that our time-based analytics now reflect true project history, not the moment the ZIP was uploaded.

Fix #2 — Robust Validation for “Fake ZIP” Files
I also improved the upload logic to correctly detect renamed or corrupted ZIP archives.

Key improvements include:
Added detection for fake ZIPs (e.g., .rar or .7z renamed to .zip)
Added a clear and user-friendly INVALID_ZIP error message
Added a secondary defensive validation using zipfile.is_zipfile() after the file is copied to the uploads directory
Updated existing tests and added two new unit tests:
Validator-triggered invalid ZIP case
Post-copy invalid ZIP guard case
This prevents issues where renamed RAR files would incorrectly appear valid, and overall improves reliability and UX during file uploads.

---

### **Ryan**
This week I continued to work on the ranking rojects logic, I had to adjust all the scoring and implemetn all the logic to account for the deep analysis logic that Sami implemented.
Along ith this i changed how the score is created. I have normalized the number so that it is between 0-100 rather than just a number that the user will not be able to understand
Link to PR
This is the link to the PR that i have made: #141
I reviewed a lot of pull requests as there was a little bit of a backlog which is something that our team needs to work on. 
The team communication was low on everyones end as it was a busy week. The only real deep communication we had was on monday in class and out meetups. Other than that not much communication occured

---

## **Current Status**
- Authentication system implemented but not yet integrated into analysis workflows.  
- Timeline metrics now use accurate ZIP metadata.  
- Upload validation is more robust and fully tested.  
- Ranking now includes deep code analysis with normalized scoring.  
- Portfolio generation system is functional and prepares for resume/portfolio features.  
- Collaborative project handling is more accurate and automated.
---

## **Testing**
This week we expanded and updated tests to support new functionality and prevent regressions:

- Added invalid ZIP tests for renamed RAR/7z files.  
- Added guard tests for post-copy ZIP validation.  
- Updated tests impacted by ZIP timestamp changes.  
- Ensured ranking and portfolio-related modules load correctly after structural updates.
- Added tests for Enforcing collaborative permission
- Added tests to make sure methods supporting the collaborative extrapolation  

Testing focused primarily on ZIP validation, timeline consistency, and ensuring new modules import and initialize without breaking existing logic.

---

### **Collaboration Highlights**
- Team members coordinated closely as several PRs overlapped with shared components such as file parsing, metrics, and ranking logic.  
- Active GitHub review cycles helped ensure complex changes (e.g., timelines, ranking normalization, portfolio orchestration) merged without breaking dependencies.  
- Members communicated regularly to avoid merge conflicts after structural changes in CLI, authentication, and portfolio modules.  
- Testing updates were shared across the team to ensure consistency between ZIP upload logic, analysis workflow, and timeline metrics.
- We had an efficient meeting to help assign the work and highlight priorities for the week.

---

### **Things to Work On / Reflection**
This week marked a strong return from Reading Break, with major progress across multiple parts of the system.  
The team successfully delivered several foundational features—authentication, improved ranking, portfolio logic—while also improving data accuracy and upload reliability.  
Coordination was smooth even with large PRs affecting shared components.  
Looking forward, the team should continue focusing on test coverage and performance, especially for collaborator detection and deep analysis.
We also want to start working on reinforcing our tests to get our coverage to 100% as currently we are not that close to that we often only have tests for expected cases or common cases and not the edge cases.

---

### **Peer Evaluations**
| Reviewer | Reviewee | Focus Area |
|-----------|-----------|-------------|
|   Kevin        |      Jinxi     |     develop basic login and logout feature #138        |
|    Eric     |      Jinxi    |      issue132: develop basic login and logout feature       |
|    Eric     |     Ryan      |      Ranked projects deep analysis   |
|    Eric     |     Evan      |      extrapolating for only colab projects |
|    Eric     |     Kevin     |       Add CLI integration for resume generation, viewing.  |
|     Ryan      |     Eric      |      Fix Timeline Metrics: Use Zip Internal Timestamps Instead of Upload Time #139       |
|     Ryan      |      Jinxi     |      issue132: develop basic login and logout feature       |
|      Sami     |       Evan    |       Extrapolate Collab Continued      |
|      Sami     |       Evan    |       extrapolating for only collab projects     |
|     Evan     |     Sami      |      Portfolio logic #145      |
|     Evan      |      Jinxi     |      issue#142 make sure the system can be used only when the user already login #149      |
|     Jinxi      |      Eric    |      Fix Timeline Metrics: Use Zip Internal Timestamps Instead of Upload Time #139      |
|     Jinxi      |      Eric    |      Improve ZIP upload validation & add test coverage for invalid ZIP cases #140      |
|     Jinxi      |      Ryan    |      Ranked projects deep analysis #141     |
|     Jinxi      |      Kevin    |      Add CLI integration for resume generation, viewing. #143     |
---

## **Next Steps**

### **Immediate**
- Everyong will doing refactoring, polishing
- Improve performance of collaborator detection.
- Enhance CLI menu flow for authenticated users.
- Increase test coverage on ranking and deep analysis edge cases.

---

## **Burnup Chart**
<img width="1006" height="493" alt="image" src="https://github.com/user-attachments/assets/250eeb33-1ca4-47bf-aaf7-4e56a463cb30" />
<img width="989" height="486" alt="image" src="https://github.com/user-attachments/assets/00b28d8b-3fc0-4793-ac13-0f5d064b2551" />

# Sprint Report – Week 13 (2025/11/24 to 2025/11/30)

## **Overview**
This sprint focused on **codebase refinement**, **system integration**, and **test coverage expansion**. The team executed a significant refactor of the database connections and resume generation features to improve maintainability. We also merged the metrics and summary modules into a unified "Full Analysis Mode" and updated the CLI menu labels for better user experience.

A major push was made on quality assurance: we achieved **100% test coverage** on several core analysis modules (`test_activity_classifier.py`, `test_analysis_init.py`) and implemented comprehensive test suites for the Portfolio and Resume managers. Additionally, the system documentation was updated, and the "Chronological Skills" feature was finalized.

## **Completed Work**
- Tests for portfolio https://github.com/COSC-499-W2025/capstone-project-team-9/pull/152
- Refactor: merge metrics and summary into full analysis mode; update menu labels https://github.com/COSC-499-W2025/capstone-project-team-9/pull/154
- Syntax fixes, documentation updates, and chronological skills https://github.com/COSC-499-W2025/capstone-project-team-9/pull/158
- Database Connection Refactor https://github.com/COSC-499-W2025/capstone-project-team-9/pull/160
- Refactoring resume feature https://github.com/COSC-499-W2025/capstone-project-team-9/pull/162
- Write tests for resume creation https://github.com/COSC-499-W2025/capstone-project-team-9/pull/164
- Refactor main menu to use list-based rendering and dispatch map https://github.com/COSC-499-W2025/capstone-project-team-9/pull/159
- Adding Tests for main menu and the app.py https://github.com/COSC-499-W2025/capstone-project-team-9/pull/165
- Fixed Testing for ranking storage and improved coverage https://github.com/COSC-499-W2025/capstone-project-team-9/pull/166
- Testing Portfolio system and file contents https://github.com/COSC-499-W2025/capstone-project-team-9/pull/169
- Testing project display and menus https://github.com/COSC-499-W2025/capstone-project-team-9/pull/168

### **Kevin**
This week, I focused on polishing the résumé generation module to ensure the codebase is clean, maintainable, and ready for final submission.
- **PR #162 – Refactoring Resume Feature:**
  - Refactored the `ResumeManager` and related formatting utilities to reduce code duplication and improve readability.
  - Optimized the logic for retrieving and structuring project data for resumes.
  - Verified that all resume-related tests pass after the structural changes, ensuring no regressions in functionality.

**Requirements addressed:**
- Issue #162 – Refactoring resume feature

---

### **Sami**
This week I spent a lot of time working on refactoring code and adding tests to ensure our project had a sufficient amount of coverage.
This was so that we know our project works inside and out and we are confident in our product going into the second milestone
which involves using API calls etc. 

Additionally, I reviewed a bunch of PR's listed below and did a final test of our project before our demo coming up.
Something that went we'll this week was our communication. In a way it stepped up more than it has in previous weeks and we were
able to get a lot of issues revolving our project solved relatively quickly. 
Yet, an issue we faced was PR's being left waiting for a review. I wasn't able to push as many tests as I hoped because we would have to wait for
one PR to get pushed, so that I can push another test and create a seperate PR for it without creating 15 different branches. We ended up being fine, yet this is 
still something we need to work on. 

---

### **Eric**
This week focused on two major backend improvements:  
(1) refactoring the CLI menu system for cleaner structure and better maintainability, and  
(2) merging the **key_metrics** and **project_summary** features into a unified analytics workflow.

These changes streamline our user experience and simplify the internal logic of our analysis pipeline.

---

#### **Refactor: CLI Menu Structure**

The existing CLI menu had become increasingly large as more features were added (cleanup, ranking, collaborative features, user prefs, login, etc.).  
This week I refactored the menu system to make it more modular and maintainable:

- Split menu logic into **dedicated handlers** for user account, analysis, and preferences  
- Removed duplicated `input()` logic and unified all input validation  
- Cleaned up inconsistent numbering caused by the login/register option  
- Ensured the menu properly updates based on logged-in state (e.g., showing the username)  
- Improved readability of the main menu loop and reduced deeply nested logic

This refactor helps future contributors add new menu options without creating conflicts or inconsistent UX.

---

#### **Feature Merge: key_metrics + project_summary**

Previously, **key_metrics** and **project_summary** were implemented as separate flows.  
This caused:

- duplicated data extraction  
- similar logic running multiple times  
- multiple DB queries for the same information  
- confusing CLI options

This week, I merged both into a single unified analysis pipeline.

Key improvements:

- **One shared backend function** now generates both metrics and summary  
- Removed duplicated code paths and consolidated all parsing logic  
- Ensured contribution data, activity breakdown, project duration, and summary statistics all come from the **same computed dataset**  
- Updated CLI routes to provide one clear “Analyze Project” flow instead of two  
- Improved performance by reducing repeated scans over file_contents  
- Cleaned up test cases to align with the merged design

This merge sets the foundation for the future analytics dashboard and simplifies how future features (visualization, ranking, insights) will plug into the system.

**Requirements addressed:**
- ...

---

### **Evan**
- I wrote the code for pull requests 169 and 168 which were both testing PR's
- I reviewed Ryan's PR's which were 166 and 165
- I also wrote the team contract and made the team presentation with Ryan

**Requirements addressed:**
- Increased testing coverage

---

### **JinXi**
This week I focus on refactoring of account system, add test to increas the test coverage on account system and review codes.

Refactoring: [Refactoring of user menus](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/161)
- use constant to store login and account management menu's options. Not direct use print to show options.
- user selections are now catch by the handlers instead of if-else
- This change would making it easier to add new features in the future

Test add: [Add more test for user_menus.py to extend the test coverage of this file.](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/167)
- Improve test coverage of user_menus.py form 69% to 82%
- Add more test for EOF Handling
- Add more test for edge cases
- Add more test for cross plateform
  
---

### **Ryan**
What I completed this week
-This week i completed a multitude of tasks.
-Evan and I created the presentation slide deck
-Evan and I did the team contract outline and added all information. We then got all team members to go over it and see if they agree, if they want to add anythign change anthing or remove something.
-I then created a lot of tests to increase the coverage of our project. I built tests for 3 files. the first file is main_menu which had a coveerage of 0 and now is 75% covered, Then i did the same for app.py which had 0 coveregae and now has 100. Then i added more tests for the ranking storage which had very simple tests which only covered around 25% of all code. It now covers 99% of code.
Along with this The studying and preperation for the Quiz #2 went well.
Link to PR
This is the link to the PR that i have made: #165
This is the link to the PR that i have made: #166
What went well
The preperation for our presentation went well for me. The slide deck that we created is a good length and i beleive that it covers all of the topcs we need to talk about
The creation of the team contract went really well and i believe that we covered all things our group was worried about
building tests for the files i did went really well as the covereage increased a lot.
The communication has improved a lot since last week
what didnt go well
There is no major thing that didnt go well this week, this was the first week in a while where i felt as though all memebers were on the same page.
We still need to improve on merging PRs quicker

---

## **Current Status**
- **Feature Complete:** Core modules (Auth, Analysis, Ranking, Portfolio) are integrated.
- **Refactoring:** Major code cleanup conducted to remove redundancy and improve readability.
- **Test Coverage:** Significant push to increase coverage towards 100%, focusing on edge cases.
- **Performance:** Collaborator detection and deep analysis speed improved.

---

## Testing
This sprint, the team made a significant push towards quality assurance, aiming for **100% test coverage** on critical analysis modules.
- **Coverage Milestones:**
  - `test_activity_classifier.py`: Achieved **100% coverage**, ensuring accurate categorization of project files.
  - `test_analysis_init.py`: Achieved **100% coverage**, verifying the stability of the analysis engine's initialization.
- **New & Updated Tests:**
  - **Resume Creation:** Comprehensive tests were written for the `ResumeManager` to validate the new formatting and data retrieval logic.
  - **Portfolio Generation:** Added a full test suite for the portfolio module to ensure skill mapping and project summaries are generated correctly.
  - `test_key_metrics.py`: Updated to align with the merged "Full Analysis Mode" and new metric definitions.
- **Integration Testing:** Verified the end-to-end flow of the new "Full Analysis Mode," ensuring that metrics and summaries are correctly combined without errors in the CLI.

---

### Collaboration Highlights
- **Cross-Module Refactoring:** The **Database Connection Refactor** required close coordination between **Sami** and **Jinxi** to ensure that user authentication states were correctly preserved when passing control to the analysis modules.
- **Unified Analysis Workflow:** **Ryan** worked closely with the team to merge the separate "Metrics" and "Summary" features into a single **"Full Analysis Mode,"** requiring careful conflict resolution in `main.py`.
- **Quality Assurance Reviews:** Peer reviews this week were strictly focused on test completeness. Members did not approve PRs until the targeted modules hit their 100% coverage goals.

### Things to Work On / Reflection
This week marked a shift from "building new features" to "perfecting existing ones." The **Database Connection Refactor** was a challenging but necessary step to remove technical debt before the final submission. While hitting **100% test coverage** on key modules was time-consuming, it has significantly increased our confidence in the system's stability.

Moving forward, we need to ensure that our **documentation** keeps pace with these rapid code changes so that the final user guide accurately reflects the polished CLI structure.

### Peer Evaluations
| Reviewer | Reviewee | Focus Area |
|-----------|-----------|-------------|
| **Kevin** | **Sami** | Added tests for deep_code_analyzer [#155](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/155) |
| **Sami** |  | **Kevin** | Refactoring Resume Feature [162] https://github.com/COSC-499-W2025/capstone-project-team-9/pull/162 |
| **Sami** |  | **Eric** |Refactor main menu to use list-based rendering and dispatch map [159] https://github.com/COSC-499-W2025/capstone-project-team-9/pull/159 |
| **Sami** |  | **Eric** | Fix CLI hang during project ranking by disabling deep analysis and live summaries; update all affected tests [157] https://github.com/COSC-499-W2025/capstone-project-team-9/pull/157 |
| **Sami** |  | **Jinxi** | issue#142 make sure the system can be used only when the user already login [149] https://github.com/COSC-499-W2025/capstone-project-team-9/pull/149 |
| **Eric** | **Jinxi** | issue#142 make sure the system can be used only when the user already login [#149](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/149) |
| **Eric** | **Sami** | Tests for portfolio [#152](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/152) |
| **Eric** | **Sami** | test_activity_classifier.py and test_analysis_init.py 100% coverage hit [#153](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/153) |
| **Eric** | **Sami** | Added tests for deep_code_analyzer [#155](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/155) |
| **Eric** | **Sami** | test_key_metrics.py update [#156](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/156) |
| **Eric** | **Sami** | Database Connection Refactor [#160](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/160) |
| **Evan** |  | ... |
| **JinXi** | **Sami** |test_key_metrics.py update [#156](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/156) |
| **JinXi** | **Eric** |Refactor main menu to use list-based rendering and dispatch map [#159](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/159) |
| **JinXi** | **Sami** |Database Connection Refactor [#160](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/160) |
| **JinXi** | **Kevin** |Refactoring resume feature [#162](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/162) |
| **JinXi** | **Kevin** |Write tests for resume creation [#164](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/164) |
| **JinXi** | **Ryan** |Fixed Testing for ranking storage and improved coverage [#166](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/166) |
| **Ryan** |  | **Jinxi** |Refactoring of user menus #161|
| **Evan** | **Ryan** |Fixed Testing for ranking storage and improved coverage [#166](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/166) |
| **Evan** |  | **Ryan** |Adding Tests for main menu and app.py [#165](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/165) 
| **Ryan** |  | **Kevin** |Refactoring resume feature #162|
---

## **Next Steps**

### **Immediate (Monday Presentation Prep)**
- **Final Rehearsal:** Conduct a full team rehearsal of the presentation and live demo to ensure smooth hand-offs between members.
- **Code Freeze:** Enforce a strict code freeze to ensure stability for the Monday demo.
- **Demo Dry-Run:** Verify the "happy path" for the demo (Login -> Analyze -> Rank -> Resume) works flawlessly on the presentation machine.
- **Final Submission:** Submit the final source code, documentation, and video deliverables before the deadline.

### **Future Work**
- **Post-Presentation Review:** Discuss feedback received from the instructors/TAs during the demo.
- **Final Wrap-up:** cleanup repository and archive the project for the term.
---

## **Burnup Chart**
<img width="988" height="470" alt="image" src="https://github.com/user-attachments/assets/880b4229-c837-4c22-a850-e0b602445c72" />
<img width="975" height="473" alt="image" src="https://github.com/user-attachments/assets/2e9e84a2-b709-4713-bdb7-daaf15f13d89" />

# Sprint Report – Week 14 (2025/12/01 to 2025/12/07)

## **Overview**
This sprint served as the final stabilization phase for the project. With the core development complete and the final presentation delivered (or impending), the team enforced a strict **code freeze** regarding new features. 
The primary focus was **System Testing and Quality Assurance**. We dedicated this week to increasing test coverage, verifying edge cases, and ensuring that all integrated modules (Authentication, Analysis, Ranking, Portfolio) function seamlessly together for the final submission.

## **Completed Work**
- **System-wide Code Freeze** enforced to ensure stability.
- **Test Coverage Expansion:** Focused on bringing remaining modules to high coverage percentages.
- **Regression Testing:** Verified that recent refactors (DB connections, Menu structure) did not break existing functionality.
- **Final Documentation:** Updated README and code docstrings to match the final system state.

### **Kevin**
- Implemented test_service_config.py: Created a comprehensive test suite for the ServiceConfig class to ensure user consent settings are stored and retrieved safely.
- Verified Initialization Logic: Added tests (test_initialize_table_success) to confirm that the external_service_permissions table and its indexes are created correctly on startup.

**Requirements addressed:**
- Quality Assurance & Final Testing
- completed Add tests for service config https://github.com/COSC-499-W2025/capstone-project-team-9/pull/181
---

### **Sami**
- Focused on ensuring the collaborative features and user preference systems are fully robust before final submission.
- Implemented test_collaborative.py: Created a full test suite for CollaborativeManager and CollaborativeDisplay.
- Update test_collaborative.py  https://github.com/COSC-499-W2025/capstone-project-team-9/pull/171

**Requirements addressed:**
- Quality Assurance & Final Testing
- Robustness of Collaborative Consent System

---

### **Eric**
**Weekly Goals Recap**

As Milestone 1 concluded this week, my focus shifted toward improving the **reliability, stability, and overall test coverage** of our backend systems.  
This included strengthening the permission workflow, validating collaborative access control, and ensuring previously untested modules now have full coverage.  
By the end of the week, overall project test coverage increased to **~90%**, marking a major milestone in system robustness.

---

## **1. Added Full Test Suite for External Service Permission Workflow**

Several components under `external_services/` previously lacked coverage, especially those interacting with the database and user permission logic.  
This week I implemented a comprehensive test suite covering:

- `ServiceConfig.initialize_table()` (success + exception paths)
- `ServiceConfig.get_permission()` for:
  - permission=True
  - permission=False
  - no record → None
  - database failures
- `ExternalServicePermission.initialize()` with correct error handling
- `ExternalServicePermission.has_permission()` fallback logic
- Full workflow tests for `request_external_service_permission()`:
  - Skip prompting when existing permission is present
  - Execute full info → prompt → store sequence when no permission exists
  - `force=True` correctly re-prompts regardless of stored value
  - Store permission only once and with correct arguments
  - Validate printed user-facing messages

These tests greatly improve reliability of our privacy and external analysis workflows.

---

## **2. Added Tests for Collaborative Permission Decorator**

The `requires_collaborative` decorator enforces access control based on collaborative settings.  
Before this week, the file had **0% test coverage**.

I added tests to verify:

- Wrapped functions execute correctly when collaborative=True
- Execution is blocked when:
  - preferences are missing (`None`)
  - collaborative flag=False
- Correct error message is printed
- Decorator returns `None` when access is denied
- Arguments are passed correctly to wrapped functions

This brings the collaborative module to **100% coverage**, ensuring reliability for team-based features.

---

## **3. Overall Coverage & Stability Improvements**

With the new test suites added:

- Total project coverage increased from ~87% → **~90%**
- External service modules now reach **96–100% coverage**
- Collaborative decorators now reach **100% coverage**
- Several untested branches across multiple modules are now fully validated

This significantly improves long-term maintainability and helps future contributors trust the behavior of the permission systems.


---

### **Evan**
- I wrote the code for pull requests 180 and 177 which closed issues 179 and 175
- all 3 pull request included multiple tests or updates of tests to cover the new content

**Requirements addressed:**
- Build external analysis method
- Extract text from images for analysis

---

### **JinXi**
Add test to increas the test coverage on account system and review codes.

**Requirements addressed:**
Test add: [Add test for consent and consent display.](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/173)
- Increase test coverage form 32% to 99%
- test for output structure
- test for different user input
- test for EOF and different valid/invalid user input
- test for Exception handling
- test for user interaction

Pr reviewed: #170, #171, #172, #181

---

### **Ryan**
### What I completed this week
- This week we had our Team presentation. Overall the presentation went well and the preperation went well. We have completed the all major features but there are still some things that we need to eb refined in the future.
- By the time it was my turn to speak in the presentation, the time was up. This resulted in me having to spped through my section and leave out many details that I wnted to speak about.
- I added to the testing file of resme formatter and increased the coverage from 50% to 99%
### Link to PR
- This is the link to the PR that i have made: https://github.com/COSC-499-W2025/capstone-project-team-9/pull/172
### What went well
- The presentation went well even though i was rushed on time. We were abl to talk about all of the unique features that we have implemented and were able to talk all about all our deep analysis.
- We recorded our video on saturday evening, and this also went well. We s
### what didnt go well
- There was a lack of communication that occured after the presentation. We did not have much doce to do so this makes sense.
**Requirements addressed:**
- Quality Assurance & Final Testing

---

## **Current Status**
- **Code Freeze:** Active. No new features are being merged.
- **Test Coverage:** significantly improved across all modules (aiming for >90% project-wide).
- **Stability:** The application is stable and ready for final grading.
- **Project State:** Completed for Milestone 2.

---

## **Testing**
This week was exclusively dedicated to testing.
- **Unit Tests:** coverage expanded for `resume_manager`, `auth_manager`, and `ranking_system`.
- **Integration Tests:** Verified the flow: *Login -> Upload -> Analyze -> Rank -> Portfolio*.
- **Manual Testing:** The team conducted a "Happy Path" walk-through to ensure the demo is flawless.
- **Bug Fixes:** (Mention any small bugs found and fixed during testing here, e.g., "Fixed a typo in the portfolio output").

---

### **Collaboration Highlights**
- **Code Freeze Coordination:** The team communicated effectively to ensure no risky changes were pushed to `main` this week.
- **Test Swapping:** Team members tested each other's modules to find edge cases that the original author might have missed.
- **Final Presentation:** The team collaborated on the slide deck and rehearsed the demo flow.

### **Things to Work On / Reflection**
- **Semester Wrap-up:** The project is now effectively concluded. The team worked well to integrate a complex set of features (Auth, NLP, Analysis, Database) into a cohesive CLI tool.
- **Final Check:** Ensure all "TODO" comments are removed or addressed in the code.
- **Documentation:** Ensure the User Manual explains the final menu structure, as it changed recently.

### **Peer Evaluations**
| Reviewer | Reviewee | Focus Area |
|-----------|-----------|-------------|
| **Kevin** | **Jinxi** | Reviewed Auth system tests |
| **Sami** | **Eric** | Reviewed Analysis pipeline tests |
| **Eric** | **Sami** | Update test_collaborative.py #171 |
| **Eric** | **Jinxi** | Add more test for user_menus.py to extend the test coverage of this file. #167 |
| **Evan** | **Sami** | Reviewed Deep Analysis tests |
| **JinXi** | **Kevin** | Reviewed Resume Manager tests |
| **JinXi** | **Eric** | Add full test coverage for external service permissions and collaborative decorator #170 |
| **JinXi** | **Sami** | Update test_collaborative.py #171 |
| **JinXi** | **Ryan** | Added more testing for the resume formatter to ensure that there is 1… #172 |
| **Ryan** | **Evan** | Reviewed Collaboration tests |
| **Ryan** | **Jinxi** | Add test for consent and consent display |

---

## **Next Steps**

### **Immediate**
- **Project Archive:** Clean up the repository and submit final deliverables.
- **Winter Break:** Rest and recover!

### **Future Work**
- **Capstone Part 2 (Next Term):** - Discuss potential transition to a Web/GUI interface.
  - Explore deploying the database to a cloud provider.
  - Implement advanced LLM features for better project summarization.

---

## **Burnup Chart**
