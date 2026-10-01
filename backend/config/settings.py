import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    MONGODB_URI: str = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/childsafe')
    JWT_SECRET: str = os.getenv('JWT_SECRET', 'dev-secret-key-change-in-production')
    JWT_EXPIRE_MINUTES: int = int(os.getenv('JWT_EXPIRE_MINUTES', '1440'))
    JWT_ALGORITHM: str = 'HS256'
    LLM_API_KEY: str = os.getenv('LLM_API_KEY', '')
    LLM_MODEL: str = os.getenv('LLM_MODEL', 'gpt-4')
    FRONTEND_URL: str = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    BACKEND_URL: str = os.getenv('BACKEND_URL', 'http://localhost:8000')
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'development')
    
    RISK_WEIGHTS: dict = {
        'rule': 0.20,
        'ml': 0.25,
        'context': 0.25,
        'behaviour': 0.20,
        'llm': 0.10
    }
    RISK_THRESHOLDS: dict = {
        'safe': 29,
        'moderate': 59,
        'high': 79,
        'critical': 100
    }
    ALERT_COOLDOWN_MINUTES: int = 30

settings = Settings()
