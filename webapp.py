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

# 🛒 Loja (Produtos, preço, link)
PRODUTOS = [
    {"nome": "Cesta de Frutas Orgânicas", "preco": 15, "link": "https://mercado-sustentavel.com/cesta"},
    {"nome": "Mel Puro de Apicultura Local", "preco": 10, "link": "https://mercado-sustentavel.com/mel"},
    {"nome": "Sabonete Natural de Alecrim", "preco": 5, "link": "https://mercado-sustentavel.com/sabonete"},
]

# 🛣️ Carregar grafo de estradas de Lisboa para rotas otimizadas
grafo = ox.graph_from_place("Lisboa, Portugal", network_type="drive")

# 🔐 Função de autenticação
def autenticar(usuario, senha):
    return USUARIOS.get(usuario) == senha

# 🚗 Encontrar melhor rota via OSMnx (menos poluição e trânsito)
def encontrar_rota_otimizada(inicio, destino):
    origem = ox.distance.nearest_nodes(grafo, LOCALIDADES[inicio][1], LOCALIDADES[inicio][0])
    destino = ox.distance.nearest_nodes(grafo, LOCALIDADES[destino][1], LOCALIDADES[destino][0])

    caminho = nx.shortest_path(grafo, origem, destino, weight="length")  # Minimiza distância
    rota = [(grafo.nodes[n]["y"], grafo.nodes[n]["x"]) for n in caminho]

    return rota

# 🗺️ Criar mapa com a rota escolhida
def criar_mapa(rota):
    centro = rota[0]  # Primeiro ponto da rota como centro
    mapa = folium.Map(location=centro, zoom_start=13)

    # Adicionar marcadores
    folium.Marker(rota[0], popup="Início", icon=folium.Icon(color="green")).add_to(mapa)
    folium.Marker(rota[-1], popup="Destino", icon=folium.Icon(color="red")).add_to(mapa)

    # Traçar a rota
    folium.PolyLine(rota, color="blue", weight=3, opacity=0.7).add_to(mapa)

    return mapa

# 🎯 Interface principal
def main():
    st.title("🚲 Roteiro Sustentável & Loja Online")

    # 🔐 Login
    if "logado" not in st.session_state:
        st.session_state.logado = False

    if not st.session_state.logado:
        st.subheader("🔐 Login")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if autenticar(usuario, senha):
                st.session_state.logado = True
                st.success(f"Bem-vindo, {usuario}!")
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha incorretos!")
        return

    # 🔓 Se logado, mostrar 
