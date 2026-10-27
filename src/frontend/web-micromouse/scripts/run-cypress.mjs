import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const cypressBin = fileURLToPath(
  new URL("../node_modules/cypress/bin/cypress", import.meta.url),
);
const environment = { ...process.env };
delete environment.ELECTRON_RUN_AS_NODE;

const result = spawnSync(process.execPath, [cypressBin, ...process.argv.slice(2)], {
  stdio: "inherit",
  env: environment,
});

if (result.error) throw result.error;
process.exit(result.status ?? 1);
