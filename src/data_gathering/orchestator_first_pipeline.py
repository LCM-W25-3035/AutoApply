"""

OpenAi GPT 4o
Prompt: How can i create a python Orchestrator script

"""

import subprocess

# List of the scripts
scripts = ["src\data_gathering\GlassdoorDataGathering.py","src\data_gathering\optiscript_conc_clean.py" ,"src\data_gathering\job-description-skill-extract.py","src\data_gathering\load_jobs.py",]

def ejecutar_script(script):
    try:
        result = subprocess.run(["python", script], capture_output=True, text=True, check=True)
        print(f" {script} execution successfully :\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f" Error executing {script}:\n{e.stderr}")

for script in scripts:
    ejecutar_script(script)
