import base64
from typing import Literal

from pydantic import BaseModel

from app.services import supabase_storage
from app.services.claude_client import MODEL, get_client

SYSTEM_PROMPT = """Du är en teknisk rekryterare som granskar kandidat-CV:n.

Läs CV:t och identifiera de konkreta skills, teknologier, roller och \
erfarenhetspåståenden kandidaten gör (t.ex. "5 år med AWS Lambda", \
"byggde betalningssystem i Go", "tech lead för ett team på 8").

För varje påstående, ange:
- skill: teknologin/kompetensen/rollen påståendet handlar om
- evidence: det konkreta påståendet ur CV:t som stödjer det (kort citat/parafras)
- confidence: "high" om påståendet är specifikt och konkret (t.ex. antal år, \
  skala, en namngiven teknologi i ett tydligt sammanhang), "medium" om det är \
  rimligt specifikt men saknar detaljer, "low" om det är vagt (t.ex. "bekant \
  med molntjänster" utan detaljer)."""


class ExtractedClaim(BaseModel):
    skill: str
    evidence: str
    confidence: Literal["high", "medium", "low"]


class ExtractedClaims(BaseModel):
    claims: list[ExtractedClaim]


def parse_cv(storage_path: str) -> list[dict]:
    """Download the CV PDF from Supabase Storage at storage_path and extract claims."""
    pdf_bytes = supabase_storage.download_object(storage_path)

    response = get_client().messages.parse(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": base64.standard_b64encode(pdf_bytes).decode("utf-8"),
                        },
                    },
                    {"type": "text", "text": "Här är kandidatens CV. Extrahera claims."},
                ],
            }
        ],
        output_format=ExtractedClaims,
    )

    return [claim.model_dump() for claim in response.parsed_output.claims]
