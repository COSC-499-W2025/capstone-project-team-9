# T2Week 4: 2026/1/26 – 2026/2/1

## Tasks Worked On
Do not found this week's team peer evaluation

---

## Weekly Goals Recap
This week, our team keep develop the milstone 2 things. We developed a basic fround end, improve the backend functions. 

---

## My Contributions
This week I am keep developing the user data isolation feature.
- [Finished] Isolation in delete_insights feature, isolation in external service feature, isolation in user content feature.

### issue developed:
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
  
### PR reviewed: 
1. [Refactor CLI for new "Settings" Menu](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/252)
2. [ranking persistance bug fix](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/265)
3. [Bug Fix for duplicate files](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/266)
4. [Main menu refactor](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/270)
5. [Gemini API (LLM) Implenentation](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/272)
6. [Refactor: standardize CLI output and harden display utilities](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/273)

### Went well:
Almost finished all user data isolation features.
### Not well:
One of the user data isolation feature do not pass all tests, need to found out why the test can pass on my PC but not pass in github
### Next cycle:
Finish the last user data isolation thing, and start the front end develop.
