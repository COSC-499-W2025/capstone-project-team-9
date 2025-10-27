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
