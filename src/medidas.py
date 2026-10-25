import csv
from pathlib import Path

import cv2
import numpy as np

from anotacoes import carregar_vagas
from recorte import recortar_vaga

PASTA_ENTRADA = Path("images/input")
ARQUIVO_SAIDA = Path("images/results/medidas_configA.csv")

MARGEM = 0.15          # fração descartada em cada lado do recorte (evita as linhas pintadas)
CANNY_BAIXO = 50
CANNY_ALTO = 150
LIMIAR = 0.10          # PROVISÓRIO: será escolhido no passo 4 com as imagens de ajuste


def densidade_de_bordas(recorte):
    """Fração de pixels de borda (Canny) na região central do recorte, entre 0 e 1."""
    cinza = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)
    suave = cv2.GaussianBlur(cinza, (5, 5), 0)
    bordas = cv2.Canny(suave, CANNY_BAIXO, CANNY_ALTO)

    altura, largura = bordas.shape
    dy = int(altura * MARGEM)
    dx = int(largura * MARGEM)
    centro = bordas[dy:altura - dy, dx:largura - dx]

    return np.count_nonzero(centro) / centro.size


if __name__ == "__main__":
    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    linhas = []

    for caminho_xml in sorted(PASTA_ENTRADA.glob("*.xml")):
        caminho_jpg = caminho_xml.with_suffix(".jpg")
        imagem = cv2.imread(str(caminho_jpg))
        if imagem is None:
            print(f"{caminho_jpg.name}: imagem não encontrada, pulando")
            continue

        dia = caminho_jpg.stem[:10]   # ex.: 2012-12-07 (usado depois para separar ajuste/teste)

        for vaga in carregar_vagas(caminho_xml):
            recorte = recortar_vaga(imagem, vaga["contorno"])
            medida = densidade_de_bordas(recorte)
            predicao_ocupada = medida > LIMIAR

            linhas.append({
                "imagem": caminho_jpg.name,
                "dia": dia,
                "id": vaga["id"],
                "rotulo_real": "ocupada" if vaga["ocupada"] else "livre",
                "medida": round(medida, 4),
                "predicao": "ocupada" if predicao_ocupada else "livre",
                "acertou": predicao_ocupada == vaga["ocupada"],
            })

    with open(ARQUIVO_SAIDA, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0].keys()))
        escritor.writeheader()
        escritor.writerows(linhas)

    print(f"{len(linhas)} vagas salvas em {ARQUIVO_SAIDA}")

    for classe in ("livre", "ocupada"):
        valores = [l["medida"] for l in linhas if l["rotulo_real"] == classe]
        if valores:
            print(f"{classe}: {len(valores)} vagas, medida média = {np.mean(valores):.4f}, "
                  f"mín = {min(valores):.4f}, máx = {max(valores):.4f}")
        else:
            print(f"{classe}: nenhuma vaga")