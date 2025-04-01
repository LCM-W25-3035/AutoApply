# Reference: 
# (OpenAI first prompt, 2025): How do you create a test branch and run case tests in a programming project? Can you give me a guide on how to implement this in Git Hub?
# (OpenAI last prompt, 2025): What does monkey do?

import pytest
import time
from pipeLine1.GlassdoorDataGathering import human_delay

# ----------- Test human_delay (mockea time.sleep) -----------
def test_human_delay_range(monkeypatch):
    called_with = []

    def fake_sleep(x):
        called_with.append(x)

    monkeypatch.setattr(time, "sleep", fake_sleep)

    human_delay(1, 2)
    assert called_with  # Verify that sleep was called
    assert 1 <= called_with[0] <= 2  # It is within the expected range