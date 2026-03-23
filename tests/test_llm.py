"""Tests for the LLM interface module."""

from unittest.mock import MagicMock, patch

from pitchcritic.llm import get_default_caller, make_llm_caller


class TestMakeLlmCaller:
    """Tests for make_llm_caller factory function."""

    @patch("pitchcritic.llm.anthropic.Anthropic")
    def test_creates_caller_with_explicit_key(self, mock_anthropic_cls: MagicMock) -> None:
        caller = make_llm_caller(api_key="test-key-123")
        assert callable(caller)
        mock_anthropic_cls.assert_called_once_with(api_key="test-key-123")

    @patch("pitchcritic.llm.anthropic.Anthropic")
    def test_creates_caller_with_env_key(self, mock_anthropic_cls: MagicMock) -> None:
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "env-key-456"}):
            caller = make_llm_caller(api_key=None)
            assert callable(caller)
            mock_anthropic_cls.assert_called_once_with(api_key="env-key-456")

    @patch("pitchcritic.llm.anthropic.Anthropic")
    def test_caller_invokes_messages_create(self, mock_anthropic_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="LLM response text")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_cls.return_value = mock_client

        caller = make_llm_caller(api_key="key")
        result = caller("system prompt", "user prompt")

        assert result == "LLM response text"
        mock_client.messages.create.assert_called_once_with(
            model="claude-opus-4-6",
            max_tokens=4096,
            system="system prompt",
            messages=[{"role": "user", "content": "user prompt"}],
        )

    @patch("pitchcritic.llm.anthropic.Anthropic")
    def test_caller_returns_text_content(self, mock_anthropic_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Brutal critique here")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_cls.return_value = mock_client

        caller = make_llm_caller(api_key="key")
        result = caller("sys", "usr")
        assert result == "Brutal critique here"


class TestGetDefaultCaller:
    """Tests for the default caller singleton."""

    def setup_method(self) -> None:
        """Reset the module-level default caller before each test."""
        import pitchcritic.llm

        pitchcritic.llm._default_caller = None

    @patch("pitchcritic.llm.make_llm_caller")
    def test_lazily_initializes_default_caller(self, mock_make: MagicMock) -> None:
        mock_make.return_value = MagicMock()
        caller = get_default_caller()
        assert caller is mock_make.return_value
        mock_make.assert_called_once()

    @patch("pitchcritic.llm.make_llm_caller")
    def test_returns_same_caller_on_second_call(self, mock_make: MagicMock) -> None:
        mock_make.return_value = MagicMock()
        caller1 = get_default_caller()
        caller2 = get_default_caller()
        assert caller1 is caller2
        mock_make.assert_called_once()
