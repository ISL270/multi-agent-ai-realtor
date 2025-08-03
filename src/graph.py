import os

from dotenv import load_dotenv

from agents.supervisor.supervisor import create_ai_realtor

# Explicitly load .env from project root (ensures environment variables are available for local/dev runs)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"))

supervisor = create_ai_realtor().compile()
