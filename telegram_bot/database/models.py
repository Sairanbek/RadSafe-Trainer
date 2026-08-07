class Question:
    def __init__(
        self,
        id,
        section,
        subsection,
        question,
        answer,
        wrong_answers
    ):
        self.id = id
        self.section = section
        self.subsection = subsection
        self.question = question
        self.answer = answer
        self.wrong_answers = wrong_answers


class User:
    def __init__(
        self,
        user_id,
        first_name=None,
        username=None,
        first_seen=None,
        last_seen=None,
        visits=0
    ):
        self.user_id = user_id
        self.first_name = first_name
        self.username = username
        self.first_seen = first_seen
        self.last_seen = last_seen
        self.visits = visits