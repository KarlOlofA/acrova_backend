from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseModel, Field

from app.services.claude_client import MODEL, get_client

FREE_TEXT_SYSTEM_PROMPT = """Du är en teknisk bedömare som rättar öppna textsvar i ett kunskapsprov.

Du får en fråga, ett facit (ideal_answer) som beskriver vad ett starkt svar \
bör innehålla, och kandidatens faktiska svar.

Bedöm kandidatens svar mot facit på en skala 0-100:
- 0-20: inget relevant innehåll, "vet inte", tomt eller helt fel
- 21-50: ytligt/generiskt svar, buzzwords utan substans, saknar konkret erfarenhet
- 51-75: rimligt svar med viss substans men saknar djup eller precision
- 76-100: starkt svar som visar verklig, konkret erfarenhet i linje med facit

Ge en kort feedback (1-3 meningar) som motiverar poängen - konkret nog att \
en rekryterare utan djup teknisk bakgrund förstår varför."""


class FreeTextGrade(BaseModel):
    score: int = Field(ge=0, le=100)
    feedback: str


def _grade_free_text(question_text: str, ideal_answer: str, candidate_answer: str) -> FreeTextGrade:
    user_message = (
        f"Fråga: {question_text}\n\n"
        f"Facit (ideal_answer): {ideal_answer}\n\n"
        f"Kandidatens svar: {candidate_answer or '(inget svar)'}"
    )
    response = get_client().messages.parse(
        model=MODEL,
        max_tokens=4096,
        system=FREE_TEXT_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
        output_format=FreeTextGrade,
    )
    return response.parsed_output


def score_submission(quiz: dict, answers: list[dict]) -> dict:
    """Score a mixed multiple_choice / free_text submission against a quiz.

    quiz: {"questions": [{"id", "question_type", "correct_answer" (MCQ),
        "ideal_answer" (free_text), ...}, ...]}
    answers: [{"question_id": str, "answer_value": dict}, ...]
        - multiple_choice: answer_value = {"answer": "A"/"B"/"C"/"D"}
        - free_text: answer_value = {"text": "..."}

    free_text questions are graded 0-100 by Claude against ideal_answer,
    normalized to 0-1 for score_awarded. is_correct for free_text is
    score_awarded >= 0.6. Total score is the mean of all score_awarded.
    Free-text grading calls run in parallel.
    """
    questions = quiz.get("questions", [])
    submitted_by_question_id = {a["question_id"]: (a.get("answer_value") or {}) for a in answers}

    results: list[dict] = [None] * len(questions)
    free_text_jobs = []

    for i, question in enumerate(questions):
        question_type = question.get("question_type", "multiple_choice")
        submitted = submitted_by_question_id.get(question["id"], {})

        if question_type == "free_text":
            free_text_jobs.append((i, question, submitted.get("text", "")))
        else:
            submitted_answer = submitted.get("answer")
            is_correct = submitted_answer == question["correct_answer"]
            results[i] = {
                "question_id": question["id"],
                "question_type": "multiple_choice",
                "submitted_answer": submitted_answer,
                "correct_answer": question["correct_answer"],
                "is_correct": is_correct,
                "score_awarded": 1.0 if is_correct else 0.0,
                "ai_feedback": None,
            }

    if free_text_jobs:
        with ThreadPoolExecutor(max_workers=len(free_text_jobs)) as executor:
            futures = {
                executor.submit(
                    _grade_free_text, question["question_text"], question["ideal_answer"], text
                ): (i, question, text)
                for i, question, text in free_text_jobs
            }
            for future, (i, question, text) in futures.items():
                grade = future.result()
                normalized = round(grade.score / 100, 4)
                results[i] = {
                    "question_id": question["id"],
                    "question_type": "free_text",
                    "submitted_answer": text,
                    "correct_answer": None,
                    "is_correct": normalized >= 0.6,
                    "score_awarded": normalized,
                    "ai_feedback": grade.feedback,
                }

    total = len(results)
    correct_count = sum(1 for r in results if r["is_correct"])
    score = round(sum(r["score_awarded"] for r in results) / total, 4) if total else 0.0

    return {"score": score, "correct": correct_count, "total": total, "details": results}
