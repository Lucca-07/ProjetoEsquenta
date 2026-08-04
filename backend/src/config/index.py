from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações gerais da aplicação, lidas do .env"""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_ENV: str = "development"
    APP_NAME: str = "esquenta-backend"
    LOG_LEVEL: str = "INFO"
    API_PREFIX: str = "/api"
    AUTH_SECRET: str = "change-this-auth-secret"
    AUTH_TOKEN_HOURS: int = 12
    ADMIN_NAME: str = "Administrador"
    ADMIN_EMAIL: str = "admin@esquenta.local"
    ADMIN_PASSWORD: str = "Admin@123"

    # Banco de dados
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/esquenta"

    # Redis / filas
    REDIS_URL: str = "redis://localhost:6379/0"

    # Evolution Go (JSON com a lista de nos/servidores)
    EVOLUTION_GO_NODES: str = "[]"

    # Segurança simples de API (header X-API-Key)
    API_KEY: str | None = None

    # ---- Parâmetros da rampa de aquecimento ----
    WARMUP_START_MESSAGES: int = 5        # mensagens/dia no dia 0
    WARMUP_INCREMENT: int = 4             # incremento de mensagens por dia
    WARMUP_MAX_MESSAGES: int = 120        # teto diário de mensagens por número
    WARMUP_MAX_DAYS: int = 30             # dias até considerar o número "aquecido"

    # Janela de funcionamento (horário local do servidor) para evitar padrão robótico

    # Intervalo mínimo/máximo (segundos) entre disparos de mensagens de um mesmo número

    # A cada quantos segundos o scheduler roda o ciclo de verificação
    SCHEDULER_INTERVAL_SECONDS: int = 60


settings = Settings()
