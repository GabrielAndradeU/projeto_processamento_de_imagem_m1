"""Calcula a medida de cada vaga para a Config A ou B e grava um CSV.

Uso (da raiz do repositório):
    python src/medidas.py A     # bordas brutas
    python src/medidas.py B     # bordas + fechamento morfológico + filtro de componentes

Tudo que NÃO muda entre A e B (recorte, suavização, Canny, margem) está nas mesmas
funções e constantes; a única diferença é `medida_config_b` aplicar a morfologia.
"""
import csv
import sys
from pathlib import Path

import cv2
import numpy as np

from anotacoes import carregar_vagas
from recorte import recortar_vaga

RAIZ = Path(__file__).resolve().parents[1]
PASTA_ENTRADA = RAIZ / "images" / "input"
PASTA_RESULTADOS = RAIZ / "images" / "results"

# --- parâmetros comuns (iguais em A e B) ---
MARGEM = 0.15          # fração descartada em cada lado do recorte (evita as linhas pintadas)
CANNY_BAIXO = 50
CANNY_ALTO = 150
KERNEL_GAUSS = (5, 5)

# --- parâmetros exclusivos da Config B ---
KERNEL_MORF = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
AREA_MIN = 8           # px: componentes menores que isso são tratados como ruído


def mapa_bordas(recorte):
    """Mapa binário de bordas (Canny) da região central do recorte (0 ou 255)."""
    cinza = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)
    suave = cv2.GaussianBlur(cinza, KERNEL_GAUSS, 0)
    bordas = cv2.Canny(suave, CANNY_BAIXO, CANNY_ALTO)

    altura, largura = bordas.shape
    dy = int(altura * MARGEM)
    dx = int(largura * MARGEM)
    return bordas[dy:altura - dy, dx:largura - dx]


def mapa_morfologico(bordas):
    """Config B: fechamento (une bordas fragmentadas) + remoção de componentes pequenos.

    Devolve a máscara filtrada (0 ou 255) e a quantidade de componentes mantidos.
    """
    fechado = cv2.morphologyEx(bordas, cv2.MORPH_CLOSE, KERNEL_MORF)
    n, rotulos, stats, _ = cv2.connectedComponentsWithStats(fechado, connectivity=8)
    manter = np.zeros(n, dtype=bool)
    manter[1:] = stats[1:, cv2.CC_STAT_AREA] >= AREA_MIN   # índice 0 é o fundo
    mascara = np.where(manter[rotulos], 255, 0).astype(np.uint8)
    return mascara, int(manter.sum())


def medida_config_a(recorte):
    """Densidade de bordas: fração (0 a 1, adimensional) de pixels de borda na região central."""
    bordas = mapa_bordas(recorte)
    return np.count_nonzero(bordas) / bordas.size


def medida_config_b(recorte):
    """Fração (0 a 1, adimensional) da região central coberta por componentes de borda
    com área >= AREA_MIN após o fechamento morfológico."""
    mascara, _ = mapa_morfologico(mapa_bordas(recorte))
    return np.count_nonzero(mascara) / mascara.size


MEDIDAS = {"A": medida_config_a, "B": medida_config_b}


def main(config):
    funcao = MEDIDAS[config]
    saida = PASTA_RESULTADOS / f"medidas_config{config}.csv"
    saida.parent.mkdir(parents=True, exist_ok=True)
    linhas = []

    for caminho_xml in sorted(PASTA_ENTRADA.glob("*.xml")):
        caminho_jpg = caminho_xml.with_suffix(".jpg")
        imagem = cv2.imread(str(caminho_jpg))
        if imagem is None:
            print(f"{caminho_jpg.name}: imagem não encontrada, pulando")
            continue

        dia = caminho_jpg.stem[:10]   # ex.: 2012-12-07 (usado para separar ajuste/teste)

        for vaga in carregar_vagas(caminho_xml):
            recorte = recortar_vaga(imagem, vaga["contorno"])
            linhas.append({
                "imagem": caminho_jpg.name,
                "dia": dia,
                "id": vaga["id"],
                "rotulo_real": "ocupada" if vaga["ocupada"] else "livre",
                "medida": round(float(funcao(recorte)), 4),
            })

    if not linhas:
        print(f"Nenhuma vaga encontrada em {PASTA_ENTRADA}. "
              "Coloque pares .jpg/.xml do PKLot nessa pasta.")
        sys.exit(1)

    with open(saida, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0].keys()))
        escritor.writeheader()
        escritor.writerows(linhas)

    print(f"Config {config}: {len(linhas)} vagas salvas em {saida}")
    for classe in ("livre", "ocupada"):
        valores = [l["medida"] for l in linhas if l["rotulo_real"] == classe]
        if valores:
            print(f"  {classe}: {len(valores)} vagas, medida média = {np.mean(valores):.4f}, "
                  f"mín = {min(valores):.4f}, máx = {max(valores):.4f}")
        else:
            print(f"  {classe}: nenhuma vaga")


if __name__ == "__main__":
    escolha = sys.argv[1].upper() if len(sys.argv) > 1 else "A"
    if escolha not in MEDIDAS:
        sys.exit("Uso: python src/medidas.py [A|B]")
    main(escolha)