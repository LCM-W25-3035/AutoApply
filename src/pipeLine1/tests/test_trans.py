
from unittest.mock import patch
from pipeLine1.trasn import detect_and_translate
import pytest


# Test English-only input
def test_english_only():
    text = "This is an English sentence."
    result = detect_and_translate(text)
    assert result == text

# Test French-only input with mocked translation
@patch("pipeLine1.trasn.GoogleTranslator.translate", return_value="Hello, how are you?")
@patch("pipeLine1.trasn.detect", return_value="fr")
def test_french_translation(mock_detect, mock_translate):
    text = "Bonjour, comment ça va?"
    result = detect_and_translate(text)
    assert "Hello" in result  # Expect the mocked translation

# Test mixed language input
@patch("pipeLine1.trasn.GoogleTranslator.translate", return_value="Hello world")
def test_mixed_input(mock_translate):
    def mock_detect(text):
        return "fr" if "Bonjour" in text else "en"

    with patch("pipeLine1.trasn.detect", side_effect=mock_detect):
        text = "Bonjour le monde. This is English."
        result = detect_and_translate(text)
        assert "Hello world" in result
        assert "This is English." in result

# Test with invalid input (e.g., number or None)
def test_invalid_input():
    text = None
    result = detect_and_translate(text)
    assert result == text
