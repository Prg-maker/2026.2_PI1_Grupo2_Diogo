type HistoryItem = {
  id: string;
  labirinto_id: string;
  labirinto_nome: string;
  labirinto_tipo: string;
  iniciada_em: string;
  finalizada_em: string | null;
  tempo_total_ms: number | null;
  status: string;
  resultado: string | null;
  velocidade_media_cm_s: number | null;
  quantidade_celulas_visitadas: number | null;
};

function run(id: number, resultado: "sucesso" | "falha" = "sucesso"): HistoryItem {
  return {
    id: String(id),
    labirinto_id: "1",
    labirinto_nome: "Labirinto 4x4",
    labirinto_tipo: "4x4",
    iniciada_em: "2026-10-20T10:00:00Z",
    finalizada_em: "2026-10-20T10:01:00Z",
    tempo_total_ms: 60_000,
    status: resultado === "sucesso" ? "concluido" : "interrompido",
    resultado,
    velocidade_media_cm_s: 12,
    quantidade_celulas_visitadas: 8,
  };
}

describe("Histórico de execuções", () => {
  it("mostra execuções e filtra por resultado", () => {
    cy.intercept("GET", "**/api/sessions/history*", (request) => {
      const resultado = new URL(request.url).searchParams.get("resultado");
      const item = resultado === "falha" ? run(2, "falha") : run(1);
      request.reply({
        body: { total: 1, limit: 20, offset: 0, items: [item] },
      });
    }).as("history");

    cy.visit("/historico");
    cy.wait("@history");
    cy.contains("Labirinto 4x4 (4x4)").should("be.visible");
    cy.contains("Sucesso").should("be.visible");

    cy.get('input[name="filtro"][value="falha"]').check({ force: true });
    cy.contains("Falha").should("be.visible");
    cy.contains("# 2").should("be.visible");
    cy.get("@history.all").should((interceptions) => {
      // React StrictMode makes the initial effect run twice in development.
      expect(interceptions).to.have.length(3);
      const filteredRequest = interceptions[2].request;
      expect(new URL(filteredRequest.url).searchParams.get("resultado")).to.equal("falha");
      expect(interceptions[2].response?.statusCode).to.equal(200);
    });
  });

  it("avança para a próxima página e solicita o offset correto", () => {
    cy.intercept("GET", "**/api/sessions/history*", (request) => {
      const url = new URL(request.url);
      const offset = Number(url.searchParams.get("offset"));
      const items = offset === 0
        ? Array.from({ length: 20 }, (_, index) => run(index + 1))
        : [run(21)];
      request.reply({
        body: { total: 21, limit: 20, offset, items },
      });
    }).as("history");

    cy.visit("/historico");
    cy.wait("@history");
    cy.contains("Exibindo 1–20 de 21").should("be.visible");
    cy.get("button").contains("Próxima").click();

    cy.contains("# 21").should("be.visible");
    cy.contains("Exibindo 21–21 de 21").should("be.visible");
    cy.get("@history.all").should((interceptions) => {
      // The first two requests come from the development StrictMode mount.
      expect(interceptions).to.have.length(3);
      expect(new URL(interceptions[2].request.url).searchParams.get("offset")).to.equal("20");
    });
  });
});

describe("Configuração da telemetria", () => {
  it("redimensiona o percurso conforme o labirinto escolhido", () => {
    cy.intercept("GET", "**/api/sessions/active", { statusCode: 200, body: null });
    cy.visit("/");

    cy.get("#tipo-labirinto").select("12x4");
    cy.contains("h2", "Percurso")
      .closest("section")
      .find("svg")
      .should("have.attr", "viewBox", "-2 -2 164 484");
    cy.contains("h2", "Execução atual").should("be.visible");
    cy.contains("Aguardando início").should("be.visible");
  });

  it("impede iniciar uma execução enquanto a ESP está desconectada", () => {
    cy.intercept("GET", "**/api/sessions/active", { statusCode: 200, body: null });
    cy.visit("/");

    cy.contains("button", "ESP desconectada").should("be.disabled");
    cy.get("button").eq(1).should("be.disabled");
  });
});
