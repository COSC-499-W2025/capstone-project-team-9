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

### **Kevin**

**Requirements addressed:**

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
PR #123 – CLI Integration & Refactoring (Structural Improvement)
PR #121 - Fixing test_upload_file.py

---

### **Eric**

**Requirements addressed:**

---

### **Evan**

**Requirements addressed:**

---

### **JinXi**

**Requirements addressed:**

---

### **Ryan**

**Requirements addressed:**

---

## **Current Status**


---

## **Testing**
---

### **Collaboration Highlights**


### **Things to Work On / Reflection**


### **Peer Evaluations**
| Reviewer | Reviewee | Focus Area |
|-----------|-----------|-------------|
|           |           |             |
|           |           |             |
|           |           |             |

---

## **Next Steps**

### **Immediate**


### **Future Work (Long Term)**


---

## **Burnup Chart**
