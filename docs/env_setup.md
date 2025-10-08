# Environment Setup Guide

This document explains how to set up your development environment for the project.

---

## 1. Requirements

Make sure you have:
- [Python 3.10+](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [VS Code](https://code.visualstudio.com/)
- [Git](https://git-scm.com/)

---

## 2. Clone the Repository
git clone <repo-url>
cd Project-Starter

--- 
## 3. Create Local Environment File
cp .env.example .env

## 4. Start the Database 
docker-compose up -d 
docker-compose down 

## 5. Install the Dependencies 
### At this step, I believe the best way to do this for everyone is to use a virtual environment to install the packages, and then run it everytime you start the program. 
python3 -m venv venv 
source venv/bin/activate 
### then run 
pip install -r requirements.txt 
### Now to turn off the environment after your coding session type 
deactivate
### into your terminal. To restart it, type
source venv/bin/activate
### into your terminal (this should be done everytime) 

## 6. Run the Project
python src/main.py
### Should get a bunch of success messages as your output. 

## 7. Run a final test 
python -m tests.test_db_connection
### if you see a success message start coding you're good to go. 
