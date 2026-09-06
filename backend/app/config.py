from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    google_api_key: str
    groq_api_key: str

    database_url: str = "postgresql+psycopg2://docintel:docintel@postgres:5432/docintel"
    redis_url: str = "redis://redis:6379/0"

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    upload_dir: str = "/app/uploads"
    chroma_host: str = "chroma"
    chroma_port: int = 8000

    embedding_model: str = "gemini-embedding-001"
    groq_model: str = "groq/openai/gpt-oss-120b"

    chunk_size: int = 1000
    chunk_overlap: int = 150
    retrieval_top_k: int = 5


settings = Settings()
