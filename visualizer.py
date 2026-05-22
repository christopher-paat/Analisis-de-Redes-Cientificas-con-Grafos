"""
Visualización de la red de colaboración científica.
Área: Sistemas Distribuidos

Genera:
  1. Grafo completo coloreado por comunidad (PNG)
  2. Grafo destacando nodos importantes por betweenness (PNG)
  3. Visualización interactiva en HTML (pyvis)
"""

import os
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import community as community_louvain
from pyvis.network import Network

GRAPH_FILE  = os.path.join("data", "graph.graphml")
OUT_FULL    = os.path.join("data", "vis_completa.png")
OUT_IMPORT  = os.path.join("data", "vis_importantes.png")
OUT_HTML    = os.path.join("data", "vis_interactiva.html")


def load_graph(path: str) -> nx.Graph:
    G = nx.read_graphml(path)
    for u, v, d in G.edges(data=True):
        d["weight"] = int(d.get("weight", 1))
    return G


def get_layout(G: nx.Graph) -> dict:
    return nx.spring_layout(G, seed=42, k=0.8)


# ─────────────────────────────────────────
# 1. GRAFO COMPLETO POR COMUNIDAD
# ─────────────────────────────────────────

def vis_completa(G: nx.Graph, pos: dict) -> None:
    print("Generando visualizacion completa...")

    partition  = community_louvain.best_partition(G, weight="weight")
    comunidades = set(partition.values())
    cmap        = cm.get_cmap("tab20", len(comunidades))
    node_colors = [cmap(partition[n]) for n in G.nodes()]

    degrees    = dict(G.degree())
    node_sizes = [30 + degrees[n] * 20 for n in G.nodes()]
    edge_widths = [d["weight"] * 0.5 for _, _, d in G.edges(data=True)]

    fig, ax = plt.subplots(figsize=(18, 14))
    ax.set_facecolor("#1a1a2e")
    fig.patch.set_facecolor("#1a1a2e")

    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.3, width=edge_widths, edge_color="#aaaaaa")
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                           node_size=node_sizes, alpha=0.9)

    # Etiquetas solo para los 15 autores con mayor grado
    top15 = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:15]
    labels = {nid: G.nodes[nid].get("name", nid).split()[-1] for nid, _ in top15}
    nx.draw_networkx_labels(G, pos, labels=labels, ax=ax,
                            font_size=7, font_color="white", font_weight="bold")

    ax.set_title("Red de Colaboracion Cientifica - Sistemas Distribuidos\n"
                 f"({G.number_of_nodes()} autores | {G.number_of_edges()} colaboraciones | "
                 f"{len(comunidades)} comunidades)",
                 color="white", fontsize=14, pad=15)
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(OUT_FULL, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Guardada en: {OUT_FULL}")


# ─────────────────────────────────────────
# 2. NODOS IMPORTANTES (BETWEENNESS)
# ─────────────────────────────────────────

def vis_importantes(G: nx.Graph, pos: dict) -> None:
    print("Generando visualizacion de nodos importantes...")

    for u, v, d in G.edges(data=True):
        d["inv_weight"] = 1 / d["weight"]

    betweenness = nx.betweenness_centrality(G, weight="inv_weight")
    degree_cent = nx.degree_centrality(G)
    closeness   = nx.closeness_centrality(G)

    # Normalizar betweenness para tamaño y color
    max_bet = max(betweenness.values()) if max(betweenness.values()) > 0 else 1
    node_sizes  = [100 + (betweenness[n] / max_bet) * 1500 for n in G.nodes()]
    node_colors = [betweenness[n] / max_bet for n in G.nodes()]

    fig, ax = plt.subplots(figsize=(18, 14))
    ax.set_facecolor("#0f0f23")
    fig.patch.set_facecolor("#0f0f23")

    edge_widths = [d["weight"] * 0.4 for _, _, d in G.edges(data=True)]
    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.2, width=edge_widths, edge_color="#666688")

    nodes = nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                                   node_size=node_sizes, cmap=plt.cm.plasma,
                                   alpha=0.95, vmin=0, vmax=1)

    # Etiquetas para top 20 por betweenness
    top20 = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:20]
    labels = {nid: G.nodes[nid].get("name", nid).split()[-1] for nid, _ in top20}
    nx.draw_networkx_labels(G, pos, labels=labels, ax=ax,
                            font_size=7, font_color="white", font_weight="bold")

    plt.colorbar(nodes, ax=ax, label="Betweenness Centrality (normalizado)",
                 orientation="vertical", shrink=0.6)

    # Tabla de top 5 en esquina
    top5 = top20[:5]
    info = "\n".join([
        f"{i+1}. {G.nodes[nid].get('name','?')[:22]}\n"
        f"   BC:{betweenness[nid]:.4f} | DC:{degree_cent[nid]:.4f} | CC:{closeness[nid]:.4f}"
        for i, (nid, _) in enumerate(top5)
    ])
    ax.text(0.01, 0.01, f"Top 5 autores clave:\n{info}",
            transform=ax.transAxes, fontsize=7, color="white",
            verticalalignment="bottom",
            bbox=dict(boxstyle="round", facecolor="#222244", alpha=0.8))

    ax.set_title("Autores mas influyentes - Betweenness Centrality\n"
                 "Nodos mas grandes y brillantes = mayor puente entre comunidades",
                 color="white", fontsize=13, pad=15)
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(OUT_IMPORT, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Guardada en: {OUT_IMPORT}")


# Paleta: Catppuccin Mocha
MOCHA = {
    "base":       "#1e1e2e",
    "mantle":     "#181825",
    "crust":      "#11111b",
    "surface0":   "#313244",
    "surface1":   "#45475a",
    "surface2":   "#585b70",
    "overlay0":   "#6c7086",
    "text":       "#cdd6f4",
    "subtext1":   "#bac2de",
    "rosewater":  "#f5e0dc",
    "flamingo":   "#f2cdcd",
    "pink":       "#f5c2e7",
    "mauve":      "#cba6f7",
    "red":        "#f38ba8",
    "maroon":     "#eba0ac",
    "peach":      "#fab387",
    "yellow":     "#f9e2af",
    "green":      "#a6e3a1",
    "teal":       "#94e2d5",
    "sky":        "#89dceb",
    "sapphire":   "#74c7ec",
    "blue":       "#89b4fa",
    "lavender":   "#b4befe",
}

MOCHA_ACCENTS = [
    MOCHA["red"],    MOCHA["peach"],   MOCHA["yellow"],  MOCHA["green"],
    MOCHA["teal"],   MOCHA["sky"],     MOCHA["blue"],    MOCHA["mauve"],
    MOCHA["pink"],   MOCHA["flamingo"],MOCHA["rosewater"],MOCHA["sapphire"],
    MOCHA["lavender"],MOCHA["maroon"],
]

CUSTOM_CSS = f"""
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  html, body {{
    width: 100%; height: 100%;
    overflow: hidden;
    background-color: {MOCHA["base"]};
    font-family: 'Segoe UI', sans-serif;
  }}

  #mynetwork {{
    width: 100vw !important;
    height: 100vh !important;
    border: none !important;
    background-color: {MOCHA["base"]};
  }}

  /* ── Loading bar ── */
  #loadingBar {{
    position: fixed !important;
    top: 0 !important; left: 0 !important;
    width: 100vw !important; height: 100vh !important;
    background-color: {MOCHA["base"]} !important;
    display: flex;
    align-items: center !important;
    justify-content: center !important;
    z-index: 999 !important;
    transition: opacity 0.4s ease !important;
  }}

  #loadingBar.hidden {{
    pointer-events: none !important;
    opacity: 0 !important;
  }}

  /* Fila: [track──────────] [65%] */
  .outerBorder {{
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 12px !important;
    background: {MOCHA["surface0"]} !important;
    border: 1px solid {MOCHA["surface2"]} !important;
    border-radius: 999px !important;
    box-shadow: none !important;
    padding: 10px 18px !important;
    width: 340px !important;
    height: auto !important;
    position: static !important;
    top: auto !important;
  }}

  #border {{
    flex: 1 !important;
    position: relative !important;
    top: auto !important; left: auto !important;
    width: auto !important;
    height: 6px !important;
    background: {MOCHA["surface2"]} !important;
    border-radius: 999px !important;
    overflow: hidden !important;
  }}

  #bar {{
    position: absolute !important;
    top: 0 !important; left: 0 !important;
    height: 100% !important;
    width: 0;
    background: linear-gradient(90deg, {MOCHA["blue"]}, {MOCHA["mauve"]}, {MOCHA["pink"]}) !important;
    background-size: 340px 100% !important;
    border-radius: 999px !important;
  }}

  #text {{
    position: static !important;
    top: auto !important; right: auto !important;
    width: 36px !important;
    height: auto !important;
    color: {MOCHA["mauve"]} !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    text-align: right !important;
  }}
</style>
"""


# ─────────────────────────────────────────
# 3. VISUALIZACIÓN INTERACTIVA (pyvis)
# ─────────────────────────────────────────

def vis_interactiva(G: nx.Graph) -> None:
    print("Generando visualizacion interactiva HTML...")

    partition   = community_louvain.best_partition(G, weight="weight")
    betweenness = nx.betweenness_centrality(G)
    degrees     = dict(G.degree())

    net = Network(height="100vh", width="100%",
                  bgcolor=MOCHA["base"], font_color=MOCHA["text"],
                  notebook=False)
    net.barnes_hut(gravity=-8000, central_gravity=0.3,
                   spring_length=120, spring_strength=0.05)

    for nid in G.nodes():
        name  = G.nodes[nid].get("name", nid)
        cid   = partition.get(nid, 0)
        color = MOCHA_ACCENTS[cid % len(MOCHA_ACCENTS)]
        size  = 10 + degrees[nid] * 3 + betweenness[nid] * 500
        title = (f"<b style='color:{MOCHA['mauve']}'>{name}</b><br>"
                 f"<span style='color:{MOCHA['subtext1']}'>Colaboradores: {degrees[nid]}<br>"
                 f"Comunidad: {cid}<br>"
                 f"Betweenness: {betweenness[nid]:.4f}</span>")
        net.add_node(nid, label=name, color=color,
                     size=float(size), title=title,
                     font={"color": MOCHA["text"], "size": 11})

    for u, v, d in G.edges(data=True):
        w = d["weight"]
        net.add_edge(u, v, value=w,
                     title=f"<span style='color:{MOCHA['subtext1']}'>Colaboraciones: {w}</span>",
                     color=MOCHA["overlay0"] + "66")

    net.save_graph(OUT_HTML)

    # Post-procesar el HTML
    with open(OUT_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. CSS personalizado
    html = html.replace("</head>", CUSTOM_CSS + "</head>")

    # 2. Pantalla completa — eliminar franja blanca
    html = html.replace('style="width: 100%; height: 750px"', 'style="width:100%;height:100vh"')
    html = html.replace("height: 750px", "height: 100vh")

    # 3. Parchar el JS de la barra: reemplazar cálculo en px por porcentaje
    #    pyvis usa: document.getElementById('bar').style.width = width + 'px'
    #    donde width = widthFactor * 496  → lo reemplazamos por widthFactor * 100 + '%'
    html = html.replace(
        "document.getElementById('bar').style.width = width + 'px';\n"
        "                          document.getElementById('text').innerHTML = Math.round(widthFactor*100) + '%';",
        "var pct = Math.round(widthFactor * 100);\n"
        "                          document.getElementById('bar').style.width = pct + '%';\n"
        "                          document.getElementById('text').innerHTML = pct + '%';"
    )
    html = html.replace(
        "document.getElementById('bar').style.width = '496px';",
        "document.getElementById('bar').style.width = '100%';"
    )

    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  Guardada en: {OUT_HTML}")
    print("  Abre el archivo en tu navegador para explorarla.")


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main() -> None:
    print("Cargando grafo...")
    G = load_graph(GRAPH_FILE)
    print(f"  {G.number_of_nodes()} nodos | {G.number_of_edges()} aristas")

    print("\nCalculando layout (puede tardar unos segundos)...")
    pos = get_layout(G)

    vis_completa(G, pos)
    vis_importantes(G, pos)
    vis_interactiva(G)

    print(f"\nVisualizaciones generadas en data/")


if __name__ == "__main__":
    main()
