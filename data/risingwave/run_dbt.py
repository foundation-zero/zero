from dotenv import load_dotenv
import subprocess

load_dotenv(dotenv_path=".env")

subprocess.run(["poetry", "run", "dbt", "compile"])

subprocess.run(["poetry", "run", "dbt", "run"])
