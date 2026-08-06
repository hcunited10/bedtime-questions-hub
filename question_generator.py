import json
import os
import re

from anthropic import Anthropic


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

Rules:
- The question must be open-ended — it must NOT be answerable with just "yes" or "no".
  Do not start with words like "Did", "Do", "Are", "Is", "Can", "Would", "Were", "Have".
  Prefer starters like "What", "Tell me about", "How did", "What was it like when".
- Tone: warm, simple, concrete — vocabulary and sentence structure appropriate for a young child to understand and answer out loud at bedtime. One sentence, or two short sentences at most.
- The question should invite the child to reflect on something specific from their day or their feelings, in a way that helps them recognize their own strengths, effort, or positive qualities related to the theme of {theme_title}.
- Do not repeat or closely paraphrase any of these recently-asked questions:
{recent_questions_text}

Also write a ONE-sentence tip for the parents (not shown to the child), explaining briefly why this kind of question helps build a child's confidence/self-esteem. Keep it under 30 words, plain language, no jargon.

Respond with ONLY a JSON object, no markdown fences, no extra text, in exactly this shape:
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
