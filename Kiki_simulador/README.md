# BODIVA Simulador — Simulador de Investimento em Obrigações do Tesouro e Ações da BODIVA

Simulador retrospetivo de investimento: o investidor define um montante, um
ativo e um período histórico, e o sistema calcula a rentabilidade nominal e a
rentabilidade real ajustada à inflação (IPC de Angola). Desenvolvido para
alinhar com o TFC "Simulador de Investimento em Obrigações de Tesouros e
Ações da BODIVA com Análise de Rentabilidade Real (ajustada com a inflação)".

## Stack

- **Backend**: Django 4.2 + Django REST Framework + JWT (SimpleJWT) + Argon2id
- **Frontend**: React 18 + Vite + Tailwind CSS + Recharts
- **Base de dados**: a tua própria base MySQL (`resumo_mercados` / `livros_de_ordens`), lida ao vivo

## Arquitectura de dados: uma só base, sem cópias

O Django liga-se **directamente** à tua base MySQL existente. As tuas duas
tabelas (`resumo_mercados`, `livros_de_ordens`) não são geridas nem alteradas
pelo Django — ele só lê. As tabelas próprias da aplicação (utilizadores,
carteiras, simulações, logs, inflação) vivem na mesma base MySQL, ao lado das
tuas, criadas pelo `migrate`.

Concretamente:

- `AtivoBodiva` é só um catálogo de metadados (nome comercial, tipo, ISIN,
  taxa de cupão, maturidade) — não guarda preço nenhum.
- `ResumoMercado` e `LivroDeOrdens` (em `models.py`) são modelos **não-geridos**
  (`managed = False`) mapeados directamente sobre as tuas tabelas reais. Toda
  a leitura de preços (simulações, gráficos, listagem de mercado) passa por
  aqui, sempre em tempo real — nunca há uma cópia desatualizada.
- Quando adicionas mais dados a `resumo_mercados` (pelo teu próprio scraper,
  fora do Django), aparecem automaticamente no simulador, sem precisares de
  correr nada.
- A única sincronização necessária é de **catálogo**: sempre que aparecer um
  código novo nas tuas tabelas, corre `python manage.py sincronizar_ativos`
  para lhe criar uma entrada no catálogo (nome provisório = código, que depois
  editas no painel de administrador).

## O que mudou em relação à primeira versão

O projeto original (antes de teres a tua base MySQL própria) implementava um
simulador de **negociação em tempo real** (compra/venda com livro de ordens
bid/ask). O TFC pede um simulador **retrospetivo**: o investidor escolhe um
ativo, um montante e um período já decorrido, e o sistema calcula o retorno
nominal e real desse investimento com base em preços históricos e no IPC. O
motor financeiro, os modelos e as páginas de simulação foram reescritos para
isso, e a lógica de IAC (imposto sobre mais-valias, que não consta do TFC)
foi removida.

Numa segunda fase, a app copiava os teus dados para uma tabela própria
(`PrecoHistorico`) via um comando de importação. Essa tabela foi removida —
agora lê-se sempre ao vivo de `resumo_mercados`, como descrito acima.

Cada investidor só pode ter **uma carteira fictícia** (RN003), imposto ao
nível da base de dados (`OneToOneField`), não apenas na aplicação.

## Estrutura de pastas

```
backend/
├── manage.py
├── .env.example                copiar para .env e preencher com as tuas credenciais MySQL
├── config/                     settings, urls, wsgi/asgi
└── bodiva_app/
    ├── models.py                User, Carteira, AtivoBodiva (catálogo),
    │                            ResumoMercado / LivroDeOrdens (não-geridos,
    │                            mapeiam as tuas tabelas reais), PosicaoCarteira,
    │                            MovimentoCarteira, HistoricoInflacao,
    │                            Simulacao, LogAuditoria
    ├── serializers.py
    ├── permissions.py           RBAC: IsAdministrador / IsInvestidor
    ├── admin.py                 Django admin (consulta e inserção manual)
    ├── views/
    │   ├── auth.py               registo, login com bloqueio (RN019), perfil,
    │   │                         recuperação de password
    │   ├── carteira.py           criar carteira, adicionar/remover ativo
    │   ├── simulacao.py          motor de simulação, dashboard investidor
    │   ├── mercado.py            catálogo, histórico de preços (ao vivo), inflação
    │   └── admin.py               utilizadores, inflação, ativos, logs, monitor
    ├── services/
    │   ├── motor_financeiro.py   cálculo de rentabilidade nominal/real
    │   ├── scraper_bodiva.py     raspagem opcional (BeautifulSoup4) — só precisas
    │   │                         disto se ainda não tiveres o teu próprio scraper
    │   └── auditoria.py          registo de logs
    └── management/commands/
        ├── sincronizar_ativos.py  python manage.py sincronizar_ativos
        ├── raspar_bodiva.py       python manage.py raspar_bodiva (opcional)
        └── seed_dados.py          python manage.py seed_dados

frontend/
└── src/
    ├── pages/                   páginas do investidor + pages/admin/
    ├── components/
    │   ├── dashboard/, simulacao/, shared/
    ├── services/api.js          toda a comunicação com o backend
    └── store/AuthContext.jsx    estado global de autenticação
```

## Como correr o backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copia `.env.example` para `.env` e preenche com as credenciais da tua base
MySQL (`meubanco_bodiva`):

```
DB_ENGINE=mysql.connector.django
DB_NAME=meubanco_bodiva
DB_USER=o_teu_utilizador_mysql
DB_PASSWORD=a_tua_password_mysql
DB_HOST=localhost
DB_PORT=3306
```

Depois:

```bash
python manage.py migrate          # cria as tabelas do Django; não toca nas tuas
python manage.py seed_dados       # cria um admin de demo + sincroniza o catálogo de ativos
python manage.py runserver
```

O `seed_dados` cria uma conta de administrador: `admin@bodiva-sim.ao` /
`Admin@2026` (**muda esta password antes de qualquer apresentação
pública**), semeia inflação de exemplo só se a tabela estiver completamente
vazia (nunca sobrepõe dados reais), e corre a sincronização do catálogo de
ativos a partir das tuas tabelas. Se só quiseres repetir a sincronização do
catálogo (por exemplo depois de raspar códigos novos), usa:

```bash
python manage.py sincronizar_ativos
```

A inflação (IPC) tem sempre de ser inserida à mão no painel de administrador
— nenhuma das tuas tabelas a contém.

### Sem base MySQL própria (modo demonstração)

Sem um `.env` configurado, o Django usa SQLite local — mas como
`resumo_mercados`/`livros_de_ordens` não existem nessa base, as páginas de
mercado e simulação vão dar erro. Para testar sem dados reais, cria essas
duas tabelas manualmente numa base MySQL de teste (o esquema exacto está em
`bodiva_app/models.py`, classes `ResumoMercado` e `LivroDeOrdens`) e aponta o
`.env` para lá.

### Scraper opcional

Se ainda não tiveres o teu próprio scraper a alimentar `resumo_mercados`,
`bodiva_app/services/scraper_bodiva.py` + `python manage.py raspar_bodiva`
são uma alternativa — mas os seletores CSS lá dentro são estimados, ajusta-os
ao HTML real de bodiva.ao antes de confiar neles.

Em produção, define `EMAIL_BACKEND` para um backend SMTP real (o backend
actual imprime os emails de recuperação de password na consola, útil só em
desenvolvimento).

## Como correr o frontend

```bash
cd frontend
npm install
npm run dev
```

Por defeito liga a `http://localhost:8000/api`. Para apontar a outro backend,
cria um ficheiro `.env` dentro de `frontend/` com `VITE_API_URL=https://o-teu-backend/api`.

## Mapeamento requisitos → implementação

| Requisito | Onde |
|---|---|
| RF001 (autenticação) | `views/auth.py`, `pages/LoginPage.jsx`, `RegistoPage.jsx` |
| RF002/RF003 (carteira) | `views/carteira.py`, `pages/CarteiraPage.jsx` |
| RF004-RF007 (simulação) | `services/motor_financeiro.py`, `views/simulacao.py`, `pages/SimulacaoPage.jsx` |
| RF008/RF009 (dados históricos) | `models.ResumoMercado` (leitura ao vivo), `sincronizar_ativos.py`, `pages/admin/AtivosPage.jsx` |
| RF010/RF011 (gráficos/relatórios) | `components/dashboard/GraficoEvolucao.jsx`, `components/simulacao/GraficoComparativo.jsx`, `services/relatorios.py` |
| RF012 (exportação em PDF) | `services/relatorios.py`, `views/simulacao.py:RelatorioSimulacaoView`, `views/admin.py:RelatorioLogsView` |
| RF013-RF015 (administração) | `views/admin.py`, `pages/admin/*` |
| RN003 (carteira única) | `models.Carteira.usuario` (`OneToOneField`) |
| RN006/RN007 (rentabilidade nominal/real) | `MotorFinanceiro.calcular_rentabilidade_nominal/real` |
| RN008 (bloqueio por inflação em falta) | `MotorFinanceiro.calcular_inflacao_acumulada` |
| RN019 (bloqueio após 5 tentativas) | `models.User.registar_tentativa_falhada`, `views/auth.py:LoginView` |
| RNF001 (Argon2id, RBAC) | `config/settings.py:PASSWORD_HASHERS`, `permissions.py` |

## Exportação de relatórios em PDF (RF011/RF012)

Implementado dos dois lados, conforme os diagramas de caso de uso:

- **Investidor** (CSU-004: "o histórico de simulação (...) podendo ser exportado pelo investidor") —
  botão "Exportar PDF" no resultado de uma simulação e em cada linha do
  histórico de simulações. `GET /api/simulacoes/<id>/relatorio/`.
- **Administrador** (CSU-009: "Consulta os registos apresentados, podendo
  emitir os relatórios administrativos") — botão "Emitir relatório
  administrativo" na página de Logs, usando os mesmos filtros da consulta.
  `GET /api/admin/logs/relatorio/`.

Gerado com `reportlab` em `bodiva_app/services/relatorios.py`.

## Simulação restrita a ativos da carteira (CSU-004)

O sistema só permite simular com um ativo que já esteja na carteira do
investidor — "Apresenta ao investidor os activos disponíveis **na carteira**
para simulação" (CSU-004). Validado no backend (`SimularView`) e reflectido
no frontend (`FormSimulacao` lista só os ativos da carteira, não o catálogo
completo do mercado).
