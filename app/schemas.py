"""Pydantic schemas for the Kuizmo API."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CourseBase(BaseModel):
    title: str = Field(..., example="Neural Networks Primer")
    description: str = Field(..., example="Master the foundations of neural networks.")
    tags: list[str] = Field(default_factory=list, example=["machine-learning", "ai"])


class CourseCreate(CourseBase):
    pass


class CourseUpdate(CourseBase):
    pass


class CourseRead(CourseBase):
    id: int


class ModuleBase(BaseModel):
    title: str = Field(..., example="Activation Functions")
    content: str = Field(..., example="Understand sigmoid, ReLU, and GELU.")


class ModuleCreate(ModuleBase):
    pass


class ModuleUpdate(ModuleBase):
    pass


class ModuleRead(ModuleBase):
    id: int
    course_id: int


class QuizQuestionBase(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prompt": "Which activation function is piecewise linear?",
                "options": ["Sigmoid", "Tanh", "ReLU", "Softmax"],
                "answer_index": 2,
            }
        }
    )

    prompt: str = Field(..., example="Which activation function is piecewise linear?")
    options: list[str] = Field(..., min_length=2)
    answer_index: int = Field(..., ge=0)


class QuizQuestionCreate(QuizQuestionBase):
    pass


class QuizQuestionUpdate(QuizQuestionBase):
    pass


class QuizQuestionRead(QuizQuestionBase):
    id: int
    course_id: int


class QuizAttempt(BaseModel):
    answers: list[int] = Field(..., example=[2, 1])


class QuizResult(BaseModel):
    score: int
    total: int
    correct_question_ids: list[int]


class ProgressRead(BaseModel):
    user_id: str
    course_id: int
    completed_module_ids: list[int]


class ProgressUpdate(BaseModel):
    module_id: int
