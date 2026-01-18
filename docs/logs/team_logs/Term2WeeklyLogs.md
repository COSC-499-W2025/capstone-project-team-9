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
### What I completed this week
This week was a slow week. There was not much communication between team members and there were some members who did not do any contributions.
I worked on fixing he resume output.
I linked the resume to the login database and the collaborators database so that the user is able to select the name that they want shown on the resume rahter than just having no name.
I had to re do a lot of tests to fix these cahnges and this resulted in me making 2 PRs
### Link to PR
This is the link to the PR that i have made: https://github.com/COSC-499-W2025/capstone-project-team-9/pull/165
This is the link to the PR that i have made: https://github.com/COSC-499-W2025/capstone-project-team-9/pull/166
### What went well
Getting back in to the capstone loop overall went well for me.
I am well aware of what is going on in our project and i know what needs to be done and improved on.
The coding aspect of this week went well and i am happy with what i accomplished coding wise
### what didnt go well
I made some mistakes when creating my pull requests and made 2 seperate pull requests. One for the project updates, and one for the test updates
This resulted in some confusing and made it so that the github actiosn we had set up failed. It was all sorted out though
Along with this some members did not write code so i was only able to review one peice of code.
### Next week 
We will address what needs to be done on our meeting tommorow. For some reason we have not all been able to meet up as a group so we have not been able to discuss this,
I would like to add in more api calls as there are a lot of feature that could benifit from this. THere is alos still work that needs to be done on the resume
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

# Sprint Report – Week 15 (2026/01/12 to 2026/01/18)

## **Overview**
This sprint marked the start of a new milestone and served as a reset point for the team. Rather than pushing new functionality immediately, the focus this week was on transitioning cleanly from Milestone 1, performing minor refactoring, and aligning on a clear plan for the work ahead.
The team spent the majority of the sprint discussing scope, responsibilities, and technical direction to ensure a strong foundation for the upcoming development phases.

## **Completed Work**
- **Minor Refactoring:** Cleaned up small pieces of code carried over from Milestone 1 to improve readability and maintainability.
- **Milestone Planning:** Team discussions around goals, priorities, and expected deliverables for this milestone.
- **Technical Alignment:** Reviewed existing architecture and identified areas that may need improvement or extension moving forward.
- **Task Breakdown:** Began outlining tickets and responsibilities for upcoming weeks.

### **Kevin**
- Write What you've done

**Requirements addressed:**
- NA for this current week as there has been no technical work done. 
---

### **Sami**
- Write What you've done

**Requirements addressed:**
- NA for this current week as there has been no technical work done. 
---

### **Eric**
-The first feature adds support for custom résumé wording on a per-project basis. Users can now provide their own description for an individual project, which is stored and later prioritized during résumé generation. This allows users to highlight specific contributions or achievements that may not be fully captured by automatically generated summaries, while still falling back to stored or generated summaries when no customization is provided.
-The second feature extends this functionality by introducing basic management for custom résumé wording. Users can clear or reset previously saved custom descriptions and list which projects currently have customized wording. Together, these features define a clear lifecycle for résumé customization and make the system more robust, maintainable, and aligned with Milestone 2 requirements.

**Requirements addressed:**
- Allow users to choose which information is represented in the résumé. This week’s work enables users to control how individual projects are presented by providing custom résumé wording, resetting it when needed, and managing customized entries, ensuring user-authored content is prioritized over automatically generated summaries.
---

### **Evan**
- Write What you've done

**Requirements addressed:**
- NA for this current week as there has been no technical work done. 
---

### **JinXi**
- Write What you've done

**Requirements addressed:**
- NA for this current week as there has been no technical work done. 

---

### **Ryan**
- Write What you've done

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
| **Eric** | **JinXi** | issue127-1:implement user data isolation on project manager (also update all other files which use project_manager.py) issue#198 #200|
| **Eric** | **Ryan** | Recognize duplicate files #195|
| **Eric** | **Sami** | FastAPI Implementation #191|

---

## **Next Steps**
### **Intermediate**
- **Capstone Part 2 (New Term):** - Discuss potential transition to a Web/GUI interface.
  - Explore deploying the database to a cloud provider.
  - Implement advanced LLM features for better project summarization.

---
