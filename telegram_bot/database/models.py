from dataclasses import dataclass, field
from typing import List

@dataclass
class Question:
    id: int
    section: str
    question: str
    answer: str
    wrong_answers: List[str] = field(default_factory=list)