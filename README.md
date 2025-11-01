# Kuizmo API

Kuizmo is a study companion API inspired by the Gizmo learning app. It exposes endpoints for
managing courses, modules, quizzes, and learner progress. The service can be run locally with
Uvicorn for development or deployed to [Vercel](https://vercel.com/) using the included
serverless configuration.

## Getting started

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Launch the development server:

   ```bash
   uvicorn app.main:app --reload
   ```

3. Explore the interactive documentation at <http://127.0.0.1:8000/docs>.

## Deploying to Vercel

1. Ensure the repository is connected to your Vercel account.
2. Set the project to use the "Python" framework preset. Vercel will detect the provided
   `vercel.json` configuration automatically.
3. Trigger a deployment. Vercel will build the FastAPI app through `api/index.py` and expose the
   API at your project URL.

## API overview

### Courses
- `GET /courses` — list courses.
- `POST /courses` — create a course.
- `GET /courses/{course_id}` — retrieve a course.
- `PUT /courses/{course_id}` — update a course.
- `DELETE /courses/{course_id}` — delete a course.

### Modules
- `GET /courses/{course_id}/modules` — list modules for a course.
- `POST /courses/{course_id}/modules` — create a module.
- `GET /courses/{course_id}/modules/{module_id}` — retrieve a module.
- `PUT /courses/{course_id}/modules/{module_id}` — update a module.
- `DELETE /courses/{course_id}/modules/{module_id}` — delete a module.

### Quizzes
- `GET /courses/{course_id}/quizzes` — list quiz questions for a course.
- `POST /courses/{course_id}/quizzes` — create a quiz question.
- `PUT /courses/{course_id}/quizzes/{question_id}` — update a quiz question.
- `DELETE /courses/{course_id}/quizzes/{question_id}` — delete a quiz question.
- `POST /courses/{course_id}/quizzes/attempt` — submit answers and receive a score.

### Progress
- `GET /courses/{course_id}/progress/{user_id}` — read a user's course progress.
- `POST /courses/{course_id}/progress/{user_id}` — mark a module as complete for a user.

### System
- `GET /health` — health check endpoint.
