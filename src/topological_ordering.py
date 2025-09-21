def top_order(nodes):
    ordered_nodes = []
    count_vector = []
    
    # 1. Inicializa o vetor de contagem de arestas de entrada para cada nó
    for node in nodes:
        count_vector.append(len(node.edges))
    
    # 2. Loop principal para encontrar e processar nós com zero arestas de entrada
    for _ in range(0, len(nodes)):
        # Verifica se ainda há nós sem arestas de entrada
        if 0 in count_vector:
            # Encontra o índice do primeiro nó com zero arestas de entrada
            i = count_vector.index(0)
            
            # Marca o nó como processado (ou "remove" simbolicamente do grafo)
            count_vector[i] = -1
            
            # Adiciona o nó à lista ordenada
            ordered_nodes.append(nodes[i])
            
            # 3. Decrementa o contador de arestas de entrada para os vizinhos
            for j in range(0, len(nodes)):
                # Se o nó processado for uma aresta para outro nó...
                if nodes[i].name in nodes[j].edges:
                    # ...decrementa o contador do vizinho
                    count_vector[j] = count_vector[j] - 1
        else:
            # Se não houver mais nós com zero arestas de entrada, há um ciclo no grafo
            return []
            
    return ordered_nodes