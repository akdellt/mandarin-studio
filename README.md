# MANDARIN STUDIO - Analisador de Tons em Mandarim

Ferramenta de análise de pronúncia em mandarim: grava a fala do usuário, extrai a curva de frequência (pitch), compara com um áudio de referência via Dynamic Time Warping e retorna uma avaliação de similaridade tonal.

Projeto de estudo em Python, com foco em processamento de áudio e organização de código.

> **Status:** MVP funcional via notebook/script. Interface gráfica ainda não implementada.

## Como funciona

1. Grava ou gera (via TTS) um áudio de referência de uma sílaba/caractere
2. Grava o áudio do usuário falando a mesma sílaba
3. Extrai a curva de pitch de ambos com `parselmouth`
4. Alinha as curvas com `fastdtw` e calcula a distância entre elas
5. Reconhece o fonema falado com `Vosk`, comparando com o esperado
6. Retorna uma categoria de resultado (perfeito / excelente / razoável / incorreto) e um gráfico comparativo

## Tecnologias

- **Linguagem:** Python 3.10+
- **Captura de microfone:** sounddevice + scipy
- **Análise de áudio:** parselmouth
- **Comparação de curvas (DTW):** fastdtw
- **Geração de gráficos:** matplotlib
- **Reconhecimento de fala:** Vosk
- **Geração de áudio de referência:** gTTS
- **Ambiente de desenvolvimento:** VS Code + Jupyter Notebook

## Instalação

```bash
git clone <https://github.com/akdellt/Mandarin-Studio.git>
cd mandarin-studio
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

Baixe um modelo do Vosk em chinês em [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models) e ajuste o caminho em `config.py`.

## Estrutura do projeto

```
mandarinstudio/
├── analysis/       # extração de pitch e reconhecimento de fala
├── audio/          # captura de microfone e geração de áudio de referência
├── comparison/     # cálc'ulo de DTW e avaliação do resultado
├── flashcards/     # manipulação de flashcards
├── visualization/  # geração de gráficos
└── config.py
notebooks/          # testes e exploração no Jupyter
tests/              # testes unitários
data/               # áudios gerados (não versionado)
```

## Requisitos do MVP

- [x] Captura de áudio ao vivo
- [x] Tratamento de ruído/silêncio
- [x] Identificação de fonema falado
- [x] Comparação com áudio de referência
- [x] Exibição gráfica da curva de tom
- [x] Percentual de similaridade com o áudio de referência
- [x] Código organizado em módulos Python
- [x] Estruturação dos flashcards
- [ ] Interface gráfica (Tkinter)

## Regras de negócio implementadas

- Similaridade por distância DTW: ≥90% Perfeito · 89–70% Excelente · 69–50% Razoável · <50% Incorreto
- A comparação de tom só é realizada se a sílaba falada corresponder à esperada; caso contrário, o resultado é automaticamente Incorreto
- Flashcards não têm restrição de caractere único, já que um mesmo hanzi pode ter pronúncias e significados diferentes (ex: 还, "hái" ou "huán")

## Em aberto / próximos passos

- [ ] Melhorar detecção de silêncio para sílabas curtas ou faladas baixo (ex: falha detectada em "是")
- [ ] Reconhecimento de fala (Vosk) retorna vazio em alguns monossílabos, mesmo com gramática restrita — investigar se está relacionado ao corte de silêncio acima

## Diário de bordo

<details>
<summary>16/09/2026 — 18/09/2026</summary>

- Alterado `check_spoken_pinyin` para comparar sílabas por pinyin sem tom
- Adicionado parâmetro `grammar` em `check_spoken_pinyin` para restringir candidatos de fonema em sílabas isoladas
- Removidos `spoken_pinyin` e `hanzi` do retorno de `check_spoken_pinyin`
- Restringido `evaluation.py` para não comparar tons quando a sílaba falada não corresponde à esperada
- Removida a condição que permitia categoria de similaridade mesmo com sílaba incorreta
- Refatoradas as funções afetadas pelos parâmetros de retorno removidos
- Movido o cálculo de `avg_distance` para dentro de `run_dtw`
- Corrigida a conversão de MP3 (gTTS) para WAV
- Melhorado o tratamento de ruído do 1º tom e limpeza de bordas em `pitch.py`
- Definida a estrutura `Flashcard` e suas funções CRUD
- Padronizados os eixos em `graphs.py` para melhor apresentação do gráfico
- Adicionado tratamento inicial de erros nas funções principais
- Corrigidos os caminhos globais em `config.py`
- Gravadas fixtures de áudio para os testes
- Adicionados testes automatizados iniciais para `analysis`, `comparison` e `flashcards`

</details>

<details>
<summary>13/09/2026</summary>

- Funções revisadas (refatoradas e renomeadas)
- Prints substituídos por logs
- Estruturas de retorno tipadas (NamedTuple) em `dtw.py` e `evaluation.py`
- `plot_graph` corrigido para receber os valores do DTW corretamente
- Corrigida redundância entre `limit` e `max_limit` em `evaluation.py`
- Notebook reestruturado, importando as funções dos módulos
- Adicionado `pyproject.toml`
- Pipeline completo testado com sucesso (哥哥)
- Identificado: threshold de corte de silêncio pode remover áudio demais em sílabas curtas/baixas (ex: 是)

</details>

<details>
<summary>11/09/2026</summary>

- Estruturação do repositório (pastas `data`, `notebooks`, `mandarinstudio`)
- Adicionados `requirements.txt` e `config.py`
- Funções organizadas em `analysis`, `audio`, `comparison` e `visualization`
- Normalização de nomes de parâmetros e adição de type hints

</details>

<details>
<summary>06/09/2026</summary>

- Adicionado percentual de acerto de tom e fonema
- Sensibilidade de detecção de silêncio ajustada (threshold 0.01 → 0.05)
- Testes com os 4 tons do mandarim
- Nova função `smooth_curve`
- Corrigida comparação de pinyin (estava ignorando o tom)

</details>
