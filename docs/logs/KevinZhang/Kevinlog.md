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
