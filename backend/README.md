# Esquenta Backend

Backend FastAPI que orquestra o aquecimento gradual de numeros de WhatsApp por
meio da [Evolution API](https://doc.evolution-api.com/), com Prisma/PostgreSQL,
Redis e workers `arq`.

## Arquitetura

- Servidor 1: API, banco do Esquenta, Redis, workers e `evolution-node1`.
- Servidor 2: `evolution-node2`, PostgreSQL e Redis exclusivos da Evolution.
- Cada numero pertence a um `EvolutionNode`, permitindo distribuir instancias
  entre os dois servidores.

A API interna do Esquenta mantem os termos `session_name` e `node_name` para
compatibilidade com o frontend. Na Evolution, cada sessao corresponde a uma
instancia `WHATSAPP-BAILEYS`.

## Configuracao

Copie `.env.example` para `.env` e configure:

```env
EVOLUTION_IMAGE=evoapicloud/evolution-api:v2.3.7
EVOLUTION_NODE1_API_KEY=troque-esta-chave
EVOLUTION_DB_PASSWORD=troque-esta-senha
EVOLUTION_NODES=[{"name":"kvm8-1","base_url":"http://evolution-node1:8080","api_key":"troque-esta-chave"},{"name":"kvm8-2","base_url":"http://IP_PRIVADO_SERVIDOR_2:8080","api_key":"troque-esta-chave-2"}]
```

O `api_key` de cada item em `EVOLUTION_NODES` deve ser igual ao
`AUTHENTICATION_API_KEY` do respectivo servidor Evolution.

## Deploy

No Servidor 2:

```bash
docker compose -f docker-compose.server2.yml up -d
```

No Servidor 1:

```bash
docker compose up -d --build
```

A Evolution usa banco e Redis proprios. Eles nao devem compartilhar o banco da
aplicacao. A porta HTTP padrao usada nos arquivos Compose e `8080`.

## Fluxo de conexao

1. `POST /api/sessions` cria uma instancia Evolution.
2. O frontend consulta `/api/sessions/pending/{session_name}/status`.
3. O backend converte `open`, `connecting` e `close` nos estados internos.
4. QR Code ou codigo por telefone e obtido pelo endpoint `instance/connect`.
5. Depois de conectado, os workers enviam por `message/sendText`.

As credenciais antigas do WAHA nao sao compativeis. Numeros existentes precisam
ser pareados novamente na Evolution.

## Testes

```bash
pip install -r requirements.txt
prisma generate
pytest
```

Os testes unitarios nao exigem Evolution, PostgreSQL ou Redis em execucao.
