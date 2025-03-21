import pytest
import time
from unittest.mock import MagicMock
from pipeLine1.GlassdoorDataGathering import dismiss_popup

def test_dismiss_popup_executes_js():
    driver = MagicMock()
    # Pretends that a modal is present
    driver.execute_script.side_effect = [True, None]

    dismiss_popup(driver)

    # Ensures that execute_script was called (once to check the modal and once to close it)
    assert driver.execute_script.call_count >= 2