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

---

### 27. Exclusão em Massa Mais Sutil + Exclusão de Grupo de Parcelas

**Data:** Junho 2026

**Descrição:** As ações de exclusão em massa ("Excluir todas as despesas" e "Excluir todas as receitas") estavam muito visíveis na listagem, ocupando espaço e distraindo. Foram movidas para um dropdown discreto ("Ações de exclusão"). Além disso, implementada a funcionalidade de excluir **todo o grupo de parcelas** de uma vez — útil para cancelar uma compra parcelada inteira.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `templates/finance_list.html` | Bulk actions convertidos em dropdown colapsável; botão "Excluir grupo" adicionado no cabeçalho de cada mês (apenas quando há parcelas) |
| `finance/views.py` | Nova view `finance_delete_installment_group` para deletar todas as transações com mesmo `installment_group` |
| `finance/urls.py` | Nova rota `installment-group/<uuid:group_id>/delete/` |
| `static/css/style.css` | Estilos para dropdown `.bulk-actions-dropdown` e botão sutil `.btn-secondary` para trigger |

**Detalhes técnicos:**

**1. Bulk Actions (Excluir por tipo) — mais sutis:**
- Antes: Dois botões vermelhos (`btn-danger-outline`) sempre visíveis na área `.bulk-actions`
- Agora: Um único botão discreto "Ações de exclusão" (`btn-secondary`, cor `var(--text-secondary)`, tamanho menor) que abre dropdown ao clicar
- Dropdown posicionado `position: absolute; right: 0` com sombra, borda, fundo `var(--bg-card)`
- Opções no dropdown: "Excluir todas as despesas" e "Excluir todas as receitas" — mesmas views, mesma proteção CSRF, mesma confirmação JS
- Fecha ao clicar fora (`document.addEventListener('click'...)`)

**2. Excluir Grupo de Parcelas:**
- No cabeçalho de cada mês agrupado, se a primeira transação do grupo tiver `is_installment=True` e `installment_group` definido, aparece botão "Excluir grupo"
- View `finance_delete_installment_group`: filtra `Transaction.objects.filter(user=request.user, installment_group=group_id)` e deleta em lote
- Mensagem de sucesso: `Grupo de parcelas "Descrição" (N parcelas) excluído com sucesso!`
- Rota: `POST /finance/installment-group/<uuid:group_id>/delete/` com nome `finance:delete_installment_group`
- Confirmação JS: `onclick="return confirm('Excluir TODAS as parcelas deste grupo? Esta ação não pode ser desfeita.')"`

**Impacto UX:**
- Listagem mais limpa — ações perigosas escondidas até necessárias
- Fluxo natural: usuário vê parcelamento (badge "1/12") → quer cancelar tudo → clica "Excluir grupo" no cabeçalho do mês
- Elimina necessidade de excluir parcela por parcela manualmente

**Segurança:**
- Ambas views usam `@require_POST` + `@login_required` + filtro `user=request.user`
- CSRF token obrigatório
- Confirmação JavaScript antes de enviar (dupla proteção: JS + view valida POST)

---

### 28. Filtro "Despesa Parcelada" + Visualização por Grupo de Parcelas

**Data:** Junho 2026

**Descrição:** Adicionada opção "Despesa Parcelada" no filtro de tipo. Ao selecionar, a listagem muda de agrupamento mensal para agrupamento por **grupo de parcelas** (`installment_group`). Cada grupo aparece como um card com: descrição, categoria, total da compra, número de parcelas, período (primeira/última data), e botão "Excluir todas" que remove todas as parcelas do grupo de uma vez.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `finance/views.py` | `apply_transaction_filters`: trata `tipo=despesa_parcelada` filtrando `type=despesa` + `is_installment=True`; `finance_list`: quando `selected_type == "despesa_parcelada"`, agrupa por `installment_group` em vez de mês; adiciona `type_choices` com nova opção |
| `finance/urls.py` | Rota `installment-group/<uuid:group_id>/delete/` → `finance_delete_installment_group` |
| `templates/finance_list.html` | Novo bloco condicional: se `selected_type == "despesa_parcelada"` renderiza cards `.installment-group-card` com tabela de parcelas; senão renderiza agrupamento mensal normal |
| `static/css/style.css` | Estilos para `.installment-group-card` (já cobertos por inline styles no template) |

**Detalhes técnicos:**

**1. Filtro "Despesa Parcelada":**
- Opção adicionada em `type_choices` no contexto: `("despesa_parcelada", "Despesa Parcelada")`
- Em `apply_transaction_filters`: `qs.filter(type="despesa", is_installment=True)`
- Combina com filtros de mês e categoria normalmente

**2. Agrupamento por Grupo de Parcelas (não por mês):**
- Quando `selected_type == "despesa_parcelada"`:
  - Itera `qs` e agrupa em dict por `installment_group` (UUID)
  - Cada grupo acumula: `description`, `category`, `total_amount` (soma das parcelas), `installment_total`, lista de `installments` (objetos Transaction), `first_date`, `last_date`
  - Ordena grupos por `first_date` decrescente (mais recentes primeiro)
  - Template recebe `grouped_transactions` com estrutura diferente: cada item tem `group_id`, `description`, `category`, `total_amount`, `installment_total`, `installments[]`, `first_date`, `last_date`

**3. Cards de Grupo de Parcelas (UI):**
- Cada grupo = um card (`.installment-group-card`) com:
  - Cabeçalho: descrição (roxo), metadados (qtd parcelas, categoria, período)
  - Total da compra em destaque (vermelho, maior)
  - Botão "Excluir todas" → POST para `finance:delete_installment_group` com confirmação JS
  - Tabela compacta das parcelas: colunas Parcela (1/12, 2/12...), Data, Valor, Status (Paga/Pendente), Ações (Marcar paga, Editar)
  - Parcelas pagas ficam com opacidade reduzida e texto tachado (`.paid-row`)

**4. Exclusão do Grupo:**
- View `finance_delete_installment_group` (reaproveitada da melhoria #27):
  - `Transaction.objects.filter(user=request.user, installment_group=group_id).delete()`
  - Mensagem: `Grupo de parcelas "Descrição" (N parcelas) excluído com sucesso!`
  - Redireciona para listagem mantendo filtro `?tipo=despesa_parcelada`

**Impacto UX:**
- Usuário filtra "Despesa Parcelada" → vê cada compra parcelada como um card único (ex: "Carro - 12x", "Moto - 24x")
- Visualização clara do total da compra, não parcelas espalhadas por meses
- Ação única para cancelar compra inteira: "Excluir todas"
- Ainda pode editar/marcar paga parcela individualmente se necessário
- Filtros de mês e categoria funcionam sobre os grupos (filtra grupos que tenham parcelas no mês/categoria)

**Segurança:**
- View usa `@require_POST` + `@login_required` + filtro `user=request.user`
- CSRF token no formulário
- Confirmação JS: `confirm('Excluir TODAS as N parcelas de "Descrição"? Esta ação não pode ser desfeita.')`

---

### 29. Correção: NoReverseMatch no Grupo de Parcelas (installment_group=None)

**Data:** Junho 2026

**Problema:** Ao acessar o filtro "Despesa Parcelada", ocorria `NoReverseMatch` com `group_id=None`. Transações importadas por CSV tinham `is_installment=True` mas `installment_group=NULL`. A URL `<uuid:group_id>` exigia UUID válido, e o template `{% url 'finance:delete_installment_group' group.group_id %}` falhava com `None`.

**Solução:**
- Removido `installment_group__isnull=False` do filtro (que ocultava as transações órfãs)
- Adicionado **backfill automático** na view `finance_list`: ao detectar transações com `installment_group=None`, agrupa por (descrição, installment_total), gera UUID e salva no banco
- Template defensivo: `{% if group.group_id %}` envolve o botão "Excluir todas"

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `finance/views.py` | Removido `installment_group__isnull=False` do filtro; adicionado backfill de UUID antes do agrupamento |
| `templates/finance_list.html` | `{% if group.group_id %}` envolvendo botão "Excluir todas" (defensivo) |

**Detalhes técnicos:**
- Backfill roda apenas na primeira requisição com `despesa_parcelada` após a correção
- Usa `(description, installment_total)` como chave de grupo — se duas compras diferentes tiverem mesma descrição e total, serão agrupadas juntas (edge case aceitável)
- Transações são atualizadas em lote com `Transaction.objects.filter(pk=tx.pk).update(installment_group=...)`
- QuerySet `qs` é reavaliado após o backfill (lazy evaluation do Django), então o agrupamento seguinte enxerga os UUIDs

---

### 30. Correção: Axes Bloqueava Todos os Usuários no Docker

**Data:** Junho 2026

**Problema:** `AXES_LOCKOUT_PARAMETERS = ["ip_address"]` combinado com ambiente Docker fazia com que tentativas falhas de UM usuário bloqueassem TODOS. Todos os containers acessam via o mesmo IP do gateway Docker (ex: `172.18.0.1`), então 5 falhas de `vani` impediam `admin` de logar.

**Solução:**
- Alterado `AXES_LOCKOUT_PARAMETERS` de `["ip_address"]` para `["username"]`
- Bloqueio passa a ser **por usuário**, não por IP

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `core/settings.py` | Adicionado `AXES_LOCKOUT_PARAMETERS = ["username"]` |

**Detalhes técnicos:**
- Antes: vani erra 5x → IP 172.18.0.1 bloqueado → admin também não loga (mesmo IP)
- Depois: vani erra 5x → apenas vani bloqueado → admin loga normalmente
- Admin pode desbloquear usuários via `/admin/axes/`
- Cooldown de 5 minutos (`AXES_COOLOFF_TIME`) continua funcionando por usuário
- `AXES_RESET_ON_SUCCESS = True` continua resetando a contagem ao logar corretamente
- Bloqueios anteriores no banco foram limpos (`TRUNCATE axes_accessattempt`)

---

### 31. Correção: Erro 500 no Registro (ValueError - multiple backends)

**Data:** Junho 2026

**Problema:** Ao cadastrar novo usuário, o registro retornava HTTP 500 com `ValueError: You have multiple authentication backends configured and therefore must provide the backend argument`. O `auth_login(request, user)` era chamado sem especificar qual backend usar, e com dois backends configurados (AxesStandaloneBackend e ModelBackend), o Django exigia que `user.backend` fosse definido explicitamente.

**Solução:** Adicionado `user.backend = "django.contrib.auth.backends.ModelBackend"` antes de `auth_login()`.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `users/views.py:16` | `user.backend = "django.contrib.auth.backends.ModelBackend"` antes de `auth_login(request, user)` |

**Detalhes técnicos:**
- `UserCreationForm.save()` cria o usuário mas não define `backend` — diferente de `authenticate()` que já retorna com `backend` preenchido
- Com `AUTHENTICATION_BACKENDS = ['axes.backends.AxesStandaloneBackend', 'django.contrib.auth.backends.ModelBackend']`, o login precisa saber qual backend usou
- AxesStandaloneBackend é usado para consultar o rate limit, ModelBackend para autenticar — definimos explícito para evitar ambiguidade

---

### 32. Correção: Import CSV Ignorava Arquivo (name do campo errado)

**Data:** Junho 2026

**Problema:** O modal de importar CSV enviava o arquivo com `name="csv_file"`, mas o formulário Django (`CSVImportForm`) espera `name="file"`. O arquivo era ignorado silenciosamente — `form.is_valid()` retornava falso porque o campo `file` estava vazio, nenhuma transação era criada e nenhum erro era exibido ao usuário.

**Solução:** Alterado `name="csv_file"` para `name="file"` no input do template.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `templates/finance_list.html:254` | `<input type="file" name="csv_file">` → `<input type="file" name="file">` |

**Detalhes técnicos:**
- `CSVImportForm` (finance/forms.py:72) define `file = forms.FileField(...)`
- Django forms usam o `name` do campo como chave no `request.FILES`
- O template foi escrito durante a reconstrução completa do `finance_list.html` (melhoria #28) e o nome do campo foi copiado errado
- Help text do modal também foi corrigido: antes mostrava cabeçalhos em inglês (`date,description,type...`), agora mostra o formato real esperado: `Data;Descrição;Categoria;Tipo;Valor;Parcela;Paga`

---

### 33. Correção: Migração Pendente no Model Finance

**Data:** Junho 2026

**Problema:** Ao iniciar o container, o migrate exibia: `Your models in app(s): 'finance' have changes that are not yet reflected in a migration`. As `Meta options` de `Category` e `Transaction` (verbose_name, ordering) foram alteradas nas melhorias #21 (localização pt-BR) mas a migração correspondente nunca foi gerada.

**Solução:** Gerada e aplicada a migração `0005_alter_category_options_alter_transaction_options.py`.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `finance/migrations/0005_alter_category_options_alter_transaction_options.py` | Nova migração com `AlterModelOptions` para Category e Transaction |

**Detalhes técnicos:**
- `python manage.py makemigrations` detectou as diferenças entre o model atual e a última migração
- Migration contém apenas `AlterModelOptions` — zero alterações de schema (colunas)
- `python manage.py migrate` aplicou a migração ao banco PostgreSQL
- O arquivo foi copiado do container para o host para persistir no build

---

### 34. Melhoria: CSV Import com Suporte a installment_group

**Data:** Junho 2026

**Problema:** Ao importar despesas parceladas via CSV, as transações eram criadas com `is_installment=True` e `installment_number`/`installment_total` preenchidos, mas **sem `installment_group`** (UUID). Isso impedia o agrupamento correto no filtro "Despesa Parcelada" e impedia a exclusão em grupo.

**Solução:** Gerado UUID de grupo automaticamente durante o import CSV, agrupando parcelas por (descrição, total de parcelas).

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `finance/views.py` | Adicionado dict `import_group_map` para rastrear grupos por chave `(descrição, installment_total)`; gerado `uuid.uuid4()` na primeira parcela de cada grupo; incluído `installment_group=installment_group` no `Transaction.objects.create()` |
| `templates/finance_list.html` | Help text do modal corrigido para mostrar o formato real do CSV |

**Detalhes técnicos:**
- `import_group_map` é um dict persistido durante o loop de importação
- Chave: `(raw_description, installment_total)` — mesma descrição + mesmo total = mesmo grupo
- UUID gerado na primeira ocorrência, reutilizado nas parcelas seguintes
- Transações não-parceladas continuam com `installment_group=None` (comportamento inalterado)

---

### 35. Aplicação Responsiva (Mobile First)

**Data:** Junho 2026

**Problema:** A aplicação não possuía nenhuma media query. Sidebar fixa de 250px, grids do dashboard sem wrap, padding excessivo no main-content, filtros com `min-width` fixo, tabelas sem adaptação mobile, chat com altura fixa de 600px, e variável CSS `--accent-1` inexistente quebrando links em páginas de autenticação.

**Solução:** Implementados 3 breakpoints com redesign completo para mobile:

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `static/css/style.css` | +300 linhas com regras responsivas, modal styles, sidebar toggle/overlay |
| `templates/base.html` | Botão hamburger, overlay, JS de toggle sidebar (fecha com overlay ou Escape) |
| `templates/dashboard.html` | Classe `.charts-grid` para empilhamento dos gráficos em mobile |
| `templates/login.html` | `--accent-1` → `--accent-blue` (2 ocorrências) |
| `templates/register.html` | `--accent-1` → `--accent-blue` (2 ocorrências: link + focus) |
| `templates/registration/password_reset_form.html` | `--accent-1` → `--accent-blue` |
| `templates/registration/password_reset_confirm.html` | `--accent-1` → `--accent-blue` |

**Breakpoints e comportamentos:**

**Tablet (≤768px):** Sidebar vira off-canvas (fixa, `transform: translateX(-100%)`, 260px), botão hamburger fixo no topo esquerdo, overlay com `backdrop-filter: blur`. Dashboard metrics: 2 colunas. Charts empilham (`grid-template-columns: 1fr`). Filtros empilham verticalmente com width 100%. Login card padding reduzido para 1.5rem. Chat container: 450px.

**Mobile (≤480px):** Sidebar max 280px. Metrics 1 coluna. Padding mínimo (0.75rem). Topbar empilha verticalmente, botões full-width. Divisor de ações some. Tabelas com padding reduzido (0.5rem). Card padding 1rem. Modal padding reduzido. Chat container 300px, input em coluna.

**Desktop pequeno (769-1024px):** Padding intermediário, filtros com `min-width: 140px`.

**Modal:** Adicionado CSS completo para `.modal` (overlay fixo, centralizado, backdrop-filter, max-height com scroll, sombra) — antes não existia, o modal aparecia sem posicionamento.

---

### 36. Progressive Web App (PWA)

**Data:** Junho 2026

**Descrição:** Implementado suporte a PWA para instalação como aplicativo nativo no celular/desktop, com cache offline de assets estáticos e botão de instalação discreto na tela de login.

**Arquivos criados:**

| Arquivo | Descrição |
|---|---|
| `static/manifest.json` | Web manifest: name, short_name, display standalone, theme/background color, ícones 192/512 |
| `static/icon-192.png` | Ícone PWA 192×192 (gradiente azul→roxo + gráfico de pizza, gerado com Pillow) |
| `static/icon-512.png` | Ícone PWA 512×512 (mesmo design) |
| `static/apple-touch-icon.png` | Ícone iOS 180×180 |
| `templates/sw.js` | Service Worker com network-first para HTML, cache-first para assets estáticos |

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `templates/base.html` | `<link rel="manifest">`, `<meta theme-color>`, meta tags iOS, `apple-touch-icon`, favicon; script PWA (beforeinstallprompt, appinstalled, registro SW) |
| `templates/login.html` | Botão `#pwa-install-btn` (oculto por padrão, aparece via beforeinstallprompt) |
| `static/css/style.css` | Classes `.pwa-install-btn` e `.pwa-hidden` |
| `core/urls.py` | Rota `/sw.js` servindo o service worker com `TemplateView` + `content_type="application/javascript"` |

**Detalhes técnicos:**

**1. Manifest:**
- `start_url: "/"`, `display: standalone`, `background_color: #141419` (fundo do app), `theme_color: #4f46e5` (accent-blue)
- Ícones com `purpose: "any maskable"` para adaptação automática a máscaras do SO

**2. Service Worker (sw.js):**
- **Network-first para HTML** (`event.request.mode === "navigate"`): sempre busca do servidor para garantir sessão atualizada. Se a rede falhar, fallback para cache. Isso resolve o problema de páginas autenticadas ficarem cached (usuário via PWA via diretamente para dashboard mesmo sem login).
- **Cache-first para assets estáticos** (CSS, imagens, manifest): serve instantaneamente do cache, atualiza em segundo plano.
- **Network-only** para API calls e outros: nunca cacheia respostas dinâmicas.
- Cache versionado (`smartfinance-v2`) para controle de atualizações.
- `skipWaiting()` + `clients.claim()` para ativar o novo SW imediatamente.
- Filtro por `/admin/` — admin nunca é cacheado.

**3. Botão de Instalação:**
- Posicionado na tela de login, abaixo do link "Cadastre-se"
- Estilo discreto: borda sutil (`1px solid var(--border-color)`), cor secundária, hover com borda azul
- Oculta automaticamente quando o app já está instalado (`appinstalled` event)
- Não aparece em navegadores que não suportam PWA (`beforeinstallprompt` nunca dispara)
- Mobile: botão full-width com padding maior

**4. Ícones:**
- Gerados com Python/Pillow via script descartável (`static/gen_icons.py`)
- Design: gradiente vertical azul (#4f46e5) → roxo (#9333ea) com gráfico de pizza em branco
- 3 tamanhos: 192px (PWA), 512px (PWA/splash), 180px (iOS)

---

### 37. Notificações com Auto-Fade

**Data:** Junho 2026

**Problema:** Mensagens de sucesso/erro (Django messages framework) ficavam fixas no topo do dashboard/settings sem nunca desaparecer, obrigando o usuário a recarregar a página para sumirem.

**Solução:** Adicionadas classes CSS de notificação com transição de fade-out + JavaScript que auto-dispensa após 4 segundos.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `static/css/style.css` | Classes `.notification`, `.notification-success`, `.notification-error`, `.notification.fade-out` (opacity 0 + translateY -8px em 500ms) |
| `templates/base.html` | JS: `querySelectorAll('.notification')` → setTimeout 4s → add `fade-out` → 500ms → `display: none` |
| `templates/dashboard.html` | Mensagens migradas de inline styles para `.notification notification-success/error` |
| `templates/settings.html` | Mensagens migradas de inline styles para `.notification notification-success/error` |

**Detalhes técnicos:**
- Transição CSS: `opacity 0.5s ease, transform 0.5s ease`
- Timer: 4 segundos visível → 500ms fade → oculto (total 4.5s)
- Login.html mantém mensagens sem auto-fade (erros de autenticação não usam `.notification`)
- Mensagens de erro (tag `error`) também sofrem fade — diferenciadas por cor vermelha (`.notification-error`)

---

### 38. Correção: SW Cacheava Página Autenticada (PWA)

**Data:** Junho 2026

**Problema:** O Service Worker original usava estratégia **cache-first** para todas as requisições GET, incluindo páginas HTML. Quando o usuário logava e depois fechava o app, o SW servia a página do dashboard do cache — pulando a tela de login e mostrando conteúdo autenticado sem sessão válida.

**Solução:** Estratégia diferenciada por tipo de requisição:

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `templates/sw.js` | Cache version bump v1→v2; implementa network-first para HTML, cache-first para assets, network-only para APIs |

**Detalhes técnicos:**
- `event.request.mode === "navigate"` → **network-first**: busca do servidor → cacheia resposta → retorna. Se rede falha → fallback para cache (offline mode)
- `isStatic(url)` → **cache-first**: serve do cache instantaneamente, sem fetch
- Demais requisições → **network-only**: nunca cacheia (APIs, admin, etc.)

---

### 40. Reports: botão "Selecionar todos" + design moderno

**Data:** Junho 2026

**Descrição:** Adicionado toggle "Selecionar todos" / "Limpar todos" no seletor de meses + melhorias visuais com glassmorphism, gradientes e micro-interações.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `templates/finance_reports.html` | Botão "Todos" com toggle select/deselect, contador de seleção, JS `updateCountAndSelectAll()` |
| `static/css/style.css` | `.card::before` com borda gradiente sutil; `.reports-select-all-btn`; `.reports-filter-count`; `.reports-month-card` com checkmark, sombra hover, gradiente selected; `.reports-summary-card::after` com barra gradiente no topo; barras income/expense com `linear-gradient`; títulos de tabela com cor mais suave; evolução com barra mais alta e gradiente |

**Detalhes técnicos:**

**1. Botão "Todos":**
- Um único botão que alterna entre "Selecionar todos" (icone square-check) e "Limpar todos" (ícone rectangle-xmark + classe .active com cor vermelha)
- Atualiza todos os checkboxes e labels em uma única ação
- Estado sincronizado com contador de seleção: se todos marcados, botão vira "Limpar todos"

**2. Contador de seleção:**
- Badge `.reports-filter-count` exibe "N selecionado(s)" em tempo real
- Atualizado via JS a cada mudança de checkbox

**3. Design visual:**
- `.card::before` com `mask-composite: exclude` para criar borda gradiente sutil (blue→transparent→purple) sem afetar conteúdo
- `.reports-month-card.selected` com gradiente de fundo (blue→purple) e glow via box-shadow
- `.reports-month-card.selected::after` com checkmark (FontAwesome) no canto
- `.reports-summary-card::after` com barra gradiente horizontal no topo (3px, blue→purple)
- `.reports-bar-income` e `.reports-bar-expense` com gradiente horizontal
- `.evolution-up` / `.evolution-down` com gradiente horizontal para barras mais vibrantes
- Texto de título de tabela com `--text-secondary` (mais suave que azul)

**4. Micro-interações:**
- Hover nos cards de mês: `translateY(-1px)` + `box-shadow` com glow azul
- Transições suaves em todas as propriedades animáveis
- Card summary com ::after barra gradiente para identidade visual consistente

---

### 39. Relatórios Comparativos com Exportação PDF

**Data:** Junho 2026

**Descrição:** Implementada página de relatórios financeiros comparativos entre meses, com tabela de resumo (receitas/despesas/saldo por mês) e detalhamento por categoria. Geração de PDF via WeasyPrint com layout profissional.

**Arquivos criados:**

| Arquivo | Descrição |
|---|---|
| `templates/finance_reports.html` | Página de relatórios com multi-select de meses, tabela resumo e tabela por categoria |
| `templates/finance_reports_pdf.html` | Template otimizado para PDF (landscape, cores, tabelas) |
| `finance/templatetags/finance_extras.py` | Filter `get_item` para acessar dicts no template |

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `finance/views.py` | View `finance_reports` (render HTML) e `finance_reports_pdf` (gera PDF com WeasyPrint); imports `Sum`, `render_to_string`, `HTML` |
| `finance/urls.py` | Rotas `reports/` e `reports/pdf/` |
| `templates/base.html` | Link "Relatórios" na sidebar (com ícone chart-column) |
| `static/css/style.css` | Estilos para cards de meses, tabelas comparativas, barras de progresso, evolução, gradiente sutil nas bordas dos cards |
| `requirements.txt` | Adicionado `weasyprint==69.0` |
| `Dockerfile` | Adicionados pacotes do sistema: `libpango-1.0-0`, `libpangocairo-1.0-0`, `libgdk-pixbuf-2.0-0`, `libffi-dev`, `libcairo2` |

**Detalhes técnicos:**

**1. Arquitetura dos Dados:**
- `finance_reports()` recebe `meses` (GET list) → filtra `Transaction` por mês/ano
- Para cada mês: agrega receitas/despesas totais (`Sum`) e quebra por categoria
- `category_rows`: lista de dicts com `{category, month_str: {income, expense}}`
- `months_data`: lista com `{month_str, income, expense, balance, categories}`

**2. Template HTML (finance_reports.html):**
- Multi-select para escolher múltiplos meses (Ctrl+Click)
- Botão "Comparar" + "Limpar" filtros
- Tabela "Resumo por Mês": Receitas | Despesas | Saldo (linhas) × meses (colunas)
- Tabela "Detalhamento por Categoria": cada categoria × (Rec./Desp.) por mês
- Botão "Exportar PDF" visível apenas quando há seleção
- Usa filter `{% load finance_extras %}` → `{{ row|get_item:month_str }}`

**3. Geração de PDF (finance_reports_pdf):**
- Template isolado `finance_reports_pdf.html` com CSS próprio para impressão
- `@page { margin: 2cm; size: A4 landscape; }` — paisagem para largura das tabelas
- WeasyPrint: `HTML(string=html_string, base_url=...).write_pdf()`
- `base_url` aponta para a raiz da aplicação para resolver URLs de assets
- Response: `Content-Disposition: attachment; filename="relatorio_financeiro.pdf"`
- Fallback: se nenhum mês selecionado, usa o mês mais recente com transações

**4. Segurança:**
- `@login_required` em ambas views
- Filtro `user=request.user` em todas as queries
- PDF gerado apenas com dados do usuário logado

**5. UX:**
- Multi-select substituído por cards clicáveis com checkbox estilizado (hidden input + label)
- Cards selecionados: borda azul, fundo com gradiente, checkmark no canto superior direito
- Cards: hover com sombra e translateY para feedback visual
- Botão "Comparar" desabilitado quando nenhum mês selecionado
- Botão "Limpar" para resetar filtros rapidamente
- Botão PDF só aparece quando há meses selecionados
- Tabelas com `overflow-x: auto` para mobile

---

### 41. Página de Análise Financeira (client-side puro)

**Data:** Junho 2026

**Descrição:** Nova página de análise financeira 100% client-side seguindo o padrão do dashboard de orçamento familiar de referência. Toda a lógica de filtro, KPIs, gráfico e heatmap roda no navegador com dados reais serializados pela view.

**Arquivos criados:**

| Arquivo | Descrição |
|---|---|
| `templates/finance_analysis.html` | Template SPA-like com seletor de meses (toggle buttons), 4 KPIs, gráfico Observable Plot, heatmap, projeção de metas |

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `finance/views.py` | View `finance_analysis` serializa todas as transações em array flat `BUDGET_DATA` + lists de meses/categorias → 4 variáveis JSON |
| `finance/urls.py` | Nova rota `analysis/` |
| `templates/base.html` | Link "Análise" na sidebar; blocos `{% block extra_head %}` e `{% block extra_scripts %}` |
| `static/css/style.css` | Estilos para `.analysis-*` (botões de mês toggle pill, KPI cards, grid 2fr+1fr, chart, heatmap, goals), responsivo |

**Detalhes técnicos:**

**1. Arquitetura (cópia do código de referência):**
- View envia 4 JSONs: `BUDGET_DATA` (flat `{month, category, type, value}`), `MONTH_KEYS`, `MONTH_LABELS`, `CATEGORIES`
- Template carrega tudo em `const` no `{% block extra_scripts %}`
- `init()` → `renderMonthFilters()` + `updateDashboard()`
- `toggleMonth(month)` atualiza `selectedMonths[]`, re-renderiza botões e dashboard
- `updateDashboard()` filtra `BUDGET_DATA` pelos meses selecionados → `updateKPIs()` + `renderChart()` + `renderHeatmapTable()` + `renderGoals()`
- Zero page reload — tudo client-side (exatamente como o referência)

**2. KPIs:**
- Média de Receitas / Despesas: `total / numMonths`
- Mês mais econômico: maior saldo (`inc - exp`) entre os meses selecionados
- Taxa de Poupança: `avgSavings / avgIncome * 100`, com barra de progresso colorida (>20% verde, >0% azul, negativa vermelha)

**3. Gráfico (Observable Plot):**
- `Plot.lineY` com `curve: monotone-x` para linhas suaves
- `Plot.dot` com `tip: true` para tooltip ao passar mouse
- `Plot.text` com `selectLast` para label da categoria no final da linha
- Tema escuro: `background: transparent`, texto `#cbd5e1`
- Re-renderiza em `resize` para adaptar ao container

**4. Heatmap:**
- Categorias como linhas, meses como colunas
- Destaque `.cell-peak` no valor máximo de cada linha (pico de gasto)
- Coluna "Média" ao final
- Zero se não há despesa na categoria/mês

**5. Metas (simuladas):**
- 3 metas fixas: Reserva de Emergência (R$ 20k), Viagem (R$ 5k), Troca de Carro (R$ 15k)
- Projeção: `remaining / (avgSavings * 0.3)` — quantos meses para atingir
- Barra de progresso colorida por meta (verde, azul, indigo)

**6. Dependências:**
- D3.js v7 + Observable Plot 0.6 via CDN no `<head>`

**7. Segurança:**
- `@login_required`, filtro `user=request.user`, `DecimalEncoder` para serialização segura

---

### 42. Correção botão PWA na tela de login

**Data:** Junho 2026

**Descrição:** O botão "Instalar App" na tela de login não aparecia no celular porque dependia do evento `beforeinstallprompt`, que só dispara após engajamento significativo no Chrome. Corrigido para sempre exibir o botão, com fallback explicativo caso o evento não tenha disparado.

**Arquivos alterados:**

| Arquivo | Mudança |
|---|---|
| `templates/login.html` | Botão sem classe `pwa-hidden` (sempre visível); adicionado `#pwa-fallback` com instrução de instalação manual |
| `templates/base.html` | JS do PWA: se `deferredPrompt` existe → prompt nativo; senão → esconde botão e mostra fallback |
| `static/css/style.css` | Classe `.pwa-hidden` removida; classe `.pwa-fallback` com estilo de card informativo |

**Detalhes técnicos:**

**Problema:**
- `beforeinstallprompt` só dispara após múltiplas visitas e ~30s de engajamento
- Na tela de login, se o usuário loga rápido, o evento nunca dispara → botão fica oculto pra sempre
- Depois de logado, o botão não existe no layout autenticado

**Solução:**
- Botão começa visível (remove `pwa-hidden`)
- Se `deferredPrompt` existe ao clicar → `prompt()` nativo (instalação padrão)
- Se não existe → esconde botão e mostra fallback: *"Para instalar, use o menu do navegador: Compartilhar → Adicionar à Tela Inicial"*
- Fallback também desaparece quando `appinstalled` dispara
