import base64

import anthropic

from app.core.config import settings
from app.schemas.test import GeneratedTest

MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """Du är en teknisk rekryterare som bygger kunskapsprov.

Du får en kandidats CV. Identifiera de konkreta skills, teknologier, roller \
och erfarenhetspåståenden kandidaten gör (t.ex. "5 år med AWS Lambda", \
"byggde betalningssystem i Go", "tech lead för ett team på 8").

Generera sedan 5-8 flervalsfrågor som testar DJUPET i just dessa påståenden \
- inte allmän trivia om teknologin. Frågorna ska vara sådana att bara någon \
som faktiskt har den påstådda erfarenheten rimligen kan svara rätt \
(praktiska gotchas, avvägningar, konkret beteende i verktyget/rollen).

Varje fråga ska ha exakt 4 svarsalternativ där exakt ett är korrekt, samt en \
kort förklaring (1-2 meningar) till varför det rätta svaret är rätt - så att \
en rekryterare utan djup teknisk bakgrund förstår varför svaret visar \
(eller inte visar) verklig erfarenhet."""

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client


def generate_test_from_cv(*, cv_text: str | None, pdf_bytes: bytes | None) -> GeneratedTest:
    if not cv_text and not pdf_bytes:
        raise ValueError("Either cv_text or pdf_bytes must be provided")

    content: list[dict] = []
    if pdf_bytes:
        content.append(
            {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": base64.standard_b64encode(pdf_bytes).decode("utf-8"),
                },
            }
        )
        content.append({"type": "text", "text": "Här är kandidatens CV (PDF). Generera provet."})
    else:
        content.append({"type": "text", "text": f"Här är kandidatens CV:\n\n{cv_text}"})

    response = _get_client().messages.parse(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
        output_format=GeneratedTest,
    )

    return response.parsed_output
