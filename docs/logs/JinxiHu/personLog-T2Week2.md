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
  
### PR reviewed: 
1. [Added tests and fixed all tests for prev PR PUSH BEFORE FIRST PR](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/183)
2. [Changing the Resume format](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/182)

### Went well:
Pushed refactoring on old codes, so that the account can play a practical role.
### Not well:
As not all people arrive school this week, we did not have a clear goal on what we should do this week.
### Next cycle:
Finish the refactoring on old codes, and push the development on milestone 2.
