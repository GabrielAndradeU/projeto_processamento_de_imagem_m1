import xml.etree.ElementTree as ET
from pathlib import Path

import cv2
import numpy as np

PASTA_ENTRADA = Path("images/input")
PASTA_RESULTADOS = Path("images/results")

COR_LIVRE = (0, 255, 0)      # verde (BGR)
COR_OCUPADA = (0, 0, 255)    # vermelho (BGR)


def carregar_vagas(caminho_xml):
    """Lê o XML do PKLot e devolve uma lista de vagas.

    Cada vaga é um dict: {"id": int, "ocupada": bool, "contorno": np.ndarray (4x2, int32)}
    Vagas sem o atributo "occupied" (sem rótulo) são ignoradas.
    """
    vagas = []
    raiz = ET.parse(caminho_xml).getroot()

    for espaco in raiz.findall("space"):
        # TODO 1: o atributo vem como texto ("1" ou "0") ou None se não existir
        atributo = espaco.get("occupied")
        if atributo is None:
            continue  # sem gabarito, não serve para avaliação
        ocupada = atributo == "1"

        pontos = [
            (int(p.get("x")), int(p.get("y")))
            for p in espaco.find("contour").findall("point")
        ]
        vagas.append({
            "id": int(espaco.get("id")),
            "ocupada": ocupada,
            "contorno": np.array(pontos, dtype=np.int32),
        })
    return vagas


def desenhar_vagas(imagem, vagas):
    """Desenha o contorno de cada vaga: verde = livre, vermelho = ocupada."""
    saida = imagem.copy()
    for vaga in vagas:
        # TODO 2: escolhe a cor conforme o estado (OpenCV usa BGR)
        cor = COR_OCUPADA if vaga["ocupada"] else COR_LIVRE
        cv2.polylines(saida, [vaga["contorno"]], isClosed=True, color=cor, thickness=2)
    return saida


if __name__ == "__main__":
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    for caminho_xml in sorted(PASTA_ENTRADA.glob("*.xml")):
        caminho_jpg = caminho_xml.with_suffix(".jpg")
        imagem = cv2.imread(str(caminho_jpg))
        if imagem is None:
            print(f"{caminho_jpg.name}: imagem não encontrada, pulando")
            continue

        vagas = carregar_vagas(caminho_xml)

        # TODO 3: resumo por imagem
        total = len(vagas)
        ocupadas = sum(v["ocupada"] for v in vagas)
        livres = total - ocupadas
        print(f"{caminho_jpg.name}: {total} vagas, {ocupadas} ocupadas, {livres} livres")

        cv2.imwrite(str(PASTA_RESULTADOS / f"{caminho_jpg.stem}_vagas.jpg"),
                    desenhar_vagas(imagem, vagas))