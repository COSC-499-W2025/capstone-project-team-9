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

# Sprint Report – Term 2 Week 4 (2026/01/26 to 2026/02/01)

## **Overview**
This week was a major pivot point for the project, focusing heavily on AI Integration and Architectural Stabilization. The team successfully integrated the Gemini LLM API, enabling advanced project analysis capabilities. Simultaneously, a significant refactoring effort was undertaken to standardize the CLI menus and display utilities, reducing technical debt and improving code maintainability. We also finalized the Resume & Portfolio backend routes, ensuring the frontend has access to rich, formatted data.

## **Completed Work**
- AI Implementation: Fully integrated Google's Gemini API to power the "Deep Analysis" features, allowing the system to generate insights beyond simple static analysis.
- Backend Finalization: Completed the API wiring for the Resume and Portfolio features, fixing critical testing mocks and routing issues.
- CLI Refactoring: Overhauled the Command Line Interface to use shared utilities, resulting in cleaner code and a consistent user experience.
- Feature Completion: Finalized "Project Deletion" logic to work correctly within isolated environments.

### **Kevin**
Core Contribution: Finalized the backend integration for the Milestone 2 display logic.
Resolved complex testing failures by standardizing database mock objects to align with new SQL query structures.
**Requirements addressed:**
- https://github.com/COSC-499-W2025/capstone-project-team-9/pull/285, feat: register resume_portfolio router and fix project manager mock data
---

### **Sami**
This week I focused on implementing the new LLM for our project. I removed the previous Ollama setup and switched to Gemini, since it provides $300 in free credits for three months. I also built on Ryan’s PR that moved the full analysis into a private mode, reworking it to include an optional LLM-generated summary that is much more coherent and useful. Overall, the LLM is now fully implemented and everything is looking solid as the front end continues to come together. We also spent a good amount of time improving the back end, especially making the CLI menus more user friendly, which has been going well. One challenge was securely sharing the LLM API key, so for now Ryan and I are the only ones with access. Next week, I plan to continue refining the LLM implementation and start using it for resume generation as well.


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
- I wrote the code for pull requests 265, 270, 313 and 311
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/265
        - I wrote a bug fix that made sure when the ranking were edited that that the correct ordering was enured.
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/270
        - I refactored the console so that there are more sub menus making it easier to find things.
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/311
        - Then I refactored the front end with sub menus to make navigating it much easier
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/313
        - I also added the displaying of evidence of success and completion to the analysis on the front end for both local and external methods

- I reviewed the pull requests of four team members the last two weeks
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/312 for sami
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/267 for sami
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/283 for jinxi
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/303 for eric
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/269 for ryan
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/266 for ryan




### My Plan for next week
- I really need to work on testing our api endpoints
- I also want to look more into image and pdf analysis for files in our projects that we analyze

### Reflection
I think the last two weeks have gone really well is anything we are now starting to get to the point where we dont have a whole lot to do and will probably need to get creative to stay busy. I think our review process is quite good now and we are getting much less merges to the main that are casuing breaking changes. One thing as a group we could improve on is trying to remove unused code from our project as there is now quite a lot of it. I also think we need to start looking at our coverage stats again as some of them are getting low. We also need to consider moving beyond unit testing and start looking at deployment testing as we finish up our front end and get closer to deploying it.

Overall as an individual I am happy with the progress I made the last two weeks especially considering that there is not to much left to do.
---

### **JinXi**
This week I am keep developing the user data isolation feature.
- [Finished] Isolation in delete_insights feature, isolation in external service feature, isolation in user content feature.

#### issue developed:
[Issue127-6: make the project delete works in isolated environment](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/278)
The new data delete feature already fit the user isolated environment, this PR implement the isolation in cleanup_insights feature.
- change cleanup_insights and related functions to implement the user isolation
- Fix the front end API problem to make the delete front end features work.

[issue127-4: Implement data isolation in external service](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/282)
This PR implement the data isolation in external service feature.
- update the external_service_permissions data table, which use foreign key user_name as unique key to replace the old user_id.
- Update all other methods that use external_service_permissions data table to fix the new data base.
- update related tests
- Add a tool to update the external service permissions table

[issue127-7: implement data isolation in user consent](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/283)
Implement the data isolation in user_consent feature
- Change the user_consent data table, which user user_name as foreign key replace the user_id.
- Update the related functions to fit the new user_consent data base
- Update the API of user_consent to fit the changes
- small change in external service data table for pass the tests
- Let the logging system as the first initialized thing
- update tests in need.
  
#### PR reviewed: 
1. [Refactor CLI for new "Settings" Menu](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/252)
2. [ranking persistance bug fix](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/265)
3. [Bug Fix for duplicate files](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/266)
4. [Main menu refactor](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/270)
5. [Gemini API (LLM) Implenentation](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/272)
6. [Refactor: standardize CLI output and harden display utilities](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/273)
   
---

### **Ryan**
### What I completed this week
- The first thing that i completed this week was in relation to a bug that we found when doing peer evaluations. When a new user created an account and then added a file that another user had already uploaded, the code detected a duplicate file. THis meant that I had to alter the logic for dupicate detection to just the user that is logged in.
- Next, I worked on continuing to develop the fron end. I Worked off Evans PR and built the analysis to work more smoothly and differentiate the analysis based off of the users permissions
- Along with this just for fun i added in a mode where the user can switch from light mode to dark mode. It deos not add any functionality i just thought it would be fun to immplement
### Link to PR
- This is the link to the PR that i have made: [https://github.com/COSC-499-W2025/capstone-project-team-9/pull/243](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/266)
- this is the second link: [https://github.com/COSC-499-W2025/capstone-project-team-9/pull/242](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/274)
### What went well
- The bug fix went really well. From the peer evaluations, i was able to find the bug pretty fast and implement a few lines of code that resolved it.
- Secondly i am really enjoying building the front end / connecting the front end to the back end.
- Along with this, Sami and i got our LLM to completely work in the front end which is a great accomplishment. There still are some bugs but that will be reseolved in a later date
### what didnt go well
-I created a pull request at the same time as evan where i was chagning the front end, and then evan created a back end chage which rendered my PR useless, therefore i had to close it. I did reuse some of the code, but a lot of it needed to be changed.
### what i will work on next week
- As the main functionalities are still being connected from front end to back end, i will continue to work on this.
- I would like to get the permissions fully working on the front end this week and make sure that they are being enforced while the user is using the website.


### **Collaboration Highlights** 
- Backend & AI Unification: This week required tight coordination between the AI team (Sami) and the Backend team (Kevin). We successfully bridged the gap between the raw analysis logic and the user-facing API, ensuring that both static analysis and new Gemini-powered insights are accessible to the frontend.
- Refactoring Synchronization: Eric and Evan coordinated a major overhaul of the CLI architecture. By creating shared utilities (run_menu, display), they reduced code duplication across the project, which required careful merging to avoid breaking existing feature branches.
- Integration Testing: The team worked together to debug environment isolation issues (specifically Jinxi's fix for project deletion), ensuring that our test suites remain reliable even as we add complex external dependencies like the LLM API.

### **Things to Work On / Reflection**
- Managing Technical Debt: The Refactoring was necessary but painful. It highlighted that we should have standardized our CLI and Output utilities earlier in the project. Moving forward, we should enforce these standards in code reviews to prevent divergence.
- API Documentation: With the addition of the new Resume and Portfolio endpoints, we need to ensure our API documentation (Swagger/OpenAPI) is kept up to date so the frontend team knows exactly what data structures to expect.

### **Peer Evaluations** 
| Reviewer | Reviewee | Focus Area |
|-----------|-----------|-------------|
| **Sami** | **Eric** | [Refactor CLI menus using shared run_menu utility ](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/271)|
| **Sami** | **Ryan** | [Frontend Changes + Analysis Fix](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/274)|
| **JinXi** | **Sami** | Refactor CLI for new "Settings" Menu |
| **JinXi** | **Sami** | Gemini API (LLM) Implenentation |
| **JinXi** | **Evan** | ranking persistance bug fix |
| **JinXi** | **Evan** | Main menu refactor |
| **JinXi** | **Ryan** | Bug Fix for duplicate files |
| **JinXi** | **Eric** | Refactor: standardize CLI output and harden display utilities |
| **Eric** | **Evan** | Main menu refactor [#270](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/270)|
| **Eric** | **Ryan** | Bug Fix for duplicate files [#266](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/266)|
| **Eric** | **Evan** | ranking persistance bug fix [#265](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/265)|
| **Ryan** | **Kevin** | feat: register resume_portfolio router and fix project manager mock data #[285](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/285) |
| **Ryan** | **Sami** | Gemini Analysis [#284](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/284) |
| **Ryan** | **Jynxi** | Issue127-6: make the project delete works in isolated environment #278 [#278](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/278) |
| **Ryan** | **Sami** | Gemini API (LLM) Implenentation #272 [#272](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/272)|
| **Ryan** | **Eric** | Refactor CLI menus using shared run_menu utility #271 [#271](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/271) |
| **Ryan** | **Evan** | Main menu refactor #270 [#270](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/270)|
| **Ryan** | **Sami** | Identify Collaborators Fix #267 [#267](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/267) |
| **Ryan** | **Evan** | ranking persistance bug fix #265 [#265](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/265) |
| **Kevin**|**Ryan**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/274 Frontend Changes + Analysis Fix|
|**Kevin**|**Sami**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/284 Gemini Analysis|
|**Kevin**|**Eric**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/273 Refactor: standardize CLI output and harden display utilities|
| **Evan** | **Sami** | https://github.com/COSC-499-W2025/capstone-project-team-9/pull/267 |
| **Evan** | **ryan** | https://github.com/COSC-499-W2025/capstone-project-team-9/pull/266 |
| **Evan** | **ryan** | https://github.com/COSC-499-W2025/capstone-project-team-9/pull/269 |
| **Evan** | **Jinxi** | https://github.com/COSC-499-W2025/capstone-project-team-9/pull/283 |
---

## **Next Steps**
### **Intermediate**
- Frontend Polish: Now that the API is returning formatted data, the next immediate step is to finalize the React components for the Portfolio Dashboard and Resume Builder to render this data beautifully.
- Prompt Engineering: Refine the system prompts used by the Gemini Analyzer to ensure the "Deep Analysis" provides actionable, specific feedback rather than generic coding advice.
- Milestone 2 Preparation: Finalize all feature branches and prepare the codebase for the Milestone 2 release and demonstration.

---
## **Burnup Chart**
<img width="985" height="501" alt="image" src="https://github.com/user-attachments/assets/dd584049-2348-4e66-891a-66803ea1a2c9" />
<img width="981" height="469" alt="image" src="https://github.com/user-attachments/assets/5a47cae0-f44d-4a37-b553-00a2d5bc4e78" />

# Sprint Report – Term 2 Week 5 (2026/02/02 to 2026/02/08)

## **Overview**
- Week 5 of term 2 was overall a good week. It was a slow week as many of us were busy with midterms so none of us were able to put in as much time as we would want to in to capstone. We still completed some tasks that needed to be done such as adding in more data isolation for personal users, and adding in the feature of "create an account" to the front end. With the completion of the create an account, the log in page is fully funcitonal. and now all of our attention can go to implementing the mileston 1 requirements in to our front end. We also refactored a lot of our tests as they were becoming redundant and caused our time complexity to be quite high when we ran them. Along with the test refactoring some API functions were refactored. 

## **Completed Work**
- For links or our completed work, refer to the peer evaluations tab we have created.

### **Kevin**
Logic Repairs:
Fixed a bug in ProjectAnalyzer line counting tests where the mock data format (10\nlines) was causing integer conversion errors.
Corrected the patching logic for ExternalServicePermission to resolve AttributeError crashes.

Test Infrastructure (tests/conftest.py):
Created a shared fixture file that automatically provides mock data to any test that needs it.
Significantly reduced code duplication in test_portfolio_formatter.py and test_project_analyzer.py.

https://github.com/COSC-499-W2025/capstone-project-team-9/pull/310 Refactor with tests

---

### **Sami**

This week, I focused on further implementing our LLM for the rankings feature by developing and testing the core logic, though I was unable to refactor the code or fully integrate the feature into the frontend. This ended up working out well, as the frontend was undergoing a refactor anyway, and adding the rankings LLM at that time could have caused conflicts. The LLM implementation is progressing smoothly overall, the frontend is starting to come together, and pull request reviews were extremely quick this week (PRs:
 and https://github.com/COSC-499-W2025/capstone-project-team-9/pull/312
). There were no major coding-related issues this week, with my main challenge being the workload from other classes. Next week, I plan to focus on properly integrating the LLM rankings feature into the frontend and writing documentation for the new additions, as the project currently feels somewhat disorganized and better documentation could help bring everything together.

---

### **Eric**
**Weekly Goals Recap**  
This week, I focused on improving the robustness and consistency of the backend API layer by standardizing error handling and aligning all related components with a clear API contract. The work was intentionally split into two independent pull requests to keep changes scoped and easier to review.

In the first pull request, I refactored API error handling across all FastAPI routes by introducing a unified error response schema. Previously, different endpoints returned errors in inconsistent formats, which made client-side handling and testing brittle. A centralized HTTP exception handler was added to ensure all API errors follow a consistent structure while preserving existing HTTP status codes.

In the second pull request, I updated the API client and refactored API endpoint tests to align with the new error contract. Tests were changed to assert against the defined response schema rather than raw framework-specific fields, effectively turning them into contract tests. This improves long-term maintainability and reduces coupling between implementation details and tests.

All changes were verified through full pytest runs, and existing behavior was preserved throughout the refactor.

**GitHub Pull Requests (Evidence of Work)**

- **PR1 – cli: stabilize input/output handling and add CLI tests#303**  
  [<<PR1 LINK>>](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/303)

- **PR2 – refactor(api): standardize error responses and align tests#304**  
  [<<PR2 LINK>>](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/304)

**Additional Contributions**
- Refactored API endpoint tests to validate a stable API contract rather than raw response details.
- Ensured consistent error behavior across all API routes without introducing breaking changes.
- Reviewed related backend code paths to confirm consistency and robustness.
---

### **Evan**
- I wrote the code for pull requests 265, 270, 313 and 311
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/265
        - I wrote a bug fix that made sure when the ranking were edited that that the correct ordering was enured.
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/270
        - I refactored the console so that there are more sub menus making it easier to find things.
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/311
        - Then I refactored the front end with sub menus to make navigating it much easier
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/313
        - I also added the displaying of evidence of success and completion to the analysis on the front end for both local and external methods

- I reviewed the pull requests of four team members the last two weeks
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/312 for sami
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/267 for sami
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/283 for jinxi
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/303 for eric
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/269 for ryan
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/266 for ryan

### My Plan for next week
- I really need to work on testing our api endpoints
- I also want to look more into image and pdf analysis for files in our projects that we analyze

### Reflection
I think the last two weeks have gone really well is anything we are now starting to get to the point where we dont have a whole lot to do and will probably need to get creative to stay busy. I think our review process is quite good now and we are getting much less merges to the main that are casuing breaking changes. One thing as a group we could improve on is trying to remove unused code from our project as there is now quite a lot of it. I also think we need to start looking at our coverage stats again as some of them are getting low. We also need to consider moving beyond unit testing and start looking at deployment testing as we finish up our front end and get closer to deploying it.

Overall as an individual I am happy with the progress I made the last two weeks especially considering that there is not to much left to do.
---

### **JinXi**
This week I am keep developing the user data isolation feature.
- [Finished] Isolation in user_preference feature.

### issue developed:
[Issue127-8: implement data isolation in user preference](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/305)
This PR is for implement the user data isolation in user preference relate functions
- Update the user_preferences table which use user_name as foreign key.
- Remove redundancy codes from collaborative_storage.py as those codes already be implement in user_preferences.py.
- Update all other functions which relate to user_preference table to transfer user_name or current_user parameter.
- Update the tests in needs.
- Add a tool called 'migrate_user_preferences_to_username.py' under developTools folder to update the database in other PC.

### PR reviewed: 
1. [cli: stabilize input/output handling and add CLI tests](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/303)
2. [refactor(api): standardize error responses and align tests](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/304)
3. [Added function to create an account](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/309)
4. [Refactor with tests](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/310)

---

### **Ryan**
### What I completed this week
- What I worked on this week was exactly what i had talked about lask week. I added the ability for a user to create an account in the front end. this means that the login page is now completely connected to the backend and the database.
- This is very exciting as now all we have to work in is actuallly implementing the rest of the milestone requiremnts
### Link to PR
- This is the link to the PR that i have made: https://github.com/COSC-499-W2025/capstone-project-team-9/pull/309
### What went well
- The coding went really well. Although there are was not much that was added this week functionality wise, this was something that needed to be added for new users who would use our system
### what didnt go well
- This week was extremely busy school wise. there were multiple midterms that i had to study for so i was not able to dedicate as much time to capstone that i usually would.
### what i will work on next week
- I would like to get the permissions fully working on the front end this week and make sure that they are being enforced while the user is using the website.
- This means that there user consent will actually be enforced. If user does not allow LLM, then there should be no LLM option, or it will send an error message is someone tries to use it with no consent

---
### **Collaboration Highlights** 
- This week we met up in class and were able to divide the rest of the work that we needed to complete for the rest of the milestone which was great.
- Along with this we were able to securely distribute the API key that we will be using for our LLM. this means that all of our group memebers are able to use Gemini and generate LLM summaries of project. This was a great accomplishment
### **Things to Work On / Reflection**
- This was a slow week for work as we are al very busy with midterms. This means that we must be more on top of our work earlier on in to the week and be able to communicate better and more efficiently with eachother.
- There are a lot of PRs that are being pushed that are not getting reviewed as fast as we would like. this can cause some merge conflicts. if we are not careful
- Yet again we must ensure that we are doing our work before late sunday night.
### **Peer Evaluations** 
| Reviewer | Reviewee | Focus Area |
|-----------|-----------|-------------|
| **Sami** | **Evan** | frontend menu refactor https://github.com/COSC-499-W2025/capstone-project-team-9/pull/311
| **JinXi** | **Kevin** | Refactor with tests
| **JinXi** | **Ryan** | Added function to create an account
| **JinXi** | **Eric** | refactor(api): standardize error responses and align tests
| **JinXi** | **Eric** | cli: stabilize input/output handling and add CLI tests
| **Eric** | **Jinxi** | Issue127-8: implement data isolation in user preference[#305](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/305)|
| **Eric** | **Kevin** | Refactor with tests[#310](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/310)|
| **Eric** | **Ryan** | Added function to create an account[#309](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/309)|
| **Ryan** | **Kevin** | Refactor with tests https://github.com/COSC-499-W2025/capstone-project-team-9/pull/310 |
| **Ryan** | **Jynxi** | Issue127-8: implement data isolation in user preference#305 https://github.com/COSC-499-W2025/capstone-project-team-9/pull/305 |
|**Kevin**|**Sami**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/312 Gemini Rankings Logic |
|**Kevin**|**Eric**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/304 refactor(api): standardize error responses and align tests|
| **Evan** | **Sami** | https://github.com/COSC-499-W2025/capstone-project-team-9/pull/312 |
| **Evan** | **Eric** | https://github.com/COSC-499-W2025/capstone-project-team-9/pull/303 |
---

## **Next Steps**
### **Intermediate**
- The main next steps are to completely finish all of the milestone 2 requirements. We are very close to completeing this but we must ensure that they are all finished to our liking.
- We will continue to develop the front end and connect it to our backend
- We will need to refactor more of our tests, and code as there is beggining to be a lot more redundant code. This is Ok right now but we do not want this to become a problem in our near future

---
## **Burnup Chart**
<img width="991" height="497" alt="image" src="https://github.com/user-attachments/assets/b14fab11-16b5-4f9c-bfe0-b3f6f0478539" />
<img width="992" height="495" alt="image" src="https://github.com/user-attachments/assets/3cf7bd97-decc-457a-8019-d4a516caff06" />

# Sprint Report – Term 2 Week 6 (2026/02/09 to 2026/02/15)

## **Overview**
This week focused on "polishing" and "feature completion" for Milestone 2. We delivered several high-impact features, including the AI Ranking System, Incremental Project Updates, and Thumbnail Support, moving the application from a functional prototype to a feature-rich product. We also addressed technical debt by replacing raw print statements with a standardized logging system and ensuring the frontend correctly initializes the database structure upon startup.

## **Completed Work**
- For links or our completed work, refer to the peer evaluations tab we have created.

### **Kevin**
Core Contribution: Backend Observability & Logging Refactor.
Replace printing with logging (#325): Refactored the backend to use a standardized logging module instead of raw print statements. Created src/common/logger.py and updated project_analyzer.py, portfolio_formatter.py, and API routes. This enables proper severity filtering (INFO vs ERROR) and improves server log manageability.

---

### **Sami**
### What I completed this week
- I implemented the Gemini-powered project ranking feature so it works in both backend and frontend.
- Backend: Added src/analysis/gemini_ranker.py. A GeminiRanker gathers each project’s code snippets, sends a comparative “rank these projects” prompt to Gemini, and parses the JSON response into a best-to-worst list with scores, strengths/weaknesses, and overall reasoning. Added POST /api/projects/rank-gemini and a convenience function rank_projects_with_gemini(user_name).
- Tests: Added tests/test_gemini_ranker.py for ranking, parsing, retries, data gathering, and snippet logic. 
- Frontend: Minimal dashboard changes: new menu item “7. AI Rank (Gemini)” under Ranking Tools, a small view panel with description and “Rank with Gemini” button, and a JS function that calls the API and displays the ranked list plus reasoning.

- https://github.com/COSC-499-W2025/capstone-project-team-9/pull/324
- https://github.com/COSC-499-W2025/capstone-project-team-9/pull/312

### What went well
Implementing the ranker and wiring it to the frontend went well. The backend stays small and the UI is a small addition (one menu item, one panel, one handler) so it fits the existing dashboard without a rework.

### What didn’t go well
This week was very busy with school; multiple midterms meant less time for capstone than usual.

### What I will work on next week
I want to get permissions fully working on the front end and enforced while using the site: user consent for the LLM should be enforced so that if a user does not allow the LLM, there is no LLM option (or an error is shown if someone tries to use it without consent).

---

### **Eric**
I did not do PR this week and upload the Pull Request in the Reading Break, but I did think about how the front-end design and api refactoring.
---

### **Evan**
# Week 6 and 7 Term 2 Project Update

### This Sprints Progress
- I wrote the code for pull requests 314, 333 and 334
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/314
        - This got the thumbnail api working and displaying in the front end
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/333
        - I wrote a whole bunch of tests to ensure coverage for our api endpoints
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/334
        - To get more in depth local analysis I added photo and pdf extraction

- I reviewed the pull requests of four team members the last two weeks
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/331 for eric
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/328 for sami




### My Plan for next week
- We need to discuss as a group our plan going forwards for milestone 3 of what we already meet and what we do not as we already have a lot of the front end implemented, therefore we need to discuss before starting work on milestone 3.

### Reflection
I think the last two weeks went really well as much as you can hope for. We have our api functionality as good as one can wish and also our front end mostly done. I think as a group we have worked well as a team for the most part but maybe didnt work on the milestone 2 presentation as equally as I would have hoped which is somethign we can hopefully improve on for next milestone.
---

### **JinXi**
This week I am developing the milestone2 features.
- [Processing] Customize and save information about a portfolio showcase project

#### issue developed:
[isssue209-1: implement customize and save information about a portfolio showcase-backend](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/317)
This PR implement the back end codes for “customize and save information about a portfolio showcase" feature
- Add a new data table called ”portfolio_customizations“ to store customization project things for each user, and also add it' CRUDs.
- Add new schemas for Portfolio Customization Request/Response.
- Update the portfolio manager in need.
- Update the router and api things to expose portfolio customization feature to front end
- Add a back end UI for this new feature.

[Test for PR #317](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/318)
This PR is the test part of the PR#317, should be merged after that.

#### PR reviewed: 
1. [Incremental additions](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/322)
2. [initialize tables in front end](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/323)
3. [AI Rankings Implementation](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/324)
4. [Replace printing with logging](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/325)
---

### **Ryan**
### What I completed this week
- I have implemeted the final milestone requiremnt that i realized that we missed. This was needing to get done so i am happy that it is finally working. It is implemeted so that it will work in the back and and the front end together.
- all milestone requirements are now implemented
- Along with this i have implemented the feature that all database tables will be initialized when the front end gets set up. This has been a hassle and has been nedding to get done
### Link to PR
- This is the link to the PR that i have made: [https://github.com/COSC-499-W2025/capstone-project-team-9/pull/309](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/322)
- second link https://github.com/COSC-499-W2025/capstone-project-team-9/pull/323
### What went well
- The coding went really well. This was a good week to coomplete the final requirement. It was partially compelted but needed the final push.
- along with this i feel as though there have been some things that have been needing to get done that are now finally finished
### what didnt go well
- This week was extremely busy school wise. there were multiple midterms that i had to study for so i was not able to dedicate as much time to capstone that i usually would.
### what i will work on next week
- I would like to get the permissions fully working on the front end this week and make sure that they are being enforced while the user is using the website.
- This means that there user consent will actually be enforced. If user does not allow LLM, then there should be no LLM option, or it will send an error message is someone tries to use it with no consent
---
### **Collaboration Highlights** 
- Backend & Frontend Sync: The implementation of Thumbnails (#314) and Table Initialization (#323) required close collaboration to ensure the API endpoints met the exact needs of the React frontend.
- AI Integration: The AI Ranking implementation (#324) involved connecting the backend GeminiRanker logic with the frontend display, requiring coordination between Sami and Kevin to ensure data structures matched.

### **Things to Work On / Reflection**
- Log Management: With the new logging system in place (#325), we need to ensure we are actually monitoring these logs during development to catch silent failures.
- Testing AI Features: Now that AI Rankings are live, we need to manually verify the quality of the scores across different types of projects to ensure the prompts are effective.

### **Peer Evaluations** 
| Reviewer | Reviewee | Focus Area |
|-----------|-----------|-------------|
| **Sami** | **Evan** |
| **JinXi** | **Evan** | https://github.com/COSC-499-W2025/capstone-project-team-9/pull/322 |
| **JinXi** | **Ryan** | https://github.com/COSC-499-W2025/capstone-project-team-9/pull/323 |
| **JinXi** | **Sami** | https://github.com/COSC-499-W2025/capstone-project-team-9/pull/324 |
| **JinXi** | **Kevinc** | https://github.com/COSC-499-W2025/capstone-project-team-9/pull/325 |
| **Eric** | **Jinxi** | |
| **Eric** | **Kevin** | |
| **Eric** | **Ryan** | |
| **Ryan** | **Kevin** |  |
| **Ryan** | **Jynxi** |  |
|**Kevin**|**Sami**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/324 #324 |
|**Kevin**|**Ryan**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/323 #323 |
| **Evan** | **Eric** |  https://github.com/COSC-499-W2025/capstone-project-team-9/pull/331 |
| **Evan** | **Sami** | https://github.com/COSC-499-W2025/capstone-project-team-9/pull/328 |
---

## **Next Steps**
### **Intermediate**
- Milestone 2 Final Polish: Ensure all UI elements (like the new Thumbnails and Rankings) are aligned and responsive.
  
- Peer Testing: Run a full team test session to verify the "Incremental Additions" feature works seamlessly without corrupting existing data.
  
- Documentation: Update the README and API docs to reflect the new endpoints and environmental variables (e.g., Logging config).

---
## **Burnup Chart**
<img width="1047" height="660" alt="image" src="https://github.com/user-attachments/assets/4bb9ee0a-cbad-4861-8f21-c52977912ae8" />

# Sprint Report – Term 2 (2026/02/16 to 2026/02/22) Reading Break

## **Overview**
This week focused heavily on system stabilization, API robustness, and finalizing frontend integrations as we approach the end of Milestone 2. Our primary achievements included implementing comprehensive API documentation and testing, adding backend request tracking middleware, and completing the user-facing customization features for the portfolio dashboard. We also resolved critical bugs in the analysis pipeline and frontend event handling to ensure a smooth user experience.

## **Completed Work**
- https://github.com/COSC-499-W2025/capstone-project-team-9/pull/322 Incremental additions
- https://github.com/COSC-499-W2025/capstone-project-team-9/pull/328 API Tests
- https://github.com/COSC-499-W2025/capstone-project-team-9/pull/329 Add API documentation
- And more and more
  
### **Kevin**
- **Centralized Constants (DRY Principle):**
    * Extracted lists of common project suffixes (like `.zip`, `-main`, `-master`) into a single source of truth.
    * Replaced duplicated string-stripping and name-formatting logic across multiple files to pull from this central list instead.
- **Database Operation Robustness (`resume_manager`):**
    * Added defensive programming checks to the portfolio customization logic. 
    * The backend now gracefully handles `None` or missing data payloads coming from the frontend, preventing unhandled exceptions and database crashes.
- https://github.com/COSC-499-W2025/capstone-project-team-9/pull/332 #322
---

### **Sami**

A new ranking endpoint, thorough testing, and a straightforward dashboard integration with a "AI Rank (Gemini)" option that shows ranked results with reasoning were all added throughout the last few weeks as I integrated the Gemini-powered project rating feature across the frontend and backend. In addition, I filmed a video demo, finished and documented the API, added comprehensive endpoint testing, and finished the Milestone 2 presentation. Despite my time constraints due to the midterms, the ranker worked flawlessly, and I intend to completely enforce frontend user authorization for all LLM features the next week.

---

### **Eric**
**Weekly Goals Recap**  
Although this week was designated as Reading Week, I continued improving the frontend dashboard layer to enhance code quality, maintainability, and system stability without introducing new features.

The work focused on strengthening the frontend structure while ensuring compatibility with existing automated tests. Changes were intentionally scoped and validated locally to avoid unintended regressions.

In the first pull request, I refactored the dashboard frontend to standardize API calls through a unified apiRequest wrapper. Previously, some actions (upload, thumbnail addition, merge operations) performed duplicate or inconsistent network requests. This refactor eliminated redundant fetch calls and ensured consistent request handling across all user actions.

In the second pull request, I improved dashboard state restoration logic to ensure the active view and selected project are reliably restored after page reload. During this refactor, I also evaluated event handling structure and ensured compatibility with the existing frontend smoke test by preserving the inline selectProject(event, ...) handler expected by the test suite.

All changes were verified through local pytest runs, and no breaking changes were introduced.

**GitHub Pull Requests (Evidence of Work)**

- **PR1 – feat(api): add request context middleware with request-id and timing headers#330**  
  [<<PR1 LINK>>](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/330)

- **PR2 – Resotre inline onclick for selectProject to satisfy existing frontend smoke test#331**  
  [<<PR2 LINK>>](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/331)

**Additional Contributions**
- Removed redundant network requests to improve correctness and reduce unnecessary backend load.
- Standardized frontend API interaction patterns for better maintainability.
- Strengthened dashboard state persistence (active view + selected project restoration).
- Ensured all frontend smoke tests pass locally after refactoring.
- Maintained backward compatibility with existing test expectations.
---

### **Evan**
Week 6 and 7 Term 2 Project Update

### This Sprints Progress
- I wrote the code for pull requests 314, 333 and 334
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/314
        - This got the thumbnail api working and displaying in the front end
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/333
        - I wrote a whole bunch of tests to ensure coverage for our api endpoints
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/334
        - To get more in depth local analysis I added photo and pdf extraction

- I reviewed the pull requests of four team members the last two weeks
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/331 for eric
    - https://github.com/COSC-499-W2025/capstone-project-team-9/pull/328 for sami

### My Plan for next week
- We need to discuss as a group our plan going forwards for milestone 3 of what we already meet and what we do not as we already have a lot of the front end implemented, therefore we need to discuss before starting work on milestone 3.

### Reflection
I think the last two weeks went really well as much as you can hope for. We have our api functionality as good as one can wish and also our front end mostly done. I think as a group we have worked well as a team for the most part but maybe didnt work on the milestone 2 presentation as equally as I would have hoped which is somethign we can hopefully improve on for next milestone.

---

### **JinXi**

#### issue developed:
[issue209-2：implement frontend of customize and save information about a portfolio showcase project](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/326)
This PR add a front end UI for customize portfolio feature based on issue209's API.

[bug-fix: the current analysis project function not work](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/327)
This PR fix the BUG of analyze project feature not work on both front and back end which caused by wrong file path.
- modify the project_analyzer.py to fit the user data isolation
- modify menus.py to transfer user_name when use analyze function
- modify upload_file.py file to ensure right path when use analyze function in backend
- Update tests in need

#### PR reviewed: 
1. [feat(api): add request context middleware with request-id and timing headers](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/330)
2. [Refactor with hardcode constants](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/332)
---

### **Ryan**

---
### **Collaboration Highlights** 
- **Full-Stack Synchronization:** The implementation of the Portfolio Customization (#326) required everyone to work closely together, using the newly generated API documentation (#329) as a bridge to ensure the React forms sent the exact payload the backend expected.
- **Testing & Stability:** Bug fix (#327) and API tests (#328) were crucial for unblocking the rest of the team. We collaborated to ensure the backend modifications (#330, #332) didn't break any of these newly established test parameters.

### **Things to Work On / Reflection**
- **Integration Bottlenecks:** This week showed that whenever we change backend data structures or add middleware, the frontend tests (like the smoke tests fixed in #331) can easily break. We need to improve our end-to-end testing pipeline so these mismatches are caught in CI/CD before merging.
- **Milestone Wrap-Up:** With Milestone 2 closing, we need to ensure all features are fully documented in the `README` and that our deployment environment is perfectly mirroring our newly tested API behavior.

### **Peer Evaluations** 
| Reviewer | Reviewee | Focus Area |
|-----------|-----------|-------------|
| **Sami** | **Jinxi** | https://github.com/COSC-499-W2025/capstone-project-team-9/pull/327 |
| **Sami** | **Ryan** | https://github.com/COSC-499-W2025/capstone-project-team-9/pull/322 |
| **JinXi** | **Eric** |feat(api): add request context middleware with request-id and timing headers(https://github.com/COSC-499-W2025/capstone-project-team-9/pull/330) |
| **JinXi** | **Kevin** |Refactor with hardcode constants(https://github.com/COSC-499-W2025/capstone-project-team-9/pull/332) |
| **Eric** | **Jinxi** | issue209-2：implement frontend of customize and save information about a portfolio showcase project#326 (https://github.com/COSC-499-W2025/capstone-project-team-9/pull/326)|
| **Eric** | **Kevin** | bug-fix: the current analysis project function not work #327 (https://github.com/COSC-499-W2025/capstone-project-team-9/pull/327)|
| **Eric** | **Jinxi** | Refactor with hardcode constants #332 (https://github.com/COSC-499-W2025/capstone-project-team-9/pull/332)|
| **Ryan** | **Kevin** |  |
| **Ryan** | **Jynxi** |  |
|**Kevin**|**Eric**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/331 #331 |
|**Kevin**|**Jinxi**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/327 #327 |
| **Evan** | **Eric** |  https://github.com/COSC-499-W2025/capstone-project-team-9/pull/331 |
| **Evan** | **Sami** | https://github.com/COSC-499-W2025/capstone-project-team-9/pull/328 |
---

## **Next Steps**
### **Intermediate**
- **Milestone Demo:** Support the frontend team in ensuring all API calls for the final demo run quickly and without errors.
- **Performance Monitoring:** Keep an eye on the new execution time headers during large zip uploads to see if our Gemini or Local analyzers are creating bottlenecks.
---
## **Burnup Chart**
<img width="1036" height="637" alt="image" src="https://github.com/user-attachments/assets/dce686ec-fc5b-4b30-bd94-5f79e9d153f5" />
<img width="1054" height="619" alt="image" src="https://github.com/user-attachments/assets/44617a48-f416-4523-98ea-62cd4d3d68d4" />

# Sprint Report – Term 2 Week 8 (2026/02/23 to 2026/03/01) 

## **Overview**
This sprint heavily focused on application resiliency, error management, and frontend stability. We implemented a major architectural upgrade on the backend to catch and standardize all server errors, preventing unexpected crashes from leaking raw stack traces to the frontend. On the client side, we standardized how the application communicates with the API, patched unsafe response handling, and improved the accessibility and request logic on the authentication pages.

## **Completed Work**
- https://github.com/COSC-499-W2025/capstone-project-team-9/pull/338
- https://github.com/COSC-499-W2025/capstone-project-team-9/pull/336
- https://github.com/COSC-499-W2025/capstone-project-team-9/pull/335
- More and More
  
### **Kevin**
- Core Contribution: Backend Error Resilience & Architecture.
- **Details:**
    - **Implement Global Exception Handling (#342):** Intercepted all unhandled server exceptions and FastAPI HTTP errors. Structured the response into a clean, predictable JSON format and automatically injected the `X-Request-ID` into the payload for instant trace-ability in our server logs. https://github.com/COSC-499-W2025/capstone-project-team-9/pull/342.

---

### **Sami**

---

### **Eric**
**Weekly Goals Recap**  
This week, I focused on strengthening the frontend layer of the system by improving reliability, accessibility, and request handling consistency without introducing new features.

The work was intentionally separated into two independent pull requests to maintain clear scope boundaries and reduce review complexity. All changes were scoped carefully and validated locally to avoid unintended regressions.

In the first pull request, I refactored the dashboard frontend to standardize API interaction patterns and eliminate unsafe response handling. Previously, some functions relied on inconsistent response structures and direct response.ok checks outside centralized request logic. I introduced a unified request wrapper and refactored dependent logic to use structured return values. I also reduced duplicated UI rendering logic by extracting reusable helper functions.

In the second pull request, I improved the authentication page (index.html) by enhancing accessibility and hardening request handling. I added ARIA live regions for login and registration feedback messages and refined username input behavior to prevent unintended browser auto-capitalization and spellcheck interference. Additionally, I introduced a centralized postJson() helper to standardize authentication requests (login, register, logout), reducing duplicated fetch logic and improving consistency.

All changes were verified through local pytest runs and manual browser testing, and no breaking changes were introduced.

**GitHub Pull Requests (Evidence of Work)**

- **PR1 – Standardize dashboard API handling and improve frontend reliability #335**  
  [<<PR1 LINK>>](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/335)

- **PR2 – Improve auth page accessibility and request handling #336**  
  [<<PR2 LINK>>](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/336)

**Additional Contributions**
- Standardized frontend API wrappers for consistent { ok, data, status } handling.
- Eliminated unsafe response usage patterns to prevent potential runtime errors.
- Reduced duplicated network request logic across dashboard and authentication pages.
- Improved accessibility through ARIA live regions and refined input behavior.
- Added frontend smoke tests to guard against regression.
- Ensured compatibility with existing test expectations.
---

### **Evan**

---

### **JinXi**
This week I fixed a bug and refactor the front end.

#### issue developed:
[Update dashboard.html](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/338)

A pretty small fix on front end. Which fix the bug of non auto close of dropdown menus. Only change front end things.

[Jinxi/t2 week8/refactor/front end css refactor](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/340)

This PR do the refactor in front end part.
- Remove <style> parts form two front end html files.
- Put all css code into three .css files and let html files to use them
- This improve the Maintainability and code readability

#### PR reviewed: 
1. [Standardize apiCall and fix unsafe response handling](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/335)
2. [Improve auth page accessibility and request handling](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/336)

---

### **Ryan**

---
### **Collaboration Highlights** 
**Frontend-Backend Contract:** The implementation of the Global Exception Handler (#342) was directly paired with the standardized `apiCall` fixes (#335). Because the backend now guarantees a standardized error JSON, the frontend can safely handle failures without the application breaking.

### **Things to Work On / Reflection**
- With the new global error handlers and standardized API calls in place, we need to dedicate time next sprint to write integration tests that intentionally trigger these errors to verify the fail-safes hold up in production.

### **Peer Evaluations** 
| Reviewer | Reviewee | Focus Area |
|-----------|-----------|-------------|
| **Sami** | **Jinxi** |  |
| **Sami** | **Ryan** |  |
| **JinXi** | **Eric** |Standardize apiCall and fix unsafe response handling(https://github.com/COSC-499-W2025/capstone-project-team-9/pull/335) |
| **JinXi** | **Eric** |Improve auth page accessibility and request handling(https://github.com/COSC-499-W2025/capstone-project-team-9/pull/336) |
| **Eric** | **Jinxi** | Update dashboard.html#338 (https://github.com/COSC-499-W2025/capstone-project-team-9/pull/338)|
| **Eric** | **Jinxi** | Jinxi/t2 week8/refactor/front end css refactor#340 (https://github.com/COSC-499-W2025/capstone-project-team-9/pull/340)|
| **Ryan** | **Kevin** |  |
| **Ryan** | **Jynxi** |  |
|**Kevin**|**Eric**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/335 |
|**Kevin**|**Jinxi**| https://github.com/COSC-499-W2025/capstone-project-team-9/pull/338 |
| **Evan** | **Eric** |   |
| **Evan** | **Sami** | |
---

## **Next Steps**
### **Intermediate**
- Prepare fot Milestone 3, Most of the refactor has completed.

---
## **Burnup Chart**
