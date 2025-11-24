# Week 12: 2025/11/17 – 2025/11/23

## Tasks Worked On
![Week12 Project Log](img/week12.png)

---

## Weekly Goals Recap
This week, our team is main focus on code feractoring/bug fixing, develop the resume system and account system.
Focus on expanding user-facing features, strengthening backend robustness, and integrating deep analysis into higher-level workflows such as project ranking and portfolio construction.

---

## My Contributions
This week I focus on Back-end accouont system development and code review.
- Fix the issues in PR [develop basic login and logout feature](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/138) that other reviewers pointed out.
- Create a new issue called [Make sure the system can be used only when the user already login.](https://github.com/COSC-499-W2025/capstone-project-team-9/issues/142), and write codes to implement it. 

### issue developed:

Problem fixing: [issue#132: develop basic login and logout feature](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/138)
- A Linux-compatible version has been added to the feature that displays the user's password input as '*', making the feature cross-platform.
- Remove all emojis / unusual characters from the code to make sure the account system still works on different platform.
- Change the all imports of AuthManager and user_account_menu into absolute imports, this is for CI compatibility。
PR developed: [issue#142 make sure the system can be used only when the user already login](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/149)
- Add a new login_menu functions to show the login menu.
- Modify the main_menu.py and main.py to make sure use can only go to the main menu when they already login.
- Add new test in test_user_menu.py to test the new codes.

### PR reviewed: 
1. [Fix Timeline Metrics: Use Zip Internal Timestamps Instead of Upload Time](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/139)
2. [Improve ZIP upload validation & add test coverage for invalid ZIP cases](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/140)
3. [Ranked projects deep analysis](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/141)
4. [Add CLI integration for resume generation, viewing](https://github.com/COSC-499-W2025/capstone-project-team-9/pull/143)

### Went well:
Fix the problems that teammates point out in my PR, and develop the account system to the point where it could have a formal impact on the system.
### Not well:
The my new PR seems not run well in others computer and also be identified some problems, I must fix them next week.
### Next cycle:
Push the development of the account system, such as fix the current problems and connect user table with other data tables.
