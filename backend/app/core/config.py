
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    """Configuration loaded from environment variables."""

    clickhouse_host: str = os.getenv("CLICKHOUSE_HOST", "localhost")
    clickhouse_port: int = int(os.getenv("CLICKHOUSE_PORT", "8123"))
    clickhouse_database: str = os.getenv(
        "CLICKHOUSE_DATABASE", "cognistream"
    )
    clickhouse_user: str = os.getenv("CLICKHOUSE_USER", "cogni")
    clickhouse_password: str = os.getenv("CLICKHOUSE_PASSWORD", "")


settings = Settings()
