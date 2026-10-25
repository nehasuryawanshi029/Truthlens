from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "TRUTHLENS"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Storage and paths
    BASE_DIR: Path = ROOT_DIR
    DATABASE_URL: str = "sqlite:///./data/truthlens.db"
    UPLOAD_DIR: str = "./data/uploads"
    SAMPLE_DIR: str = "./data/samples"
    REFERENCE_DOCS_DIR: str = "./data/reference_documents"
    MAX_UPLOAD_SIZE_MB: int = 15
    ALLOWED_IMAGE_EXTENSIONS: list[str] = [".jpg", ".jpeg", ".png", ".webp"]
    
    # External capability switches & Vision Models
    ENABLE_EXTERNAL_WEB_SEARCH: bool = True  # Live Wikipedia & DuckDuckGo active without API key
    WEB_SEARCH_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    SERPER_API_KEY: str = ""

    ENABLE_EXTERNAL_LLM: bool = False
    LLM_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    VISION_MODEL: str = "gemini-2.5-flash"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""

    @model_validator(mode="after")
    def resolve_paths(self):
        data_dir = self.BASE_DIR / "data"
        if self.DATABASE_URL == "sqlite:///./data/truthlens.db":
            self.DATABASE_URL = "sqlite:///" + (data_dir / "truthlens.db").as_posix()
        if self.UPLOAD_DIR == "./data/uploads":
            self.UPLOAD_DIR = (data_dir / "uploads").as_posix()
        if self.SAMPLE_DIR == "./data/samples":
            self.SAMPLE_DIR = (data_dir / "samples").as_posix()
        if self.REFERENCE_DOCS_DIR == "./data/reference_documents":
            self.REFERENCE_DOCS_DIR = (data_dir / "reference_documents").as_posix()
        return self

    def get_gemini_key(self) -> str:
        return self.GEMINI_API_KEY or self.GOOGLE_API_KEY or self.LLM_API_KEY

    def has_vision_api(self) -> bool:
        return bool(self.get_gemini_key() or self.OPENAI_API_KEY)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

