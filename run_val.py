import subprocess
import os
import sys

def main():
    venv_python = os.path.join("venv", "Scripts", "python.exe")
    openenv_script = os.path.join("venv", "Scripts", "openenv")
    
    if os.path.exists(openenv_script):
        # run openenv validate
        try:
            res = subprocess.run([openenv_script, "validate"], capture_output=True, text=True)
            with open("val_out.txt", "w", encoding="utf-8") as f:
                f.write(f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}\nRC: {res.returncode}")
        except Exception as e:
            with open("val_out.txt", "w", encoding="utf-8") as f:
                f.write(f"Exception: {str(e)}")
    else:
        with open("val_out.txt", "w", encoding="utf-8") as f:
            f.write("openenv script not found in venv/Scripts/")

if __name__ == "__main__":
    main()
