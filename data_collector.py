"""
Recolección de datos desde la API de Semantic Scholar.
Área: Sistemas Distribuidos
"""

import requests
import json
import time
import os

BASE_URL = "https://api.semanticscholar.org/graph/v1"
DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "papers.json")

# Queries representativas: Sistemas Distribuidos
QUERIES = [
    "Raft consensus distributed",
    "Paxos distributed consensus",
    "Byzantine fault tolerance",
]

PAPERS_PER_QUERY = 50


def fetch_papers(query: str, limit: int = 100, offset: int = 0) -> dict | None:
    """Consulta la API de Semantic Scholar y retorna los resultados."""
    url = f"{BASE_URL}/paper/search"
    params = {
        "query": query,
        "fields": "paperId,title,authors,year",
        "limit": limit,
        "offset": offset,
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("  [!] Rate limit alcanzado. Esperando 30 segundos...")
            time.sleep(30)
            return fetch_papers(query, limit, offset)
        else:
            print(f"  [!] Error {response.status_code} en query '{query}'")
            return None
    except requests.RequestException as e:
        print(f"  [!] Excepción de red: {e}")
        return None


def collect_data() -> list[dict]:
    """
    Recolecta papers de Semantic Scholar para múltiples queries
    de Sistemas Distribuidos y guarda los resultados en JSON.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    all_papers: dict[str, dict] = {}

    for query in QUERIES:
        print(f"\nBuscando: '{query}'...")
        result = fetch_papers(query, limit=PAPERS_PER_QUERY)

        if result and "data" in result:
            nuevos = 0
            for paper in result["data"]:
                pid = paper.get("paperId")
                authors = paper.get("authors", [])
                year = paper.get("year")

                # Solo papers con al menos 2 autores identificados y año registrado
                valid_authors = [a for a in authors if a.get("authorId")]
                if pid and pid not in all_papers and len(valid_authors) >= 2 and year:
                    all_papers[pid] = {
                        "paperId": pid,
                        "title": paper.get("title", "Sin título"),
                        "authors": [
                            {"authorId": a["authorId"], "name": a.get("name", "Desconocido")}
                            for a in valid_authors
                        ],
                        "year": year,
                    }
                    nuevos += 1

            print(f"  -> {nuevos} papers nuevos. Total acumulado: {len(all_papers)}")
        else:
            print("  -> Sin resultados.")

        # Pausa para respetar el rate limit de la API
        time.sleep(1.5)

    papers_list = list(all_papers.values())

    # Conteo de autores únicos para verificar el mínimo de 100
    author_ids = {
        a["authorId"]
        for paper in papers_list
        for a in paper["authors"]
    }

    print(f"\n{'='*50}")
    print(f"Papers recolectados : {len(papers_list)}")
    print(f"Autores únicos      : {len(author_ids)}")
    print(f"{'='*50}")

    if len(author_ids) < 100:
        print("[AVISO] Se tienen menos de 100 autores únicos. Considera agregar más queries.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(papers_list, f, ensure_ascii=False, indent=2)

    print(f"\nDatos guardados en: {OUTPUT_FILE}")
    return papers_list


if __name__ == "__main__":
    collect_data()
