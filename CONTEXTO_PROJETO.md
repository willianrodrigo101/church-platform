# CONTEXTO DO PROJETO — CHURCH PLATFORM

> **PARA A IA:** Leia tudo. Este documento contém o contexto e o método de
> trabalho. Siga o mesmo estilo descrito aqui.

---

## 🎯 O QUE É O PROJETO

**Church Platform** — Plataforma SaaS pastoral multi-igreja.

**Ideia central:** Responder "Quem precisa de atenção hoje?"

**Visão:** Um pastor abre o sistema e em 30 segundos sabe quem precisa de
cuidado — com histórico completo, sigilo pastoral e multi-igreja.

**Diferencial:** Não é um CRUD de igreja. É uma plataforma de cuidado
pastoral com 11 módulos integrados.

---

## 🎯 MÉTODO DE TRABALHO (OBRIGATÓRIO)

O usuário construiu a plataforma com um método específico. **Siga sempre:**

1. **Guiar pelo PowerShell** — comandos prontos para copiar e colar
2. **Código COMPLETO** — nunca "mude a linha X". Arquivo inteiro pronto
3. **Blocos pequenos** — um passo por vez, esperar confirmação antes de seguir
4. **Com validação** — "Esperado: ..." em cada passo
5. **Com diagnóstico** — se der erro, ler, achar causa, mandar correção completa
6. **Próximos passos claros** — "📋 Me manda:" no final de cada script
7. **Nunca desistir** — se travar, volta, ajusta e segue
8. **Comemorar conquistas** — registrar progresso a cada módulo fechado
9. **Sem excesso de emoji** — só nos títulos e pontos de atenção
10. **Português brasileiro coloquial** — sem formalidade

### Formato de resposta

\`\`\`
### 🎯 PASSO N — O que fazer

\`\`\`powershell
comando aqui
\`\`\`

**Esperado:**
\`\`\`
saída esperada
\`\`\`
\`\`\`

Final:
\`\`\`
### 📋 Me manda

1. Saída do comando X
2. Apareceu Y?
3. Deu erro? Qual?
\`\`\`

### Estrutura de cada bloco novo

1. **Script 1 — Backend** (setup_xxx.py): models, schemas, repository, service, router + alembic + testar Swagger
2. **Script 2 — Frontend** (setup_frontend_xxx.py): CSS, HTML, JS no index.html
3. **Testes finais**: criar dados, testar ações, confirmar visualmente

---## 💻 AMBIENTE TÉCNICO

### Duas máquinas

| Máquina | Caminho | Status |
|---|---|---|
| **Usuario** (antiga) | `C:\Users\Usuario\Documents\robo\CHURCH_PLATFORM` | Funcionava (28 tabelas) |
| **PC** (atual) | `C:\Users\PC\Documents\CHURCH_PLATFORM` | Replicado, funcionando |

**Atualmente: máquina PC.**

### Stack

- **Backend:** Python 3.12 + FastAPI + SQLAlchemy async
- **Banco:** PostgreSQL 18 (`church_platform`)
- **Migrations:** Alembic (14 aplicadas)
- **Auth:** JWT
- **Frontend:** HTML/CSS/JS puro em arquivo único (~290 KB)
- **venv:** `.venv` na pasta backend

### Como subir o sistema

**Backend (janela 1):**
\`\`\`powershell
cd C:\Users\PC\Documents\CHURCH_PLATFORM\backend
& ".\.venv\Scripts\Activate.ps1"
uvicorn app.main:app --reload
\`\`\`

**Frontend (janela 2):**
\`\`\`powershell
cd C:\Users\PC\Documents\CHURCH_PLATFORM\backend
& ".\.venv\Scripts\Activate.ps1"
python ..\servir_frontend.py
\`\`\`

**Acessar:** `http://localhost:5500/index.html`
**Login:** `pastor@igreja.com` / `senha123`
**Swagger:** `http://127.0.0.1:8000/docs`

### Estrutura de pastas

\`\`\`
CHURCH_PLATFORM/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/           (config, db, security, exceptions)
│   │   ├── api/            (routers + dependencies)
│   │   ├── modules/
│   │   │   ├── usuarios/   (auth + roles)
│   │   │   ├── igreja/
│   │   │   ├── pessoas/
│   │   │   ├── cuidado/
│   │   │   ├── oracao/
│   │   │   ├── eventos/
│   │   │   ├── jornada/
│   │   │   ├── anexos/
│   │   │   ├── estudo/     ← módulo maior
│   │   │   ├── dashboard/
│   │   │   └── notificacoes/
│   │   └── shared/
│   ├── migrations/         (14 migrations)
│   ├── .venv/
│   └── .env
├── frontend/
│   └── web/
│       └── index.html      (arquivo único ~290 KB)
├── servir_frontend.py
├── CONTEXTO_PROJETO.md     ← este arquivo
└── README.md
\`\`\`

### Credenciais

- **PostgreSQL:** usuário `postgres`, senha `postgres`, porta `5432`
- **Banco:** `church_platform`
- **Admin:** `pastor@igreja.com` / `senha123` (role: admin, sem igreja)

### Padrão multi-tenant

- Admin global (sem igreja_id) cria em qualquer igreja — pega a primeira ativa automaticamente
- Outros usuários usam a própria igreja
- Regra aplicada em: Eventos, Jornada, Estudo, Anexos

---

## 📊 ESTADO ATUAL DA PLATAFORMA

### Módulos completos (11)

| # | Módulo | Status | Endpoints |
|---|---|---|---|
| 1 | 🔐 Autenticação | ✅ | 14 |
| 2 | 🏠 Dashboard Premium | ✅ | 1 + 3 gráficos |
| 3 | 🔔 Notificações | ✅ | 5 |
| 4 | 🏛️ Igrejas | ✅ | 7 |
| 5 | 👥 Pessoas + Aniversariantes | ✅ | 9 |
| 6 | 🕊️ Cuidado Pastoral | ✅ | 8 |
| 7 | 🙏 Oração | ✅ | 8 |
| 8 | 📅 Eventos | ✅ | 12 |
| 9 | 🎯 Jornada | ✅ | 15 |
| 10 | 📎 Anexos | ✅ | 5 |
| 11 | 📚 Estudo (Blocos 1, 2, 3) | ✅ | 54 |

### Módulo Estudo — status

\`\`\`
✅ Bloco 1 — Trilhas + Cursos + Módulos + Conteúdos
   ├── 4 tabelas: trilhas_formacao, cursos, modulos_curso, conteudos_modulo
   ├── Frontend: sub-aba 📖 Catálogo
   └── Endpoints: ~22

✅ Bloco 2 — Turmas + Matrículas + Presenças
   ├── 4 tabelas: turmas, matriculas, progresso_modulos, presencas
   ├── Frontend: sub-aba 🎓 Turmas
   └── Endpoints: ~20

✅ Bloco 3 — Quizzes + Fórum + Badges
   ├── 6 tabelas: quizzes, perguntas_quiz, tentativas_quiz,
   │              comentarios, badges, conquistas
   ├── Frontend: sub-abas 📝 Quizzes, 💬 Fórum, 🏅 Gamificação
   └── Endpoints: ~13

⏸️ Bloco 4 — Certificados + Ferramentas + IA (NÃO COMEÇADO)
\`\`\`

### Números totais

- **~113 endpoints REST**
- **28 tabelas no banco**
- **14 migrations aplicadas**
- **10 abas + 5 sub-abas no Estudo**
- **~290 KB de frontend puro**

### Abas atuais do frontend

\`\`\`
🏠 Início | 🏛️ Igrejas | 👥 Pessoas | 🕊️ Cuidado | 🙏 Oração |
📅 Eventos | 🎯 Jornada | 📚 Estudo | 👤 Usuários

📚 Estudo → sub-abas:
├── 📖 Catálogo
├── 🎓 Turmas
├── 📝 Quizzes
├── 💬 Fórum
└── 🏅 Gamificação
\`\`\`

---## 🎯 ONDE PARAMOS

**Última coisa feita:** Bloco 3 do módulo Estudo 100% concluído (backend + frontend).

**Última confirmação do usuário:** "tudo funcionando" — Quizzes, Fórum e
Gamificação funcionando.

**Próximo passo a escolher:**
- 🅰️ Bloco 4 do Estudo — Certificados + Ferramentas + IA
- 🅱️ Integração dos Anexos no Estudo
- 🅲️ Deploy na internet
- 🅳️ Pausa — consolidar

**Recomendação da IA:** 🅰️ Bloco 4 do Estudo.

---

## 📋 PRÓXIMOS PASSOS PLANEJADOS

### 🅰️ Bloco 4 do Estudo — Certificados + Ferramentas + IA

**O que faz:**
1. **Certificados em PDF** — gerados ao concluir curso, com QR code verificável
2. **Ferramentas de estudo** — interlinear grego/hebraico, léxico Strong,
   mapas bíblicos (curados — links para STEP Bible, Blue Letter Bible)
3. **Anotações pessoais** — por módulo, salvas por pessoa
4. **IA pedagógica** — recomendações personalizadas, resumos

**Tabelas novas previstas:** certificados, anotacoes, ferramentas_estudo
**Backend:** ~15 endpoints novos
**Frontend:** aba de certificados + ferramentas dentro do Estudo

**Divisão:**
- Script 1 — Backend (certificados + anotações + ferramentas)
- Script 2 — Frontend
- Testes finais

### 🅱️ Integração de Anexos no Estudo

Adicionar anexos (que já existem) em Cursos, Módulos e Conteúdos.
Tempo: ~20 min.

### 🅲️ Deploy na internet

- Docker Compose (backend + PostgreSQL)
- Hospedagem gratuita: Fly.io + Neon
- HTTPS + subdomínio
- Variáveis de ambiente de produção

---

## 📋 MÓDULOS AINDA NÃO COMEÇADOS (plano original de 18)

1. 👥 Comunidade (grupos, células)
2. 🎓 Ministérios (departamentos)
3. 🌟 Talentos (dons e habilidades)
4. 🤝 Assistência (ajuda social)
5. 🏠 Família (núcleo familiar)
6. 📚 Conteúdo (sermões, materiais)
7. 🌍 Missões (obra missionária)
8. 💰 Financeiro (dízimos, ofertas)
9. 📢 Comunicação (email, WhatsApp)
10. 🧠 Inteligência (IA pastoral)

**Prioridade sugerida:** Financeiro > Comunicação > Família > Comunidade.

---

## ⚠️ PROBLEMAS CONHECIDOS E COMO RESOLVER

### 1. "ModuleNotFoundError: No module named 'app'"

**Causa:** uvicorn rodando na pasta errada (raiz em vez de `backend`).

**Solução:**
\`\`\`powershell
cd C:\Users\PC\Documents\CHURCH_PLATFORM\backend
uvicorn app.main:app --reload
\`\`\`

### 2. "Failed to fetch" no frontend

**Causa:** uvicorn caiu.

**Solução:** subir o uvicorn de novo em outra janela.

### 3. Python 3.14 não funciona

**Causa:** pydantic-core sem binários para 3.14.

**Solução:** usar Python 3.12 (tem tudo pronto).

### 4. MissingGreenlet em respostas

**Causa:** lazy load de relacionamentos em async.

**Solução:** usar `selectinload` no repository + recarregar objeto antes de retornar.

### 5. Ambiguidade entre máquinas

**Causa:** usuário alterna entre `Usuario` e `PC`.

**Solução:** sempre confirmar `Get-Location` antes de rodar.

### 6. VS Code trunca texto colado

**Causa:** textos muito grandes são cortados.

**Solução:** colar em partes menores (dividir em 2-3 pedaços).

---

## 🎯 CONTEXTO HUMANO

- **Nome:** Willian (Pastor Willian no sistema)
- **Nível técnico:** Iniciante em programação, muito dedicado e paciente
- **Nível pastoral:** Pastor de igreja real (CASA DE ORACAO PARA TODOS OS POVOS)
- **Visão:** Criar plataforma que sirva igrejas brasileiras de verdade
- **Motivação:** Cuidar melhor das pessoas da igreja dele e ajudar outras igrejas

**Como o usuário reage:**
- Quando dá certo → "tudo ok", "deu tudo certo", "funcionando"
- Quando dá errado → cola o log completo para diagnóstico
- Prefere scripts prontos para colar no PowerShell
- Confia na IA para decidir tecnicamente

---

## 🚀 COMO INICIAR A NOVA CONVERSA

Cole este documento inteiro no início da nova conversa e diga:

> "Esse é o contexto do projeto Church Platform. Vamos continuar de onde
> paramos. Última coisa feita: Bloco 3 do módulo Estudo 100% concluído.
> Próximo passo: [🅰️ Bloco 4 / 🅱️ Anexos / 🅲️ Deploy / 🅳️ Pausa].
> Siga o método de trabalho descrito no documento."

---

## ✅ RESUMO EM UMA FRASE

**Church Platform é uma plataforma SaaS pastoral multi-igreja com 11 módulos
funcionando (~113 endpoints, 28 tabelas), construída por um pastor iniciante
em programação seguindo um método de trabalho colaborativo passo a passo com
uma IA. Atualmente no módulo Estudo (Bloco 3 fechado), pronto para o Bloco 4
(Certificados + Ferramentas + IA) ou Deploy.**

---

*Última atualização: 13 de outubro de 2026*
*Máquina atual: PC (C:\Users\PC\Documents\CHURCH_PLATFORM)*