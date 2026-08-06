from unittest.mock import MagicMock, patch

import pytest

from question_generator import _parse_and_validate, generate_question


class TestParseAndValidate:
    """Test the validation logic without calling the real API."""

    def test_valid_json_with_question_and_tip(self):
        """Valid JSON with question and tip returns both."""
        response = '{"question": "What makes you proud?", "tip": "Helps kids recognize strengths."}'
        result = _parse_and_validate(response)
        assert result == ("What makes you proud?", "Helps kids recognize strengths.")

    def test_json_with_markdown_fences(self):
        """JSON wrapped in markdown fences is cleaned and parsed."""
        response = '```json\n{"question": "What makes you proud?", "tip": "Helps kids recognize strengths."}\n```'
        result = _parse_and_validate(response)
        assert result == ("What makes you proud?", "Helps kids recognize strengths.")

    def test_invalid_json_returns_none(self):
        """Invalid JSON returns None."""
        response = '{ not json }'
        result = _parse_and_validate(response)
        assert result is None

    def test_missing_question_field_returns_none(self):
        """Missing 'question' field returns None."""
        response = '{"tip": "..."}'
        result = _parse_and_validate(response)
        assert result is None

    def test_yes_no_starter_returns_none(self):
        """Question starting with yes/no word returns None."""
        for starter in ["Did", "Do", "Are", "Is", "Can", "Would"]:
            response = f'{{"question": "{starter} you like this?", "tip": "tip"}}'
            result = _parse_and_validate(response)
            assert result is None, f"Failed for starter '{starter}'"

    def test_no_question_mark_returns_none(self):
        """Question without a question mark returns None."""
        response = '{"question": "Tell me about your day", "tip": "tip"}'
        result = _parse_and_validate(response)
        assert result is None

    def test_valid_open_ended_questions(self):
        """Open-ended question starters are accepted."""
        for starter in ["What", "Tell me about", "How did"]:
            response = f'{{"question": "{starter} something?", "tip": "tip"}}'
            result = _parse_and_validate(response)
            assert result is not None, f"Failed for starter '{starter}'"


class TestGenerateQuestion:
    """Test question generation with mocked Anthropic client."""

    @patch("question_generator.Anthropic")
    def test_generate_question_success(self, mock_anthropic_class):
        """Successfully generates a question."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"question": "What makes you happy?", "tip": "Reflection helps."}')]
        mock_client.messages.create.return_value = mock_response

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            result = generate_question(theme="courage", recent_questions=[])

        assert result == ("What makes you happy?", "Reflection helps.")

    @patch("question_generator.Anthropic")
    def test_generate_question_retries_on_invalid(self, mock_anthropic_class):
        """Retries when validation fails."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        invalid_response = MagicMock()
        invalid_response.content = [MagicMock(text='{"question": "Did you have fun?", "tip": "tip"}')]

        valid_response = MagicMock()
        valid_response.content = [MagicMock(text='{"question": "What made you smile?", "tip": "tip"}')]

        mock_client.messages.create.side_effect = [invalid_response, valid_response]

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            result = generate_question(theme="courage", recent_questions=[], max_retries=1)

        assert result == ("What made you smile?", "tip")
        assert mock_client.messages.create.call_count == 2

    def test_generate_question_no_api_key_raises(self):
        """Missing API key raises RuntimeError."""
        with patch.dict("os.environ", {}, clear=True), pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
            generate_question(theme="courage", recent_questions=[])

    @patch("question_generator.Anthropic")
    def test_generate_question_exhausts_retries(self, mock_anthropic_class):
        """Exhausting retries raises RuntimeError."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        bad_response = MagicMock()
        bad_response.content = [MagicMock(text='{"question": "Did you?", "tip": "tip"}')]
        mock_client.messages.create.return_value = bad_response

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}), pytest.raises(RuntimeError, match="Failed to generate"):
            generate_question(theme="courage", recent_questions=[], max_retries=1)
