import socket

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, DBAPIError

from app.core.config import settings
from app.core.database import engine
from app.main import app

try:
    socket.create_connection(
        (settings.POSTGRES_HOST, settings.POSTGRES_PORT), timeout=1
    ).close()
except OSError:
    pytest.skip(
        f"banco fora do ar na porta {settings.POSTGRES_PORT}: "
        "rode docker compose up -d backend",
        allow_module_level=True,
    )

client = TestClient(app)

@pytest.fixture
def labirinto_e_execucao():
    """
    Cria um labirinto + execução isolados e apaga ao final.
    Nome único por teste para não colidir com outras execuções.
    """
    nome_lab = "integrity-test"

    with engine.begin() as conn:
        # Remove resíduo de execução anterior, se houver
        conn.execute(
            text("DELETE FROM labirinto WHERE nome = :n"), {"n": nome_lab}
        )

        lab = conn.execute(
            text(
                "INSERT INTO labirinto (nome, tipo) VALUES (:n, '4x4') RETURNING id"
            ),
            {"n": nome_lab},
        ).scalar_one()

        exe = conn.execute(
            text(
                "INSERT INTO execucao (labirinto_id, status) "
                "VALUES (:l, 'em_execucao') RETURNING id"
            ),
            {"l": lab},
        ).scalar_one()

    yield {"labirinto_id": lab, "execucao_id": exe}

    # Cleanup: apaga amostras, paredes, execução e labirinto
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM amostra_telemetria WHERE execucao_id = :e"),
            {"e": exe},
        )
        conn.execute(
            text("DELETE FROM amostra_movimento WHERE execucao_id = :e"),
            {"e": exe},
        )
        conn.execute(
            text("DELETE FROM parede_detectada WHERE execucao_id = :e"),
            {"e": exe},
        )
        conn.execute(text("DELETE FROM execucao WHERE id = :e"), {"e": exe})
        conn.execute(text("DELETE FROM labirinto WHERE id = :l"), {"l": lab})



# Operações de escrita usam transações


def test_falha_em_insert_multiplo_nao_grava_parcialmente(labirinto_e_execucao):
    """
    Insere 3 amostras; a 2ª viola a constraint de bateria (>100).
    Como tudo está numa transação, nenhuma das 3 deve persistir.
    """
    exe = labirinto_e_execucao["execucao_id"]

    amostras = [
        {"exe": exe, "tempo": 0,   "bat": 50.0},   # válida
        {"exe": exe, "tempo": 100, "bat": 150.0},  # inválida (>100)
        {"exe": exe, "tempo": 200, "bat": 40.0},   # válida
    ]

    with pytest.raises(IntegrityError):
        with engine.begin() as conn:
            for a in amostras:
                conn.execute(
                    text(
                        "INSERT INTO amostra_telemetria "
                        "(execucao_id, tempo_relativo_ms, nivel_bateria_pct, "
                        "consumo_eletrico_ma, velocidade_instantanea_cm_s, "
                        "rpm_motor_esq, rpm_motor_dir) "
                        "VALUES (:exe, :tempo, :bat, 0, 0, 0, 0)"
                    ),
                    a,
                )

    with engine.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM amostra_telemetria WHERE execucao_id = :e"),
            {"e": exe},
        ).scalar_one()

    assert count == 0, (
        "Amostras foram gravadas parcialmente: transação não foi desfeita"
    )


def test_falha_no_segundo_insert_desfaz_o_primeiro(labirinto_e_execucao):
    """
    Insere telemetria OK, depois movimento com pos_x NULL (viola NOT NULL).
    Nada deve persistir.
    """
    exe = labirinto_e_execucao["execucao_id"]

    with pytest.raises(IntegrityError):
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO amostra_telemetria "
                    "(execucao_id, tempo_relativo_ms, nivel_bateria_pct, "
                    "consumo_eletrico_ma, velocidade_instantanea_cm_s, "
                    "rpm_motor_esq, rpm_motor_dir) "
                    "VALUES (:e, 0, 50.0, 0, 0, 0, 0)"
                ),
                {"e": exe},
            )
            conn.execute(
                text(
                    "INSERT INTO amostra_movimento "
                    "(execucao_id, tempo_relativo_ms, giro_x_deg_s, "
                    "giro_y_deg_s, giro_z_deg_s, pos_x, pos_y) "
                    "VALUES (:e, 0, 0, 0, 0, NULL, 0)"
                ),
                {"e": exe},
            )

    with engine.connect() as conn:
        t_count = conn.execute(
            text("SELECT COUNT(*) FROM amostra_telemetria WHERE execucao_id = :e"),
            {"e": exe},
        ).scalar_one()
        m_count = conn.execute(
            text("SELECT COUNT(*) FROM amostra_movimento WHERE execucao_id = :e"),
            {"e": exe},
        ).scalar_one()

    assert t_count == 0, "Telemetria persistiu apesar de o movimento falhar"
    assert m_count == 0


def test_rollback_nao_deixa_labirinto_orfao():
    """
    Insere labirinto OK, depois execução com labirinto_id inexistente.
    O labirinto não deve persistir (rollback atômico).
    """
    nome_lab = "orfao-test"

    with pytest.raises(IntegrityError):
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO labirinto (nome, tipo) VALUES (:n, '4x4')"
                ),
                {"n": nome_lab},
            )
            conn.execute(
                text(
                    "INSERT INTO execucao (labirinto_id, status) "
                    "VALUES (999999999, 'em_execucao')"
                )
            )

    with engine.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM labirinto WHERE nome = :n"),
            {"n": nome_lab},
        ).scalar_one()

    assert count == 0, "Labirinto órfão persistiu após falha"



# Sem alteração indevida dos dados


@pytest.mark.parametrize(
    "status_invalido", ["lixo", "finished", "RUNNING", "", "em execucao"]
)
def test_status_invalido_e_rejeitado(labirinto_e_execucao, status_invalido):
    lab = labirinto_e_execucao["labirinto_id"]
    with pytest.raises(IntegrityError):
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO execucao (labirinto_id, status) "
                    "VALUES (:l, :st)"
                ),
                {"l": lab, "st": status_invalido},
            )


@pytest.mark.parametrize("lado_invalido", ["north", "Norte", "", "up"])
def test_lado_de_parede_invalido_e_rejeitado(labirinto_e_execucao, lado_invalido):
    exe = labirinto_e_execucao["execucao_id"]
    with pytest.raises(IntegrityError):
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO parede_detectada "
                    "(execucao_id, celula_x, celula_y, lado) "
                    "VALUES (:e, 0, 0, :lado)"
                ),
                {"e": exe, "lado": lado_invalido},
            )


def test_bateria_fora_do_intervalo_e_rejeitada(labirinto_e_execucao):
    exe = labirinto_e_execucao["execucao_id"]
    for bat in (-1.0, 101.0):
        with pytest.raises(IntegrityError):
            with engine.begin() as conn:
                conn.execute(
                    text(
                        "INSERT INTO amostra_telemetria "
                        "(execucao_id, tempo_relativo_ms, nivel_bateria_pct, "
                        "consumo_eletrico_ma, velocidade_instantanea_cm_s, "
                        "rpm_motor_esq, rpm_motor_dir) "
                        "VALUES (:e, 0, :bat, 0, 0, 0, 0)"
                    ),
                    {"e": exe, "bat": bat},
                )


def test_parede_duplicada_e_rejeitada(labirinto_e_execucao):
    exe = labirinto_e_execucao["execucao_id"]
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO parede_detectada "
                "(execucao_id, celula_x, celula_y, lado) "
                "VALUES (:e, 0, 0, 'norte')"
            ),
            {"e": exe},
        )

    with pytest.raises(IntegrityError):
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO parede_detectada "
                    "(execucao_id, celula_x, celula_y, lado) "
                    "VALUES (:e, 0, 0, 'norte')"
                ),
                {"e": exe},
            )

    with engine.connect() as conn:
        count = conn.execute(
            text(
                "SELECT COUNT(*) FROM parede_detectada "
                "WHERE execucao_id = :e AND celula_x = 0 AND celula_y = 0 "
                "AND lado = 'norte'"
            ),
            {"e": exe},
        ).scalar_one()
    assert count == 1


def test_nao_apaga_labirinto_com_execucao(labirinto_e_execucao):
    """
    FK sem ON DELETE CASCADE (NO ACTION) deve impedir apagar labirinto
    que tem execuções. Garante RNF-SW05: histórico protegido.
    """
    lab = labirinto_e_execucao["labirinto_id"]
    with pytest.raises(IntegrityError):
        with engine.begin() as conn:
            conn.execute(
                text("DELETE FROM labirinto WHERE id = :l"), {"l": lab}
            )

    with engine.connect() as conn:
        count = conn.execute(
            text("SELECT COUNT(*) FROM labirinto WHERE id = :l"), {"l": lab}
        ).scalar_one()
    assert count == 1


def test_nao_apaga_execucao_com_amostras(labirinto_e_execucao):
    exe = labirinto_e_execucao["execucao_id"]
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO amostra_telemetria "
                "(execucao_id, tempo_relativo_ms, nivel_bateria_pct, "
                "consumo_eletrico_ma, velocidade_instantanea_cm_s, "
                "rpm_motor_esq, rpm_motor_dir) "
                "VALUES (:e, 0, 50.0, 0, 0, 0, 0)"
            ),
            {"e": exe},
        )

    with pytest.raises(IntegrityError):
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM execucao WHERE id = :e"), {"e": exe})


def test_nome_de_labirinto_duplicado_e_rejeitado(labirinto_e_execucao):
    with pytest.raises(IntegrityError):
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO labirinto (nome, tipo) VALUES ('integrity-test', '4x4')"
                )
            )



# Cenários de falha durante gravação (via rota)


def test_finish_em_execucao_ja_finalizada_nao_altera_dados(labirinto_e_execucao):
    """
    A rota /finish só atualiza execuções em 'em_execucao'.
    Chamar de novo numa já finalizada retorna 404 e NÃO altera.
    """
    exe = labirinto_e_execucao["execucao_id"]

    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE execucao SET status = 'concluido', "
                "resultado = 'sucesso', tempo_total_ms = 1000 "
                "WHERE id = :e"
            ),
            {"e": exe},
        )

    r = client.post(
        f"/api/sessions/{exe}/finish",
        json={"status": "interrompido", "resultado": "falha"},
    )
    assert r.status_code == 404, r.json()

    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT status, resultado, tempo_total_ms "
                "FROM execucao WHERE id = :e"
            ),
            {"e": exe},
        ).one()

    assert row[0] == "concluido"
    assert row[1] == "sucesso"
    assert row[2] == 1000


def test_start_nao_cria_duas_execucoes_ativas():
    """
    A rota /sessions usa advisory lock + checa status 'em_execucao'.
    A segunda chamada deve retornar 409.
    """

    with engine.begin() as conn:
        conn.execute(
            text(
                "UPDATE execucao SET status = 'interrompido' "
                "WHERE status = 'em_execucao'"
            )
        )

    r1 = client.post("/api/sessions", json={"tipo": "4x4"})
    assert r1.status_code == 201, r1.json()

    try:
        r2 = client.post("/api/sessions", json={"tipo": "4x4"})
        assert r2.status_code == 409, r2.json()
    finally:
        # Limpa a execução e o labirinto criados pelo teste
        with engine.begin() as conn:
            exe_id = int(r1.json()["id"])
            lab_id = conn.execute(
                text("SELECT labirinto_id FROM execucao WHERE id = :e"),
                {"e": exe_id},
            ).scalar_one()
            conn.execute(
                text("DELETE FROM execucao WHERE id = :e"), {"e": exe_id}
            )
            # Só apaga o labirinto se não tiver outras execuções
            outras = conn.execute(
                text("SELECT COUNT(*) FROM execucao WHERE labirinto_id = :l"),
                {"l": lab_id},
            ).scalar_one()
            if outras == 0:
                conn.execute(
                    text("DELETE FROM labirinto WHERE id = :l"), {"l": lab_id}
                )