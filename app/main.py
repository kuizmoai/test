"""Kuizmo API - A study companion inspired by Gizmo."""
from __future__ import annotations

from typing import List

from fastapi import FastAPI, HTTPException, Path, status

from . import data
from .schemas import (
    CourseCreate,
    CourseRead,
    CourseUpdate,
    ModuleCreate,
    ModuleRead,
    ModuleUpdate,
    ProgressRead,
    ProgressUpdate,
    QuizAttempt,
    QuizQuestionCreate,
    QuizQuestionRead,
    QuizQuestionUpdate,
    QuizResult,
)

app = FastAPI(
    title="Kuizmo API",
    description="A Gizmo-compatible study API for managing courses, modules, quizzes, and progress.",
    version="1.0.0",
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


# Courses ----------------------------------------------------------------
@app.get("/courses", response_model=List[CourseRead], tags=["courses"])
def list_courses() -> List[CourseRead]:
    return list(data.db.courses.values())


@app.post(
    "/courses",
    response_model=CourseRead,
    status_code=status.HTTP_201_CREATED,
    tags=["courses"],
)
def create_course(payload: CourseCreate) -> CourseRead:
    course = data.db.create_course(payload.title, payload.description, payload.tags)
    return course


@app.get("/courses/{course_id}", response_model=CourseRead, tags=["courses"])
def get_course(course_id: int = Path(..., gt=0)) -> CourseRead:
    course = data.db.courses.get(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@app.put("/courses/{course_id}", response_model=CourseRead, tags=["courses"])
def update_course(course_id: int, payload: CourseUpdate) -> CourseRead:
    if course_id not in data.db.courses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    course = data.db.update_course(
        course_id,
        title=payload.title,
        description=payload.description,
        tags=payload.tags,
    )
    return course


@app.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["courses"])
def delete_course(course_id: int) -> None:
    if course_id not in data.db.courses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    data.db.delete_course(course_id)


# Modules ----------------------------------------------------------------
@app.get(
    "/courses/{course_id}/modules",
    response_model=List[ModuleRead],
    tags=["modules"],
)
def list_modules(course_id: int) -> List[ModuleRead]:
    _ensure_course_exists(course_id)
    return [module for module in data.db.modules.values() if module.course_id == course_id]


@app.post(
    "/courses/{course_id}/modules",
    response_model=ModuleRead,
    status_code=status.HTTP_201_CREATED,
    tags=["modules"],
)
def create_module(course_id: int, payload: ModuleCreate) -> ModuleRead:
    _ensure_course_exists(course_id)
    module = data.db.create_module(course_id, payload.title, payload.content)
    return module


@app.get(
    "/courses/{course_id}/modules/{module_id}",
    response_model=ModuleRead,
    tags=["modules"],
)
def get_module(course_id: int, module_id: int) -> ModuleRead:
    _ensure_course_exists(course_id)
    module = data.db.modules.get(module_id)
    if not module or module.course_id != course_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    return module


@app.put(
    "/courses/{course_id}/modules/{module_id}",
    response_model=ModuleRead,
    tags=["modules"],
)
def update_module(course_id: int, module_id: int, payload: ModuleUpdate) -> ModuleRead:
    module = get_module(course_id, module_id)
    updated = data.db.update_module(module.id, title=payload.title, content=payload.content)
    return updated


@app.delete(
    "/courses/{course_id}/modules/{module_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["modules"],
)
def delete_module(course_id: int, module_id: int) -> None:
    get_module(course_id, module_id)
    data.db.delete_module(module_id)


# Quizzes ----------------------------------------------------------------
@app.get(
    "/courses/{course_id}/quizzes",
    response_model=List[QuizQuestionRead],
    tags=["quizzes"],
)
def list_quiz_questions(course_id: int) -> List[QuizQuestionRead]:
    _ensure_course_exists(course_id)
    return [q for q in data.db.quiz_questions.values() if q.course_id == course_id]


@app.post(
    "/courses/{course_id}/quizzes",
    response_model=QuizQuestionRead,
    status_code=status.HTTP_201_CREATED,
    tags=["quizzes"],
)
def create_quiz_question(course_id: int, payload: QuizQuestionCreate) -> QuizQuestionRead:
    _ensure_course_exists(course_id)
    if payload.answer_index >= len(payload.options):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="answer_index out of range")
    question = data.db.create_quiz_question(
        course_id,
        prompt=payload.prompt,
        options=payload.options,
        answer_index=payload.answer_index,
    )
    return question


@app.put(
    "/courses/{course_id}/quizzes/{question_id}",
    response_model=QuizQuestionRead,
    tags=["quizzes"],
)
def update_quiz_question(course_id: int, question_id: int, payload: QuizQuestionUpdate) -> QuizQuestionRead:
    question = _get_quiz_question(course_id, question_id)
    if payload.answer_index >= len(payload.options):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="answer_index out of range")
    updated = data.db.update_quiz_question(
        question.id,
        prompt=payload.prompt,
        options=payload.options,
        answer_index=payload.answer_index,
    )
    return updated


@app.delete(
    "/courses/{course_id}/quizzes/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["quizzes"],
)
def delete_quiz_question(course_id: int, question_id: int) -> None:
    _get_quiz_question(course_id, question_id)
    data.db.delete_quiz_question(question_id)


@app.post(
    "/courses/{course_id}/quizzes/attempt",
    response_model=QuizResult,
    tags=["quizzes"],
)
def attempt_quiz(course_id: int, payload: QuizAttempt) -> QuizResult:
    _ensure_course_exists(course_id)
    questions = [q for q in data.db.quiz_questions.values() if q.course_id == course_id]
    if not questions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No quiz questions available")
    if len(payload.answers) != len(questions):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Answer count mismatch")

    score = 0
    correct_question_ids: List[int] = []
    for question, answer in zip(questions, payload.answers):
        if answer == question.answer_index:
            score += 1
            correct_question_ids.append(question.id)
    return QuizResult(score=score, total=len(questions), correct_question_ids=correct_question_ids)


# Progress ---------------------------------------------------------------
@app.get(
    "/courses/{course_id}/progress/{user_id}",
    response_model=ProgressRead,
    tags=["progress"],
)
def read_progress(course_id: int, user_id: str) -> ProgressRead:
    _ensure_course_exists(course_id)
    progress = data.db.get_progress(user_id=user_id, course_id=course_id)
    return ProgressRead(**progress.__dict__)


@app.post(
    "/courses/{course_id}/progress/{user_id}",
    response_model=ProgressRead,
    tags=["progress"],
)
def update_progress(course_id: int, user_id: str, payload: ProgressUpdate) -> ProgressRead:
    module = get_module(course_id, payload.module_id)
    progress = data.db.record_module_completion(user_id=user_id, course_id=course_id, module_id=module.id)
    return ProgressRead(**progress.__dict__)


# Internal helpers -------------------------------------------------------
def _ensure_course_exists(course_id: int) -> None:
    if course_id not in data.db.courses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")


def _get_quiz_question(course_id: int, question_id: int) -> data.QuizQuestion:
    question = data.db.quiz_questions.get(question_id)
    if not question or question.course_id != course_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz question not found")
    return question
