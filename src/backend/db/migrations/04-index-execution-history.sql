-- Índices para acelerar o histórico de execuções.
BEGIN;

-- Acelera a listagem filtrada por labirinto, mais recentes primeiro.
CREATE INDEX IF NOT EXISTS ix_execucao_labirinto_iniciada_em
    ON execucao (labirinto_id, iniciada_em DESC);

-- Acelera a listagem geral, mais recentes primeiro.
CREATE INDEX IF NOT EXISTS ix_execucao_iniciada_em
    ON execucao (iniciada_em DESC);

COMMIT;