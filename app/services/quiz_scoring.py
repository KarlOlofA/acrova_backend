def score_submission(quiz: dict, answers: list[dict]) -> dict:
    """Score a submission against a quiz's answer key.

    quiz: {"questions": [{"id": str, "correct_answer": str, ...}, ...]}
    answers: [{"question_id": str, "answer_value": {"answer": str}}, ...]
        (answer_value.answer is expected to be one of "A"/"B"/"C"/"D" for
        multiple_choice questions, matching QuizQuestion.correct_answer.)
    """
    questions = quiz.get("questions", [])
    submitted_by_question_id = {a["question_id"]: a.get("answer_value") for a in answers}

    details = []
    correct_count = 0
    for question in questions:
        question_id = question["id"]
        submitted = submitted_by_question_id.get(question_id) or {}
        submitted_answer = submitted.get("answer")
        is_correct = submitted_answer == question["correct_answer"]
        if is_correct:
            correct_count += 1
        details.append(
            {
                "question_id": question_id,
                "submitted_answer": submitted_answer,
                "correct_answer": question["correct_answer"],
                "is_correct": is_correct,
            }
        )

    total = len(questions)
    score = round(correct_count / total, 4) if total else 0.0
    return {"score": score, "correct": correct_count, "total": total, "details": details}
