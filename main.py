import streamlit as st
import folium
from streamlit_folium import st_folium
import openrouteservice
from openrouteservice import convert
import time
import os

# Configuração do layout
st.set_page_config(page_title="Otimizador de Rotas & Loja", layout="wide")
tabs = st.tabs(["Mapa", "Loja Online"])

# Simulação de login
st.sidebar.title("Login")
usuario = st.sidebar.text_input("Usuário", value="admin")
senha = st.sidebar.text_input("Senha", type="password", key="password")

# Autenticação básica
if usuario == "admin" and senha == "1234":
    with tabs[0]:
        st.title("🚴 Otimizador de Percurso - GPS Ativo")

        # Localizações predefinidas
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

        # Seletor de ponto de partida e destino
        inicio = st.selectbox("Escolha o ponto de partida", list(LOCALIDADES.keys()))
        destino = st.selectbox("Escolha o destino", list(LOCALIDADES.keys()))
        calcular_rota = st.button("Calcular Rota")

        if calcular_rota:
            if inicio == destino:
                st.error("⛔ O ponto de partida e o destino são iguais!")
            else:
                with st.spinner("Calculando rota..."):
                    try:
                        # Configurar a chave da API do OpenRouteService
                        API_KEY = os.getenv("5b3ce3597851110001cf62481e1354879e17494ba3aa4a0619563108")  # Defina sua chave no ambiente
                        cliente = openrouteservice.Client(key=API_KEY)

                        coordenadas = [
                            (LOCALIDADES[inicio][1], LOCALIDADES[inicio][0]),
                            (LOCALIDADES[destino][1], LOCALIDADES[destino][0])
                        ]

                        # Requisitar rota para bicicleta
                        rota = cliente.directions(coordenadas, profile='cycling-regular', format='geojson')
                        distancia = round(rota['features'][0]['properties']['summary']['distance'] / 1000, 2)
                        duracao = round(rota['features'][0]['properties']['summary']['duration'] / 60, 2)

                        # Criar mapa
                        mapa = folium.Map(location=LOCALIDADES[inicio], zoom_start=12)

                        # Adicionar rota
                        folium.GeoJson(rota, name="route").add_to(mapa)

                        # Marcadores de início e destino
                        folium.Marker(LOCALIDADES[inicio], tooltip="Início", icon=folium.Icon(color='green')).add_to(mapa)
                        folium.Marker(LOCALIDADES[destino], tooltip="Destino", icon=folium.Icon(color='red')).add_to(mapa)

                        # Exibir resultados
                        st.success(f"🌍 Distância: {distancia} km | ⏱️ Duração estimada: {duracao} min")
                        st_folium(mapa, width=800, height=500)

                    except Exception as e:
                        st.error(f"❌ Erro ao calcular a rota: {e}")
        else:
            mapa = folium.Map(location=[38.7169, -9.1399], zoom_start=11)
            st_folium(mapa, width=800, height=500)

    # Loja Online
    with tabs[1]:
        st.title("🛍️ Loja Sustentável")

        produtos = [
            {"nome": "Cesta Orgânica", "preco": 12.99, "img": "Horta.png"},
            {"nome": "Sabonete Natural", "preco": 7.50, "img": "soap.png"},
            {"nome": "Bolsa Ecológica", "preco": 15.00, "img": "BolsaCometico.png"},
            {"nome": "Kit Bambu", "preco": 9.99, "img": "KitBambu.png"},
            {"nome": "Mel Orgânico", "preco": 18.50, "img": "mel.png"},
            {"nome": "Horta Caseira", "preco": 25.00, "img": "Horta.jpg"},
            {"nome": "Cosméticos Naturais", "preco": 19.99, "img": "Cosmetico.png"},
            {"nome": "Chá Artesanal", "preco": 10.99, "img": "Chá.jpg"},
            {"nome": "Velas Ecológicas", "preco": 14.50, "img": "Velas.png"},
        ]

        st.session_state.setdefault("carrinho", {})

        def adicionar_ao_carrinho(produto):
            if produto in st.session_state["carrinho"]:
                st.session_state["carrinho"][produto] += 1
            else:
                st.session_state["carrinho"][produto] = 1

        cols = st.columns(3)
        for i, produto in enumerate(produtos):
            with cols[i % 3]:
                st.image(produto["img"], caption=produto["nome"], use_column_width=True)
                st.write(f"€ {produto['preco']:.2f}")
                if st.button(f"🛒 Adicionar {produto['nome']}", key=produto["nome"]):
                    adicionar_ao_carrinho(produto["nome"])
                    st.success(f"{produto['nome']} adicionado ao carrinho!")

        # Carrinho de Compras
        st.sidebar.title("🛒 Carrinho de Compras")
        if st.session_state["carrinho"]:
            total = 0
            for item, qtd in st.session_state["carrinho"].items():
                preco = next(p["preco"] for p in produtos if p["nome"] == item)
                subtotal = preco * qtd
                total += subtotal
                st.sidebar.write(f"{item} ({qtd}x) - €{subtotal:.2f}")
            st.sidebar.write(f"**Total: €{total:.2f}**")
            if st.sidebar.button("✅ Finalizar Pedido"):
                st.sidebar.success("Pedido realizado com sucesso! 🌱")
                st.session_state["carrinho"] = {}
        else:
            st.sidebar.write("Seu carrinho está vazio.")
else:
    st.sidebar.error("❌ Credenciais incorretas")
