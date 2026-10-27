describe("Telemetria", () => {
  const apiUrl = Cypress.expose("apiUrl") as string;
  const frontendOrigin = Cypress.config("baseUrl");

  it("carrega a tela e consulta a sessão ativa com CORS liberado", () => {
    cy.intercept("GET", `${apiUrl}/api/sessions/active`).as("activeSession");
    cy.visit("/");

    cy.wait("@activeSession").then(({ response }) => {
      expect(response?.statusCode).to.equal(200);
      expect(response?.headers["access-control-allow-origin"]).to.equal(frontendOrigin);
    });

    cy.contains("h1", "Telemetria").should("be.visible");
    cy.contains("h2", "Configurar execução").should("be.visible");
    cy.contains("h2", "Execução atual").should("be.visible");
    cy.get("button")
      .filter(":visible")
      .should(($buttons) => {
        const labels = [...$buttons].map((button) => button.textContent?.trim());
        expect(labels.some((label) => /^(Iniciar|ESP desconectada|Execução iniciada)$/.test(label ?? ""))).to.equal(true);
      });
  });

  it("passa pelo preflight do POST sem alterar uma execução", () => {
    cy.visit("/");

    // O id negativo não pode corresponder a uma sessão válida; a rota responde
    // 404 após o preflight, sem atualizar nenhum registro.
    cy.window().then((window) =>
      window
        .fetch(`${apiUrl}/api/sessions/-987654321/finish`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status: "interrompido" }),
        })
        .then(async (response) => {
          expect(response.status).to.equal(404);
          const body = await response.json();
          expect(body.detail).to.equal("Execução ativa não encontrada.");
        }),
    );
  });
});
