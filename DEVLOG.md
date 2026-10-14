## Diário de bordo

## 13/10/2026

- Definido o escopo da primeira versão: criar, listar, praticar e visualizar o gráfico
- Base da interface gerada com Copilot, a partir de uma especificação com as assinaturas reais das funções do backend
- Revisadas as assinaturas e o código gerado antes de aceitar
- Ajustado `plot_graph` para retornar a `Figure` em vez de chamar `plt.show()`, permitindo embutir o gráfico na janela
- Adicionadas edição e exclusão de flashcards na interface
- Testado o fluxo completo manualmente (criar → praticar → editar → excluir)
- Suíte de testes passando após a integração

## 16/09/2026

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

## 13/09/2026

- Funções revisadas (refatoradas e renomeadas)
- Prints substituídos por logs
- Estruturas de retorno tipadas (NamedTuple) em `dtw.py` e `evaluation.py`
- `plot_graph` corrigido para receber os valores do DTW corretamente
- Corrigida redundância entre `limit` e `max_limit` em `evaluation.py`
- Notebook reestruturado, importando as funções dos módulos
- Adicionado `pyproject.toml`
- Pipeline completo testado com sucesso (哥哥)
- Identificado: threshold de corte de silêncio pode remover áudio demais em sílabas curtas/baixas (ex: 是)

## 11/09/2026

- Estruturação do repositório (pastas `data`, `notebooks`, `mandarinstudio`)
- Adicionados `requirements.txt` e `config.py`
- Funções organizadas em `analysis`, `audio`, `comparison` e `visualization`
- Normalização de nomes de parâmetros e adição de type hints

## 06/09/2026

- Adicionado percentual de acerto de tom e fonema
- Sensibilidade de detecção de silêncio ajustada (threshold 0.01 → 0.05)
- Testes com os 4 tons do mandarim
- Nova função `smooth_curve`
- Corrigida comparação de pinyin (estava ignorando o tom)
