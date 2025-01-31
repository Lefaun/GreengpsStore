import streamlit as st
import folium
from streamlit_folium import st_folium
import networkx as nx
import osmnx as ox
import pandas as pd

# 🔐 Usuários e senhas
USUARIOS = {"admin": "1234", "user1": "abcd"}

# 🗺️ Localidades (nome, coordenadas)
LOCALIDADES = {
    "Amadora": (38.7597, -9.2399),
    "Queluz": (38.7566, -9.2545),
    "Reboleira": (38.7599, -9.2245),
    "Damaia": (38.7414, -9.2125),
    "Alfragide": (38.7323, -9.2095),
    "Benfica": (38.7503, -9.2037),
    "Pontinha": (38.7713, -9.1964),
    "Odivelas": (38.7920, -9.1835),
    "Carnide": (38.7671, -9.1774),
    "Lumiar": (38.7755, -9.1603),
}

# Localidades e coordenadas
LOCALIDADES = {
    "Amadora": (38.7597, -9.2399),
    "Queluz": (38.7566, -9.2546),
    "Lisboa": (38.7169, -9.1399),
    "Amadora": (38.7597, -9.2399),
    "Queluz": (38.7566, -9.2545),
    "Reboleira": (38.7599, -9.2245),
    "Damaia": (38.7414, -9.2125),
    "Alfragide": (38.7323, -9.2095),
    "Benfica": (38.7503, -9.2037),
    "Pontinha": (38.7713, -9.1964),
    "Odivelas": (38.7920, -9.1835),
    "Carnide": (38.7671, -9.1774),
    "Lumiar": (38.7755, -9.1603),
}

def carregar_grafo():
    """Carrega um grafo de estradas para cálculo de rotas."""
    return ox.graph_from_place("Lisboa, Portugal", network_type='walk')

def encontrar_rota_otimizada(grafo, inicio, destino):
    """Encontra a rota com menos trânsito e poluição."""
    if inicio not in LOCALIDADES or destino not in LOCALIDADES:
        st.error("Localização inválida! Escolha pontos válidos.")
        return None
    
    origem = ox.distance.nearest_nodes(grafo, LOCALIDADES[inicio][1], LOCALIDADES[inicio][0])
    destino = ox.distance.nearest_nodes(grafo, LOCALIDADES[destino][1], LOCALIDADES[destino][0])
    
    try:
        caminho = nx.shortest_path(grafo, origem, destino, weight='length')
        return caminho
    except nx.NetworkXNoPath:
        st.error("Não foi possível encontrar uma rota entre os pontos escolhidos.")
        return None

def criar_mapa(grafo, rota):
    """Gera um mapa com a rota selecionada."""
    if not rota:
        return None
    
    mapa = folium.Map(location=[LOCALIDADES['Lisboa'][0], LOCALIDADES['Lisboa'][1]], zoom_start=12)
    
    # Adicionar pontos de início e destino
    folium.Marker(LOCALIDADES['Amadora'], popup="Amadora", icon=folium.Icon(color='blue')).add_to(mapa)
    folium.Marker(LOCALIDADES['Queluz'], popup="Queluz", icon=folium.Icon(color='green')).add_to(mapa)
    folium.Marker(LOCALIDADES['Lisboa'], popup="Lisboa", icon=folium.Icon(color='red')).add_to(mapa)
    
    # Traçar rota
    rota_coords = [(grafo.nodes[node]['y'], grafo.nodes[node]['x']) for node in rota]
    folium.PolyLine(rota_coords, color="blue", weight=5, opacity=0.7).add_to(mapa)
    
    return mapa

def login_page():
    """Tela de login."""
    st.title("Bem-vindo ao GreenGPS Store")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if username == "admin" and password == "1234":
            st.session_state["logado"] = True
            st.success("Login bem-sucedido!")
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos!")

def loja_online():
    """Página da loja online."""
    st.title("Loja Online Sustentável")
    produtos = {
        "Bicicleta Elétrica": "https://loja-sustentavel.com/bicicleta",
        "Painel Solar": "https://loja-sustentavel.com/painel-solar",
        "Filtro de Água": "https://loja-sustentavel.com/filtro-agua",
    }
    
    for produto, link in produtos.items():
        if st.button(f"Comprar {produto}"):
            st.write(f"Clique no link para comprar: [Acesse aqui]({link})")

def main():
    """Função principal da aplicação."""
    if "logado" not in st.session_state:
        login_page()
        return
    
    st.sidebar.title("Menu")
    pagina = st.sidebar.radio("Navegar para:", ["Mapa de Rotas", "Loja Online"])
    
    if pagina == "Mapa de Rotas":
        st.title("Encontre a melhor rota")
        grafo = carregar_grafo()
        
        inicio = st.selectbox("Escolha o ponto de partida", list(LOCALIDADES.keys()))
        destino = st.selectbox("Escolha o destino", list(LOCALIDADES.keys()))
        
        if st.button("Calcular Rota"):
            rota = encontrar_rota_otimizada(grafo, inicio, destino)
            mapa = criar_mapa(grafo, rota)
            if mapa:
                st_folium(mapa, width=800)
    
    elif pagina == "Loja Online":
        loja_online()

if __name__ == "__main__":
    main()

