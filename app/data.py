"""In-memory datastore for the Kuizmo API."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Module:
    id: int
    course_id: int
    title: str
    content: str


@dataclass
class QuizQuestion:
    id: int
    course_id: int
    prompt: str
    options: List[str]
    answer_index: int


@dataclass
class Course:
    id: int
    title: str
    description: str
    tags: List[str] = field(default_factory=list)


@dataclass
class UserProgress:
    user_id: str
    course_id: int
    completed_module_ids: List[int] = field(default_factory=list)


class Database:
    """A naive in-memory database used to emulate the Gizmo API behaviour."""

    def __init__(self) -> None:
        self._course_counter = 0
        self._module_counter = 0
        self._question_counter = 0

        self.courses: Dict[int, Course] = {}
        self.modules: Dict[int, Module] = {}
        self.quiz_questions: Dict[int, QuizQuestion] = {}
        self.progress_records: Dict[tuple[str, int], UserProgress] = {}

        self._seed()

    def _seed(self) -> None:
        """Populate the datastore with a baseline set of demo data."""
        demo_course = self.create_course(
            title="Neural Networks Primer",
            description=(
                "Master the foundations of neural networks with short lessons,"
                " animations, and interactive quizzes."
            ),
            tags=["machine-learning", "ai", "beginner"],
        )
        self.create_module(
            course_id=demo_course.id,
            title="Perceptron Intuition",
            content=(
                "Explore the history of the perceptron, how it models a linear"
                " separator, and its connection to modern neural architectures."
            ),
        )
        self.create_module(
            course_id=demo_course.id,
            title="Activation Functions",
            content=(
                "Survey sigmoid, ReLU, and GELU activations through intuitive"
                " animations and real-world examples."
            ),
        )
        self.create_quiz_question(
            course_id=demo_course.id,
            prompt="Which activation function is piecewise linear?",
            options=["Sigmoid", "Tanh", "ReLU", "Softmax"],
            answer_index=2,
        )
        self.create_quiz_question(
            course_id=demo_course.id,
            prompt="What problem does the perceptron struggle with?",
            options=["Linearly separable data", "Non-linear boundaries", "High bias", "Overfitting"],
            answer_index=1,
        )

    # Course operations -------------------------------------------------
    def create_course(self, title: str, description: str, tags: Optional[List[str]] = None) -> Course:
        self._course_counter += 1
        course = Course(
            id=self._course_counter,
            title=title,
            description=description,
            tags=tags or [],
        )
        self.courses[course.id] = course
        return course

    def update_course(self, course_id: int, *, title: str, description: str, tags: List[str]) -> Course:
        course = self.courses[course_id]
        course.title = title
        course.description = description
        course.tags = tags
        return course

    def delete_course(self, course_id: int) -> None:
        self.courses.pop(course_id, None)
        modules_to_remove = [m_id for m_id, module in self.modules.items() if module.course_id == course_id]
        for module_id in modules_to_remove:
            self.modules.pop(module_id, None)
        questions_to_remove = [q_id for q_id, question in self.quiz_questions.items() if question.course_id == course_id]
        for question_id in questions_to_remove:
            self.quiz_questions.pop(question_id, None)
        for key in list(self.progress_records):
            if key[1] == course_id:
                self.progress_records.pop(key, None)

    # Module operations -------------------------------------------------
    def create_module(self, course_id: int, title: str, content: str) -> Module:
        self._module_counter += 1
        module = Module(id=self._module_counter, course_id=course_id, title=title, content=content)
        self.modules[module.id] = module
        return module

    def update_module(self, module_id: int, *, title: str, content: str) -> Module:
        module = self.modules[module_id]
        module.title = title
        module.content = content
        return module

    def delete_module(self, module_id: int) -> None:
        module = self.modules.pop(module_id, None)
        if module:
            for progress in self.progress_records.values():
                if module_id in progress.completed_module_ids:
                    progress.completed_module_ids.remove(module_id)

    # Quiz operations ---------------------------------------------------
    def create_quiz_question(
        self,
        course_id: int,
        prompt: str,
        options: List[str],
        answer_index: int,
    ) -> QuizQuestion:
        self._question_counter += 1
        question = QuizQuestion(
            id=self._question_counter,
            course_id=course_id,
            prompt=prompt,
            options=options,
            answer_index=answer_index,
        )
        self.quiz_questions[question.id] = question
        return question

    def update_quiz_question(
        self,
        question_id: int,
        *,
        prompt: str,
        options: List[str],
        answer_index: int,
    ) -> QuizQuestion:
        question = self.quiz_questions[question_id]
        question.prompt = prompt
        question.options = options
        question.answer_index = answer_index
        return question

    def delete_quiz_question(self, question_id: int) -> None:
        self.quiz_questions.pop(question_id, None)

    # Progress tracking -------------------------------------------------
    def record_module_completion(self, user_id: str, course_id: int, module_id: int) -> UserProgress:
        key = (user_id, course_id)
        progress = self.progress_records.get(key)
        if not progress:
            progress = UserProgress(user_id=user_id, course_id=course_id)
            self.progress_records[key] = progress
        if module_id not in progress.completed_module_ids:
            progress.completed_module_ids.append(module_id)
        return progress

    def get_progress(self, user_id: str, course_id: int) -> UserProgress:
        key = (user_id, course_id)
        progress = self.progress_records.get(key)
        if not progress:
            progress = UserProgress(user_id=user_id, course_id=course_id)
            self.progress_records[key] = progress
        return progress


db = Database()


__all__ = ["Course", "Module", "QuizQuestion", "UserProgress", "db"]
