# Detecção de Vagas de Estacionamento Livres/Ocupadas

Projeto aplicado longitudinal da disciplina de Processamento de Imagens — **Etapa M2** (continuação da M1).

## Integrantes

| Integrante | GitHub | Contribuição principal (evidências em `docs/relatorio_m2.md`, seção 9) |
|---|---|---|
| Guilherme de Alcantara Leite | [@guilhermedalcantara](https://github.com/guilhermedalcantara) | Núcleo do pipeline: leitura de XML, recorte retificado, medidas de bordas (Configs A e B), avaliação com limiar e diagnóstico de recortes |
| Gabriel de Andrade Urbano | [@GabrielAndradeU](https://github.com/GabrielAndradeU) | Organização do repositório e dos documentos; comparador A × B (`src/comparar.py`) e gerador de figuras (`src/figuras.py`) |

## Problema

A partir de imagens de câmeras fixas de estacionamento, determinar automaticamente, **para cada vaga**, se ela está **livre** ou **ocupada**, usando apenas o conteúdo visual da vaga (sem sensores).

Sistemas de monitoramento de vagas costumam depender de sensores físicos por vaga, caros de instalar e manter. Aqui exploramos o uso de câmeras já existentes e análise de imagem, sem hardware adicional por vaga.

## Objetivos (atualizados na M2)

- Recortar e retificar cada vaga a partir dos polígonos do XML do PKLot.
- Segmentar/descrever o conteúdo de cada vaga com técnicas clássicas: bordas (Canny), morfologia e componentes conectados.
- Comparar, de forma controlada, **bordas brutas (Config A)** contra **bordas + morfologia + filtro de componentes (Config B)**.
- Avaliar quantitativamente (acurácia balanceada, recall/precisão/F1 da classe "livre") com separação ajuste/teste **por dia**.
- M3: evoluir para um classificador sobre vários descritores (plano em `docs/relatorio_m2.md`).

> **Mudança de escopo desde a M1:** a proposta previa comparar descritores clássicos + SVM/RF contra uma CNN e usar o CNRPark-EXT. Na M2 o grupo concentrou-se em segmentação, morfologia e descritores simples (foco da etapa); CNN e CNRPark-EXT saem do escopo. Justificativa e registro em `docs/relatorio_m2.md` e `docs/proposta.md`.

## Estágio atual

| Etapa do pipeline | Estado |
|---|---|
| Leitura do XML e gabarito (`src/anotacoes.py`) | ✅ implementado |
| Recorte retificado por vaga (`src/recorte.py`) | ✅ implementado |
| Diagnóstico de recortes inválidos (`src/diagnostico.py`) | ✅ implementado |
| Medida de densidade de bordas — Config A (`src/medidas.py A`) | ✅ implementado |
| Config B: fechamento morfológico + componentes conectados (`src/medidas.py B`) | ✅ implementado |
| Avaliação ajuste/teste com limiar (`src/avaliacao.py`) | ✅ implementado |
| Comparação A × B (`src/comparar.py`) e figuras (`src/figuras.py`) | ✅ implementado |
| Ampliação da amostra (mais dias, climas e vagas livres) | 🔜 planejado M3 |
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
   ↓ comparar.py    : tabela A × B
   ↓ figuras.py     : figuras do relatório
```

Saídas: `images/results/` (contornos, recortes, CSV de medidas, figuras) e métricas no terminal.

## Dados

- **Dataset:** [PKLot](https://web.inf.ufpr.br/vri/databases/parking-lot-database/) (UFPR/PUCPR), licença CC BY 4.0. Citar: Almeida et al., *PKLot – A robust dataset for parking lot classification*, Expert Systems with Applications, 2015.
- **Estacionamento/câmera usado:** UFPR04.
- **Não versionamos o dataset completo.** Em `images/input/` há apenas a amostra usada nos experimentos (pares `AAAA-MM-DD_HH_MM_SS.jpg` + `.xml`).
- **Amostra preliminar:** 6 imagens, 166 vagas.
  - Ajuste: 2012-12-07 (`16_42_25`, `16_47_25`, `17_12_25`, `17_17_25`; 110 vagas, 5 livres).
  - Teste: 2012-12-12 (`10_00_05`, `10_05_05`; 56 vagas, **0 livres**).
  - Clima: [PREENCHER: Sunny, Cloudy ou Rainy de cada dia].
  - A imagem `2012-12-07_16_52_25.jpg` está em `images/input/` mas não tem XML, então não é usada.
- **Como obter os dados:** baixe o PKLot pelo link acima, localize as imagens dos dias 2012-12-07 e 2012-12-12 da UFPR04 e copie para `images/input/` o `.jpg` e o `.xml` de cada ID listado.
- **Limitação:** quase não há vagas livres na amostra atual e o teste não tem nenhuma. A ampliação da amostra fica para a M3.
- **Referência de avaliação:** rótulos `occupied` do XML do PKLot, verificados manualmente pelos autores do dataset. Limite: não foram revisados por nós.
- **Atenção a vazamento:** ajuste e teste são separados por **dia** (`DIAS_TESTE` em `src/avaliacao.py`), pois quadros do mesmo dia são quase idênticos.

## Tecnologias

- **Python 3.12**, com ambiente virtual `venv` (testado no Windows).
- **OpenCV** (`opencv-python`): leitura de imagens, suavização gaussiana, Canny, transformação de perspectiva, operações morfológicas e componentes conectados.
- **NumPy**: arrays, coordenadas dos polígonos e cálculo das medidas.
- **Matplotlib**: figuras do relatório (`src/figuras.py`).
- **Biblioteca padrão:** `xml.etree.ElementTree` (anotações XML), `csv`, `pathlib`.
- **Dados:** PKLot, câmera UFPR04 (imagens `.jpg` com anotações `.xml` por vaga).

Versões exatas das bibliotecas em `requirements.txt`.

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

**Exemplo mínimo:** com os arquivos de `images/input/`, rode `python src/medidas.py A`, `python src/medidas.py B` e `python src/comparar.py`. A saída esperada é a tabela de métricas no dia de teste (baseline, Config A, Config B) e as matrizes de confusão. [PREENCHER: colar aqui um trecho real da saída do `comparar.py`.]

## Resultados

Resumo, tabelas e figuras: [`docs/relatorio_m2.md`](docs/relatorio_m2.md).

**Amostra preliminar** — dia de teste 2012-12-12, 56 vagas, todas ocupadas:

| Config | Limiar | Ocupadas previstas como livres (FP) | Ocupadas corretas (VN) |
|---|---|---|---|
| A (bordas brutas) | 0,0832 | 23 | 33 |
| B (+ morfologia) | 0,0831 | 12 | 44 |

A Config B reduziu os falsos "livre", mas o teste não tem vagas livres e o limiar foi ajustado com apenas 5 vagas livres, então **a conclusão é preliminar**. Recall, precisão e F1 da classe "livre" só poderão ser calculados quando a amostra for ampliada na M3.

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
├── src/              # anotacoes, recorte, diagnostico, medidas, avaliacao, comparar, figuras
├── notebooks/
└── tests/
```

## Documentação e vídeos

- Proposta: [`docs/proposta.md`](docs/proposta.md)
- Relatório M2: [`docs/relatorio_m2.md`](docs/relatorio_m2.md)
- Vídeo M1: https://youtu.be/zJYcdofJcpc
- Vídeo M2: https://youtu.be/T9y1NH5FoJI

## Uso de Inteligência Artificial generativa

- **Ferramenta:** Claude (Anthropic).
- **Finalidade:** apoio na redação e estruturação do README, da proposta e do relatório; sugestões e revisão de código (organização dos scripts, tratamento de erros, implementação da Config B, do comparador e do gerador de figuras).
- **Uso por integrante:** Guilherme usou a ferramenta no núcleo do pipeline (`src/anotacoes.py`, `src/recorte.py`, `src/medidas.py`, `src/avaliacao.py`, `src/diagnostico.py`, `requirements.txt`). Gabriel [PREENCHER: usou / não usou] ferramenta de IA em `src/comparar.py`, `src/figuras.py` e nos documentos.
- **Materiais modificados:** `README.md`, `docs/proposta.md`, `docs/relatorio_m2.md`, `src/medidas.py`, `src/avaliacao.py`, `src/comparar.py`, `src/figuras.py`, `src/anotacoes.py`, `src/recorte.py`, `src/diagnostico.py`, `requirements.txt`.
- **Verificação:** o grupo executou o código, conferiu as métricas nos CSV/saídas e revisou os textos. As decisões técnicas e a interpretação dos resultados são do grupo.
