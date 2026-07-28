from prisma import Prisma

# Instância única do client Prisma, reaproveitada em toda a aplicação
# (API e workers arq).
db = Prisma(auto_register=True)


async def connect_db() -> None:
    if not db.is_connected():
        await db.connect()


async def disconnect_db() -> None:
    if db.is_connected():
        await db.disconnect()
