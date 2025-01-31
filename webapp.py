import streamlit as st
import folium
from streamlit_folium import st_folium
import networkx as nx
import osmnx as ox
import time

# Configuração do layout
tabs = st.tabs(["Mapa", "Loja Online"])

# Simulação de login
st.sidebar.title("Login")
usuario = st.sidebar.text_input("Usuário", value="admin")
senha = st.sidebar.text_input("Senha", type="password", value="1234", key="password")

if usuario == "admin" and senha == "1234":
    with tabs[0]:
        st.title("🚴 Otimizador de Percurso - GPS Ativo")

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

        if calcular_rota:
            try:
                # Criar grafo da rede viária para pedestres 🚶‍♂️
                grafo = ox.graph_from_place("Lisboa, Portugal", network_type="walk")
                
                # Encontrar os nós mais próximos das coordenadas selecionadas
                origem = ox.distance.nearest_nodes(grafo, LOCALIDADES[inicio][1], LOCALIDADES[inicio][0])
                destino = ox.distance.nearest_nodes(grafo, LOCALIDADES[destino][1], LOCALIDADES[destino][0])
                
                # Calcular o caminho mais curto 🚲
                caminho = nx.shortest_path(grafo, origem, destino, weight="length")
                coords = [(grafo.nodes[n]['y'], grafo.nodes[n]['x']) for n in caminho]

                # Criar mapa
                mapa = folium.Map(location=[(LOCALIDADES[inicio][0] + LOCALIDADES[destino][0]) / 2, 
                                            (LOCALIDADES[inicio][1] + LOCALIDADES[destino][1]) / 2], zoom_start=14)

                # Adicionar linha azul (como no GPS) 🟦
                folium.PolyLine(coords, color="blue", weight=6).add_to(mapa)

                # Adicionar um marcador inicial para a bicicleta 🚴‍♂️
                bicicleta = folium.Marker(
                    location=coords[0],
                    icon=folium.Icon(color="red", icon="bicycle", prefix="fa")
                )
                bicicleta.add_to(mapa)

                # Exibir o mapa inicial
                mapa_placeholder = st_folium(mapa, width=800)

                # Simulação de navegação GPS ⏳
                for i in range(len(coords)):
                    mapa = folium.Map(location=coords[i], zoom_start=14)

                    # Linha azul sólida 🟦
                    folium.PolyLine(coords, color="blue", weight=6).add_to(mapa)

                    # Atualizar a posição da bicicleta 🚴‍♂️
                    bicicleta = folium.Marker(
                        location=coords[i],
                        icon=folium.Icon(color="red", icon="bicycle", prefix="fa")
                    )
                    bicicleta.add_to(mapa)

                    # Atualiza o mapa
                    mapa_placeholder = st_folium(mapa, width=800)
                    time.sleep(1)  # Simula o deslocamento GPS

            except nx.NetworkXNoPath:
                st.error("❌ Não foi possível encontrar um caminho entre as localidades selecionadas.")
            except KeyError:
                st.error("❌ Erro ao acessar as localidades. Verifique as seleções e tente novamente.")
        else:
            mapa = folium.Map(location=[38.7169, -9.1399], zoom_start=11)
            st_folium(mapa, width=800)

    with tabs[1]:
        st.title("🛒 Loja Online - Produtos Sustentáveis")

        produtos = [
            {"nome": "Cesta de Legumes", "preco": "10€"},
            {"nome": "Sabão Orgânico", "preco": "5€"},
            {"nome": "Garrafa Ecológica", "preco": "15€"},
            {"nome": "Bolsa Reciclável", "preco": "7€"},
            {"nome": "Kit Sustentável", "preco": "20€"},
            {"nome": "Talheres de Bambu", "preco": "8€"}
        ]

        if "carrinho" not in st.session_state:
            st.session_state.carrinho = []

        for produto in produtos:
            if st.button(f"Comprar {produto['nome']} - {produto['preco']}"):
                st.session_state.carrinho.append(produto["nome"])
                st.success(f"✅ {produto['nome']} adicionado ao carrinho!")

        if st.session_state.carrinho:
            st.subheader("🛍️ Carrinho de Compras")
            for item in st.session_state.carrinho:
                st.write(f"- {item}")

else:
    st.sidebar.error("❌ Credenciais incorretas")
