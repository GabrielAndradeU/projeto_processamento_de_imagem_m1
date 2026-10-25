from pathlib import Path

import cv2
import numpy as np

from anotacoes import carregar_vagas

RAIZ = Path(__file__).resolve().parents[1]
PASTA_ENTRADA = RAIZ / "images" / "input"
PASTA_RECORTES = RAIZ / "images" / "results" / "recortes"

# Tamanho fixo de cada vaga retificada (ajuste olhando os recortes)
LARGURA = 64
ALTURA = 96


def ordenar_pontos(pontos):
    """Ordena 4 pontos no sentido horário, com o lado curto da vaga em 0->1.

    Ordena pelo ângulo em torno do centro (não depende de empates de soma/diferença,
    que geravam pontos repetidos em vagas inclinadas), começa pelo canto de menor
    x + y e gira a lista para que o lado 0->1 seja o menor: o lado curto da vaga
    vira LARGURA e o lado longo vira ALTURA.
    """
    pontos = pontos.astype(np.float32)
    centro = pontos.mean(axis=0)
    angulos = np.arctan2(pontos[:, 1] - centro[1], pontos[:, 0] - centro[0])
    # Na imagem o eixo y desce, então ângulo crescente = sentido horário
    ordenados = pontos[np.argsort(angulos)]

    inicio = int(np.argmin(ordenados.sum(axis=1)))
    ordenados = np.roll(ordenados, -inicio, axis=0)

    lado_01 = np.linalg.norm(ordenados[1] - ordenados[0])
    lado_12 = np.linalg.norm(ordenados[2] - ordenados[1])
    if lado_01 > lado_12:
        ordenados = np.roll(ordenados, -1, axis=0)
    return ordenados


def recortar_vaga(imagem, contorno):
    """Recorta e retifica uma vaga para um retângulo LARGURA x ALTURA."""
    origem = ordenar_pontos(contorno)
    destino = np.array([
        [0, 0],
        [LARGURA - 1, 0],
        [LARGURA - 1, ALTURA - 1],
        [0, ALTURA - 1],
    ], dtype=np.float32)

    matriz = cv2.getPerspectiveTransform(origem, destino)
    return cv2.warpPerspective(imagem, matriz, (LARGURA, ALTURA))


if __name__ == "__main__":
    for caminho_xml in sorted(PASTA_ENTRADA.glob("*.xml")):
        caminho_jpg = caminho_xml.with_suffix(".jpg")
        imagem = cv2.imread(str(caminho_jpg))
        if imagem is None:
            print(f"{caminho_jpg.name}: imagem não encontrada, pulando")
            continue

        pasta_saida = PASTA_RECORTES / caminho_jpg.stem
        pasta_saida.mkdir(parents=True, exist_ok=True)

        vagas = carregar_vagas(caminho_xml)
        for vaga in vagas:
            recorte = recortar_vaga(imagem, vaga["contorno"])
            estado = "ocupada" if vaga["ocupada"] else "livre"
            nome = f"vaga_{vaga['id']}_{estado}.jpg"
            cv2.imwrite(str(pasta_saida / nome), recorte)

        print(f"{caminho_jpg.name}: {len(vagas)} recortes salvos")