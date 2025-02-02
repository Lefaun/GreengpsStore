import streamlit as st
import openrouteservice
import pydeck as pdk

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
                # OpenRouteService API Key (substitua pela sua)
                API_KEY = "5b3ce3597851110001cf62481e1354879e17494ba3aa4a0619563108"
                cliente = openrouteservice.Client(key=API_KEY)

                coordenadas = [LOCALIDADES[inicio][::-1], LOCALIDADES[destino][::-1]]

                # Calculando a rota
                rota = cliente.directions(coordenadas, profile='cycling-regular', format='geojson')
                coords = rota['features'][0]['geometry']['coordinates']

                # Configuração do traçado fino e discreto
                linha_rota = pdk.Layer(
                    "LineLayer",
                    data=[{"path": coords}],
                    get_path="path",
                    get_color="[0, 0, 255]",  # Azul discreto
                    width_min_pixels=2,  # Traço mais fino
                    get_width=2,
                )

                view_state = pdk.ViewState(
                    latitude=coordenadas[0][1],
                    longitude=coordenadas[0][0],
                    zoom=12,
                    pitch=0
                )

                # Exibir o mapa com a rota ajustada às ruas
                st.pydeck_chart(pdk.Deck(
                    map_style=map_style_selected,
                    layers=[linha_rota],
                    initial_view_state=view_state
                ))

            except Exception as e:
                st.error(f"❌ Erro ao calcular a rota: {e}")

    # TAB 2 - Loja Online (permanece inalterada)
else:
    st.sidebar.error("❌ Credenciais incorretas")
