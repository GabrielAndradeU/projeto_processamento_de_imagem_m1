"""Gera as figuras do relatório M2 em images/results/figuras/.

Uso (da raiz do repositório), depois de rodar medidas.py A e B:
    python src/figuras.py        # casos de sucesso/falha usando a Config B
    python src/figuras.py A      # casos de sucesso/falha usando a Config A

Figuras:
  fig1_recortes.png    grade de recortes retificados (livres x ocupadas)
  fig2_bordas_AB.png   recorte | bordas brutas (A) | bordas após morfologia (B)
  fig3_histogramas.png distribuição da medida por classe, com o limiar do ajuste
  fig4_casos_<cfg>.png um caso de sucesso e dois de falha, no dia de teste
"""
import sys
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from anotacoes import carregar_vagas
from avaliacao import DIAS_TESTE, carregar_medidas, escolher_limiar
from medidas import MEDIDAS, mapa_bordas, mapa_morfologico
from recorte import recortar_vaga

RAIZ = Path(__file__).resolve().parents[1]
PASTA_ENTRADA = RAIZ / "images" / "input"
PASTA_RESULTADOS = RAIZ / "images" / "results"
PASTA_FIGURAS = PASTA_RESULTADOS / "figuras"


def rgb(imagem_bgr):
    return cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2RGB)


class Acervo:
    """Carrega imagens/vagas sob demanda e devolve o recorte de (imagem, id)."""

    def __init__(self):
        self._imagens, self._vagas = {}, {}

    def recorte(self, nome_jpg, id_vaga):
        if nome_jpg not in self._imagens:
            self._imagens[nome_jpg] = cv2.imread(str(PASTA_ENTRADA / nome_jpg))
            xml = (PASTA_ENTRADA / nome_jpg).with_suffix(".xml")
            self._vagas[nome_jpg] = {v["id"]: v for v in carregar_vagas(xml)}
        vaga = self._vagas[nome_jpg][int(id_vaga)]
        return recortar_vaga(self._imagens[nome_jpg], vaga["contorno"])


def carregar(config):
    caminho = PASTA_RESULTADOS / f"medidas_config{config}.csv"
    if not caminho.exists():
        sys.exit(f"Falta {caminho.name}. Rode: python src/medidas.py {config}")
    return carregar_medidas(caminho)


def espalhado(linhas, n):
    """n elementos distribuídos ao longo da lista (evita pegar só os vizinhos)."""
    if len(linhas) <= n:
        return list(linhas)
    idx = np.linspace(0, len(linhas) - 1, n).astype(int)
    return [linhas[i] for i in idx]


def fig1_recortes(acervo, linhas, n=8):
    teste = [l for l in linhas if l["dia"] in DIAS_TESTE]
    base = teste if teste else linhas
    nome = base[0]["imagem"]
    da_imagem = [l for l in linhas if l["imagem"] == nome]
    grupos = [("livre", [l for l in da_imagem if l["livre"]]),
              ("ocupada", [l for l in da_imagem if not l["livre"]])]

    fig, eixos = plt.subplots(2, n, figsize=(1.4 * n, 5))
    for linha, (classe, vagas) in enumerate(grupos):
        for col, l in enumerate(espalhado(vagas, n)):
            eixos[linha, col].imshow(rgb(acervo.recorte(l["imagem"], l["id"])))
            eixos[linha, col].set_title(f"vaga {l['id']}", fontsize=8)
        eixos[linha, 0].set_ylabel(classe, fontsize=11)
    for eixo in eixos.ravel():
        eixo.set_xticks([]); eixo.set_yticks([])
    fig.suptitle(f"Recortes retificados (64×96 px) — {nome}", fontsize=11)
    fig.tight_layout()
    fig.savefig(PASTA_FIGURAS / "fig1_recortes.png", dpi=150)
    plt.close(fig)


def fig2_bordas(acervo, linhas, por_classe=2):
    escolhidas = []
    for livre in (True, False):
        escolhidas += espalhado([l for l in linhas if l["livre"] == livre], por_classe)

    fig, eixos = plt.subplots(len(escolhidas), 3, figsize=(6, 2.6 * len(escolhidas)))
    eixos = np.atleast_2d(eixos)
    for i, l in enumerate(escolhidas):
        recorte = acervo.recorte(l["imagem"], l["id"])
        bordas = mapa_bordas(recorte)
        mascara, n_comp = mapa_morfologico(bordas)
        classe = "livre" if l["livre"] else "ocupada"
        eixos[i, 0].imshow(rgb(recorte))
        eixos[i, 0].set_title(f"{classe} — vaga {l['id']}", fontsize=8)
        eixos[i, 1].imshow(bordas, cmap="gray")
        eixos[i, 1].set_title(f"A: bordas ({np.count_nonzero(bordas) / bordas.size:.3f})", fontsize=8)
        eixos[i, 2].imshow(mascara, cmap="gray")
        eixos[i, 2].set_title(f"B: morfologia ({np.count_nonzero(mascara) / mascara.size:.3f}, "
                              f"{n_comp} comp.)", fontsize=8)
    for eixo in eixos.ravel():
        eixo.set_xticks([]); eixo.set_yticks([])
    fig.tight_layout()
    fig.savefig(PASTA_FIGURAS / "fig2_bordas_AB.png", dpi=150)
    plt.close(fig)


def limiar_do_ajuste(linhas):
    return escolher_limiar([l for l in linhas if l["dia"] not in DIAS_TESTE])


def fig3_histogramas(dados):
    fig, eixos = plt.subplots(1, 2, figsize=(10, 3.8))
    for eixo, config in zip(eixos, "AB"):
        linhas = dados[config]
        livres = [l["medida"] for l in linhas if l["livre"]]
        ocupadas = [l["medida"] for l in linhas if not l["livre"]]
        maximo = max(livres + ocupadas) or 1.0
        faixas = np.linspace(0, maximo, 40)
        eixo.hist(livres, bins=faixas, alpha=0.6, color="tab:green", label="livre")
        eixo.hist(ocupadas, bins=faixas, alpha=0.6, color="tab:red", label="ocupada")
        limiar = limiar_do_ajuste(linhas)
        if limiar is not None:
            eixo.axvline(limiar, color="k", linestyle="--", label=f"limiar = {limiar:.3f}")
        eixo.set_title(f"Config {config}")
        eixo.set_xlabel("medida (fração, adimensional)")
        eixo.set_ylabel("nº de vagas")
        eixo.legend(fontsize=8)
    fig.suptitle("Distribuição da medida por classe (todas as vagas); "
                 "limiar escolhido apenas nos dias de ajuste", fontsize=10)
    fig.tight_layout()
    fig.savefig(PASTA_FIGURAS / "fig3_histogramas.png", dpi=150)
    plt.close(fig)


def fig4_casos(acervo, linhas, config):
    teste = [l for l in linhas if l["dia"] in DIAS_TESTE]
    limiar = limiar_do_ajuste(linhas)
    if not teste or limiar is None:
        print("fig4: sem dados de teste/limiar; ignorada.")
        return

    ocupadas = sorted((l for l in teste if not l["livre"]), key=lambda l: l["medida"])
    livres = sorted((l for l in teste if l["livre"]), key=lambda l: l["medida"])
    casos = []
    acerto_ocup = [l for l in ocupadas if l["medida"] > limiar]
    if acerto_ocup:
        casos.append(("SUCESSO: ocupada prevista ocupada", acerto_ocup[len(acerto_ocup) // 2]))
    if ocupadas and ocupadas[0]["medida"] <= limiar:
        casos.append(("FALHA: ocupada prevista livre", ocupadas[0]))
    if livres and livres[-1]["medida"] > limiar:
        casos.append(("FALHA: livre prevista ocupada", livres[-1]))
    if not casos:
        print("fig4: nenhum caso encontrado.")
        return

    fig, eixos = plt.subplots(len(casos), 3, figsize=(6.5, 2.7 * len(casos)))
    eixos = np.atleast_2d(eixos)
    for i, (titulo, l) in enumerate(casos):
        recorte = acervo.recorte(l["imagem"], l["id"])
        bordas = mapa_bordas(recorte)
        mascara, _ = mapa_morfologico(bordas)
        eixos[i, 0].imshow(rgb(recorte))
        eixos[i, 0].set_title(f"{titulo}\n{l['imagem']} vaga {l['id']}", fontsize=7)
        eixos[i, 1].imshow(bordas, cmap="gray")
        eixos[i, 1].set_title("bordas (Canny)", fontsize=8)
        eixos[i, 2].imshow(mascara, cmap="gray")
        eixos[i, 2].set_title(f"medida {config} = {l['medida']:.3f}\nlimiar = {limiar:.3f}", fontsize=8)
    for eixo in eixos.ravel():
        eixo.set_xticks([]); eixo.set_yticks([])
    fig.tight_layout()
    fig.savefig(PASTA_FIGURAS / f"fig4_casos_{config}.png", dpi=150)
    plt.close(fig)
    for titulo, l in casos:
        print(f"  {titulo}: {l['imagem']} vaga {l['id']} medida={l['medida']:.4f}")


if __name__ == "__main__":
    config_casos = sys.argv[1].upper() if len(sys.argv) > 1 else "B"
    if config_casos not in MEDIDAS:
        sys.exit("Uso: python src/figuras.py [A|B]")
    PASTA_FIGURAS.mkdir(parents=True, exist_ok=True)

    dados = {c: carregar(c) for c in "AB"}
    acervo = Acervo()
    fig1_recortes(acervo, dados["A"])
    fig2_bordas(acervo, dados["A"])
    fig3_histogramas(dados)
    print(f"Casos da Config {config_casos}:")
    fig4_casos(acervo, dados[config_casos], config_casos)
    print(f"Figuras salvas em {PASTA_FIGURAS}")
