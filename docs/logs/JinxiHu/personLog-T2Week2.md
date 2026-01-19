# T2Week 2: 2026/1/12 – 2026/1/18

## Tasks Worked On
![Week15 Project Log](img/T2week2.png)

---

## Weekly Goals Recap
This week, our team starting development of the milstone 2 thing. We develop the Fast API, custom words in resume generate function, and implement the data isolation. 

---

## My Contributions
This week I am developing the user data isolation feature.
- [Finished] Change the codes which related with project manage function, this implement the project data isolation between different users.
- [Ongoing-need fix] Change other data table which need to be associate with user_information and update other codes in need.

### issue developed:
[issue127-1:implement user data isolation on project manager (also update all other files which use project_manager.py)](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/200)
- This PR update the project_manager.py to implement user data isolation, and also do other needed change to ensure the system still works.
1. Update the project_manager.py, add user_name as parameters for all functions which use the updated_file data table.
2. Update other files such as project_display.py, project_summarize.py, profolio_manager.py, project_ranking.py and so on. Which add user_name as parameters into them, and update functions in need. (This Update ensure the system can work.)
3. Update codes of resume generate and portfolio functions, let them user logged in user's name as permeate instead of 'defult_user'.
4. Change some variable name 'user_id' into 'user_name', this is for reduce naming conflicts.
5. Update the test files of all changed files.

(**Still in develop**)[issue127-2: update other data table which include user id to connect them with user information table)](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/204)
- Update the data table external_service_permissions, user_consent, user_preferences to implement user data isolation, and also update related codes.
1. change files such as consent_manager.py, service_config.py, permission_manager.py, external_service_promopt.py and so on. Add user_name as parameter to replace the old hard coded user_id.
2. write migrations.py to auto update data base.
3. change the system initial order, put the login page to most first thing.
update the tests files.
4. !! IMPORTANT: This pr change the data base lot, not encourage to merge it before the evaluation !!
  
### PR reviewed: 
1. [Feature: Resume content selection (projects & skills)](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/197)
2. [feat: support custom resume wording per project](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/202)

### Went well:
Success change the old database and implement the user data isolation based on the new data base.
### Not well:
Start my work too late, so other people do their work based on the old data base, this cause problems.
### Next cycle:
Fix the problems that caused by my development, and finish next step of data base develop beform all other people start work.
