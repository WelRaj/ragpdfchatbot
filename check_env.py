from dotenv import load_dotenv, dotenv_values
from pathlib import Path

env_path = Path(__file__).resolve().parent / ".env"

print("File exists:", env_path.exists())

config = dotenv_values(env_path)

print("Variables found:", list(config.keys()))
print("API key loaded:", bool(config.get("GOOGLE_API_KEY")))