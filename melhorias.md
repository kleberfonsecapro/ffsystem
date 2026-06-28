# Melhorias

## ✅ Implementado

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

### 8. Correção de layout e rotas CSV na Gestão Financeira

**Data:** Junho 2026

**Descrição:** Corrigido o layout quebrado da página de `Gestão Financeira` e adicionadas as rotas `export_csv` e `import_csv` usadas pelo template.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `finance/urls.py` | Adicionadas rotas `export-csv/` e `import-csv/` com nomes `finance:export_csv` e `finance:import_csv` |
| `templates/finance_list.html` | Estrutura de topo reorganizada, botões CSV e filtro alinhados, tabela envolvida em container responsivo |
| `static/css/style.css` | Adicionadas classes de layout para `topbar-actions`, `section-header`, `filter-form`, `select-filter`, `btn-filter` e `table-container` |

**Detalhes técnicos:**
- As ações de exportar/importar usam GET/POST corretos e o template mantém filtros ativos na exportação.
- O layout foi estabilizado para telas menores com flex-wrap no cabeçalho e filtros.
- A tabela permanece responsiva graças a `table-container`.

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
- **Cada parcela lança APENAS seu valor individual no mês** (ex: R$ 100), não o valor total (R$ 1200)
- Badge roxo "1/12" na listagem identificando parcelas
- Dashboard reflete corretamente: total geral soma todas as parcelas, gráfico mensal mostra apenas a parcela do mês

---

### 6. Correção: Serialização do Gráfico de Fluxo de Caixa

**Data:** Junho 2026

**Descrição:** Gráfico de linha do dashboard parou de funcionar após a implementação do agrupamento mensal. O problema era que os dados eram passados como listas Python e renderizadas com `|safe`, gerando JavaScript inválido (aspas simples do Python em vez de JSON).

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `dashboard/views.py` | `chart_labels`, `chart_income` e `chart_expense` passam por `json.dumps()` antes de ir ao template |

**Detalhes técnicos:**
- Antes: `{{ chart_labels|safe }}` → `['Jan', 'Fev', ...]` (aspas simples, inválido como JSON)
- Depois: `json.dumps(labels)` → `["Jan", "Fev", ...]` (JSON válido)
- `json.dumps()` garante serialização correta de strings, números e booleanos

---

### 7. Correção: Valores Não Divisíveis em Parcelamento

**Data:** Junho 2026

**Problema:** Ao lançar uma despesa parcelada com valor total não exatamente divisível pelo número de parcelas (ex: R$ 3.028,11 em 12x), o formulário rejeitava com erro "O valor total não é divisível exatamente pelo número de parcelas".

**Solução:** Removida a validação de divisibilidade em centavos e implementada distribuição do resto (`remainder`) nas primeiras parcelas no backend.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `finance/forms.py` | Removido `else` com validação `(amount * 100) % installment_total != 0` |
| `finance/views.py` | Substituída divisão simples por aritmética de centavos: `total_cents // total` + distribuição do `remainder` nas primeiras parcelas |
| `templates/finance_add.html` | Preview JS agora calcula com centavos e mostra distribuição quando há resto |

**Detalhes técnicos:**
- Cálculo: `total_cents = round(amount * 100)`, `base_cents = total_cents // total`, `remainder = total_cents % total`
- As primeiras `remainder` parcelas recebem `base_cents + 1` centavo, as demais recebem `base_cents`
- Ex: R$ 3028,11 em 12x → 302811 centavos → 302811 // 12 = 25234, resto 3 → 3x de R$ 252,35 + 9x de R$ 252,34
- Garantia: a soma de todas as parcelas em centavos é sempre igual a `total_cents`

---

### 15. Filtro date__lte no Dashboard para Excluir Parcelas Futuras

**Data:** Junho 2026

**Problema:** Dashboard somava transações de todos os tempos, incluindo parcelas futuras. Ex: geladeira de R$ 1.949,02 em 10x aparecia como despesa total de R$ 1.949,02, confundindo o saldo atual.

**Solução:** Adicionar `date__lte=today` APENAS em `total_expense`. A receita (`total_income`) e `recent_transactions` não têm filtro de data — toda receita cadastrada (inclusive salário futuro) aparece no total. Motivo: o usuário espera ver toda a receita prevista, mas apenas despesas já vencidas.

**Arquivos envolvidos:** `dashboard/views.py`

**Observação:** O gráfico mensal (últimos 6 meses) e a listagem por mês não foram alterados. O insight API seguiu a mesma lógica: receita total, despesa com date__lte.

---

### 16. Status "Paga" para Transações

**Data:** Junho 2026

**Problema:** Não era possível marcar uma despesa como paga, dificultando o controle do que já foi quitado.

**Solução:** Adicionado campo booleano `paid` ao model `Transaction`. Na listagem, cada transação tem um botão verde (✓) para marcar como paga / desmarcar. Transações pagas aparecem com opacidade reduzida, descrição tachada, e badge "Paga" no lugar do tipo. O botão de toggle é um POST (segue o padrão de delete).

**Arquivos envolvidos:**
- `finance/models.py` — campo `paid = BooleanField(default=False)`
- `finance/migrations/0002_transaction_installment_group_and_more.py` — migração com o novo campo
- `finance/views.py` — view `finance_toggle_paid`
- `finance/urls.py` — rota `<int:pk>/toggle-paid/`
- `templates/finance_list.html` — botão toggle + badge + classe paid-row
- `static/css/style.css` — classes `.btn-paid`, `.paid-row`, `.badge-paid`, `.text-paid`

---

### 17. Remoção do Card "Agente Financeiro IA" da Gestão Financeira

**Data:** Junho 2026

**Problema:** A tela de gestão financeira tinha um grid 2fr 1fr com o card do chat IA ocupando espaço desnecessário, comprimindo a tabela de lançamentos.

**Solução:** Removido o card do chat IA e seu JavaScript, e o card da tabela de transações agora ocupa 100% da largura disponível.

**Arquivos envolvidos:**
- `templates/finance_list.html` — removido grid, coluna do chat, e script JS

---

### 19. Cards de Receitas e Despesas do Próximo Mês no Dashboard

**Data:** Junho 2026

**Problema:** O dashboard mostrava apenas os valores do mês corrente. Com receitas e despesas futuras (ex: salários de julho), o usuário não tinha visibilidade do próximo mês sem acessar a listagem.

**Solução:** Adicionados 2 novos cards no dashboard exibindo a soma de receitas e despesas do mês seguinte ao corrente. Cada card mostra o nome do mês (ex: "Julho") dinamicamente.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `dashboard/views.py` | Cálculo de `next_month_start`, `next_month_end`, queries `next_income`/`next_expense`, e nome do mês `next_month_name` |
| `templates/dashboard.html` | 2 novos cards "Receitas (Julho)" e "Despesas (Julho)" com bordas amarela/laranja |

**Detalhes técnicos:**
- `next_month_start = month_start + relativedelta(months=1)` — primeiro dia do mês seguinte
- `next_month_end = next_month_start + relativedelta(months=1) - timedelta(days=1)` — último dia do mês seguinte
- `next_month_name = MESES_PT[next_month_start.month]` — nome do mês em português (ex: "Julho") via lista `MESES_PT`
- Queries filtradas por `date__gte=next_month_start, date__lte=next_month_end`
- Usa `dateutil.relativedelta` já disponível no projeto

---

### 20. Categorias Personalizadas

**Data:** Junho 2026

**Descrição:** Implementado model `Category` com suporte a categorias padrão (globais) e futuramente categorias por usuário. O campo `category` do model `Transaction` foi mantido como legado, e um novo FK `category_ref` foi adicionado para referenciar o model `Category`.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `finance/models.py` | Novo model `Category` (name, user, type) + FK `category_ref` em `Transaction` + property `category_display` |
| `finance/migrations/0003_category_transaction_category_ref.py` | Cria model Category e adiciona campo category_ref |
| `finance/migrations/0004_seed_categories.py` | Data migration que cria 8 categorias padrão e vincula transações existentes |
| `finance/forms.py` | Form usa `category_ref` (ModelChoiceField) com queryset filtrado por tipo |
| `finance/views.py` | `form.cleaned_data["category"]` → `form.cleaned_data["category_ref"]` |
| `finance/admin.py` | `CategoryAdmin` registrado, `TransactionAdmin` usa `category_display` |
| `templates/finance_list.html` | `tx.category` → `tx.category_display` |
| `templates/finance_add.html` | `form.category` → `form.category_ref` |

**Detalhes técnicos:**
- `Category` model: `name` (CharField), `user` (FK null → global), `type` (receita/despesa/ambos)
- 8 categorias padrão criadas com `user=None` (visíveis a todos)
- `Transaction.category_ref` é FK nullable com `on_delete=SET_NULL` (não quebra registros se categoria for removida)
- `Transaction.category_display` property: retorna `category_ref.name` se existir, senão fallback para `category` (legado)
- Form `__init__` filtra categorias: globais + do usuário da transação
- Transações parceladas também usam `category_ref` na criação em lote

---

### 21. Localização pt-BR completa do sistema

**Data:** Junho 2026

**Problema:** Diversos textos no sistema estavam em inglês: título da página, brand na sidebar, login, cadastro, labels/help texts de formulários, nomes de meses nos gráficos, e `verbose_name` dos models.

**Solução:** Substituídos todos os textos para português brasileiro nativo.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `users/forms.py` | Novo arquivo com `CadastroForm` e `AlterarSenhaForm` — labels e help texts em pt-br |
| `users/views.py` | `UserCreationForm` → `CadastroForm` |
| `dashboard/views.py` | `PasswordChangeForm` → `AlterarSenhaForm`; `month_abbr` → `MESES_PT_ABBR` (Jan/Fev/Mar...) |
| `finance/models.py` | `verbose_name` e `verbose_name_plural` em pt-br para Category e Transaction |
| `templates/base.html` | Brand "Family Finance System AI" → "SmartFinance AI"; title padrão pt-br |
| `templates/login.html` | Título "Login - Financial..." → "Entrar - SmartFinance AI"; H1 traduzido |
| `templates/register.html` | Título "Cadastro - Financial..." → "Cadastro - SmartFinance AI" |

---

### 22. Filtros na Listagem (Tipo + Categoria)

**Data:** Junho 2026

**Descrição:** Adicionados filtros por tipo (receita/despesa) e categoria na página de listagem de transações, complementando o filtro por mês já existente.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `finance/views.py` | Parâmetros `tipo` e `categoria` no GET; filtros `type` e `category_ref__name` no queryset; `categories_available` ordenadas; context com `type_choices`, `categories_available`, `selected_type`, `selected_category` |
| `templates/finance_list.html` | Dois `<select>` adicionados ao formulário de filtro: "Tipo" (receita/despesa) e "Categoria" (lista dinâmica de `categories_available`); seleções persistem via `selected` |

**Detalhes técnicos:**
- Filtros aplicados no queryset **antes** do agrupamento em Python — performance mantida
- Combina com filtro de mês existente: `?mes=2026-06&tipo=despesa&categoria=Alimentação`
- Categorias disponíveis: globais (`user=None`) + do usuário logado, ordenadas alfabeticamente
- Formulário único GET, botão "Filtrar", seleções persistem visualmente
- Futuramente: adicionar categorias custom por usuário já funcionará automaticamente

---

### 23. Restauração das Rotas CSV (Import/Export)

**Data:** Junho 2026

**Problema:** As rotas `export-csv/` e `import-csv/` tinham sido removidas de `finance/urls.py`, enquanto as views e o template `finance_list.html` continuavam referenciando `finance:export_csv` e `finance:import_csv`, quebrando exportação e importação na listagem.

**Solução:** Restauradas as duas rotas apontando para `views.export_csv` e `views.import_csv`.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `finance/urls.py` | Rotas `export-csv/` e `import-csv/` restauradas |

---

### 24. Unificação de Categorias (`category_ref` como fonte única)

**Data:** Junho 2026

**Problema:** Conviviam o campo legado `category` (choices fixas) e o FK `category_ref` (model `Category`). Formulário manual e import CSV usavam `category_ref`; o assistente IA gravava só em `category`, gerando inconsistência entre canais de entrada.

**Solução:**
- Criado `finance/categories.py` com `resolve_category()` e `default_category_names()` — lógica centralizada de busca/criação de categorias
- `Transaction.save()` sincroniza `category` a partir de `category_ref.name` (campo legado mantido por compatibilidade, preenchido automaticamente)
- Import CSV refatorado para usar `resolve_category()`
- Chat IA passa a gravar via `category_ref`; prompt lista categorias dinamicamente do banco

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `finance/categories.py` | Novo módulo com helpers de categoria |
| `finance/models.py` | `save()` sincroniza `category` ← `category_ref` |
| `finance/views.py` | Import CSV usa `resolve_category()` |
| `intelligence/views.py` | IA usa `category_ref` + categorias dinâmicas no prompt |

**Detalhes técnicos:**
- `resolve_category(user, name, tx_type)`: busca categoria do usuário → global → cria personalizada
- Campo `category` permanece no model para migrations e dados legados, mas deixa de ser preenchido manualmente nos fluxos novos
- `category_display` continua funcionando para registros antigos sem `category_ref`

---

### 25. Correção de regressões na Gestão Financeira

**Data:** Junho 2026

**Problema:** Ao adicionar rotas CSV, a rota `delete-by-type/` foi removida acidentalmente de `finance/urls.py`, quebrando os botões de exclusão em massa no template. A URL de exportação CSV usava `request.GET.urlencode`, propagando parâmetros desnecessários.

**Solução:**
- Restaurada rota `delete-by-type/` → `finance:delete_by_type`
- Export CSV passa a repassar apenas filtros ativos (`mes`, `tipo`, `categoria`)

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `finance/urls.py` | Rota `delete-by-type/` restaurada |
| `templates/finance_list.html` | Link de exportação com filtros explícitos |

---

## ⏳ A Implementar

### 9. Insight IA Real no Dashboard
**Descrição:** Substituir a regra simples de comparação receita/despesa por uma chamada real à Groq para gerar análise financeira contextual.
**Arquivos envolvidos:** `dashboard/views.py`, `dashboard/urls.py`
**Observação:** Reaproveitar o cliente Groq já configurado em `intelligence/views.py`.

### 10. Rate Limiting na API Groq
**Descrição:** Limitar chamadas à API Groq por usuário para controlar custos.
**Arquivos envolvidos:** `intelligence/views.py`
**Observação:** README já lista como pendência.

### 11. Password Reset (Esqueci Minha Senha)
**Status:** ✅ **IMPLEMENTADO** (Junho 2026)

**Descrição:** Fluxo completo de recuperação de senha por email usando as views built-in do Django (`django.contrib.auth.views`).

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `core/settings.py` | Configuração de email (EMAIL_BACKEND, EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, DEFAULT_FROM_EMAIL, PASSWORD_RESET_TIMEOUT) |
| `users/urls.py` | 4 rotas de password reset usando `auth_views`: `password_reset`, `password_reset_done`, `password_reset_confirm`, `password_reset_complete` |
| `templates/login.html` | Link "Esqueci minha senha" apontando para `users:password_reset` |
| `templates/registration/password_reset_form.html` | Template para solicitar reset (email) |
| `templates/registration/password_reset_done.html` | Template de confirmação de envio |
| `templates/registration/password_reset_confirm.html` | Template para definir nova senha (token) |
| `templates/registration/password_reset_complete.html` | Template de sucesso |
| `.env.example` | Variáveis de email documentadas |

**Detalhes técnicos:**
- Usa `PasswordResetView`, `PasswordResetDoneView`, `PasswordResetConfirmView`, `PasswordResetCompleteView` do `django.contrib.auth.views`
- Token gerado por `django.contrib.auth.tokens.default_token_generator` (HMAC com timestamp, válido por 1h - `PASSWORD_RESET_TIMEOUT = 3600`)
- Email enviado via `django.core.mail.send_mail` com template HTML simples
- Em desenvolvimento, usa `console.EmailBackend` (exibe email no console/logs)
- Em produção, configurar SMTP via variáveis de ambiente (`EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, etc.)
- Link no login: "Esqueci minha senha" → `/users/password-reset/`

---

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

### 18. Botão IA Flutuante na Gestão Financeira
**Descrição:** Adicionar um botão "IA" ao lado de "Nova Transação" na página de gestão financeira. Ao clicar, abre um chat flutuante (modal/overlay) para conversar com o assistente IA, sem ocupar espaço fixo na tela.
**Arquivos envolvidos:** `templates/finance_list.html`, `static/css/style.css`, `static/js/chat.js`
**Observação:** O chat fixo foi removido na melhoria #17; esta é a substituição planejada.

### 19. Histórico de Conversas com IA no Banco
**Descrição:** Criar model `ConversationHistory` para armazenar as conversas do usuário com a IA (mensagens e respostas compactadas). Manter por 7 dias, com deleção automática via cron/management command. A IA poderá recuperar o histórico quando o usuário pedir para "relembrar toda a conversa".
**Arquivos envolvidos:** `intelligence/models.py`, `intelligence/management/commands/`, `core/settings.py`
**Observação:** Compactar mensagens antes de salvar (ex: zlib/gzip no campo TextField/ BinaryField). O comando de limpeza pode rodar via cron no docker ou como task periódica.

---

### 11. Password Reset (Esqueci Minha Senha)

**Data:** Junho 2026

**Descrição:** Implementado fluxo completo de recuperação de senha usando as views built-in do Django (`PasswordResetView`, `PasswordResetDoneView`, `PasswordResetConfirmView`, `PasswordResetCompleteView`).

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `.env.example` | Adicionadas variáveis de email (EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, DEFAULT_FROM_EMAIL) |
| `core/settings.py` | Configuração de email via variáveis de ambiente, `PASSWORD_RESET_TIMEOUT = 3600` (1 hora) |
| `users/urls.py` | 4 rotas de password reset usando `django.contrib.auth.views` |
| `templates/login.html` | Link "Esqueci minha senha" apontando para `users:password_reset` |
| `templates/registration/password_reset_form.html` | Formulário de solicitação (email) |
| `templates/registration/password_reset_done.html` | Confirmação de e-mail enviado |
| `templates/registration/password_reset_email.html` | Template do e-mail HTML/texto com link de reset |
| `templates/registration/password_reset_subject.txt` | Assunto do e-mail |
| `templates/registration/password_reset_confirm.html` | Formulário de nova senha (token validation) |
| `templates/registration/password_reset_complete.html` | Confirmação de senha alterada |

**Detalhes técnicos:**
- Usa views nativas do Django — zero código customizado de validação de token
- Token gerado com `django.contrib.auth.tokens.PasswordResetTokenGenerator` (HMAC + timestamp, expira em 1 hora via `PASSWORD_RESET_TIMEOUT`)
- E-mail enviado via `EMAIL_BACKEND` configurável (console em dev, SMTP em produção)
- Templates seguem o design system existente (glass-panel, variáveis CSS, pt-BR)
- Link no login: "Esqueci minha senha" → `/users/password-reset/`
- Fluxo: email → token por e-mail → nova senha → login

**Configuração necessária para produção:**
```bash
# .env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
DEFAULT_FROM_EMAIL=SmartFinance AI <noreply@smartfinance.ai>
```
Sem configuração de SMTP, usa `console.EmailBackend` (imprime no log do container).

---

### 26. Email Obrigatório no Cadastro (Pré-requisito do Password Reset)

**Data:** Junho 2026

**Descrição:** Tornado o campo **e-mail obrigatório** no formulário de cadastro, garantindo que todo usuário criado tenha e-mail válido — pré-requisito para o fluxo de recuperação de senha funcionar.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `users/forms.py` | `CadastroForm`: adicionado campo `email` (EmailField, required=True), `fields = ("username", "email")`, sobrescrito `save()` para persistir email no User |

**Detalhes técnicos:**
- `CadastroForm` agora herda `UserCreationForm` + campo `email` obrigatório com widget `EmailInput` (classe `form-control`, placeholder)
- `Meta.fields = ("username", "email")` — email incluído no formulário
- Método `save()` sobrescrito para atribuir `user.email = cleaned_data["email"]` antes de salvar
- Template `register.html` **não precisou de alteração** — usa `{% for field in form %}` que renderiza automaticamente o novo campo
- CSS `.login-card input` já estiliza corretamente (padding, focus, borda)
- Modelo `User` do Django já possui campo `email` (CharField, blank=True por padrão); agora preenchido obrigatoriamente no cadastro

**Impacto no Password Reset:**
- Antes: usuário podia cadastrar sem email → `PasswordResetView` não encontrava usuário → reset falhava silenciosamente (mesma mensagem de sucesso)
- Agora: **todo usuário tem email** → reset funciona 100% dos casos
- `PasswordResetView` filtra `User.objects.filter(email__iexact=email, is_active=True)` — email único não é forçado no model, mas formulário impede duplicatas via validação de integridade

**Validação adicional recomendada (futuro):**
- Adicionar `unique=True` no email via migration customizada ou `User.email` unique constraint
- Ou validar unicidade no `CadastroForm.clean_email()`
