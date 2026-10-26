#!/usr/bin/env python3
"""Envia telemetria fictícia para a API, para demonstrar o front-end."""

import argparse
import json
import math
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def request_json(base_url: str, path: str, payload: dict | None = None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        f"{base_url.rstrip('/')}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    with urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="URL base da API")
    parser.add_argument("--tipo", choices=("4x4", "8x4", "12x4"), default="4x4")
    parser.add_argument("--quantidade", type=int, default=40, help="Número de amostras")
    parser.add_argument("--intervalo", type=float, default=0.5, help="Segundos entre amostras")
    args = parser.parse_args()
    if args.quantidade < 1 or args.intervalo < 0:
        parser.error("quantidade deve ser positiva e intervalo não pode ser negativo")

    try:
        active = request_json(args.url, "/api/sessions/active")
        if active is None:
            active = request_json(args.url, "/api/sessions", {"tipo": args.tipo})
            print(f"Execução de demonstração criada: {active['id']}")
        else:
            print(f"Usando execução ativa existente: {active['id']}")

        # Caminho em zigue-zague para visualizar movimento no labirinto.
        route = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (1, 2),
                 (1, 1), (1, 0), (2, 0), (2, 1), (2, 2), (2, 3),
                 (3, 3), (3, 2), (3, 1), (3, 0)]
        for index in range(args.quantidade):
            row, col = route[index % len(route)]
            payload = {
                "position": {"row": row, "col": col},
                "metrics": {
                    "speed_cm_s": round(8 + 3 * math.sin(index / 3), 2),
                    "rpm": round(260 + 35 * math.sin(index / 4)),
                    "battery_pct": round(max(0, 96 - index * 0.08), 1),
                },
                "events": [],
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
            result = request_json(args.url, "/api/telemetry", payload)
            print(f"[{index + 1}/{args.quantidade}] {result}")
            if index + 1 < args.quantidade:
                time.sleep(args.intervalo)
        print("Concluído. Consulte /api/telemetry/current no front-end.")
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise SystemExit(f"A API respondeu HTTP {error.code}: {detail}")
    except URLError as error:
        raise SystemExit(f"Não foi possível acessar a API: {error.reason}")


if __name__ == "__main__":
    main()
