This week, I worked on implementing issue #6: User Consent Management for our Digital Work Artifacts Mining project, with 3 sub-issues completed.
<img width="1054" height="606" alt="image" src="https://github.com/user-attachments/assets/daa2427a-470d-4b2c-87ac-04932d7fe54d" />

# **What I Did This Week (2025/10/13 to 2025/10/19 week 7)**

## **Issue #38: Implemented Conditional Logic for External Service Routing**

### **In Simple Terms**
You built a system that checks whether users want to use external services (like ChatGPT or other LLMs) before sending their data out.  
If they say **no**, the system automatically uses **local analysis** instead.

---

### **What I Created**

- **AnalysisRouter** – The "traffic cop" that decides: *“Should we use external help or stay local?”*  
- **ExternalServicePermission** – Checks if the user has granted permission  
- **ServiceConfig** – Stores the user's choice in the database  
- **Database Table:** `external_service_permissions` – Remembers each user's preferences  
- **8 Unit Tests** – Ensure routing and permissions logic work correctly  

---

### **By The Numbers**

| Metric | Value |
|--------|-------|
| Lines of Code | ~350 (manageable PR size) |
| New Tests | 8 (all passing) |
| New Modules | 2 (`analysis/`, `external_services/`) |
| New Database Table | 1 (`external_service_permissions`) |

---
<img width="1034" height="537" alt="image" src="https://github.com/user-attachments/assets/14f847c8-9142-4f4b-81e1-aab31f467116" />

# **What I Did This Week (2025/10/20 to 2025/10/26 – Week 8)**

## **Issue #39 Set up internal analysis method 

---

#### What I Built
I created the `LocalAnalyzer` class in `src/analysis/local_analyzer.py` - a complete analysis engine that works entirely offline. This class provides seven major analysis capabilities:

**1. Language Detection**
- Detects 30+ programming languages with pattern matching
- Includes: Python, JavaScript, TypeScript, Java, C++, C, C#, PHP, Ruby, Go, Rust, Swift, Kotlin, Scala, R, MATLAB, SQL, HTML, CSS, SCSS, SASS, JSON, XML, YAML, Shell scripts, PowerShell, Bash, and more
- Returns language distribution, percentages, and primary language
- Stores file paths for each detected language

**2. Framework Detection**
- Identifies popular frameworks and technologies through file content analysis and naming patterns
- Covers: React, Vue, Angular, Django, Flask, Express, Spring, Node.js, Docker, PostgreSQL, MongoDB
- Uses regex pattern matching on source files (Python, JavaScript, Java, etc.)
- Returns sorted list of detected frameworks

---

### **Next Steps**
- Feature: Retrieve Portfolio Information #24

<img width="1054" height="600" alt="image" src="https://github.com/user-attachments/assets/4e89a800-cd0e-4914-9d8f-8af3617f5980" />

# What I did this week – Week 9 (2025/10/27 to 2025/11/02)

## Overview
This week I focused on implementing a new analysis workflow that functions completely offline and respects user privacy preferences.  
I completed PR #102, which allows the system to perform local analysis when a user declines external service usage.  
In addition to this, I participated in code reviews, testing, and team discussions to ensure the stability of the refactored backend.

## What I Did
- Implemented **ProjectAnalyzer** class to coordinate both local and external analysis workflows.  
- Added permission prompts and privacy handling for users who opt out of external APIs.  
- Integrated the new local analysis workflow into the command-line interface, adding options for “Analyze Project” and “Manage External Services.”  
- Created and updated database tables to store service permissions and analysis results.  
- Wrote and verified **19 unit tests** to ensure analysis routing and fallback behavior worked correctly.  
- Collaborated with teammates on refactoring and testing tasks to maintain consistency across the system.  
- Reviewed teammate code to confirm compatibility with the new local analysis logic.  
- Participated in team meetings and debugging sessions to coordinate progress and fix test issues.

## Reflection
This week’s work significantly improved the system’s flexibility and privacy compliance.  
The local analysis implementation ensures that users can run meaningful project evaluations without internet access or external API dependencies.  
Through collaboration and testing, I helped strengthen the project’s reliability and modular design while reinforcing good testing and documentation practices.
<img width="1044" height="613" alt="image" src="https://github.com/user-attachments/assets/46b7cd37-bcd0-4328-8568-06676c91ea13" />

### **Next Steps**
- Feature: Retrieve Portfolio Information #24 and resume information
- Debugging, refactoring. 

### **Next Steps**###
<img width="1044" height="613" alt="image" src="https://github.com/user-attachments/assets/891222a2-5135-4c26-985e-c41af51b6e9f" />

# What I Did This Week – Week 10 (2025/11/03 to 2025/11/09)

## Overview
This week I focused on expanding the system’s user-facing functionality by implementing the résumé generation and management features.  
These updates complete the foundation for the “Retrieve Resume” feature and integrate analyzed project data into a structured résumé format.  
I also contributed to reviews and testing to ensure compatibility with the new CLI structure introduced by the team.

## What I Did
- **PR #122 – Resume Generation and Formatting:**  
  Implemented formatting capabilities for generated résumé data, supporting multiple output types including JSON, Markdown, and plain text.  
  Ensured the formatter aligns with project analysis outputs and user readability standards.  
- **PR #120 – Resume Manager Module and Initialization File:**  
  Developed the `ResumeManager` class to handle creation, retrieval, and storage of résumé data derived from analyzed project artifacts.  
  Integrated the manager into the project’s initialization flow for smooth linkage with analysis results.  
- Added and updated tests for résumé-related modules to confirm data accuracy and integration with existing workflows.  
- Reviewed PRs for CLI refactoring and collaborative identification to verify proper structure, imports, and performance behavior.  
- Participated in debugging and team coordination meetings to maintain stability after major structural changes.

## Reflection
This week marks a shift from backend setup toward delivering meaningful, user-facing functionality.  
By introducing résumé management and formatting, the project can now generate tangible outputs from analysis data, supporting the broader goal of creating a portfolio-building tool.  
Working alongside teammates on refactoring and integration reinforced the importance of clear architecture and testing after large-scale restructuring.

### **Next Steps**
- Extend résumé generation to include ranking and skill summarization.  
- Integrate résumé data with project summaries for unified reporting.  
- Continue debugging and improving modular documentation for new components.
<img width="1264" height="649" alt="image" src="https://github.com/user-attachments/assets/99d1732f-24ec-4eab-98d6-abc185463379" />

# **What I Did This Week - Week 11**
This week is Reading break, I did not do anything.

# **What I Did This Week – Week 12**

## **Overview**
This week I focused on integrating résumé functionality directly into the CLI and ensuring that users can generate, view, and manage their résumés through a seamless command-line workflow. This work builds on the résumé generation logic implemented in previous weeks and extends it into user-accessible CLI features.

## **What I Did**
- Implemented **CLI integration for résumé operations** (#143). https://github.com/COSC-499-W2025/capstone-project-team-9/pull/143
- Added `handle_generate_resume()` to support generating and regenerating résumés from project analysis results.
- Implemented `handle_view_resume()` allowing users to view résumés in multiple formats (JSON, Markdown, and plain text).
- Added `handle_delete_resume()` with confirmation prompts to safely remove stored résumé data.
- Updated the main menu to include new résumé options (Items 12–14).
- Wrote **11 comprehensive test cases** covering:
  - Résumé generation logic
  - Résumé viewing in different formats
  - Résumé deletion workflow
  - CLI argument handling and error cases

## **Reflection**
This week’s work expanded the résumé subsystem from a backend feature into a fully interactive user workflow. Integrating it into the CLI improved usability and makes it easier for users to manage their résumé outputs without relying on internal modules. The testing coverage ensures that the new functionality is stable and compatible with recent refactoring changes in the CLI architecture.

## **Next Steps**
- Finalize portfolio integration so résumé and portfolio outputs share consistent formatting.
- Expand test coverage for cross-module interactions (Resume Manager + Portfolio Manager).
- Prepare for upcoming Milestone 2 features that will require CLI extensibility.
<img width="1020" height="593" alt="image" src="https://github.com/user-attachments/assets/140d9878-c65e-4aba-917b-e1d9d83d136d" />

# **What I Did This Week (2025/11/24 to 2025/11/30 Week 13)**

- Refactoring resume feature https://github.com/COSC-499-W2025/capstone-project-team-9/pull/162
- Write tests for resume creation  https://github.com/COSC-499-W2025/capstone-project-team-9/pull/164

### **In Simple Terms**
This week was all about **polish and stability**. Instead of building new features, I cleaned up the code for the résumé system to make it easier to read and maintain. I also wrote a lot of automated tests to prove that the résumé generator works perfectly every time.

---

### **What I Created**

- **Refactored `ResumeManager`:** Cleaned up the code that handles résumé data, removing repetitive logic and making it more modular.
- **Optimized Data Retrieval:** Improved how the system pulls project summaries and metrics to generate résumés faster.
- **New Test Suite:** Wrote comprehensive tests for:
  - `test_resume_creation.py` – Verifying that résumés are generated with the correct data.
  - `test_resume_formatter.py` – Ensuring JSON, Markdown, and Text formats look correct.
- **100% Coverage Goal:** Contributed to the team's goal of reaching 100% test coverage on critical modules.

---

## **Reflection**
This week marked the transition from "development" to "delivery." Refactoring the résumé feature was necessary to remove technical debt before our final submission. It was satisfying to see the code become cleaner and to have the confidence (backed by tests) that the feature is robust. This "cleanup" phase is just as important as the building phase to ensure a high-quality final product.

## **Next Steps**
- **Final Demo Prep:** Rehearse the live demo workflow (Login -> Analyze -> Resume).
- **Code Freeze:** Stop making changes to ensure stability for Monday's presentation.
- **Documentation:** Ensure the User Guide accurately reflects the final CLI options for résumés.
<img width="1029" height="609" alt="image" src="https://github.com/user-attachments/assets/0a95d169-6f69-44aa-8c39-59100c3500a3" />

# What I Did This Week (2025/12/01 to 2025/12/07 Week 14)

## Overview
This week was dedicated to **final system stabilization and Quality Assurance (QA)**. With the project in a strict code freeze, my primary focus was increasing test coverage for the configuration and permission modules to ensure the system handles user consent reliably in production environments. I also performed final regression testing on the résumé features.

## What I Did
- **Implemented `test_service_config.py`:** Created a comprehensive test suite for the `ServiceConfig` class to ensure user consent settings are stored and retrieved safely.
  - **Initialization:** Verified that the `external_service_permissions` table and its indexes are created correctly on startup.
  - **Error Handling:** Implemented tests to verify that the system handles database connection failures gracefully (e.g., simulating a "DB is down" scenario).
  - **Permission Logic:** Verified all three permission states: **Granted**, **Denied**, and **None** (not set).
- **Resume & Portfolio QA:** Conducted final manual and automated testing on the `ResumeManager`.
  - Verified that deleting a résumé cleans up the database correctly.
  - Checked that generated Markdown and JSON outputs are formatted correctly for the final demo.
- **Regression Testing:** Verified that recent refactors in the database layer did not break the existing user consent flow.

## Reflection
This final week of testing was crucial. By writing tests for `ServiceConfig`, I ensured that one of the most sensitive parts of our application—user privacy and consent—is robust against failures. It feels good to end the semester with a stable, well-tested codebase rather than scrambling to fix bugs at the last minute. The transition from "building" to "stabilizing" has given me much more confidence in our final submission.

## Next Steps
- Submit final project deliverables and archive the repository.
- Winter Break!

<img width="1045" height="617" alt="image" src="https://github.com/user-attachments/assets/1a43c257-5f37-421a-8d66-5cce65e90e42" />

# **Term 2 Week 2 (2026/01/12 to 2026/01/18)**

This week marked the start of Milestone 2. My primary focus was architecting the backend display logic for the Resume feature.

## **Issue: [Milestone 2] Implement Project Presentation & Resume Display Logic**

### **In Simple Terms**
I built the "translator" engine for our backend. It takes raw technical data from the project analyzer (like "15 files, 2000 lines of code, has_tests=True") and automatically converts it into professional, human-readable resume bullet points

---

### **What I Created**

* **Data Contracts (`src/common/schemas.py`)**: Defined strictly typed Pydantic models (`ResumeItemResponse`) to ensure the frontend receives consistent JSON data.
* **Resume Logic Engine (`src/resume/item_formatter.py`)**: A dedicated class that separates the "display logic" from the heavy "ranking logic." It includes:
    * **Smart Title Cleaning**: Automatically cleans messy repo names (e.g., `ecommerce-backend-main.zip` → "Ecommerce Backend").
    * **Dynamic Bullet Generator**: analyzing code metrics to write descriptions automatically.
* **Test Suite**:
    * `tests/test_schemas.py`: Verifies data validation rules.
    * `tests/test_item_formatter.py`: specific tests for the new logic, ensuring it handles missing data gracefully.
* **Infrastructure Fix**: Resolved a legacy import error with the `config` module by implementing a robust path-fix in the test runner.

---

### **By The Numbers**

| Metric | Value |
| :--- | :--- |
| **New Tests** | 8 (100% Pass Rate) |
| **New Classes** | 3 (`ItemFormatter`, `ResumeItemResponse`, `PortfolioCardResponse`) |
| **PR Strategy** | "Stacked" (PR #2 built on PR #1) |

---

### **Reflection**
Instead of writing one massive "Resume Generator," I adopted a "Stacked PR" strategy: first merging the data schemas (the contract), and then merging the logic (the implementation). This kept my code reviewable.

I also encountered a tricky environment issue where legacy imports (like `from config...`) were breaking new tests. I solved this by patching the system path in the test suite, allowing new code to interface with old modules without a massive refactor.

### **Next Steps**
* **Portfolio Logic:** Implement the richer `PortfolioFormatter` to handle images and success metrics.
* **API Wiring:** Connect these new formatters to Sami's FastAPI endpoints (`GET /resume/{id}`).
* **Integration:** Work with Eric to allow users to customize these auto-generated bullet points.

<img width="1050" height="601" alt="image" src="https://github.com/user-attachments/assets/ed110395-2e32-4b49-a3af-341c321b0934" />

# **Term 2 Week 3 (Jan 19 – Jan 25, 2026)**

This week, I focused on the second half of the display architecture: the **Portfolio Showcase** and the **User Customization System**.

## **Issue: [Milestone 2] Implement Portfolio Display & User Customization**

### **In Simple Terms**
I built the "visual" engine for our system and the "edit" functionality.
While last week was about generating text for resumes, this week was about generating rich data for the portfolio website. I also added the ability for users to say "No, I want to write this myself," allowing them to override our auto-generated descriptions with their own words.

---

### **What I Created**

* **Portfolio Logic Engine 
    * **Showcase Card Generator:** Created the logic to transform raw analysis data into a `PortfolioCardResponse` for the frontend.
    * **Evidence Integration:** Instead of writing my own metric calculations, I refactored the formatter to import and use the shared `evidence_extractor` module (built by Evan). This ensures that "Success Metrics" are consistent across the entire application.

* **User Customization Layer**
    * **Dependency Injection:** Modified both `ItemFormatter` (Resume) and `PortfolioFormatter` (Portfolio) to accept a `user_options` dictionary.
    * **Override Logic:** The system now intelligently checks for user input. If a user provides a `custom_title` or `custom_description`, the system prioritizes it; otherwise, it falls back to the auto-generated content.

* **Verified Reliability**
    * **Tests:** Wrote specific tests (`tests/test_portfolio_formatter.py` and `tests/test_custom_preferences.py`) to prove that:
        1.  The Portfolio card correctly pulls data from the shared evidence module.
        2.  User overrides successfully replace the default content.

---

### **Reflection**
The main challenge this week was **integration**. I had to build the Portfolio logic without breaking the existing "Download Report" feature from Term 1. I solved this by extending the existing class rather than replacing it.

I also adopted a **"Stacked PR" workflow** to keep my contributions clean:
1.  https://github.com/COSC-499-W2025/capstone-project-team-9/pull/253 Implemented the base Portfolio Logic.
2.  https://github.com/COSC-499-W2025/capstone-project-team-9/pull/251 Added the User Customization layer on top of PR #251.
This approach allowed my teammates to review the core logic first, while I continued working on the customization features in a separate branch.

### **Next Steps**
* **API Wiring:** Connect these new formatters to the FastAPI endpoints (`GET /portfolio/{id}`).
* **Frontend Check:** Verify that the React components can correctly display the JSON data structure I designed.

<img width="1027" height="609" alt="image" src="https://github.com/user-attachments/assets/bef6de8e-0c07-49d1-8039-2e264aeca770" />

---

# **Term 2 Week 4 (2026/01/26 to 2026/02/01)**

## **Issue: https://github.com/COSC-499-W2025/capstone-project-team-9/pull/285 feat: register resume_portfolio router and fix project manager mock data

I finished the "wiring" for our project's display logic. Previously, we had the engines to format resumes and portfolios, but they weren't connected to the web server. I built the API endpoints so the frontend can actually ask for and receive this data. I also fixed a bunch of broken tests that were causing headaches for the team.

### **What I Created**

- API Routes: GET /api/resume/preview/{project_id} – Returns bullet points for the resume builder. GET /api/portfolio/card/{project_id} – Returns rich data for the portfolio showcase.
- Data Retrieval Logic: ProjectManager.get_project_by_id() – A new method to fetch raw analysis data specifically for formatting.
- Test Stability: Refactored tests/test_project_manager.py to match our actual SQL queries, resolving the "column mismatch" crashes we were seeing in CI/CD.

---
### **Reflection** 
This week taught me the importance of keeping test mocks updated with production code. We spent a lot of time debugging why get_project_by_id was returning None in tests but working fine in the app. It turned out our mock database was returning 5 columns while the new query expected 4. Going forward, I want to look into using a Factory Pattern for our test data so we don't have to manually update tuples in 10 different test files every time we change a SQL query.

### Next Steps
- Frontend Integration: Work with the frontend team to ensure the React components interpret my JSON response correctly.
- Documentation: Update the Swagger/OpenAPI docs to reflect these new endpoints for the rest of the team.

# **What I Did This Week (2026/02/02 to 2026/02/08 Week 5)**

## **https://github.com/COSC-499-W2025/capstone-project-team-9/pull/310 Refactor with tests**

### **In Simple Terms**
I performed a major "cleanup" of our automated testing system. Previously, every test file created its own fake project data, meaning if we changed one thing in our database, we had to fix it in 5 different places. I consolidated all this data into a single "Source of Truth" (`conftest.py`).

I also fixed a critical issue where our tests were crashing because the test database was still looking for `user_id` instead of the new `user_name` field we implemented recently.

---

### **What I Created / Fixed**

* **Test Infrastructure (`tests/conftest.py`):**
    * Created a shared fixture file that automatically provides mock data to any test that needs it.
    * Significantly reduced code duplication in `test_portfolio_formatter.py` and `test_project_analyzer.py`.
* **Database Schema Fixes in Tests:**
    * Fixed `psycopg.errors.UndefinedColumn` errors in `test_analysis_router.py`.
    * Implemented a `DROP TABLE` command in the test setup to ensure the test environment always uses the latest database schema (fixing the conflict between `user_id` and `user_name`).
* **Logic Repairs:**
    * Fixed a bug in `ProjectAnalyzer` line counting tests where the mock data format (`10\nlines`) was causing integer conversion errors.
    * Corrected the patching logic for `ExternalServicePermission` to resolve `AttributeError` crashes.

---

### **By The Numbers**

| Metric | Value |
| :--- | :--- |
| **Pull Request** | **#255** |
| **Tests Rescued** | 11 (3 Failed, 8 Errors -> All Passing) |
| **Lines of Code Removed** | ~100+ (Deleted redundant setup code) |
| **New Test Files** | 1 (`conftest.py`) |

---

### **Reflection**
This week highlighted the cost of **technical debt** in test suites. Because we copy-pasted data setup code across multiple files early in the project, a simple database change (switching ID to Username) broke the entire analysis test suite.

Refactoring to use `pytest` fixtures (`conftest.py`) was necessary. It enforces the **DRY (Don't Repeat Yourself)** principle. Now, if we add a new field to a project, I only have to update it in one file, and all formatters and analyzers will automatically test against the new structure.

### **Next Steps**
* **Frontend Handoff:** Confirm with Sami that the Frontend can consume the JSON data exactly as the tests verify.
* **Resume Builder:** Finalize the integration of the `ItemFormatter` into the actual PDF generation flow.

<img width="1051" height="606" alt="image" src="https://github.com/user-attachments/assets/3c6773bd-3acc-4696-9d1b-6e0c76cc6f21" />

# **What I Did This Week (2026/02/09 to 2026/02/15 Week 6)**

## [Replace printing with logging#325](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/325)**

### **In Simple Terms**
I upgraded how our server "talks" to us when it runs. Previously, the code used simple `print()` statements (like you use when learning Python) to show errors or status updates. This is bad for real web servers because those messages often get lost or don't have timestamps. I replaced them with a professional **Logging System** that automatically tags every message with the time, severity (Info vs. Error), and the file it came from.

---

### **What I Created**

* **Centralized Logger (`src/common/logger.py`):**
    * Created a singleton configuration that ensures all logs follow a standard format: `[Time] - [Module] - [Level] - [Message]`.
    * Configured it to output correctly to the system's standard output (stdout), which is required for Docker and cloud deployment.
* **Backend Refactoring:**
    * Updated **`src/project_analyzer.py`**: Replaced raw error prints with `logger.error()` to catch analysis failures without crashing the server.
    * Updated **`src/portfolio/portfolio_formatter.py`**: Added logging to track when portfolio cards are successfully generated or if they return empty data.
    * Updated **`src/api/routes/resume_portfolio.py`**: Ensured every API request is logged, making it easier to debug why a specific request might fail (e.g., 404 Not Found vs 500 Server Error).

---

### **By The Numbers**

| Metric | Value |
| :--- | :--- |
| **Pull Request** | Replace printing with logging#325 #325 |
| **Files Changed** | 4 |
| **Lines of Code Modified** | ~300 (Refactoring) |
| **New Module** | `src/common/logger.py` |

---

### **Reflection**
This task was about **Production Readiness**. While `print("Error")` is fine for a homework assignment, it is a nightmare for a deployed application because you can't tell *when* an error happened or filter the logs to show *only* errors.

By implementing the `logging` library, we have improved our system's **observability**. Now, if the frontend team reports a bug, I can look at the server logs and instantly filter for `[ERROR]` to see exactly what went wrong, rather than scrolling through thousands of "Analyzing..." print statements.

### **Next Steps**
* **Log Monitoring:** Verify that these logs show up correctly in our Docker container output.
* **Frontend Support:** Assist Sami and the frontend team as they integrate the new AI Ranking display, using the server logs to troubleshoot any data connection issues.

# **What I Did This Week (2026/02/16 to 2026/02/22 Week 7)**

## **Refactor with Hardcode Constants & Database Robustness (https://github.com/COSC-499-W2025/capstone-project-team-9/pull/332)**

### **In Simple Terms**
I cleaned up how our system reads and formats project names. Before, if a user uploaded a file like "my-project-main.zip", the rules to delete the "-main" and ".zip" parts were copied and pasted in several different files. I moved all these rules into one central location. I also fixed a bug in the database saving process so the server won't crash if the frontend accidentally sends empty or missing data when saving portfolio customizations.

---

### **What I Created & Refactored**

* **Centralized Constants (DRY Principle):**
    * Extracted lists of common project suffixes (like `.zip`, `-main`, `-master`) into a single source of truth.
    * Replaced duplicated string-stripping and name-formatting logic across multiple files to pull from this central list instead.
* **Database Operation Robustness (`resume_manager`):**
    * Added defensive programming checks to the portfolio customization logic. 
    * The backend now gracefully handles `None` or missing data payloads coming from the frontend, preventing unhandled exceptions and database crashes.

---

### **By The Numbers**

| Metric | Value |
| :--- | :--- |
| **Pull Request** | **#332** |
| **Design Principle** | DRY (Don't Repeat Yourself) |
| **Code Smells Removed** | Multiple "Magic Strings" & Duplicated Logic |
| **Bugs Prevented** | `NoneType` crashes from frontend payloads |

---

### **Reflection**
This week was heavily focused on paying down **technical debt**. Copy-pasting string cleaning logic seemed harmless early in the project, but it quickly became unmaintainable. By enforcing DRY principles, I ensured that if we ever need to support a new repository suffix (like `-dev` or `-v2`), we only have to update a single file, rather than hunting down every `.replace()` method in the codebase.

Additionally, the fix in the resume manager reinforced a critical lesson in API development: **never fully trust the data coming from the frontend**. Building resilient backend operations that fail gracefully when receiving `None` ensures a much smoother experience for the end user and a more stable server.

### **Next Steps**
- **Milestone 2 Demo:** Ensure the deployment environment is perfectly stable and ready for the TA demonstration.
- **Log Monitoring:** Use the logging infrastructure implemented in previous weeks to monitor the API endpoints and verify that the fallback logic for missing frontend data is working silently and correctly in production.

# **What I Did This Week (2026/02/23 to 2026/03/01 Week 8)**

## **Implement Global Exception Handling (#342)** https://github.com/COSC-499-W2025/capstone-project-team-9/pull/342

### **In Simple Terms**
I built a "safety net" for our backend server. Previously, if something unexpected happened—like the database going down or the AI timing out—the server would crash and send an ugly, unreadable error to the frontend, which would break the user interface. Now, I intercept every single crash before it leaves the server, log it silently for the developers, and send back a clean, polite error message to the user along with a specific "Request ID" so we can easily track down the bug.

---

### **What I Created / Modified**

* **Created `src/api/exception_handlers.py`:**
    * Wrote a `global_exception_handler` to catch unexpected 500 Internal Server Errors.
    * Wrote an `http_exception_handler` to standardize standard HTTP errors (like 404 Not Found or 401 Unauthorized).
* **Modified `src/api/main.py` & Middleware:**
    * Registered the handlers with our core FastAPI instance.
    * Hooked the error handlers into the `request_context` middleware I built last week, allowing the server to grab the exact `X-Request-ID` of the crash and inject it directly into the JSON error response sent to the frontend.

---

### **By The Numbers**

| Metric | Value |
| :--- | :--- |
| **Pull Request** | **#342** |
| **Files Modified** | 3 |
| **New Modules** | 1 (`exception_handlers.py`) |
| **Impact** | 100% of API endpoints are now protected from raw trace leaks |

---

### **Reflection**
This task brings our API to a true production-ready state. In the real world, servers fail all the time. The mark of a professional backend is how gracefully it handles those failures. 

By standardizing our error formats, I significantly unblocked the frontend team. They no longer have to write messy `try/catch` blocks guessing if they are going to receive HTML, text, or a dictionary. They know they will *always* receive a standard JSON object. Furthermore, injecting the Request ID into the payload turns bug-hunting from a 30-minute chore into a 10-second log search.

### **Next Steps**
* **Background Tasks:** Now that our errors and logs are fully mapped, the next logical step is migrating our heavy analysis functions (like the Zip extraction and Gemini prompt generation) to run asynchronously in the background so we stop blocking the main server thread.

<img width="1040" height="622" alt="image" src="https://github.com/user-attachments/assets/adfa8f25-6e17-45fa-a7ba-8ce2b7ad6772" />

# **What I Did This Week (2026/03/02 to 2026/03/08 Week 9)**

## Implement global error toast notification UI (#354) https://github.com/COSC-499-W2025/capstone-project-team-9/pull/354

### **In Simple Terms**
Last week, I built a safety net on the server to catch crashes and generate clean error messages. This week, I brought those messages directly to the user interface. I built a "Toast Notification"—a sleek red popup that automatically slides into the bottom corner of the screen whenever a network request fails or the server throws an error. Instead of the website just freezing silently when something goes wrong, the user now sees exactly what happened along with a specific "Request ID" they can send to developers.

---

### **What I Created / Modified**

Modified frontend/dashboard.html (HTML & JS):

Added the hidden HTML container and structure for the notification popup.

Wrote new JavaScript functions (showErrorToast, closeErrorToast) to control the popup's behavior and auto-hide timer.

Updated the global apiCall function block to automatically extract the message and request_id from the backend's JSON and trigger the UI popup on any failure.

Modified frontend/css/dashboard.css:

Added custom styling to make the notification look like a modern, professional alert (similar to GitHub or Google Drive).

Implemented CSS transitions for smooth slide-in and fade-out animations.

---

### **By The Numbers**

| Metric | Value |
| :--- | :--- |
| **Pull Request** | **#354** |
| **Files Modified** | 2 |
| **New Modules** | 1 (Global Error Toast) |
| **Impact** | 100% of frontend API failures now provide instant visual feedback to the user |

---

### **Reflection**
This task was incredibly satisfying because it perfectly closed the loop on my backend error architecture from last week. A robust backend error-handling system is only useful if the frontend actually consumes its data properly.

By bringing the X-Request-ID directly into the user's view, we have elevated the application to a highly polished, production-ready state. Bug hunting is now drastically easier for the whole team because users (or testers) can simply take a screenshot of the UI popup, and we can immediately search our backend server logs for that exact request ID.

### **Next Steps**
* **Documentation & API Architecture:** As we push deep into Milestone 3, I plan to shift my focus to taking ownership of our System Architecture documentation. I will be updating our README with the newly required Data Flow Diagrams (DFD levels 0 and 1) and evaluating our API routes to implement the required Public/Private view modes.
<img width="1044" height="606" alt="image" src="https://github.com/user-attachments/assets/258d226c-3004-4ab9-ab3c-39e680f78ffb" />

# **What I Did This Week (2026/03/09 to 2026/03/15 Week 10)**

## fix generate resume bug 374 https://github.com/COSC-499-W2025/capstone-project-team-9/pull/374

### **In Simple Terms**
I fixed a critical bug where the server would completely freeze when a user tried to generate a resume from the web dashboard. The issue was that the backend code was originally written for a terminal (CLI), so it was pausing the entire server to ask "Which name do you want to use?" and waiting endlessly for someone to type an answer. I updated the code to detect when it is being run by the website (headless mode) so it automatically skips the manual prompt and instantly generates the resume using the user's login name

---

### **What I Created / Modified**
Modified src/resume/resume_manager.py:

Added a sys.stdin.isatty() environment check inside the generate_user_resume function to determine if the code is running in an interactive terminal or as a web API.

Implemented a headless fallback path: if the code is triggered via the API, it automatically assigns display_name = user_name and completely bypasses the blocking input() menus.

Preserved the original interactive menu logic so the function still works perfectly when developers run it locally from the command line.

---

### **By The Numbers**

| Metric | Value |
| :--- | :--- |
| **Pull Request** | 374 |
| **Files Modified** | 1 |
| **New Modules** | 0 (Architectural logic fix) |
| **Impact** | 100% of frontend resume generation requests now succeed without locking the server thread. |

---

### **Reflection**
This bug was a fantastic lesson in software architecture and the challenges of transitioning a project from a Command Line Interface (CLI) to a Web API. It highlighted the danger of mixing user-interface logic (like input() prompts) directly inside core business logic.

Finding the root cause required full-stack debugging: the frontend console looked fine, the network requests were simply "pending," but the backend VSCode terminal was secretly waiting for a keystroke. By properly decoupling the interactive prompts from the generation code using standard input checks, I made our backend significantly more robust and production-ready.

### **Next Steps**
Audit Legacy CLI Logic: I need to do a thorough sweep of the remaining backend services to ensure no other features contain hidden print() menus or input() prompts that could cause similar server hangs on the live website.

Implement Background Tasks: With the immediate freezing bug patched, the next major hurdle is preventing browser timeouts during long operations. I plan to implement FastAPI BackgroundTasks for our heavy operations (like extracting massive ZIP files or waiting 20+ seconds for the Gemini AI), allowing the server to return an instant "Processing" response to the frontend while the heavy lifting happens behind the scenes.
