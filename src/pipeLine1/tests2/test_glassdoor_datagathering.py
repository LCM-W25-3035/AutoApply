import pytest
import time
from unittest.mock import MagicMock
from pipeLine1 import GlassdoorDataGathering as gdg

# Unit test for load_list_from_file function
def test_load_list_from_file(tmp_path):
    test_file = tmp_path / "keywords.txt"
    test_file.write_text("data scientist\nmachine learning engineer\n")

    result = gdg.load_list_from_file(str(test_file))
    assert isinstance(result, list)
    assert result == ["data scientist", "machine learning engineer"]

# Unit test for human_delay function 
def test_human_delay_range(monkeypatch):
    called = []

    def fake_sleep(duration):
        called.append(duration)

    monkeypatch.setattr(time, "sleep", fake_sleep)

    gdg.human_delay(1, 2)
    assert len(called) == 1
    assert 1 <= called[0] <= 2

# Unit test for dismiss_popup function
def dismiss_popup(driver):
    try:
        modal_exists = driver.execute_script("""
            return document.querySelector("div[class*='modal']") !== null;
        """)

        if modal_exists:
            driver.execute_script("""
                var closeButton = document.querySelector("button[data-test='job-alert-modal-close']");
                if (closeButton) {
                    closeButton.click();
                }
            """)
    except Exception as e:
        print(f"Error while checking or removing popup: {e}")
