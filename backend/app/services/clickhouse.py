
import clickhouse_connect

from backend.app.core.config import settings


def get_clickhouse_client():
    """Create a ClickHouse client using application settings."""
    return clickhouse_connect.get_client(
        host=settings.clickhouse_host,
        port=settings.clickhouse_port,
        username=settings.clickhouse_user,
        password=settings.clickhouse_password,
        database=settings.clickhouse_database,
    )
