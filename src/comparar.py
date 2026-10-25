"""Comparação controlada Config A (bordas brutas) x Config B (bordas + morfologia).

Uso (da raiz do repositório), depois de rodar `medidas.py A` e `medidas.py B`:
    python src/comparar.py

Mantém constantes: as mesmas vagas, a mesma divisão ajuste/teste (DIAS_TESTE) e o mesmo
critério de escolha do limiar (maior acurácia balanceada no ajuste). Só a medida muda.
Grava images/results/comparacao_AB.md (tabela pronta para o relatório).
"""
import sys
from pathlib import Path

from avaliacao import (DIAS_TESTE, carregar_medidas, contagens, escolher_limiar,
                       fmt, metricas)

RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / "images" / "results"
COLUNAS = ["acuracia", "acuracia_balanceada", "recall_livre", "precisao_livre", "f1_livre"]


def avaliar(caminho):
    linhas = carregar_medidas(caminho)
    ajuste = [l for l in linhas if l["dia"] not in DIAS_TESTE]
    teste = [l for l in linhas if l["dia"] in DIAS_TESTE]
    limiar = escolher_limiar(ajuste)
    if limiar is None or not teste:
        sys.exit(f"{caminho.name}: ajuste/teste inválidos (veja DIAS_TESTE em avaliacao.py).")
    return {
        "chaves": {(l["imagem"], l["id"]) for l in linhas},
        "limiar": limiar,
        "ajuste": (len(ajuste), contagens(ajuste, limiar), metricas(*contagens(ajuste, limiar))),
        "teste": (len(teste), contagens(teste, limiar), metricas(*contagens(teste, limiar))),
        "base": metricas(*contagens(teste, -1.0)),
    }


def main():
    caminhos = {c: PASTA / f"medidas_config{c}.csv" for c in "AB"}
    for c, caminho in caminhos.items():
        if not caminho.exists():
            sys.exit(f"Falta {caminho.name}. Rode: python src/medidas.py {c}")

    res = {c: avaliar(caminhos[c]) for c in "AB"}
    if res["A"]["chaves"] != res["B"]["chaves"]:
        sys.exit("As configs A e B não cobrem as mesmas vagas: a comparação não é controlada.")

    linhas_md = [
        f"Dias de teste: {sorted(DIAS_TESTE)} | vagas no ajuste: {res['A']['ajuste'][0]} "
        f"| vagas no teste: {res['A']['teste'][0]}",
        "",
        "| Método | Limiar (ajuste) | Acurácia | Acur. balanceada | Recall livre | Precisão livre | F1 livre |",
        "|---|---|---|---|---|---|---|",
        "| Baseline 'sempre ocupada' | — | " + " | ".join(fmt(res["A"]["base"][k]) for k in COLUNAS) + " |",
    ]
    for c, nome in (("A", "Config A (bordas brutas)"), ("B", "Config B (+ morfologia)")):
        m = res[c]["teste"][2]
        linhas_md.append(f"| {nome} | {res[c]['limiar']:.4f} | "
                         + " | ".join(fmt(m[k]) for k in COLUNAS) + " |")

    linhas_md += ["", "Matrizes de confusão no TESTE (positivo = livre):", "",
                  "| Config | VP | FN | FP | VN |", "|---|---|---|---|---|"]
    for c in "AB":
        vp, fn, fp, vn = res[c]["teste"][1]
        linhas_md.append(f"| {c} | {vp} | {fn} | {fp} | {vn} |")

    texto = "\n".join(linhas_md)
    print(texto)
    (PASTA / "comparacao_AB.md").write_text(texto + "\n", encoding="utf-8")
    print(f"\nTabela salva em {PASTA / 'comparacao_AB.md'}")


if __name__ == "__main__":
    main()
