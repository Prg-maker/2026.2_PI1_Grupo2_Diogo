import socket

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.main import app

try:
    socket.create_connection(
        (settings.POSTGRES_HOST, settings.POSTGRES_PORT), timeout=1
    ).close()
except OSError:
    pytest.skip(
        f"banco fora do ar na porta {settings.POSTGRES_PORT}: rode docker compose up -d backend",
        allow_module_level=True,
    )

client = TestClient(app)


@pytest.fixture
def execucoes_de_teste():
    """
    Cria duas execuções de teste em labirintos diferentes e apaga ao final.
    Isola o teste do seed_db.py (não depende de rodar o seed antes).
    """
    with engine.begin() as conn:
        lab_a = conn.execute(
            text(
                "INSERT INTO labirinto (nome, tipo) VALUES (:nome, :tipo) "
                "ON CONFLICT (nome) DO UPDATE SET tipo = EXCLUDED.tipo RETURNING id"
            ),
            {"nome": "hist-test-4x4", "tipo": "4x4"},
        ).scalar_one()
        lab_b = conn.execute(
            text(
                "INSERT INTO labirinto (nome, tipo) VALUES (:nome, :tipo) "
                "ON CONFLICT (nome) DO UPDATE SET tipo = EXCLUDED.tipo RETURNING id"
            ),
            {"nome": "hist-test-8x4", "tipo": "8x4"},
        ).scalar_one()

        def criar_exec(labirinto_id, status, resultado, segundos):
            return conn.execute(
                text(
                    "INSERT INTO execucao (labirinto_id, iniciada_em, finalizada_em, "
                    "tempo_total_ms, status, resultado, velocidade_media_cm_s, "
                    "quantidade_celulas_visitadas) "
                    "VALUES (:lab, LOCALTIMESTAMP - make_interval(secs => :s), "
                    "LOCALTIMESTAMP, :ms, :st, :res, 12.5, 7) RETURNING id"
                ),
                {
                    "lab": labirinto_id,
                    "s": segundos,
                    "ms": segundos * 1000,
                    "st": status,
                    "res": resultado,
                },
            ).scalar_one()

        exec_a = criar_exec(lab_a, "concluido", "sucesso", 40)
        exec_b = criar_exec(lab_b, "interrompido", "falha", 20)

    yield {"lab_a": lab_a, "lab_b": lab_b, "exec_a": exec_a, "exec_b": exec_b}

    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM execucao WHERE id IN (:a, :b)"),
            {"a": exec_a, "b": exec_b},
        )
        conn.execute(
            text("DELETE FROM labirinto WHERE id IN (:a, :b)"),
            {"a": lab_a, "b": lab_b},
        )


def test_history_returns_paginated(execucoes_de_teste):
    r = client.get("/api/sessions/history")
    assert r.status_code == 200, r.json()
    body = r.json()
    assert {"total", "limit", "offset", "items"} <= set(body.keys())
    assert body["limit"] == 20
    assert body["offset"] == 0
    # deve conter pelo menos as 2 criadas no fixture
    ids = {item["id"] for item in body["items"]}
    assert str(execucoes_de_teste["exec_a"]) in ids
    assert str(execucoes_de_teste["exec_b"]) in ids


def test_history_orders_by_iniciada_em_desc(execucoes_de_teste):
    r = client.get("/api/sessions/history")
    items = r.json()["items"]
    inicios = [item["iniciada_em"] for item in items]
    assert inicios == sorted(inicios, reverse=True)


def test_history_filters_by_labirinto(execucoes_de_teste):
    lab = execucoes_de_teste["lab_a"]
    r = client.get(f"/api/sessions/history?labirinto_id={lab}")
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == str(execucoes_de_teste["exec_a"])
    assert body["items"][0]["labirinto_id"] == str(lab)


def test_history_filters_by_status(execucoes_de_teste):
    r = client.get("/api/sessions/history?status=interrompido")
    body = r.json()
    ids = {item["id"] for item in body["items"]}
    assert str(execucoes_de_teste["exec_b"]) in ids
    assert str(execucoes_de_teste["exec_a"]) not in ids


def test_history_filters_by_resultado(execucoes_de_teste):
    r = client.get("/api/sessions/history?resultado=sucesso")
    body = r.json()
    ids = {item["id"] for item in body["items"]}
    assert str(execucoes_de_teste["exec_a"]) in ids
    assert str(execucoes_de_teste["exec_b"]) not in ids


def test_history_invalid_status_returns_422():
    r = client.get("/api/sessions/history?status=lixo")
    assert r.status_code == 422


def test_history_pagination(execucoes_de_teste):
    r1 = client.get("/api/sessions/history?limit=1&offset=0")
    r2 = client.get("/api/sessions/history?limit=1&offset=1")
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json()["total"] == r2.json()["total"]
    id1 = r1.json()["items"][0]["id"]
    id2 = r2.json()["items"][0]["id"]
    assert id1 != id2


def test_history_empty_when_filter_matches_nothing():
    r = client.get("/api/sessions/history?labirinto_id=999999999")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 0
    assert body["items"] == []