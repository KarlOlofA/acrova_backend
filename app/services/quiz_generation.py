from typing import Literal

from pydantic import BaseModel, Field

from app.services.claude_client import MODEL, get_client

SYSTEM_PROMPT = """Du är en teknisk rekryterare som bygger kunskapsprov.

Du får en lista med "claims" - konkreta skills/teknologier/erfarenhetspåståenden \
extraherade ur en kandidats CV (varje claim har skill, evidence och confidence) \
- samt ett requirements_spec som beskriver rollen rekryteraren tillsätter.

Generera ett prov med exakt 3 flervalsfrågor (multiple_choice) och exakt 2 \
öppna textfrågor (free_text), båda typerna som testar DJUPET i claims-listan, \
prioriterat mot det som är relevant för rollen i requirements_spec - inte \
allmän trivia om teknologin.

Om claims-listan är tom, generera istället frågor baserat enbart på \
requirements_spec (allmän kompetensvalidering för rollen).

FLERVALSFRÅGOR: exakt 4 svarsalternativ (A-D) där exakt ett är korrekt. \
Frågan ska vara sådan att bara någon som faktiskt har den påstådda \
erfarenheten rimligen kan svara rätt (praktiska gotchas, avvägningar, \
konkret beteende i verktyget/rollen).

TEXTFRÅGOR: öppna frågor utan svarsalternativ, med ett ideal_answer (Claudes \
facit i löptext, det en bedömare skulle leta efter i ett bra svar). Frågorna \
ska testa djup som INTE kan fejkas genom att googla eller slänga in \
buzzwords - t.ex. "beskriv en avvägning du gjorde", "vad gick fel och varför", \
"förklara varför X händer i praktiken" snarare än definitionsfrågor.

Varje fråga (oavsett typ) ska ha en skill_tag som anger vilken skill/teknologi \
frågan testar - använd samma skill-namn som i claims-listan när frågan kommer \
från en specifik claim."""


class MCQOptions(BaseModel):
    A: str
    B: str
    C: str
    D: str


class MCQQuestion(BaseModel):
    question_text: str
    options: MCQOptions
    correct_answer: Literal["A", "B", "C", "D"]
    skill_tag: str


class FreeTextQuestion(BaseModel):
    question_text: str
    ideal_answer: str
    skill_tag: str


class GeneratedQuiz(BaseModel):
    mcq_questions: list[MCQQuestion] = Field(min_length=3, max_length=3)
    free_text_questions: list[FreeTextQuestion] = Field(min_length=2, max_length=2)


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
    generated = response.parsed_output

    questions = []
    for q in generated.mcq_questions:
        questions.append(
            {
                "question_text": q.question_text,
                "question_type": "multiple_choice",
                "options": q.options.model_dump(),
                "correct_answer": q.correct_answer,
                "ideal_answer": None,
                "skill_tag": q.skill_tag,
            }
        )
    for q in generated.free_text_questions:
        questions.append(
            {
                "question_text": q.question_text,
                "question_type": "free_text",
                "options": None,
                "correct_answer": None,
                "ideal_answer": q.ideal_answer,
                "skill_tag": q.skill_tag,
            }
        )

    for i, question in enumerate(questions):
        question["order_index"] = i

    return {"questions": questions}
