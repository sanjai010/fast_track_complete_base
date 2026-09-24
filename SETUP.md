3. Prerequisites

Install the following software before setting up the project.

3.1 Python

Install Python 3.x.

Verify the installation:

python --version

Example:

Python 3.x.x
3.2 Node.js

Install Node.js.

Verify:

node --version
3.3 npm

npm is installed together with Node.js.

Verify:

npm --version
3.4 Git

Verify:

git --version
4. Clone the Repository

Clone the GitHub repository:

git clone https://github.com/sanjai010/fast_track_complete_base.git

Move into the project:

cd fast_track_complete_base

The project should contain:

backend/
frontend/
README.md
SETUP.md
.gitignore
5. Backend Setup

Open a terminal in the project root.

Move into the backend:

cd backend
5.1 Create Python Virtual Environment

Create the virtual environment:

python -m venv .venv
5.2 Activate Virtual Environment

For Windows PowerShell:

.venv\Scripts\Activate.ps1

After activation, the terminal should show something similar to:

(.venv)
5.3 Install Python Dependencies

Install the backend dependencies:

pip install -r requirements.txt
6. Environment Variables

The project uses environment variables for API keys and configuration.

The .env file is NOT stored in GitHub.

You must create it manually on every new machine.

Create:

backend/.env

Example:

OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openrouter/free

QDRANT_LOCAL_PATH=./qdrant_storage

Replace:

your_openrouter_api_key

with the actual OpenRouter API key.

6.1 Important Security Rule

Never commit the .env file.

Do NOT push:

backend/.env

to GitHub.

Never place API keys directly inside:

Python files
JavaScript files
React components
GitHub repositories
README files
7. Qdrant Setup

The project currently uses local Qdrant.

Qdrant is used as the vector database for RAG retrieval.

The local Qdrant database is stored at:

backend/qdrant_storage/

This folder is intentionally excluded from GitHub.

7.1 Why Qdrant Storage Is Not in GitHub

The qdrant_storage folder contains the local vector database created by the ingestion process.

It should not be committed to the repository.

Therefore, when a new developer clones the project, the Qdrant database must be created/populated on that machine.

8. RAG / Qdrant Pipeline

The backend contains the following processing pipeline:

Step 1
Parse
   ↓
Step 2
Clean
   ↓
Step 3
Chunk
   ↓
Step 4
Metadata
   ↓
Step 5
Embeddings
   ↓
Step 6
Qdrant Ingestion
   ↓
Step 7
Retrieval

Relevant files:

backend/src/step1_parse.py
backend/src/step2_clean.py
backend/src/step3_chunk.py
backend/src/step4_metadata.py
backend/src/step5_embed.py
backend/src/step6_ingest_qdrant.py
backend/src/step7_retrieve.py

The project also contains processed data under:

backend/data/processed/

and raw knowledge under:

backend/data/raw/
9. Backend Architecture

After retrieval, the enhanced chatbot flow is:

Customer Message
       │
       ▼
Conversation Routing
       │
       ▼
Support / Complaint Routing
       │
       ▼
Query Retrieval
       │
       ▼
Qdrant
       │
       ▼
Intent Detection
       │
       ▼
Candidate Analysis
       │
       ▼
Multi-Intent Analysis
       │
       ▼
Business Rules / Guardrails
       │
       ▼
Response Generation
       │
       ▼
OpenRouter
       │
       ▼
Response Validation
       │
       ▼
Frontend
       │
       ▼
Customer
10. Backend Processing Steps
Step 1 - Parse

File:

backend/src/step1_parse.py

Responsible for processing the incoming/raw information.

Step 2 - Clean

File:

backend/src/step2_clean.py

Responsible for cleaning the data.

Step 3 - Chunk

File:

backend/src/step3_chunk.py

Responsible for preparing knowledge chunks.

Step 4 - Metadata

File:

backend/src/step4_metadata.py

Responsible for adding metadata to the knowledge records.

Step 5 - Embeddings

File:

backend/src/step5_embed.py

Creates vector embeddings for retrieval.

Step 6 - Qdrant Ingestion

File:

backend/src/step6_ingest_qdrant.py

Loads the processed knowledge into the local Qdrant vector database.

Step 7 - Retrieval

File:

backend/src/step7_retrieve.py

Retrieves relevant knowledge from Qdrant based on the customer's question.

Step 8 - Business Rules

File:

backend/src/step8_business_rules.py

Applies business rules and guardrails before response generation.

Examples:

Price guardrails
Booking requests
Availability verification
Complaint handling
Required data collection
Approved-answer handling
Human handoff
Step 9 - Response Generation

File:

backend/src/step9_gemini.py

The current implementation uses OpenRouter for response generation.

The configured model is controlled through:

OPENROUTER_MODEL=openrouter/free
Step 10 - Response Validation

File:

backend/src/step10_validate.py

Validates the generated response before returning it to the customer.

11. Start the Backend

From the backend directory:

cd backend

Activate the virtual environment:

.venv\Scripts\Activate.ps1

Start the FastAPI server:

uvicorn enhancements.enhanced_api_server:app --host 127.0.0.1 --port 8001

The backend will run at:

http://127.0.0.1:8001

Keep this terminal running.

12. Frontend Setup

Open a SECOND terminal.

From the project root:

cd frontend

Install frontend dependencies:

npm install

This installs the dependencies defined in:

frontend/package.json
13. Start the Frontend

Run:

npm run dev

Vite will normally start the frontend at:

http://localhost:5173

Open this URL in your browser.

14. Run the Complete Application

The complete application requires two terminals.

Terminal 1 - Backend
cd C:\Users\User\Desktop\fast_track_complete_base\backend

Activate the environment:

.venv\Scripts\Activate.ps1

Start the server:

uvicorn enhancements.enhanced_api_server:app --host 127.0.0.1 --port 8001

Backend:

http://127.0.0.1:8001
Terminal 2 - Frontend
cd C:\Users\User\Desktop\fast_track_complete_base\frontend

Start Vite:

npm run dev

Frontend:

http://localhost:5173
15. Application Connection

The frontend communicates with the backend through the chat API.

Current backend endpoint:

http://127.0.0.1:8001/chat

The flow is:

React Frontend
      │
      │ POST /chat
      ▼
FastAPI Backend
      │
      ▼
RAG + Business Rules
      │
      ▼
OpenRouter
      │
      ▼
Validated Response
      │
      ▼
React Frontend
16. First-Time Setup Summary

For a completely new machine:

git clone https://github.com/sanjai010/fast_track_complete_base.git

cd fast_track_complete_base

cd backend

python -m venv .venv

.venv\Scripts\Activate.ps1

pip install -r requirements.txt

Create:

backend/.env

Add:

OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openrouter/free
QDRANT_LOCAL_PATH=./qdrant_storage

Then set up/populate the local Qdrant database using the project's ingestion pipeline.

Then open another terminal:

cd fast_track_complete_base\frontend

npm install

npm run dev

And in the backend terminal:

cd fast_track_complete_base\backend

.venv\Scripts\Activate.ps1

uvicorn enhancements.enhanced_api_server:app --host 127.0.0.1 --port 8001

Open:

http://localhost:5173
17. Daily Development Workflow

When working on the project:

Terminal 1

Start backend:

cd backend
.venv\Scripts\Activate.ps1
uvicorn enhancements.enhanced_api_server:app --host 127.0.0.1 --port 8001
Terminal 2

Start frontend:

cd frontend
npm run dev

Then open:

http://localhost:5173
18. Pull Latest Changes

If another team member has pushed changes:

git pull origin main

Check the repository status:

git status
19. Update Backend Dependencies

If backend/requirements.txt has changed:

cd backend
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
20. Update Frontend Dependencies

If frontend/package.json or frontend/package-lock.json has changed:

cd frontend
npm install
21. Git Workflow

After making changes:

Check the changes:

git status

Stage:

git add .

Commit:

git commit -m "Describe your changes"

Push:

git push

Example:

git add .
git commit -m "Fix multi-intent response handling"
git push
22. Recommended Commit Messages

Use clear commit messages.

Examples:

Add multi-intent handling
Fix price guardrail
Update chatbot UI
Fix OpenRouter integration
Add response validation
Update Qdrant retrieval
Improve customer routing
Add setup documentation
Fix frontend API connection
23. Important Files That Must NOT Be Pushed

Never push:

backend/.env
backend/.venv/
backend/qdrant_storage/
backend/qdrant_storage_backup_20260922/
frontend/node_modules/
frontend/dist/

These files/folders are local or contain sensitive information.

24. Security Rules

Never commit:

API keys
Passwords
Authentication tokens
Private credentials
.env files
Local virtual environments
Local Qdrant storage

If an API key is accidentally pushed to GitHub, revoke/rotate it immediately.

25. Qdrant Important Note

The project uses local Qdrant storage.

Do not start multiple processes that create separate Qdrant clients against the same local storage directory.

If you see:

Storage folder ... qdrant_storage is already accessed by another instance of Qdrant client.

it means another Qdrant client/process is already using the local storage.

Stop the existing backend/process before starting another one.

26. Frontend Cannot Connect to Backend

If the chatbot UI loads but messages do not receive responses:

Check backend

Make sure this is running:

http://127.0.0.1:8001
Check frontend API configuration

The frontend chat API should point to:

http://127.0.0.1:8001/chat
Check browser console

Open:

Browser → F12 → Console

Look for network/API errors.

27. Backend Import Errors

If Python reports a missing package:

ModuleNotFoundError

activate the virtual environment:

cd backend
.venv\Scripts\Activate.ps1

Then reinstall:

pip install -r requirements.txt
28. OpenRouter Errors

If response generation fails:

Check:

backend/.env

Make sure:

OPENROUTER_API_KEY=your_actual_key

is present.

Check:

OPENROUTER_MODEL=openrouter/free

Restart the backend after changing .env.

29. Local Development URLs

Frontend:

http://localhost:5173

Backend:

http://127.0.0.1:8001

Chat API:

http://127.0.0.1:8001/chat
30. Team Setup

Every team member should have:

Git
Python
Node.js
npm

Each developer should:

Clone the repository.
Create their own Python virtual environment.
Install backend dependencies.
Create their own .env.
Configure their API key.
Set up local Qdrant.
Install frontend dependencies.
Start the backend.
Start the frontend.
Test the chatbot.
31. Before Pushing Code

Always run:

git status

Make sure the following are NOT listed:

backend/.env
backend/.venv/
backend/qdrant_storage/
frontend/node_modules/

Then:

git add .
git commit -m "Describe your changes"
git push
32. Repository

GitHub Repository:

https://github.com/sanjai010/fast_track_complete_base

33. Quick Start

For developers who already understand the project:

Backend
cd backend
.venv\Scripts\Activate.ps1
uvicorn enhancements.enhanced_api_server:app --host 127.0.0.1 --port 8001
Frontend

Open a second terminal:

cd frontend
npm run dev

Open:

http://localhost:5173
34. Final Architecture
                    ┌─────────────────────┐
                    │      Customer       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React Frontend    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   FastAPI Backend   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Conversation Router │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Intent Detection   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Qdrant Retrieval    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Candidate Analysis  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Multi-Intent Logic  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Business Rules /    │
                    │ Guardrails          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ OpenRouter / LLM    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Response Validation │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Customer Response   │
                    └─────────────────────┘
End of Setup Guide

### After saving `SETUP.md`

From the project root:

```powershell
git add SETUP.md
git commit -m "Add complete setup guide"
git push

Then your repo will have a clean separation:

README.md
    ↓
"What is this project?"

SETUP.md
    ↓
"How do I install and run it?"
