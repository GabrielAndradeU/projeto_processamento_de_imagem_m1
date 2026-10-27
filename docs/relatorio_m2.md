# Relatório parcial — M2

**Projeto:** Detecção de vagas de estacionamento livres/ocupadas
**Integrantes:** Guilherme de Alcantara Leite ([@guilhermedalcantara](https://github.com/guilhermedalcantara)) e Gabriel de Andrade Urbano ([@GabrielAndradeU](https://github.com/GabrielAndradeU))

---

## 1. Síntese do problema e objetivos atuais

O projeto classifica, a partir de imagens de câmera fixa, cada vaga de um estacionamento como **livre** ou **ocupada**. A posição de cada vaga é conhecida (polígonos do XML do dataset PKLot); o que se infere é o estado da vaga a partir do conteúdo visual do recorte.

Na M2 o objetivo foi transformar a proposta da M1 em uma implementação parcial executável e avaliada, com foco em **segmentação (bordas), morfologia, análise de componentes conectados e descrição por uma medida de região**. Os objetivos atuais são:

1. Recortar e retificar cada vaga a partir do polígono anotado.
2. Calcular, por vaga, uma medida baseada em bordas e compará-la com e sem morfologia.
3. Escolher um limiar de decisão **apenas** com dias de ajuste e avaliá-lo em dias separados.
4. Documentar falhas e limitações para orientar a M3.

**Critérios de sucesso para a M2:** pipeline executável de ponta a ponta; comparação controlada entre duas configurações; ao menos um indicador quantitativo por configuração; um caso de sucesso e um de falha documentados.

## 2. Evolução desde a M1 e resposta ao feedback

### 2.1 O que foi mantido, corrigido ou substituído

| Item | Situação na M2 | Justificativa | Evidência |
|---|---|---|---|
| Dataset PKLot com XML das vagas | **Mantido** | Fornece polígonos e rótulos, dispensando anotação manual | `images/input/`, `src/anotacoes.py` |
| Extração de recorte por vaga | **Implementado** | Transformação de perspectiva padroniza cada vaga em 64×96 px | `src/recorte.py` |
| Característica simples por limiar (README da M1) | **Implementado** com densidade de bordas | Era o plano declarado para a M2 | `src/medidas.py` |
| Variância de intensidade | **Não implementada** | Priorizou-se bordas + morfologia, foco da M2; fica para a M3 | — |
| Equalização/gama no pré-processamento | **Não utilizada** | Optou-se por Gaussiana + Canny; efeito da iluminação passa a ser limitação analisada | Seção 7 |
| Descritores clássicos (LBP/HOG/cor) + SVM/RF | **Adiado para a M3** | Fora do foco da M2 (segmentação/morfologia) | Plano da M3 |
| CNN rasa | **Removida do escopo** | Complexidade e tempo; o enunciado não exige | `docs/proposta.md` |
| CNRPark-EXT como segundo dataset | **Removido** | Escopo e tempo; foco em um único dataset bem caracterizado | `docs/proposta.md` |
| Avaliação de generalização entre câmeras/clima | **Parcial** | Separação por dia implementada; câmeras/clima ficam para a M3 | `src/avaliacao.py` |

### 2.2 Resposta ao feedback da M1

> ⚠️ **Preencher com o feedback recebido.** Para cada orientação, indique a ação tomada ou a justificativa técnica para ter adotado outra solução, com o arquivo ou experimento correspondente. Se não houve feedback escrito, declare isso aqui.

| Orientação recebida | Ação tomada / justificativa | Arquivo ou experimento |
|---|---|---|
| ⚠️ | ⚠️ | ⚠️ |

## 3. Dados e protocolo experimental

### 3.1 Origem e características

- **Dataset:** PKLot (Almeida et al., 2015), UFPR/PUCPR, licença CC BY 4.0. As imagens têm 1280×720 px, vêm com um XML por imagem (polígono de 4 pontos e atributo `occupied` por vaga) e foram capturadas por câmeras fixas elevadas.
- **Estacionamento/câmera usado:** ⚠️ (ex.: UFPR04).
- **Distribuição:** o dataset **não é versionado** no repositório. As instruções de obtenção estão no README; `images/input/` contém apenas a amostra usada.

### 3.2 Amostra da rodada preliminar (Rodada 1)

| Dia | Imagens (ID) | Papel | Horário |
|---|---|---|---|
| 2012-12-07 | `2012-12-07_16_42_25`, `_16_47_25`, `_17_12_25`, `_17_17_25` | Ajuste do limiar | fim da tarde |
| 2012-12-12 | `2012-12-12_10_00_05`, `_10_05_05` | Teste | manhã |

| Conjunto | Imagens | Vagas | Livres | Ocupadas |
|---|---|---|---|---|
| Ajuste | 4 | 110 | 5 | 105 |
| Teste | 2 | 56 | **0** | 56 |
| Total | 6 | 166 | 5 | 161 |

Clima das imagens: ⚠️ (ensolarado/nublado/chuvoso, conforme a pasta de origem no PKLot).

**Limitação desta amostra:** a classe "livre" é praticamente inexistente (5 de 166 vagas) e **o conjunto de teste não contém nenhuma vaga livre**. Por isso recall, precisão e F1 da classe "livre" não são calculáveis e a acurácia do teste mede apenas a taxa de acerto sobre vagas ocupadas. Esta rodada é tratada como **preliminar** (ver seções 6 e 8).

### 3.3 Rodada 2 (amostra ampliada)

> ⚠️ **Preencher após ampliar a amostra:** dias, climas, nº de imagens, nº de vagas livres/ocupadas no ajuste e no teste, critério de seleção e lista de IDs. O critério deve incluir situações típicas e difíceis (vagas livres e ocupadas, diferentes horários e climas).

### 3.4 Referência de avaliação

- **Referência:** atributo `occupied` do XML do PKLot, produzido e verificado manualmente pelos autores do dataset.
- **Limites:** o grupo não revisou os rótulos; vagas parcialmente ocluídas ou fora do enquadramento podem ter rótulos discutíveis.
- **Alinhamento:** `src/anotacoes.py` desenha os polígonos sobre a imagem e `src/diagnostico.py` verifica recortes com cantos fora da imagem (**0 recortes sinalizados** em todas as imagens da Rodada 1).

### 3.5 Divisão ajuste/teste

A divisão é **por dia** (`DIAS_TESTE` em `src/avaliacao.py`), porque quadros do mesmo dia, em intervalos de 5 minutos, são quase idênticos. Colocá-los dos dois lados favoreceria artificialmente o resultado. O limiar é escolhido só nos dias de ajuste; os dias de teste são usados uma vez, para a avaliação final.

## 4. Pipeline implementado e etapas pendentes

```
imagem .jpg + .xml (PKLot)
   ↓ anotacoes.py : polígono e rótulo de cada vaga
   ↓ recorte.py   : retificação por perspectiva → 64×96 px
   ↓ medidas.py   : cinza → Gaussiana 5×5 → Canny(50,150) → descarta margem de 15%
   │                Config A: densidade de bordas
   │                Config B: + fechamento morfológico + filtro de componentes por área
   ↓ avaliacao.py : limiar nos dias de ajuste → métricas no dia de teste
   ↓ comparar.py  : tabela A × B
   ↓ figuras.py   : figuras do relatório
```

| Etapa | Operação | Parâmetros | Finalidade |
|---|---|---|---|
| Recorte | `getPerspectiveTransform` + `warpPerspective` | 64×96 px; cantos ordenados por ângulo | Padronizar geometria e escala da vaga |
| Suavização | Filtro gaussiano | kernel 5×5 | Reduzir ruído antes das bordas |
| Bordas | Canny | limiares 50 e 150 | Marcar contornos do veículo |
| Margem | Descarte da borda do recorte | 15% por lado | Evitar as linhas pintadas da vaga |
| Morfologia (B) | Fechamento (`MORPH_CLOSE`) | elemento elíptico 3×3 | Unir bordas fragmentadas |
| Componentes (B) | `connectedComponentsWithStats` (8-conexo) | área mínima = 8 px | Eliminar componentes de ruído |
| Decisão | Limiar na medida | escolhido no ajuste | Livre se medida ≤ limiar |

**Descritores calculados (unidade e forma de cálculo):**

- **Config A, densidade de bordas:** `N_borda / N_total`, onde `N_borda` é o número de pixels de borda na região central do recorte e `N_total` é o número de pixels dessa região. Adimensional, entre 0 e 1.
- **Config B, fração coberta por componentes de borda:** `N_mascara / N_total`, onde `N_mascara` é o número de pixels pertencentes a componentes com área ≥ 8 px após o fechamento. Adimensional, entre 0 e 1.

**Pendente (M3):** descritores adicionais (variância, cor/HSV, LBP), classificador sobre os descritores, avaliação por clima e câmera, e overlay final com a contagem de vagas livres.

## 5. Fundamentação das técnicas e parâmetros

- **Retificação por perspectiva:** vagas aparecem rotacionadas e deformadas pela câmera. A transformação leva cada vaga ao mesmo retângulo, de modo que a mesma medida seja comparável entre vagas. A ordenação dos cantos por ângulo em torno do centro evita pontos repetidos em vagas inclinadas.
- **Gaussiana 5×5:** o Canny é sensível a ruído de alta frequência (textura do asfalto, compressão JPEG). A suavização reduz bordas espúrias antes da detecção.
- **Canny (50/150):** a razão de 1:3 entre os limiares segue a recomendação usual do método (Canny, 1986). Os valores foram fixados antes dos experimentos e **não** foram otimizados no dia de teste. É um parâmetro sensível à iluminação (seção 7).
- **Margem de 15%:** as linhas brancas que delimitam a vaga produzem bordas fortes tanto em vagas livres quanto ocupadas e não carregam informação sobre ocupação. O descarte concentra a medida na região onde o veículo aparece.
- **Fechamento morfológico:** o contorno de um veículo gera bordas fragmentadas; o fechamento (dilatação seguida de erosão) liga fragmentos próximos sem alargar o conjunto. Foi escolhido em vez da abertura porque o objetivo é *unir* bordas do mesmo objeto, não remover estruturas finas.
- **Filtro de componentes por área:** componentes isolados e muito pequenos tendem a ser textura de asfalto, e não veículo. O limite de 8 px é um valor inicial; sua variação é parte do plano da M3.
- **Limiar por acurácia balanceada:** como as classes são muito desbalanceadas, a acurácia simples favorece a classe majoritária. A acurácia balanceada (média dos recalls de cada classe) pesa as duas classes igualmente. Os candidatos são os pontos médios entre medidas consecutivas do conjunto de ajuste.
- **Baseline "sempre ocupada":** dá o piso de comparação. Um método só tem valor se superar esse baseline em uma métrica que considere as duas classes.

**Métricas (positivo = livre):** `recall_livre = VP/(VP+FN)`; `precisão_livre = VP/(VP+FP)`; `F1_livre = 2·P·R/(P+R)`; `acurácia balanceada = (recall_livre + recall_ocupada)/2`, com `recall_ocupada = VN/(VN+FP)`.

## 6. Experimento 1 — bordas brutas (A) × bordas com morfologia (B)

### 6.1 Pergunta e configuração

> Fechamento morfológico seguido de filtro de componentes pequenos melhora a separação entre vagas livres e ocupadas em relação ao uso das bordas brutas?

- **Muda:** apenas o cálculo da medida (Config A × Config B).
- **Constante:** imagens, recortes, margem, parâmetros de Gaussiana/Canny, divisão ajuste/teste e critério de escolha do limiar.

### 6.2 Execução

```bash
python src/medidas.py A
python src/medidas.py B
python src/comparar.py
python src/figuras.py B
```

### 6.3 Resultados da Rodada 1 (preliminar)

**Distribuição da medida (todas as 166 vagas):**

| Config | Classe | Vagas | Média | Mín | Máx |
|---|---|---|---|---|---|
| A | livre | 5 | 0,0585 | 0,0316 | 0,0822 |
| A | ocupada | 161 | 0,1097 | 0,0364 | 0,1746 |
| B | livre | 5 | 0,0631 | 0,0457 | 0,0828 |
| B | ocupada | 161 | 0,1253 | 0,0380 | 0,2331 |

**Avaliação no dia de teste (2012-12-12; 56 vagas, todas ocupadas):**

| Método | Limiar (ajuste) | Acurácia | Acurácia balanceada | Recall livre | Precisão livre | F1 livre |
|---|---|---|---|---|---|---|
| Baseline "sempre ocupada" | — | 1,000 | n/d | n/d | n/d | n/d |
| Config A | 0,0832 | 0,589 | n/d | n/d | 0,000 | n/d |
| Config B | 0,0831 | 0,786 | n/d | n/d | 0,000 | n/d |

| Config | VP | FN | FP | VN |
|---|---|---|---|---|
| A | 0 | 0 | 23 | 33 |
| B | 0 | 0 | 12 | 44 |

### 6.4 Interpretação

1. **A rodada não permite concluir que B é melhor que A.** O teste não tem vagas livres; as métricas da classe "livre" não existem e a acurácia reflete só a taxa de acerto em ocupadas. O baseline obtém 1,000 justamente por isso.
2. **Indício, não prova:** a Config B classificou erroneamente como "livre" 12 das 56 ocupadas, contra 23 da Config A. Isso é compatível com a hipótese de que a remoção de componentes pequenos reduz bordas espúrias, mas o limiar de cada configuração foi estimado com apenas 5 vagas livres.
3. **Limiar pouco confiável:** os limiares ficaram em 0,083, praticamente no valor máximo das cinco vagas livres (0,082–0,083). Isso indica ajuste a poucos pontos.
4. **Sobreposição entre classes:** o valor mínimo das ocupadas (0,036–0,038) está abaixo da média das livres, o que mostra que existem veículos com poucas bordas detectadas.
5. **Possível mudança de condição entre ajuste e teste (hipótese a verificar):** o ajuste usa imagens do fim da tarde (16h42–17h17) e o teste, da manhã (10h00). Diferenças de iluminação podem deslocar a distribuição da medida e, com ela, o limiar adequado. Esta hipótese deve ser verificada comparando visualmente os recortes e as distribuições por horário.

### 6.5 Casos de sucesso e de falha (Config B, dia de teste)

| Tipo | Imagem | Vaga | Medida | Interpretação |
|---|---|---|---|---|
| Sucesso | `2012-12-12_10_00_05` | 24 | 0,1186 | Ocupada prevista ocupada; medida acima do limiar de 0,083 |
| Falha | `2012-12-12_10_05_05` | 5 | 0,0380 | Ocupada prevista livre; medida abaixo do limiar |

Figuras (em `images/results/figuras/`): `fig1_recortes.png`, `fig2_bordas_AB.png`, `fig3_histogramas.png`, `fig4_casos_B.png`.

> ⚠️ **Inserir as figuras com legenda e interpretação.** Modelo:
> `![Legenda](../images/results/figuras/fig4_casos_B.png)` — *Figura X. Caso de falha (vaga 5, 2012-12-12_10_05_05): ⚠️ descreva o que se vê no recorte (cor do veículo, sombra, bordas fracas) e por que a medida ficou abaixo do limiar.*

### 6.6 Rodada 2 (amostra ampliada)

> ⚠️ **Preencher após ampliar a amostra** (ver seção 3.3): repetir a tabela de métricas, as matrizes de confusão e os casos de sucesso/falha, agora com vagas livres e ocupadas nos dois conjuntos. Comparar com a Rodada 1 e concluir se a Config B melhora a separação.

## 7. Falhas, limitações e riscos

- **Desbalanceamento extremo na Rodada 1:** 5 livres em 166 vagas, 0 no teste. A conclusão sobre A × B depende da Rodada 2.
- **Teste em um único dia:** a avaliação é preliminar e pode refletir condições particulares desse dia.
- **Sensibilidade à iluminação:** os limiares do Canny são fixos; contraste e horário alteram a quantidade de bordas.
- **Veículos com poucas bordas:** carros de cor próxima à do asfalto ou com baixo contraste geram medida baixa e são confundidos com vagas livres (falha da vaga 5).
- **Sombras e linhas:** podem gerar bordas em vagas livres e elevar a medida.
- **Descritor único:** uma só medida escalar limita a separação entre classes; mitigação prevista na M3 com descritores adicionais e classificador.
- **Dependência do rótulo do dataset:** erros de anotação do PKLot não foram verificados pelo grupo.

## 8. Plano de conclusão para a M3

| Tarefa | Responsável | Evidência esperada |
|---|---|---|
| Ampliar a amostra (mais dias, climas e vagas livres) e documentá-la | ⚠️ | Tabela de amostra, métricas da Rodada 2 |
| Avaliar variação de parâmetros da B (área mínima, kernel, abertura), ajustando só nos dias de ajuste | ⚠️ | Tabela comparativa |
| Descritores adicionais (variância, HSV, LBP) | ⚠️ | CSV de descritores e análise |
| Classificador sobre os descritores (ex.: regressão logística/SVM) | ⚠️ | Métricas no teste, comparação com o limiar simples |
| Avaliar por clima e por horário | ⚠️ | Tabela por condição |
| Overlay final com contagem de vagas livres | ⚠️ | Imagens de saída |
| Testes e limpeza do repositório | ⚠️ | `tests/`, README final |

## 9. Contribuições dos integrantes

| Integrante | Contribuições | Evidências |
|---|---|---|
| Guilherme de Alcantara Leite | Implementação do núcleo do pipeline: leitura dos XMLs do PKLot e desenho das vagas; recorte e retificação por perspectiva (incluindo a correção da ordenação dos cantos por ângulo, que eliminou recortes totalmente pretos nas vagas 4, 5 e 9); densidade de bordas (Config A) e Config B com fechamento morfológico e componentes conectados; escolha do limiar por acurácia balanceada e avaliação no dia de teste; diagnóstico de recortes fora da imagem. Execução dos experimentos da Rodada 1. | `src/anotacoes.py`, `src/recorte.py`, `src/medidas.py`, `src/avaliacao.py`, `src/diagnostico.py`; `images/results/medidas_configA.csv`, `images/results/avaliacao_configA.txt`; histórico de commits |
| Gabriel de Andrade Urbano | Organização do repositório no GitHub (ajustes e padronização do `README.md`, do relatório e dos demais documentos); implementação do comparador A × B e do gerador de figuras do relatório. | `src/comparar.py`, `src/figuras.py`, `images/results/figuras/`; `README.md`, `docs/relatorio_m2.md`, `docs/proposta.md`; histórico de commits |

## 10. Referências

- ALMEIDA, P.; OLIVEIRA, L.; SILVA JR., E.; BRITTO JR., A.; KOERICH, A. **PKLot – A robust dataset for parking lot classification**. *Expert Systems with Applications*, 2015.
- AMATO, G. et al. **Deep learning for decentralized parking lot occupancy detection**. *Expert Systems with Applications*, 2017 (CNRPark-EXT; citado como trabalho relacionado).
- CANNY, J. **A computational approach to edge detection**. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 1986.
- Documentação do OpenCV: Canny, operações morfológicas e `connectedComponentsWithStats` (https://docs.opencv.org).

## 11. Declaração de uso de IA generativa

- **Ferramenta:** Claude (Anthropic).
- **Finalidade:** apoio na redação e estruturação do README, da proposta e deste relatório; sugestões e revisão de código (organização dos scripts, tratamento de erros, implementação da Config B, do comparador e do gerador de figuras).
- **Materiais modificados:** `README.md`, `docs/proposta.md`, `docs/relatorio_m2.md`, `src/medidas.py`, `src/avaliacao.py`, `src/comparar.py`, `src/figuras.py`, `src/anotacoes.py`, `src/recorte.py`, `src/diagnostico.py`, `requirements.txt`. ⚠️ Ajustar para refletir exatamente o que cada integrante usou.
- **Verificação:** o grupo executou os scripts no PKLot, conferiu as saídas e as métricas, e revisou os textos. A interpretação dos resultados e as decisões técnicas são do grupo, que responde pelo conteúdo entregue.
