# projeto_processamento_de_imagem_m1
# Detecção de Vagas de Estacionamento Livres/Ocupadas

Projeto aplicado longitudinal da disciplina de Processamento de Imagens — Etapa M1.

## Integrantes

- Guilherme de Alcantara Leite
- Gabriel Andrade Urbano

## Problema investigado

A partir de imagens capturadas por câmeras fixas de estacionamentos, o projeto busca determinar automaticamente, para cada vaga individual, se ela está **livre** ou **ocupada**.

Trata-se de um problema de processamento de imagens porque a resposta (livre/ocupada) precisa ser inferida a partir do conteúdo visual de cada vaga — não há nenhuma informação estruturada disponível além da imagem em si. O sistema deve analisar o recorte correspondente a cada vaga e decidir seu estado com base em características visuais extraídas da imagem (por exemplo, textura, variação de intensidade de pixels ou bordas presentes na região).

## Contexto de aplicação

Sistemas de monitoramento de vagas são usados em estacionamentos comerciais, shoppings e áreas urbanas para orientar motoristas até vagas livres e reduzir o tempo gasto procurando estacionamento. Normalmente dependem de sensores físicos por vaga (caros de instalar e manter) ou de câmeras já existentes, que é a abordagem explorada aqui: usar apenas a análise de imagem para inferir a ocupação, sem hardware adicional por vaga.

## Objetivo

**Objetivo geral:** desenvolver um sistema capaz de classificar, a partir de uma imagem de estacionamento, o estado de cada vaga (livre ou ocupada).

**Objetivos específicos:**
- Extrair automaticamente o recorte de imagem correspondente a cada vaga, a partir das coordenadas fornecidas pelo dataset.
- Investigar características visuais simples (variância de intensidade, contagem de bordas) capazes de diferenciar vagas livres de ocupadas.
- Avaliar a proporção de acertos da abordagem inicial em um subconjunto de imagens de teste.
- Evoluir progressivamente de regras simples baseadas em limiar para uma abordagem de classificação mais robusta ao longo da M2 e M3.

## Visão resumida da solução proposta

O sistema recebe uma imagem de estacionamento e as coordenadas de cada vaga (fornecidas pelo dataset). Cada vaga é recortada individualmente, pré-processada (conversão para escala de cinza, normalização) e analisada por meio de uma característica extraída da região (inicialmente, variância de intensidade de pixels ou contagem de bordas). Com base nessa característica, a vaga é classificada como livre ou ocupada.

```
Imagem do estacionamento
        ↓
Recorte de cada vaga (coordenadas do dataset)
        ↓
Pré-processamento (escala de cinza, normalização)
        ↓
Extração de característica (variância de pixels / bordas)
        ↓
Classificação (limiar simples, nesta etapa)
        ↓
Resultado: vaga livre ou ocupada
```

## Conjunto/origem das imagens

- **Dataset:** [PKLot](https://web.inf.ufpr.br/vri/databases/parking-lot-database/) (UFPR/PUCPR), também disponível no Kaggle.
- Contém milhares de imagens de estacionamentos reais, já anotadas com a posição de cada vaga e seu status (ocupada/livre), capturadas em diferentes condições de iluminação e clima.
- Para a M1, será utilizado um subconjunto pequeno e controlado do dataset (poucas imagens de um mesmo estacionamento, em condição de iluminação semelhante), para reduzir variabilidade nos primeiros testes.
- **Licença/uso:** [preencher com a licença específica do PKLot — verificar na página oficial antes da entrega].

## Estágio atual do projeto

Etapa **M1**: definição do problema, escolha do dataset e desenho do pipeline preliminar concluídos. [Atualizar aqui conforme o projeto avançar: ex. "experimentos preliminares em andamento", "primeira versão do classificador por limiar implementada", etc.]

## Organização do repositório

```
[nome-do-projeto]/
├── README.md
├── docs/
│   └── proposta.md
├── images/
│   ├── input/        # imagens de exemplo do PKLot usadas nos testes
│   └── results/       # imagens de saída com vagas marcadas (livre/ocupada)
├── src/                # código-fonte (quando implementado)
├── notebooks/          # notebooks exploratórios (quando aplicável)
└── .gitignore
```

## Tecnologias previstas

- **Linguagem:** Python
- **Bibliotecas previstas:** OpenCV (pré-processamento, recorte, extração de características), NumPy
- Justificativa: Python + OpenCV é uma combinação amplamente documentada para tarefas clássicas de PDI (recorte, filtros, extração de bordas), adequada ao nível de complexidade da primeira versão do projeto.

## Instruções para reproduzir experimentos

[Ainda não há código implementado nesta etapa (M1). Esta seção será preenchida na M2 com instruções de ambiente (requirements.txt), comando de execução e parâmetros necessários.]

## Vídeo da M1

[Link do vídeo não listado no YouTube — adicionar após a gravação]

## Documentação adicional

- Proposta detalhada: [`docs/proposta.md`](docs/proposta.md)

## Uso de Inteligência Artificial generativa

[Preencher conforme uso real: ferramenta utilizada (ex. Claude), finalidade (ex. apoio na estruturação do README e da proposta), material produzido/modificado, e como o grupo verificou o conteúdo gerado.]
