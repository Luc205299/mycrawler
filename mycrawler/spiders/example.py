import scrapy
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Utiliser le backend Agg
import matplotlib.pyplot as plt
from urllib.parse import urlparse

class ExampleSpider(scrapy.Spider):
    name = "test"
    start_urls = ['https://www.youtube.com/']

    def __init__(self, *args, **kwargs):
        super(ExampleSpider, self).__init__(*args, **kwargs)
        self.graph = nx.DiGraph()  # Crée un graphe orienté
        self.domains = []  # Initialiser comme attribut de classe

    def parse(self, response):
        current_url = response.url
        self.graph.add_node(current_url)  # Ajoute le nœud pour la page actuelle
        domain = self.get_domain(current_url)
        if domain not in self.domains:
            self.domains.append(domain)  # Ajouter le domaine à la liste des domaines

        # Récupère tous les titres h1
        for h1 in response.css('h1'):
            yield {'title': h1.css('::text').get()}

        # Suivre les liens pour continuer le crawling
        for next_page in response.css('a::attr(href)').getall():
            next_page = response.urljoin(next_page)  # Construit l'URL absolue
            if next_page is not None and next_page.startswith(('http://', 'https://')):
                self.graph.add_edge(current_url, next_page)  # Ajoute une arête entre les pages
                yield response.follow(next_page, self.parse)

    def closed(self, reason):
        # Vérifie que le graphe contient des nœuds
        if len(self.graph) > 0:
            self.log(f"Graph contains {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges.")
            pos = nx.spring_layout(self.graph)  # Positionnement des nœuds
            plt.figure(figsize=(100, 100))  # Définit une taille de figure raisonnable
            nx.draw(self.graph, pos, with_labels=True, node_size=50, font_size=8, arrowsize=10, font_color='red')
            print("Domains:", self.domains)
            try:
                plt.savefig("graph.png")  # Enregistre le graphe dans un fichier image
                self.log("Graph saved successfully.")
            except Exception as e:
                self.log(f"Error saving graph: {e}")
            finally:
                print("Domains:", self.domains)
                plt.close()  # Ferme la figure pour libérer des ressources
        else:
            self.log("Le graphe est vide. Aucun nœud n'a été ajouté.")

    def get_domain(self, url):
        parsed_url = urlparse(url)
        return parsed_url.netloc
