# Sprint Report – Week 6 (2025/10/06 to 2025/10/12)

## Overview
This sprint marked the transition from planning and design into **initial implementation**.  
The team began developing core system modules, connecting the database, and writing the first round of automated tests.

## Completed Work
- **Requirement #1 (issue #6) – User Consent Management** implemented by **Kevin**
  - Includes consent scope definition, status checking before data access, and withdrawal handling  
  - Related sub-issues: #11, #14, #18  
- **Database connection and configuration** verified; test scripts executed successfully  
- **File format validation** feature completed by **Eric** (#23)  
- **File-listing functionality** (nested folder display) expanded by **Jinxi** (#35)  
- **Initial test cases** added for consent and database modules  
- **Team collaboration setup** refined: branch naming, pull-request workflow, and environment consistency  
- **Sami** focused on reviewing pull requests and assisting with environment setup
- **Ryan** created Subtasks for features in GitHub, Reviewed Sami Jaffris pull request
- **Ryan** also set up a uplaoded files tab in the database, and wrote a basic python script that allows users to upload the file and file path that they want in to the database
- **Evan** was reviewing and put all the features in Github project. 

## Current Status
- Core backend structure and modules created under `src/consent/`  
- Database container (PostgreSQL) successfully built and running via Docker  
- Unit tests passing locally  
- PR for Requirement #1 (issue #6) under review  
- Preparing for next sprint: integrating file operations with consent logic

## Testing
- **Pytest** configured and executed  
- Verified database connection tests (`test_db_connection.py`)  
- Verified consent management tests (`test_consent.py`)  
- All current tests pass locally, CI integration planned for next sprint

## Next Steps
- Merge approved PRs into `main`  
- Begin work on next project
- Expand unit tests for error handling and invalid consent scenarios  
- Ensure documentation and weekly logs remain up to date

## Burnup Chart
<img width="1084" height="554" alt="image" src="https://github.com/user-attachments/assets/76e1fbc8-3bbb-4a26-89ef-47b3a82c0de5" />
<img width="1040" height="514" alt="image" src="https://github.com/user-attachments/assets/89ca42dd-fe09-4293-a87d-7388ec1898f8" />
