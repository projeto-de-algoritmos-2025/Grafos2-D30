from src.dijkstra import dijkstra
from tkinter import messagebox, simpledialog, Toplevel, Canvas, Scrollbar
import tkinter.font as tkfont
import tkinter as tk
import json
import uuid
import os
import math

class Graph():
    def __init__(self, name):
        self.id = uuid.uuid4().hex
        self.name = name
        self.nodes = []
        self.edges = []

DEFAULT_FILE = 'db/database.json'

class App():
    def __init__(self, root):
        self.root = root
        self.root.title('Graph Manager')
        self.graphs = []
        self.current_filepath = DEFAULT_FILE

        # --- UI ---
        frame = tk.Frame(root, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text='Grafos:').grid(row=0, column=0, sticky='w')

        self.listbox = tk.Listbox(frame, height=10, width=60)
        self.listbox.grid(row=1, column=0, columnspan=3, sticky='nsew')
        self.listbox.bind('<Double-Button-1>', self.on_edit)

        # Scrollbar
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.grid(row=1, column=3, sticky='ns')
        self.listbox.configure(yscrollcommand=scrollbar.set)

        # Buttons
        btn_add = tk.Button(frame, text='Adicionar', width=12, command=self.on_add)
        btn_remove = tk.Button(frame, text='Remover', width=12, command=self.on_remove)
        btn_save = tk.Button(frame, text='Salvar em JSON', width=12, command=self.on_save)
        btn_view = tk.Button(frame, text='Gerar Caminho Mínimo', width=12, command=self.on_view)
        btn_quit = tk.Button(frame, text='Sair', width=12, command=root.quit)

        btn_add.grid(row=2, column=0, pady=8, sticky='w')
        btn_remove.grid(row=3, column=0, pady=4, sticky='w')
        btn_save.grid(row=2, column=2, pady=4, sticky='e')
        btn_view.grid(row=3, column=2, pady=4, sticky='e')

        btn_quit.grid(row=4, column=2, pady=(12,0), sticky='e')

        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Carrega automaticamente o arquivo padrão (se existir)
        if os.path.exists(self.current_filepath):
            try:
                self.load_from_file(self.current_filepath)
            except Exception:
                messagebox.showwarning('Aviso', f'Não foi possível carregar {self.current_filepath}')

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for g in self.graphs:
            self.listbox.insert(tk.END, g.name)

    def on_add(self):
        name = simpledialog.askstring('Adicionar grafo', 'Nome do grafo:')
        names = [item.name for item in self.graphs]
        if name in names:
            messagebox.showwarning('Erro', 'Já existe um grafo com esse nome.')
            return
        elif name == '':
            messagebox.showwarning('Erro', 'O nome não deve ser vazio.')
            return
        else:
            # cria objeto de grafo
            new_graph = Graph(name.strip())
            self.graphs.append(new_graph)
            self.refresh_listbox()

    def on_remove(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo('Remover', 'Selecione um grafo para remover.')
            return
        idx = sel[0]
        graph = self.graphs[idx]
        if messagebox.askyesno('Confirmar remoção', f'Deseja remover o grafo "{graph.name}"?'):
            del self.graphs[idx]
            self.refresh_listbox()

    def on_save(self):
        try:
            self.save_to_file(self.current_filepath)
            messagebox.showinfo('Salvo', f'Salvo em: {self.current_filepath}')
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao salvar:\n{e}')

    def save_to_file(self, filepath):
        # criar pasta se necessário
        folder = os.path.dirname(filepath)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            db_dump = []
            for g in self.graphs:
                db_dump.append({"id": g.id,
                                "name": g.name,
                                "nodes": g.nodes,
                                "edges": g.edges})
            json.dump(db_dump, f, ensure_ascii=False, indent=2)

    def load_from_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # deserialization start
        db_graphs = []
        
        for d in data:
            g = Graph(d["name"])
            g.id = d["id"]
            g.nodes = d["nodes"]
            g.edges = d["edges"]
            db_graphs.append(g)
        # deserialization end

        if not isinstance(data, list):
            raise ValueError('Formato inválido: esperado uma lista de grafos')
        self.graphs = db_graphs
        self.refresh_listbox()

    def on_edit(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo('Nós', 'Selecione um grafo para gerenciar os nós.')
            return
        idx = sel[0]
        graph = self.graphs[idx]
        self.open_nodes_window(graph)

    def open_nodes_window(self, graph):
        win = tk.Toplevel(self.root)
        win.title(f"Nós — {graph.name}")
        
        tk.Label(win, text='Nome:').grid(row=0, column=0, sticky='w', padx=8, pady=(8,0))
        name_node = tk.StringVar(value=graph.name)
        entry = tk.Entry(win, textvariable=name_node, width=40)
        entry.grid(row=0, column=1, padx=8, pady=(8,0), sticky='nsew')

        tk.Label(win, text='Nós:').grid(row=1, column=0, columnspan=2, sticky='w', padx=8, pady=(8,0))
        lb = tk.Listbox(win, height=12)
        lb.grid(row=2, column=0, columnspan=2, padx=8, pady=(4,8), sticky='nsew')

        sb = tk.Scrollbar(win, orient=tk.VERTICAL, command=lb.yview)
        sb.grid(row=2, column=2, sticky='ns')
        lb.configure(yscrollcommand=sb.set)

        def refresh_node_list():
            lb.delete(0, tk.END)
            for d in graph.nodes:
                lb.insert(tk.END, d)

        def add_node():
            name = simpledialog.askstring('Adicionar nó', 'Nome do nó:', parent=win)
            names = graph.nodes
            if name in names:
                messagebox.showwarning('Erro', 'Já existe um nó com esse nome.', parent=win)
                return
            elif name == '':
                messagebox.showwarning('Erro', 'O nome não deve ser vazio.', parent=win)
                return
            else:
                graph.nodes.append(name.strip())
                refresh_node_list()
                self.refresh_listbox()

        def remove_node():
            s = lb.curselection()
            if not s:
                messagebox.showinfo('Remover', 'Selecione um nó para remover.', parent=win)
                return
            i = s[0]
            node = graph.nodes[i]
            if messagebox.askyesno('Confirmar remoção', f'Deseja remover o nó "{node}"?', parent=win):

                for ed in graph.edges: # deleta as arestas
                    if i in ed[0]:
                        j = graph.edges.index(ed)
                        del graph.edges[j]

                del graph.nodes[i]
                refresh_node_list()
                self.refresh_listbox()

        def save_node():
            new_name = name_node.get().strip()
            names = [item.name for item in self.graphs]
            if (new_name in names) and (new_name != graph.name):
                messagebox.showwarning('Erro', 'Já existe um grafo com esse nome.', parent=win)
                return
            elif new_name == '':
                messagebox.showwarning('Erro', 'O nome não deve ser vazio.', parent=win)
                return
            else:
                graph.name = new_name
                refresh_node_list()
                self.refresh_listbox()
                win.destroy()

        def edit_node(self):
            s = lb.curselection()
            if not s:
                messagebox.showinfo('Editar', 'Selecione um nó para editar.', parent=win)
                return
            i = s[0]
            node = graph.nodes[i]

            # Janela de edição: permite alterar nome e selecionar arestas
            ed = tk.Toplevel(win)
            ed.title(f"Editar — {node}")

            tk.Label(ed, text='Nome:').grid(row=0, column=0, sticky='w', padx=8, pady=(8, 0))
            name_var = tk.StringVar(value=node)
            entry = tk.Entry(ed, textvariable=name_var, width=20)
            entry.grid(row=0, column=1, padx=8, pady=(8, 0), sticky='nsew')

            tk.Label(ed, text='Arestas de saída (selecione múltiplos e defina custos):').grid(
                row=1, column=0, columnspan=2, sticky='w', padx=8, pady=(8, 0))

            # Lista de possíveis arestas: todos os outros nós no mesmo grafo
            candidates = [d for d in graph.nodes if d != node]

            # Dicionário para armazenar o custo das arestas
            edge_costs = {}

            def update_cost(event, node_name, cost_var):
                """Função que será chamada para aumentar o custo da aresta quando pressionada uma seta"""
                current_cost = cost_var.get()
                if current_cost == "Desmarcado":
                    new_cost = 0
                else:
                    new_cost = int(current_cost) + 1
                cost_var.set(new_cost)

            # Preencher as opções de aresta com Checkbuttons e Spinboxes

            for idx, cand in enumerate(candidates):
                row = idx + 2
                tk.Label(ed, text=cand).grid(row=row, column=0, padx=8, pady=4, sticky='w')

                # Inicializa o valor da aresta (se existe)
                for item in graph.edges:
                    if graph.nodes.index(cand) in item[0] and graph.nodes.index(node) in item[0]:
                        edge_costs[cand] = item[1]
                        cost_var = tk.IntVar(value=item[1])  # Usando IntVar, já que é um valor inteiro
                        break
                else:
                    edge_costs[cand] = 0
                    cost_var = tk.IntVar(value=0)

                # Criar o Spinbox e associar a cost_var a ele
                cost_entry = tk.Spinbox(ed, from_=0, to=100, textvariable=cost_var, state="normal", width=5)
                cost_entry.grid(row=row, column=2, padx=8, pady=4, sticky='w')

                # Função de callback que será chamada sempre que o valor do Spinbox mudar
                def on_spinbox_change(*args, cand=cand, cost_var=cost_var):  # Passar 'cost_var' explicitamente
                    edge_costs[cand] = cost_var.get()  # Atualiza o custo para o nó específico
                    #print(edge_costs)  # Exibe para debug

                # Registrar a função de callback com trace
                cost_var.trace("w", on_spinbox_change)

                # Função para aumentar o custo ao pressionar a seta direita
                def increase_cost(event, cand=cand, cost_var=cost_var):  # Passar 'cost_var' explicitamente
                    current_value = cost_var.get()
                    new_value = current_value + 1
                    cost_var.set(new_value)  # Atualiza o valor do Spinbox
                    edge_costs[cand] = new_value  # Atualiza o dicionário de arestas

                # Associar a tecla de seta direita para aumentar o custo
                cost_entry.bind("<Right>", lambda event, var=cost_var, cand=cand: increase_cost(event, cand))
                

            def save_edit():
                new_name = name_var.get().strip()
                names = graph.nodes
                if (new_name in names) and (new_name != node):
                    messagebox.showwarning('Erro', 'Já existe um nó com esse nome.', parent=ed)
                    return
                elif new_name == '':
                    messagebox.showwarning('Erro', 'O nome não deve ser vazio.', parent=ed)
                    return
                    
    
                # Coletar as arestas selecionadas e seus custos
                new_edges = []
                for key, value in edge_costs.items():
                    if value != 0:
                        new_edges.append([[graph.nodes.index(node), graph.nodes.index(key)], value])

                
                # Salvar
                graph.nodes[s[0]] = new_name
                graph.edges = new_edges

                refresh_node_list()
                ed.destroy()

            btn_save = tk.Button(ed, text='Salvar', width=12, command=save_edit)
            btn_cancel = tk.Button(ed, text='Cancelar', width=12, command=ed.destroy)
            btn_save.grid(row=len(candidates) + 2, column=0, pady=8, padx=8, sticky='w')
            btn_cancel.grid(row=len(candidates) + 2, column=1, pady=8, padx=8, sticky='e')

            ed.grid_rowconfigure(1, weight=1)
            ed.grid_rowconfigure(2, weight=1)
            ed.grid_columnconfigure(1, weight=1)

            ed.after(100, ed.grab_set)
            ed.after(100, entry.focus_set)

        lb.bind('<Double-Button-1>', edit_node)
        btn_add = tk.Button(win, text='Adicionar', width=12, command=add_node)
        btn_remove = tk.Button(win, text='Remover', width=12, command=remove_node)
        btn_save = tk.Button(win, text='Salvar', width=12, command=save_node)
        btn_cancel = tk.Button(win, text='Cancelar', width=12, command=win.destroy)

        btn_add.grid(row=3, column=0, pady=4, padx=8, sticky='w')
        btn_remove.grid(row=4, column=0, pady=8, padx=8, sticky='w')
        btn_save.grid(row=3, column=1, pady=4, padx=8, sticky='e')
        btn_cancel.grid(row=4, column=1, pady=8, padx=8, sticky='e')

        win.grid_rowconfigure(1, weight=1)
        win.grid_rowconfigure(2, weight=1)
        win.grid_columnconfigure(1, weight=1)

        refresh_node_list()
        
        
        win.after(100, win.grab_set)
        win.after(100, win.focus_force)

    def on_view(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo('Visualizar Grafo', 'Selecione um grafo para visualizar.')
            return
        idx = sel[0]
        graph = self.graphs[idx]

        start_node = simpledialog.askstring('Nó de Origem', 'Digite o Nome do nó de origem:')
        if start_node not in graph.nodes:
            messagebox.showwarning('Erro', 'Não existe um nó com esse nome.', parent=self.root)
            return
        end_node = simpledialog.askstring('Nó de Destino', 'Digite o Nome do nó de destino:')
        if end_node not in graph.nodes:
            messagebox.showwarning('Erro', 'Não existe um nó com esse nome.', parent=self.root)
            return
        
        dict = dijkstra(graph, start_node, end_node)

        messagebox.showinfo('Algoritmo de Dijkstra', f'Caminho: {dict['path']}\nDistância: {dict['distance']}')
        