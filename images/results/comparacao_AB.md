Dias de teste: ['2012-12-12'] | vagas no ajuste: 110 | vagas no teste: 56

| Método | Limiar (ajuste) | Acurácia | Acur. balanceada | Recall livre | Precisão livre | F1 livre |
|---|---|---|---|---|---|---|
| Baseline 'sempre ocupada' | — | 1.000 | n/d | n/d | n/d | n/d |
| Config A (bordas brutas) | 0.0832 | 0.589 | n/d | n/d | 0.000 | n/d |
| Config B (+ morfologia) | 0.0831 | 0.786 | n/d | n/d | 0.000 | n/d |

Matrizes de confusão no TESTE (positivo = livre):

| Config | VP | FN | FP | VN |
|---|---|---|---|---|
| A | 0 | 0 | 23 | 33 |
| B | 0 | 0 | 12 | 44 |
