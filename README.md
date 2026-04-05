# Artifact Mining System - Team 9

**COSC 499 (2025 Sept to 2026 April)**  
**Team Members:** 
* Ryan Eveson 99775389
* Sami Jaffri  44165611
* Evan Pasenau 36403509
* Jinxi Hu 48528608
* Kevin Zhang 10811057
* Eric Chen 47368527

### Prerequisites
* Docker and Docker Compose installed and running
* Git installed
* A Gemini API Key (You will need API key to use AI feature)

### Running the Project

1. **Clone the repository or [Download our folder](https://github.com/COSC-499-W2025/capstone-project-team-9/releases/tag/Release)**
   ```bash
   git clone https://github.com/COSC-499-W2025/capstone-project-team-9
   cd capstone-project-team-9
   
2. **Set up Environment Variables**
   ```bash
   cp .env.example .env

3. **Start all services**
   ```bash
   docker-compose up -d
   
4. **Application**
   - Frontend Dashboard: http://localhost:8000
   - Backend API Docs (Swagger UI): http://localhost:8000/docs
   - Backend API Docs (ReDoc): http://localhost:8000/redoc

5. **Testing Files**
   - We have included sample ZIP files in the root directory to test the artifact parsing engine:
   - test.zip: A sample project repository for skill extraction.
   - testfile.zip: An alternative project repository for testing portfolio generation.
  
6. **Stopping the Project**
   ```bash
   docker-compose down -v

7. **View Logs**
   ```bash
   docker compose logs -f
   docker compose logs -f backend

## Diagrams & System Documentation

There is no separate written report. All relevant system documentation can be navigated from the links below:
- [System Architecture Diagram](https://github.com/COSC-499-W2025/capstone-project-team-9/blob/Milestone1/README.md)
- [Work Breakdown Structure (WBS)](https://github.com/COSC-499-W2025/capstone-project-team-9/blob/Milestone1/README.md)
- [Data Flow Diagram (DFD)](https://github.com/COSC-499-W2025/capstone-project-team-9/blob/Milestone1/README.md)
- 

## Technology Stack

### Frontend [API setup](https://github.com/COSC-499-W2025/capstone-project-team-9/blob/main/docs/api.md)
| Technology | Purpose |
| :--- | :--- |
| **HTML5 / CSS3** | Core markup and responsive styling (`frontend/css/`) |
| **Vanilla JavaScript** | DOM manipulation and API integration (`frontend/js/`) |
| **html2pdf.js** | Client-side PDF generation for portfolios/resumes |
| **marked.js** | Markdown parsing for formatted text rendering |

### Backend [Backendend Setup](https://github.com/COSC-499-W2025/capstone-project-team-9/blob/main/docs/env_setup.md)
| Technology | Purpose |
| :--- | :--- |
| **Python 3** | Core backend programming language |
| **FastAPI** | High-performance async web framework and routing |
| **Pydantic** | Data validation and settings management |
| **Docker** | Containerization and environment standardization |

### AI & Parsing Subsystem
| Technology | Purpose |
| :--- | :--- |
| **Gemini API** | Advanced code analysis and skill extraction |
| **Python AST / ZipFile** | Local deep code parsing and artifact mining |
