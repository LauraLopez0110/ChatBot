#!/usr/bin/env python3
# view_prompts.py

import sqlite3
import argparse
import os
import textwrap

DB_PATH = "prompts.db"

def fetch_records(tema=None):
    """
    Recupera todos los registros de prompts_responses.
    Si se pasa 'tema', filtra por ese tema.
    """
    if not os.path.exists(DB_PATH):
        print(f"❌ No se encontró la base de datos en '{DB_PATH}'.")
        return []

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if tema:
        cursor.execute(
            "SELECT id, tema, pregunta, respuesta FROM prompts_responses WHERE tema = ? ORDER BY id",
            (tema,)
        )
    else:
        cursor.execute(
            "SELECT id, tema, pregunta, respuesta FROM prompts_responses ORDER BY id"
        )

    rows = cursor.fetchall()
    conn.close()
    return rows

def main():
    parser = argparse.ArgumentParser(
        description="Muestra el contenido de la tabla prompts_responses."
    )
    parser.add_argument(
        "--tema",
        help="Filtrar por nombre de tema (opcional).",
        required=False
    )
    args = parser.parse_args()

    registros = fetch_records(args.tema)
    if not registros:
        print("⚠️ No se encontraron registros.")
        return

    for idx, (pk, tema, pregunta, respuesta) in enumerate(registros, start=1):
        print(f"\nRegistro #{idx}")
        print(f"  ID       : {pk}")
        print(f"  Tema     : {tema}")
        print("  Pregunta :")
        print(textwrap.indent(textwrap.fill(pregunta, width=80), "    "))
        print("  Respuesta:")
        print(textwrap.indent(textwrap.fill(respuesta, width=80), "    "))
        print("-" * 80)

if __name__ == "__main__":
    main()
