# Sprint Report – Term 2 Week 1 (2026/01/04 to 2026/01/11)

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

# Sprint Report – Term 2 Week 2 (2026/01/12 to 2026/01/18)

## **Overview**
This sprint marked the start of a new milestone and served as a reset point for the team. Rather than pushing new functionality immediately, the focus this week was on transitioning cleanly from Milestone 1, performing minor refactoring, and aligning on a clear plan for the work ahead.
The team spent the majority of the sprint discussing scope, responsibilities, and technical direction to ensure a strong foundation for the upcoming development phases.

## **Completed Work**
- **Minor Refactoring:** Cleaned up small pieces of code carried over from Milestone 1 to improve readability and maintainability.
- **Milestone Planning:** Team discussions around goals, priorities, and expected deliverables for this milestone.
- **Technical Alignment:** Reviewed existing architecture and identified areas that may need improvement or extension moving forward.
- **Task Breakdown:** Began outlining tickets and responsibilities for upcoming weeks.

### **Kevin**
- Milestone Strategy & Task Breakdown: Analyzed Milestone 2 requirements and established a "Stacked PR" workflow and maintaining development velocity. Created a project and five granular sub-issues on the Kanban board to track deliverables.
- Core Feature Implementation: Developed a new ItemFormatter utility in src/resume/item_formatter.py. This module handles the granular transformation of raw project analysis data into professional, resume-ready bullet points.

**Requirements addressed:**
- Display textual information about a project as a résumé item
- Define Pydantic Output Schemas (Resume & Portfolio) https://github.com/COSC-499-W2025/capstone-project-team-9/issues/210
- Implement ResumeFormatter Logic https://github.com/COSC-499-W2025/capstone-project-team-9/issues/211
---

### **Sami**
### What I completed this week
- This week I worked on the milestone goal of setting up FastAPI to facilitate communication between the backend and frontend. This addresses issues #188-190.
- I created a new API structure in the src/api/ directory with:
    - main.py - FastAPI application with CORS middleware for frontend connectivity
    - dependencies.py - Shared database connection helpers using FastAPI's dependency injection pattern
    - routes/health.py - Health check endpoints (basic and database connectivity)
    - routes/project.py - Projects verification endpoint
- I linked the API to Docker by:
    - Adding an API service to docker-compose.yml that depends on the database service
    - Creating a Dockerfile for the API container
    - Setting up networking between services
- I created a mock frontend (frontend/index.html) to test API connectivity with buttons to test all endpoints and display JSON responses.
- I also worked with Kevin to fix a bug in the get_db_cursor dependency. The issue was using @contextmanager decorator instead of a FastAPI dependency function that yields, which would prevent proper cleanup. This was fixed to use FastAPI's dependency injection lifecycle correctly.
- Finally, I created a test file (tests/test_api.py) covering all endpoints, error handling, and dependency lifecycle.

### Link to PR
This is the link to the PR that I have made: #191

### What went well
- My coding went well this week. I was able to set up the FastAPI structure and get all endpoints working. I'm pleased with the clean separation of concerns (routes, dependencies, main app).
The Docker integration went smoothly, and the API service properly waits for the database to be healthy before starting.
- I didn't have any problems while attending class or communicating with my group members, which was very nice.

### What didn't go well
- I initially had an issue with the dependency injection pattern - I used a context manager decorator instead of a FastAPI dependency function. Kevin caught this in review, and I was able to fix it quickly.
- There was also a missing dependency (httpx) that was needed for the test client, but I added it to requirements.txt once identified.

### What I will work on next week
Next week I would like to continue expanding the API by adding more endpoints for the existing functionality (projects, analysis, portfolio, etc.).
---

### **Eric**
-The first feature adds support for custom résumé wording on a per-project basis. Users can now provide their own description for an individual project, which is stored and later prioritized during résumé generation. This allows users to highlight specific contributions or achievements that may not be fully captured by automatically generated summaries, while still falling back to stored or generated summaries when no customization is provided.
-The second feature extends this functionality by introducing basic management for custom résumé wording. Users can clear or reset previously saved custom descriptions and list which projects currently have customized wording. Together, these features define a clear lifecycle for résumé customization and make the system more robust, maintainable, and aligned with Milestone 2 requirements.

**Requirements addressed:**
- Allow users to choose which information is represented in the résumé. This week’s work enables users to control how individual projects are presented by providing custom résumé wording, resetting it when needed, and managing customized entries, ensuring user-authored content is prioritized over automatically generated summaries.
---

### **Evan**
- I wrote the code for pull requests 215 and 224 both of these included tests
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/215
        - testing and codeing
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/224
        - also includes aditional tests and a bug fix, therefore is codeing debugging and testing.

- I reviewed the pull requests of two team members 202 and 204
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/202 for for Eric
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/204 for JinXi
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/222 for Kevin
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/222 for Kevin

### My Plan for next week
- I will continue to work on milestone 2 requirements particulairly Incorporating evidence of success for projects

### Reflection
- Overall I got a good feature for milestone 2 done as well as some enhancments and bug fixes so I would call it a successful week
- I also reviewed lots of code
- One negative was there was somehow a bug that did not show up in my initial testing but was causing a timeout error in some cases that got by our code review and ended up in main which was painful

**Requirements addressed:**
- I addressed the requirement of having a thumbnail for each project is PR 215 
---

### **JinXi**
- This week keep developing on implement user data isolation feature.
#### Developed PRs:
[issue127-1:implement user data isolation on project manager (also update all other files which use project_manager.py)](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/200)
- This PR update the project_manager.py to implement user data isolation, and also do other needed change to ensure the system still works.
1. Update the project_manager.py, add user_name as parameters for all functions which use the updated_file data table.
2. Update other files such as project_display.py, project_summarize.py, profolio_manager.py, project_ranking.py and so on. Which add user_name as parameters into them, and update functions in need. (This Update ensure the system can work.)
3. Update codes of resume generate and portfolio functions, let them user logged in user's name as permeate instead of 'defult_user'.
4. Change some variable name 'user_id' into 'user_name', this is for reduce naming conflicts.
5. Update the test files of all changed files.

(**Need bug fix**)[issue127-2: update other data table which include user id to connect them with user information table)](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/204)
- Update the data table external_service_permissions, user_consent, user_preferences to implement user data isolation, and also update related codes.
1. change files such as consent_manager.py, service_config.py, permission_manager.py, external_service_promopt.py and so on. Add user_name as parameter to replace the old hard coded user_id.
2. write migrations.py to auto update data base.
3. change the system initial order, put the login page to most first thing.
update the tests files.
  
#### PR reviewed: 
1. [Feature: Resume content selection (projects & skills)](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/197)
2. [feat: support custom resume wording per project](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/202)

---

### **Ryan**
### What I completed this week
- This week I worked on the milestone goal of only allowing files that havent been uploaded to be uploaded
- This means that we are now only able to upload files or zip files that have already been uploaded. This is done by first cheking the zip folder name and bits, and then next checking all of the file content of each file to see if there are any non duplicate files. 
- If there is a file that is a duplicate it needs to be skipped and that will happen
- Along with this is worked with kevin to solve a bug that cam from Evans code. The error was not caught until the code was merged
### Link to PR
- This is the link to the PR that i have made: [https://github.com/COSC-499-W2025/capstone-project-team-9/pull/195](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/195)
### What went well
- MY coding went very well this week. I was able to get all my coding done early on in to the week and was proud of the work that i outputed.
- My code did have a merge conflict but i was able to resolve it quite easily
- I did not have any problems while attending class or communicating with my group members which was very nice,
### what didnt go well
- I did have a merge conflit which isnt the best but it was not too complcated to resolve
- Other than this i dont think that there is anything that personally didnt go very well for me
- There was a peice of evans code that borke the testing and this was now found out until it was merged so i had to write a bug fix test.
### what i will work on next week
- Next week i would like to continue to work on the duplicate file and zip code. there are a few things that i need to add in order to ensure the best product
- I will also begin to work on this: Allow incremental information by adding another zipped folder of files for the same portfolio or résumé that incorporates additional information at a later point in time
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
| **Ryan** | **JinXi** | issue127-1:implement user data isolation on project manager (also update all other files which use project_manager.py) issue#198 #200|
| **Ryan** | **Evan** | add thumbnail for projects and tests accordingly|
| **Kevin**|**Eric**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/202 feat: support custom resume wording per project
|**Kevin**|**Eric**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/197 Feature: Resume content selection (projects & skills)
|**Kevin**|**JinXi**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/200 Implement user data isolation on project manager 
| **Evan** | **Eric** |https://github.com/COSC-499-W2025/capstone-project-team-9/pull/202 custom resume wording|
| **Evan** | **JinXi** |https://github.com/COSC-499-W2025/capstone-project-team-9/pull/204 update user tables with data|
| **Evan** | **Kevin** |https://github.com/COSC-499-W2025/capstone-project-team-9/pull/222 schemas for resume and portfolio|
| **Evan** | **Kevin** |https://github.com/COSC-499-W2025/capstone-project-team-9/pull/223 resume item formatter|
| **Sami** | **Ryan** |https://github.com/COSC-499-W2025/capstone-project-team-9/pull/195 Recognize Duplicate Files|
| **Sami** | **Eric** |https://github.com/COSC-499-W2025/capstone-project-team-9/pull/197 Feature: Resume content selection (projects & skills) |
---

## **Next Steps**
### **Intermediate**
- **Capstone Part 2 (New Term):** - Discuss potential transition to a Web/GUI interface.
  - Explore deploying the database to a cloud provider.
  - Implement advanced LLM features for better project summarization.

---
## **Burnup Chart**
<img width="1047" height="626" alt="image" src="https://github.com/user-attachments/assets/16ab36a8-f92d-4164-94d5-bd185beda6f1" />
<img width="1022" height="579" alt="image" src="https://github.com/user-attachments/assets/d691bbe6-df59-4d3d-b9f1-da6cc79d2199" />

---

# Sprint Report – Term 2 Week 3 (2026/01/19 to 2026/01/25)

## **Overview**
This sprint marked the start of a new milestone and served as a reset point for the team. Rather than pushing new functionality immediately, the focus this week was on transitioning cleanly from Milestone 1, performing minor refactoring, and aligning on a clear plan for the work ahead.
The team spent the majority of the sprint discussing scope, responsibilities, and technical direction to ensure a strong foundation for the upcoming development phases.

## **Completed Work**
- **Minor Refactoring:** Cleaned up small pieces of code carried over from Milestone 1 to improve readability and maintainability.
- **Milestone Planning:** Team discussions around goals, priorities, and expected deliverables for this milestone.
- **Technical Alignment:** Reviewed existing architecture and identified areas that may need improvement or extension moving forward.
- **Task Breakdown:** Began outlining tickets and responsibilities for upcoming weeks.

### **Kevin**
I built the "visual" engine for our system and the "edit" functionality.
While last week was about generating text for resumes, this week was about generating rich data for the portfolio website. I also added the ability for users to say "No, I want to write this myself," allowing them to override our auto-generated descriptions with their own words.

**Requirements addressed:**
-  https://github.com/COSC-499-W2025/capstone-project-team-9/pull/253 Implemented the base Portfolio Logic. Added the User Customization layer on top of PR #251
- https://github.com/COSC-499-W2025/capstone-project-team-9/pull/251 

---

### **Sami**
- This week I refactored the CLI to consolidate all configuration options into a single Settings menu, added and standardized backend API endpoints for settings and project data management, and expanded automated tests to match the updated behavior. I also built out frontend functionality by setting up the initial frontend with Docker integration and implementing a login page connected to the existing backend authentication. In addition, I implemented multiple project-related API endpoints, closed several tracked issues, and fixed bugs introduced during development to keep feature branches stable. Overall, the CLI and API are now cleaner and easier to maintain, frontend and backend communication works end-to-end, and issues were caught early, though some refactors required follow-up fixes and frontend PRs were larger than expected. Next week, I plan to continue expanding frontend features, add additional API endpoints, and polish the overall UI/UX and application flow.

---

### **Eric**
-Implemented support for custom résumé wording on a per-project basis, allowing users to provide and persist their own project descriptions. Custom wording is prioritized during résumé generation, with a safe fallback to stored or automatically generated summaries when no customization is provided.
-Added basic management capabilities for custom résumé wording, including clearing or resetting saved descriptions and listing projects with customized entries. This establishes a clear and maintainable lifecycle for résumé customization aligned with Milestone 2 goals.

**Requirements addressed:**
- Allow users to choose which information is represented in the résumé.
This work enables users to control how individual projects are presented by prioritizing user-authored résumé wording over system-generated summaries, while also providing mechanisms to manage and reset customized content.
---

### **Evan**
- I wrote the code for pull requests 246 this was big pr for a feature to really change our analysis it also included a bunch of tests.
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/246
        - testing and codeing
        - I probably should have split this into a least two PR's

- I reviewed the pull requests of two team members 202 and 204
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/233 for sami
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/231 for sami
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/241 for jinxi
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/245 for eric

### My Plan for next week
- I want to work one fixing bugs and making our frontend work as well as some refactoring in the console.

### Reflection
- I got a big complex feature implemented this week which was sucsessful
- I also reviewed a lot of code
- I had two bits of code that were redundant due to miscomunication with team mates which was annoying.
---

### **JinXi**
This week I am keep developing the user data isolation feature.
- [Finished] Isolation in portfolio feature; isolation in resume feature; isolation in project rank feature.
- [Additional] Add a development evnironment only tool to manage the data base.

#### issue developed:
[Add a DB manage tool, and delete useless files](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/238)
The current main branch actually do not have any breaking errors, but the local data base may cause problems.
- Add a development tool called drop_table.py. This file is used to drop data tables in data base, this would same time.
- Add security check for the drop_table.py to ensure it wont work in business environment.

[Issue127-2: implement data isolation in portfolio feature](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/240)
A small PR, only change few lines of codes on portfolio_manager.py and portofolio_display.py.
- Add auto get current user function in this two files
- update the test file

[issue127-3: implement user data isolation in resume function](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/241)
This PR implement the data isolation in resume feature, and fix some old Bugs.
- Change the generated_resumes data tables, which reference user_name from user_information table as the forigen key.
- Change the CRUDs of generated_resumes table to fit the new data table and implement the resume isolation between different users.
- Add codes to update the old data table
- Fix the Bug which print 'Error: No user logged in' in project summary, portfolio and resume.
- Update the tests.

[issue127-5: implement the data isolation on project summary and rank feature](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/250)
This PR implement the data isolation in project rank feature based on user_name.
- Add user_name as a foreign key into the project_rankings data table.
- Update the functions in ranking_storage.py, make the could use user_name as a parameter to do their job.
- updata the test files in need

#### PR reviewed: 
PR#231, PR#233, PR#234, PR#239, PR#242

---

### **Ryan**
### What I completed this week
- This week I worked on developing the front end with sami. He created a general layout of the website and I used fastAPI connections to connect the backend to the front end.
- I enhanced the Analysis section of the webiste and allowed for it to show all of the details of the project after ou analyzied it.
- Along with this had a bug fix in the front end. This was a simple bug fix so that the files uploaded will use the same names when you list the Projects. Before they were using a random name that was generated from the strong of the project name.
### Link to PR
- This is the link to the PR that i have made: https://github.com/COSC-499-W2025/capstone-project-team-9/pull/243
- this is the second link: https://github.com/COSC-499-W2025/capstone-project-team-9/pull/242
### What went well
- As the frontend has now been created it was easy to spot things that need enhancement and things that need work
- The front end is getting built very fast
### what didnt go well
- There is a lot of pull requests that are still adding functionlaity to the main menu. This causes some problems as we will have to keep adding in API routes wihotut just doing it at one time. we need to solely start to add this directly to the front end.
### what i will work on next week
- I will continue to work on the front end development by connecting the front end to back end
- I will need to refactor a lot of work that has been already done. We need to limit the amount of overlapping code and limit the amount of menu options
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

### **Peer Evaluations** (Do not Skip this part, they were from last week, you need to change to this week)
| Reviewer | Reviewee | Focus Area |
|-----------|-----------|-------------|
| **Sami** | **Evan** | [incorporate evidence of sucess and related tests](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/246) |
| **Sami** | **Ryan** | [Enhance Project Analysis](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/243) |
| **Sami** | **Evan** | [add the ability to delete a project](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/249) |
| **Sami** | **Eric** | [Added custom résumé wording management API (save/list/clear).](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/244)) |
| **Sami** | **Jinxi** | [Implement Portfolio Formatter Logic](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/251) |
| **JinXi** | **Sami** | Issue #227-#230 (Project API Endpoints) |
| **JinXi** | **Sami** | Frontend - Login Page|
| **JinXi** | **Sami** | Simple Frontend|
| **JinXi** | **Sami** | API Endpoints Resume, Skills, Portfolio|
| **JinXi** | **Ryan** | Simple Bug fix|
| **Eric** | **JinXi** | Issue127-2: implement data isolation in portfolio feature #240|
| **Eric** | **Ryan** | Enhance project analysis #243|
| **Eric** | **Sami** | Frontend - Login Page #233|
| **Ryan** | **JinXi** | Issue127-2: implement data isolation in portfolio feature https://github.com/COSC-499-W2025/capstone-project-team-9/pull/240|
| **Ryan** | **Jynxi** | Add a DB manage tool, and delete useless files [#238](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/240)|
| **Ryan** | **Sami** | API Endpoints Resume, Skills, Portfolio https://github.com/COSC-499-W2025/capstone-project-team-9/pull/239|
| **Ryan** | **Sami** | Simple Frontend [ #234](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/234)|
| **Ryan** | **Evan** |add the ability to delete a project [#249 ](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/249)|
| **Kevin**|**Ryan**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/243 Enhance project analysis
|**Kevin**|**Eric**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/244 Added custom résumé wording management API
|**Kevin**|**Eric**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/245 feat(resume): add evidence of success generation for projects
| **Evan** | **Sami** |https://github.com/COSC-499-W2025/capstone-project-team-9/pull/233 front end login|
| **Evan** | **Sami** |https://github.com/COSC-499-W2025/capstone-project-team-9/pull/231 api endpoints|
| **Evan** | **Eric** |https://github.com/COSC-499-W2025/capstone-project-team-9/pull/245 evidence of success|
| **Evan** | **Jinxi** |https://github.com/COSC-499-W2025/capstone-project-team-9/pull/241 user data isolation bug|
---

## **Next Steps**
### **Intermediate**
- **Capstone Part 2 (New Term):** - Discuss potential transition to a Web/GUI interface.
  - Explore deploying the database to a cloud provider.
  - Implement advanced LLM features for better project summarization.

---
## **Burnup Chart**
<img width="1051" height="569" alt="image" src="https://github.com/user-attachments/assets/b38589a2-2d96-4b0f-86db-5594fd2340fc" />
<img width="1043" height="611" alt="image" src="https://github.com/user-attachments/assets/b9721f35-e6ed-420a-8267-dbd20368bd1c" />

---

# Sprint Report – Term 2 Week 4 (2026/01/26 to 2026/02/01) (STOP COPY AND PASTE LAST WEEK)

## **Overview**
This sprint marked the start of a new milestone and served as a reset point for the team. Rather than pushing new functionality immediately, the focus this week was on transitioning cleanly from Milestone 1, performing minor refactoring, and aligning on a clear plan for the work ahead.
The team spent the majority of the sprint discussing scope, responsibilities, and technical direction to ensure a strong foundation for the upcoming development phases.

## **Completed Work**
- **Minor Refactoring:** Cleaned up small pieces of code carried over from Milestone 1 to improve readability and maintainability.
- **Milestone Planning:** Team discussions around goals, priorities, and expected deliverables for this milestone.
- **Technical Alignment:** Reviewed existing architecture and identified areas that may need improvement or extension moving forward.
- **Task Breakdown:** Began outlining tickets and responsibilities for upcoming weeks.

### **Kevin**
I built the "visual" engine for our system and the "edit" functionality.
While last week was about generating text for resumes, this week was about generating rich data for the portfolio website. I also added the ability for users to say "No, I want to write this myself," allowing them to override our auto-generated descriptions with their own words.

**Requirements addressed:**
-  https://github.com/COSC-499-W2025/capstone-project-team-9/pull/253 Implemented the base Portfolio Logic. Added the User Customization layer on top of PR #251
- https://github.com/COSC-499-W2025/capstone-project-team-9/pull/251 

---

### **Sami**
- ...

---

### **Eric**
This week, I focused on refactoring the CLI layer to improve maintainability, consistency, and testability without changing user-facing behavior. The work was intentionally split into two independent pull requests to keep changes scoped and easier to review.
In the first pull request, I refactored the CLI menu execution logic by introducing a shared menu runner abstraction. Previously, individual menus duplicated input loops and control flow, which made behavior inconsistent and harder to test. By centralizing menu execution logic, menus now follow a consistent structure and are easier to extend and reason about.
In the second pull request, I refactored the CLI display and output layer to standardize how success and error messages are rendered. A shared output utility was introduced to reduce duplicated formatting logic. Existing display helpers were hardened to safely handle both dictionary-based and object-based result structures, improving robustness across the CLI.
Throughout the refactor, existing behavior was preserved to remain compatible with current tests. Additional unit tests were added to validate display behavior and protect against regressions. All tests passed locally.

**GitHub Pull Requests (Evidence of Work)**
-PR1 – Refactor CLI menu execution logic:
[<<PR1 LINK>>](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/271)
-PR2 – Refactor CLI display/output layer and add tests:
[<<PR2 LINK>>](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/273)

**Additional Contributions**
-Reviewed teammates’ pull requests and provided feedback on code structure and test compatibility.
-Verified refactored CLI behavior through manual testing and full pytest runs.

---

### **Evan**
- ...
---

### **JinXi**
- ...

---

### **Ryan**
- ... 

---

### **Collaboration Highlights**
- **Code Freeze Coordination:** The team communicated effectively to ensure no risky changes were pushed to `main` this week.
- **Test Swapping:** Team members tested each other's modules to find edge cases that the original author might have missed.
- **Production Planning:** The team collaborated on the plan for the next milestone. 

### **Things to Work On / Reflection**
- **Semester Wrap-up:** The project is now effectively concluded. The team worked well to integrate a complex set of features (Auth, NLP, Analysis, Database) into a cohesive CLI tool.
- **Final Check:** Ensure all "TODO" comments are removed or addressed in the code.
- **Documentation:** Ensure the User Manual explains the final menu structure, as it changed recently.

### **Peer Evaluations** (Do not Skip this part, they were from last week, you need to change to this week)
| Reviewer | Reviewee | Focus Area |
|-----------|-----------|-------------|
| **Sami** | **Evan** | [incorporate evidence of sucess and related tests](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/246) |
| **Sami** | **Ryan** | [Enhance Project Analysis](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/243) |
| **Sami** | **Evan** | [add the ability to delete a project](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/249) |
| **Sami** | **Eric** | [Added custom résumé wording management API (save/list/clear).](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/244)) |
| **Sami** | **Jinxi** | [Implement Portfolio Formatter Logic](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/251) |
| **JinXi** | **Sami** | Issue #227-#230 (Project API Endpoints) |
| **JinXi** | **Sami** | Frontend - Login Page|
| **JinXi** | **Sami** | Simple Frontend|
| **JinXi** | **Sami** | API Endpoints Resume, Skills, Portfolio|
| **JinXi** | **Ryan** | Simple Bug fix|
| **Eric** | **Evan** | Main menu refactor [#270](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/270)|
| **Eric** | **Ryan** | Bug Fix for duplicate files [#266](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/266)|
| **Eric** | **Evan** | ranking persistance bug fix [#265](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/265)|
| **Ryan** | **JinXi** | Issue127-2: implement data isolation in portfolio feature https://github.com/COSC-499-W2025/capstone-project-team-9/pull/240|
| **Ryan** | **Jynxi** | Add a DB manage tool, and delete useless files [#238](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/240)|
| **Ryan** | **Sami** | API Endpoints Resume, Skills, Portfolio https://github.com/COSC-499-W2025/capstone-project-team-9/pull/239|
| **Ryan** | **Sami** | Simple Frontend [ #234](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/234)|
| **Ryan** | **Evan** |add the ability to delete a project [#249 ](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/249)|
| **Kevin**|**Ryan**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/243 Enhance project analysis
|**Kevin**|**Eric**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/244 Added custom résumé wording management API
|**Kevin**|**Eric**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/245 feat(resume): add evidence of success generation for projects
| **Evan** | **Sami** |https://github.com/COSC-499-W2025/capstone-project-team-9/pull/233 front end login|
| **Evan** | **Sami** |https://github.com/COSC-499-W2025/capstone-project-team-9/pull/231 api endpoints|
| **Evan** | **Eric** |https://github.com/COSC-499-W2025/capstone-project-team-9/pull/245 evidence of success|
| **Evan** | **Jinxi** |https://github.com/COSC-499-W2025/capstone-project-team-9/pull/241 user data isolation bug|
---

## **Next Steps**
### **Intermediate**
- **Capstone Part 2 (New Term):** - Discuss potential transition to a Web/GUI interface.
  - Explore deploying the database to a cloud provider.
  - Implement advanced LLM features for better project summarization.

---
## **Burnup Chart**

