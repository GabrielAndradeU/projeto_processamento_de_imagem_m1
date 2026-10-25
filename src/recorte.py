from pathlib import Path

import cv2
import numpy as np

from anotacoes import carregar_vagas

PASTA_ENTRADA = Path("images/input")
PASTA_RECORTES = Path("images/results/recortes")

# Tamanho fixo de cada vaga retificada (ajuste olhando os recortes)
LARGURA = 64
ALTURA = 96


def ordenar_pontos(pontos):
    """Ordena 4 pontos em: topo-esq, topo-dir, baixo-dir, baixo-esq."""
    pontos = pontos.astype(np.float32)
    soma = pontos.sum(axis=1)                 # x + y
    dif = np.diff(pontos, axis=1).ravel()     # y - x

    ordenados = np.zeros((4, 2), dtype=np.float32)
    ordenados[0] = pontos[np.argmin(soma)]    # topo-esquerdo: menor x + y
    ordenados[2] = pontos[np.argmax(soma)]    # baixo-direito: maior x + y
    ordenados[1] = pontos[np.argmin(dif)]     # topo-direito: menor y - x
    ordenados[3] = pontos[np.argmax(dif)]     # baixo-esquerdo: maior y - x
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