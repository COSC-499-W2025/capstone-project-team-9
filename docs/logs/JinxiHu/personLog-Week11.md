# Week 11: 2025/11/9 – 2025/11/16

## Tasks Worked On
- This is the reading week, no team formation

---

## Weekly Goals Recap
As week11 is the reading week, our team not has goal for this week.

---

## My Contributions
This week I focus on Back-end accouont system development and code review.

I develop the [issue#132: develop basic login and logout feature](https://github.com/COSC-499-W2025/capstone-project-team-9/issues/132) 
- This issue is right after the issue 126, which basic on user table and it's CRUDs to implement the basic account management functions. Such as login, logout and account registrition.
-  At the same time, also include the menu change to initial integration of the account system into the existing system.

### issue developed:

[issue#132: develop basic login and logout feature](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/138)
- Developed user_manager.py file, which use a class to manage and do all account operations, currently has loging, logout and registration.
- At the same time, user_manager.py file could also store the current login account information locally.
- Developed user_menus.py file and modify the main_menus.py to  add an user menus to the system, which displays the current user and allows users to log in, log out, and register an account.
- This user menus would be extened as future more account system's functions be developed.
- The issue 132 current effect the menus and user data table only, the account system has not yet been linked with other systems.

### PR reviewed: 
1. [Feature #10: Extract key contribution metrics in a project, displaying information about the duration of the project and activity type contribution frequency](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/129)
2. [Summarize ranked projects](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/131)
3. [CLI Integration w/ minor code refactoring](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/123)
4. [Resume Generation and Formatting](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/122)

### Went well:
Found out our project need an account system and creat step by step issues to develop this system.
### Not well:
The account system must relate to many of old codes may cause alot of bugs, I have to confirm this with others.
### Next cycle:
Push the development of the account system and be sure it wont break the whole project.
