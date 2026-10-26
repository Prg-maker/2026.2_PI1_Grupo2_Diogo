# Documento de Sprints: Frontend

**Projeto:** 2026.2_PI1_Grupo2_Diogo
**Repositório:** https://github.com/fcte-pi1/2026.2_PI1_Grupo2_Diogo
**Sprints cobertas:** 1, 2 e 3 (a sprint 3 está em andamento)

> Os períodos foram estimados a partir das datas dos commits e PRs, por isso são aproximados. Os campos marcados com `[preencher]` não aparecem no histórico do repositório e precisam ser completados pela equipe.

## Visão geral

| Sprint | Entregas do frontend | Período | Status |
|---|---|---|---|
| 1 | Setup, painel, dashboard, labirinto, telemetria e navegação | 23/09 a 29/09 (aprox.) | Concluída |
| 2 | Controle do percurso, ícones, componentização e header | 30/09 a 03/10 (aprox.) | Concluída |
| 3 | Tela de histórico | a partir de 04/10 | Em andamento |

## Equipe (frontend)

| Username | Nome | Atuação principal observada |
|---|---|---|
| Prg-maker | Daniel | Setup do frontend, sidebar, controle do percurso, tela de histórico; integração de PRs |
| CauaHenriqueM | Caua | Base do painel, página do labirinto, dashboard web |
| Karmantinedev | Pedro | Base do painel |
| Jvezyk | Joao | Telemetria |
| Gabriel-Ma7os | Gabriel | Trabalhou em conjunto com o Joao (Jvezyk) |
| yanrdgs-dev | Yan | Merge do PR da NavBar |

---

## Sprint 1

**Período:** 23/09/2026 a 29/09/2026 (aprox.)

### Entregue
- **Setup do frontend** (PR #60): estrutura inicial do projeto.
- **Base do painel frontend**, seguindo o visual do Figma, com remoção de PNGs e logs de console.
- **Dashboard web** (PR #77, branch `feature/dev-dashboard-web`).
- **Página do labirinto**: tela movida para `pages/LabirintoPage`, com resolução de conflitos com a main.
- **Exibição de telemetria (RF01)**, com página própria para telemetria.
- **Sidebar e navegação** finalizadas (PR #79, branch `NavBar`).

### Dificuldades e decisões
- Conflitos de merge com a main durante a organização das páginas.
- Ajuste da interface para manter o visual do Figma.
- Fluxo de trabalho adotado: feature branches, Pull Requests e merge na main, com sincronizações periódicas com o repositório da turma (`fcte-pi1:main`).
- `[preencher outras dificuldades]`

### Pendências para a próxima sprint
- `[preencher]`

---

## Sprint 2

**Período:** 30/09/2026 a 03/10/2026 (aprox.)

### Entregue (PR #84, branch `bugfix`)
- Botões para **iniciar** e **reiniciar o percurso**, com correção para desabilitar o botão no estado correto.
- Inclusão de **ícones** na interface.
- **Componentização:** os cards foram movidos para `components`.
- Ajuste do **header**.

### Dificuldades e decisões
- Reorganização do código em componentes reutilizáveis.
- `[preencher outras dificuldades]`

### Pendências para a próxima sprint
- Criar a tela de histórico, para consumir os dados das execuções.
- `[preencher]`

---

## Sprint 3 (em andamento)

**Período:** a partir de 04/10/2026

### Entregue até agora
- **Tela de histórico**, que deve consumir os dados das execuções modeladas na sprint 2.

### Dificuldades e decisões
- `[preencher]`

### Em andamento e próximos passos
- `[preencher]`

---

## Resumo da evolução

1. **Sprint 1:** estrutura e telas (painel, dashboard, labirinto, telemetria e navegação).
2. **Sprint 2:** interação com o percurso e organização do código em componentes.
3. **Sprint 3:** tela de histórico, a primeira a depender dos dados do backend.
