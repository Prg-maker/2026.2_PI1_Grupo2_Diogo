-- Índices para acelerar o histórico de execuções (RF04).
-- Aplica em bancos existentes sem recriar o schema:
--   docker compose exec -T backend sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
--     < db/migrations/04-index-execution-history.sql
--
-- se criado do 0, o 01-schema.sql pode incorporar os índices

BEGIN;

-- Acelera a listagem filtrada por labirinto, mais recentes primeiro.
CREATE INDEX IF NOT EXISTS ix_execucao_labirinto_iniciada_em
    ON execucao (labirinto_id, iniciada_em DESC);

-- Acelera a listagem geral, mais recentes primeiro.
CREATE INDEX IF NOT EXISTS ix_execucao_iniciada_em
    ON execucao (iniciada_em DESC);

COMMIT;