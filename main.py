import streamlit as st
import openrouteservice
import pydeck as pdk
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

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
        estilo_mapa = st.selectbox("Escolha o estilo do mapa", ["Claro", "Satélite"])
        calcular_rota = st.button("Calcular Rota")

        # Definição do estilo do mapa
        map_styles = {
            "Claro": "mapbox://styles/mapbox/light-v9",
            "Satélite": "mapbox://styles/mapbox/satellite-v9"
        }
        map_style_selected = map_styles[estilo_mapa]

        if calcular_rota:
            try:
                API_KEY = "SUA_API_KEY"
                cliente = openrouteservice.Client(key=API_KEY)

                coordenadas = [LOCALIDADES[inicio][::-1], LOCALIDADES[destino][::-1]]

                # Calculando a rota
                rota = cliente.directions(coordenadas, profile='cycling-regular', format='geojson')
                coords = rota['features'][0]['geometry']['coordinates']

                # Criando linha do percurso
                linha_rota = pdk.Layer(
                    "LineLayer",
                    data=[{"path": coords}],
                    get_path="path",
                    get_color="[0, 0, 255]",  # Azul discreto
                    width_min_pixels=2,
                    get_width=2,
                )

                view_state = pdk.ViewState(
                    latitude=coordenadas[0][1],
                    longitude=coordenadas[0][0],
                    zoom=12,
                    pitch=0
                )

                # Exibir o mapa
                st.pydeck_chart(pdk.Deck(
                    map_style=map_style_selected,
                    layers=[linha_rota],
                    initial_view_state=view_state
                ))

                # Simulação de GPS
                for i, ponto in enumerate(coords):
                    st.write(f"🚴 Em movimento: Latitude {ponto[1]}, Longitude {ponto[0]}")
                    time.sleep(1)

            except Exception as e:
                st.error(f"❌ Erro ao calcular a rota: {e}")

    # TAB 2 - Loja Online
    with tabs[1]:
        st.title("🛒 Loja Sustentável")

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
            pedido = ""
            for item, qtd in st.session_state["carrinho"].items():
                preco = next(p["preco"] for p in produtos if p["nome"] == item)
                subtotal = preco * qtd
                total += subtotal
                pedido += f"{item} ({qtd}x) - €{subtotal:.2f}\n"

            st.sidebar.write(f"**Total: €{total:.2f}**")
            endereco = st.sidebar.text_input("📍 Endereço de Entrega")
            pagamento = st.sidebar.selectbox("💳 Forma de Pagamento", ["Transferência Bancária", "MB Way", "PayPal"])

            if st.sidebar.button("✅ Finalizar Pedido"):
                if endereco:
                    if enviar_email(pedido, total, endereco, pagamento):
                        st.sidebar.success("Pedido realizado com sucesso! 📩")
                        st.session_state["carrinho"] = {}
                    else:
                        st.sidebar.error("❌ Erro ao enviar e-mail.")
                else:
                    st.sidebar.error("❌ Informe um endereço de entrega.")
        else:
            st.sidebar.write("Seu carrinho está vazio.")

else:
    st.sidebar.error("❌ Credenciais incorretas")
