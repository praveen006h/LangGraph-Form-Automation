from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/hcp_crm.db"
    groq_api_key: str = ""
    llm_model: str = "llama3-8b-8192"

    class Config:
        env_file = ".env"

settings = Settings()
