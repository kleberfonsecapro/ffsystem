# ffsystem — Análise e Resolução de Problemas

**O que é:** Sistema de **finanças pessoais** em Django 5.0.1, com templates renderizados no servidor e integração com IA via **Groq (Llama 3.1)**.

---

## Pilha Tecnológica

| Tecnologia | Uso |
|---|---|
| Django 5.0.1 | Framework web |
| PostgreSQL 16 | Banco de dados (containerizado) |
| Groq API + Llama 3.1 | Chat IA financeiro |
| Gunicorn | Servidor WSGI |
| Whitenoise | Static files |
| Docker / Compose | Containerização |

---

## Estrutura (4 apps)

| App | Função |
|---|---|
| **users** | Autenticação — cadastro, login, logout |
| **dashboard** | Home com saldo, receitas/despesas, insight IA |
| **finance** | CRUD de transações financeiras |
| **intelligence** | Chat IA que cria transações via Groq |

## Modelo Principal

- **`Transaction`** (`finance/models.py`): `user` (FK), `description`, `amount`, `date`, `category`, `type` (receita/despesa)

## Rotas

```
/                    → dashboard.home
/users/login/        → login
/users/logout/       → logout (POST)
/users/register/     → registro
/finance/            → listar transações (paginado)
/finance/add/        → adicionar transação (com validação)
/intelligence/chat/  → chat IA
/intelligence/api/chat/ → API do chat (POST JSON/Form)

```

---

## Problemas Encontrados e Resoluções

### 🔴 CRÍTICOS

| # | Problema | Arquivo | Resolução |
|---|----------|---------|-----------|
| 1 | **XSS Refletido** — `innerHTML` com input do usuário sem sanitização | `templates/chat.html:34-38`, `finance_list.html:83-86` | Substituído por `document.createTextNode()` + `appendChild()` — sem interpretação de HTML |
| 2 | **Zero validação** em `finance_add` — dados criados direto do `request.POST` | `finance/views.py:13-19` | Criado `finance/forms.py` com `ModelForm` + validação de `amount > 0` |
| 3 | **Prompt Injection** — LLM criava transações sem validar saída | `intelligence/views.py:46-53` | Validação rigorosa: `amount > 0`, `type` em {receita,despesa}, `category` até 100 chars, `description` truncada |
| 4 | **`SECRET_KEY` fallback hardcoded público** | `core/settings.py:8` | Agora `raise ValueError` se `SECRET_KEY` não definida; sem fallback |
| 5 | **`DEBUG=True` como padrão** | `core/settings.py:10` | Padrão alterado para `"False"` |

### 🟠 SEGURANÇA

| # | Problema | Arquivo | Resolução |
|---|----------|---------|-----------|
| 6 | **Logout via GET** — vulnerável a CSRF | `users/views.py:39-41`, `base.html:31` | View decorada com `@require_POST`; link substituído por formulário POST com `{% csrf_token %}` |
| 7 | **`DB_PASSWORD` com fallback hardcoded** | `core/settings.py:77` | Removido fallback; usa `os.environ.get("DB_PASSWORD")` sem default |
| 8 | **Sem HTTPS/Security headers** | `core/settings.py` | Adicionados: `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_*`, `SECURE_CONTENT_TYPE_NOSNIFF`, `SECURE_BROWSER_XSS_FILTER`, `CSRF_TRUSTED_ORIGINS` |
| 9 | **CORS sem restrição de origens** | `core/settings.py` | Adicionado `CORS_ALLOWED_ORIGINS` lido de variável de ambiente |
| 10 | **Vazamento de info em erros (chat_api)** | `intelligence/views.py:61` | Erros genéricos: `"Ocorreu um erro interno"` + logging com `logger.exception()` |
| 11 | **Sem proteção contra brute force** | `users/views.py` | Pendente: requer `django-axes` ou `django-ratelimit` |
| 12 | **Variável GROQ_API_KEY vazia causava erro obscuro** | `intelligence/views.py:32` | Validação explícita: retorna mensagem amigável se chave não configurada |
| 13 | **CDN sem SRI** | `base.html:8-9` | Adicionados atributos `integrity` e `crossorigin` |

### 🟡 INFRAESTRUTURA

| # | Problema | Arquivo | Resolução |
|---|----------|---------|-----------|
| 14 | **Sem healthcheck no web** | `docker-compose.yml` | Adicionado healthcheck com `curl http://localhost:8000` |
| 15 | **Sem restart policy** | `docker-compose.yml` | Adicionado `restart: unless-stopped` em ambos serviços |
| 16 | **collectstatic no entrypoint (ineficiente)** | `entrypoint.sh:7` | Movido para o `Dockerfile` (executado no build) |
| 17 | **Race condition em migrations** | `entrypoint.sh:5` | Documentado; aceito para ambiente single-replica |
| 18 | **Workers fixos (3) do Gunicorn** | `entrypoint.sh` | Calculado automaticamente: `(nproc * 2 + 1)` com fallback por env var |
| 19 | **Sem graceful shutdown** | `entrypoint.sh` | Adicionado `trap SIGTERM/SIGINT` com `kill -TERM` no gunicorn |
| 20 | **Porta hardcoded** | `entrypoint.sh` | Lida de `GUNICORN_PORT` env var (padrão 8000) |

### 🟢 QUALIDADE DE CÓDIGO

| # | Problema | Arquivo | Resolução |
|---|----------|---------|-----------|
| 21 | **Ineficiência: soma em memória no insight_api** | `dashboard/views.py:30-31` | Agora usa `aggregate(Sum("amount"))` no banco |
| 22 | **REST Framework instalado e não usado** | `requirements.txt` | Removido das dependências |
| 23 | **Versões imprecisas (`>=`) sem lock** | `requirements.txt` | Versões fixadas com `==` |
| 24 | **`Transaction` não registrado no admin** | `finance/admin.py` | Registrado com `TransactionAdmin` |
| 25 | **Sem paginação na listagem** | `finance/views.py` | Adicionado `Paginator` (20 itens/página) |
| 26 | **Sem `forms.py`** | `finance/` | Criado `TransactionForm` com `ModelForm` + validação |
| 27 | **Sem tratamento de erro em `finance_add`** | `finance/views.py` | Adicionado `try/except` com `messages.error()` |
| 28 | **Sem feedback visual (messages)** | `templates/` | Adicionado display de `messages` no dashboard, finance_add e login |
| 29 | **`LANGUAGE_CODE = "pt-br"` não padrão** | `core/settings.py` | Corrigido para `"pt-BR"` |
| 30 | **Sem logging configurado** | `core/settings.py` | Adicionado `LOGGING` com console handler |
| 31 | **Session sem expiração** | `core/settings.py` | Adicionado `SESSION_EXPIRE_AT_BROWSER_CLOSE=True` e `SESSION_COOKIE_AGE=28800` |
| 32 | **`ALLOWED_HOSTS` sem strip de espaços** | `core/settings.py` | Adicionado `[h.strip() for h in ...]` |
| 33 | **`.dockerignore` com padrão sem `**/`** | `.dockerignore` | Corrigido para `**/__pycache__/` |
| 34 | **`.gitignore` incompleto** | `.gitignore` | Adicionados: `__pycache__/`, `*.pyc`, `.DS_Store`, `staticfiles/`, `.venv/` |
| 35 | **CDN externo para Chart.js** | `base.html:9` | Mantido com SRI; recomendado bundle local em produção |
| 36 | **Senha fraca (`admin123`)** | `.env` | Alterada para `Str0ng!Admin#2024` |
| 37 | **Credenciais versionadas no resumo** | `resumo_inicial.md` | Removidas credenciais explícitas do documento |

---

## Containerização

### Arquivos criados

| Arquivo | Descrição |
|---|---|
| `Dockerfile` | Python 3.12-slim com collectstatic no build |
| `docker-compose.yml` | `web` (Gunicorn) + `db` (PostgreSQL 16) com healthcheck e restart |
| `requirements.txt` | Dependências com versões fixadas |
| `entrypoint.sh` | Migrations, superuser automático, graceful shutdown, workers dinâmicos |
| `.dockerignore` | Padrões glob atualizados |
| `.env` | Variáveis reais (ignorado pelo git) |
| `.env.example` | Template com seções obrigatórias e opcionais |
| `finance/forms.py` | `ModelForm` com validação de `amount` |

### Arquivos modificados

| Arquivo | Mudanças |
|---|---|
| `core/settings.py` | `SECRET_KEY` obrigatória, `DEBUG=False` padrão, `ALLOWED_HOSTS` sanitizado, `DB_PASSWORD` sem fallback, HTTPS/CORS/LOGGING/SESSION configurados |
| `intelligence/views.py` | Validação de chave e saída do LLM, timeout 30s, suporte JSON, logging, erros genéricos |
| `finance/views.py` | Form validation, paginação (20 itens), mensagens de feedback |
| `dashboard/views.py` | Aggregate no banco em vez de soma em memória |
| `users/views.py` | Logout via `@require_POST` |
| `templates/base.html` | `{% static %}`, SRI nas CDNs, logout via formulário POST |
| `templates/chat.html` | XSS corrigido: `textContent` no lugar de `innerHTML` |
| `templates/finance_list.html` | XSS corrigido, paginação exibida |
| `templates/finance_add.html` | Exibição de erros do form, `{{ form.as_p }}` |
| `templates/dashboard.html` | Exibição de `messages` |
| `finance/admin.py` | `Transaction` registrado no admin |
| `Dockerfile` | `collectstatic` durante o build |
| `entrypoint.sh` | Graceful shutdown, workers dinâmicos, porta configurável |
| `docker-compose.yml` | `restart: unless-stopped`, healthcheck no web, `SECRET_KEY:?error` |
| `.env` | Senha do superusuário fortalecida |
| `.env.example` | Seções obrigatórias/opcionais documentadas |
| `.gitignore` | `__pycache__/`, `*.pyc`, `.DS_Store`, `staticfiles/`, `.venv/` |
| `.dockerignore` | `**/__pycache__/` com glob correto |

---

## Variáveis de Ambiente

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `SECRET_KEY` | **Sim** | — | Chave secreta Django |
| `DEBUG` | Não | `False` | Modo debug |
| `DJANGO_ALLOWED_HOSTS` | Não | `localhost,127.0.0.1` | Hosts permitidos |
| `DB_NAME` | Não | `ffsystem` | Nome do banco |
| `DB_USER` | Não | `ffsystem` | Usuário do banco |
| `DB_PASSWORD` | **Sim** | — | Senha do banco |
| `DB_HOST` | Não | `db` | Host do PostgreSQL |
| `DB_PORT` | Não | `5432` | Porta do PostgreSQL |
| `GROQ_API_KEY` | Não | vazio | Chave da API Groq |
| `DJANGO_SUPERUSER_USERNAME` | Não | `admin` | Superusuário Django |
| `DJANGO_SUPERUSER_EMAIL` | Não | `admin@example.com` | Email do superusuário |
| `DJANGO_SUPERUSER_PASSWORD` | **Sim** | — | Senha do superusuário |
| `SECURE_SSL_REDIRECT` | Não | `False` | Redirecionar para HTTPS |
| `CORS_ALLOWED_ORIGINS` | Não | vazio | Origens permitidas CORS |
| `CSRF_TRUSTED_ORIGINS` | Não | vazio | Origens confiáveis CSRF |
| `GUNICORN_PORT` | Não | `8000` | Porta do servidor |

---

## Como subir

```bash
# 1. Gere uma SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 2. Edite o .env com as credenciais
cp .env.example .env
# Preencha: SECRET_KEY, DB_PASSWORD, DJANGO_SUPERUSER_PASSWORD, GROQ_API_KEY

# 3. Suba os containers
docker compose up -d

# 4. Acesse
open http://localhost:8000
```

## Credenciais padrão (desenvolvimento)

- **Usuário:** `admin`
- **Senha:** definida em `DJANGO_SUPERUSER_PASSWORD` no `.env`

---

## Pendências (para próxima iteração)

- [ ] Rate limiting no login (`django-axes`) — brute force
- [ ] Rate limiting na API Groq — custo financeiro
- [ ] Password reset (esqueci minha senha)
- [ ] Testes unitários e de integração
- [ ] Bundle local do Chart.js (remover dependência de CDN)
- [ ] Migrar `psycopg2-binary` para `psycopg2` em produção
