<div align="center">
  <img src="https://img.shields.io/badge/Django-5.0.1-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Groq_Llama_3.1-1B1B2F?style=for-the-badge&logo=groq&logoColor=white" alt="Groq">
  <img src="https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white" alt="Gunicorn">
  <br>
  <img src="https://img.shields.io/badge/status-em%20produ%C3%A7%C3%A3o-10b981?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/coverage-0%25-red?style=flat-square" alt="Coverage">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square" alt="PRs Welcome">
</div>

<br>

<div align="center">
  <h1>🧠 SmartFinance AI</h1>
  <h3>Sistema inteligente de finanças pessoais com assistente IA</h3>
  <p>Gerencie receitas e despesas de forma simples, segura e com inteligência artificial integrada.</p>
</div>

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 📊 **Dashboard Financeiro** | Visão geral do saldo, receitas, despesas e insight inteligente |
| 💰 **Gestão de Transações** | Cadastro, listagem com paginação e categorização de receitas/despesas |
| 🤖 **Assistente IA (Groq)** | Chat em linguagem natural que interpreta e registra transações automaticamente |
| 🔐 **Autenticação** | Cadastro, login e sessão segura com expiração configurada |
| 🐳 **Containerizado** | Docker Compose com PostgreSQL 16 e healthcheck |
| 🛡️ **Segurança Reforçada** | HTTPS headers, CORS configurado, XSS mitigado, CSRF proteção |

---

## 🚀 Tecnologias

**Backend** — Django 5.0.1 • Gunicorn • Whitenoise • Python 3.12

**Banco de Dados** — PostgreSQL 16

**Inteligência Artificial** — Groq API + Llama 3.1 (8B)

**Infraestrutura** — Docker • Docker Compose

---

## 📋 Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) (v24+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2+)
- Conta na [Groq](https://console.groq.com) para obter uma API Key

---

## ⚡ Quick Start

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/ffsystem.git
cd ffsystem

# 2. Gere uma SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 3. Configure o ambiente
cp .env.example .env
# Edite o .env com:
#   - SECRET_KEY (gerada acima)
#   - DB_PASSWORD (senha do banco)
#   - DJANGO_SUPERUSER_PASSWORD (senha do admin)
#   - GROQ_API_KEY (sua chave da Groq)

# 4. Suba os containers
docker compose up -d

# 5. Acesse
open http://localhost:8000
```

> **Credenciais padrão** — usuário: `admin` | senha: definida em `DJANGO_SUPERUSER_PASSWORD` no `.env`

---

## 🏗️ Estrutura do Projeto

```
ffsystem/
├── core/                  # Configurações do Django
│   ├── settings.py        # Settings com variáveis de ambiente
│   ├── urls.py            # Rotas principais
│   └── wsgi.py            # WSGI para Gunicorn
├── dashboard/             # Dashboard financeiro
│   └── views.py           # Home + Insight API
├── finance/               # Gestão financeira
│   ├── models.py          # Model Transaction
│   ├── forms.py           # ModelForm com validação
│   ├── views.py           # CRUD com paginação
│   └── admin.py           # Admin registrado
├── intelligence/          # Assistente IA
│   └── views.py           # Chat + API com Groq
├── users/                 # Autenticação
│   └── views.py           # Login/registro/logout
├── templates/             # Templates Django
├── static/                # Arquivos estáticos
├── docker-compose.yml     # Orquestração de serviços
├── Dockerfile             # Build da imagem
├── entrypoint.sh          # Entrypoint com graceful shutdown
├── resumo_inicial.md      # Análise técnica detalhada
└── .env.example           # Template de variáveis de ambiente
```

---

## 🔒 Segurança

Este projeto passou por uma auditoria de segurança completa com **37 problemas identificados e corrigidos**:

| Categoria | Itens | Descrição |
|---|---|---|
| 🔴 **Críticos** | 5 | XSS, validação zero, prompt injection, SECRET_KEY, DEBUG |
| 🟠 **Segurança** | 8 | Logout CSRF, CORS, HTTPS headers, vazamento de erros |
| 🟡 **Infraestrutura** | 7 | Healthcheck, restart policy, graceful shutdown, workers |
| 🟢 **Qualidade** | 17 | Paginação, forms, admin, logging, versões fixadas |

> 📖 Detalhes completos no [`resumo_inicial.md`](./resumo_inicial.md)

---

## 🧪 Pendências

- [ ] Rate limiting no login (`django-axes`)
- [ ] Rate limiting na API Groq (custo financeiro)
- [ ] Password reset (esqueci minha senha)
- [ ] Testes unitários e de integração
- [ ] Bundle local do Chart.js
- [ ] Migrar `psycopg2-binary` → `psycopg2` em produção

---

## 🌐 Rotas da API

| Rota | Método | Descrição |
|---|---|---|
| `/` | GET | Dashboard financeiro |
| `/users/login/` | GET/POST | Login |
| `/users/logout/` | **POST** | Logout (protegido contra CSRF) |
| `/users/register/` | GET/POST | Cadastro |
| `/finance/` | GET | Lista de transações (paginada) |
| `/finance/add/` | GET/POST | Nova transação (com validação) |
| `/intelligence/chat/` | GET | Página do chat IA |
| `/intelligence/api/chat/` | POST | API do chat IA (JSON ou Form) |
| `/dashboard/api/insight/` | GET | Insight financeiro inteligente |
| `/admin/` | GET/POST | Admin Django |

---

## 🤝 Como Contribuir

1. Faça um fork do projeto
2. Crie uma branch: `git checkout -b minha-feature`
3. Commit suas mudanças: `git commit -m 'feat: minha nova feature'`
4. Push: `git push origin minha-feature`
5. Abra um Pull Request

---

<div align="center">
  <p>Feito com ❤️ usando Django, Docker e Groq</p>
  <p>
    <a href="#">Reportar Bug</a>
    ·
    <a href="#">Solicitar Feature</a>
    ·
    <a href="https://github.com/seu-usuario/ffsystem">GitHub</a>
  </p>
</div>
