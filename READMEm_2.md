# Detecção de Vagas de Estacionamento Livres/Ocupadas

Projeto aplicado longitudinal da disciplina de Processamento de Imagens — **Etapa M2** (continuação da M1).

## Integrantes

| Integrante | GitHub | Contribuição principal (ver evidências em `docs/relatorio_m2.md`) |
|---|---|---|
| Guilherme de Alcantara Leite | [@guilhermedalcantara](https://github.com/guilhermedalcantara) | ⚠️ PREENCHER |
| Gabriel de Andrade Urbano | [@GabrielAndradeU](https://github.com/GabrielAndradeU) | ⚠️ PREENCHER |

## Problema

A partir de imagens de câmeras fixas de estacionamento, determinar automaticamente, **para cada vaga**, se ela está **livre** ou **ocupada**, usando apenas o conteúdo visual da vaga (sem sensores).

## Objetivos (atualizados na M2)

- Recortar e retificar cada vaga a partir dos polígonos do XML do PKLot.
- Segmentar/descrever o conteúdo de cada vaga com técnicas clássicas: bordas (Canny), morfologia e componentes conectados.
- Comparar, de forma controlada, **bordas brutas (Config A)** contra **bordas + morfologia + filtro de componentes (Config B)**.
- Avaliar quantitativamente (acurácia balanceada, recall/precisão/F1 da classe "livre") com separação ajuste/teste **por dia**.
- M3: evoluir para um classificador sobre vários descritores (ver plano em `docs/relatorio_m2.md`).

> **Mudança de escopo desde a M1:** a proposta previa comparar descritores clássicos + SVM/RF contra uma CNN e usar o CNRPark-EXT. Na M2 o grupo concentrou-se em segmentação, morfologia e descritores simples (foco da etapa); CNN e CNRPark-EXT saem do escopo. Justificativa e registro em `docs/relatorio_m2.md` e `docs/proposta.md`.

## Estágio atual

| Etapa do pipeline | Estado |
|---|---|
| Leitura do XML e gabarito (`src/anotacoes.py`) | ✅ implementado |
| Recorte retificado por vaga (`src/recorte.py`) | ✅ implementado |
| Diagnóstico de recortes inválidos (`src/diagnostico.py`) | ✅ implementado |
| Medida de densidade de bordas — Config A (`src/medidas.py`) | ✅ implementado |
| Avaliação ajuste/teste com limiar (`src/avaliacao.py`) | ✅ implementado |
| Config B: fechamento morfológico + componentes conectados (`src/medidas.py B`) | ✅ implementado (⚠️ confirmar após rodar no PKLot) |
| Comparação A × B (`src/comparar.py`) e figuras (`src/figuras.py`) | ✅ implementado |
| Descritores adicionais (variância, LBP, HSV) | 🔜 planejado M3 |
| Classificador (SVM/regressão logística) | 🔜 planejado M3 |
| Overlay final com contagem de vagas livres | 🔜 planejado M3 |

## Pipeline implementado

```
imagem .jpg + .xml (PKLot)
   ↓ anotacoes.py   : polígono + rótulo (livre/ocupada) de cada vaga
   ↓ recorte.py     : retificação por perspectiva → recorte 64×96
   ↓ medidas.py     : cinza → Gaussiana 5×5 → Canny(50,150) → descarta margem de 15%
   │                  Config A: densidade de bordas
   │                  Config B: + fechamento morfológico + filtro de componentes por área
   ↓ avaliacao.py   : limiar escolhido nos dias de ajuste → métricas no dia de teste
```

Saídas: `images/results/` (contornos, recortes, CSV de medidas) e métricas no terminal.

## Dados

- **Dataset:** [PKLot](https://web.inf.ufpr.br/vri/databases/parking-lot-database/) (UFPR/PUCPR), licença CC BY 4.0. Citar: Almeida et al., *PKLot – A robust dataset for parking lot classification*, Expert Systems with Applications, 2015.
- **Não versionamos o dataset completo.** Em `images/input/` há apenas a amostra usada nos experimentos (pares `AAAA-MM-DD_HH_MM_SS.jpg` + `.xml`).
- **Amostra da Rodada 1 (preliminar):** 6 imagens, 166 vagas. Ajuste: 2012-12-07 (4 imagens, 110 vagas, 5 livres). Teste: 2012-12-12 (2 imagens, 56 vagas, **0 livres**). Estacionamento/clima: ⚠️ PREENCHER. IDs completos em `docs/relatorio_m2.md`.
- **Limitação:** quase não há vagas livres na amostra atual; será ampliada na Rodada 2 antes da conclusão da comparação A × B.
- **Referência de avaliação:** rótulos `occupied` do XML do PKLot, verificados manualmente pelos autores do dataset. Limite: não foram revisados por nós.
- **Atenção a vazamento:** ajuste e teste são separados por **dia** (`DIAS_TESTE` em `src/avaliacao.py`), pois quadros do mesmo dia são quase idênticos.

## Tecnologias

Python 3.⚠️ + OpenCV + NumPy + Matplotlib (versões em `requirements.txt`).

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Execução (a partir da raiz do repositório)

```bash
python src/anotacoes.py     # overlay de vagas: images/results/*_vagas.jpg
python src/recorte.py       # recortes: images/results/recortes/
python src/diagnostico.py   # recortes suspeitos (cantos fora da imagem)
python src/medidas.py A     # Config A -> images/results/medidas_configA.csv
python src/medidas.py B     # Config B -> images/results/medidas_configB.csv
python src/avaliacao.py images/results/medidas_configB.csv   # métricas detalhadas de uma config
python src/comparar.py      # tabela A x B -> images/results/comparacao_AB.md
python src/figuras.py B     # figuras do relatório -> images/results/figuras/
```

Os scripts podem ser chamados de qualquer diretório (os caminhos partem da raiz do repositório).

**Exemplo mínimo:** com os arquivos de `images/input/` e o comando `python src/comparar.py` (após `medidas.py A` e `B`), a saída esperada é a tabela de métricas no dia de teste (baseline, Config A, Config B) e as matrizes de confusão. ⚠️ Colar aqui um trecho real da saída.

## Resultados

Resumo, tabelas e figuras: [`docs/relatorio_m2.md`](docs/relatorio_m2.md).

**Rodada 1 (preliminar)** — dia de teste 2012-12-12, 56 vagas, todas ocupadas:

| Config | Limiar | Ocupadas previstas como livres (FP) | Ocupadas corretas (VN) |
|---|---|---|---|
| A (bordas brutas) | 0,0832 | 23 | 33 |
| B (+ morfologia) | 0,0831 | 12 | 44 |

A Config B reduziu os falsos "livre", mas o teste não tem vagas livres e o limiar foi ajustado com 5 vagas livres, então **a conclusão é preliminar**. A Rodada 2 (amostra ampliada) completará a comparação com recall, precisão e F1 da classe "livre".

## Estrutura

```
├── README.md
├── requirements.txt
├── docs/
│   ├── proposta.md
│   └── relatorio_m2.md
├── images/
│   ├── input/        # amostra do PKLot
│   └── results/      # saídas intermediárias e finais
├── src/              # anotacoes, recorte, diagnostico, medidas, avaliacao
├── notebooks/
└── tests/
```

## Documentação e vídeos

- Proposta: [`docs/proposta.md`](docs/proposta.md)
- Relatório M2: [`docs/relatorio_m2.md`](docs/relatorio_m2.md)
- Vídeo M1: https://youtu.be/zJYcdofJcpc
- Vídeo M2: ⚠️ PREENCHER (YouTube, não listado)

## Entrega M2

Tag/commit: ⚠️ PREENCHER (ex.: `m2-entrega`).

## Uso de Inteligência Artificial generativa

- **Ferramenta:** Claude (Anthropic).
- **Finalidade:** apoio na redação e estruturação do README, da proposta e do relatório; revisão e sugestões sobre o código (organização, tratamento de erros, desenho do experimento A vs B). ⚠️ Ajustar à realidade: se a IA gerou ou alterou trechos de código, listar quais arquivos.
- **Materiais modificados:** `README.md`, `docs/proposta.md`, `docs/relatorio_m2.md` ⚠️ + arquivos de código, se houver.
- **Verificação:** o grupo executou o código, conferiu as métricas nos CSV/saídas e revisou os textos. As decisões técnicas e a interpretação dos resultados são do grupo.
