# Projeto Esquenta

Plataforma web para conectar, organizar e aquecer números de WhatsApp de forma gradual. O sistema cria conversas automatizadas entre os números cadastrados, distribui os envios ao longo do tempo e oferece uma interface para acompanhar sessões, progresso, mensagens e falhas.

> O uso de automações no WhatsApp deve respeitar os termos da plataforma, a legislação aplicável e o consentimento dos envolvidos. Este projeto não garante que números fiquem imunes a bloqueios.

## Funcionalidades

- Autenticação com token e controle de acesso por perfil (`ADMIN` e `USER`);
- conexão de números por QR Code ou código de pareamento;
- acompanhamento do estado das instancias Evolution;
- criação de grupos de aquecimento com múltiplos números;
- configuração de intervalo entre mensagens e duração do aquecimento;
- início, pausa e encerramento individual ou em lote;
- evolução gradual da quantidade diária de mensagens;
- escolha automática dos pares que conversam entre si;
- geração de mensagens variadas a partir de frases em formato spintax;
- agendamento e processamento assíncrono de mensagens com Redis e ARQ;
- distribuicao das instancias entre diferentes nos Evolution;
- painel com números conectados, em aquecimento e concluídos;
- busca, ordenação e seleção em lote de números;
- histórico de mensagens e grupos, com filtros por período, telefone e status;
- indicadores de mensagens enviadas, pendentes e com falha;
- administração de usuários e permissões;
- API documentada automaticamente pelo FastAPI.

## Tecnologias

| Camada          | Tecnologias                                  |
| --------------- | -------------------------------------------- |
| Frontend        | React 19, Vite 8, React Router e React Icons |
| API             | Python 3.12, FastAPI, Pydantic e Uvicorn     |
| Persistência    | PostgreSQL e Prisma Client Python            |
| Filas e tarefas | Redis e ARQ                                  |
| WhatsApp        | Evolution Go (whatsmeow)                     |
| Infraestrutura  | Docker e Docker Compose                      |
| Testes          | Pytest e Pytest Asyncio                      |

## Arquitetura

```text
Frontend React
      │ HTTP / Bearer Token
      ▼
API FastAPI ─────────────── PostgreSQL
      │                         dados e históricos
      ├──────── Redis/ARQ
      │          filas, scheduler e workers
      ▼
Nos Evolution (um ou mais)
      │
      ▼
Sessões do WhatsApp
```

O scheduler verifica periodicamente os aquecimentos ativos. Dentro da janela de funcionamento configurada, ele seleciona remetente e destinatario, escolhe uma frase, processa o spintax e agenda o envio com um atraso aleatorio. O worker envia a mensagem pelo no Evolution associado ao numero e registra o resultado no banco.

O repositorio tambem contem uma configuracao de producao em dois servidores: o primeiro executa API, PostgreSQL, Redis, worker e um no Evolution; o segundo hospeda outro no Evolution para distribuir as instancias.

## Estrutura do projeto

```text
ProjetoEsquenta/
├── backend/
│   ├── prisma/             # Schema do banco de dados
│   ├── src/
│   │   ├── config/         # Configuracoes da aplicacao, Redis e Evolution
│   │   ├── controllers/    # Regras de entrada e saída da API
│   │   ├── jobs/           # Tarefas executadas pelo ARQ
│   │   ├── models/         # Schemas de validação
│   │   ├── repositories/   # Acesso aos dados
│   │   ├── routes/         # Rotas HTTP
│   │   ├── services/       # Regras de negócio e integrações
│   │   ├── utils/          # Logs, aleatoriedade e spintax
│   │   ├── main.py         # Aplicação FastAPI
│   │   └── worker.py       # Configuração do worker ARQ
│   ├── tests/              # Testes automatizados
│   ├── docker-compose.yml
│   └── requirements.txt
└── frontend/
    ├── assets/             # Imagens e identidade visual
    └── src/
        ├── api/            # Cliente e serviços HTTP
        ├── components/     # Componentes reutilizáveis
        └── pages/          # Login, Esquenta, Logs e Administração
```

## Como rodar localmente

### Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) com Docker Compose;
- [Node.js](https://nodejs.org/) 20 ou superior;
- Git.

### 1. Clone o repositório

```bash
git clone https://github.com/Lucca-07/ProjetoEsquenta.git
cd ProjetoEsquenta
```

### 2. Configure o backend

Crie o arquivo `backend/.env` com o conteúdo abaixo:

```env
APP_ENV=development
APP_NAME=esquenta-backend
LOG_LEVEL=INFO
API_PREFIX=/api

AUTH_SECRET=
AUTH_TOKEN_HOURS=
ADMIN_NAME=Administrator
ADMIN_EMAIL=admin@esquenta.local
ADMIN_PASSWORD=Admin@123

POSTGRES_PASSWORD=
DATABASE_URL=
REDIS_URL=

EVOLUTION_GO_NODE1_API_KEY=
EVOLUTION_GO_DB_PASSWORD=
EVOLUTION_GO_NODES=

SCHEDULER_INTERVAL_SECONDS=
```

### 3. Suba o backend e os serviços

```bash
cd backend
docker compose up -d --build
```

Esse comando inicia:

- API em `http://localhost:8000`;
- documentação Swagger em `http://localhost:8000/docs`;
- PostgreSQL na porta local `5433`;
- Redis na porta `6379`;
- Evolution Go em `http://localhost:8080`;
- worker responsável pelas tarefas agendadas.

Confira se a API está saudável:

```bash
curl http://localhost:8000/health
```

Na primeira execucao, abra `http://localhost:8080/manager/login` e ative a
licenca da Evolution Go usando `EVOLUTION_GO_NODE1_API_KEY`. Antes da ativacao,
os endpoints de WhatsApp retornam HTTP 503.

Para acompanhar ou encerrar os serviços:

```bash
docker compose logs -f api worker
docker compose down
```

Use `docker compose down -v` somente se tambem quiser apagar os dados locais do PostgreSQL, Redis e as instancias Evolution.

### 4. Inicie o frontend

Em outro terminal, a partir da raiz do repositório:

```bash
cd frontend
npm install
npm run dev
```

Acesse `http://localhost:5173`. Por padrão, o frontend consome `http://localhost:8000/api`. Para usar outro endereço, crie `frontend/.env.local`:

```env
VITE_API_URL=http://localhost:8000/api
```

No primeiro start, o backend cria o administrador informado no `.env`. Com o exemplo acima, o acesso inicial é:

```text
E-mail: admin@esquenta.local
Senha:  Admin@123
```

Altere esses dados no `.env` antes do primeiro start em qualquer ambiente compartilhado.

## Execução manual do backend

Se preferir executar a API fora do Docker, tenha PostgreSQL, Redis e uma Evolution Go acessiveis e ajuste as URLs do `.env` para `localhost`. No PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
prisma generate
prisma db push
uvicorn src.main:app --reload --port 8000
```

Em outro terminal, com o mesmo ambiente virtual ativado:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
arq src.worker.WorkerSettings
```

Para essa modalidade, use URLs como estas no `backend/.env`:

```env
DATABASE_URL=postgresql://esquenta:esquenta_local@localhost:5433/esquenta
REDIS_URL=redis://localhost:6379/0
EVOLUTION_GO_NODES=[{"name":"kvm8-1","base_url":"http://localhost:8080","api_key":"troque-esta-chave"}]
```

## Uso básico

1. Entre com uma conta válida.
2. Abra **Esquenta** e informe o telefone com DDI e DDD.
3. Conecte o número por QR Code ou código de pareamento.
4. Aguarde a sessão ficar conectada.
5. Selecione ao menos dois números.
6. Defina nome, intervalo e duração do grupo e inicie o aquecimento.
7. Acompanhe o progresso no painel e os detalhes na área de logs.

## Configuração da rampa

| Variável                     | Padrão | Descrição                               |
| ---------------------------- | -----: | --------------------------------------- |
| `WARMUP_START_MESSAGES`      |    `5` | Meta de mensagens no primeiro dia       |
| `WARMUP_INCREMENT`           |    `4` | Quantidade adicionada à meta a cada dia |
| `WARMUP_MAX_MESSAGES`        |  `120` | Limite diário por número                |
| `WARMUP_MAX_DAYS`            |   `30` | Dias até considerar o número aquecido   |
| `SCHEDULER_INTERVAL_SECONDS` |   `60` | Frequência de verificação do scheduler  |

## Testes e qualidade

Os testes do backend cobrem autenticação, sessões, mensagens, schemas e regras do aquecimento sem exigir os serviços externos em execução:

```bash
cd backend
pytest
```

No frontend:

```bash
cd frontend
npm run lint
npm run build
```

## API

Com o backend em execução, a especificação interativa completa fica disponível em `/docs`. Os principais grupos de endpoints são:

| Prefixo         | Responsabilidade                                        |
| --------------- | ------------------------------------------------------- |
| `/api/auth`     | Login, usuário atual e gestão de usuários               |
| `/api/sessions` | Criação, pareamento, consulta e encerramento de sessões |
| `/api/numbers`  | Listagem e resumo dos números                           |
| `/api/warmup`   | Início, pausa, encerramento e logs do aquecimento       |
| `/api/messages` | Envio e histórico de mensagens                          |
| `/api/phrases`  | Cadastro e manutenção das frases spintax                |
| `/api/logs`     | Dashboard administrativo e histórico                    |
| `/health`       | Estado básico da API                                    |

As rotas protegidas esperam o token retornado pelo login:

```http
Authorization: Bearer <token>
```

## Deploy em uma KVM-8

O Compose principal executa API, worker, Redis, banco da aplicacao, Evolution Go e o banco da Evolution na mesma KVM-8:

```bash
cd backend
docker compose up -d --build
```

Todos os numeros usam o no `kvm8-1`, configurado em `EVOLUTION_GO_NODES`. Proteja as portas e nunca publique PostgreSQL, Redis ou Evolution Go sem autenticacao e regras de firewall.

## Colaboradores

- [Lucca Rodrigues](https://github.com/Lucca-07) — Desenvolvimento do projeto;
- [David Ferreira](https://github.com/FerreiraHub) — Desenvolvimento do projeto.
- [Luiz Gustavo](https://github.com/SrLgart) - Prototipação do projeto

## Licença

Este repositório não possui um arquivo de licença. Até que uma licença seja adicionada, todos os direitos permanecem reservados aos autores.
