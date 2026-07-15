from dataclasses import dataclass


@dataclass
class Question:
    id: int
    question: str
    answer: str