import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import heapq

# Bellman-Ford algoritması
def bellman_ford(graph, source, distances, predecessors):
    distances[source] = 0
    for _ in range(len(graph) - 1):
        for u in graph:
            for v, weight in graph[u].items():
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    predecessors[v] = u

    for u in graph:
        for v, weight in graph[u].items():
            if distances[u] + weight < distances[v]:
                raise ValueError("Graf negatif ağırlıklı bir döngü içeriyor")

# Dijkstra algoritması
def dijkstra(graph, source):
    distances = {vertex: float('infinity') for vertex in graph}
    distances[source] = 0
    öncelik_kuyruğu = [(0, source)]
    
    while öncelik_kuyruğu:
        mevcut_mesafe, mevcut_düğüm = heapq.heappop(öncelik_kuyruğu)
        
        if mevcut_mesafe > distances[mevcut_düğüm]:
            continue
        
        for komşu, ağırlık in graph[mevcut_düğüm].items():
            mesafe = mevcut_mesafe + ağırlık
            if mesafe < distances[komşu]:
                distances[komşu] = mesafe
                heapq.heappush(öncelik_kuyruğu, (mesafe, komşu))
    
    return distances

# Johnson algoritması
def johnson(graph):
    yeni_graf = graph.copy()
    yeni_düğüm = 's'
    yeni_graf[yeni_düğüm] = {vertex: 0 for vertex in graph}

    distances = {vertex: float('infinity') for vertex in yeni_graf}
    predecessors = {vertex: None for vertex in yeni_graf}

    try:
        bellman_ford(yeni_graf, yeni_düğüm, distances, predecessors)
    except ValueError as e:
        return str(e)
    
    h = distances
    yeniden_ağırlıklı_graf = {}
    for u in graph:
        yeniden_ağırlıklı_graf[u] = {}
        for v in graph[u]:
            yeniden_ağırlıklı_graf[u][v] = graph[u][v] + h[u] - h[v]
    
    en_kısa_yollar = {}
    for u in graph:
        en_kısa_yollar[u] = dijkstra(yeniden_ağırlıklı_graf, u)
        for v in en_kısa_yollar[u]:
            if en_kısa_yollar[u][v] != float('infinity'):
                en_kısa_yollar[u][v] += h[v] - h[u]

    return en_kısa_yollar

class GrafUygulaması:
    def __init__(self, root):
        self.root = root
        self.root.title("Johnson Algoritması Uygulaması")
        self.graph = nx.DiGraph()

        self.frame = tk.Frame(root)
        self.frame.grid(row=0, column=0, padx=10, pady=10)

        self.düğüm_etiket = tk.Label(self.frame, text="Düğüm:")
        self.düğüm_etiket.grid(row=0, column=0)
        self.düğüm_girişi = tk.Entry(self.frame)
        self.düğüm_girişi.grid(row=0, column=1)

        self.düğüm_ekle_buton = tk.Button(self.frame, text="Düğüm Ekle", command=self.düğüm_ekle)
        self.düğüm_ekle_buton.grid(row=0, column=2)

        self.kenar_etiket = tk.Label(self.frame, text="Kenar (kaynak hedef ağırlık):")
        self.kenar_etiket.grid(row=1, column=0)
        self.kenar_girişi = tk.Entry(self.frame)
        self.kenar_girişi.grid(row=1, column=1)

        self.kenar_ekle_buton = tk.Button(self.frame, text="Kenar Ekle", command=self.kenar_ekle)
        self.kenar_ekle_buton.grid(row=1, column=2)

        self.hesapla_buton = tk.Button(self.frame, text="En Kısa Yolları Hesapla", command=self.en_kısa_yolları_hesapla)
        self.hesapla_buton.grid(row=2, column=1, pady=10)

        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.grid(row=0, column=1, rowspan=3, padx=10, pady=10)
        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack()

        self.sonuç_frame = tk.Frame(root)
        self.sonuç_frame.grid(row=0, column=2, rowspan=3, padx=10, pady=10)

    def düğüm_ekle(self):
        düğüm = self.düğüm_girişi.get()
        if düğüm:
            self.graph.add_node(düğüm)
            self.düğüm_girişi.delete(0, tk.END)
            self.grafiği_çiz()
            

    def kenar_ekle(self):
        kenar = self.kenar_girişi.get()
        try:
            kaynak, hedef, ağırlık = kenar.split()
            ağırlık = int(ağırlık)
            if kaynak in self.graph and hedef in self.graph:
                self.graph.add_edge(kaynak, hedef, weight=ağırlık)
                self.kenar_girişi.delete(0, tk.END)
                self.grafiği_çiz()
                messagebox.showinfo("Başarılı", f"Kenar '{kaynak} -> {hedef}' ağırlık: {ağırlık} eklendi.")
            else:
                messagebox.showerror("Hata", "Kaynak veya hedef düğüm mevcut değil.")
        except ValueError:
            messagebox.showerror("Hata", "Kenar 'kaynak hedef ağırlık' formatında olmalıdır.")

    def en_kısa_yolları_hesapla(self):
        graf_sözlüğü = {node: {neighbor: data['weight'] for neighbor, data in self.graph[node].items()} for node in self.graph.nodes}
        try:
            en_kısa_yollar = johnson(graf_sözlüğü)
            self.en_kısa_yolları_göster(en_kısa_yollar)
        except ValueError as e:
            messagebox.showerror("Hata", str(e))

    def en_kısa_yolları_göster(self, en_kısa_yollar):
        for widget in self.sonuç_frame.winfo_children():
            widget.destroy()

        düğümler = list(self.graph.nodes)
        n = len(düğümler)

        for i in range(n+1):
            for j in range(n+1):
                if i == 0 and j == 0:
                    etiket = tk.Label(self.sonuç_frame, text="")
                elif i == 0:
                    etiket = tk.Label(self.sonuç_frame, text=düğümler[j-1])
                elif j == 0:
                    etiket = tk.Label(self.sonuç_frame, text=düğümler[i-1])
                else:
                    kaynak = düğümler[i-1]
                    hedef = düğümler[j-1]
                    değer = en_kısa_yollar[kaynak].get(hedef, "∞")
                    etiket = tk.Label(self.sonuç_frame, text=str(değer))
                etiket.grid(row=i, column=j, padx=5, pady=5)

    def grafiği_çiz(self):
        self.figure.clear()
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, ax=self.figure.add_subplot(111))
        etiketler = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=etiketler)
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = GrafUygulaması(root)
    root.mainloop()
