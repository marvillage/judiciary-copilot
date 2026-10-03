from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "casegraph-dev"

    ollama_base_url: str = "http://localhost:11434"
    embed_model: str = "bge-m3"
    chat_model: str = "llama3.2:3b"

    data_dir: Path = Path("./data")
    ecourts_sample_rows: int = 50000
    judgments_sample_rows: int = 2000
    refresh_interval_minutes: int = 60

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def import_dir(self) -> Path:
        return self.data_dir / "import"


settings = Settings()
