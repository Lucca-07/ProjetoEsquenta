from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações gerais da aplicação, lidas do .env"""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_ENV: str = "development"
    APP_NAME: str = "esquenta-backend"
    LOG_LEVEL: str = "INFO"
    API_PREFIX: str = "/api"

    # Banco de dados
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/esquenta"

    # Redis / filas
    REDIS_URL: str = "redis://localhost:6379/0"

    # WAHA (JSON com a lista de nós/servidores WAHA, ver config/waha.py)
    WAHA_NODES: str = "[]"

    # Segurança simples de API (header X-API-Key)
    API_KEY: str | None = None

    # ---- Parâmetros da rampa de aquecimento ----
    WARMUP_START_MESSAGES: int = 5        # mensagens/dia no dia 0
    WARMUP_INCREMENT: int = 4             # incremento de mensagens por dia
    WARMUP_MAX_MESSAGES: int = 120        # teto diário de mensagens por número
    WARMUP_MAX_DAYS: int = 30             # dias até considerar o número "aquecido"

    # Janela de funcionamento (horário local do servidor) para evitar padrão robótico
    WORK_HOUR_START: int = 8
    WORK_HOUR_END: int = 22

    # Intervalo mínimo/máximo (segundos) entre disparos de mensagens de um mesmo número
    MESSAGE_MIN_DELAY_SECONDS: int = 45
    MESSAGE_MAX_DELAY_SECONDS: int = 240

    # A cada quantos segundos o scheduler roda o ciclo de verificação
    SCHEDULER_INTERVAL_SECONDS: int = 60


settings = Settings()
