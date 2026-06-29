# DevOps — SmartFinance AI

## Domínio

```
https://ffsystem.giize.com
```

---

## Stack de Infraestrutura

| Componente | Tecnologia | Versão |
|---|---|---|
| Servidor web | Gunicorn | 26.0.0 |
| Framework | Django | 5.0.1 |
| Database | PostgreSQL | 16 (Alpine) |
| Proxy/Static | Whitenoise | 6.12.0 |
| Container | Docker + Compose | — |
| OS Base | python:3.12-slim | Debian |

---

## Docker

### Dockerfile (`Dockerfile`)

```
python:3.12-slim → instala dependências do sistema → pip install → collectstatic → entrypoint
```

**Detalhes:**
- Base `python:3.12-slim` — imagem oficial enxuta
- Pacotes do sistema instalados:
  - `libpq-dev`, `gcc`, `postgresql-client` — driver psycopg2
  - `python3-dev` — headers para compilação
  - `libpango-1.0-0`, `libpangocairo-1.0-0`, `libgdk-pixbuf-2.0-0`, `libffi-dev`, `libcairo2` — WeasyPrint (geração de PDF)
- `collectstatic` executado **no build** (não no entrypoint), usando `SECRET_KEY=dummy-build-only`
- `ENTRYPOINT` aponta para `entrypoint.sh`

### Docker Compose (`docker-compose.yml`)

**2 serviços:**

#### `db` (PostgreSQL 16 Alpine)
- Volume persistente: `postgres_data:/var/lib/postgresql/data`
- Variáveis: `POSTGRES_DB`, `POSTGRES_USER` lidas do `.env`, `POSTGRES_PASSWORD` obrigatória
- Healthcheck: `pg_isready` a cada 5s, 3s timeout, 5 retries
- Restart: `unless-stopped`

#### `web` (Aplicação Django)
- Build do Dockerfile local
- Porta `8000:8000`
- Volume: `static_volume:/app/staticfiles`
- Variáveis obrigatórias: `SECRET_KEY`, `DB_PASSWORD`, `DJANGO_SUPERUSER_PASSWORD`
- `depends_on`: aguarda `db` estar saudável (`condition: service_healthy`)
- Healthcheck: `curl -sf http://localhost:8000` a cada 30s, 10s timeout, 3 retries, start period 40s
- Restart: `unless-stopped`

### Redes

| Rede | Driver | Tipo | Propósito |
|---|---|---|---|
| `internal` | bridge | interno | Comunicação entre `db` e `web` |
| `traefik_global` | bridge | `external: true` | Tráfego HTTP/HTTPS do Traefik |

---

## Proxy Reverso — Traefik Global

O Traefik é um proxy reverso global que atende múltiplas aplicações no servidor (`/home/kleber/traefik/`). Ele gerencia:

- **Terminação SSL** via Let's Encrypt
- **Roteamento** por domínio
- **Redirecionamento** HTTP → HTTPS

### Arquitetura

```
Internet → Portas 80/443 → Traefik → traefik_global → ffsystem_web:8000
```

### Configuração do Traefik

O Traefik utiliza **provedor de arquivo** (`dynamic.yml`) para definir as rotas — não usa labels Docker.

#### Rotas em `traefik/dynamic.yml`

```yaml
ffsystem-http:
  rule: "Host(`ffsystem.giize.com`)"
  entrypoints: web
  middlewares:
    - redirect-https
  service: ffsystem

ffsystem-https:
  rule: "Host(`ffsystem.giize.com`)"
  entrypoints: websecure
  service: ffsystem
  tls:
    certresolver: letsencrypt

ffsystem:
  loadBalancer:
    servers:
      - url: "http://ffsystem_web:8000"
```

#### Como a aplicação se conecta

O `docker-compose.yml` do ffsystem declara a rede `traefik_global` como externa e conecta o container `ffsystem_web` a ela. O container `db` fica apenas na rede `internal` (não exposto externamente).

```yaml
networks:
  web:
    ...
    networks:
      - internal
      - traefik_global

  db:
    ...
    networks:
      - internal

networks:
  internal:
    driver: bridge
  traefik_global:
    external: true
    name: traefik_global
```

### Restart do Traefik

O Traefik monitora o `dynamic.yml` em tempo real. Para forçar recarga:

```bash
docker restart traefik_global
```

---

## Entrypoint (`entrypoint.sh`)

Sequência de inicialização:

1. **Graceful shutdown**: `trap SIGTERM/SIGINT` → `kill -TERM` no gunicorn → `wait` → `exit 0`
2. **Migrate**: `python manage.py migrate --noinput` (race condition aceita em single-replica)
3. **Superuser**: cria automaticamente se `DJANGO_SUPERUSER_USERNAME` e `DJANGO_SUPERUSER_PASSWORD` definidos (falha silenciosa se já existe)
4. **Gunicorn**: workers calculados dinamicamente:
   - `WORKERS = (nproc * 2 + 1)` com fallback via `GUNICORN_WORKERS`
   - Bind em `0.0.0.0:{GUNICORN_PORT:-8000}`
   - Timeout 120s
   - Roda em background (`&`) + `wait`

---

## Variáveis de Ambiente

### Obrigatórias

| Variável | Descrição |
|---|---|
| `SECRET_KEY` | Chave secreta Django (sem fallback — levanta `ValueError`) |
| `DB_PASSWORD` | Senha do PostgreSQL |
| `DJANGO_SUPERUSER_PASSWORD` | Senha do admin inicial |
| `GROQ_API_KEY` | Chave da API Groq |

### Opcionais

| Variável | Padrão | Descrição |
|---|---|---|
| `DEBUG` | `False` | Modo debug Django |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,ffsystem.giize.com` | Hosts permitidos (strip automático) |
| `CSRF_TRUSTED_ORIGINS` | `https://ffsystem.giize.com` | Origens confiáveis CSRF |
| `CORS_ALLOWED_ORIGINS` | `https://ffsystem.giize.com` | Origens permitidas CORS |
| `DB_NAME` | `ffsystem` | Nome do banco |
| `DB_USER` | `ffsystem` | Usuário do banco |
| `DB_HOST` | `localhost` (dev) / `db` (docker) | Host do PostgreSQL |
| `DB_PORT` | `5432` | Porta do PostgreSQL |
| `DJANGO_SUPERUSER_USERNAME` | `admin` | Superusuário |
| `DJANGO_SUPERUSER_EMAIL` | `admin@example.com` | Email do superusuário |
| `SECURE_SSL_REDIRECT` | `False` | Forçar HTTPS |
| `CORS_ALLOWED_ORIGINS` | vazio | Origens CORS |
| `CSRF_TRUSTED_ORIGINS` | vazio | Origens CSRF |
| `GUNICORN_PORT` | `8000` | Porta do servidor |
| `GUNICORN_WORKERS` | `nproc * 2 + 1` | Workers do gunicorn |
| `EMAIL_BACKEND` | `console` | Backend de email (console ou smtp) |
| `EMAIL_HOST` | vazio | SMTP host |
| `EMAIL_PORT` | `587` | SMTP porta |
| `EMAIL_USE_TLS` | `True` | TLS no SMTP |
| `EMAIL_HOST_USER` | vazio | SMTP usuário |
| `EMAIL_HOST_PASSWORD` | vazio | SMTP senha |
| `DEFAULT_FROM_EMAIL` | `SmartFinance AI <noreply@smartfinance.ai>` | Remetente padrão |

---

## Segurança da Infraestrutura

### HTTPS (configurável por env vars)
- `SECURE_SSL_REDIRECT`
- `SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE`
- `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`, `SECURE_HSTS_PRELOAD`
- `SECURE_CONTENT_TYPE_NOSNIFF = True`
- `SECURE_BROWSER_XSS_FILTER = True`

### CORS
- `CORS_ALLOWED_ORIGINS` lido de env var (vazio = sem restrição)

### Rate Limiting
- `django-axes`: 5 tentativas falhas → bloqueio de 5 minutos por **usuário** (não por IP)
- Reset automático ao login bem-sucedido
- Admin `/admin/axes/` para desbloqueio manual

### Network
- Container `web` exposto apenas na rede `traefik_global` (porta 8000 TCP)
- Container `db` isolado na rede `internal` — sem acesso externo
- `depends_on` com `condition: service_healthy` evita race conditions

### Proxy Reverso
- **Traefik** gerencia SSL (Let's Encrypt) e HTTP → HTTPS
- `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")` — Django confia no header do Traefik
- `SECURE_SSL_REDIRECT = False` — Traefik faz o redirect, não o Django (evita loop)

---

## Monitoramento

### Healthchecks
- **db**: `pg_isready -U ffsystem -d ffsystem` (intervalo 5s, 3s timeout, 5 retries)
- **web**: `curl -sf http://localhost:8000` (intervalo 30s, 10s timeout, 3 retries, start period 40s)

### Logging
- Django: console handler, nível `INFO` (configurável via `DJANGO_LOG_LEVEL`)
- Gunicorn: logs no stdout/stderr (coletados pelo Docker)

---

## Storage

### Static Files
- Framework: Whitenoise (`CompressedManifestStaticFilesStorage`)
- Diretório source: `static/`
- Diretório coletado: `staticfiles/` (montado como volume `static_volume`)
- Coletados durante o **build** da imagem Docker

### Media Files (Uploads)
- Diretório: `media/`
- Subdiretório: `documents/%Y/%m/%d/`
- Servidos em dev via `django.conf.urls.static`
- **Em produção**: configurar proxy reverso (nginx/s3) para servir media — atualmente servido pelo Django apenas em `DEBUG=True`

---

## Processo de Deploy

### Desenvolvimento local (porta direta)

```bash
# 1. Configurar ambiente
cp .env.example .env
# Preencher SECRET_KEY, DB_PASSWORD, DJANGO_SUPERUSER_PASSWORD, GROQ_API_KEY

# 2. Subir containers
docker compose up -d

# 3. Acompanhar logs
docker compose logs -f
```

Acesso: `http://localhost:8000`

### Produção (via Traefik)

```bash
# 1. Configurar ambiente
cp .env.example .env
# Preencher SECRET_KEY, DB_PASSWORD, DJANGO_SUPERUSER_PASSWORD, GROQ_API_KEY

# 2. Subir containers com build
docker compose up -d --build

# 3. Verificar logs
docker compose logs -f web

# 4. Garantir que o Traefik está ativo
docker ps | grep traefik_global
```

Acesso: `https://ffsystem.giize.com`

### Atualização (deploy roll)

```bash
cd /home/kleber/ffsystem

# Pull das mudanças (se usando git)
git pull

# Rebuild e restart sem downtime
docker compose up -d --build --no-deps web

# Verificar health
docker ps | grep ffsystem_web
```

### SSL Certificate

O Traefik obtém certificados automaticamente via Let's Encrypt (DNS Challenge). Certificado armazenado em `/home/kleber/traefik/acme.json`.

Para verificar:
```bash
docker logs traefik_global | grep ffsystem
```

---

## Dependências do Sistema (Dockerfile)

Necessárias para compilação dos pacotes Python:

| Pacote | Motivo |
|---|---|
| `libpq-dev`, `gcc` | Compilar `psycopg2` |
| `postgresql-client` | `pg_isready` no entrypoint |
| `curl` | Healthcheck do container |
| `python3-dev` | Headers Python para compilação C |
| `libpango-1.0-0`, `libpangocairo-1.0-0` | WeasyPrint (PDF) |
| `libgdk-pixbuf-2.0-0` | WeasyPrint (imagens) |
| `libffi-dev` | WeasyPrint (cFFI) |
| `libcairo2` | WeasyPrint (renderização) |

---

## Troubleshooting Comum

### Container web reinicia em loop
Verificar se as variáveis obrigatórias estão definidas no `.env`:
```bash
docker compose config  # mostra o resolved config
docker compose logs web
```

### Erro de conexão com banco
```bash
docker compose exec db pg_isready -U ffsystem
docker compose exec db psql -U ffsystem -d ffsystem -c "\dt"
```

### Migrations pendentes
```bash
docker compose exec web python manage.py showmigrations
docker compose exec web python manage.py migrate --noinput
```

### Usuário bloqueado pelo Axes
```bash
# Via admin Django
docker compose exec web python manage.py axes_reset
# Ou acessar /admin/axes/ e desbloquear manualmente
```

### Coletar static files manualmente
```bash
docker compose exec web python manage.py collectstatic --noinput
```

### Aplicação não responde pelo domínio
Verificar se o container está na rede `traefik_global`:
```bash
docker inspect ffsystem_web --format '{{range $net, $v := .NetworkSettings.Networks}}{{$net}} {{end}}'
# Deve conter: ffsystem_internal traefik_global
```

Verificar se o Traefik reconheceu a rota:
```bash
docker logs traefik_global | grep ffsystem
```

### SSL não emite (certificado Let's Encrypt)
O DNS de `ffsystem.giize.com` precisa apontar para o IP do servidor. Verificar:
```bash
dig +short ffsystem.giize.com
# Deve retornar o IP público do servidor
```

### Dump/Restore do banco
```bash
# Dump
docker compose exec db pg_dump -U ffsystem ffsystem > backup.sql

# Restore
cat backup.sql | docker compose exec -T db psql -U ffsystem ffsystem
```

---

## Arquivos DevOps no Projeto

| Arquivo | Propósito |
|---|---|
| `Dockerfile` | Build da imagem da aplicação |
| `docker-compose.yml` | Orquestração web + db |
| `entrypoint.sh` | Script de inicialização com graceful shutdown |
| `.env.example` | Template de variáveis de ambiente |
| `.dockerignore` | Exclusões para o build Docker |
| `.gitignore` | Exclusões para versionamento |
| `requirements.txt` | Dependências Python com versões fixadas |
| `devops.md` | Documentação de infraestrutura e deploy |

### Arquivos de Configuração Externa

| Arquivo | Localização | Propósito |
|---|---|---|
| `dynamic.yml` | `/home/kleber/traefik/dynamic.yml` | Rotas do Traefik para ffsystem.giize.com |
| `docker-compose.yml` | `/home/kleber/traefik/docker-compose.yml` | Orquestração do Traefik global |
| `acme.json` | `/home/kleber/traefik/acme.json` | Certificados SSL Let's Encrypt |
