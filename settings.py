from pathlib import Path

from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    token: str
    database_url: str
    mode: str = "dev"
    log_dir: Path = Path('logs')
