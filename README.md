# **Milestone 1 Overview — Mining Digital Work Artifacts**

This document includes both the **Work Breakdown Structure (WBS)** and the **System Architecture Diagram** for **Milestone #1 (October – December 07)** of the *Mining Digital Work Artifacts* project.

---

## **Work Breakdown Structure (WBS)**

```mermaid
graph LR
    A["Milestone 1: Parsing and Output Functionality (Oct–Dec 07)"] --> B["1 System Design and Architecture"]
    A --> C["2 Consent and Privacy Module"]
    A --> D["3 File Parsing and Validation"]
    A --> E["4 Analysis and Metrics Extraction"]
    A --> F["5 External Service Integration"]
    A --> G["6 Data Storage and Retrieval"]
    A --> H["7 Testing and Documentation"]

    %% System Design
    B --> B1["Define core modules (src structure)"]
    B --> B2["Set up configuration files and environment"]
    B --> B3["Design data flow diagrams (DFD Level 0 and 1)"]
    B --> B4["Create initial database schema draft"]

    %% Consent Module
    C --> C1["Implement user consent prompt"]
    C --> C2["Store consent choices in database"]
    C --> C3["Restrict access if consent denied"]

    %% File Parsing and Validation
    D --> D1["Parse zipped folders with nested files"]
    D --> D2["Return error for invalid file formats"]
    D --> D3["Extract metadata (file names, paths, types)"]
    D --> D4["Identify coding vs non-coding files"]

    %% Analysis and Metrics
    E --> E1["Identify programming languages and frameworks"]
    E --> E2["Calculate project contribution metrics"]
    E --> E3["Determine project duration and activity frequency"]
    E --> E4["Extract key skills from projects"]

    %% External Services
    F --> F1["Request permission before using external APIs or LLMs"]
    F --> F2["Implement fallback to local analysis"]
    F --> F3["Store user external-service configuration"]

    %% Data Storage and Retrieval
    G --> G1["Create PostgreSQL database and tables"]
    G --> G2["Store parsed and analyzed project data"]
    G --> G3["Enable retrieval of résumé and portfolio information"]
    G --> G4["Implement delete and update operations safely"]

    %% Testing and Documentation
    H --> H1["Unit tests for all modules (Pytest)"]
    H --> H2["Integration testing for file-to-database pipeline"]
    H --> H3["Documentation of architecture and data flow"]
    H --> H4["Weekly sprint reports and team logs"]
```
---

## **System Architecture**

This layered architecture diagram provides a high-level view of how the system interacts across components and data flows.

```mermaid
graph TD
  %% ===== LAYERS =====
  subgraph P["Presentation Layer"]
    UI["CLI / Web Interface"]
  end

  subgraph A["Application Layer"]
    PARSE["File Parsing & Consent Management"]
    ANALYZE["AnalysisRouter & Local Analysis"]
    PERM["External Service Permission Handling"]
  end

  subgraph D["Data / Integration Layer"]
    LLM["External Services (LLMs / APIs)"]
    META["Metadata Extraction & File Crawling"]
  end

  subgraph DB["Database Layer"]
    PG["PostgreSQL (User Consents, Configs, Metadata, Results)"]
  end

  %% ===== DATA FLOW =====
  UI -->|"User Input"| PARSE
  PARSE -->|"Validated Data"| ANALYZE
  ANALYZE -->|"Permission Check"| PERM
  PERM -->|"Allowed?"| LLM
  PERM -->|"Not allowed"| META
  META -->|"Store results"| PG
  ANALYZE -->|"Store analysis output"| PG
  PG -->|"Retrieve data"| UI
```
### **Architecture Overview**

The architecture is organized into **four primary layers**, each with a specific responsibility:

**Presentation Layer**
   – user facing interfaces for interaction and output 
   - Display project summaries, metrics, and skill visualizations
   - Support future React-based Web Dashboard
     
**Application Layer** 
  – core business logic for analysis and decision-making  
  - Parse and validate ZIP files
  - Route analysis tasks (local vs external)
    
**Data / Integration Layer**
  – mediates between logic and storage or external APIs
  - Handle optional connections to external LLMs or APIs (if user allows)
  - Extract file metadata (name, type, size, structure)
    
**Database Layer**
  – persistent storage for structured data and metadata
  - Provides durable, structured storage for all collected and analyzed data.
  - Support data retrieval for résumé and portfolio generation

## **DFD level 1**
<img width="643" height="924" alt="image" src="https://github.com/user-attachments/assets/6dea9944-18a2-4b55-9224-f82c0c6db18e" />

### **Overview**
This DFD represents the **data movement and processing** inside the system when a user uploads, analyzes, and retrieves work artifacts.  
It highlights the main external entities, processes, and data stores involved in the workflow.

---

#### 1. **External Entities**
- **Early Professionals / Students**  
  The main users of the system who provide login credentials and initiate artifact scanning.  
  They want to analyze their work output and generate summarized portfolios.

- **HR Representative**  
  Acts as a facilitator or stakeholder who can provide **user details** or verify data sources (for professional data mining).

- **Data Source**  
  Represents external systems, repositories, or local folders containing digital work artifacts — such as documents, code, media, or design files.

---

#### 2. **Core Process: Mining Digital Work Artifacts**
This is the **main system** responsible for analyzing digital files.

**Inputs:**
- User details (from HR or direct login)
- Extracted raw data (from data sources)

**Processes:**
- Scans and parses the digital artifacts
- Extracts metadata (file type, timestamps, contributions)
- Performs content and activity analysis
- Summarizes insights (skills, project duration, contributions, etc.)

**Outputs:**
- Result data ready for visualization and portfolio storage

---

#### 3. **Supporting Processes**

- **Digital Artifacts System**  
  The entry point where user operations (like “Scan Artifacts”) are initiated.  
  It requires login credentials and sends **user detail** information downstream.

- **HR Representative**  
  Validates user identity and provides additional metadata (if applicable).

- **Data Source**  
  Supplies **raw digital artifacts** for analysis. It interacts with the system by sending **data extraction results** to the Mining system.

---

#### 4. **Downstream Systems**

- **Portfolio Store System**  
  After analysis, results (such as summary reports or extracted skills) are sent here for **storage and visualization**.  
  It converts processed results into structured **portfolio data**.

- **Portfolio Database**  
  The storage backend where all summarized user portfolios and extracted data insights are kept for retrieval.

---
