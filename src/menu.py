from src.classes import Graph, Node
from src.topological_ordering import top_order
from tkinter import messagebox, simpledialog, Toplevel, Canvas, Scrollbar
import tkinter.font as tkfont
import tkinter as tk
import json
import uuid
import os
import math

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
        btn_view = tk.Button(frame, text='Gerar Topologia', width=12, command=self.on_view)
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
                db_dump.append(g.data_list())
            json.dump(db_dump, f, ensure_ascii=False, indent=2)

    def load_from_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # deserialization start
        db_graphs = []
        
        for d in data:
            db_nodes = []
            for key, value in d['nodes'].items():
                db_node = Node(key)
                db_node.edges = value
                db_nodes.append(db_node)

            db_graph = Graph(d['name'])
            db_graph.id = d['id']
            db_graph.nodes = db_nodes
            db_graphs.append(db_graph)
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
                lb.insert(tk.END, d.name)

        def add_node():
            name = simpledialog.askstring('Adicionar nó', 'Nome do nó:', parent=win)
            names = [item.name for item in graph.nodes]
            if name in names:
                messagebox.showwarning('Erro', 'Já existe um nó com esse nome.', parent=win)
                return
            elif name == '':
                messagebox.showwarning('Erro', 'O nome não deve ser vazio.', parent=win)
                return
            else:
                graph.create_node(name.strip())
                refresh_node_list()
                self.refresh_listbox()

        def remove_node():
            s = lb.curselection()
            if not s:
                messagebox.showinfo('Remover', 'Selecione um nó para remover.', parent=win)
                return
            i = s[0]
            node = graph.nodes[i]
            if messagebox.askyesno('Confirmar remoção', f'Deseja remover o nó "{node.name}"?', parent=win):
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
            ed.title(f"Editar — {node.name}")

            tk.Label(ed, text='Nome:').grid(row=0, column=0, sticky='w', padx=8, pady=(8,0))
            name_var = tk.StringVar(value=node.name)
            entry = tk.Entry(ed, textvariable=name_var, width=20)
            entry.grid(row=0, column=1, padx=8, pady=(8,0), sticky='nsew')

            tk.Label(ed, text='Arestas de saída (selecione múltiplos):').grid(row=1, column=0, columnspan=2, sticky='w', padx=8, pady=(8,0))

            # Lista de possíveis arestas: todos os outros nós no mesmo grafo
            candidates = [d for d in graph.nodes if d.name != node.name]
            listbox_pr = tk.Listbox(ed, selectmode=tk.MULTIPLE, height=10, width=40)
            listbox_pr.grid(row=2, column=0, columnspan=2, padx=8, pady=(4,8), sticky='nsew')

            # preencher
            id_to_index = {}
            for idx_c, cand in enumerate(candidates):
                listbox_pr.insert(tk.END, cand.name)
                id_to_index[cand.name] = idx_c

            # pre-selecionar os que já são arestas
            existing = node.edges
            for pid in existing:
                if pid in id_to_index:
                    listbox_pr.selection_set(id_to_index[pid])

            def save_edit():
                new_name = name_var.get().strip()
                names = [item.name for item in graph.nodes]
                if (new_name in names) and (new_name != node.name):
                    messagebox.showwarning('Erro', 'Já existe um nó com esse nome.', parent=ed)
                    return
                elif new_name == '':
                    messagebox.showwarning('Erro', 'O nome não deve ser vazio.', parent=ed)
                    return
                
                # coletar seleções e mapear para ids
                sel_idxs = listbox_pr.curselection()
                selected_ids = [candidates[j].name for j in sel_idxs]

                # salvar
                node.name = new_name
                node.edges = selected_ids

                refresh_node_list()
                ed.destroy()

            btn_save = tk.Button(ed, text='Salvar', width=12, command=save_edit)
            btn_cancel = tk.Button(ed, text='Cancelar', width=12, command=ed.destroy)
            btn_save.grid(row=3, column=0, pady=8, padx=8, sticky='w')
            btn_cancel.grid(row=3, column=1, pady=8, padx=8, sticky='e')

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
        nodes = graph.nodes
        
        if not nodes:
            messagebox.showinfo('Visualizar Grafo', 'O grafo selecionado não possui nós.')
            return

        win = Toplevel(self.root)
        win.title(f"Visualização do Grafo — {graph.name}")
        win.geometry('600x600')

        canvas = Canvas(win, bg='white')
        canvas.pack(fill='both', expand=True)

        # --- Parâmetros de desenho do grafo ---
        center_x = 300
        center_y = 300
        radius = 200
        node_size = 30
        
        # Guardar posições dos nós para desenhar as arestas
        node_positions = {}
        
        # Distribui os nós em um círculo
        num_nodes = len(nodes)
        for i, node in enumerate(nodes):
            angle = 2 * 3.14159 * i / num_nodes
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            node_positions[node.name] = (x, y)
            
            # Desenha o círculo do nó
            canvas.create_oval(x - node_size, y - node_size, x + node_size, y + node_size,
                               fill='#f0f0f0', outline='#333', width=1.5)
            # Desenha o texto do nome do nó
            canvas.create_text(x, y, text=node.name)

        # Desenha as arestas entre os nós
        for node in nodes:
            for edge_name in node.edges:
                if edge_name in node_positions:
                    x1, y1 = node_positions[node.name]
                    x2, y2 = node_positions[edge_name]
                    canvas.create_line(x1, y1, x2, y2, width=1.5, fill='#666')

        # Botão fechar
        btn_frame = tk.Frame(win, bg='white')
        btn_frame.pack(fill='x', pady=(6,6))
        close_btn = tk.Button(btn_frame, text='Fechar', command=win.destroy, width=12)
        close_btn.pack(side='right', padx=10)

        win.transient(self.root)
        win.grab_set()
        win.focus_force()