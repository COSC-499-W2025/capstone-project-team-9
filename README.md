# Artifact Mining System - Team 9

**COSC 499 (2025 Sept to 2026 April)**  
**Team Members:** 
* Ryan Eveson 99775389
* Sami Jaffri  44165611
* Evan Pasenau 36403509
* Jinxi Hu 48528608
* Kevin Zhang 10811057
* Eric Chen 47368527

## System Overview

The Artifact Mining System is an end-to-end automated platform designed to bridge the gap between raw development work and professional presentation. By deeply analyzing a developer's code repositories, the system extracts verifiable skills, ranks projects by complexity, and automatically generates tailored resumes and portfolios.

The system operates through four primary pipelines:

### 1. Artifact Ingestion & Deep Code Analysis
At the core of the system is the parsing engine. Users upload raw project artifacts (such as zipped repositories). The system utilizes Python Abstract Syntax Tree (AST) parsing combined with the Gemini AI API to deeply analyze the codebase. It doesn't just read file names; it evaluates the architecture, identifies the technology stack, and isolates individual contributor commits to understand exactly what the user built.

### 2. Skill Extraction & Project Ranking
Once the code is analyzed, the `Activity Classifier` and `Skill Mapper` translate raw technical implementations into professional competencies. The system evaluates the depth and complexity of the ingested projects, utilizing a proprietary ranking algorithm to score and sort the user's work. This ensures that the most impactful and technically complex projects are prioritized for display.

### 3. Automated Resume Generation
The extracted skills and ranked projects are fed directly into the Resume Builder module. The system dynamically generates professional, LaTeX-formatted resumes. Evidence extractors ensure that every skill listed on the resume is directly backed up by verified code from the user's uploaded artifacts, creating a highly credible professional profile.

### 4. Dynamic Portfolio Creation
Parallel to the resume builder, the Portfolio Manager generates comprehensive web-based portfolios. Using HTML and customized templates, the system creates a visual showcase of the developer's top-ranked projects, complete with AI-generated project summaries and skill tags. These portfolios can be customized via the frontend dashboard and exported seamlessly to PDF.

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

## Testing & CI/CD

This report documents our automated testing strategy used to keep the system stable during development.

### How to Run Tests Locally

We use `pytest` for our testing framework. You can run the entire suite, which covers our parsers, file validators, and API endpoints, directly from the root directory:

```bash
# Install dependencies
pip install -r requirements.txt

#Run the test suite
pytest
