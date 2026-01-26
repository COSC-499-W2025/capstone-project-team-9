<img width="1103" height="646" alt="image" src="https://github.com/user-attachments/assets/e77041ac-a2cc-49b2-bd64-1ed2a9272752" />

## What I completed this week
- Refactored the CLI to consolidate all configuration-related actions into a single Settings menu.
- Added and updated backend API endpoints to support settings, project data management, and deletion flows.
- Renamed and standardized project data deletion endpoints to improve API clarity and consistency.
- Expanded and updated automated tests to match new API behavior and CLI flows.
- Built out frontend functionality, including:
- Initial frontend setup and Docker integration
- Login page UI connected to existing backend authentication
- Implemented multiple project-related API endpoints and closed several tracked issues.
- Fixed bugs introduced during endpoint development to keep feature branches stable.

## Link to PRs
#252 
#234 
#233 
#231 
#232 

## What went well
The CLI and API are now much cleaner and easier to maintain.
Backend endpoints were well-tested and integrated smoothly with both the CLI and frontend.
Frontend login and API communication worked end-to-end.
Bugs were caught early and fixed before merging, preventing regressions.

## What didn’t go well
Some refactors introduced minor bugs that required follow-up fixes.
Frontend PRs were larger than expected due to HTML/CSS changes, making reviews slightly heavier.

## What I will work on next week
Continue expanding frontend features beyond login (projects, settings, data views).
Add additional API endpoints as needed and improve frontend ↔ backend integration.
Polish UI/UX and improve overall application flow.
