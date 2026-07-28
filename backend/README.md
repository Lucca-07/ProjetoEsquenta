# Esquenta Backend — Sistema de Aquecimento de Números

Backend em Python (FastAPI + Prisma/Postgres + Redis + arq) que orquestra o
aquecimento gradual de números de WhatsApp via [WAHA](https://waha.devlike.pro/),
distribuído em dois servidores KVM8 da Hostinger.

## Arquitetura

- **Servidor 1**: API (FastAPI), Postgres, Redis, workers `arq` (fila +
  cron) e uma instância WAHA local (`waha-node1`) hospedando uma **menor
  parte** dos números.
- **Servidor 2**: apenas instância(s) WAHA (`waha-node2`), hospedando o
  **restante** dos números. A API no Servidor 1 fala com ela via HTTP.

Cada `Number` (chip) fica associado a um `WahaNode` no banco — o backend
escolhe automaticamente qual servidor WAHA usar para cada envio.

## Como funciona o aquecimento

1. Cada número começa com uma meta diária pequena (`WARMUP_START_MESSAGES`),
   que cresce (`WARMUP_INCREMENT`/dia) até um teto (`WARMUP_MAX_MESSAGES`),
   ao longo de `WARMUP_MAX_DAYS`.
2. A cada minuto (cron do `arq`), o `scheduler_service` verifica todos os
   números ativos, avança o dia quando necessário e — se ainda não bateu a
   meta diária — escolhe um parceiro (`pairing_service`), gera um texto via
   spintax e agenda o envio com um atraso aleatório
   (`MESSAGE_MIN/MAX_DELAY_SECONDS`), só dentro do horário comercial
   configurado (`WORK_HOUR_START/END`).
3. O job `send_message_job` efetivamente dispara a mensagem pelo nó WAHA
   correto e registra o resultado (`Message` + `WarmupLog`).

## Deploy

### 1. Servidor 2 (só WAHA)

```bash
scp docker-compose.server2.yml usuario@SERVIDOR_2:/opt/esquenta/
ssh usuario@SERVIDOR_2
cd /opt/esquenta
docker compose -f docker-compose.server2.yml up -d
```

Anote o IP público (ou da VPN/rede privada) do Servidor 2.

### 2. Servidor 1 (tudo mais)

```bash
cp .env.example .env
# edite .env: DATABASE_URL, REDIS_URL, WAHA_NODES (kvm8-2 -> IP do Servidor 2), etc.
docker compose up -d --build
```

O serviço `api` roda `prisma db push` automaticamente no start para criar as
tabelas. Em produção, prefira gerar migrations (`prisma migrate deploy`) em
vez de `db push`.

### 3. Registrar os números

```bash
# Cria a sessão no nó kvm8-1 (local) ou kvm8-2 (remoto)
curl -X POST http://SERVIDOR_1:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"phone": "5511999999999", "node_name": "kvm8-1"}'

# Escaneie o QR code
curl http://SERVIDOR_1:8000/api/sessions/{id}/status

# Ative o aquecimento
curl -X POST http://SERVIDOR_1:8000/api/warmup/{id}/start
```

## Rodando localmente / testes

```bash
pip install -r requirements.txt --break-system-packages
prisma generate
pytest
```

Os testes em `tests/` cobrem apenas lógica pura (spintax, curva de rampa,
validação de schema) — não exigem Postgres/Redis/WAHA rodando.

## Ajustando a rampa de aquecimento

Todos os parâmetros ficam no `.env` (`WARMUP_START_MESSAGES`,
`WARMUP_INCREMENT`, `WARMUP_MAX_MESSAGES`, `WARMUP_MAX_DAYS`,
`WORK_HOUR_START/END`, `MESSAGE_MIN/MAX_DELAY_SECONDS`,
`SCHEDULER_INTERVAL_SECONDS`) — não é necessário alterar código para
recalibrar a velocidade do aquecimento.
