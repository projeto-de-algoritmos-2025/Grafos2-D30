import heapq

def dijkstra(graph, start_node, end_node):
    """
    Encontra o caminho mais curto entre um nó inicial e um nó final
    usando o algoritmo de Dijkstra.

    Args:
        graph (dict): Um dicionário de grafo no formato JSON.
        start_node: O nó de partida.
        end_node: O nó de destino.

    Returns:
        dict: Um dicionário contendo o caminho mais curto do nó inicial ao final,
              e a distância total. Retorna None se o destino não for alcançável.
    """
    nodes = graph.nodes
    edges = graph.edges
    
    # Etapa 1: Converter para lista de adjacências
    adjacency_list = {node: [] for node in nodes}
    for edge in edges:
        source_index = edge[0][0]
        dest_index = edge[0][1]
        weight = edge[1]

        source_node = nodes[source_index]
        dest_node = nodes[dest_index]

        adjacency_list[source_node].append((dest_node, weight))

    # Etapa 2: Executar o algoritmo de Dijkstra
    distances = {node: float('inf') for node in adjacency_list}
    previous_nodes = {node: None for node in adjacency_list}
    distances[start_node] = 0
    priority_queue = [(0, start_node)]  # (distância, nó)

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        # Se o nó atual for o destino, o caminho foi encontrado
        if current_node == end_node:
            break

        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in adjacency_list[current_node]:
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    # Etapa 3: Reconstruir o caminho
    path = []
    current_node = end_node
    while current_node is not None:
        path.insert(0, current_node)
        current_node = previous_nodes[current_node]

    # Verifica se o destino foi alcançado
    if path[0] == start_node:
        return {
            "path": path,
            "distance": distances[end_node]
        }
    else:
        return None  # Retorna None se o nó de destino não for alcançável


"""
# Exemplo de uso
graph = {
    "id": "17049ee2478340ef93fc4f657eaf53b1",
    "name": "G",
    "nodes": ["A", "B", "C", "D"],
    "edges": [ [ [0, 1], 1 ], [ [0, 2], 10 ], [ [1, 2], 1 ], [ [1, 3], 10 ], [ [2, 3], 10 ] ]
}

graph_2 = {
    "id": "17049ee2478340ef93fc4f657eaf53b1",
    "name": "G",
    "nodes": ["A", "B", "C", "D"],
    "edges": [ [ [0, 1], 3 ], [ [0, 2], 5 ] ]
}

start_node = 'A'
end_node = 'C'
result = dijkstra(graph, start_node, end_node)

if result:
    print(f"Caminho mais curto de {start_node} para {end_node}:")
    print(f"Caminho: {result['path']}")
    print(f"Distância: {result['distance']}")
else:
    print(f"Nenhum caminho encontrado de {start_node} para {end_node}.")
"""