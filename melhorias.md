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

### 3. Editar Transações

**Data:** Junho 2026

**Descrição:** Adicionada funcionalidade para editar transações existentes, completando o CRUD.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `finance/views.py` | Nova view `finance_edit` com form pré-preenchido via `instance` |
| `finance/urls.py` | Nova rota `<int:pk>/edit/` |
| `templates/finance_add.html` | Action do form dinâmica, título e botão condicionais (add/edit) |
| `templates/finance_list.html` | Botão "Editar" (ícone lápis) ao lado do Excluir |
| `static/css/style.css` | Classe `.btn-edit` com estilo azul e hover |

**Detalhes técnicos:**
- Reaproveita o template `finance_add.html` com contexto `"editing": True`
- `TransactionForm(instance=transaction)` pré-preenche os campos automaticamente
- `form.save()` sem `commit=False` — atualiza o registro existente
- Verifica que a transação pertence ao usuário logado (`get_object_or_404`)
- Redireciona para a lista de transações após salvar

---

### 4. Agrupamento Mensal e Gráfico de Fluxo Receita/Despesa

**Data:** Junho 2026

**Descrição:** Listagem de transações agora agrupada por mês com subtotais, filtro por mês, e gráfico de linha no dashboard mostrando receitas e despesas dos últimos 6 meses.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `finance/views.py` | View `finance_list` agora agrupa por mês com `grouped_transactions`, filtro `?mes=` e subtotais |
| `templates/finance_list.html` | Tabela com cabeçalhos de mês, subtotais de receitas/despesas e seletor de filtro |
| `dashboard/views.py` | View `home` calcula receitas/despesas mensais dos últimos 6 meses (`chart_labels`, `chart_income`, `chart_expense`) |
| `templates/dashboard.html` | Gráfico de linha com 2 séries (Receitas verde, Despesas vermelha) e labels dinâmicos |

**Detalhes técnicos:**
- Listagem usa `TruncMonth` do Django para listar meses disponíveis no filtro
- Agrupamento feito em Python com dict de grupos por `YYYY-MM`
- Cada grupo exibe subtotal de receitas e despesas do mês
- Gráfico do dashboard mostra 6 meses com dados reais (não mais dados fictícios)
- Eixo X com abreviações dos meses (`month_abbr`)

---

### 5. Transações Parceladas

**Data:** Junho 2026

**Descrição:** Adicionado suporte a lançamento de despesas parceladas. Ao marcar "Pagamento parcelado", o sistema divide automaticamente o valor total em N parcelas mensais.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `finance/models.py` | +4 campos: `is_installment`, `installment_total`, `installment_number`, `installment_group` |
| `finance/forms.py` | Campos `is_installment` (checkbox) e `installment_total` com validação de divisibilidade |
| `finance/views.py` | Lógica de criar N transações em lote com `relativedelta` |
| `templates/finance_add.html` | JS que mostra/esconde campos de parcelamento |
| `templates/finance_list.html` | Badge "1/12" nas transações parceladas |
| `static/css/style.css` | Classe `.badge-installment` |
| `requirements.txt` | `python-dateutil==2.9.0` |

**Melhoria visual (Junho 2026):**
- Toggle switch estilizado no lugar de checkbox padrão
- Preview dinâmico: "12x de R$ 100,00 — sem juros" conforme usuário digita
- Campos de parcelamento em container com fundo escuro consistente
- Labels e placeholders mudam dinamicamente ao ativar/desativar parcelamento
- Toggle posicionado logo após o campo Valor, antes dos demais campos (fluxo natural: descreve → valor → parcelamento → data → categoria → tipo)

**Detalhes técnicos:**
- Toggle switch "Pagamento parcelado" no formulário de nova transação
- Ao ativar, aparecem campos: "Número de parcelas" com preview do cálculo
- Validação: valor total deve ser exatamente divisível pelo número de parcelas
- Cada parcela é uma `Transaction` individual com `installment_group` UUID compartilhado
- Parcela 1 na data informada, parcela 2 no mês seguinte (+1 mês), etc.
- Badge roxo "1/12" na listagem identificando parcelas

---

## Pendências (não implementadas)

### 6. Categorias Personalizadas
**Descrição:** Permitir que o usuário crie suas próprias categorias em vez de usar as 8 fixas no model.
**Arquivos envolvidos:** `finance/models.py` (novo model `Category`), `finance/forms.py`, migrações
**Observação:** Model `Transaction.category` mudaria de `CharField` para `ForeignKey` para `Category`.

### 7. Filtros na Listagem
**Descrição:** Adicionar filtros por tipo (receita/despesa) e categoria na página de listagem (filtro por mês já implementado).
**Arquivos envolvidos:** `finance/views.py`, `templates/finance_list.html`
**Observação:** Usar `django-filter` ou filtro manual via `request.GET`.

### 8. Exportar Transações (CSV)
**Descrição:** Botão para exportar as transações do usuário em formato CSV.
**Arquivos envolvidos:** `finance/views.py`, `finance/urls.py`, `templates/finance_list.html`
**Observação:** Usar `csv` module do Python ou `HttpResponse` com `content_type=text/csv`.

### 9. Insight IA Real no Dashboard
**Descrição:** Substituir a regra simples de comparação receita/despesa por uma chamada real à Groq para gerar análise financeira contextual.
**Arquivos envolvidos:** `dashboard/views.py`, `dashboard/urls.py`
**Observação:** Reaproveitar o cliente Groq já configurado em `intelligence/views.py`.

### 10. Rate Limiting na API Groq
**Descrição:** Limitar chamadas à API Groq por usuário para controlar custos.
**Arquivos envolvidos:** `intelligence/views.py`
**Observação:** README já lista como pendência.

### 11. Password Reset (Esqueci Minha Senha)
**Descrição:** Fluxo completo de recuperação de senha por email.
**Arquivos envolvidos:** `core/urls.py`, `templates/`, `core/settings.py`
**Observação:** Django já fornece `django.contrib.auth.views.PasswordResetView`.

### 12. Testes Unitários e de Integração
**Descrição:** Cobrir models, views e a integração com Groq com testes.
**Arquivos envolvidos:** `finance/tests.py`, `intelligence/tests.py`, `dashboard/tests.py`, `users/tests.py`
**Observação:** README lista cobertura atual em 0%.

### 13. Bundle Local do Chart.js
**Descrição:** Substituir CDN do Chart.js por bundle local (elimina dependência externa).
**Arquivos envolvidos:** `templates/base.html`, `static/js/`
**Observação:** README já lista como pendência.

### 14. Migrar psycopg2-binary para psycopg2
**Descrição:** Substituir `psycopg2-binary` por `psycopg2` em produção (boas práticas).
**Arquivos envolvidos:** `requirements.txt`, `Dockerfile`
**Observação:** README já lista como pendência.

---

*Documentado em Junho 2026*
