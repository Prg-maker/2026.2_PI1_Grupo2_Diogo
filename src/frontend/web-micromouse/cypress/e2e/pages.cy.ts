describe("Página do labirinto", () => {
  it("mostra o labirinto padrão e os dados vazios sem execução ativa", () => {
    cy.intercept("GET", "**/api/sessions/active", { statusCode: 200, body: null });
    cy.visit("/labirinto");

    cy.contains("h2", "Labirinto Atual").should("be.visible");
    cy.contains("h1", "Labirinto").parent().should("contain.text", "4x4");
    cy.contains("h2", "Labirinto Atual")
      .closest("section")
      .find("svg")
      .should("have.attr", "viewBox", "-2 -2 164 164");
    cy.contains("span", "tipo").parent().should("contain.text", "4x4");
    cy.contains("span", "Células visitadas").parent().should("contain.text", "-");
    cy.contains("h2", "Detalhes da Execução").should("be.visible");
    cy.contains("h2", "Métricas da Corrida").should("be.visible");
  });

  it("carrega posição e métricas da execução ativa", () => {
    cy.intercept("GET", "**/api/sessions/active", {
      statusCode: 200,
      body: { id: "7", status: "em_execucao", algorithm: "Flood Fill", tempo_total_ms: 90_000 },
    });
    cy.intercept("GET", "**/api/sessions/7/maze", {
      statusCode: 200,
      body: { size: 4, grid: [], start: { row: 0, col: 0 }, goal: { row: 3, col: 3 } },
    });
    cy.intercept("GET", "**/api/sessions/7/path", {
      statusCode: 200,
      body: [{ row: 0, col: 0 }, { row: 0, col: 1 }, { row: 1, col: 1 }],
    });
    cy.intercept("GET", "**/api/sessions/7/metrics", {
      statusCode: 200,
      body: { speed_cm_s: 12.5, rpm: 320, battery_pct: 75 },
    });
    cy.visit("/labirinto");

    cy.contains("span", "Células visitadas").parent().should("contain.text", "3");
    cy.contains("span", "Posição").parent().should("contain.text", "(1, 1)");
    cy.contains("Velocidade").parent().should("contain.text", "12.5");
    cy.contains("RPM").parent().should("contain.text", "320");
    cy.contains("Bateria").parent().should("contain.text", "75");
    cy.contains("h2", "Labirinto Atual")
      .closest("section")
      .find("polyline")
      .should("have.attr", "points", "20,20 60,20 60,60");
  });
});

describe("Relatórios", () => {
  it("atualiza os dados ao selecionar outra execução", () => {
    cy.visit("/relatorio");

    cy.contains("button", "#0013").click();
    cy.contains("Execução #0013").should("be.visible");
    cy.contains("Não concluída").should("be.visible");
    cy.contains("41").should("be.visible");
    cy.contains("button", "#0013").should("have.attr", "aria-pressed", "true");
  });

  it("gera um PDF e apresenta a opção de exportação", () => {
    cy.visit("/relatorio");

    cy.contains("button", "Gerar Relatório PDF").click();
    cy.contains("Relatório gerado com sucesso!", { timeout: 10_000 }).should("be.visible");
    cy.get('a[download="micronav-relatorio-0047.pdf"]')
      .should("be.visible")
      .and("have.attr", "href")
      .and("match", /^blob:/);
    cy.contains("button", "Novo relatório").should("be.visible");
  });
});

describe("Navegação e execução", () => {
  it("navega pela barra lateral até o histórico", () => {
    cy.intercept("GET", "**/api/sessions/history*", {
      statusCode: 200,
      body: { total: 0, limit: 20, offset: 0, items: [] },
    });
    cy.visit("/");

    cy.contains("a", "Histórico").click();
    cy.location("pathname").should("equal", "/historico");
    cy.contains("h1", "Histórico").should("be.visible");
    cy.contains("Nenhuma execução encontrada.").should("be.visible");
  });

  it("inicia e finaliza uma execução com a ESP conectada", () => {
    cy.intercept("GET", "**/api/sessions/active", { statusCode: 200, body: null });
    cy.intercept("POST", "**/api/sessions", (request) => {
      expect(request.body).to.deep.equal({ tipo: "4x4" });
      request.reply({
        statusCode: 201,
        body: { id: "87", iniciada_em: new Date().toISOString(), status: "em_execucao", algorithm: "Flood Fill" },
      });
    }).as("startExecution");
    cy.intercept("POST", "**/api/sessions/87/finish", {
      statusCode: 200,
      body: { id: "87", status: "concluido", resultado: "sucesso" },
    }).as("finishExecution");

    cy.visit("/", {
      onBeforeLoad(window) {
        class MockWebSocket {
          onmessage: ((event: { data: string }) => void) | null = null;
          onclose: (() => void) | null = null;
          onerror: (() => void) | null = null;

          constructor() {
            window.setTimeout(() => {
              this.onmessage?.({ data: JSON.stringify({ connected: true }) });
            }, 10);
          }

          close() {}
        }

        Object.defineProperty(window, "WebSocket", {
          configurable: true,
          value: MockWebSocket,
        });
      },
    });

    cy.contains("button", "Iniciar", { timeout: 5_000 }).should("be.enabled").click();
    cy.wait("@startExecution");
    cy.contains("Em execução").should("be.visible");
    cy.contains("button", "Execução iniciada").should("be.disabled");

    cy.contains("h2", "Configurar execução")
      .closest("section")
      .find("button")
      .eq(1)
      .should("be.enabled")
      .click();
    cy.wait("@finishExecution");
    cy.contains("Aguardando início").should("be.visible");
    cy.get("#tipo-labirinto").should("not.be.disabled");
  });
});
