# Week 10: 2025/11/3 – 2025/11/9

## Tasks Worked On
![Week10 Project Log](img/week10.png)

---

## Weekly Goals Recap
This week, our team is main focus on code feractoring/bug fixing, enhance project analysis and summarize feature.
At the same time we also start developing new features: The user account system; the Resume generate and manage system.

---

## My Contributions
This week I focus on Back-end feature development and code review.

I set up a new issue [Feature: user login system #125](https://github.com/COSC-499-W2025/capstone-project-team-9/issues/125) and assinged it as my main development direction for the next two weeks. And at this week I have one the basic user_informations data table develop.
The account system enables our platform to isolate personal data between different users, while also making it more convenient to manage file uploads and report generation. To achieve these goals, we need to create a data table for storing user account information and link other necessary tables to the user table for unified management. In addition, new code must be written to display user information, and existing code needs to be modified to ensure compatibility with the account system.

### issue developed:

[Basic user information table and it's CRUDs#126](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/133)
- Developed user_informations data table which is used for store all account informations of users.
- Developed CRUD functions for user_informations data table, those functions could be used to creat new account, select accounts, delete account, and update account.
- The issue 126 current has no impact on the current system, but it forms the foundation for future development of the entire account system.

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
