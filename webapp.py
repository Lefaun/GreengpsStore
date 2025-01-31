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
            "Cascais": (38.6970, -9.4223),
            "Loures": (38.8309, -9.1685),
            "Almada": (38.6766, -9.1668),
            "Setúbal": (38.5243, -8.8882)
        }

        inicio = st.selectbox("Escolha o ponto de partida", list(LOCALIDADES.keys()))
        destino = st.selectbox("Escolha o destino", list(LOCALIDADES.keys()))
        calcular_rota = st.button("Calcular Rota")

        # Exibir mapa inicial sem rota
        mapa = folium.Map(location=[38.7169, -9.1399], zoom_start=11)
        st_folium(mapa, width=800)
        
        if calcular_rota:
            try:
                grafo = ox.graph_from_place("Lisboa, Portugal", network_type="walk")
                origem = ox.distance.nearest_nodes(grafo, LOCALIDADES[inicio][1], LOCALIDADES[inicio][0])
                destino = ox.distance.nearest_nodes(grafo, LOCALIDADES[destino][1], LOCALIDADES[destino][0])
                
                caminho = nx.shortest_path(grafo, origem, destino, weight="length")
                coords = [(grafo.nodes[n]['y'], grafo.nodes[n]['x']) for n in caminho]
                mapa = folium.Map(location=[(LOCALIDADES[inicio][0] + LOCALIDADES[destino][0]) / 2, 
                                            (LOCALIDADES[inicio][1] + LOCALIDADES[destino][1]) / 2], zoom_start=13)
                folium.PolyLine(coords, color="blue", weight=3).add_to(mapa)
                st_folium(mapa, width=800)
            except nx.NetworkXNoPath:
                st.error("Não foi possível encontrar um caminho entre as localidades selecionadas.")
            except KeyError:
                st.error("Erro ao acessar as localidades. Verifique as seleções e tente novamente.")

    with tabs[1]:
        st.title("Loja Online - Produtos Sustentáveis")
        produtos = [
            {"nome": "Cesta de Legumes", "preco": "10€"},
            {"nome": "Sabão Orgânico", "preco": "5€"},
            {"nome": "Garrafa Ecológica", "preco": "15€"},
            {"nome": "Bolsa Reciclável", "preco": "7€"},
            {"nome": "Kit Sustentável", "preco": "20€"},
            {"nome": "Talheres de Bambu", "preco": "8€"}
        ]
        
        carrinho = []
        for produto in produtos:
            if st.button(f"Comprar {produto['nome']} - {produto['preco']}"):
                carrinho.append(produto["nome"])
                st.success(f"{produto['nome']} adicionado ao carrinho!")
        
        if carrinho:
            st.subheader("Carrinho de Compras")
            for item in carrinho:
                st.write(f"- {item}")
else:
    st.sidebar.error("Credenciais incorretas")
