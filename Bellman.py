import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class BellmanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Algorithme de Bellman (Programmation Dynamique) - JAOUAD Salah-Eddine")

        # Création du graphe orienté acyclique (DAG)
        self.graph = {}
        self.vertices_order = []  # Pour maintenir l'ordre topologique

        # Création des widgets
        self.create_widgets()

    def create_widgets(self):
        # Frame pour l'ajout des sommets
        vertex_frame = ttk.LabelFrame(self.root, text="Ajouter un sommet")
        vertex_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(vertex_frame, text="Sommet:").grid(row=0, column=0, padx=5, pady=5)
        self.vertex = ttk.Entry(vertex_frame, width=10)
        self.vertex.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(vertex_frame, text="Ajouter Sommet",
                   command=self.add_vertex).grid(row=0, column=2, padx=5, pady=5)

        # Frame pour l'ajout des arêtes
        input_frame = ttk.LabelFrame(self.root, text="Ajouter une arête")
        input_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(input_frame, text="De:").grid(row=0, column=0, padx=5, pady=5)
        self.source = ttk.Entry(input_frame, width=10)
        self.source.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Vers:").grid(row=0, column=2, padx=5, pady=5)
        self.dest = ttk.Entry(input_frame, width=10)
        self.dest.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Poids:").grid(row=0, column=4, padx=5, pady=5)
        self.weight = ttk.Entry(input_frame, width=10)
        self.weight.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(input_frame, text="Ajouter Arête",
                   command=self.add_edge).grid(row=0, column=6, padx=5, pady=5)

        # Frame pour le calcul
        calc_frame = ttk.LabelFrame(self.root, text="Calcul du plus court chemin")
        calc_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(calc_frame, text="Sommet de départ:").grid(row=0, column=0, padx=5, pady=5)
        self.start_vertex = ttk.Entry(calc_frame, width=10)
        self.start_vertex.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(calc_frame, text="Calculer (Récursif)",
                   command=lambda: self.calculate_path("recursive")).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(calc_frame, text="Calculer (Dynamique)",
                   command=lambda: self.calculate_path("dynamic")).grid(row=0, column=3, padx=5, pady=5)

        # Frame pour l'affichage des résultats
        self.result_frame = ttk.LabelFrame(self.root, text="Résultats")
        self.result_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self.result_text = tk.Text(self.result_frame, height=10, width=50)
        self.result_text.pack(padx=5, pady=5, fill="both", expand=True)

        # Frame pour le graphe
        self.graph_frame = ttk.LabelFrame(self.root, text="Visualisation du graphe")
        self.graph_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def add_vertex(self):
        vertex = self.vertex.get()
        if vertex and vertex not in self.vertices_order:
            self.vertices_order.append(vertex)
            self.graph[vertex] = {}
            self.vertex.delete(0, tk.END)
            self.update_graph_visualization()
            messagebox.showinfo("Succès", "Sommet ajouté avec succès!")
        else:
            messagebox.showerror("Erreur", "Sommet invalide ou déjà existant")

    def add_edge(self):
        try:
            src = self.source.get()
            dst = self.dest.get()
            w = float(self.weight.get())

            if src not in self.graph or dst not in self.graph:
                messagebox.showerror("Erreur", "Les sommets doivent être créés d'abord")
                return

            # Vérifier que l'arête respecte l'ordre topologique
            if self.vertices_order.index(src) >= self.vertices_order.index(dst):
                messagebox.showerror("Erreur", "L'arête ne respecte pas l'ordre topologique")
                return

            self.graph[src][dst] = w
            self.update_graph_visualization()
            messagebox.showinfo("Succès", "Arête ajoutée avec succès!")

            # Clear entries
            self.source.delete(0, tk.END)
            self.dest.delete(0, tk.END)
            self.weight.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides")

    def bellman_recursive(self, source, target, memo=None):
        if memo is None:
            memo = {}

        if source == target:
            return 0, [source]

        if source in memo:
            return memo[source]

        min_dist = float('inf')
        min_path = None

        for next_vertex, weight in self.graph[source].items():
            if self.vertices_order.index(next_vertex) <= self.vertices_order.index(source):
                continue

            dist, path = self.bellman_recursive(next_vertex, target, memo)
            if dist != float('inf') and weight + dist < min_dist:
                min_dist = weight + dist
                min_path = [source] + path

        memo[source] = (min_dist, min_path if min_path else [source])
        return memo[source]

    def bellman_dynamic(self, source):
        n = len(self.vertices_order)
        dist = {v: float('inf') for v in self.vertices_order}
        prev = {v: None for v in self.vertices_order}
        dist[source] = 0

        # Parcours dans l'ordre topologique
        for u in self.vertices_order:
            if dist[u] == float('inf'):
                continue
            for v, w in self.graph[u].items():
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    prev[v] = u

        # Reconstruction des chemins
        paths = {}
        for v in self.vertices_order:
            if dist[v] != float('inf'):
                path = []
                curr = v
                while curr is not None:
                    path.append(curr)
                    curr = prev[curr]
                path.reverse()
                paths[v] = (dist[v], path)
            else:
                paths[v] = (float('inf'), None)

        return paths

    def calculate_path(self, method):
        source = self.start_vertex.get()
        if source not in self.graph:
            messagebox.showerror("Erreur", "Sommet de départ invalide")
            return

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Résultats pour la méthode {method}:\n\n")

        if method == "recursive":
            for target in self.vertices_order:
                if self.vertices_order.index(target) >= self.vertices_order.index(source):
                    dist, path = self.bellman_recursive(source, target)
                    if dist != float('inf'):
                        self.result_text.insert(tk.END,
                                                f"Vers {target}: Distance = {dist}, Chemin = {' -> '.join(path)}\n")
                    else:
                        self.result_text.insert(tk.END,
                                                f"Vers {target}: Pas de chemin trouvé\n")
        else:
            paths = self.bellman_dynamic(source)
            for vertex, (dist, path) in paths.items():
                if dist != float('inf'):
                    self.result_text.insert(tk.END,
                                            f"Vers {vertex}: Distance = {dist}, Chemin = {' -> '.join(path)}\n")
                else:
                    self.result_text.insert(tk.END,
                                            f"Vers {vertex}: Pas de chemin trouvé\n")

    def update_graph_visualization(self):
        self.ax.clear()
        G = nx.DiGraph()

        # Ajout des sommets dans l'ordre
        for vertex in self.vertices_order:
            G.add_node(vertex)

        # Ajout des arêtes
        for u in self.graph:
            for v, w in self.graph[u].items():
                G.add_edge(u, v, weight=w)

        pos = nx.spring_layout(G)
        nx.draw(G, pos, ax=self.ax, with_labels=True, node_color='lightblue',
                node_size=500, arrowsize=20)

        # Ajout des poids sur les arêtes
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels)

        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = BellmanGUI(root)
    root.mainloop()