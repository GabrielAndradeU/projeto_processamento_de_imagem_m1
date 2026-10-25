from pathlib import Path

import cv2
import numpy as np

from anotacoes import carregar_vagas
from recorte import recortar_vaga

RAIZ = Path(__file__).resolve().parents[1]
PASTA_ENTRADA = RAIZ / "images" / "input"
PASTA_SAIDA = RAIZ / "images" / "results" / "diagnostico"

LIMITE_PRETO = 0.5   # fração de pixels pretos a partir da qual o recorte é sinalizado
NIVEL_PRETO = 5      # tom de cinza (0-255) considerado preto


def fracao_preta(recorte):
    """Fração de pixels praticamente pretos no recorte."""
    cinza = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)
    return float(np.mean(cinza <= NIVEL_PRETO))


def pontos_fora(contorno, largura, altura):
    """Quantos dos 4 cantos da vaga caem fora da imagem."""
    x = contorno[:, 0]
    y = contorno[:, 1]
    fora = (x < 0) | (x >= largura) | (y < 0) | (y >= altura)
    return int(fora.sum())


def desenhar_ids(imagem, vagas):
    """Contorno de cada vaga (verde = livre, vermelho = ocupada) com o id escrito no centro."""
    saida = imagem.copy()
    for vaga in vagas:
        cor = (0, 0, 255) if vaga["ocupada"] else (0, 255, 0)
        cv2.polylines(saida, [vaga["contorno"]], isClosed=True, color=cor, thickness=2)
        centro = vaga["contorno"].mean(axis=0).astype(int)
        cv2.putText(saida, str(vaga["id"]), (int(centro[0]) - 8, int(centro[1]) + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1, cv2.LINE_AA)
    return saida


if __name__ == "__main__":
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    for caminho_xml in sorted(PASTA_ENTRADA.glob("*.xml")):
        caminho_jpg = caminho_xml.with_suffix(".jpg")
        imagem = cv2.imread(str(caminho_jpg))
        if imagem is None:
            print(f"{caminho_jpg.name}: imagem não encontrada, pulando")
            continue

        altura, largura = imagem.shape[:2]
        vagas = carregar_vagas(caminho_xml)
        todos = np.vstack([v["contorno"] for v in vagas])

        print(f"\n{caminho_jpg.name}")
        print(f"  imagem: {largura} x {altura}")
        print(f"  contornos: x de {todos[:, 0].min()} a {todos[:, 0].max()}, "
              f"y de {todos[:, 1].min()} a {todos[:, 1].max()}")

        sinalizadas = 0
        for vaga in vagas:
            recorte = recortar_vaga(imagem, vaga["contorno"])
            preto = fracao_preta(recorte)
            if preto > LIMITE_PRETO:
                sinalizadas += 1
                estado = "ocupada" if vaga["ocupada"] else "livre"
                fora = pontos_fora(vaga["contorno"], largura, altura)
                print(f"  vaga {vaga['id']:>2} ({estado}): {preto:.0%} preto, "
                      f"{fora} de 4 cantos fora da imagem")
        print(f"  recortes sinalizados: {sinalizadas} de {len(vagas)}")

        cv2.imwrite(str(PASTA_SAIDA / f"{caminho_jpg.stem}_ids.jpg"), desenhar_ids(imagem, vagas))