# Sprint Report – Week 14 (2026/01/04 to 2026/01/11)

## **Overview**
This sprint marked the start of a new milestone and served as a reset point for the team. Rather than pushing new functionality immediately, the focus this week was on transitioning cleanly from Milestone 1, performing minor refactoring, and aligning on a clear plan for the work ahead.
The team spent the majority of the sprint discussing scope, responsibilities, and technical direction to ensure a strong foundation for the upcoming development phases.

## **Completed Work**
- **Minor Refactoring:** Cleaned up small pieces of code carried over from Milestone 1 to improve readability and maintainability.
- **Milestone Planning:** Team discussions around goals, priorities, and expected deliverables for this milestone.
- **Technical Alignment:** Reviewed existing architecture and identified areas that may need improvement or extension moving forward.
- **Task Breakdown:** Began outlining tickets and responsibilities for upcoming weeks.

### **Kevin**


**Requirements addressed:**
- NA for this current week as there has been no technical work done. 
---

### **Sami**
- Spent time creating the weekly log this week, and helping devleop a plan for the next milestone.
- Reviewed 2 PR's for refactoring based off of last milestone. 

**Requirements addressed:**
- NA for this current week as there has been no technical work done. 
---

### **Eric**
- This week I spent time reading through the Milestone 2 requirements and discussing them with the team. The focus was on understanding the scope and planning rather than writing new code. I also began considering which areas I can contribute to in the next sprint.

**Requirements addressed:**
- NA for this current week as there has been no technical work done. 
---

### **Evan**
- I wrote the code for pull requests 185 which helped with integration of our LLM
- I also started planning on what i need to do for milestone 2

**Requirements addressed:**
- NA for this current week as there has been no technical work done. 
---

### **JinXi**
This week I do the refactoring on upload file functions and the upload_file data table.
-  Change the codes in upload_file.py to fit the existed account system, and change test_upload_file.py to test the new codes.

**Refactoring**: issue128 refactoring associate newly uploaded files with the user
- refactoring on the file uploaded codes and uploaded_file DB.
- Add user_name form user_information table as the foreign key to uploaded_file table
- Modify file upload codes to make the system can upload current user's user_name to the uploaded_file table
- update the tests of uploaded file

**PR reviewed**: #182;#183

---

### **Ryan**


**Requirements addressed:**
- NA for this current week as there has been no technical work done. 
---

## **Current Status**
- **Code Freeze:** Active. No new features are being merged.
- **Test Coverage:** Test coverage is fantastic from previous milestone. Ready for next milestone implementation. 
- **Stability:** The application is stable and ready for next milestone. 
- **Project State:** Completed for Milestone 2.
---

## **Testing**
- We added testing for the resume generation feature and the LLM feature. The resume was a refactor of the previous milestone and the LLM is new, however very basic as we've only just begun. 

---

### **Collaboration Highlights**
- **Code Freeze Coordination:** The team communicated effectively to ensure no risky changes were pushed to `main` this week.
- **Test Swapping:** Team members tested each other's modules to find edge cases that the original author might have missed.
- **Production Planning:** The team collaborated on the plan for the next milestone. 

### **Things to Work On / Reflection**
- **Semester Wrap-up:** The project is now effectively concluded. The team worked well to integrate a complex set of features (Auth, NLP, Analysis, Database) into a cohesive CLI tool.
- **Final Check:** Ensure all "TODO" comments are removed or addressed in the code.
- **Documentation:** Ensure the User Manual explains the final menu structure, as it changed recently.

### **Peer Evaluations**
| Reviewer | Reviewee | Focus Area |
|-----------|-----------|-------------|
| **Sami** | **Ryan** | Reviewed Added tests and fixed all tests for prev PR PUSH BEFORE FIRST PR |
| **Sami** | **Ryan** | Reviewed Added tests and fixed all tests for prev PR PUSH BEFORE FIRST PR |
| **JinXi** | **Ryan** | Reviewed Resume Manager tests |
| **JinXi** | **Ryan** | Reviewed Changing the Resume format|
| **Eric** | **JinXi** | issue128 refactoring associate newly uploaded files with the user #184|
| **Eric** | **Evan** | integrating llm into our menus #185|

---

## **Next Steps**
### **Intermediate**
- **Capstone Part 2 (New Term):** - Discuss potential transition to a Web/GUI interface.
  - Explore deploying the database to a cloud provider.
  - Implement advanced LLM features for better project summarization.

---

