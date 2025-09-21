import uuid

class Graph():
    def __init__(self, name):
        self.id = uuid.uuid4().hex
        self.name = name
        self.nodes = []

    def create_node(self, name):
        node = Node(name)
        self.nodes.append(node)

    def data_list(self):
        nodes_data = {}
        for n in self.nodes:
            nodes_data[n.name] = n.edges
        db_list = {
            'id': self.id,
            'name': self.name,
            'nodes': nodes_data
        }
        return db_list

class Node():
    def __init__(self, name):
        self.name = name
        self.edges = []
    
    def add_edge(self, node_name):
        self.edges.append(node_name)