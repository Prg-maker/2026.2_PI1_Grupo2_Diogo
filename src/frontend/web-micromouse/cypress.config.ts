import { defineConfig } from "cypress";

export default defineConfig({
  e2e: {
    baseUrl: process.env.CYPRESS_BASE_URL ?? "http://0.0.0.0:5173",
    specPattern: "cypress/e2e/**/*.cy.{js,jsx,ts,tsx}",
    supportFile: false,
    video: false,
    screenshotOnRunFailure: true,
  },
  expose: {
    apiUrl: process.env.CYPRESS_API_URL ?? "http://localhost:8000",
  },
});
