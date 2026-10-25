import csv
import sys
from pathlib import Path

ARQUIVO_PADRAO = Path("images/results/medidas_configA.csv")
DIAS_TESTE = {"2012-12-12"}   # dias reservados para a avaliação final; os demais ajustam o limiar


def carregar_medidas(caminho):
    """Lê o CSV gerado pelo medidas.py."""
    with open(caminho, newline="", encoding="utf-8") as arquivo:
        return [
            {
                "imagem": l["imagem"],
                "dia": l["dia"],
                "id": l["id"],
                "medida": float(l["medida"]),
                "livre": l["rotulo_real"] == "livre",
            }
            for l in csv.DictReader(arquivo)
        ]


def contagens(linhas, limiar):
    """Positivo = livre. Prevê 'livre' quando a medida é menor ou igual ao limiar."""
    vp = fn = fp = vn = 0
    for l in linhas:
        previsto_livre = l["medida"] <= limiar
        if l["livre"] and previsto_livre:
            vp += 1
        elif l["livre"]:
            fn += 1
        elif previsto_livre:
            fp += 1
        else:
            vn += 1
    return vp, fn, fp, vn


def dividir(a, b):
    return a / b if b else None


def metricas(vp, fn, fp, vn):
    recall_livre = dividir(vp, vp + fn)          # das livres reais, quantas achei
    precisao_livre = dividir(vp, vp + fp)        # das que previ livres, quantas eram
    recall_ocupada = dividir(vn, vn + fp)        # das ocupadas reais, quantas acertei

    f1_livre = None
    if recall_livre is not None and precisao_livre is not None and (recall_livre + precisao_livre) > 0:
        f1_livre = 2 * recall_livre * precisao_livre / (recall_livre + precisao_livre)

    acuracia_balanceada = None
    if recall_livre is not None and recall_ocupada is not None:
        acuracia_balanceada = (recall_livre + recall_ocupada) / 2

    return {
        "acuracia": dividir(vp + vn, vp + fn + fp + vn),
        "acuracia_balanceada": acuracia_balanceada,
        "recall_livre": recall_livre,
        "precisao_livre": precisao_livre,
        "f1_livre": f1_livre,
    }


def fmt(valor):
    return "n/d" if valor is None else f"{valor:.3f}"


def escolher_limiar(linhas_ajuste):
    """Testa os pontos médios entre medidas consecutivas e fica com o de maior acurácia balanceada."""
    valores = sorted({l["medida"] for l in linhas_ajuste})
    candidatos = [(a + b) / 2 for a, b in zip(valores, valores[1:])]

    melhor_limiar, melhor_nota = None, -1.0
    for candidato in candidatos:
        nota = metricas(*contagens(linhas_ajuste, candidato))["acuracia_balanceada"]
        if nota is not None and nota > melhor_nota:   # em empate, fica o menor limiar
            melhor_limiar, melhor_nota = candidato, nota
    return melhor_limiar


def imprimir(titulo, linhas, limiar):
    vp, fn, fp, vn = contagens(linhas, limiar)
    m = metricas(vp, fn, fp, vn)
    livres = vp + fn
    print(f"\n=== {titulo} ===")
    print(f"vagas: {len(linhas)} ({livres} livres, {len(linhas) - livres} ocupadas)")
    print("                  previsto livre | previsto ocupada")
    print(f"real livre        {vp:>14} | {fn:>16}")
    print(f"real ocupada      {fp:>14} | {vn:>16}")
    print(f"acuracia: {fmt(m['acuracia'])} | acuracia balanceada: {fmt(m['acuracia_balanceada'])}")
    print(f"livre -> recall: {fmt(m['recall_livre'])} | precisao: {fmt(m['precisao_livre'])} | F1: {fmt(m['f1_livre'])}")


if __name__ == "__main__":
    caminho = Path(sys.argv[1]) if len(sys.argv) > 1 else ARQUIVO_PADRAO
    linhas = carregar_medidas(caminho)

    ajuste = [l for l in linhas if l["dia"] not in DIAS_TESTE]
    teste = [l for l in linhas if l["dia"] in DIAS_TESTE]

    print(f"Arquivo: {caminho}")
    print(f"Dias de ajuste: {sorted({l['dia'] for l in ajuste})}")
    print(f"Dias de teste:  {sorted({l['dia'] for l in teste})}")

    if not any(l["livre"] for l in ajuste) or all(l["livre"] for l in ajuste):
        print("O conjunto de ajuste precisa ter vagas livres E ocupadas.")
        sys.exit(1)

    limiar = escolher_limiar(ajuste)
    print(f"\nLimiar escolhido no ajuste: {limiar:.4f}")

    # Baseline "sempre ocupada": limiar negativo nunca prevê livre (medida >= 0)
    imprimir("AJUSTE - baseline 'sempre ocupada'", ajuste, -1.0)
    imprimir("AJUSTE - método", ajuste, limiar)
    if teste:
        imprimir("TESTE - baseline 'sempre ocupada'", teste, -1.0)
        imprimir("TESTE - método", teste, limiar)

    print("\n=== Ocupadas com menor medida (candidatas à análise de falhas) ===")
    ocupadas = sorted((l for l in linhas if not l["livre"]), key=lambda l: l["medida"])
    for l in ocupadas[:8]:
        print(f"{l['imagem']}  vaga {l['id']}  medida = {l['medida']:.4f}")