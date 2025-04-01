import pytest
from unittest.mock import patch, MagicMock
from pipeLine1.orchestator_first_pipeline import ejecutar_script
import subprocess

# --------- Test when script runs successfully ---------
@patch("pipeLine1.orchestator_first_pipeline.subprocess.run")
def test_ejecutar_script_success(mock_run, capsys):
    mock_run.return_value = MagicMock(stdout="Script executed successfully", returncode=0)

    ejecutar_script("fake_script.py")
    captured = capsys.readouterr()

    assert "execution successfully" in captured.out
    assert "Script executed successfully" in captured.out
    mock_run.assert_called_once_with(["python", "fake_script.py"], capture_output=True, text=True, check=True)

# --------- Test when script fails ---------
@patch("pipeLine1.orchestator_first_pipeline.subprocess.run")
def test_ejecutar_script_failure(mock_run, capsys):
    mock_run.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd="python fake_script.py",
        stderr="Script failed with error"
    )

    ejecutar_script("fake_script.py")
    captured = capsys.readouterr()

    assert "Error executing" in captured.out
    assert "Script failed with error" in captured.out
