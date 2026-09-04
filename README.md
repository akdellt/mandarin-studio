# MANDARIN STUDIO - Analisador de Tons em Mandarim

Projeto desenvolvido para visualização e análise de curvas de frequência (pitch) para auxílio na pronúncia de tons do Chinês.

## Teconologias e bibliotecas

- Linguagem: Python
- Captura de microfone: sounddevice + scipy
- Análise de áudio: parselmouth
- Dynamic Time Warping: fastdtw
- Geração de gráficos: matplotlib
- Reconhecimento de fala: [Vosk](https://alphacephei.com/vosk/models)
- Referência de áudio: edge-tts
- Ambiente de desenvolvimento: VS Code + Jupyter Notebook

## Requisitos do MVP

- [x] Leitura de arquivo de áudio `.wav` ao vivo
- [x] Tratamento do áudio (ruídos, silêncio e comprimento)
- [x] Identificação de fonema
- [x] Comparação com áudio base (banco de dados ou google)
- [x] Exibição do gráfico da curva do tom
- [ ] Exibição da porcentagem de fidelidade ao áudio base
- [ ] Refatoração do código em arquivo python

## Regras de negócio

- [ ] Comparação só pode ser feita se for a mesma sílaba
- [ ] Tons diferentes reprova
- [ ] Normalização de timbres diferentes (grave e agudo)
- [ ] Melhorar remoção do silêncio e ruídos iniciais/finais
- [ ] DTW < 25 - Perfeito, 25 a 45 - Melhorar, > 45 - Incorreto
