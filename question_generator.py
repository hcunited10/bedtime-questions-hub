import json
import os
import re

from anthropic import Anthropic


def _strip_dashes(text: str) -> str:
    """Remove em-dashes and en-dashes, replacing with commas."""
    text = text.replace(" — ", ", ").replace("—", ", ")
    text = text.replace(" – ", ", ").replace("–", ", ")
    return text


def _parse_and_validate(raw_text: str) -> tuple[str, str] | None:
    """Parse and validate LLM response. Returns (question, tip) or None if invalid."""
    cleaned = re.sub(r"```json\s*|\s*```", "", raw_text).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None
    if "question" not in data or "tip" not in data:
        return None
    if not isinstance(data["question"], str) or not isinstance(data["tip"], str):
        return None
    if not data["question"] or not data["tip"]:
        return None

    question = data["question"]
    tip = data["tip"]

    banned_starts = r"^(did|do|does|are|is|am|can|could|would|will|was|were|have|has|should)\b"
    if re.match(banned_starts, question.strip(), re.IGNORECASE):
        return None

    if not question.rstrip().endswith("?"):
        return None

    question = _strip_dashes(question)
    tip = _strip_dashes(tip)

    return (question, tip)


def generate_question(
    theme: str, recent_questions: list[str], max_retries: int = 1
) -> tuple[str, str]:
    """
    Generate an open-ended confidence-building question for young children (ages ~4-10).
    Returns (question, tip). Raises RuntimeError if validation fails after retries.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable not set")

    client = Anthropic(api_key=api_key)

    recent_questions_text = "\n".join(f"  - {q}" for q in recent_questions[-10:])
    if not recent_questions_text:
        recent_questions_text = "  (none yet)"

    theme_title = " ".join(word.capitalize() for word in theme.split("-"))

    system_prompt = f"""You are helping parents build their young child's confidence and self-esteem through a short bedtime conversation. The child is roughly ages 4-10, and may be any gender.

Generate ONE open-ended bedtime question for tonight, themed around: {theme_title}.

CRITICAL RULES:
1. The question MUST be open-ended (NOT answerable with just "yes" or "no").
2. NEVER start the question with: Did, Do, Does, Are, Is, Am, Can, Could, Would, Will, Was, Were, Have, Has, Should.
3. Good starters: "What...", "Tell me about...", "How did...", "What was it like when...", "Describe...".
4. The question MUST end with a question mark (?).
5. Use commas for name vocatives (e.g., "David, what..."), NEVER em-dashes or en-dashes.
6. Keep it simple, warm, age-appropriate for a 4-10 year old at bedtime.
7. One sentence is ideal; two short sentences maximum.

The question should help the child reflect on their day/feelings and recognize their strengths related to {theme_title}.

Do NOT repeat any of these recent questions:
{recent_questions_text}

Also write a ONE-sentence parent tip (under 30 words) explaining why this helps build confidence. No jargon, no em-dashes.

Respond ONLY with valid JSON (no markdown fences, no extra text):
{{"question": "...", "tip": "..."}}"""

    for attempt in range(max_retries + 1):
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            messages=[
                {"role": "user", "content": system_prompt}
            ]
        )

        raw_response = message.content[0].text

        result = _parse_and_validate(raw_response)
        if result:
            return result

        if attempt < max_retries:
            system_prompt += "\n\nYour previous attempt was invalid. Please try again, strictly following the JSON structure and rules."

    raise RuntimeError(
        f"Failed to generate a valid question after {max_retries + 1} attempts"
    )
