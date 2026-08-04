# Esquenta Backend

Backend FastAPI que orquestra aquecimento de numeros de WhatsApp pela
[Evolution Go](https://github.com/evolution-foundation/evolution-go), com
Prisma/PostgreSQL, Redis e workers `arq`.

## Arquitetura

- Servidor 1: API, banco do Esquenta, Redis, workers e `evolution-go-node1`.
- Servidor 2: `evolution-go-node2` e PostgreSQL proprio.
- Cada numero pertence a um `EvolutionNode`, permitindo distribuir instancias.

O frontend continua usando `session_name`, `node_name` e os endpoints internos
`/api/sessions`. O backend traduz esse contrato para a Evolution Go.

## Configuracao

```env
EVOLUTION_GO_IMAGE=evoapicloud/evolution-go:0.7.1
EVOLUTION_GO_NODE1_API_KEY=troque-esta-chave
EVOLUTION_GO_DB_PASSWORD=troque-esta-senha
EVOLUTION_GO_NODES=[{"name":"kvm8-1","base_url":"http://evolution-go-node1:8080","api_key":"troque-esta-chave"},{"name":"kvm8-2","base_url":"http://IP_PRIVADO_SERVIDOR_2:8080","api_key":"troque-esta-chave-2"}]
```

O `api_key` de cada no deve ser igual ao `GLOBAL_API_KEY` do respectivo
container. O backend deriva um token diferente e estavel para cada instancia.

## Licenca

A Evolution Go exige ativacao na primeira execucao. Depois de subir o servidor,
abra `http://localhost:8080/manager/login`, informe a URL da API e a
`EVOLUTION_GO_NODE1_API_KEY`, e conclua o registro. Enquanto nao estiver ativa,
os endpoints de negocio retornam HTTP 503.

Tambem e possivel definir `EVOLUTION_OPERATOR_EMAIL` com um email previamente
registrado para tentar ativacao automatica na inicializacao.

## Deploy

Servidor 2:

```bash
docker compose -f docker-compose.server2.yml up -d
```

Servidor 1:

```bash
docker compose up -d --build
```

O arquivo `evolution-go-init.sql` cria os bancos `evogo_auth` e `evogo_users`.

## Endpoints usados

- `POST /instance/create`
- `GET /instance/status`
- `GET /instance/qr`
- `POST /instance/pair`
- `POST /instance/reconnect`
- `DELETE /instance/delete/{instanceId}`
- `POST /send/text`

As sessoes da Evolution API Node nao sao compativeis com Evolution Go. Os
numeros existentes precisam ser pareados novamente.

## Testes

```bash
pip install -r requirements.txt
prisma generate
pytest
```
