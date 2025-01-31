import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import networkx as nx
import osmnx as ox

# Configuração do layout
tabs = st.tabs(["Mapa", "Loja Online"])

# Simulação de login
st.sidebar.title("Login")
usuario = st.sidebar.text_input("Usuário", value="admin")
senha = st.sidebar.text_input("Senha", type="password", value="1234", key="password")

if usuario == "admin" and senha == "1234":
    with tabs[0]:
        st.title("Otimizador de Percurso - Áreas Limpas")

        LOCALIDADES = {
            "Amadora": (38.7597, -9.2249),
            "Queluz": (38.7566, -9.2546),
            "Lisboa": (38.7169, -9.1399),
            "Sintra": (38.8029, -9.3817),
            "Oeiras": (38.6979, -9.3017),
            "Cascais": (38.6970, -9.4223)
        }

        inicio = st.selectbox("Escolha o ponto de partida", list(LOCALIDADES.keys()))
        destino = st.selectbox("Escolha o destino", list(LOCALIDADES.keys()))
        calcular_rota = st.button("Calcular Rota")
        
        if calcular_rota:
            grafo = ox.graph_from_place("Lisboa, Portugal", network_type="walk")
            origem = ox.distance.nearest_nodes(grafo, LOCALIDADES[inicio][1], LOCALIDADES[inicio][0])
            destino = ox.distance.nearest_nodes(grafo, LOCALIDADES[destino][1], LOCALIDADES[destino][0])
            
            try:
                caminho = nx.shortest_path(grafo, origem, destino, weight="length")
                coords = [(grafo.nodes[n]['y'], grafo.nodes[n]['x']) for n in caminho]
                mapa = folium.Map(location=[(LOCALIDADES[inicio][0] + LOCALIDADES[destino][0]) / 2, 
                                            (LOCALIDADES[inicio][1] + LOCALIDADES[destino][1]) / 2], zoom_start=13)
                folium.PolyLine(coords, color="blue", weight=3).add_to(mapa)
                st_folium(mapa, width=800)
            except nx.NetworkXNoPath:
                st.error("Não foi possível encontrar um caminho entre as localidades selecionadas.")

    with tabs[1]:
        st.title("Loja Online - Produtos Sustentáveis")
        produtos = ["Cesta de Legumes", "Sabão Orgânico", "Garrafa Ecológica", "Bolsa Reciclável", "Kit Sustentável", "Talheres de Bambu"]
        for produto in produtos:
            if st.button(f"Comprar {produto}"):
                st.success(f"{produto} adicionado ao carrinho!")
else:
    st.sidebar.error("Credenciais incorretas")
