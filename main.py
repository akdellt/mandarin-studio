def alocar_pacotes(lista_pacotes, lista_entregadores):
     for pacote in lista_pacotes:
        pares_distancia = []
        for entregador in lista_entregadores:
            dist = calcular_distancia_geograficamente(pacote.coordenadas, entregador.coordenadas)
            pares_distancia.append([entregador, dist])

        tamanho = len(pares_distancia)
        for i in range(tamanho - 1):
             for j in range(i-2):
                  if (pares_distancia[j].dist > pares_distancia[j+1]):
                       pares_distancia[j] = pares_distancia[j+1]

        pacote.calocado_para = pares_distancia[0].entregador