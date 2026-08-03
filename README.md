# Interactive Story Generator

A full-stack choose-your-own-adventure application. Enter a theme, and the app uses an OpenAI model to generate a branching story with player choices, winning endings, and losing endings.

The frontend creates a story-generation job and polls for its status. The FastAPI backend generates the story in the background, stores its nodes and choices in a SQL database, and returns the completed story tree for play.

## Stack

- Frontend: React, Vite, Axios
- Backend: FastAPI, SQLAlchemy, LangChain, OpenAI
- Database: any SQLAlchemy-supported database configured through `DATABASE_URL`

## Project layout

```text
frontend/  React and Vite user interface
backend/   FastAPI API, story generation, database models, and tests
```

## Prerequisites

- Node.js and npm
- Python 3.14 or later
- An OpenAI API key
- `uv` (recommended for the backend)

## Configuration

Create `backend/.env` with your local settings:

```env
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///./database.db
LLM_MODEL=gpt-5-mini
ALLOWED_ORIGINS=http://localhost:5173
```

`backend/.env` and local database files are intentionally ignored by Git.

## Run locally

Start the API from one terminal:

```bash
cd backend
uv sync
uv run uvicorn main:app --reload --port 8000
```

Start the frontend from another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally `http://localhost:5173`. The Vite development server proxies `/api` requests to `http://localhost:8000`.

API documentation is available at `http://localhost:8000/docs` while the backend is running.

## API overview

- `POST /api/stories/create` creates an asynchronous story-generation job.
- `GET /api/jobs/{job_id}` returns the job status.
- `GET /api/stories/{story_id}/complete` returns a completed story and its node tree.

## Tests

From `backend/`:

```bash
uv run pytest
```
