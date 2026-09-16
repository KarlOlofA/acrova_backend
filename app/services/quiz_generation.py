from typing import Literal

from pydantic import BaseModel, Field

from app.services.claude_client import MODEL, get_client

SYSTEM_PROMPT = """Du är en teknisk rekryterare som bygger kunskapsprov.

Du får en lista med "claims" - konkreta skills/teknologier/erfarenhetspåståenden \
extraherade ur en kandidats CV (varje claim har skill, evidence och confidence) \
- samt ett requirements_spec som beskriver rollen rekryteraren tillsätter.

Generera 5-8 flervalsfrågor som testar DJUPET i claims-listan, prioriterat mot \
det som är relevant för rollen i requirements_spec - inte allmän trivia om \
teknologin. Frågorna ska vara sådana att bara någon som faktiskt har den \
påstådda erfarenheten rimligen kan svara rätt (praktiska gotchas, avvägningar, \
konkret beteende i verktyget/rollen).

Om claims-listan är tom, generera istället frågor baserat enbart på \
requirements_spec (allmän kompetensvalidering för rollen).

Varje fråga ska ha exakt 4 svarsalternativ (A-D) där exakt ett är korrekt, samt \
en skill_tag som anger vilken skill/teknologi frågan testar - använd samma \
skill-namn som i claims-listan när frågan kommer från en specifik claim."""


class QuestionOptions(BaseModel):
    A: str
    B: str
    C: str
    D: str


class GeneratedQuizQuestion(BaseModel):
    question_text: str
    options: QuestionOptions
    correct_answer: Literal["A", "B", "C", "D"]
    skill_tag: str


class GeneratedQuiz(BaseModel):
    questions: list[GeneratedQuizQuestion] = Field(min_length=5, max_length=8)


def generate_quiz(profile: dict, requirements_spec: dict) -> dict:
    claims = profile.get("claims", [])

    user_message = f"requirements_spec:\n{requirements_spec}\n\nclaims:\n{claims}"

    response = get_client().messages.parse(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
        output_format=GeneratedQuiz,
    )

    questions = [
        {
            "order_index": i,
            "question_text": q.question_text,
            "question_type": "multiple_choice",
            "options": q.options.model_dump(),
            "correct_answer": q.correct_answer,
            "skill_tag": q.skill_tag,
        }
        for i, q in enumerate(response.parsed_output.questions)
    ]

    return {"questions": questions}
