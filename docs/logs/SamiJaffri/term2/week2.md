## What I completed this week
- This week I worked on the milestone goal of setting up FastAPI to facilitate communication between the backend and frontend. This addresses issues #188-190.
- I created a new API structure in the src/api/ directory with:
    - main.py - FastAPI application with CORS middleware for frontend connectivity
    - dependencies.py - Shared database connection helpers using FastAPI's dependency injection pattern
    - routes/health.py - Health check endpoints (basic and database connectivity)
    - routes/project.py - Projects verification endpoint
- I linked the API to Docker by:
    - Adding an API service to docker-compose.yml that depends on the database service
    - Creating a Dockerfile for the API container
    - Setting up networking between services
- I created a mock frontend (frontend/index.html) to test API connectivity with buttons to test all endpoints and display JSON responses.
- I also worked with Kevin to fix a bug in the get_db_cursor dependency. The issue was using @contextmanager decorator instead of a FastAPI dependency function that yields, which would prevent proper cleanup. This was fixed to use FastAPI's dependency injection lifecycle correctly.
- Finally, I created a test file (tests/test_api.py) covering all endpoints, error handling, and dependency lifecycle.

## Link to PR
This is the link to the PR that I have made: #191

## What went well
- My coding went well this week. I was able to set up the FastAPI structure and get all endpoints working. I'm pleased with the clean separation of concerns (routes, dependencies, main app).
The Docker integration went smoothly, and the API service properly waits for the database to be healthy before starting.
- I didn't have any problems while attending class or communicating with my group members, which was very nice.

## What didn't go well
- I initially had an issue with the dependency injection pattern - I used a context manager decorator instead of a FastAPI dependency function. Kevin caught this in review, and I was able to fix it quickly.
- There was also a missing dependency (httpx) that was needed for the test client, but I added it to requirements.txt once identified.

## What I will work on next week
Next week I would like to continue expanding the API by adding more endpoints for the existing functionality (projects, analysis, portfolio, etc.).
