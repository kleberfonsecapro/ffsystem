# Melhorias Implementadas

## Dezembro 2024

### 1. Deleção de Transações

**Data:** Dezembro 2024

**Descrição:** Adicionada funcionalidade para excluir transações (receitas e despesas) diretamente da lista de gestão financeira.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `finance/views.py` | Nova view `finance_delete` com `@require_POST` e proteção por usuário |
| `finance/urls.py` | Nova rota `<int:pk>/delete/` |
| `templates/finance_list.html` | Coluna "Ações" com botão de excluir por transação + confirmação |
| `static/css/style.css` | Classe `.btn-delete` com estilo vermelho e hover |

**Detalhes técnicos:**
- Requisição POST com CSRF token (não aceita GET, evitando deleção acidental por bots)
- Verifica que a transação pertence ao usuário logado (`get_object_or_404` com filtro `user=request.user`)
- Confirmação via `confirm()` no frontend antes de enviar
- Mensagem de sucesso com `messages.success`
- Redireciona para a lista de transações após excluir

**Impacto nos gráficos:** Automático — o dashboard e insight já consultam o banco a cada requisição, refletindo a deleção imediatamente.

---

### 2. Rate Limiting no Login

**Data:** Junho 2026

**Descrição:** Implementado rate limiting no login com `django-axes` para prevenir ataques de força bruta.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `requirements.txt` | Adicionado `django-axes==6.4.0` |
| `core/settings.py` | Adicionado `'axes'` em INSTALLED_APPS, `AxesMiddleware`, `AUTHENTICATION_BACKENDS` e configs `AXES_*` |

**Detalhes técnicos:**
- Bloqueio após **5 tentativas** erradas por combinação de IP + usuário
- **15 minutos** de bloqueio (`AXES_COOLOFF_TIME`)
- Contagem resetada ao login bem-sucedido (`AXES_RESET_ON_SUCCESS = True`)
- Painel no admin para visualizar tentativas e desbloquear
- Comando `manage.py axes_reset` para desbloqueio manual

---

## Pendências (não implementadas)

### 3. Editar Transações
**Descrição:** Adicionar edição de transações na listagem para completar o CRUD.
**Arquivos envolvidos:** `finance/views.py`, `finance/urls.py`, `templates/finance_list.html`
**Observação:** A view de add já existe, basta criar uma similar para edição com `UpdateView` ou view function.

### 3. Categorias Personalizadas
**Descrição:** Permitir que o usuário crie suas próprias categorias em vez de usar as 8 fixas no model.
**Arquivos envolvidos:** `finance/models.py` (novo model `Category`), `finance/forms.py`, migrações
**Observação:** Model `Transaction.category` mudaria de `CharField` para `ForeignKey` para `Category`.

### 4. Filtros na Listagem
**Descrição:** Adicionar filtros por tipo (receita/despesa), data e categoria na página de listagem.
**Arquivos envolvidos:** `finance/views.py`, `templates/finance_list.html`
**Observação:** Usar `django-filter` ou filtro manual via `request.GET`.

### 5. Exportar Transações (CSV)
**Descrição:** Botão para exportar as transações do usuário em formato CSV.
**Arquivos envolvidos:** `finance/views.py`, `finance/urls.py`, `templates/finance_list.html`
**Observação:** Usar `csv` module do Python ou `HttpResponse` com `content_type=text/csv`.

### 6. Insight IA Real no Dashboard
**Descrição:** Substituir a regra simples de comparação receita/despesa por uma chamada real à Groq para gerar análise financeira contextual.
**Arquivos envolvidos:** `dashboard/views.py`, `dashboard/urls.py`
**Observação:** Reaproveitar o cliente Groq já configurado em `intelligence/views.py`.

### 7. Rate Limiting no Login
**Descrição:** Prevenir brute force com `django-axes` ou `django-ratelimit`.
**Arquivos envolvidos:** `core/settings.py`, `requirements.txt`
**Observação:** README já lista como pendência.

### 8. Rate Limiting na API Groq
**Descrição:** Limitar chamadas à API Groq por usuário para controlar custos.
**Arquivos envolvidos:** `intelligence/views.py`
**Observação:** README já lista como pendência.

### 9. Password Reset (Esqueci Minha Senha)
**Descrição:** Fluxo completo de recuperação de senha por email.
**Arquivos envolvidos:** `core/urls.py`, `templates/`, `core/settings.py`
**Observação:** Django já fornece `django.contrib.auth.views.PasswordResetView`.

### 10. Testes Unitários e de Integração
**Descrição:** Cobrir models, views e a integração com Groq com testes.
**Arquivos envolvidos:** `finance/tests.py`, `intelligence/tests.py`, `dashboard/tests.py`, `users/tests.py`
**Observação:** README lista cobertura atual em 0%.

### 11. Bundle Local do Chart.js
**Descrição:** Substituir CDN do Chart.js por bundle local (elimina dependência externa).
**Arquivos envolvidos:** `templates/base.html`, `static/js/`
**Observação:** README já lista como pendência.

### 12. Migrar psycopg2-binary para psycopg2
**Descrição:** Substituir `psycopg2-binary` por `psycopg2` em produção (boas práticas).
**Arquivos envolvidos:** `requirements.txt`, `Dockerfile`
**Observação:** README já lista como pendência.

---

*Documentado em Junho 2026*
