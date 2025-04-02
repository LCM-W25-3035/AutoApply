"""

OpenAi GPT 4o
Prompt: How can i create a python Orchestrator script that can execute different scripts in order and in parallel

"""
import subprocess
import os

# Scripts to run in parallel (simultaneously)
parallel_scripts = [
    "src/data_gathering/GlassdoorDataGathering.py",
    "src/data_gathering/JobSpy.py"
    
]

# Scripts to run in sequence (one after another)
sequential_scripts = [
    "src/data_gathering/JobSpy_Octoparse_combined_jobs.py",
    "src/data_gathering/conc_clean.py",
    "src/data_gathering/trans.py",
    "src/data_gathering/job-description-skill-extract.py",
    "src/data_gathering/load_jobs.py",
]

def ejecutar_script(script):
    try:
        result = subprocess.run(["python", script], capture_output=True, text=True, check=True)
        print(f"[✔] {script} executed successfully:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"[✖] Error executing {script}:\n{e.stderr}")

def run_parallel(scripts):
    processes = []
    for script in scripts:
        print(f"[→] Starting {script}...")
        p = subprocess.Popen(["python", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        processes.append((script, p))

    # Wait for all parallel scripts to finish
    for script, p in processes:
        stdout, stderr = p.communicate()
        if p.returncode == 0:
            print(f"[✔] {script} completed:\n{stdout}")
        else:
            print(f"[✖] {script} failed:\n{stderr}")

if __name__ == "__main__":
    print("Running parallel scripts...\n")
    run_parallel(parallel_scripts)

    print("\nRunning sequential scripts...\n")
    for script in sequential_scripts:
        ejecutar_script(script)

    print("\n All scripts completed.")
