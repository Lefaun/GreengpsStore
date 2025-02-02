import streamlit as st
import folium
from streamlit_folium import st_folium
import openrouteservice
import time

# Configuração do layout
tabs = st.tabs(["Mapa", "Loja Online"])

# Simulação de login
st.sidebar.title("Login")
usuario = st.sidebar.text_input("Usuário", value="admin")
senha = st.sidebar.text_input("Senha", type="password", value="1234", key="password")

if usuario == "admin" and senha == "1234":
    # TAB 1 - Mapa
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
                # OpenRouteService API Key (substitua pela sua)
                API_KEY = "sua_api_key_aqui"
                cliente = openrouteservice.Client(key=API_KEY)

                coordenadas = [LOCALIDADES[inicio][::-1], LOCALIDADES[destino][::-1]]

                # Calculando a rota
                rota = cliente.directions(coordenadas, profile='cycling-regular', format='geojson')
                coords = [(ponto[1], ponto[0]) for ponto in rota['features'][0]['geometry']['coordinates']]

                # Criar o mapa com zoom no ponto inicial
                mapa = folium.Map(location=coords[0], zoom_start=14)
                folium.PolyLine(coords, color="green", weight=6).add_to(mapa)

                # Adicionar ícone de bicicleta no ponto inicial
                folium.Marker(
                    location=coords[0],
                    icon=folium.Icon(color="blue", icon="bicycle", prefix="fa")
                ).add_to(mapa)

                mapa_placeholder = st_folium(mapa, width=800)

                # Simulação de GPS
                for i in range(len(coords)):
                    mapa = folium.Map(location=coords[i], zoom_start=14)
                    folium.PolyLine(coords, color="green", weight=6).add_to(mapa)

                    folium.Marker(
                        location=coords[i],
                        icon=folium.Icon(color="blue", icon="bicycle", prefix="fa")
                    ).add_to(mapa)

                    mapa_placeholder = st_folium(mapa, width=800)
                    time.sleep(1)

            except Exception as e:
                st.error(f"❌ Erro ao calcular a rota: {e}")
        else:
            mapa = folium.Map(location=[38.7169, -9.1399], zoom_start=11)
            st_folium(mapa, width=800)

    # TAB 2 - Loja Online
    with tabs[1]:
        st.title("🛒 Loja Sustentável")

        produtos = [
            {"nome": "Cesta Orgânica", "preco": 12.99, "img": "imagens/Horta.png"},
            {"nome": "Sabonete Natural", "preco": 7.50, "img": "imagens/soap.png"},
            {"nome": "Bolsa Ecológica", "preco": 15.00, "img": "imagens/BolsaCometico.png"},
            {"nome": "Kit Bambu", "preco": 9.99, "img": "imagens/KitBambu.png"},
            {"nome": "Mel Orgânico", "preco": 18.50, "img": "imagens/mel.png"},
            {"nome": "Horta Caseira", "preco": 25.00, "img": "imagens/Horta.jpg"},
            {"nome": "Cosméticos Naturais", "preco": 19.99, "img": "imagens/Cosmetico.png"},
            {"nome": "Chá Artesanal", "preco": 10.99, "img": "imagens/Chá.jpg"},
            {"nome": "Velas Ecológicas", "preco": 14.50, "img": "imagens/Velas.png"},
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
                try:
                    st.image(produto["img"], caption=produto["nome"], use_column_width=True)
                except Exception:
                    st.warning(f"Imagem não encontrada para {produto['nome']}.")
                st.write(f"€ {produto['preco']:.2f}")
                if st.button(f"🛒 Adicionar {produto['nome']}", key=produto["nome"]):
                    adicionar_ao_carrinho(produto["nome"])
                    st.success(f"{produto['nome']} adicionado ao carrinho!")

        # Exibir Carrinho
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
